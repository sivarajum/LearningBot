"""
DAG 01: Classic ETL Pipeline with Retries, SLAs, XComs, and Branching
======================================================================
Demonstrates:
- PythonOperator tasks in an extract→validate→transform→load pattern
- retries=3 with retry_delay
- SLA monitoring per task
- XCom push/pull to pass row counts between tasks
- BranchPythonOperator for conditional execution
- email_on_failure configuration
- Task dependencies using the >> operator

Observability additions (ARJUN-01):
- Structured JSON logging in all task callables
- SLA miss callback (on_sla_miss) wired into the DAG definition
- Dead-letter queue (DLQ) task on the validation-failure branch

This DAG simulates a typical enterprise ETL: pulling raw transactions
from a source database, validating data quality, transforming to the
target schema, and loading into a data warehouse.
"""

import json
import random
import logging
from datetime import UTC, datetime, timedelta

logger = logging.getLogger(__name__)

# ---------------------------------------------------------------------------
# Airflow imports — gracefully degrade when running in simulator mode
# ---------------------------------------------------------------------------
try:
    from airflow import DAG
    from airflow.operators.python import PythonOperator, BranchPythonOperator
    from airflow.operators.empty import EmptyOperator
    from airflow.utils.dates import days_ago
    AIRFLOW_AVAILABLE = True
except ImportError:
    AIRFLOW_AVAILABLE = False
    # Provide stub classes so the file is importable without Airflow
    class DAG:  # noqa: E501
        def __init__(self, *a, **kw): pass
        def __enter__(self): return self
        def __exit__(self, *a): pass

    class PythonOperator:
        def __init__(self, *a, **kw): pass
        def __rshift__(self, other): return other

    class BranchPythonOperator(PythonOperator): pass

    class EmptyOperator(PythonOperator): pass

    def days_ago(n): return datetime.now(UTC) - timedelta(days=n)


# ---------------------------------------------------------------------------
# SLA miss callback — import gracefully so the file loads without the plugin
# ---------------------------------------------------------------------------
try:
    from plugins.callbacks import on_sla_miss
except ImportError:
    on_sla_miss = None


# ---------------------------------------------------------------------------
# DAG-level metadata
# ---------------------------------------------------------------------------
DAG_ID = "etl_transactions_pipeline"
DESCRIPTION = (
    "Enterprise ETL: extracts raw transactions, validates quality, "
    "transforms to star-schema, and loads into the warehouse."
)

DEFAULT_ARGS = {
    "owner": "data-engineering",
    "depends_on_past": False,
    "email": ["data-alerts@company.com"],
    "email_on_failure": True,       # config only — no real SMTP in dev
    "email_on_retry": False,
    "retries": 3,
    "retry_delay": timedelta(minutes=5),
    "retry_exponential_backoff": True,
    "max_retry_delay": timedelta(minutes=30),
    "execution_timeout": timedelta(hours=1),
    "sla": timedelta(hours=2),
}

# ---------------------------------------------------------------------------
# Task implementations
# ---------------------------------------------------------------------------

def extract_data(**context):
    """
    Extract raw transaction records from the source system.

    In production this would use PostgresHook / S3Hook.  Here we simulate
    by generating a deterministic dataset so the DAG can run in the simulator.

    Pushes extracted row count to XCom so downstream tasks can make decisions.
    """
    execution_date = context.get("execution_date", datetime.now(UTC))
    dag_id = context.get('dag').dag_id if context.get('dag') else DAG_ID
    run_id = context.get('run_id', 'unknown')

    logger.info(json.dumps({
        "event": "extract_start",
        "dag_id": dag_id,
        "run_id": run_id,
        "task_id": "extract_data",
        "timestamp": datetime.now(UTC).isoformat(),
        "execution_date": str(execution_date),
    }))

    # Simulate fetching from a database — vary count by day to exercise branching
    seed = hash(str(execution_date)) % 1000
    row_count = 500 + (seed % 5000)           # 500–5499 rows

    # Simulate a transient failure ~10 % of the time (Airflow will retry)
    if random.random() < 0.10:
        raise ConnectionError("Source DB connection timed out (transient). Will retry.")

    extracted_data = {
        "source": "postgres://txn-db/transactions",
        "row_count": row_count,
        "columns": ["txn_id", "customer_id", "amount", "currency", "ts", "status"],
        "extraction_ts": datetime.now(UTC).isoformat(),
        "min_ts": (datetime.now(UTC) - timedelta(hours=24)).isoformat(),
        "max_ts": datetime.now(UTC).isoformat(),
    }

    # Push to XCom — automatically available to downstream tasks
    ti = context["ti"]
    ti.xcom_push(key="extracted_row_count", value=row_count)
    ti.xcom_push(key="extraction_metadata", value=extracted_data)

    logger.info(json.dumps({
        "event": "extract_complete",
        "dag_id": dag_id,
        "run_id": run_id,
        "task_id": "extract_data",
        "timestamp": datetime.now(UTC).isoformat(),
        "row_count": row_count,
        "source": extracted_data["source"],
    }))
    return extracted_data


