"""
DAG 04: Data Quality Pipeline with Branching
=============================================
Demonstrates:
- Dedicated DQ DAG (best practice: separate DQ from ETL)
- BranchPythonOperator to route based on check severity
- Multiple DQ checks running as independent parallel tasks
- Aggregating check results with a downstream join task
- Three-branch routing: all_pass → publish | soft_fail → alert_and_publish
  | hard_fail → quarantine_and_stop
- EmptyOperator used as join/gate nodes
- Trigger rules: TriggerRule.ONE_SUCCESS for join nodes

Real-world context:
  At large enterprises (Home Depot, KLM), a dedicated DQ DAG runs after
  each ETL pipeline.  It checks the loaded data *before* downstream BI
  tools or ML models consume it.  This DAG demonstrates that pattern.
"""

import json
import logging
import random
from datetime import UTC, datetime, timedelta

logger = logging.getLogger(__name__)

# ---------------------------------------------------------------------------
# Airflow imports with graceful fallback
# ---------------------------------------------------------------------------
try:
    from airflow import DAG
    from airflow.operators.python import PythonOperator, BranchPythonOperator
    from airflow.operators.empty import EmptyOperator
    from airflow.utils.dates import days_ago
    from airflow.utils.trigger_rule import TriggerRule
    AIRFLOW_AVAILABLE = True
except ImportError:
    AIRFLOW_AVAILABLE = False

    class TriggerRule:
        ALL_SUCCESS = "all_success"
        ONE_SUCCESS = "one_success"
        ALL_DONE = "all_done"
        NONE_FAILED = "none_failed"

    class DAG:
        def __init__(self, dag_id="", *a, **kw):
            self.dag_id = dag_id
        def __enter__(self): return self
        def __exit__(self, *a): pass

    class PythonOperator:
        def __init__(self, task_id="", python_callable=None, **kw):
            self.task_id = task_id
            self.python_callable = python_callable
        def __rshift__(self, other): return other
        def __rrshift__(self, other): return self

    class BranchPythonOperator(PythonOperator): pass

    class EmptyOperator:
        def __init__(self, task_id="", **kw):
            self.task_id = task_id
        def __rshift__(self, other): return other
        def __rrshift__(self, other): return self

    def days_ago(n): return datetime.now(UTC) - timedelta(days=n)


# ---------------------------------------------------------------------------
# Constants
# ---------------------------------------------------------------------------
DAG_ID = "data_quality_pipeline"

DEFAULT_ARGS = {
    "owner": "data-quality",
    "depends_on_past": False,
    "email": ["dq-alerts@company.com"],
    "email_on_failure": True,
    "email_on_retry": False,
    "retries": 1,
    "retry_delay": timedelta(minutes=5),
}

# DQ thresholds
THRESHOLDS = {
    "max_null_rate": 0.01,          # 1 % max null rate on critical columns
    "min_row_count": 100,           # minimum rows expected
    "max_duplicate_rate": 0.005,    # 0.5 % max duplicate rate
    "max_referential_failures": 50, # max FK violations allowed
    "min_freshness_minutes": 60,    # data must be < 60 min old
    "value_range_pass_rate": 0.999, # 99.9 % rows must have valid amounts
}


# ---------------------------------------------------------------------------
# Individual DQ check functions
# ---------------------------------------------------------------------------

def check_null_rates(**context):
    """
    Check null rates across all critical columns.
    Critical columns: customer_id, txn_id, amount, ts
    """
    ti = context["ti"]

    # Simulate null rate measurement
    null_rates = {
        "customer_id": round(random.uniform(0, 0.008), 4),
        "txn_id": round(random.uniform(0, 0.001), 4),
        "amount": round(random.uniform(0, 0.005), 4),
        "ts": round(random.uniform(0, 0.002), 4),
    }

    threshold = THRESHOLDS["max_null_rate"]
    violations = {col: rate for col, rate in null_rates.items() if rate > threshold}
    passed = len(violations) == 0

    result = {
        "check": "null_rates",
        "passed": passed,
        "severity": "hard" if not passed and any(r > threshold * 3 for r in violations.values()) else "soft",
        "null_rates": null_rates,
        "violations": violations,
        "threshold": threshold,
        "ts": datetime.now(UTC).isoformat(),
    }

    ti.xcom_push(key="null_rate_result", value=result)
    log_fn = logger.info if passed else logger.warning
    log_fn(json.dumps({
        "event": "dq_check_null_rates",
        "dag_id": DAG_ID,
        "run_id": context.get('run_id', 'unknown'),
        "task_id": "check_null_rates",
        "timestamp": datetime.now(UTC).isoformat(),
        "passed": passed,
        "violations": violations,
        "severity": result["severity"],
    }))
    return result


