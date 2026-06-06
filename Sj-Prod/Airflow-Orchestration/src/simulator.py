"""
DAG Simulator — run Airflow DAGs locally without a Docker stack
===============================================================
This module parses the DAG Python files, extracts task definitions,
resolves the dependency graph, and executes tasks in topological order
(respecting task >> task dependencies).

It provides:
  - DAGSimulator.list_dags()         → metadata about all discovered DAGs
  - DAGSimulator.get_dag_graph()     → node/edge list for visualisation
  - DAGSimulator.simulate()          → execute a DAG, return full trace

XCom is implemented as a simple in-process dict so tasks can push/pull
values exactly as they would with the real Airflow XCom backend.

Design principle:
  The DAG files import Airflow if available, otherwise use stub classes.
  The simulator operates in the stub-class world and introspects the
  module's globals() to find DAG objects.  This means the same DAG code
  runs identically in simulator mode and real Airflow.
"""

import importlib.util
import logging
import sys
import time
import traceback
from collections import defaultdict, deque
from dataclasses import dataclass, field
from datetime import UTC, datetime
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple

from src.settings import MAX_RETRIES

logger = logging.getLogger(__name__)

# ---------------------------------------------------------------------------
# Paths
# ---------------------------------------------------------------------------
_ROOT = Path(__file__).resolve().parent.parent
_DAGS_DIR = _ROOT / "dags"
_PLUGINS_DIR = _ROOT / "plugins"

# ---------------------------------------------------------------------------
# Status constants
# ---------------------------------------------------------------------------
STATUS_PENDING = "pending"
STATUS_RUNNING = "running"
STATUS_SUCCESS = "success"
STATUS_FAILED = "failed"
STATUS_SKIPPED = "skipped"
STATUS_UPSTREAM_FAILED = "upstream_failed"

STATUS_COLORS = {
    STATUS_PENDING: "#9e9e9e",
    STATUS_RUNNING: "#2196f3",
    STATUS_SUCCESS: "#4caf50",
    STATUS_FAILED: "#f44336",
    STATUS_SKIPPED: "#ff9800",
    STATUS_UPSTREAM_FAILED: "#9c27b0",
}


# ---------------------------------------------------------------------------
# Data structures
# ---------------------------------------------------------------------------

@dataclass
class TaskInfo:
    task_id: str
    operator_type: str
    upstream_task_ids: List[str] = field(default_factory=list)
    downstream_task_ids: List[str] = field(default_factory=list)
    retries: int = 0
    has_sla: bool = False


@dataclass
class TaskResult:
    task_id: str
    status: str
    start_time: str
    end_time: str
    duration_ms: int
    attempt: int = 1
    return_value: Any = None
    error: Optional[str] = None
    xcoms_pushed: Dict[str, Any] = field(default_factory=dict)


@dataclass
class DAGInfo:
    dag_id: str
    description: str
    schedule: str
    tags: List[str]
    tasks: List[TaskInfo]
    source_file: str
    owner: str = "data-engineering"


@dataclass
class SimulationResult:
    dag_id: str
    run_id: str
    status: str
    start_time: str
    end_time: str
    duration_ms: int
    task_results: List[TaskResult]
    xcoms: Dict[str, Any]
    task_order: List[str]
    errors: List[str]


# ---------------------------------------------------------------------------
# Fake XCom store (per simulation run)
# ---------------------------------------------------------------------------

class XComStore:
    """
    In-memory XCom implementation that mirrors the Airflow XCom API.

    The real Airflow XCom stores values in Postgres.  Here we use a dict
    keyed by (task_id, key) to allow tasks to push/pull values normally.
    """

    def __init__(self):
        self._store: Dict[Tuple[str, str], Any] = {}

    def push(self, task_id: str, key: str, value: Any):
        self._store[(task_id, key)] = value
        logger.debug("XCom push: task=%s key=%s value_type=%s", task_id, key, type(value).__name__)

    def pull(self, task_ids, key: str) -> Any:
        """Mirrors ti.xcom_pull(task_ids=..., key=...)."""
        if isinstance(task_ids, str):
            task_ids = [task_ids]
        for tid in task_ids:
            # Support "group.task_id" → "task_id" fallback for TaskGroup tasks
            val = self._store.get((tid, key))
            if val is None:
                # Try stripping task group prefix
                short_id = tid.split(".")[-1]
                val = self._store.get((short_id, key))
            if val is not None:
                return val
        return None

    def all_xcoms(self) -> Dict[str, Any]:
        return {f"{tid}/{key}": val for (tid, key), val in self._store.items()}

    def task_xcoms(self, task_id: str) -> Dict[str, Any]:
        return {key: val for (tid, key), val in self._store.items() if tid == task_id}