def validate_data(**context):
    """
    Run data quality checks on the extracted dataset.

    Checks performed:
      1. Row count above minimum threshold (> 100)
      2. No duplicate transaction IDs (simulated)
      3. Amount field is non-negative
      4. Null rate for critical columns < 1 %

    Pushes a validation_status XCom ("pass" | "fail") that the branch
    operator reads to decide the next step.
    """
    ti = context["ti"]
    dag_id = context.get('dag').dag_id if context.get('dag') else DAG_ID
    run_id = context.get('run_id', 'unknown')

    # Pull extraction metadata from the upstream task via XCom
    row_count = ti.xcom_pull(task_ids="extract_data", key="extracted_row_count")
    metadata = ti.xcom_pull(task_ids="extract_data", key="extraction_metadata")

    logger.info(json.dumps({
        "event": "validate_start",
        "dag_id": dag_id,
        "run_id": run_id,
        "task_id": "validate_data",
        "timestamp": datetime.now(UTC).isoformat(),
        "row_count": row_count,
    }))

    validation_results = {
        "row_count_check": row_count > 100,
        "duplicate_check": True,            # simulated — always passes
        "negative_amount_check": True,      # simulated
        "null_rate_check": row_count > 0,
        "row_count": row_count,
    }

    passed_checks = sum(validation_results[k] for k in validation_results if k.endswith("_check"))
    total_checks = sum(1 for k in validation_results if k.endswith("_check"))
    validation_status = "pass" if passed_checks == total_checks else "fail"

    ti.xcom_push(key="validation_status", value=validation_status)
    ti.xcom_push(key="validation_results", value=validation_results)

    logger.info(json.dumps({
        "event": "validate_complete",
        "dag_id": dag_id,
        "run_id": run_id,
        "task_id": "validate_data",
        "timestamp": datetime.now(UTC).isoformat(),
        "passed_checks": passed_checks,
        "total_checks": total_checks,
        "validation_status": validation_status,
    }))
    return validation_results


def check_validation_branch(**context):
    """
    BranchPythonOperator callable.

    Reads the validation_status XCom and returns the task_id of the next
    task to execute.  Airflow will skip all other downstream tasks.
    """
    ti = context["ti"]
    dag_id = context.get('dag').dag_id if context.get('dag') else DAG_ID
    run_id = context.get('run_id', 'unknown')
    status = ti.xcom_pull(task_ids="validate_data", key="validation_status")

    if status == "pass":
        logger.info(json.dumps({
            "event": "branch_decision",
            "dag_id": dag_id,
            "run_id": run_id,
            "task_id": "check_validation_branch",
            "timestamp": datetime.now(UTC).isoformat(),
            "decision": "transform_data",
            "reason": "validation_passed",
        }))
        return "transform_data"
    else:
        logger.warning(json.dumps({
            "event": "branch_decision",
            "dag_id": dag_id,
            "run_id": run_id,
            "task_id": "check_validation_branch",
            "timestamp": datetime.now(UTC).isoformat(),
            "decision": "write_to_dead_letter_queue",
            "reason": "validation_failed",
        }))
        return "write_to_dead_letter_queue"


def write_to_dlq(**context):
    """Write failed record metadata to dead-letter queue (local sim; prod: Pub/Sub DLQ)."""
    import os
    dag_id = context.get('dag').dag_id if context.get('dag') else DAG_ID
    run_id = context.get('run_id', 'unknown')

    dlq_dir = os.path.join(os.path.dirname(__file__), '..', 'data', 'dlq')
    os.makedirs(dlq_dir, exist_ok=True)

    record = {
        "dag_id": dag_id,
        "run_id": run_id,
        "failed_at": datetime.now(UTC).isoformat(),
        "reason": "validation_failed",
    }

    path = os.path.join(dlq_dir, f"dlq_{run_id}.json")
    with open(path, 'w') as f:
        json.dump(record, f, indent=2)

    logger.info(json.dumps({
        "event": "dlq_write",
        "dag_id": dag_id,
        "run_id": run_id,
        "task_id": "write_to_dead_letter_queue",
        "timestamp": datetime.now(UTC).isoformat(),
        "path": path,
        # Production: replace local file write with Pub/Sub publish:
        # pubsub_client.publish(topic_path, data=json.dumps(record).encode())
    }))


