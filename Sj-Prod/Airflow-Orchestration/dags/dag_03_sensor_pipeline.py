"""
DAG 03: Sensor Pipeline — FileSensor + ExternalTaskSensor
==========================================================
Demonstrates:
- FileSensor: pause DAG execution until an input file appears in a directory
- ExternalTaskSensor: wait for a task in a *different* DAG to complete
  before continuing (cross-DAG dependency)
- Timeout and poke_interval configuration for sensors
- Downstream processing tasks that run after sensors unblock
- soft_fail=True on sensor to skip gracefully if file never arrives

Real-world scenario:
  A partner system drops a vendor CSV to an SFTP/S3 location every night.
  Our DAG cannot start processing until the file is confirmed present.
  Additionally, a dimension table must have been refreshed by dag_01 before
  we can join against it.

Interview talking point:
  "Sensors are a first-class Airflow citizen for event-driven orchestration.
  We used FileSensor + S3KeySensor extensively at [Company] to decouple
  upstream data producers from our processing DAGs without polling in
  application code."
"""

import json
import logging
import time
from datetime import UTC, datetime, timedelta
from pathlib import Path

logger = logging.getLogger(__name__)

# ---------------------------------------------------------------------------
# Airflow imports with graceful fallback
# ---------------------------------------------------------------------------
try:
    from airflow import DAG
    from airflow.operators.python import PythonOperator
    from airflow.sensors.filesystem import FileSensor
    from airflow.sensors.external_task import ExternalTaskSensor
    from airflow.utils.dates import days_ago
    AIRFLOW_AVAILABLE = True
except ImportError:
    AIRFLOW_AVAILABLE = False

    class DAG:
        def __init__(self, dag_id="", *a, **kw):
            self.dag_id = dag_id
        def __enter__(self): return self
        def __exit__(self, *a): pass

    class PythonOperator:
        def __init__(self, task_id="", python_callable=None, **kw):
            self.task_id = task_id
            self.python_callable = python_callable
        def __rshift__(self, other):
            if isinstance(other, list):
                for o in other: o
            return other
        def __rrshift__(self, other): return self

    class FileSensor(PythonOperator):
        pass

    class ExternalTaskSensor(PythonOperator):
        pass

    def days_ago(n): return datetime.now(UTC) - timedelta(days=n)


# ---------------------------------------------------------------------------
# DAG-level config
# ---------------------------------------------------------------------------
DAG_ID = "sensor_vendor_file_pipeline"

DEFAULT_ARGS = {
    "owner": "data-engineering",
    "depends_on_past": False,
    "email": ["data-alerts@company.com"],
    "email_on_failure": True,
    "email_on_retry": False,
    "retries": 1,
    "retry_delay": timedelta(minutes=10),
}

# Where the partner file is expected to land
WATCH_DIR = Path(__file__).resolve().parent.parent / "data"
VENDOR_FILE_PATTERN = "vendor_sales_*.csv"


# ---------------------------------------------------------------------------
# Task callables
# ---------------------------------------------------------------------------

def check_file_metadata(**context):
    """
    After the FileSensor confirms the file exists, read its metadata:
    size, row count estimate, creation timestamp.

    Pushes file_info to XCom for the next task.
    """
    ti = context["ti"]

    # In production: use S3Hook.head_object or os.stat()
    file_info = {
        "file_path": str(WATCH_DIR / "vendor_sales_sample.csv"),
        "size_bytes": 2_450_000,
        "estimated_rows": 45000,
        "detected_at": datetime.now(UTC).isoformat(),
    }

    ti.xcom_push(key="file_info", value=file_info)
    logger.info(json.dumps({
        "event": "file_metadata_checked",
        "dag_id": DAG_ID,
        "run_id": context.get('run_id', 'unknown'),
        "task_id": "check_file_metadata",
        "timestamp": datetime.now(UTC).isoformat(),
        "file_path": file_info["file_path"],
        "size_bytes": file_info["size_bytes"],
        "estimated_rows": file_info["estimated_rows"],
    }))
    return file_info


def process_vendor_file(**context):
    """
    Parse and ingest the vendor CSV.

    Steps:
    1. Read file from landing zone
    2. Detect encoding and delimiter
    3. Apply schema mapping to canonical format
    4. Validate required columns present
    5. Write to staging table
    """
    ti = context["ti"]
    file_info = ti.xcom_pull(task_ids="check_file_metadata", key="file_info")

    estimated_rows = file_info.get("estimated_rows", 0) if file_info else 0
    logger.info("Processing vendor file: %d estimated rows", estimated_rows)

    # Simulate processing time proportional to file size
    time.sleep(0.05)

    result = {
        "rows_processed": estimated_rows,
        "rows_rejected": int(estimated_rows * 0.002),
        "staging_table": "staging.vendor_sales_raw",
        "processing_ts": datetime.now(UTC).isoformat(),
    }

    ti.xcom_push(key="vendor_process_result", value=result)
    logger.info(json.dumps({
        "event": "vendor_file_processed",
        "dag_id": DAG_ID,
        "run_id": context.get('run_id', 'unknown'),
        "task_id": "process_vendor_file",
        "timestamp": datetime.now(UTC).isoformat(),
        "rows_processed": result["rows_processed"],
        "rows_rejected": result["rows_rejected"],
        "staging_table": result["staging_table"],
    }))
    return result