# ---------------------------------------------------------------------------
# Fake TaskInstance (ti) injected into task context
# ---------------------------------------------------------------------------

class FakeTaskInstance:
    """
    Minimal task instance that lets PythonOperator callables use
    ti.xcom_push() and ti.xcom_pull() without real Airflow.
    """

    def __init__(self, task_id: str, xcom_store: XComStore):
        self.task_id = task_id
        self._xcom_store = xcom_store
        self.xcom_data: Dict[str, Any] = {}

    def xcom_push(self, key: str, value: Any):
        self._xcom_store.push(self.task_id, key, value)
        self.xcom_data[key] = value

    def xcom_pull(self, task_ids=None, key: str = "return_value") -> Any:
        if task_ids is None:
            task_ids = []
        return self._xcom_store.pull(task_ids, key)


# ---------------------------------------------------------------------------
# DAG loader — imports a DAG module without crashing if Airflow is absent
# ---------------------------------------------------------------------------

def _load_dag_module(dag_file: Path):
    """
    Import a DAG file as a module.  Returns the module object or None on error.
    """
    module_name = f"sim_dag_{dag_file.stem}"

    # Remove any cached version so re-imports pick up file changes
    if module_name in sys.modules:
        del sys.modules[module_name]

    spec = importlib.util.spec_from_file_location(module_name, dag_file)
    if spec is None or spec.loader is None:
        return None

    module = importlib.util.module_from_spec(spec)
    sys.modules[module_name] = module

    try:
        spec.loader.exec_module(module)
    except Exception as exc:
        logger.warning("Error loading DAG file %s: %s", dag_file.name, exc)
        logger.debug(traceback.format_exc())
        return None

    return module


# ---------------------------------------------------------------------------
# DAG introspection — extract tasks and dependencies from a module
# ---------------------------------------------------------------------------

def _extract_dag_info(module, dag_file: Path) -> List[DAGInfo]:
    """
    Look for DAG objects in the module's globals() and extract structured info.

    Works with both real airflow.DAG objects (when Airflow is installed) and
    the stub DAG class used in simulator mode.
    """
    results = []

    for attr_name in dir(module):
        obj = getattr(module, attr_name, None)
        if obj is None:
            continue

        # Is it a DAG-like object?
        is_dag = (
            type(obj).__name__ == "DAG"
            or (hasattr(obj, "dag_id") and hasattr(obj, "tasks"))
            or (hasattr(obj, "dag_id") and attr_name.startswith("etl_"))
        )

        if not is_dag:
            continue

        dag_id = getattr(obj, "dag_id", attr_name)
        if not dag_id:
            continue

        # --- Extract tasks ---
        tasks = []
        if hasattr(obj, "tasks"):
            for task in getattr(obj, "tasks", []):
                t_info = TaskInfo(
                    task_id=getattr(task, "task_id", "?"),
                    operator_type=type(task).__name__,
                    upstream_task_ids=[
                        t.task_id for t in getattr(task, "upstream_list", [])
                    ],
                    downstream_task_ids=[
                        t.task_id for t in getattr(task, "downstream_list", [])
                    ],
                    retries=getattr(task, "retries", 0),
                    has_sla=bool(getattr(task, "sla", None)),
                )
                tasks.append(t_info)

        # If no tasks found from .tasks attr, fall back to module-level analysis
        if not tasks:
            tasks = _extract_tasks_from_source(dag_file, module)

        dag_info = DAGInfo(
            dag_id=dag_id,
            description=getattr(obj, "description", getattr(module, "DESCRIPTION", "")),
            schedule=str(getattr(obj, "schedule_interval", "@daily") or "@daily"),
            tags=list(getattr(obj, "tags", []) or []),
            tasks=tasks,
            source_file=str(dag_file),
            owner=_extract_owner(obj),
        )
        results.append(dag_info)

    # Also capture any DAG IDs exported by the module's factory pattern
    if hasattr(module, "get_generated_dag_ids"):
        try:
            for dag_id in module.get_generated_dag_ids():
                # Check we haven't already captured it
                if any(d.dag_id == dag_id for d in results):
                    continue
                tasks = _extract_tasks_from_source(dag_file, module, pipeline_name=dag_id)
                results.append(DAGInfo(
                    dag_id=dag_id,
                    description=f"Dynamic DAG: {dag_id}",
                    schedule="@daily",
                    tags=["dynamic"],
                    tasks=tasks,
                    source_file=str(dag_file),
                    owner="data-engineering",
                ))
        except (AttributeError, TypeError, ValueError) as exc:
            logger.warning("Failed to get generated DAG IDs from %s: %s", dag_file.name, exc)

    return results