def handle_validation_failure(**context):
    """
    Called when validation fails.  In production this would:
    - Send an alert to PagerDuty / Slack
    - Move bad data to a quarantine S3 prefix
    - Create a JIRA ticket with the DQ report

    Here we just log and raise so Airflow marks the run as failed.
    """
    ti = context["ti"]
    dag_id = context.get('dag').dag_id if context.get('dag') else DAG_ID
    run_id = context.get('run_id', 'unknown')
    results = ti.xcom_pull(task_ids="validate_data", key="validation_results")

    logger.error(json.dumps({
        "event": "validation_failure",
        "dag_id": dag_id,
        "run_id": run_id,
        "task_id": "handle_validation_failure",
        "timestamp": datetime.now(UTC).isoformat(),
        "validation_results": results,
        "severity": "ERROR",
    }))
    raise ValueError(f"Data quality checks failed: {results}")


def transform_data(**context):
    """
    Transform raw records to the star-schema target format.

    Operations:
    - Currency normalisation (convert to USD)
    - Timestamp standardisation (UTC)
    - Customer dimension lookup
    - Deduplication
    - SCD Type 2 change detection for customer dimension

    Pushes transformed_row_count to XCom.
    """
    ti = context["ti"]
    dag_id = context.get('dag').dag_id if context.get('dag') else DAG_ID
    run_id = context.get('run_id', 'unknown')
    row_count = ti.xcom_pull(task_ids="extract_data", key="extracted_row_count")

    logger.info(json.dumps({
        "event": "transform_start",
        "dag_id": dag_id,
        "run_id": run_id,
        "task_id": "transform_data",
        "timestamp": datetime.now(UTC).isoformat(),
        "input_row_count": row_count,
    }))

    # Simulate transformation logic — some rows dropped as duplicates
    dedup_dropped = int(row_count * 0.02)   # ~2 % duplicates
    transformed_count = row_count - dedup_dropped

    transform_summary = {
        "input_rows": row_count,
        "dedup_dropped": dedup_dropped,
        "output_rows": transformed_count,
        "currency_conversions": int(transformed_count * 0.15),
        "scd2_updates": int(transformed_count * 0.005),
        "transform_ts": datetime.now(UTC).isoformat(),
    }

    ti.xcom_push(key="transformed_row_count", value=transformed_count)
    ti.xcom_push(key="transform_summary", value=transform_summary)

    logger.info(json.dumps({
        "event": "transform_complete",
        "dag_id": dag_id,
        "run_id": run_id,
        "task_id": "transform_data",
        "timestamp": datetime.now(UTC).isoformat(),
        "output_rows": transformed_count,
        "dedup_dropped": dedup_dropped,
    }))
    return transform_summary


def load_data(**context):
    """
    Load transformed records into the data warehouse.

    Strategy: UPSERT (merge on txn_id) so reruns are idempotent.

    In production uses BigQueryHook or PostgresHook with an explicit
    transaction to ensure atomicity.
    """
    ti = context["ti"]
    dag_id = context.get('dag').dag_id if context.get('dag') else DAG_ID
    run_id = context.get('run_id', 'unknown')
    transformed_count = ti.xcom_pull(task_ids="transform_data", key="transformed_row_count")
    transform_summary = ti.xcom_pull(task_ids="transform_data", key="transform_summary")

    logger.info(json.dumps({
        "event": "load_start",
        "dag_id": dag_id,
        "run_id": run_id,
        "task_id": "load_data",
        "timestamp": datetime.now(UTC).isoformat(),
        "row_count": transformed_count,
        "destination": "bigquery://dw.fact_transactions",
    }))

    # Simulate load — occasional write failures to demonstrate retry behaviour
    if random.random() < 0.05:
        raise IOError("Warehouse write timeout (transient). Airflow will retry.")

    load_summary = {
        "rows_loaded": transformed_count,
        "rows_inserted": int(transformed_count * 0.98),
        "rows_updated": int(transformed_count * 0.02),
        "destination": "bigquery://dw.fact_transactions",
        "load_ts": datetime.now(UTC).isoformat(),
        "duration_seconds": round(transformed_count / 10000 * 45, 1),
    }

    ti.xcom_push(key="load_summary", value=load_summary)

    logger.info(json.dumps({
        "event": "load_complete",
        "dag_id": dag_id,
        "run_id": run_id,
        "task_id": "load_data",
        "timestamp": datetime.now(UTC).isoformat(),
        "rows_inserted": load_summary["rows_inserted"],
        "rows_updated": load_summary["rows_updated"],
        "duration_seconds": load_summary["duration_seconds"],
    }))
    return load_summary


