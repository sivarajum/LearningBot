"""
Streamlit UI for the Airflow Orchestration POC
===============================================
Four tabs:
  1. DAGs         — list all DAGs, expand to see tasks / schedule
  2. Run          — select DAG, trigger simulation, show step-by-step trace
  3. Task Graph   — Plotly dependency graph for any DAG
  4. Learn        — Airflow concepts explained with examples

Run:
    streamlit run src/ui.py
"""

import json
import sys
from pathlib import Path

# ---------------------------------------------------------------------------
# Path setup so local imports work when running directly
# ---------------------------------------------------------------------------
_ROOT = Path(__file__).resolve().parent.parent
if str(_ROOT) not in sys.path:
    sys.path.insert(0, str(_ROOT))

import streamlit as st

# ---------------------------------------------------------------------------
# Page config — must be first Streamlit call
# ---------------------------------------------------------------------------
st.set_page_config(
    page_title="Airflow Orchestration POC",
    page_icon="pipeline_icon",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ---------------------------------------------------------------------------
# Lazy imports so the page loads even if packages are missing
# ---------------------------------------------------------------------------
try:
    import plotly.graph_objects as go
    PLOTLY_AVAILABLE = True
except ImportError:
    PLOTLY_AVAILABLE = False

try:
    from src.simulator import STATUS_COLORS, get_simulator, reset_simulator
    SIMULATOR_AVAILABLE = True
except Exception as e:
    SIMULATOR_AVAILABLE = False
    _sim_error = str(e)

# ---------------------------------------------------------------------------
# Custom CSS
# ---------------------------------------------------------------------------
st.markdown("""
<style>
.dag-card {
    background: #1e2332;
    border-radius: 8px;
    padding: 16px 20px;
    margin-bottom: 10px;
    border-left: 4px solid #42a5f5;
}
.task-success  { color: #4caf50; font-weight: 700; }
.task-failed   { color: #f44336; font-weight: 700; }
.task-skipped  { color: #ff9800; font-weight: 700; }
.task-running  { color: #2196f3; font-weight: 700; }
.task-pending  { color: #9e9e9e; font-weight: 700; }
.concept-box {
    background: #12161f;
    border-left: 3px solid #42a5f5;
    padding: 12px 16px;
    border-radius: 4px;
    margin: 8px 0;
}
.metric-row { display: flex; gap: 12px; flex-wrap: wrap; }
.big-metric { font-size: 2rem; font-weight: 800; color: #42a5f5; }
</style>
""", unsafe_allow_html=True)

# ---------------------------------------------------------------------------
# Header
# ---------------------------------------------------------------------------
st.title("Airflow Orchestration POC")
st.caption("POC-07 — Enterprise DAG Design Patterns | Lead Data Engineer Interview Prep")

# ---------------------------------------------------------------------------
# Sidebar
# ---------------------------------------------------------------------------
with st.sidebar:
    st.header("Navigation")
    tab_names = ["DAGs", "Run Simulation", "Task Graph", "Learn Concepts"]
    selected_tab = st.radio("Go to", tab_names, label_visibility="collapsed")

    st.divider()
    st.subheader("Status")
    if SIMULATOR_AVAILABLE:
        st.success("Simulator ready")
    else:
        st.error(f"Simulator unavailable: {_sim_error}")

    try:
        import airflow
        st.info(f"Airflow {airflow.__version__} installed")
    except ImportError:
        st.warning("Airflow not installed — simulator mode active")

    st.divider()
    if st.button("Reload DAGs", use_container_width=True):
        if SIMULATOR_AVAILABLE:
            reset_simulator()
            st.success("DAGs reloaded")

# ---------------------------------------------------------------------------
# Helper: get simulator with error handling
# ---------------------------------------------------------------------------

@st.cache_resource
def _get_sim():
    if not SIMULATOR_AVAILABLE:
        return None
    return get_simulator()


def _sim():
    return _get_sim() if SIMULATOR_AVAILABLE else None


# ---------------------------------------------------------------------------
# TAB 1: DAGs
# ---------------------------------------------------------------------------

if selected_tab == "DAGs":
    st.header("Discovered DAGs")
    st.caption("All DAGs parsed from the dags/ directory — including dynamically-generated ones.")

    sim = _sim()
    if sim is None:
        st.error("Simulator not available.")
        st.stop()

    dags = sim.list_dags()

    if not dags:
        st.warning("No DAGs found. Check the dags/ directory.")
        st.stop()

    # Summary metrics
    col1, col2, col3, col4 = st.columns(4)
    col1.metric("Total DAGs", len(dags))
    col2.metric("Dynamic DAGs", sum(1 for d in dags if "dynamic" in d.tags))
    col3.metric("Total Tasks", sum(len(d.tasks) for d in dags))
    col4.metric("Unique Owners", len({d.owner for d in dags}))

    st.divider()

    # DAG cards
    for dag in dags:
        with st.expander(f"**{dag.dag_id}** — {dag.schedule}", expanded=False):
            c1, c2 = st.columns([3, 1])
            with c1:
                st.markdown(f"**Description:** {dag.description}")
                st.markdown(f"**Owner:** `{dag.owner}`")
                st.markdown(f"**Tags:** {' '.join(f'`{t}`' for t in dag.tags) if dag.tags else 'none'}")
            with c2:
                st.metric("Tasks", len(dag.tasks))
                graph = sim.get_dag_graph(dag.dag_id)
                st.metric("Edges", graph.get("edge_count", 0))

            if dag.tasks:
                st.markdown("**Tasks:**")
                task_data = []
                for t in dag.tasks:
                    task_data.append({
                        "task_id": t.task_id,
                        "operator": t.operator_type,
                        "retries": t.retries,
                        "has_sla": "yes" if t.has_sla else "no",
                    })
                st.dataframe(task_data, use_container_width=True, hide_index=True)


# ---------------------------------------------------------------------------
# TAB 2: Run Simulation
# ---------------------------------------------------------------------------

elif selected_tab == "Run Simulation":
    st.header("Run DAG Simulation")
    st.caption(
        "Select a DAG and trigger a local simulation. "
        "Task callables execute in topological order; XComs are passed between tasks."
    )

    sim = _sim()
    if sim is None:
        st.error("Simulator not available.")
        st.stop()

    dags = sim.list_dags()
    dag_ids = [d.dag_id for d in dags]

    selected_dag_id = st.selectbox(
        "Select DAG",
        dag_ids,
        index=0,
        help="Choose which DAG to simulate",
    )

    dag_info_map = {d.dag_id: d for d in dags}
    if selected_dag_id in dag_info_map:
        info = dag_info_map[selected_dag_id]
        st.markdown(f"**Description:** {info.description}")
        st.markdown(f"**Schedule:** `{info.schedule}`  |  **Tasks:** {len(info.tasks)}")

    if st.button("Run Simulation", type="primary", use_container_width=True):
        with st.spinner(f"Simulating {selected_dag_id}..."):
            try:
                result = sim.simulate(selected_dag_id)
                st.session_state["last_result"] = result
                st.session_state["last_dag_id"] = selected_dag_id
            except Exception as e:
                st.error(f"Simulation failed: {e}")
                st.stop()

    # Display results
    result = st.session_state.get("last_result")
    if result and st.session_state.get("last_dag_id") == selected_dag_id:
        st.divider()

        # Overall status
        status_color = "#4caf50" if result.status == "success" else "#f44336"
        st.markdown(
            f"### Run: `{result.run_id}`  "
            f"<span style='color:{status_color}; font-weight:800;'>{result.status.upper()}</span>",
            unsafe_allow_html=True,
        )

        col1, col2, col3, col4 = st.columns(4)
        col1.metric("Duration", f"{result.duration_ms}ms")
        col2.metric("Tasks", len(result.task_results))
        col3.metric("Succeeded", sum(1 for t in result.task_results if t.status == "success"))
        col4.metric("XComs", len(result.xcoms))

        st.divider()

        # Task-by-task trace
        st.subheader("Task Execution Trace")
        for tr in result.task_results:
            color = STATUS_COLORS.get(tr.status, "#78909c")
            status_emoji = {
                "success": "✓",
                "failed": "✗",
                "skipped": "→",
                "running": "⟳",
                "pending": "○",
                "upstream_failed": "↑✗",
            }.get(tr.status, "?")

            with st.expander(
                f"{status_emoji} **{tr.task_id}** — {tr.status.upper()} ({tr.duration_ms}ms)",
                expanded=(tr.status == "failed"),
            ):
                c1, c2, c3 = st.columns(3)
                c1.markdown(f"**Status:** :{('green' if tr.status == 'success' else 'red' if tr.status == 'failed' else 'orange')}[{tr.status}]")
                c2.markdown(f"**Duration:** {tr.duration_ms}ms")
                c3.markdown(f"**Attempt:** {tr.attempt}")

                if tr.error:
                    st.error(f"Error: {tr.error}")

                if tr.xcoms_pushed:
                    st.markdown("**XComs pushed:**")
                    st.json(tr.xcoms_pushed)

                if tr.return_value is not None:
                    st.markdown("**Return value:**")
                    if isinstance(tr.return_value, dict):
                        st.json(tr.return_value)
                    else:
                        st.code(str(tr.return_value))

        # XCom viewer
        if result.xcoms:
            st.divider()
            st.subheader("XCom Store")
            st.caption("Values exchanged between tasks during this run")

            xcom_rows = []
            for key, value in result.xcoms.items():
                parts = key.split("/", 1)
                task_id = parts[0] if len(parts) >= 1 else key
                xcom_key = parts[1] if len(parts) == 2 else ""
                xcom_rows.append({
                    "task_id": task_id,
                    "key": xcom_key,
                    "value": json.dumps(value, default=str)[:200],
                })
            st.dataframe(xcom_rows, use_container_width=True, hide_index=True)

        # Errors
        if result.errors:
            st.divider()
            st.subheader("Errors")
            for err in result.errors:
                st.error(err)


# ---------------------------------------------------------------------------
# TAB 3: Task Graph
# ---------------------------------------------------------------------------

elif selected_tab == "Task Graph":
    st.header("Task Dependency Graph")
    st.caption("Visual representation of task >> task dependencies in each DAG.")

    if not PLOTLY_AVAILABLE:
        st.warning("plotly not installed. Run `pip install plotly` to enable graph visualisation.")
        st.info("Task graph data is still available via the API at /dags/{dag_id}/graph")
        st.stop()

    sim = _sim()
    if sim is None:
        st.error("Simulator not available.")
        st.stop()

    dags = sim.list_dags()
    dag_ids = [d.dag_id for d in dags]

    selected = st.selectbox("Select DAG", dag_ids)
    graph = sim.get_dag_graph(selected)

    if not graph.get("nodes"):
        st.warning("No graph data available for this DAG.")
        st.stop()

    st.markdown(f"**{graph['task_count']} tasks**, **{graph['edge_count']} edges**")

    # Build layout using a simple layered approach
    nodes = graph["nodes"]
    edges = graph["edges"]

    # Determine depths via BFS from roots
    adjacency = {n["id"]: [] for n in nodes}
    parent_count = {n["id"]: 0 for n in nodes}
    for e in edges:
        adjacency[e["source"]].append(e["target"])
        parent_count[e["target"]] = parent_count.get(e["target"], 0) + 1

    depths: dict = {}
    from collections import deque as _deque
    roots = [n["id"] for n in nodes if parent_count.get(n["id"], 0) == 0]
    q = _deque()
    for r in roots:
        depths[r] = 0
        q.append(r)
    while q:
        nid = q.popleft()
        for child in adjacency.get(nid, []):
            if child not in depths:
                depths[child] = depths[nid] + 1
                q.append(child)

    # Group nodes by depth
    depth_groups: dict = {}
    for nid, depth in depths.items():
        depth_groups.setdefault(depth, []).append(nid)

    # Assign x/y positions
    node_positions = {}
    for depth, node_ids in sorted(depth_groups.items()):
        n = len(node_ids)
        for i, nid in enumerate(sorted(node_ids)):
            node_positions[nid] = {
                "x": depth * 2.5,
                "y": (i - (n - 1) / 2) * 1.8,
            }

    # Build Plotly figure
    edge_x, edge_y = [], []
    for e in edges:
        src = node_positions.get(e["source"], {"x": 0, "y": 0})
        tgt = node_positions.get(e["target"], {"x": 0, "y": 0})
        edge_x += [src["x"], tgt["x"], None]
        edge_y += [src["y"], tgt["y"], None]

    edge_trace = go.Scatter(
        x=edge_x, y=edge_y,
        line=dict(width=1.5, color="#555"),
        hoverinfo="none",
        mode="lines",
        showlegend=False,
    )

    node_x = [node_positions.get(n["id"], {"x": 0})["x"] for n in nodes]
    node_y = [node_positions.get(n["id"], {"y": 0})["y"] for n in nodes]
    node_colors = [n["color"] for n in nodes]
    node_labels = [n["label"] for n in nodes]
    node_hover = [f"{n['id']}<br>Operator: {n['operator']}" + (f"<br>Group: {n['group']}" if n['group'] else "") for n in nodes]

    node_trace = go.Scatter(
        x=node_x, y=node_y,
        mode="markers+text",
        hoverinfo="text",
        hovertext=node_hover,
        text=node_labels,
        textposition="bottom center",
        textfont=dict(size=9, color="white"),
        marker=dict(
            size=22,
            color=node_colors,
            line=dict(width=2, color="#ffffff"),
        ),
        showlegend=False,
    )

    fig = go.Figure(
        data=[edge_trace, node_trace],
        layout=go.Layout(
            title=dict(text=f"DAG: {selected}", font=dict(size=16, color="white")),
            showlegend=False,
            hovermode="closest",
            paper_bgcolor="#0e1117",
            plot_bgcolor="#0e1117",
            xaxis=dict(showgrid=False, zeroline=False, showticklabels=False),
            yaxis=dict(showgrid=False, zeroline=False, showticklabels=False),
            height=550,
            margin=dict(t=60, b=20, l=20, r=20),
            font=dict(color="white"),
        ),
    )

    st.plotly_chart(fig, use_container_width=True)

    # Legend
    st.divider()
    st.subheader("Operator Legend")
    operator_colors = {
        "PythonOperator": "#42a5f5",
        "BranchPythonOperator": "#ffa726",
        "EmptyOperator": "#bdbdbd",
        "FileSensor": "#66bb6a",
        "ExternalTaskSensor": "#26c6da",
        "DataValidationOperator": "#ab47bc",
    }
    cols = st.columns(len(operator_colors))
    for i, (op, color) in enumerate(operator_colors.items()):
        cols[i].markdown(
            f"<span style='background:{color}; color:white; padding:2px 8px; "
            f"border-radius:4px; font-size:11px;'>{op}</span>",
            unsafe_allow_html=True,
        )

    # Raw data
    with st.expander("Raw graph data (JSON)"):
        st.json(graph)


# ---------------------------------------------------------------------------
# TAB 4: Learn Concepts
# ---------------------------------------------------------------------------

elif selected_tab == "Learn Concepts":
    st.header("Airflow Concepts")
    st.caption("Key concepts for Data Architect / Principal DE interviews")

    concepts = {
        "DAG (Directed Acyclic Graph)": {
            "emoji": "graph",
            "definition": (
                "The fundamental unit of Airflow. A collection of tasks with "
                "directional dependencies that form a graph with no cycles. "
                "Each DAG has a unique dag_id, a schedule, and a start_date."
            ),
            "key_points": [
                "schedule_interval accepts cron expressions or presets: @daily, @hourly, @weekly",
                "catchup=False prevents backfilling all missed runs on first deploy",
                "max_active_runs limits concurrent DAG runs (prevents resource storms)",
                "default_args applies shared config (retries, owner, email) to all tasks",
            ],
            "interview_answer": (
                "A DAG is Airflow's model for a workflow. I define the graph structure once; "
                "Airflow handles scheduling, execution, and retry logic. The key design principle "
                "is idempotency — every task should produce the same result if re-run."
            ),
            "code": (
                "with DAG(\n"
                "    dag_id='my_etl',\n"
                "    schedule_interval='@daily',\n"
                "    start_date=datetime(2024, 1, 1),\n"
                "    catchup=False,\n"
                "    default_args={'retries': 3, 'retry_delay': timedelta(minutes=5)},\n"
                ") as dag:\n"
                "    ..."
            ),
        },
        "Operators & Tasks": {
            "emoji": "tools",
            "definition": (
                "An Operator is a template; a Task is a specific instance of that operator in a DAG. "
                "The >> operator wires dependencies: task_a >> task_b means 'run b after a succeeds'."
            ),
            "key_points": [
                "PythonOperator: most flexible — call any Python function",
                "BranchPythonOperator: return a task_id (or list) to follow; others are skipped",
                "EmptyOperator: no-op, used as a gate/join point (replaced DummyOperator in 2.4)",
                "Custom operators: extend BaseOperator, implement execute(context)",
            ],
            "interview_answer": (
                "I choose the right operator for the job. For complex transformations I use "
                "PythonOperator. For waiting on external events I use Sensors. For cross-DAG "
                "dependencies I use ExternalTaskSensor or TriggerDagRunOperator."
            ),
            "code": (
                "def my_task(**context):\n"
                "    ti = context['ti']\n"
                "    data = ti.xcom_pull(task_ids='prev', key='result')\n"
                "    ...\n\n"
                "t = PythonOperator(\n"
                "    task_id='my_task',\n"
                "    python_callable=my_task,\n"
                "    retries=3,\n"
                "    sla=timedelta(hours=1),\n"
                ")"
            ),
        },
        "XComs (Cross-Communications)": {
            "emoji": "exchange",
            "definition": (
                "The mechanism for passing data between tasks. Values are stored in the metadata "
                "database and retrieved by key. Designed for small metadata (row counts, file paths, "
                "status flags) — not for large datasets."
            ),
            "key_points": [
                "ti.xcom_push(key='my_key', value=my_value) — write",
                "ti.xcom_pull(task_ids='task_name', key='my_key') — read",
                "Return value of PythonOperator is auto-pushed as key='return_value'",
                "For large data: push S3/GCS path as XCom, not the data itself",
            ],
            "interview_answer": (
                "XComs are how tasks share context. I use them for row counts, validation status, "
                "file paths, and job IDs. For actual data I push a pointer (S3 path) rather than "
                "the payload, since XComs are stored in the Postgres metadata DB and have a "
                "practical limit around 48KB."
            ),
            "code": (
                "# Push\n"
                "ti.xcom_push(key='row_count', value=42000)\n\n"
                "# Pull in downstream task\n"
                "count = ti.xcom_pull(task_ids='extract', key='row_count')\n"
            ),
        },
        "Sensors": {
            "emoji": "sensor",
            "definition": (
                "Special operators that poll for a condition and block until it is true. "
                "Used for event-driven orchestration — waiting for files, API readiness, "
                "or upstream pipeline completion."
            ),
            "key_points": [
                "poke_interval: how often to check (e.g., 300 = every 5 minutes)",
                "timeout: how long to wait before giving up",
                "mode='reschedule': release the worker slot between pokes (production best practice)",
                "mode='poke': hold the worker slot — wastes resources for long waits",
                "soft_fail=True: mark as SKIPPED rather than FAILED on timeout",
            ],
            "interview_answer": (
                "I use sensors to decouple pipelines from upstream producers. FileSensor waits "
                "for a vendor to drop a file. ExternalTaskSensor waits for another DAG to finish. "
                "Critical choice: always use mode='reschedule' in production to avoid holding "
                "worker slots while waiting hours for a file."
            ),
            "code": (
                "FileSensor(\n"
                "    task_id='wait_for_file',\n"
                "    filepath='data/vendor_*.csv',\n"
                "    fs_conn_id='fs_default',\n"
                "    poke_interval=300,\n"
                "    timeout=7200,\n"
                "    mode='reschedule',\n"
                "    soft_fail=True,\n"
                ")"
            ),
        },
        "Dynamic DAG Generation": {
            "emoji": "factory",
            "definition": (
                "Generating multiple DAGs programmatically at module import time by looping "
                "over a config and assigning DAG objects to globals(). Airflow's scheduler "
                "discovers any DAG object in a module's global namespace."
            ),
            "key_points": [
                "Loop over config at import time — not inside functions",
                "globals()[dag_id] = dag registers each DAG with Airflow",
                "Config lives in JSON/YAML in Git — adding a pipeline = one PR",
                "All generated DAGs share the same task structure, varying by config values",
            ],
            "interview_answer": (
                "At [Company] we had 200+ similar ETL pipelines. Dynamic DAGs let us express "
                "all of them as a JSON config + one factory function. Adding a new pipeline "
                "required only a config PR, reviewed by non-engineers. The alternative — "
                "200 separate Python files — would be unmaintainable."
            ),
            "code": (
                "for pipeline in config['pipelines']:\n"
                "    dag_id = f'etl_{pipeline[\"name\"]}'\n"
                "    with DAG(dag_id, ...) as dag:\n"
                "        extract = PythonOperator(...)\n"
                "        load = PythonOperator(...)\n"
                "        extract >> load\n"
                "    globals()[dag_id] = dag  # Airflow discovers via globals()"
            ),
        },
        "TaskGroups": {
            "emoji": "group",
            "definition": (
                "Visual grouping of related tasks in the Airflow UI Graph View. "
                "Replacement for deprecated SubDAGs since Airflow 2.0. TaskGroups "
                "are purely organisational — they do not affect scheduling."
            ),
            "key_points": [
                "Task IDs are scoped: 'group_id.task_id'",
                "Groups appear as collapsible boxes in Graph View",
                "No extra scheduler overhead (unlike SubDAGs which were mini-DAGs)",
                "Nested TaskGroups are supported",
            ],
            "interview_answer": (
                "TaskGroups are my go-to for DAGs with 20+ tasks. I group by stage "
                "(ingest, transform, publish) so the graph is readable at a glance. "
                "I avoid SubDAGs entirely — they had concurrency issues and are deprecated."
            ),
            "code": (
                "with TaskGroup(group_id='ingest') as tg_ingest:\n"
                "    t_crm = PythonOperator(task_id='ingest_crm', ...)\n"
                "    t_erp = PythonOperator(task_id='ingest_erp', ...)\n"
                "    [t_crm, t_erp] >> validate\n\n"
                "tg_ingest >> tg_transform"
            ),
        },
        "Error Handling & Retries": {
            "emoji": "retry",
            "definition": (
                "Airflow retries failed tasks automatically based on operator config. "
                "Additional callbacks let you take custom actions on failure, retry, or SLA miss."
            ),
            "key_points": [
                "retries=3 with retry_delay=timedelta(minutes=5) is a common default",
                "retry_exponential_backoff=True doubles the delay between each retry",
                "on_failure_callback: called when a task exhausts all retries",
                "sla=timedelta(hours=2): calls sla_miss_callback if task exceeds this",
                "execution_timeout: hard kill if task runs too long",
                "TriggerRule.ALL_DONE: run regardless of upstream state (good for cleanup tasks)",
            ],
            "interview_answer": (
                "I configure retries at the operator level for transient failures (network, "
                "DB timeouts). SLAs give early warning before a task fully fails. on_failure_callback "
                "triggers a PagerDuty page. I also use on_retry_callback to log to our observability "
                "platform so we can detect recurring flakiness before it causes incidents."
            ),
            "code": (
                "PythonOperator(\n"
                "    task_id='load_to_bq',\n"
                "    python_callable=load_fn,\n"
                "    retries=3,\n"
                "    retry_delay=timedelta(minutes=5),\n"
                "    retry_exponential_backoff=True,\n"
                "    sla=timedelta(hours=2),\n"
                "    execution_timeout=timedelta(hours=1),\n"
                "    on_failure_callback=pagerduty_alert,\n"
                ")"
            ),
        },
        "Executors": {
            "emoji": "executor",
            "definition": (
                "The component that actually runs task instances. The executor type "
                "determines how tasks are distributed and parallelised."
            ),
            "key_points": [
                "SequentialExecutor: dev only, one task at a time",
                "LocalExecutor: parallel on one machine, good for small teams",
                "CeleryExecutor: distributed — tasks queued to Redis/RabbitMQ and executed by workers",
                "KubernetesExecutor: each task = one K8s pod, maximum isolation",
                "CeleryKubernetesExecutor: Celery for steady-state + K8s for burst",
            ],
            "interview_answer": (
                "Production choice depends on scale. For most enterprise ETL teams, "
                "CeleryExecutor on managed services (Astronomer, MWAA, Cloud Composer) is "
                "the sweet spot. KubernetesExecutor is ideal when task isolation and autoscaling "
                "are critical — e.g., ML training pipelines where tasks need GPUs."
            ),
            "code": "# Set in airflow.cfg or env var:\n# AIRFLOW__CORE__EXECUTOR=CeleryExecutor",
        },
    }

    for concept_name, details in concepts.items():
        with st.expander(f"**{concept_name}**", expanded=False):
            st.markdown(f"**Definition:** {details['definition']}")

            st.markdown("**Key Points:**")
            for point in details.get("key_points", []):
                st.markdown(f"- {point}")

            st.markdown(
                f"<div class='concept-box'><strong>Interview Answer:</strong><br>{details.get('interview_answer', '')}</div>",
                unsafe_allow_html=True,
            )

            if details.get("code"):
                st.code(details["code"], language="python")

    st.divider()
    st.subheader("DAG Design Patterns")

    patterns = {
        "Linear ETL": "extract >> validate >> transform >> load >> notify",
        "Fan-out / Fan-in": "[source_a, source_b, source_c] >> merge >> publish",
        "Branch": "extract >> validate >> branch >> [transform | handle_failure]",
        "Sensor-gated": "[file_sensor, upstream_sensor] >> process >> load",
        "TaskGroup nested": "tg_ingest >> tg_transform >> tg_publish",
        "Dynamic": "for p in config: globals()[f'etl_{p}'] = DAG(...)",
    }

    col1, col2 = st.columns(2)
    for i, (name, pattern) in enumerate(patterns.items()):
        col = col1 if i % 2 == 0 else col2
        with col:
            st.markdown(f"**{name}**")
            st.code(pattern, language="python")


# ---------------------------------------------------------------------------
# Footer
# ---------------------------------------------------------------------------
st.divider()
st.caption(
    "POC-07 — Enterprise Airflow Orchestration Platform | "
    "Built for Lead DE / Data Architect interview prep | "
    "Local simulator mode — no Airflow installation required"
)