def _extract_owner(dag_obj) -> str:
    default_args = getattr(dag_obj, "default_args", {}) or {}
    if isinstance(default_args, dict):
        return default_args.get("owner", "data-engineering")
    return "data-engineering"


def _extract_tasks_from_source(dag_file: Path, module, pipeline_name: str = "") -> List[TaskInfo]:
    """
    Fallback: parse the module's globals to find PythonOperator / similar
    objects that look like tasks.
    """
    tasks = []
    seen_ids = set()

    for name, obj in vars(module).items():
        task_id = getattr(obj, "task_id", None)
        if task_id and task_id not in seen_ids:
            if callable(getattr(obj, "__rshift__", None)) or type(obj).__name__ in (
                "PythonOperator", "BranchPythonOperator", "EmptyOperator",
                "FileSensor", "ExternalTaskSensor", "DataValidationOperator",
            ):
                tasks.append(TaskInfo(
                    task_id=task_id,
                    operator_type=type(obj).__name__,
                    upstream_task_ids=[],
                    downstream_task_ids=[],
                    retries=getattr(obj, "retries", 0),
                    has_sla=bool(getattr(obj, "sla", None)),
                ))
                seen_ids.add(task_id)

    return tasks


# ---------------------------------------------------------------------------
# Static task graph for each known DAG (used when dynamic introspection
# fails — these represent what the DAGs actually define)
# ---------------------------------------------------------------------------