def check_row_count(**context):
    """
    Verify the table has at least the minimum expected row count.
    A sharp drop in row count often indicates an upstream pipeline failure.
    """
    ti = context["ti"]

    actual_rows = 500 + random.randint(0, 9500)
    minimum = THRESHOLDS["min_row_count"]
    passed = actual_rows >= minimum

    result = {
        "check": "row_count",
        "passed": passed,
        "severity": "hard" if not passed else "none",
        "actual_rows": actual_rows,
        "minimum_expected": minimum,
        "ts": datetime.now(UTC).isoformat(),
    }

    ti.xcom_push(key="row_count_result", value=result)
    logger.info(json.dumps({
        "event": "dq_check_row_count",
        "dag_id": DAG_ID,
        "run_id": context.get('run_id', 'unknown'),
        "task_id": "check_row_count",
        "timestamp": datetime.now(UTC).isoformat(),
        "passed": passed,
        "actual_rows": actual_rows,
        "minimum_expected": minimum,
    }))
    return result


def check_duplicates(**context):
    """
    Detect duplicate transaction IDs using a COUNT vs COUNT(DISTINCT) approach.
    """
    ti = context["ti"]

    total_rows = 10000
    duplicate_rate = round(random.uniform(0, 0.003), 4)
    duplicate_count = int(total_rows * duplicate_rate)
    threshold = THRESHOLDS["max_duplicate_rate"]
    passed = duplicate_rate <= threshold

    result = {
        "check": "duplicates",
        "passed": passed,
        "severity": "hard" if duplicate_rate > threshold * 5 else "soft",
        "duplicate_count": duplicate_count,
        "duplicate_rate": duplicate_rate,
        "threshold": threshold,
        "ts": datetime.now(UTC).isoformat(),
    }

    ti.xcom_push(key="duplicate_result", value=result)
    logger.info(json.dumps({
        "event": "dq_check_duplicates",
        "dag_id": DAG_ID,
        "run_id": context.get('run_id', 'unknown'),
        "task_id": "check_duplicates",
        "timestamp": datetime.now(UTC).isoformat(),
        "passed": passed,
        "duplicate_rate": duplicate_rate,
        "threshold": threshold,
        "duplicate_count": duplicate_count,
    }))
    return result


def check_referential_integrity(**context):
    """
    Verify that all foreign keys exist in their reference tables.
    Example: every customer_id in fact_transactions must exist in dim_customer.
    """
    ti = context["ti"]

    fk_violations = random.randint(0, 30)
    threshold = THRESHOLDS["max_referential_failures"]
    passed = fk_violations <= threshold

    result = {
        "check": "referential_integrity",
        "passed": passed,
        "severity": "hard" if fk_violations > threshold * 2 else "soft",
        "fk_violations": fk_violations,
        "threshold": threshold,
        "checks": {
            "customer_id → dim_customer": random.randint(0, 20),
            "product_id → dim_product": random.randint(0, 10),
        },
        "ts": datetime.now(UTC).isoformat(),
    }

    ti.xcom_push(key="referential_result", value=result)
    logger.info(json.dumps({
        "event": "dq_check_referential_integrity",
        "dag_id": DAG_ID,
        "run_id": context.get('run_id', 'unknown'),
        "task_id": "check_referential_integrity",
        "timestamp": datetime.now(UTC).isoformat(),
        "passed": passed,
        "fk_violations": fk_violations,
        "threshold": threshold,
    }))
    return result


def check_data_freshness(**context):
    """
    Ensure the most recent record timestamp is within the expected window.
    Stale data often indicates a silent upstream failure.
    """
    ti = context["ti"]

    # Simulate age of most recent record
    age_minutes = random.uniform(5, 120)
    threshold = THRESHOLDS["min_freshness_minutes"]
    passed = age_minutes <= threshold

    result = {
        "check": "data_freshness",
        "passed": passed,
        "severity": "soft",    # freshness failures are soft — data may still be valid
        "max_record_age_minutes": round(age_minutes, 1),
        "threshold_minutes": threshold,
        "ts": datetime.now(UTC).isoformat(),
    }

    ti.xcom_push(key="freshness_result", value=result)
    logger.info(json.dumps({
        "event": "dq_check_data_freshness",
        "dag_id": DAG_ID,
        "run_id": context.get('run_id', 'unknown'),
        "task_id": "check_data_freshness",
        "timestamp": datetime.now(UTC).isoformat(),
        "passed": passed,
        "max_record_age_minutes": round(age_minutes, 1),
        "threshold_minutes": threshold,
    }))
    return result


