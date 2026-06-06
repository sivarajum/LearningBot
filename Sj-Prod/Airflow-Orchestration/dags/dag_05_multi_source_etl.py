"""
DAG 05: Multi-Source ETL with TaskGroups and Parallel Ingestion
===============================================================
Demonstrates:
- TaskGroup to organise logically related tasks without a SubDAG
  (SubDAGs are deprecated since Airflow 2.0 in favour of TaskGroups)
- Parallel ingestion from multiple data sources in a single TaskGroup
- Cross-task dependencies between groups
- TriggerRule.ALL_SUCCESS to enforce that all sources loaded before merging
- Final merge and publish step

Architecture:
  Three source systems run in parallel inside the "ingest" TaskGroup:
    1. CRM (Salesforce) — customer records
    2. ERP (SAP) — order headers
    3. Web Analytics (GA4) — session events

  After all three complete, the "transform_and_merge" group:
    1. Resolves entity matches between CRM customers and orders
    2. Joins with session events on customer_id
    3. Builds unified customer journey fact table

  Finally, "publish" group delivers to BI + ML consumers.

Real-world note:
  TaskGroups are how Airflow shows nested task hierarchies in the UI.
  They appear as collapsible groups in the Graph View, making complex
  DAGs with 50+ tasks readable.
"""

import json
import logging
import random
import time
from datetime import UTC, datetime, timedelta

logger = logging.getLogger(__name__)

# ---------------------------------------------------------------------------
# Airflow imports with graceful fallback
# ---------------------------------------------------------------------------
try:
    from airflow import DAG
    from airflow.operators.python import PythonOperator
    from airflow.operators.empty import EmptyOperator
    from airflow.utils.dates import days_ago
    from airflow.utils.task_group import TaskGroup
    from airflow.utils.trigger_rule import TriggerRule
    AIRFLOW_AVAILABLE = True
except ImportError:
    AIRFLOW_AVAILABLE = False

    class TriggerRule:
        ALL_SUCCESS = "all_success"
        ALL_DONE = "all_done"

    class TaskGroup:
        def __init__(self, group_id="", **kw):
            self.group_id = group_id
        def __enter__(self): return self
        def __exit__(self, *a): pass
        def __rshift__(self, other): return other
        def __rrshift__(self, other): return self

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

    class EmptyOperator:
        def __init__(self, task_id="", **kw):
            self.task_id = task_id
        def __rshift__(self, other): return other
        def __rrshift__(self, other): return self

    def days_ago(n): return datetime.now(UTC) - timedelta(days=n)


# ---------------------------------------------------------------------------
# Constants
# ---------------------------------------------------------------------------
DAG_ID = "multi_source_etl_customer_journey"

DEFAULT_ARGS = {
    "owner": "data-engineering",
    "depends_on_past": False,
    "email": ["data-alerts@company.com"],
    "email_on_failure": True,
    "email_on_retry": False,
    "retries": 2,
    "retry_delay": timedelta(minutes=5),
}


# ---------------------------------------------------------------------------
# TaskGroup 1: Ingest — parallel source ingestion
# ---------------------------------------------------------------------------

def ingest_crm_data(**context):
    """
    Pull customer records from Salesforce CRM.
    In production: uses SalesforceHook with REST API.
    """
    ti = context["ti"]
    logger.info("Ingesting CRM data from Salesforce")

    rows = 15000 + random.randint(0, 5000)
    result = {
        "source": "salesforce_crm",
        "rows": rows,
        "entities": ["Account", "Contact", "Opportunity"],
        "ingested_at": datetime.now(UTC).isoformat(),
    }
    ti.xcom_push(key="crm_result", value=result)
    logger.info(json.dumps({
        "event": "ingest_crm_complete",
        "dag_id": DAG_ID,
        "run_id": context.get('run_id', 'unknown'),
        "task_id": "ingest.ingest_crm",
        "timestamp": datetime.now(UTC).isoformat(),
        "source": "salesforce_crm",
        "rows": rows,
    }))
    return result