STATIC_TASK_GRAPHS: Dict[str, List[Dict]] = {
    "etl_transactions_pipeline": [
        {"task_id": "extract_data",             "operator": "PythonOperator",       "upstream": [],                    "callable": "extract_data"},
        {"task_id": "validate_data",            "operator": "PythonOperator",       "upstream": ["extract_data"],      "callable": "validate_data"},
        {"task_id": "check_validation_branch",  "operator": "BranchPythonOperator", "upstream": ["validate_data"],     "callable": "check_validation_branch"},
        {"task_id": "handle_validation_failure","operator": "PythonOperator",       "upstream": ["check_validation_branch"], "callable": "handle_validation_failure"},
        {"task_id": "transform_data",           "operator": "PythonOperator",       "upstream": ["check_validation_branch"], "callable": "transform_data"},
        {"task_id": "load_data",                "operator": "PythonOperator",       "upstream": ["transform_data"],    "callable": "load_data"},
        {"task_id": "notify_success",           "operator": "PythonOperator",       "upstream": ["load_data"],         "callable": "notify_success"},
    ],
    "sensor_vendor_file_pipeline": [
        {"task_id": "wait_for_vendor_file",      "operator": "FileSensor",           "upstream": [],                                         "callable": None},
        {"task_id": "wait_for_dimension_refresh","operator": "ExternalTaskSensor",   "upstream": [],                                         "callable": None},
        {"task_id": "check_file_metadata",       "operator": "PythonOperator",       "upstream": ["wait_for_vendor_file","wait_for_dimension_refresh"], "callable": "check_file_metadata"},
        {"task_id": "process_vendor_file",       "operator": "PythonOperator",       "upstream": ["check_file_metadata"],                    "callable": "process_vendor_file"},
        {"task_id": "join_with_dimension",       "operator": "PythonOperator",       "upstream": ["process_vendor_file"],                    "callable": "join_with_dimension"},
        {"task_id": "load_vendor_to_warehouse",  "operator": "PythonOperator",       "upstream": ["join_with_dimension"],                    "callable": "load_vendor_to_warehouse"},
    ],
    "data_quality_pipeline": [
        {"task_id": "start_dq_checks",           "operator": "EmptyOperator",        "upstream": [],                  "callable": None},
        {"task_id": "check_null_rates",          "operator": "PythonOperator",       "upstream": ["start_dq_checks"], "callable": "check_null_rates"},
        {"task_id": "check_row_count",           "operator": "PythonOperator",       "upstream": ["start_dq_checks"], "callable": "check_row_count"},
        {"task_id": "check_duplicates",          "operator": "PythonOperator",       "upstream": ["start_dq_checks"], "callable": "check_duplicates"},
        {"task_id": "check_referential_integrity","operator": "PythonOperator",      "upstream": ["start_dq_checks"], "callable": "check_referential_integrity"},
        {"task_id": "check_data_freshness",      "operator": "PythonOperator",       "upstream": ["start_dq_checks"], "callable": "check_data_freshness"},
        {"task_id": "aggregate_dq_results",      "operator": "PythonOperator",       "upstream": ["check_null_rates","check_row_count","check_duplicates","check_referential_integrity","check_data_freshness"], "callable": "aggregate_dq_results"},
        {"task_id": "branch_on_dq_result",       "operator": "BranchPythonOperator", "upstream": ["aggregate_dq_results"], "callable": "branch_on_dq_result"},
        {"task_id": "publish_to_downstream",     "operator": "PythonOperator",       "upstream": ["branch_on_dq_result"], "callable": "publish_to_downstream"},
        {"task_id": "send_soft_fail_alert",      "operator": "PythonOperator",       "upstream": ["branch_on_dq_result"], "callable": "send_soft_fail_alert"},
        {"task_id": "quarantine_data",           "operator": "PythonOperator",       "upstream": ["branch_on_dq_result"], "callable": "quarantine_data"},
        {"task_id": "finalize_dq_run",           "operator": "PythonOperator",       "upstream": ["publish_to_downstream","send_soft_fail_alert","quarantine_data"], "callable": "finalize_dq_run"},
    ],
    "multi_source_etl_customer_journey": [
        {"task_id": "pipeline_start",        "operator": "EmptyOperator",   "upstream": [],                                              "callable": None},
        {"task_id": "ingest.ingest_crm",     "operator": "PythonOperator",  "upstream": ["pipeline_start"],                              "callable": "ingest_crm_data"},
        {"task_id": "ingest.ingest_erp",     "operator": "PythonOperator",  "upstream": ["pipeline_start"],                              "callable": "ingest_erp_data"},
        {"task_id": "ingest.ingest_analytics","operator": "PythonOperator", "upstream": ["pipeline_start"],                              "callable": "ingest_analytics_data"},
        {"task_id": "ingest.validate_completeness","operator": "PythonOperator","upstream": ["ingest.ingest_crm","ingest.ingest_erp","ingest.ingest_analytics"], "callable": "validate_ingest_completeness"},
        {"task_id": "transform.resolve_entities","operator": "PythonOperator","upstream": ["ingest.validate_completeness"],              "callable": "resolve_customer_entities"},
        {"task_id": "transform.join_sessions","operator": "PythonOperator", "upstream": ["transform.resolve_entities"],                  "callable": "join_sessions_to_customers"},
        {"task_id": "transform.build_journey","operator": "PythonOperator", "upstream": ["transform.join_sessions"],                     "callable": "build_customer_journey"},
        {"task_id": "publish.publish_bi",    "operator": "PythonOperator",  "upstream": ["transform.build_journey"],                     "callable": "publish_to_bi"},
        {"task_id": "publish.publish_ml_features","operator": "PythonOperator","upstream": ["transform.build_journey"],                  "callable": "publish_to_ml_feature_store"},
        {"task_id": "publish.update_catalogue","operator": "PythonOperator","upstream": ["publish.publish_bi","publish.publish_ml_features"], "callable": "update_data_catalogue"},
        {"task_id": "pipeline_end",          "operator": "EmptyOperator",   "upstream": ["publish.update_catalogue"],                    "callable": None},
    ],
}

