# Airflow Orchestration -- Running Guide

Complete guide for running, testing, and deploying the Enterprise Airflow Orchestration Platform (POC-07).

## Prerequisites

- Python 3.11+
- pip
- Docker and Docker Compose (only for full Airflow stack; not required for simulator mode)

## Install

```bash
cd Sj-Prod/Airflow-Orchestration

# Install runtime dependencies
pip install -r requirements.txt

# Install test dependencies
pip install -r requirements-test.txt
```

## Running Tests

All tests run without Apache Airflow installed. The DAG files and simulator use stub classes that mimic the Airflow API.

```bash
# Run all tests
PYTHONPATH=. pytest -v

# Run all tests with coverage
PYTHONPATH=. pytest --cov=src --cov=plugins --cov=dags -v

# Run individual test files
PYTHONPATH=. pytest tests/test_validation_operator.py -v
PYTHONPATH=. pytest tests/test_simulator.py -v
PYTHONPATH=. pytest tests/test_api.py -v
PYTHONPATH=. pytest tests/test_dags.py -v

# Run a single test
PYTHONPATH=. pytest tests/test_simulator.py::TestXComStore::test_push_and_pull_basic -v
```

### Test suite overview

| File | What it covers |
|------|---------------|
| `tests/test_validation_operator.py` | Custom DataValidationOperator: all 8 check types, pass/fail logic, XCom push, report structure, SLA miss callback |
| `tests/test_simulator.py` | DAGSimulator: instantiation, DAG loading, topological sort, XComStore, FakeTaskInstance, simulation execution, branch handling, retry logic, error handling |
| `tests/test_api.py` | FastAPI endpoints: /health, /dags, /dags/{id}, /dags/{id}/graph, /dags/{id}/run, /xcoms, /concepts, /reload |
| `tests/test_dags.py` | DAG definitions: importability, DAG_ID constants, task callable exports, dynamic DAG factory, Airflow fallback stubs |

## Simulating DAGs

The simulator runs DAG task callables locally in dependency order without Docker or Airflow. XComs are passed between tasks exactly as they would be in real Airflow.

```bash
# Simulate all main DAGs (default 5)
python main.py simulate

# Simulate a specific DAG
python main.py simulate etl_transactions_pipeline
python main.py simulate data_quality_pipeline
python main.py simulate multi_source_etl_customer_journey
python main.py simulate sensor_vendor_file_pipeline
python main.py simulate etl_sales

# Simulate multiple DAGs
python main.py simulate etl_sales etl_inventory
```

The output shows a step-by-step execution trace with task status, duration, retry attempts, and XCom values pushed by each task.

## Listing Available DAGs

```bash
python main.py list
```

This prints a table of all discovered DAGs with their schedule, task count, and owner. Includes both statically defined DAGs and dynamically generated ones.

## Running the API

```bash
# Start FastAPI on port 8000
python main.py api

# Custom port
python main.py api --api-port 9000
```

Once running, the interactive API docs are at:
- Swagger UI: http://localhost:8000/docs
- ReDoc: http://localhost:8000/redoc

### API endpoints

| Method | Path | Description |
|--------|------|-------------|
| GET | `/health` | Liveness check |
| GET | `/dags` | List all DAGs with metadata |
| GET | `/dags/{dag_id}` | DAG detail with task list |
| POST | `/dags/{dag_id}/run` | Simulate a DAG run |
| GET | `/dags/{dag_id}/graph` | Task dependency graph (nodes + edges) |
| GET | `/xcoms` | XCom data from last simulation |
| GET | `/concepts` | Airflow concepts dictionary |
| POST | `/reload` | Force reload all DAG modules |

## Running the UI

```bash
# Start Streamlit on port 8501
python main.py ui

# Custom port
python main.py ui --ui-port 9501
```

The Streamlit UI provides four tabs:
1. **DAGs** -- browse all discovered DAGs, inspect tasks and metadata
2. **Run Simulation** -- trigger DAG simulations and see step-by-step traces
3. **Task Graph** -- interactive Plotly dependency graph for any DAG
4. **Learn Concepts** -- Airflow concepts explained with interview-ready answers

