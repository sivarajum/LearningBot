"""
FastAPI service for the Airflow Orchestration POC
==================================================
Endpoints:
  GET  /health               — liveness check
  GET  /dags                 — list all DAGs with metadata
  GET  /dags/{dag_id}        — DAG detail + task list
  POST /dags/{dag_id}/run    — simulate a DAG run
  GET  /dags/{dag_id}/graph  — task dependency graph (nodes + edges)
  GET  /xcoms                — XComs from the last simulation run
  GET  /concepts             — Airflow concepts dictionary for learning
"""

import logging
import os
from datetime import UTC, datetime
from typing import Any, Dict, List, Optional

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

# Local imports
from src.settings import CORS_ORIGINS
from src.simulator import (
    STATUS_COLORS,
    DAGInfo,
    SimulationResult,
    get_simulator,
    reset_simulator,
)

logger = logging.getLogger(__name__)

# ---------------------------------------------------------------------------
# App
# ---------------------------------------------------------------------------

app = FastAPI(
    title="Airflow Orchestration POC API",
    description=(
        "Local simulator API for POC-07: Enterprise Airflow Orchestration Platform. "
        "Demonstrates DAG design patterns, sensors, XComs, dynamic DAGs, and DQ pipelines."
    ),
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.middleware("http")
async def log_requests(request, call_next):
    """Log every incoming request with method, path, and response status."""
    logger.info("Request: %s %s", request.method, request.url.path)
    response = await call_next(request)
    logger.info("Response: %s %s -> %d", request.method, request.url.path, response.status_code)
    return response


# In-memory store for the last simulation result per dag_id
_last_simulations: Dict[str, dict] = {}


# ---------------------------------------------------------------------------
# Pydantic models
# ---------------------------------------------------------------------------

class HealthResponse(BaseModel):
    status: str
    timestamp: str
    version: str
    airflow_mode: str


class TaskInfoResponse(BaseModel):
    task_id: str
    operator_type: str
    upstream_task_ids: List[str]
    downstream_task_ids: List[str]
    retries: int
    has_sla: bool


class DAGListItem(BaseModel):
    dag_id: str
    description: str
    schedule: str
    tags: List[str]
    task_count: int
    owner: str
    source_file: str


class DAGDetailResponse(BaseModel):
    dag_id: str
    description: str
    schedule: str
    tags: List[str]
    owner: str
    tasks: List[TaskInfoResponse]
    task_count: int


class RunRequest(BaseModel):
    task_inputs: Optional[Dict[str, Any]] = None
    conf: Optional[Dict[str, Any]] = None


class TaskResultResponse(BaseModel):
    task_id: str
    status: str
    start_time: str
    end_time: str
    duration_ms: int
    attempt: int
    return_value: Optional[Any]
    error: Optional[str]
    xcoms_pushed: Dict[str, Any]
    status_color: str


class SimulationResponse(BaseModel):
    dag_id: str
    run_id: str
    status: str
    start_time: str
    end_time: str
    duration_ms: int
    task_results: List[TaskResultResponse]
    xcoms: Dict[str, Any]
    task_order: List[str]
    errors: List[str]
    summary: Dict[str, Any]


class GraphNode(BaseModel):
    id: str
    label: str
    operator: str
    group: str
    color: str


class GraphEdge(BaseModel):
    source: str
    target: str


class GraphResponse(BaseModel):
    dag_id: str
    nodes: List[GraphNode]
    edges: List[GraphEdge]
    task_count: int
    edge_count: int


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _dag_info_to_list_item(info: DAGInfo) -> DAGListItem:
    return DAGListItem(
        dag_id=info.dag_id,
        description=info.description,
        schedule=info.schedule,
        tags=info.tags,
        task_count=len(info.tasks),
        owner=info.owner,
        source_file=info.source_file,
    )


def _simulation_to_response(result: SimulationResult) -> SimulationResponse:
    task_responses = []
    for tr in result.task_results:
        task_responses.append(TaskResultResponse(
            task_id=tr.task_id,
            status=tr.status,
            start_time=tr.start_time,
            end_time=tr.end_time,
            duration_ms=tr.duration_ms,
            attempt=tr.attempt,
            return_value=tr.return_value,
            error=tr.error,
            xcoms_pushed=tr.xcoms_pushed or {},
            status_color=STATUS_COLORS.get(tr.status, "#78909c"),
        ))

    success_count = sum(1 for t in result.task_results if t.status == "success")
    failed_count = sum(1 for t in result.task_results if t.status == "failed")
    skipped_count = sum(1 for t in result.task_results if t.status == "skipped")

    return SimulationResponse(
        dag_id=result.dag_id,
        run_id=result.run_id,
        status=result.status,
        start_time=result.start_time,
        end_time=result.end_time,
        duration_ms=result.duration_ms,
        task_results=task_responses,
        xcoms=result.xcoms,
        task_order=result.task_order,
        errors=result.errors,
        summary={
            "total_tasks": len(result.task_results),
            "succeeded": success_count,
            "failed": failed_count,
            "skipped": skipped_count,
            "xcom_count": len(result.xcoms),
        },
    )


# ---------------------------------------------------------------------------
# Endpoints
# ---------------------------------------------------------------------------

@app.get("/health", response_model=HealthResponse, tags=["system"])
async def health() -> HealthResponse:
    """Liveness check."""
    try:
        import airflow
        airflow_mode = f"airflow {airflow.__version__} installed"
    except ImportError:
        airflow_mode = "simulator mode (no Airflow installed)"

    return HealthResponse(
        status="healthy",
        timestamp=datetime.now(UTC).isoformat(),
        version="1.0.0",
        airflow_mode=airflow_mode,
    )


@app.get("/dags", response_model=List[DAGListItem], tags=["dags"])
async def list_dags() -> list[DAGListItem]:
    """
    List all discovered DAGs with metadata.

    Returns all DAGs found under dags/, including dynamically-generated ones.
    """
    sim = get_simulator()
    dags = sim.list_dags()
    return [_dag_info_to_list_item(d) for d in dags]


@app.get("/dags/{dag_id}", response_model=DAGDetailResponse, tags=["dags"])
async def get_dag(dag_id: str) -> DAGDetailResponse:
    """
    Return detailed information about a specific DAG, including all task definitions.
    """
    sim = get_simulator()
    dag_list = {d.dag_id: d for d in sim.list_dags()}

    if dag_id not in dag_list:
        raise HTTPException(
            status_code=404,
            detail=f"DAG '{dag_id}' not found. Available: {list(dag_list.keys())}",
        )

    info = dag_list[dag_id]
    return DAGDetailResponse(
        dag_id=info.dag_id,
        description=info.description,
        schedule=info.schedule,
        tags=info.tags,
        owner=info.owner,
        tasks=[
            TaskInfoResponse(
                task_id=t.task_id,
                operator_type=t.operator_type,
                upstream_task_ids=t.upstream_task_ids,
                downstream_task_ids=t.downstream_task_ids,
                retries=t.retries,
                has_sla=t.has_sla,
            )
            for t in info.tasks
        ],
        task_count=len(info.tasks),
    )


@app.post("/dags/{dag_id}/run", response_model=SimulationResponse, tags=["simulation"])
async def run_dag(dag_id: str, request: RunRequest = RunRequest()) -> SimulationResponse:
    """
    Simulate a DAG run.

    Executes all task callables in topological order, passing XComs between
    tasks exactly as Airflow would.  Returns a full execution trace.

    **Note**: Branch operators are respected — only the chosen branch executes.
    Sensors succeed instantly in simulator mode.
    """
    sim = get_simulator()

    try:
        result = sim.simulate(dag_id=dag_id, task_inputs=request.task_inputs or {})
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except (RuntimeError, TypeError, KeyError, AttributeError, OSError) as e:
        logger.exception("Simulation error for dag_id=%s", dag_id)
        raise HTTPException(status_code=500, detail=f"Simulation failed: {e}")

    response = _simulation_to_response(result)
    _last_simulations[dag_id] = response.model_dump()
    return response


@app.get("/dags/{dag_id}/graph", response_model=GraphResponse, tags=["dags"])
async def get_dag_graph(dag_id: str) -> GraphResponse:
    """
    Return the task dependency graph for a DAG.

    Each node has: id, label, operator type, task group, and a colour
    for rendering.  Edges represent >> dependencies.
    """
    sim = get_simulator()

    try:
        graph = sim.get_dag_graph(dag_id)
    except (ValueError, KeyError) as e:
        logger.warning("Failed to get graph for dag_id=%s: %s", dag_id, e)
        raise HTTPException(status_code=404, detail=str(e))

    if not graph.get("nodes"):
        raise HTTPException(status_code=404, detail=f"No graph data for DAG '{dag_id}'")

    return GraphResponse(
        dag_id=graph["dag_id"],
        nodes=[GraphNode(**n) for n in graph["nodes"]],
        edges=[GraphEdge(**e) for e in graph["edges"]],
        task_count=graph["task_count"],
        edge_count=graph["edge_count"],
    )


@app.get("/xcoms", tags=["simulation"])
async def get_xcoms(dag_id: Optional[str] = None) -> Dict[str, Any]:
    """
    Return XCom data from the last simulation run.

    Optionally filter by dag_id.
    """
    if dag_id:
        run_data = _last_simulations.get(dag_id)
        if not run_data:
            return {"message": f"No simulation run found for dag_id='{dag_id}'", "xcoms": {}}
        return {
            "dag_id": dag_id,
            "run_id": run_data.get("run_id"),
            "xcoms": run_data.get("xcoms", {}),
        }

    # Return all
    return {
        "runs": {
            dag_id: {
                "run_id": data.get("run_id"),
                "xcoms": data.get("xcoms", {}),
            }
            for dag_id, data in _last_simulations.items()
        }
    }


@app.get("/concepts", tags=["learning"])
async def get_concepts() -> Dict[str, Any]:
    """
    Return a structured dictionary of Airflow concepts.

    Useful for learning and interview preparation.
    """
    return {
        "dag": {
            "full_name": "Directed Acyclic Graph",
            "definition": (
                "A collection of tasks with directional dependencies, "
                "forming a graph with no cycles.  The fundamental unit of "
                "work in Airflow."
            ),
            "key_properties": [
                "dag_id: unique identifier",
                "schedule_interval: cron or preset (@daily, @hourly)",
                "start_date: first execution date",
                "catchup: whether to backfill missed runs",
                "max_active_runs: concurrency limit",
                "default_args: shared config for all tasks",
            ],
            "example": "with DAG('my_dag', schedule_interval='@daily') as dag: ...",
        },
        "operators": {
            "definition": "Templates for tasks — define what a task does.",
            "types": {
                "PythonOperator": "Run a Python function",
                "BashOperator": "Run a bash command",
                "BranchPythonOperator": "Conditional routing — returns task_id of next task",
                "EmptyOperator": "No-op — used as start/end gates",
                "PostgresOperator": "Execute SQL on Postgres",
                "BigQueryOperator": "Execute SQL on BigQuery",
                "S3ToRedshiftOperator": "Transfer data from S3 to Redshift",
                "TriggerDagRunOperator": "Trigger another DAG from within a DAG",
                "SimpleHttpOperator": "Make an HTTP request",
                "EmailOperator": "Send an email",
            },
            "custom_operators": (
                "Extend BaseOperator, override execute(context). "
                "Package in plugins/operators/ for auto-discovery."
            ),
        },
        "tasks": {
            "definition": "A specific instance of an operator in a DAG.",
            "key_properties": [
                "task_id: unique within a DAG",
                "retries: number of retry attempts on failure",
                "retry_delay: time between retries",
                "execution_timeout: max task runtime before kill",
                "sla: expected completion time (triggers SLA miss callback)",
                "trigger_rule: when to run based on upstream states",
            ],
        },
        "xcoms": {
            "full_name": "Cross-Communications",
            "definition": (
                "Mechanism for tasks to exchange small amounts of data. "
                "Stored in the metadata database."
            ),
            "push": "ti.xcom_push(key='my_key', value=my_value)",
            "pull": "ti.xcom_pull(task_ids='upstream_task', key='my_key')",
            "limitations": [
                "Not for large data — use S3/GCS for datasets",
                "Serialised as JSON — must be JSON-serialisable",
                "Visible in Airflow UI under Admin > XComs",
            ],
        },
        "sensors": {
            "definition": (
                "Special operators that wait for a condition to be true "
                "before allowing downstream tasks to proceed."
            ),
            "common_sensors": {
                "FileSensor": "Wait for a file to exist on a filesystem",
                "S3KeySensor": "Wait for an S3 object to exist",
                "ExternalTaskSensor": "Wait for a task in another DAG to complete",
                "HttpSensor": "Wait for an HTTP endpoint to return a success status",
                "SqlSensor": "Wait for a SQL query to return a non-empty result",
                "TimeDeltaSensor": "Wait for a time offset from execution_date",
            },
            "modes": {
                "poke": "Hold a worker slot and poll periodically (simple, wastes resources)",
                "reschedule": "Release slot between pokes (production best practice for long waits)",
            },
        },
        "executors": {
            "definition": "The mechanism that runs task instances.",
            "types": {
                "SequentialExecutor": "One task at a time, dev only",
                "LocalExecutor": "Parallel on one machine using multiprocessing",
                "CeleryExecutor": "Distributed — tasks sent to Celery workers (most common prod setup)",
                "KubernetesExecutor": "Each task runs in its own K8s pod (cloud-native)",
                "CeleryKubernetesExecutor": "Hybrid — Celery + K8s for burst capacity",
            },
        },
        "dynamic_dags": {
            "definition": (
                "Generate multiple DAGs programmatically at import time "
                "by iterating over a config and calling globals()[dag_id] = dag."
            ),
            "pattern": (
                "for pipeline in config['pipelines']:\n"
                "    dag_id = f'etl_{pipeline[\"name\"]}'\n"
                "    with DAG(dag_id, ...) as dag:\n"
                "        ...\n"
                "    globals()[dag_id] = dag"
            ),
            "use_cases": [
                "Many similar pipelines varying only in source/destination",
                "Tenant-specific pipelines",
                "Feature pipeline per ML model",
            ],
        },
        "task_groups": {
            "definition": (
                "Visual grouping of related tasks in the Airflow UI. "
                "Replacement for deprecated SubDAGs since Airflow 2.0."
            ),
            "benefits": [
                "Collapse/expand groups in Graph View",
                "No extra scheduler overhead (unlike SubDAGs)",
                "Task IDs scoped as 'group_id.task_id'",
            ],
        },
        "trigger_rules": {
            "definition": "Control when a task runs based on its upstream tasks' states.",
            "rules": {
                "all_success": "Default — all upstreams must succeed",
                "all_done": "Run regardless of upstream outcome (success/failed/skipped)",
                "all_failed": "Run only if all upstreams failed",
                "one_success": "Run if at least one upstream succeeded",
                "one_failed": "Run if at least one upstream failed",
                "none_failed": "Run if no upstreams failed (skipped OK)",
                "none_failed_min_one_success": "At least one success, none failed",
            },
        },
        "hooks": {
            "definition": (
                "Interface to external systems.  Operators use hooks internally. "
                "Hooks read connection config from Airflow's connection store."
            ),
            "examples": [
                "PostgresHook → connect to Postgres",
                "S3Hook → read/write S3",
                "BigQueryHook → interact with BigQuery",
                "HttpHook → make HTTP calls",
                "SlackWebhookHook → send Slack messages",
            ],
        },
        "connections": {
            "definition": "Named credentials stored in Airflow (UI or env vars).",
            "env_var_pattern": "AIRFLOW_CONN_{CONN_ID_UPPERCASE}=scheme://user:pass@host:port/schema",
            "example": "AIRFLOW_CONN_POSTGRES_DEFAULT=postgresql://user:pass@localhost:5432/db",
        },
        "pools": {
            "definition": (
                "Resource limits to prevent overwhelming external systems. "
                "Tasks can be assigned to a pool; Airflow will not run more "
                "than pool.slots tasks simultaneously."
            ),
            "use_case": "Limit concurrent API calls to a rate-limited vendor endpoint",
        },
        "sla": {
            "full_name": "Service Level Agreement",
            "definition": (
                "Expected completion time for a task or DAG.  When missed, "
                "Airflow calls sla_miss_callback and can send email alerts."
            ),
            "task_level": "sla=timedelta(hours=2) on the operator",
            "dag_level": "sla_miss_callback=my_callback on the DAG",
        },
    }


@app.post("/reload", tags=["system"])
async def reload_dags() -> Dict[str, Any]:
    """Force reload of all DAG modules (useful during development)."""
    reset_simulator()
    sim = get_simulator()
    dag_ids = [d.dag_id for d in sim.list_dags()]
    return {"reloaded": True, "dag_count": len(dag_ids), "dag_ids": dag_ids}


# ---------------------------------------------------------------------------
# Dev server entry point
# ---------------------------------------------------------------------------
if __name__ == "__main__":
    import uvicorn

    from src.settings import API_HOST, API_PORT, LOG_LEVEL

    uvicorn.run(
        "src.api:app",
        host=API_HOST,
        port=API_PORT,
        reload=True,
        log_level=LOG_LEVEL.lower(),
    )