# Dynamic DAGs share the same task structure
for _name in ["sales", "inventory", "customer_360", "marketing_attribution"]:
    STATIC_TASK_GRAPHS[f"etl_{_name}"] = [
        {"task_id": "extract",  "operator": "PythonOperator", "upstream": [],            "callable": f"extract_{_name}"},
        {"task_id": "validate", "operator": "PythonOperator", "upstream": ["extract"],   "callable": f"validate_{_name}"},
        {"task_id": "transform","operator": "PythonOperator", "upstream": ["validate"],  "callable": f"transform_{_name}"},
        {"task_id": "load",     "operator": "PythonOperator", "upstream": ["transform"], "callable": f"load_{_name}"},
    ]


# ---------------------------------------------------------------------------
# Topological sort (Kahn's algorithm)
# ---------------------------------------------------------------------------

def _topological_sort(tasks: List[Dict]) -> List[str]:
    """Return task_ids in a valid execution order (all upstreams before a task)."""
    in_degree: Dict[str, int] = {t["task_id"]: 0 for t in tasks}
    children: Dict[str, List[str]] = defaultdict(list)

    for task in tasks:
        for up in task.get("upstream", []):
            if up in in_degree:
                in_degree[task["task_id"]] += 1
                children[up].append(task["task_id"])

    queue = deque(tid for tid, deg in in_degree.items() if deg == 0)
    order = []

    while queue:
        current = queue.popleft()
        order.append(current)
        for child in children[current]:
            in_degree[child] -= 1
            if in_degree[child] == 0:
                queue.append(child)

    return order


# ---------------------------------------------------------------------------
# Main simulator class
# ---------------------------------------------------------------------------