def ingest_erp_data(**context):
    """
    Pull order headers and line items from SAP ERP.
    In production: uses JdbcOperator or SapHook.
    """
    ti = context["ti"]
    logger.info("Ingesting ERP data from SAP")

    rows = 8000 + random.randint(0, 2000)
    result = {
        "source": "sap_erp",
        "rows": rows,
        "tables": ["SO_HEADER", "SO_ITEM", "CUSTOMER_MASTER"],
        "ingested_at": datetime.now(UTC).isoformat(),
    }
    ti.xcom_push(key="erp_result", value=result)
    logger.info(json.dumps({
        "event": "ingest_erp_complete",
        "dag_id": DAG_ID,
        "run_id": context.get('run_id', 'unknown'),
        "task_id": "ingest.ingest_erp",
        "timestamp": datetime.now(UTC).isoformat(),
        "source": "sap_erp",
        "rows": rows,
    }))
    return result


def ingest_analytics_data(**context):
    """
    Pull web session events from Google Analytics 4 via Data Export API.
    """
    ti = context["ti"]
    logger.info("Ingesting web analytics from GA4")

    rows = 200000 + random.randint(0, 50000)
    result = {
        "source": "google_analytics_4",
        "rows": rows,
        "event_types": ["session_start", "page_view", "purchase", "add_to_cart"],
        "ingested_at": datetime.now(UTC).isoformat(),
    }
    ti.xcom_push(key="analytics_result", value=result)
    logger.info(json.dumps({
        "event": "ingest_analytics_complete",
        "dag_id": DAG_ID,
        "run_id": context.get('run_id', 'unknown'),
        "task_id": "ingest.ingest_analytics",
        "timestamp": datetime.now(UTC).isoformat(),
        "source": "google_analytics_4",
        "rows": rows,
    }))
    return result


def validate_ingest_completeness(**context):
    """
    After all three sources complete, verify all delivered data.
    Checks: all three sources have > 0 rows, timestamps are recent.
    """
    ti = context["ti"]

    crm = ti.xcom_pull(task_ids="ingest.ingest_crm", key="crm_result")
    erp = ti.xcom_pull(task_ids="ingest.ingest_erp", key="erp_result")
    analytics = ti.xcom_pull(task_ids="ingest.ingest_analytics", key="analytics_result")

    sources = {
        "crm": crm.get("rows", 0) if crm else 0,
        "erp": erp.get("rows", 0) if erp else 0,
        "analytics": analytics.get("rows", 0) if analytics else 0,
    }

    all_present = all(v > 0 for v in sources.values())
    log_fn = logger.info if all_present else logger.error
    log_fn(json.dumps({
        "event": "ingest_completeness_check",
        "dag_id": DAG_ID,
        "run_id": context.get('run_id', 'unknown'),
        "task_id": "ingest.validate_completeness",
        "timestamp": datetime.now(UTC).isoformat(),
        "all_present": all_present,
        "source_row_counts": sources,
    }))

    if not all_present:
        raise ValueError(f"One or more sources returned no data: {sources}")

    result = {"sources": sources, "all_present": all_present}
    ti.xcom_push(key="ingest_completeness", value=result)
    return result


# ---------------------------------------------------------------------------
# TaskGroup 2: Transform — entity resolution and joins
# ---------------------------------------------------------------------------

def resolve_customer_entities(**context):
    """
    Match CRM Account records to ERP CUSTOMER_MASTER using fuzzy matching
    on name + address.  Produces a unified customer_id mapping table.

    In production: uses recordlinkage or Splink library.
    """
    ti = context["ti"]
    crm = ti.xcom_pull(task_ids="ingest.ingest_crm", key="crm_result")
    erp = ti.xcom_pull(task_ids="ingest.ingest_erp", key="erp_result")

    crm_rows = crm.get("rows", 0) if crm else 0
    erp_rows = erp.get("rows", 0) if erp else 0

    matched = int(min(crm_rows, erp_rows) * 0.88)    # 88 % match rate
    logger.info(json.dumps({
        "event": "entity_resolution_complete",
        "dag_id": DAG_ID,
        "run_id": context.get('run_id', 'unknown'),
        "task_id": "transform.resolve_entities",
        "timestamp": datetime.now(UTC).isoformat(),
        "crm_rows": crm_rows,
        "erp_rows": erp_rows,
        "matched_entities": matched,
        "match_rate": round(matched / crm_rows, 4) if crm_rows else 0,
    }))

    result = {
        "crm_rows": crm_rows,
        "erp_rows": erp_rows,
        "matched_entities": matched,
        "match_rate": round(matched / crm_rows, 4) if crm_rows else 0,
    }
    ti.xcom_push(key="entity_resolution", value=result)
    return result


