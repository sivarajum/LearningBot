# POC-07: Enterprise Airflow Orchestration Platform
## A Complete Guide for Data Architect / Principal DE Interviews

---

## Table of Contents

1. What is Apache Airflow and Why It Matters
2. Core Concepts Deep Dive
3. DAG Design Patterns
4. DAG 01 — Classic ETL Pipeline
5. DAG 02 — Dynamic DAG Generation
6. DAG 03 — Sensor Pipeline
7. DAG 04 — Data Quality with Branching
8. DAG 05 — Multi-Source ETL with TaskGroups
9. Custom Operator: DataValidationOperator
10. XCom: Passing Data Between Tasks
11. Error Handling — Retries, SLAs, Callbacks
12. TaskGroups vs SubDAGs
13. Running Locally (Simulator Mode)
14. Running with Docker (Full Airflow Stack)
15. API Reference with curl Examples
16. Real-World Mapping
17. Interview Q&A
18. Troubleshooting
19. Glossary

---

## 1. What is Apache Airflow and Why It Matters

Apache Airflow is an open-source workflow orchestration platform. You write Python code that describes workflows as **Directed Acyclic Graphs (DAGs)**. Airflow handles scheduling, execution, monitoring, retries, alerting, and history.

### Why it dominates enterprise data engineering

Every large organisation has hundreds of data pipelines. Without a proper orchestrator you end up with cron jobs nobody understands, Bash scripts with no retry logic, and zero visibility into what ran when. Airflow solves all of these:

- **Scheduling**: run at any cron schedule or on event triggers
- **Dependencies**: define exact task order with `>>` operator
- **Observability**: web UI showing every run's status, logs, and XComs
- **Retries**: automatic retry with configurable backoff
- **Alerting**: email/Slack on failure, SLA miss, or retry
- **History**: full audit trail of every execution
- **Idempotency**: DAGs can be re-run safely — by design

### Airflow vs alternatives

| Tool | Strength | Weakness |
|---|---|---|
| Airflow | Most mature, huge ecosystem, Python-native | Heavy infra, steep learning curve |
| Prefect | Simpler setup, dynamic flows | Smaller community |
| Dagster | Strong asset-centric model | Different mental model |
| dbt | Transformation-focused, SQL-native | Not a general orchestrator |
| Luigi | Simple, dependency tracking | Limited UI, less active |

**Interview answer**: "At the companies I've worked with, Airflow was the standard because it has the richest operator ecosystem, deepest cloud integrations, and the largest talent pool. For greenfield projects I'd evaluate Prefect or Dagster, but for enterprise adoption Airflow wins on battle-tested reliability."

---

## 2. Core Concepts Deep Dive

### 2.1 DAG

A **Directed Acyclic Graph** is the fundamental unit of Airflow. It defines:
- Which tasks exist
- How tasks depend on each other (directed edges)
- When to run (schedule)
- Shared defaults (retries, owner, email)

```python
with DAG(
    dag_id="my_etl",
    description="Daily sales ETL",
    schedule_interval="@daily",          # or cron: "0 2 * * *"
    start_date=datetime(2024, 1, 1),
    catchup=False,                        # critical: prevent backfill storm
    max_active_runs=1,                    # prevent overlapping runs
    default_args={
        "owner": "data-engineering",
        "retries": 3,
        "retry_delay": timedelta(minutes=5),
        "email_on_failure": True,
        "email": ["alerts@company.com"],
    },
    tags=["etl", "sales"],
) as dag:
    ...
```

### 2.2 Operators

An **Operator** defines the template; a **Task** is an instance.

```python
# PythonOperator — most versatile
t = PythonOperator(
    task_id="extract_data",
    python_callable=my_function,
    op_kwargs={"source": "postgres"},   # pass extra args
)

# BashOperator — run shell commands
t = BashOperator(
    task_id="run_dbt",
    bash_command="dbt run --select +my_model",
)

# BranchPythonOperator — conditional routing
t = BranchPythonOperator(
    task_id="route_by_quality",
    python_callable=decide_branch,  # returns task_id string
)
```

### 2.3 Tasks and Dependencies

```python
# Sequential
extract >> validate >> load

# Parallel fan-out
extract >> [validate_schema, validate_counts, validate_freshness]

# Fan-in (all must complete before merge)
[validate_schema, validate_counts] >> merge_results

# Mixed
start >> [task_a, task_b] >> join >> end
```

### 2.4 Scheduler and Executor

The **Scheduler** reads DAG files, determines what needs to run, and places `TaskInstance` records in the metadata DB.

The **Executor** picks up queued TaskInstances and runs them. Choice of executor determines parallelism:

```
SequentialExecutor → LocalExecutor → CeleryExecutor → KubernetesExecutor
    (dev only)         (1 machine)    (multi-machine)   (K8s pod per task)
```

Production recommendation: **CeleryExecutor** for most teams, **KubernetesExecutor** when you need full isolation or GPU tasks.

### 2.5 Connections and Hooks

A **Connection** stores credentials (host, port, login, password) under a `conn_id`. A **Hook** uses a connection to talk to an external system.