def aggregate_dq_results(**context):
    """
    Collect all individual check results, compute an overall DQ score,
    and classify the outcome as:
      - "all_pass"    → proceed normally
      - "soft_fail"   → alert and proceed with warnings
      - "hard_fail"   → quarantine data and halt downstream
    """
    ti = context["ti"]

    check_keys = [
        ("check_null_rates", "null_rate_result"),
        ("check_row_count", "row_count_result"),
        ("check_duplicates", "duplicate_result"),
        ("check_referential_integrity", "referential_result"),
        ("check_data_freshness", "freshness_result"),
    ]

    all_results = []
    hard_failures = []
    soft_failures = []

    for task_id, key in check_keys:
        result = ti.xcom_pull(task_ids=task_id, key=key)
        if result:
            all_results.append(result)
            if not result.get("passed", True):
                severity = result.get("severity", "soft")
                if severity == "hard":
                    hard_failures.append(result["check"])
                else:
                    soft_failures.append(result["check"])

    total_checks = len(all_results)
    passed_checks = sum(1 for r in all_results if r.get("passed", True))
    dq_score = round(passed_checks / total_checks * 100, 1) if total_checks else 0.0

    if hard_failures:
        overall_status = "hard_fail"
    elif soft_failures:
        overall_status = "soft_fail"
    else:
        overall_status = "all_pass"

    summary = {
        "overall_status": overall_status,
        "dq_score": dq_score,
        "total_checks": total_checks,
        "passed_checks": passed_checks,
        "hard_failures": hard_failures,
        "soft_failures": soft_failures,
        "all_results": all_results,
        "evaluated_at": datetime.now(UTC).isoformat(),
    }

    ti.xcom_push(key="dq_summary", value=summary)
    logger.info(json.dumps({
        "event": "dq_aggregate_complete",
        "dag_id": DAG_ID,
        "run_id": context.get('run_id', 'unknown'),
        "task_id": "aggregate_dq_results",
        "timestamp": datetime.now(UTC).isoformat(),
        "overall_status": overall_status,
        "dq_score": dq_score,
        "hard_failures": hard_failures,
        "soft_failures": soft_failures,
        "total_checks": total_checks,
        "passed_checks": passed_checks,
    }))
    return summary


def branch_on_dq_result(**context):
    """
    BranchPythonOperator callable.
    Reads the aggregated DQ status and returns the next task_id.
    """
    ti = context["ti"]
    summary = ti.xcom_pull(task_ids="aggregate_dq_results", key="dq_summary")
    status = summary.get("overall_status", "hard_fail") if summary else "hard_fail"

    route_map = {
        "all_pass": "publish_to_downstream",
        "soft_fail": "send_soft_fail_alert",
        "hard_fail": "quarantine_data",
    }
    next_task = route_map.get(status, "quarantine_data")
    logger.info(json.dumps({
        "event": "dq_branch_decision",
        "dag_id": DAG_ID,
        "run_id": context.get('run_id', 'unknown'),
        "task_id": "branch_on_dq_result",
        "timestamp": datetime.now(UTC).isoformat(),
        "dq_status": status,
        "next_task": next_task,
    }))
    return next_task


def publish_to_downstream(**context):
    """All checks passed — release data to BI tools and ML feature store."""
    ti = context["ti"]
    summary = ti.xcom_pull(task_ids="aggregate_dq_results", key="dq_summary")
    logger.info("DQ PASS (%.1f%%) — publishing data to downstream consumers", summary.get("dq_score", 0))
    return {"action": "published", "dq_score": summary.get("dq_score")}


def send_soft_fail_alert(**context):
    """Soft failures — send warning alert but allow downstream to continue."""
    ti = context["ti"]
    summary = ti.xcom_pull(task_ids="aggregate_dq_results", key="dq_summary")
    logger.warning(
        "DQ SOFT FAIL (score=%.1f%%) — failures: %s. Alerting team but continuing.",
        summary.get("dq_score", 0), summary.get("soft_failures", []),
    )
    # In production: post to Slack #data-quality channel, create JIRA ticket
    return {"action": "soft_alert_sent", "failures": summary.get("soft_failures")}