def notify_success(**context):
    """
    Post-load success notification.

    In production: send Slack message, update metadata catalogue,
    trigger downstream DAGs via TriggerDagRunOperator.
    """
    ti = context["ti"]
    dag_id = context.get('dag').dag_id if context.get('dag') else DAG_ID
    run_id = context.get('run_id', 'unknown')
    load_summary = ti.xcom_pull(task_ids="load_data", key="load_summary")

    logger.info(json.dumps({
        "event": "pipeline_success",
        "dag_id": dag_id,
        "run_id": run_id,
        "task_id": "notify_success",
        "timestamp": datetime.now(UTC).isoformat(),
        "rows_loaded": load_summary.get("rows_loaded", 0) if load_summary else 0,
        "destination": load_summary.get("destination") if load_summary else None,
    }))
    return {"status": "success", "summary": load_summary}


# ---------------------------------------------------------------------------
# DAG definition
# ---------------------------------------------------------------------------
_sla_callback_kwargs = {}
if on_sla_miss is not None:
    _sla_callback_kwargs["sla_miss_callback"] = on_sla_miss

with DAG(
    dag_id=DAG_ID,
    description=DESCRIPTION,
    default_args=DEFAULT_ARGS,
    schedule_interval="@daily",
    start_date=days_ago(7),
    catchup=False,
    max_active_runs=1,
    tags=["etl", "transactions", "poc-07"],
    doc_md=__doc__,
    **_sla_callback_kwargs,
) as dag:

    # ── Task definitions ────────────────────────────────────────────────────

    t_extract = PythonOperator(
        task_id="extract_data",
        python_callable=extract_data,
        sla=timedelta(minutes=30),
        doc_md="Extract raw transactions from source postgres DB.",
    )

    t_validate = PythonOperator(
        task_id="validate_data",
        python_callable=validate_data,
        sla=timedelta(minutes=15),
        doc_md="Run DQ checks: row count, nulls, duplicates, value ranges.",
    )

    t_branch = BranchPythonOperator(
        task_id="check_validation_branch",
        python_callable=check_validation_branch,
        doc_md="Route to transform or DLQ/failure handler based on validation result.",
    )

    t_dlq = PythonOperator(
        task_id="write_to_dead_letter_queue",
        python_callable=write_to_dlq,
        doc_md="Write failed record metadata to DLQ (local file sim; prod: Pub/Sub).",
    )

    t_fail_handler = PythonOperator(
        task_id="handle_validation_failure",
        python_callable=handle_validation_failure,
        doc_md="Quarantine bad data and raise an alert.",
    )

    t_transform = PythonOperator(
        task_id="transform_data",
        python_callable=transform_data,
        sla=timedelta(minutes=45),
        doc_md="Normalise, deduplicate, and reshape to star schema.",
    )

    t_load = PythonOperator(
        task_id="load_data",
        python_callable=load_data,
        sla=timedelta(minutes=30),
        doc_md="UPSERT transformed records into BigQuery fact_transactions.",
    )

    t_notify = PythonOperator(
        task_id="notify_success",
        python_callable=notify_success,
        doc_md="Send Slack notification and update data catalogue.",
    )

    # ── Task dependencies (the pipeline graph) ──────────────────────────────
    #
    #   extract_data
    #       │
    #   validate_data
    #       │
    #   check_validation_branch
    #      / \
    #  dlq  transform_data
    #   │         │
    # fail_handler  load_data
    #                  │
    #              notify_success
    #
    t_extract >> t_validate >> t_branch
    t_branch >> t_dlq >> t_fail_handler
    t_branch >> t_transform >> t_load >> t_notify


# Make the dag object accessible for the simulator when this module is imported
__all__ = ["dag", "DAG_ID", "DEFAULT_ARGS"]