## Running API + UI Together

```bash
python main.py all
```

This starts the API in a background thread (port 8000) and the Streamlit UI in the main thread (port 8501).

## Running with Docker

### Lightweight mode (simulator only, no Airflow)

```bash
# Build
docker build -t poc-07-airflow .

# Run API only
docker run -p 8000:8000 poc-07-airflow

# Run UI only
docker run -p 8501:8501 poc-07-airflow python main.py ui
```

### Full Airflow stack

The `docker-compose.yml` brings up a complete Airflow 2.9 environment with CeleryExecutor:

```bash
# Start everything
docker compose up -d

# Stop and remove volumes
docker compose down -v
```

Services and ports:

| Service | Port | URL |
|---------|------|-----|
| Airflow Webserver | 8080 | http://localhost:8080 (admin/admin) |
| FastAPI Simulator | 8000 | http://localhost:8000/docs |
| Streamlit UI | 8501 | http://localhost:8501 |
| Flower (Celery monitor) | 5555 | http://localhost:5555 |
| PostgreSQL | 5432 | metadata database |
| Redis | 6379 | Celery broker |

## DAG Reference

### DAG 01: ETL Transactions Pipeline (`etl_transactions_pipeline`)

Classic ETL pattern: extract raw transactions, validate data quality, transform to star schema, and load into the warehouse.

- **Schedule:** `@daily`
- **Pattern:** Linear with branch (BranchPythonOperator)
- **Tasks:** extract_data -> validate_data -> check_validation_branch -> [transform_data -> load_data -> notify_success | handle_validation_failure]
- **Features:** XCom-based data passing, retry with exponential backoff (retries=3), SLA monitoring, dead-letter queue on validation failure

### DAG 02: Dynamic DAG Factory (`etl_sales`, `etl_inventory`, `etl_customer_360`, `etl_marketing_attribution`)

Generates multiple DAGs at import time from `config/pipeline_config.json`. All share the same task structure but vary in schedule, sources, and metadata.

- **Schedule:** Varies per pipeline (daily, hourly, cron)
- **Pattern:** Linear (extract -> validate -> transform -> load)
- **Features:** Config-driven, zero new Python to add a pipeline, `globals()` registration for Airflow discovery

### DAG 03: Sensor Pipeline (`sensor_vendor_file_pipeline`)

Waits for a vendor file (FileSensor) and an upstream DAG (ExternalTaskSensor) before processing.

- **Schedule:** `0 4 * * *` (4 AM daily)
- **Pattern:** Sensor-gated linear
- **Tasks:** [wait_for_vendor_file, wait_for_dimension_refresh] -> check_file_metadata -> process_vendor_file -> join_with_dimension -> load_vendor_to_warehouse
- **Features:** `mode='reschedule'` (production best practice), `soft_fail=True`, cross-DAG dependency via ExternalTaskSensor

### DAG 04: Data Quality Pipeline (`data_quality_pipeline`)

Dedicated DQ DAG with parallel checks, result aggregation, and three-branch severity routing.

- **Schedule:** `@daily`
- **Pattern:** Fan-out/fan-in with branch
- **Tasks:** start_dq_checks -> [check_null_rates, check_row_count, check_duplicates, check_referential_integrity, check_data_freshness] -> aggregate_dq_results -> branch_on_dq_result -> [publish_to_downstream | send_soft_fail_alert | quarantine_data] -> finalize_dq_run
- **Features:** Parallel execution, severity-based branching (all_pass/soft_fail/hard_fail), TriggerRule.ALL_DONE for aggregation

### DAG 05: Multi-Source ETL (`multi_source_etl_customer_journey`)

Ingests from three systems (CRM, ERP, Analytics) in parallel using TaskGroups, resolves customer entities, and publishes to BI and ML consumers.