def quarantine_data(**context):
    """Hard failure — move data to quarantine table, block downstream, page on-call."""
    ti = context["ti"]
    summary = ti.xcom_pull(task_ids="aggregate_dq_results", key="dq_summary")
    logger.error(
        "DQ HARD FAIL — hard failures: %s. Data quarantined.",
        summary.get("hard_failures", []),
    )
    # In production: move table to quarantine schema, page PagerDuty, stop downstream DAGs
    raise ValueError(
        f"Hard DQ failures detected: {summary.get('hard_failures', [])}. "
        "Data quarantined. Manual review required."
    )


def finalize_dq_run(**context):
    """
    Runs after any branch (uses TriggerRule.NONE_FAILED_MIN_ONE_SUCCESS).
    Writes DQ run metadata to the data catalogue.
    """
    ti = context["ti"]
    summary = ti.xcom_pull(task_ids="aggregate_dq_results", key="dq_summary")
    logger.info("DQ run finalised. Summary: %s", summary)
    return {"finalised": True, "status": summary.get("overall_status") if summary else "unknown"}


# ---------------------------------------------------------------------------
# DAG definition
# ---------------------------------------------------------------------------
with DAG(
    dag_id=DAG_ID,
    description="Parallel DQ checks with severity-based branching",
    default_args=DEFAULT_ARGS,
    schedule_interval="@daily",
    start_date=days_ago(7),
    catchup=False,
    max_active_runs=1,
    tags=["data-quality", "dq", "poc-07"],
    doc_md=__doc__,
) as dag:

    # ── Gate: start of parallel checks ──────────────────────────────────────
    t_start = EmptyOperator(task_id="start_dq_checks")

    # ── Parallel DQ checks ───────────────────────────────────────────────────
    t_null = PythonOperator(task_id="check_null_rates", python_callable=check_null_rates)
    t_count = PythonOperator(task_id="check_row_count", python_callable=check_row_count)
    t_dups = PythonOperator(task_id="check_duplicates", python_callable=check_duplicates)
    t_ri = PythonOperator(task_id="check_referential_integrity", python_callable=check_referential_integrity)
    t_fresh = PythonOperator(task_id="check_data_freshness", python_callable=check_data_freshness)

    # ── Aggregate results ─────────────────────────────────────────────────────
    t_aggregate = PythonOperator(
        task_id="aggregate_dq_results",
        python_callable=aggregate_dq_results,
        trigger_rule=TriggerRule.ALL_DONE,  # run even if some checks failed
    )

    # ── Branch ────────────────────────────────────────────────────────────────
    t_branch = BranchPythonOperator(
        task_id="branch_on_dq_result",
        python_callable=branch_on_dq_result,
    )

    # ── Branch outcomes ───────────────────────────────────────────────────────
    t_publish = PythonOperator(task_id="publish_to_downstream", python_callable=publish_to_downstream)
    t_soft_alert = PythonOperator(task_id="send_soft_fail_alert", python_callable=send_soft_fail_alert)
    t_quarantine = PythonOperator(task_id="quarantine_data", python_callable=quarantine_data)

    # ── Finalize: join all branches ───────────────────────────────────────────
    t_finalize = PythonOperator(
        task_id="finalize_dq_run",
        python_callable=finalize_dq_run,
        trigger_rule=TriggerRule.ALL_DONE,
    )

    # ── Dependency graph ─────────────────────────────────────────────────────
    #
    #            start_dq_checks
    #           /  |  |  |  \
    #     null count dup ri fresh    (parallel)
    #           \  |  |  |  /
    #         aggregate_dq_results
    #                  │
    #         branch_on_dq_result
    #          /         |        \
    #    publish  soft_alert  quarantine
    #          \         |        /
    #           finalize_dq_run
    #
    if AIRFLOW_AVAILABLE:
        t_start >> [t_null, t_count, t_dups, t_ri, t_fresh]
        [t_null, t_count, t_dups, t_ri, t_fresh] >> t_aggregate
        t_aggregate >> t_branch
        t_branch >> [t_publish, t_soft_alert, t_quarantine]
        [t_publish, t_soft_alert, t_quarantine] >> t_finalize
    else:
        for _t in [t_null, t_count, t_dups, t_ri, t_fresh]:
            t_start >> _t
            _t >> t_aggregate
        t_aggregate >> t_branch
        for _t in [t_publish, t_soft_alert, t_quarantine]:
            t_branch >> _t
            _t >> t_finalize


__all__ = ["dag", "DAG_ID", "THRESHOLDS"]