```python
# Hook pattern
from airflow.providers.postgres.hooks.postgres import PostgresHook

def my_task(**context):
    hook = PostgresHook(postgres_conn_id="postgres_dw")
    df = hook.get_pandas_df("SELECT * FROM sales WHERE dt = '{{ ds }}'")
    ...
```

Set connections via:
- Airflow UI → Admin → Connections
- Environment variable: `AIRFLOW_CONN_POSTGRES_DW=postgresql://user:pass@host:5432/db`
- Secrets backend (Vault, AWS Secrets Manager)

### 2.6 Variables

Global key-value store for runtime configuration:

```python
from airflow.models import Variable

threshold = Variable.get("dq_row_count_threshold", default_var="100", deserialize_json=False)
config = Variable.get("pipeline_config", deserialize_json=True)
```

Prefer config files or environment variables for sensitive data — Variables are visible in the UI.

---

## 3. DAG Design Patterns

### Pattern 1: Linear ETL

The most common pattern. Each stage gates the next.

```
extract_data
    │
validate_data
    │
transform_data
    │
load_data
    │
notify_success
```

### Pattern 2: Parallel Fan-Out

Multiple independent tasks run simultaneously, then a join task collects results.

```
              ┌── ingest_crm ──┐
pipeline_start├── ingest_erp ──┼── validate_all ── merge ── publish
              └── ingest_ga4 ──┘
```

### Pattern 3: Branch (Conditional)

Based on a condition at runtime, only one branch executes. The others are marked `SKIPPED`.

```
extract
  │
validate
  │
branch ──────────────────────────────┐
  │                                  │
transform (validation passed)   handle_failure (DQ failed)
  │
load
  │
notify
```

### Pattern 4: Sensor-Gated

Block until an external condition is met.

```
wait_for_vendor_file (FileSensor) ──┐
                                    ├── process_file ── load
wait_for_dim_refresh (ExtSensor) ───┘
```

### Pattern 5: Dynamic DAG Factory

One config file → N DAGs generated at import time.

```
pipeline_config.json
    ├── sales      → DAG: etl_sales       (runs @daily)
    ├── inventory  → DAG: etl_inventory   (runs @hourly)
    └── customer   → DAG: etl_customer    (runs at 2am)
```

### Pattern 6: TaskGroup Hierarchy

Organise complex DAGs with collapsible groups.

```
┌──────────────────────────────────────────────────────────────────┐
│ INGEST                   TRANSFORM              PUBLISH          │
│  crm ──┐               resolve ──┐           bi ──┐             │
│  erp ──┼──validate     join     ──┼──build    ml ──┼──catalogue  │
│  ga4 ──┘               sessions ──┘               └──┘          │
└──────────────────────────────────────────────────────────────────┘
```

---

## 4. DAG 01 — Classic ETL Pipeline

**File**: `dags/dag_01_etl_pipeline.py`

This is the foundational pattern for any enterprise ETL DAG.

### What it demonstrates

- `PythonOperator` for each stage
- `BranchPythonOperator` to route on validation result
- `retries=3` with exponential backoff
- `SLA` per task
- XCom push/pull to pass row counts between tasks
- `email_on_failure=True` (config, not sending in dev)

### Task walkthrough

**extract_data**

```python
def extract_data(**context):
    ti = context["ti"]
    # ... simulate extraction ...
    ti.xcom_push(key="extracted_row_count", value=row_count)
    return extracted_data
```

Pushes the row count so `validate_data` can check it without re-querying.

**validate_data**

```python
def validate_data(**context):
    ti = context["ti"]
    row_count = ti.xcom_pull(task_ids="extract_data", key="extracted_row_count")
    # Run checks, push status
    ti.xcom_push(key="validation_status", value="pass" or "fail")
```

**check_validation_branch**

```python
def check_validation_branch(**context):
    ti = context["ti"]
    status = ti.xcom_pull(task_ids="validate_data", key="validation_status")
    return "transform_data" if status == "pass" else "handle_validation_failure"
```

The `BranchPythonOperator` reads the XCom and returns the task_id of the next task. Airflow marks all other branches as `SKIPPED`.

### Key design decisions

1. **Idempotency**: the load task uses UPSERT (merge on txn_id) so re-runs don't create duplicates
2. **SLA per task**: different stages have different expected durations — 30 min for extract, 45 min for transform
3. **Separate failure handler**: the `handle_validation_failure` task quarantines bad data rather than silently skipping

---

## 5. DAG 02 — Dynamic DAG Generation

**File**: `dags/dag_02_dynamic_dag.py`

### The problem dynamic DAGs solve

Imagine you have 50 data source systems, each needing an identical ETL pipeline. You could write 50 DAG files that are 95% identical — or you could write one factory function and a config.

### How Airflow discovers DAGs

The Airflow scheduler imports every `.py` file in the `dags/` folder. Any object that is an instance of `airflow.DAG` in the module's `globals()` namespace gets registered. This is the mechanism dynamic DAGs exploit:

```python
for pipeline in config["pipelines"]:
    dag_id = f"etl_{pipeline['name']}"

    with DAG(dag_id, ...) as dag:
        t_extract = PythonOperator(task_id="extract", ...)
        t_load = PythonOperator(task_id="load", ...)
        t_extract >> t_load

    globals()[dag_id] = dag   # <-- THIS is how Airflow finds it
```

### Performance considerations

Dynamic DAG generation runs at every scheduler parse cycle. Keep it fast:
- Cache the config with `functools.lru_cache` or module-level constants
- Don't make network calls at import time
- Keep the config small (this POC's JSON is ~2KB)

### The factory pattern in this POC

```python
CONFIG = _load_config()  # reads pipeline_config.json once

for _pipeline in CONFIG.get("pipelines", []):
    _dag_id = f"etl_{_pipeline['name']}"
    _dag = create_pipeline_dag(_pipeline, GLOBAL)
    globals()[_dag_id] = _dag
```

This generates 4 DAGs from the config: `etl_sales`, `etl_inventory`, `etl_customer_360`, `etl_marketing_attribution`.

### Task parameterisation

Each task's callable is dynamically bound to the pipeline config using closures:

```python
def make_extract_task(pipeline_cfg):
    def extract(**context):
        # Uses pipeline_cfg from closure
        sources = pipeline_cfg["sources"]
        ...
    extract.__name__ = f"extract_{pipeline_cfg['name']}"
    return extract
```

---

## 6. DAG 03 — Sensor Pipeline

**File**: `dags/dag_03_sensor_pipeline.py`

### FileSensor

Blocks execution until a file matching a glob pattern exists in a directory:

```python
FileSensor(
    task_id="wait_for_vendor_file",
    filepath="data/vendor_sales_*.csv",
    fs_conn_id="fs_default",
    poke_interval=300,     # check every 5 minutes
    timeout=7200,          # give up after 2 hours
    mode="reschedule",     # <-- CRITICAL: don't hold worker slot
    soft_fail=True,        # mark SKIPPED (not FAILED) on timeout
)
```

**mode="reschedule" is the production best practice.** In `poke` mode, the sensor occupies a worker slot the entire time it's waiting. If you have 10 sensors waiting 4 hours each and only 8 workers, your pipeline stalls. In `reschedule` mode, the sensor releases its slot between pokes.

### ExternalTaskSensor

Cross-DAG dependency — wait for a specific task in another DAG to succeed:

```python
ExternalTaskSensor(
    task_id="wait_for_dimension_refresh",
    external_dag_id="etl_transactions_pipeline",
    external_task_id="load_data",
    execution_delta=timedelta(hours=0),  # same logical date
    poke_interval=120,
    timeout=3600,
    mode="reschedule",
)
```

`execution_delta` is powerful: you can wait for yesterday's run with `timedelta(days=1)`, which is useful for daily dimension refreshes.

### When to use sensors vs TriggerDagRunOperator

- **Sensor**: your DAG passively waits for another DAG/event. The upstream owns its schedule.
- **TriggerDagRunOperator**: your DAG actively kicks off another DAG. You own both sides.

Use sensors for vendor deliveries, file drops, and cross-team dependencies. Use TriggerDagRunOperator for tight internal dependencies where you control both DAGs.

---

## 7. DAG 04 — Data Quality with Branching

**File**: `dags/dag_04_data_quality.py`

### Why a dedicated DQ DAG?

Best practice in large organisations is to separate DQ checks from the ETL pipeline:

1. **Separation of concerns**: ETL is about moving data; DQ is about asserting correctness
2. **Independent scheduling**: DQ can run after ETL and before BI refresh
3. **Reusability**: multiple ETL pipelines can share one DQ DAG

### The three-severity routing pattern

```
aggregate_dq_results
        │
branch_on_dq_result
    /       |        \
all_pass  soft_fail  hard_fail
    │         │          │
publish  alert+pub  quarantine+stop
    \         |          /
        finalize_dq_run
           (ALL_DONE trigger rule)
```

**all_pass**: data is clean — release to BI and ML consumers
**soft_fail**: minor issues (data slightly stale, 2 duplicate rows) — alert team but allow
**hard_fail**: serious issues (row count dropped 90%, primary keys are null) — quarantine data, page on-call

### TriggerRule for the join task

The `finalize_dq_run` task must run after any branch:

```python
PythonOperator(
    task_id="finalize_dq_run",
    python_callable=finalize_dq_run,
    trigger_rule=TriggerRule.ALL_DONE,  # run even if some upstreams failed/skipped
)
```

Without `trigger_rule=ALL_DONE`, Airflow's default (`ALL_SUCCESS`) would leave this task stuck in `upstream_failed` state if the `quarantine_data` task raised an exception.

### Parallel DQ checks

The 5 check tasks run in parallel — no dependencies between them:

```python
t_start >> [t_null, t_count, t_dups, t_ri, t_fresh]
[t_null, t_count, t_dups, t_ri, t_fresh] >> t_aggregate
```

This is significantly faster than running them sequentially. For a table with 100M rows, each check might take 2 minutes — parallel means 2 min total instead of 10.

---

## 8. DAG 05 — Multi-Source ETL with TaskGroups

**File**: `dags/dag_05_multi_source_etl.py`

### TaskGroup structure

Three nested groups model the three pipeline stages:

```python
with TaskGroup(group_id="ingest") as tg_ingest:
    t_crm = PythonOperator(task_id="ingest_crm", ...)
    t_erp = PythonOperator(task_id="ingest_erp", ...)
    t_analytics = PythonOperator(task_id="ingest_analytics", ...)
    [t_crm, t_erp, t_analytics] >> t_validate

with TaskGroup(group_id="transform") as tg_transform:
    t_resolve >> t_join_sessions >> t_build_journey

with TaskGroup(group_id="publish") as tg_publish:
    [t_bi, t_ml] >> t_catalogue

# Group-level dependencies — clean and readable
t_start >> tg_ingest >> tg_transform >> tg_publish >> t_end
```

### Task ID scoping

TaskGroups scope task IDs: `ingest.ingest_crm`, `transform.resolve_entities`. This matters for XCom pulls:

```python
# When pulling XCom from a task in a group:
crm_result = ti.xcom_pull(task_ids="ingest.ingest_crm", key="crm_result")
```

### Real-world mapping: Customer 360

This DAG models a genuine enterprise use case:

1. **CRM** (Salesforce): account and contact records
2. **ERP** (SAP): order headers, line items, customer master
3. **Web Analytics** (GA4): session and event data

Entity resolution (matching CRM customers to ERP customers) is the hardest part — names differ, addresses are inconsistent. Production implementations use libraries like `recordlinkage`, `Splink`, or vendor-specific MDM tools.

---

## 9. Custom Operator: DataValidationOperator

**File**: `plugins/operators/validation_operator.py`

### Why custom operators?

When a pattern repeats across many DAGs, package it as a custom operator:

```python
# Before: repeated code in 50 DAG files
def validate_table(table_name, conn_id, **context):
    ...

# After: one operator used everywhere
t = DataValidationOperator(
    task_id="validate",
    table="fact_transactions",
    connection_id="postgres_dw",
    checks=[
        {"type": "not_null", "column": "txn_id"},
        {"type": "row_count_min", "threshold": 100},
        {"type": "value_range", "column": "amount", "min": 0, "max": 1_000_000},
    ],
    fail_on_error=True,
)
```

### Operator anatomy

```python
class DataValidationOperator(BaseOperator):

    template_fields = ("table",)   # Jinja-templateable
    ui_color = "#fff9c4"           # colour in Graph View

    @apply_defaults
    def __init__(self, table, connection_id, checks, fail_on_error=True, ...):
        super().__init__(...)
        self.table = table
        self.checks = checks
        ...

    def execute(self, context):
        # This is called by Airflow to run the task
        report = self._run_all_checks()
        context["ti"].xcom_push(key="validation_report", value=report)
        if not report["overall_passed"] and self.fail_on_error:
            raise ValueError(f"DQ failed: {report['errors']}")
        return report
```

### Plugin auto-discovery

Place the operator in `plugins/operators/` and Airflow auto-discovers it. No additional registration needed. DAGs import it as:

```python
from plugins.operators.validation_operator import DataValidationOperator
```

### Supported check types

| Check Type | What It Does |
|---|---|
| `not_null` | Null rate below threshold for a column |
| `row_count_min` | Table has at least N rows |
| `row_count_max` | Table does not exceed N rows (anomaly detection) |
| `value_range` | All values in [min, max] |
| `freshness` | Latest record age below threshold |
| `unique` | No duplicate values in column(s) |
| `regex` | Values match regex pattern |
| `referential_integrity` | FK values exist in reference table |

---

## 10. XCom: Passing Data Between Tasks

### What XComs are for

XComs (Cross-Communications) let tasks exchange small pieces of metadata — row counts, file paths, status flags, job IDs. They are **not** designed for large datasets.

```python
# Task A: push
def extract(**context):
    ti = context["ti"]
    row_count = fetch_from_db()
    ti.xcom_push(key="row_count", value=row_count)

# Task B: pull (must list task A's ID)
def validate(**context):
    ti = context["ti"]
    count = ti.xcom_pull(task_ids="extract", key="row_count")
    if count < 100:
        raise ValueError("Insufficient rows")
```

### Auto return value

If a `PythonOperator` returns a value, it is automatically pushed as `key="return_value"`:

```python
def extract(**context):
    return {"row_count": 1000, "file": "s3://bucket/data.parquet"}

# Pull in downstream task:
data = ti.xcom_pull(task_ids="extract")  # returns the dict
```

### XCom size limits

XComs are serialised as JSON and stored in the Airflow metadata DB (Postgres). Practical limits:
- Postgres: ~1GB per cell (but use S3 for anything over a few KB)
- MySQL: ~64KB per cell

**The pattern**: push S3/GCS paths as XComs, not data:

```python
# Good
ti.xcom_push(key="output_path", value="s3://data-lake/processed/2024-01-01/data.parquet")

# Bad — storing a DataFrame in XCom
ti.xcom_push(key="data", value=df.to_json())  # could be 50MB
```

### Custom XCom backends

Airflow 2.0+ supports custom XCom backends that store values in S3 or GCS automatically:

```python
# airflow.cfg
[core]
xcom_backend = airflow.providers.amazon.aws.xcom_backends.s3.S3XComBackend
```

With this configured, large XComs are transparently stored in S3 and the key is just a reference.

---

## 11. Error Handling — Retries, SLAs, Callbacks

### Retry configuration

```python
PythonOperator(
    task_id="load_to_warehouse",
    python_callable=load_fn,
    retries=3,
    retry_delay=timedelta(minutes=5),
    retry_exponential_backoff=True,    # delay doubles each retry: 5min → 10min → 20min
    max_retry_delay=timedelta(minutes=30),
    execution_timeout=timedelta(hours=1),
)
```

When to use exponential backoff: any task that calls an external API or database. Avoids hammering a struggling service.

### SLAs

SLA (Service Level Agreement) is the expected completion time. When missed:
1. `sla_miss_callback` is called on the DAG
2. Email notification is sent (if configured)
3. The task continues running (SLA miss does not kill the task)

```python
def my_sla_miss_callback(dag, task_list, blocking_task_list, slas, blocking_tis):
    # Send to PagerDuty, Slack, etc.
    logger.error("SLA MISSED: %s", task_list)

dag = DAG(
    ...,
    sla_miss_callback=my_sla_miss_callback,
)

# Per-task SLA
t = PythonOperator(
    task_id="heavy_transform",
    sla=timedelta(hours=2),      # warn if this task takes > 2 hours
    ...
)
```

### Callbacks

Five callback hooks on operators:

| Callback | Trigger |
|---|---|
| `on_execute_callback` | Before task starts |
| `on_success_callback` | Task completed successfully |
| `on_failure_callback` | Task failed (retries exhausted) |
| `on_retry_callback` | Task is about to retry |
| `on_skipped_callback` | Task was skipped |

```python
def on_failure_alert(context):
    task = context["task_instance"].task_id
    dag = context["task_instance"].dag_id
    error = context.get("exception")
    send_pagerduty_alert(f"{dag}/{task} failed: {error}")

PythonOperator(
    ...,
    on_failure_callback=on_failure_alert,
)
```

### Alerting strategy (production)

```
Task failure → retry (3x)
              ↓
        Still failing
              ↓
    on_failure_callback
         /         \
    Critical?     Non-critical?
    PagerDuty     Slack #data-alerts
                  JIRA ticket
```

---

## 12. TaskGroups vs SubDAGs

### Why SubDAGs were deprecated

Before Airflow 2.0, **SubDAGs** were the way to organise groups of tasks. They worked by embedding a mini-DAG inside a parent DAG. Problems:

1. **Deadlock risk**: SubDAG had its own pool slots. With `ConcurrencyLimit=1` and a busy cluster, SubDAGs would deadlock waiting for slots.
2. **Performance**: each SubDAG required a separate scheduler cycle to process.
3. **Complexity**: debugging SubDAG failures required understanding two DAG contexts.

### TaskGroups are the modern replacement

```python
# Old (avoid)
from airflow.operators.subdag import SubDagOperator

# New (correct)
from airflow.utils.task_group import TaskGroup

with TaskGroup(group_id="ingest", tooltip="Ingest from CRM, ERP, Analytics") as tg:
    t_crm = PythonOperator(task_id="ingest_crm", ...)
    t_erp = PythonOperator(task_id="ingest_erp", ...)
    [t_crm, t_erp] >> t_validate
```

TaskGroups are purely visual. They have no scheduling implications. They simply scope task IDs and create collapsible groups in the Graph View.

---

## 13. Running Locally (Simulator Mode)

The simulator lets you run all DAGs without installing Airflow or Docker.

### Quick start

```bash
# Clone / navigate to project
cd POC-07-Airflow-Orchestration

# Install lightweight requirements (no Airflow needed)
pip install -r requirements.txt

# List all available DAGs
python main.py list

# Simulate all main DAGs
python main.py simulate

# Simulate a specific DAG
python main.py simulate etl_transactions_pipeline
python main.py simulate data_quality_pipeline
python main.py simulate multi_source_etl_customer_journey
python main.py simulate etl_sales

# Start the API server
python main.py api

# Start the Streamlit UI
python main.py ui

# Start both
python main.py all
```

### What the simulator does

1. **Imports** each `dags/dag_*.py` file using `importlib`
2. **Extracts** task definitions from the module's globals and the `STATIC_TASK_GRAPHS` registry
3. **Sorts** tasks topologically using Kahn's algorithm
4. **Executes** each task's Python callable in order
5. **Injects** a `FakeTaskInstance` that implements `xcom_push`/`xcom_pull` using an in-memory dict
6. **Respects** `BranchPythonOperator` by reading the return value and skipping unchosen branches
7. **Simulates** sensors as instant-success (no actual file waiting)
8. **Returns** a full `SimulationResult` with per-task status, duration, and XCom data

### Verify imports work

```bash
python -c "from src.api import app; print('API import OK')"
python -c "from src.simulator import get_simulator; print('Simulator import OK')"
python -c "from plugins.operators.validation_operator import DataValidationOperator; print('Operator import OK')"
python -c "from dags.dag_01_etl_pipeline import extract_data; print('DAG 01 import OK')"
```

---

## 14. Running with Docker (Full Airflow Stack)

### Prerequisites

- Docker Desktop installed and running
- 8GB+ RAM allocated to Docker (Airflow needs it)
- Ports 8080, 8000, 8501, 5432, 6379 available

### Start the full stack

```bash
cd POC-07-Airflow-Orchestration

# Create the required log directory
mkdir -p logs

# Set the Airflow UID (required on Linux/Mac)
echo "AIRFLOW_UID=$(id -u)" > .env

# Initialise the database and create admin user
docker-compose up airflow-init

# Start all services
docker-compose up -d

# Watch startup
docker-compose logs -f airflow-webserver
```

### Access the services

| Service | URL | Credentials |
|---|---|---|
| Airflow Webserver | http://localhost:8080 | admin / admin |
| Celery Flower | http://localhost:5555 | none |
| POC FastAPI | http://localhost:8000/docs | none |
| POC Streamlit | http://localhost:8501 | none |

### Trigger a DAG run from the UI

1. Open http://localhost:8080
2. Login with admin/admin
3. Find `etl_transactions_pipeline`
4. Click the toggle to unpause it
5. Click the "Trigger DAG" button (play icon)
6. Watch the Graph View update in real-time

### Check DAG parse errors

```bash
# See if Airflow can parse the DAGs without errors
docker-compose exec airflow-scheduler airflow dags list

# Check for import errors
docker-compose exec airflow-scheduler airflow dags list-import-errors
```

### Tail logs for a specific task

```bash
docker-compose exec airflow-scheduler \
  airflow tasks test etl_transactions_pipeline extract_data 2024-01-01
```

### Stop the stack

```bash
docker-compose down       # stop but keep data
docker-compose down -v    # stop and delete all volumes (fresh start)
```

---

## 15. API Reference with curl Examples

### Health check

```bash
curl http://localhost:8000/health
```

Response:
```json
{
  "status": "healthy",
  "timestamp": "2024-01-15T10:30:00",
  "version": "1.0.0",
  "airflow_mode": "simulator mode (no Airflow installed)"
}
```

### List all DAGs

```bash
curl http://localhost:8000/dags | python -m json.tool
```

### Get DAG details

```bash
curl http://localhost:8000/dags/etl_transactions_pipeline
```

### Simulate a DAG run

```bash
curl -X POST http://localhost:8000/dags/etl_transactions_pipeline/run \
  -H "Content-Type: application/json" \
  -d '{}'
```

Response includes full task trace with XComs:
```json
{
  "dag_id": "etl_transactions_pipeline",
  "run_id": "sim__etl_transactions_pipeline__20240115T103000",
  "status": "success",
  "duration_ms": 245,
  "task_results": [
    {
      "task_id": "extract_data",
      "status": "success",
      "duration_ms": 12,
      "xcoms_pushed": {"extracted_row_count": 3412, "extraction_metadata": {...}}
    },
    ...
  ],
  "xcoms": {
    "extract_data/extracted_row_count": 3412,
    "validate_data/validation_status": "pass",
    ...
  },
  "summary": {"total_tasks": 7, "succeeded": 6, "skipped": 1}
}
```

### Get task dependency graph

```bash
curl http://localhost:8000/dags/data_quality_pipeline/graph
```

### View XComs from last run

```bash
# All DAGs
curl http://localhost:8000/xcoms

# Specific DAG
curl "http://localhost:8000/xcoms?dag_id=etl_transactions_pipeline"
```

### Get concepts dictionary

```bash
curl http://localhost:8000/concepts | python -m json.tool
```

### Reload DAGs (dev mode)

```bash
curl -X POST http://localhost:8000/reload
```

---

## 16. Real-World Mapping

### Home Depot style: 500+ store ETL

At a retailer with hundreds of locations, a DAG per store runs nightly:

```
Dynamic DAG: etl_store_{store_id}
├── extract_pos_data          (POS system → S3)
├── validate_pos              (row count, null checks)
├── transform_to_schema       (standardise to enterprise format)
├── load_to_dw                (BigQuery UPSERT)
└── update_store_dashboard    (refresh Looker)
```

Using dynamic DAGs: one factory + one config = 500 DAGs maintained as a single codebase.

### KLM style: flight operations pipeline

Airlines run time-critical pipelines where SLAs mean real money:

```
sensor_new_flight_manifest (FileSensor, poke every 60s)
    │
check_manifest_completeness
    │
branch_on_departure_proximity
    /                    \
< 4 hours                > 4 hours
expedited_processing     standard_processing
    │                         │
assign_crew              load_to_ops_db
    │                         │
notify_gate             notify_planning
    \                    /
     update_flight_ops_dashboard
```

SLA on `assign_crew`: 30 minutes. Missed SLA pages duty manager immediately.

### Feature pipeline for ML

```
TaskGroup: feature_extraction
    ├── user_features           (30-day rolling aggregates)
    ├── product_features        (inventory, price history)
    └── contextual_features     (weather, events, holidays)

TaskGroup: feature_validation
    ├── check_feature_drift     (compare distribution to baseline)
    └── check_training_set_size

TaskGroup: feature_store_publish
    ├── push_to_feast           (online feature store)
    └── push_to_bigquery        (offline feature store)
```

The validation step uses DataValidationOperator with statistical distribution checks — if a feature's mean shifts by >3σ from baseline, the pipeline halts and pages the ML team.

---

## 17. Interview Q&A

**Q: How do you handle idempotency in Airflow DAGs?**

A: Every task must be safe to re-run. For load tasks I use UPSERT/MERGE rather than INSERT. For S3 writes I use partition-based overwrite. For API calls I check if the operation already completed. The key principle: if a task ran successfully and runs again with the same execution_date, the result should be identical and no duplicates created.

**Q: How do you handle backfilling when you add a new DAG?**

A: I always set `catchup=False` on new DAGs unless backfill is explicitly needed. If backfill is needed I run it manually with `airflow dags backfill --start-date 2024-01-01 --end-date 2024-03-01 my_dag` and monitor it closely. I also set `max_active_runs=3` to prevent it overwhelming the cluster.

**Q: What's the difference between execution_date and start_date?**

A: `start_date` is when the DAG first becomes eligible to run. `execution_date` is the logical date a run is *for* — Airflow runs the DAG for `execution_date` after that date has passed. For `@daily` with `start_date=Jan 1`, the first run has `execution_date=Jan 1` and runs just after midnight on Jan 2. This is a common source of confusion for newcomers.

**Q: How do you scale Airflow in production?**

A: For medium scale I use CeleryExecutor with 5-10 workers and Redis as broker. For large scale (1000+ concurrent tasks) I switch to KubernetesExecutor so each task gets its own pod with exactly the resources it needs. I also: tune `parallelism` and `max_active_tasks_per_dag`, use pools to rate-limit tasks hitting the same external systems, and separate the scheduler from workers onto dedicated instances.

**Q: How would you design a DAG for a complex multi-step ML pipeline?**

A: I'd use a three-stage TaskGroup structure: (1) data validation + feature engineering in parallel per feature group, (2) model training gated by a validation check, (3) evaluation + conditional deployment using BranchPythonOperator — if metrics pass, deploy; otherwise, alert and halt. I'd use ExternalTaskSensor to ensure the feature store was refreshed before training starts.

**Q: What causes the "zombie task" problem in Airflow?**

A: Zombie tasks happen when a task's worker dies mid-execution — the TaskInstance is stuck in `running` state but no process is actually executing it. Airflow's scheduler detects this when the heartbeat from the task times out and marks it as `failed`. You can configure `zombie_detection_interval` to tune how quickly this is detected. Prevent it by using appropriate `execution_timeout` on tasks and ensuring workers have stable infrastructure.

**Q: Your manager asks you to migrate 150 legacy cron jobs to Airflow in 3 months. How do you approach this?**

A: I'd break this into four phases. First, **inventory and categorise**: analyse all 150 cron jobs for schedule, dependencies, SLAs, failure behaviour, and owner. Most cron jobs fall into 3-5 patterns (ETL, report generation, data sync, cleanup). Second, **build templates**: create Airflow DAG templates for each pattern so migration becomes configuration, not custom code. Third, **run in parallel**: keep cron running while the equivalent Airflow DAG runs in a shadow mode — compare outputs for 2 weeks before cutting over. This de-risks each migration. Fourth, **migrate in business-value order**: start with the highest-risk jobs (longest chains, most dependencies) not the easiest ones, so the hard problems surface early while there's still buffer time. I'd also instrument everything with DAG tags (team, system, criticality) so the Airflow UI stays navigable as the DAG count grows. Red flag to watch for: cron jobs that rely on implicit sequencing from wall-clock timing — they need explicit `>>` dependencies in Airflow.

**Q: A DAG runs successfully every night but last week the downstream report showed wrong numbers. No task failed. How do you investigate?**

A: This is a "silent success" failure — the hardest type to catch. My investigation steps: (1) Check XComs from the suspect run — did the upstream task push the right row counts and metadata? A task can succeed but produce empty or stale data. (2) Look at the `execution_date` of the run — was it processing the right date's data? Time-zone mismatches cause off-by-one-day processing. (3) Check sensors — did any FileSensor or ExternalTaskSensor resolve instantly on a cached/stale file? (4) Review any BranchPythonOperator — was a validation branch skipped that should have caught a problem? (5) Check idempotency: if the task runs twice (manual trigger + scheduled), did the second run overwrite valid data with a partial result? Prevention: add data quality tasks after every load step that push row counts, null rates, and key metrics to XComs, then have a downstream `validate_output` task that raises `AirflowFailException` if the numbers are outside expected ranges.

**Q: You need to generate a separate DAG for each of 500 clients, each with slightly different schedules and parameters. How do you do this without creating 500 files?**

A: This is the dynamic DAG pattern. The approach: maintain a single `dag_factory.py` file that reads a config source (YAML file, database table, or API) and programmatically creates DAG objects in a loop at module import time. The key requirements: (1) Each generated `dag_id` must be unique and deterministic — I use `f"client_pipeline_{client_id}"`. (2) The loop must complete fast (< 30 seconds) — Airflow re-parses DAG files frequently. Avoid DB calls in the factory; use a cached config file instead. (3) Use `default_args` to set per-client retry/alerting, and pass client-specific params via `dag.params` or `Variable.get()`. (4) Add a uniqueness assertion to prevent duplicate `dag_id` if the config has errors. For 500+ DAGs, also tune `dag_discovery_safe_mode=False` and increase `min_file_process_interval`. At scale, consider DAG bundles or the Airflow 2.6+ `DynamicTask` API for cases where client config changes frequently.

---

## 18. Troubleshooting

### DAG not appearing in UI

```bash
# Check for parse errors
airflow dags list-import-errors

# Test import manually
python -c "import dags.dag_01_etl_pipeline"

# Check the scheduler log
docker-compose logs airflow-scheduler | grep ERROR
```

Common causes: syntax error in DAG file, circular import, exception raised at module import time, `start_date` is in the future.

### Tasks stuck in "queued" state

Usually a worker issue:
```bash
# Check workers are running
docker-compose ps

# Check Celery queue
docker-compose exec airflow-worker celery --app airflow.executors.celery_executor.app inspect active

# Check pool slots
airflow pools list
```

### XCom not found

```python
# Wrong: task_id doesn't match the actual task_id
ti.xcom_pull(task_ids="extract")  # but the task_id is "extract_data"

# For TaskGroup tasks, must include group prefix
ti.xcom_pull(task_ids="ingest.ingest_crm", key="crm_result")
```

### Scheduler not picking up new DAGs

```bash
# Force rescan
airflow dags reserialize

# Check scheduler health
airflow jobs check --job-type SchedulerJob
```

### Out of memory on workers

Increase Docker resources or reduce `worker_concurrency` in `airflow.cfg`. Large pandas DataFrames in tasks eat memory — use Spark or Dask for big data transformations, and use the Airflow worker only for orchestration.

### "DAG with dag_id already exists" error

Two DAG files are generating the same `dag_id`. With dynamic DAGs this can happen if the config has duplicate `name` fields. Add a uniqueness assertion in the factory:

```python
assert len(set(p["name"] for p in config["pipelines"])) == len(config["pipelines"]), \
    "Duplicate pipeline names in config"
```

---

## 19. Glossary

| Term | Definition |
|---|---|
| **DAG** | Directed Acyclic Graph. The workflow definition file in Airflow |
| **Task** | A specific instance of an operator in a DAG |
| **Operator** | Template that defines what a task does |
| **TaskInstance** | A specific execution of a task at a given `execution_date` |
| **DagRun** | An execution of a DAG at a given `execution_date` |
| **Scheduler** | Airflow service that parses DAGs and queues tasks |
| **Executor** | Runs task instances; determines parallelism strategy |
| **Worker** | Process that executes task callables (in CeleryExecutor) |
| **Webserver** | Airflow's web UI service |
| **Metadata DB** | Postgres database storing DAGRun, TaskInstance, XCom, etc. |
| **XCom** | Key-value store for inter-task data exchange |
| **Sensor** | Operator that polls for a condition before proceeding |
| **Hook** | Interface to external systems, uses connections |
| **Connection** | Named credential set stored in Airflow |
| **Variable** | Key-value store for runtime config |
| **Pool** | Resource group limiting concurrent task slots |
| **SLA** | Service Level Agreement; expected task completion time |
| **Trigger Rule** | Condition controlling when a task starts based on upstream state |
| **catchup** | Whether to backfill missed DAGRuns |
| **execution_date** | The logical date a DAGRun represents |
| **start_date** | Earliest execution_date a DAG can have |
| **schedule_interval** | How often to create DagRuns |
| **idempotency** | Property of tasks: safe to re-run with same result |
| **BranchPythonOperator** | Operator that returns task_id to follow; others are skipped |
| **TaskGroup** | Visual grouping of tasks in the UI (no scheduling effect) |
| **SubDAG** | Deprecated: mini-DAG embedded in parent (replaced by TaskGroups) |
| **dynamic DAGs** | Multiple DAGs generated from config at import time |
| **plugins** | Directory where custom operators, hooks, macros are auto-discovered |
| **Jinja templating** | `{{ ds }}`, `{{ execution_date }}` etc. expanded in operator args |
| **backfill** | Running a DAG for historical execution_dates |
| **zombie** | Task stuck in running state after its process died |

---

*End of Guide*

*This POC was built for Lead Data Engineer / Data Architect interview preparation, demonstrating real enterprise Airflow patterns: dynamic DAG generation, sensor-driven orchestration, parallel DQ with branching, TaskGroup hierarchies, and custom operators.*