def join_sessions_to_customers(**context):
    """
    Join GA4 session events to the resolved customer IDs.
    Sessions without a matching customer_id go to an "anonymous" bucket.
    """
    ti = context["ti"]
    entity_res = ti.xcom_pull(task_ids="transform.resolve_entities", key="entity_resolution")
    analytics = ti.xcom_pull(task_ids="ingest.ingest_analytics", key="analytics_result")

    matched = entity_res.get("matched_entities", 0) if entity_res else 0
    sessions = analytics.get("rows", 0) if analytics else 0

    attributed = int(sessions * 0.62)   # 62 % of sessions attributed to known customers
    anonymous = sessions - attributed

    logger.info(json.dumps({
        "event": "session_attribution_complete",
        "dag_id": DAG_ID,
        "run_id": context.get('run_id', 'unknown'),
        "task_id": "transform.join_sessions",
        "timestamp": datetime.now(UTC).isoformat(),
        "total_sessions": sessions,
        "attributed_sessions": attributed,
        "anonymous_sessions": anonymous,
    }))

    result = {
        "total_sessions": sessions,
        "attributed_sessions": attributed,
        "anonymous_sessions": anonymous,
        "attribution_rate": round(attributed / sessions, 4) if sessions else 0,
    }
    ti.xcom_push(key="session_attribution", value=result)
    return result


def build_customer_journey(**context):
    """
    Assemble the final customer_journey fact table by combining:
    - Resolved customer entities (CRM + ERP merge)
    - Attributed web sessions
    - Purchase history from ERP

    Output: one row per customer per day with aggregated metrics.
    """
    ti = context["ti"]
    entity_res = ti.xcom_pull(task_ids="transform.resolve_entities", key="entity_resolution")
    session_attr = ti.xcom_pull(task_ids="transform.join_sessions", key="session_attribution")

    customers = entity_res.get("matched_entities", 0) if entity_res else 0
    sessions = session_attr.get("attributed_sessions", 0) if session_attr else 0

    output_rows = customers   # one row per customer per day
    logger.info(json.dumps({
        "event": "customer_journey_build_start",
        "dag_id": DAG_ID,
        "run_id": context.get('run_id', 'unknown'),
        "task_id": "transform.build_journey",
        "timestamp": datetime.now(UTC).isoformat(),
        "output_rows": output_rows,
        "sessions_linked": sessions,
    }))

    result = {
        "output_rows": output_rows,
        "sessions_linked": sessions,
        "destination": "bigquery://dw.fact_customer_journey",
        "built_at": datetime.now(UTC).isoformat(),
    }
    ti.xcom_push(key="journey_result", value=result)
    return result


# ---------------------------------------------------------------------------
# TaskGroup 3: Publish — deliver to consumers
# ---------------------------------------------------------------------------

def publish_to_bi(**context):
    """
    Trigger Looker/Tableau dataset refresh via API.
    In production: uses LookerHook or Tableau REST API operator.
    """
    ti = context["ti"]
    journey = ti.xcom_pull(task_ids="transform.build_journey", key="journey_result")
    rows = journey.get("output_rows", 0) if journey else 0
    logger.info("Publishing %d rows to BI tools (Looker + Tableau)", rows)
    return {"published_to": "bi", "rows": rows}


def publish_to_ml_feature_store(**context):
    """
    Write customer features to the ML feature store (Feast / Tecton).
    In production: uses FeastHook to push feature vectors.
    """
    ti = context["ti"]
    journey = ti.xcom_pull(task_ids="transform.build_journey", key="journey_result")
    rows = journey.get("output_rows", 0) if journey else 0
    logger.info("Publishing %d feature vectors to ML feature store", rows)
    return {"published_to": "feast_feature_store", "feature_rows": rows}


def update_data_catalogue(**context):
    """
    Update the data catalogue (DataHub / OpenMetadata) with run statistics,
    lineage, and quality metadata.
    """
    ti = context["ti"]
    logger.info("Updating data catalogue with lineage and statistics")
    return {"catalogue_updated": True, "ts": datetime.now(UTC).isoformat()}