class DAGSimulator:
    """
    Local DAG executor that runs task callables in dependency order
    without a running Airflow installation.
    """

    def __init__(self, dags_dir: Path = _DAGS_DIR):
        self.dags_dir = dags_dir
        self._modules: Dict[str, Any] = {}
        self._dag_infos: Dict[str, DAGInfo] = {}
        self._load_all()

    # ------------------------------------------------------------------
    # Module loading
    # ------------------------------------------------------------------

    def _load_all(self):
        """Import all .py files under dags/ and extract DAG metadata."""
        for dag_file in sorted(self.dags_dir.glob("dag_*.py")):
            module = _load_dag_module(dag_file)
            if module is None:
                continue
            self._modules[dag_file.stem] = module
            infos = _extract_dag_info(module, dag_file)
            for info in infos:
                self._dag_infos[info.dag_id] = info

        # Ensure dynamic DAGs are registered even if introspection missed them
        for dag_id in STATIC_TASK_GRAPHS:
            if dag_id not in self._dag_infos:
                self._dag_infos[dag_id] = DAGInfo(
                    dag_id=dag_id,
                    description=f"DAG: {dag_id}",
                    schedule="@daily",
                    tags=["simulated"],
                    tasks=[
                        TaskInfo(task_id=t["task_id"], operator_type=t["operator"])
                        for t in STATIC_TASK_GRAPHS[dag_id]
                    ],
                    source_file=str(self.dags_dir),
                    owner="data-engineering",
                )

    def _get_module_for_dag(self, dag_id: str):
        """Return the loaded module that contains a given dag_id."""
        # Direct match: module stem matches dag_id
        if dag_id in self._modules:
            return self._modules[dag_id]
        # Try the five known DAG files
        mapping = {
            "etl_transactions_pipeline": "dag_01_etl_pipeline",
            "sensor_vendor_file_pipeline": "dag_03_sensor_pipeline",
            "data_quality_pipeline": "dag_04_data_quality",
            "multi_source_etl_customer_journey": "dag_05_multi_source_etl",
        }
        if dag_id in mapping:
            return self._modules.get(mapping[dag_id])
        # Dynamic DAGs come from dag_02
        if dag_id.startswith("etl_"):
            return self._modules.get("dag_02_dynamic_dag")
        return None

    # ------------------------------------------------------------------
    # Public API
    # ------------------------------------------------------------------

    def list_dags(self) -> List[DAGInfo]:
        """Return metadata about all discovered DAGs."""
        return list(self._dag_infos.values())

    def get_dag_graph(self, dag_id: str) -> Dict:
        """
        Return nodes + edges for a DAG, suitable for Plotly/D3 rendering.

        Node dict: {id, label, operator, group, color}
        Edge dict: {source, target}
        """
        task_defs = STATIC_TASK_GRAPHS.get(dag_id, [])
        if not task_defs:
            info = self._dag_infos.get(dag_id)
            if info:
                task_defs = [
                    {"task_id": t.task_id, "operator": t.operator_type, "upstream": t.upstream_task_ids}
                    for t in info.tasks
                ]

        nodes = []
        edges = []
        operator_colors = {
            "PythonOperator": "#42a5f5",
            "BranchPythonOperator": "#ffa726",
            "EmptyOperator": "#bdbdbd",
            "FileSensor": "#66bb6a",
            "ExternalTaskSensor": "#26c6da",
            "DataValidationOperator": "#ab47bc",
        }

        for task in task_defs:
            tid = task["task_id"]
            op = task.get("operator", "PythonOperator")
            group = tid.split(".")[0] if "." in tid else ""
            nodes.append({
                "id": tid,
                "label": tid.split(".")[-1],    # show short name
                "operator": op,
                "group": group,
                "color": operator_colors.get(op, "#78909c"),
            })
            for up in task.get("upstream", []):
                edges.append({"source": up, "target": tid})

        return {
            "dag_id": dag_id,
            "nodes": nodes,
            "edges": edges,
            "task_count": len(nodes),
            "edge_count": len(edges),
        }

    def simulate(self, dag_id: str, task_inputs: Optional[Dict] = None) -> SimulationResult:
        """
        Execute a DAG simulation.

        Parameters
        ----------
        dag_id : str
            ID of the DAG to simulate.
        task_inputs : dict, optional
            Optional per-task input overrides (not used by real tasks but
            available for testing).

        Returns
        -------
        SimulationResult
            Full trace of the simulation with per-task results and XComs.
        """
        task_inputs = task_inputs or {}

        task_defs = STATIC_TASK_GRAPHS.get(dag_id)
        if not task_defs:
            info = self._dag_infos.get(dag_id)
            if not info:
                raise ValueError(f"DAG '{dag_id}' not found. Available: {list(self._dag_infos.keys())}")
            task_defs = [
                {"task_id": t.task_id, "operator": t.operator_type,
                 "upstream": t.upstream_task_ids, "callable": None}
                for t in info.tasks
            ]

        module = self._get_module_for_dag(dag_id)
        xcom = XComStore()
        run_id = f"sim__{dag_id}__{datetime.now(UTC).strftime('%Y%m%dT%H%M%S')}"
        sim_start = time.time()
        sim_start_str = datetime.now(UTC).isoformat()

        task_order = _topological_sort(task_defs)
        task_map = {t["task_id"]: t for t in task_defs}

        task_statuses: Dict[str, str] = {t["task_id"]: STATUS_PENDING for t in task_defs}
        task_results: List[TaskResult] = []
        errors: List[str] = []
        branch_target: Optional[str] = None   # set by BranchPythonOperator

        logger.info(
            "Starting simulation: dag_id=%s run_id=%s tasks=%d",
            dag_id, run_id, len(task_defs),
        )

        for task_id in task_order:
            task_def = task_map.get(task_id, {})
            upstream_ids = task_def.get("upstream", [])
            operator_type = task_def.get("operator", "PythonOperator")

            # ── Skip if upstream failed ──────────────────────────────────
            upstream_failed = any(
                task_statuses.get(u) in (STATUS_FAILED, STATUS_UPSTREAM_FAILED)
                for u in upstream_ids
            )
            if upstream_failed:
                task_statuses[task_id] = STATUS_UPSTREAM_FAILED
                logger.debug("Task %s skipped: upstream task failed", task_id)
                task_results.append(TaskResult(
                    task_id=task_id, status=STATUS_UPSTREAM_FAILED,
                    start_time=datetime.now(UTC).isoformat(),
                    end_time=datetime.now(UTC).isoformat(),
                    duration_ms=0, error="Upstream task failed",
                ))
                continue

            # ── Skip if branch operator excluded this task ────────────────
            if branch_target is not None:
                # If this task is not on the active branch AND has branch operator upstream,
                # skip it (but don't affect further downstream)
                if not upstream_ids:
                    pass
                elif all(task_statuses.get(u) in (STATUS_SKIPPED, STATUS_SUCCESS, STATUS_PENDING)
                         for u in upstream_ids):
                    # Check if any direct upstream is a BranchPythonOperator that didn't choose us
                    branch_parents = [
                        u for u in upstream_ids
                        if task_map.get(u, {}).get("operator") == "BranchPythonOperator"
                    ]
                    if branch_parents and task_id != branch_target and branch_target is not None:
                        # Check it's a direct branch child
                        is_direct_branch_child = any(
                            task_id in (task_map.get(u, {}).get("downstream", []) or
                                        [t["task_id"] for t in task_defs
                                         if u in t.get("upstream", [])])
                            for u in branch_parents
                        )
                        if is_direct_branch_child:
                            task_statuses[task_id] = STATUS_SKIPPED
                            task_results.append(TaskResult(
                                task_id=task_id, status=STATUS_SKIPPED,
                                start_time=datetime.now(UTC).isoformat(),
                                end_time=datetime.now(UTC).isoformat(),
                                duration_ms=0, error="Skipped by branch operator",
                            ))
                            continue

                # For finalize/join tasks after branch: allow even if some upstreams skipped
                all_upstreams_done = all(
                    task_statuses.get(u) in (STATUS_SUCCESS, STATUS_SKIPPED, STATUS_FAILED)
                    for u in upstream_ids
                )
                if not all_upstreams_done and upstream_ids:
                    task_statuses[task_id] = STATUS_PENDING
                    continue

            # Skip EmptyOperator/sensors quickly — they succeed instantly
            if operator_type in ("EmptyOperator",):
                task_statuses[task_id] = STATUS_SUCCESS
                task_results.append(TaskResult(
                    task_id=task_id, status=STATUS_SUCCESS,
                    start_time=datetime.now(UTC).isoformat(),
                    end_time=datetime.now(UTC).isoformat(),
                    duration_ms=1, return_value=None,
                ))
                continue

            if operator_type in ("FileSensor", "ExternalTaskSensor"):
                # Sensors succeed in simulator (no actual waiting)
                task_statuses[task_id] = STATUS_SUCCESS
                task_results.append(TaskResult(
                    task_id=task_id, status=STATUS_SUCCESS,
                    start_time=datetime.now(UTC).isoformat(),
                    end_time=datetime.now(UTC).isoformat(),
                    duration_ms=50,
                    return_value={"sensor": "triggered", "note": "Simulated — no actual file/task wait"},
                ))
                xcom.push(task_id, "sensor_result", {"triggered": True, "simulated": True})
                continue

            # ── Find and execute the Python callable ─────────────────────
            callable_name = task_def.get("callable")
            python_fn = None

            if callable_name and module:
                python_fn = getattr(module, callable_name, None)

            # If we can't find by name, skip gracefully
            if python_fn is None:
                task_statuses[task_id] = STATUS_SUCCESS
                task_results.append(TaskResult(
                    task_id=task_id, status=STATUS_SUCCESS,
                    start_time=datetime.now(UTC).isoformat(),
                    end_time=datetime.now(UTC).isoformat(),
                    duration_ms=5,
                    return_value={"note": f"No callable found for {task_id} — skipped in simulator"},
                ))
                continue

            # ── Execute with retry logic ──────────────────────────────────
            fake_ti = FakeTaskInstance(task_id, xcom)
            context = {
                "ti": fake_ti,
                "execution_date": datetime.now(UTC),
                "dag_run": {"run_id": run_id},
                "task": {"task_id": task_id},
                "ds": datetime.now(UTC).strftime("%Y-%m-%d"),
                "ts": datetime.now(UTC).isoformat(),
                **(task_inputs.get(task_id, {})),
            }

            task_statuses[task_id] = STATUS_RUNNING
            t_start = time.time()
            t_start_str = datetime.now(UTC).isoformat()

            attempt = 1
            max_attempts = MAX_RETRIES    # configurable via MAX_RETRIES env var
            last_error = None
            return_value = None
            succeeded = False

            while attempt <= max_attempts and not succeeded:
                try:
                    return_value = python_fn(**context)
                    succeeded = True
                except Exception as exc:
                    last_error = str(exc)
                    logger.warning(
                        "Task %s attempt %d/%d failed: %s",
                        task_id, attempt, max_attempts, exc,
                    )
                    attempt += 1
                    if attempt <= max_attempts:
                        time.sleep(0.01)  # tiny delay to simulate retry backoff

            t_end = time.time()
            duration_ms = int((t_end - t_start) * 1000)

            if succeeded:
                task_statuses[task_id] = STATUS_SUCCESS

                # Handle BranchPythonOperator: return value is the next task_id
                if operator_type == "BranchPythonOperator" and isinstance(return_value, str):
                    branch_target = return_value
                    logger.info("Branch operator %s chose: %s", task_id, branch_target)

                task_results.append(TaskResult(
                    task_id=task_id,
                    status=STATUS_SUCCESS,
                    start_time=t_start_str,
                    end_time=datetime.now(UTC).isoformat(),
                    duration_ms=duration_ms,
                    attempt=attempt - 1,
                    return_value=return_value if _is_serialisable(return_value) else str(return_value),
                    xcoms_pushed=fake_ti.xcom_data,
                ))
            else:
                task_statuses[task_id] = STATUS_FAILED
                errors.append(f"{task_id}: {last_error}")

                task_results.append(TaskResult(
                    task_id=task_id,
                    status=STATUS_FAILED,
                    start_time=t_start_str,
                    end_time=datetime.now(UTC).isoformat(),
                    duration_ms=duration_ms,
                    attempt=attempt - 1,
                    error=last_error,
                    xcoms_pushed=fake_ti.xcom_data,
                ))

        sim_end = time.time()
        overall_status = (
            STATUS_SUCCESS if all(
                r.status in (STATUS_SUCCESS, STATUS_SKIPPED)
                for r in task_results
            ) else STATUS_FAILED
        )

        duration_ms = int((sim_end - sim_start) * 1000)
        succeeded_count = sum(1 for r in task_results if r.status == STATUS_SUCCESS)
        failed_count = sum(1 for r in task_results if r.status == STATUS_FAILED)
        skipped_count = sum(1 for r in task_results if r.status == STATUS_SKIPPED)

        logger.info(
            "Simulation complete: dag_id=%s status=%s duration=%dms "
            "tasks=%d succeeded=%d failed=%d skipped=%d errors=%d",
            dag_id, overall_status, duration_ms,
            len(task_results), succeeded_count, failed_count, skipped_count, len(errors),
        )

        return SimulationResult(
            dag_id=dag_id,
            run_id=run_id,
            status=overall_status,
            start_time=sim_start_str,
            end_time=datetime.now(UTC).isoformat(),
            duration_ms=duration_ms,
            task_results=task_results,
            xcoms=xcom.all_xcoms(),
            task_order=task_order,
            errors=errors,
        )


def _is_serialisable(obj) -> bool:
    """Quick check whether an object is JSON-safe."""
    import json
    try:
        json.dumps(obj)
        return True
    except (TypeError, ValueError):
        return False


# ---------------------------------------------------------------------------
# Module-level singleton
# ---------------------------------------------------------------------------
_simulator_instance: Optional[DAGSimulator] = None


def get_simulator() -> DAGSimulator:
    """Return the module-level singleton DAGSimulator (lazy init)."""
    global _simulator_instance
    if _simulator_instance is None:
        _simulator_instance = DAGSimulator()
    return _simulator_instance


def reset_simulator():
    """Force re-initialisation (useful after DAG files change)."""
    global _simulator_instance
    _simulator_instance = None


__all__ = [
    "DAGSimulator",
    "SimulationResult",
    "TaskResult",
    "DAGInfo",
    "TaskInfo",
    "XComStore",
    "get_simulator",
    "reset_simulator",
    "STATUS_SUCCESS",
    "STATUS_FAILED",
    "STATUS_PENDING",
    "STATUS_RUNNING",
    "STATUS_SKIPPED",
    "STATUS_UPSTREAM_FAILED",
    "STATUS_COLORS",
]