def join_with_dimension(**context):
    """
    Join vendor data with the customer dimension table that was refreshed
    by dag_01 (guarded by ExternalTaskSensor).

    This is the cross-DAG dependency payoff: we are guaranteed that
    dim_customer is fresh before we run this join.
    """
    ti = context["ti"]
    vendor_result = ti.xcom_pull(task_ids="process_vendor_file", key="vendor_process_result")
    rows = vendor_result.get("rows_processed", 0) if vendor_result else 0

    logger.info("Joining %d vendor rows with dim_customer", rows)

    # Simulate join
    join_result = {
        "input_rows": rows,
        "matched_customers": int(rows * 0.92),
        "unmatched_rows": int(rows * 0.08),
        "output_table": "staging.vendor_sales_enriched",
        "join_ts": datetime.now(UTC).isoformat(),
    }

    ti.xcom_push(key="join_result", value=join_result)
    logger.info(json.dumps({
        "event": "dimension_join_complete",
        "dag_id": DAG_ID,
        "run_id": context.get('run_id', 'unknown'),
        "task_id": "join_with_dimension",
        "timestamp": datetime.now(UTC).isoformat(),
        "matched_customers": join_result["matched_customers"],
        "unmatched_rows": join_result["unmatched_rows"],
    }))
    return join_result


def load_vendor_to_warehouse(**context):
    """
    Final load of enriched vendor data into the warehouse fact table.
    Runs after both sensors have confirmed readiness.
    """
    ti = context["ti"]
    join_result = ti.xcom_pull(task_ids="join_with_dimension", key="join_result")
    rows = join_result.get("matched_customers", 0) if join_result else 0

    logger.info("Loading %d enriched rows to warehouse", rows)

    load_result = {
        "rows_loaded": rows,
        "destination": "bigquery://dw.fact_vendor_sales",
        "load_ts": datetime.now(UTC).isoformat(),
    }

    ti.xcom_push(key="load_result", value=load_result)
    logger.info(json.dumps({
        "event": "warehouse_load_complete",
        "dag_id": DAG_ID,
        "run_id": context.get('run_id', 'unknown'),
        "task_id": "load_vendor_to_warehouse",
        "timestamp": datetime.now(UTC).isoformat(),
        "rows_loaded": rows,
        "destination": load_result["destination"],
    }))
    return load_result


# ---------------------------------------------------------------------------
# DAG definition
# ---------------------------------------------------------------------------
with DAG(
    dag_id=DAG_ID,
    description="Vendor file ingestion with FileSensor and ExternalTaskSensor",
    default_args=DEFAULT_ARGS,
    schedule_interval="0 4 * * *",      # 4 AM daily — vendor drops file by 3 AM
    start_date=days_ago(7),
    catchup=False,
    max_active_runs=1,
    tags=["sensors", "vendor", "poc-07"],
    doc_md=__doc__,
) as dag:

    # ── Sensor 1: Wait for vendor file in the data/ directory ───────────────
    #
    # poke_interval=300  → check every 5 minutes
    # timeout=7200       → give up after 2 hours (file should arrive by 6 AM)
    # mode="reschedule"  → release the worker slot between pokes (production best practice)
    # soft_fail=True     → mark as SKIPPED rather than FAILED if timeout hits
    #                       (allows the rest of the run graph to proceed or skip cleanly)
    t_wait_for_file = FileSensor(
        task_id="wait_for_vendor_file",
        filepath=str(WATCH_DIR / VENDOR_FILE_PATTERN),
        fs_conn_id="fs_default",
        poke_interval=300,              # 5 minutes
        timeout=7200,                   # 2 hours
        mode="reschedule",
        soft_fail=True,
        doc_md=(
            "Block until the vendor CSV appears under data/. "
            "Uses reschedule mode to not occupy a worker slot while waiting."
        ),
    )

    # ── Sensor 2: Wait for dim table refresh from dag_01 ───────────────────
    #
    # ExternalTaskSensor waits for a specific task in a different DAG.
    # execution_delta=timedelta(0) means same logical execution date.
    # This ensures our join task always has a fresh dimension table.
    t_wait_for_dim = ExternalTaskSensor(
        task_id="wait_for_dimension_refresh",
        external_dag_id="etl_transactions_pipeline",
        external_task_id="load_data",
        execution_delta=timedelta(hours=0),
        poke_interval=120,              # check every 2 minutes
        timeout=3600,                   # wait up to 1 hour
        mode="reschedule",
        soft_fail=True,
        doc_md=(
            "Wait for dag_01's load_data task to succeed before joining "
            "vendor data against the refreshed dimension tables."
        ),
    )

    # ── Processing tasks that run after both sensors unblock ────────────────
    t_check_metadata = PythonOperator(
        task_id="check_file_metadata",
        python_callable=check_file_metadata,
    )

    t_process_vendor = PythonOperator(
        task_id="process_vendor_file",
        python_callable=process_vendor_file,
    )

    t_join_dim = PythonOperator(
        task_id="join_with_dimension",
        python_callable=join_with_dimension,
    )

    t_load = PythonOperator(
        task_id="load_vendor_to_warehouse",
        python_callable=load_vendor_to_warehouse,
    )

    # ── Dependency graph ────────────────────────────────────────────────────
    #
    #   wait_for_vendor_file ──┐
    #                          ├── check_file_metadata
    #   wait_for_dimension ────┘        │
    #                              process_vendor_file
    #                                   │
    #                              join_with_dimension
    #                                   │
    #                           load_vendor_to_warehouse
    #
    if AIRFLOW_AVAILABLE:
        [t_wait_for_file, t_wait_for_dim] >> t_check_metadata
    else:
        t_wait_for_file >> t_check_metadata
        t_wait_for_dim >> t_check_metadata
    t_check_metadata >> t_process_vendor >> t_join_dim >> t_load


__all__ = ["dag", "DAG_ID"]