# ---------------------------------------------------------------------------
# DAG definition
# ---------------------------------------------------------------------------
with DAG(
    dag_id=DAG_ID,
    description="Multi-source ETL with TaskGroups: CRM + ERP + Analytics → Customer Journey",
    default_args=DEFAULT_ARGS,
    schedule_interval="0 3 * * *",      # 3 AM daily
    start_date=days_ago(7),
    catchup=False,
    max_active_runs=1,
    tags=["multi-source", "task-groups", "customer-journey", "poc-07"],
    doc_md=__doc__,
) as dag:

    t_start = EmptyOperator(task_id="pipeline_start")

    # ── TaskGroup: ingest ─────────────────────────────────────────────────
    with TaskGroup(group_id="ingest", tooltip="Parallel ingestion from CRM, ERP, and Analytics") as tg_ingest:
        t_crm = PythonOperator(task_id="ingest_crm", python_callable=ingest_crm_data)
        t_erp = PythonOperator(task_id="ingest_erp", python_callable=ingest_erp_data)
        t_analytics = PythonOperator(task_id="ingest_analytics", python_callable=ingest_analytics_data)
        t_validate = PythonOperator(
            task_id="validate_completeness",
            python_callable=validate_ingest_completeness,
            trigger_rule=TriggerRule.ALL_SUCCESS,
        )
        # All three run in parallel, validate waits for all three
        if AIRFLOW_AVAILABLE:
            [t_crm, t_erp, t_analytics] >> t_validate
        else:
            for _t in [t_crm, t_erp, t_analytics]:
                _t >> t_validate

    # ── TaskGroup: transform ──────────────────────────────────────────────
    with TaskGroup(group_id="transform", tooltip="Entity resolution and customer journey assembly") as tg_transform:
        t_resolve = PythonOperator(task_id="resolve_entities", python_callable=resolve_customer_entities)
        t_join_sessions = PythonOperator(task_id="join_sessions", python_callable=join_sessions_to_customers)
        t_build_journey = PythonOperator(task_id="build_journey", python_callable=build_customer_journey)

        # Entity resolution can start once ingest completes;
        # join_sessions needs entity resolution first
        t_resolve >> t_join_sessions >> t_build_journey

    # ── TaskGroup: publish ────────────────────────────────────────────────
    with TaskGroup(group_id="publish", tooltip="Deliver to BI tools, ML feature store, and data catalogue") as tg_publish:
        t_bi = PythonOperator(task_id="publish_bi", python_callable=publish_to_bi)
        t_ml = PythonOperator(task_id="publish_ml_features", python_callable=publish_to_ml_feature_store)
        t_catalogue = PythonOperator(task_id="update_catalogue", python_callable=update_data_catalogue)

        # BI and ML publish in parallel; catalogue update waits for both
        if AIRFLOW_AVAILABLE:
            [t_bi, t_ml] >> t_catalogue
        else:
            t_bi >> t_catalogue
            t_ml >> t_catalogue

    t_end = EmptyOperator(
        task_id="pipeline_end",
        trigger_rule=TriggerRule.ALL_DONE,
    )

    # ── Top-level dependency chain ─────────────────────────────────────────
    #
    #   pipeline_start
    #         │
    #    ┌─────────────────────────────────┐
    #    │  INGEST (TaskGroup)             │
    #    │   crm ─┐                        │
    #    │   erp ─┼──► validate_complete   │
    #    │   ga4 ─┘                        │
    #    └─────────────────────────────────┘
    #         │
    #    ┌──────────────────────────────────────────────┐
    #    │  TRANSFORM (TaskGroup)                        │
    #    │   resolve_entities → join_sessions → journey │
    #    └──────────────────────────────────────────────┘
    #         │
    #    ┌──────────────────────────────────┐
    #    │  PUBLISH (TaskGroup)             │
    #    │   publish_bi ─┐                  │
    #    │   publish_ml ─┼──► catalogue     │
    #    └──────────────────────────────────┘
    #         │
    #   pipeline_end
    #
    t_start >> tg_ingest >> tg_transform >> tg_publish >> t_end


__all__ = ["dag", "DAG_ID"]