- **Schedule:** `0 3 * * *` (3 AM daily)
- **Pattern:** TaskGroup pipeline (ingest -> transform -> publish)
- **Tasks:** pipeline_start -> [ingest_crm, ingest_erp, ingest_analytics] -> validate_completeness -> resolve_entities -> join_sessions -> build_journey -> [publish_bi, publish_ml_features] -> update_catalogue -> pipeline_end
- **Features:** TaskGroups for visual organisation, entity resolution, multi-consumer publish (BI + ML feature store)

## Custom Operator Reference

### DataValidationOperator

Location: `plugins/operators/validation_operator.py`

A reusable operator that runs configurable data quality checks against a table and pushes a validation report to XCom.

**Parameters:**

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `table` | str | required | Target table to validate |
| `connection_id` | str | `postgres_default` | Airflow connection ID |
| `checks` | list[dict] | `[]` | Check definitions (see types below) |
| `fail_on_error` | bool | `True` | Raise on check failure |
| `xcom_key` | str | `validation_report` | XCom key for the report |

**Supported check types:**

| Check Type | Required Fields | Description |
|-----------|----------------|-------------|
| `not_null` | `column`, `threshold` | Null rate below threshold |
| `row_count_min` | `threshold` | Table has at least N rows |
| `row_count_max` | `threshold` | Table has at most N rows |
| `value_range` | `column`, `min`, `max` | Values within range |
| `freshness` | `column`, `max_age_hours` | Most recent record is recent enough |
| `unique` | `column` or `columns` | No duplicate values |
| `regex` | `column`, `pattern` | Values match regex pattern |
| `referential_integrity` | `column`, `reference_table`, `reference_column` | FK values exist in reference |

**Usage example:**

```python
from plugins.operators.validation_operator import DataValidationOperator

t_validate = DataValidationOperator(
    task_id="validate_transactions",
    table="fact_transactions",
    connection_id="postgres_dw",
    checks=[
        {"type": "not_null", "column": "txn_id", "threshold": 0.0},
        {"type": "row_count_min", "threshold": 100},
        {"type": "freshness", "column": "created_at", "max_age_hours": 2},
    ],
    fail_on_error=True,
)
```

### SLA Miss Callback

Location: `plugins/callbacks.py`

`on_sla_miss(dag, task_list, blocking_task_list, slas, blocking_tis)` -- emits a structured JSON WARNING log when any task misses its SLA. Includes a commented-out webhook pattern for Slack/PagerDuty integration.

Wire into a DAG with `sla_miss_callback=on_sla_miss`.

## Production Deployment Notes

For a real Airflow deployment:

1. **Use a managed service:** Google Cloud Composer, AWS MWAA, or Astronomer. These handle scheduler HA, worker autoscaling, and metadata DB management.

2. **Executor choice:**
   - CeleryExecutor for most enterprise ETL teams (distributed, battle-tested)
   - KubernetesExecutor when you need per-task isolation and autoscaling (ML pipelines, GPU tasks)

3. **Connections and secrets:** Store credentials in Airflow's connection store or an external secrets backend (HashiCorp Vault, AWS Secrets Manager, GCP Secret Manager). Never hardcode credentials in DAG files.

4. **DAG deployment:** Use CI/CD to sync `dags/` and `plugins/` to the Airflow environment. The `docker-compose.yml` in this project mounts these as volumes. In production, use `gsutil rsync`, `aws s3 sync`, or a Git-sync sidecar.

5. **Monitoring:** Configure `on_failure_callback` and `sla_miss_callback` on all production DAGs. Integrate with PagerDuty or Opsgenie for alerting. Use Airflow's built-in metrics endpoint with Prometheus/Grafana for dashboards.

6. **Pools:** Use Airflow pools to limit concurrent access to rate-limited external APIs or databases. Example: a pool of 5 slots for a vendor API that allows 5 concurrent connections.

7. **Testing:** Run `pytest` in CI before deploying DAG changes. The test suite in this project validates DAG importability, operator logic, and API correctness without requiring an Airflow installation.

## Linting

```bash
# From the Sj-Prod root (shared ruff.toml)
ruff check Airflow-Orchestration/
ruff format Airflow-Orchestration/
```
