"""
DAG 02: Dynamic DAG Generation from Configuration
==================================================
Demonstrates:
- Generating multiple DAGs at import time from pipeline_config.json
- Each pipeline entry in the config becomes its own DAG
- All DAGs share the same task structure (extract→transform→load)
  but vary in schedule, sources, SLA, and metadata
- Using globals() to register dynamically created DAGs with Airflow
- This is the canonical pattern used in large organisations where
  hundreds of similar pipelines exist

Key interview talking point:
  "We had 200+ similar ETL pipelines at [Company].  Instead of 200
  separate DAG files, we used a single dynamic DAG factory driven by
  a YAML/JSON config stored in Git.  Adding a new pipeline = one PR
  touching config, zero new Python."
"""

import os
import json
import logging
from datetime import UTC, datetime, timedelta
from pathlib import Path

logger = logging.getLogger(__name__)

# ---------------------------------------------------------------------------
# Airflow imports with graceful fallback
# ---------------------------------------------------------------------------
try:
    from airflow import DAG
    from airflow.operators.python import PythonOperator
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
        def __init__(self, *a, **kw): pass
        def __rshift__(self, other): return other

    def days_ago(n): return datetime.now(UTC) - timedelta(days=n)


# ---------------------------------------------------------------------------
# Load configuration
# ---------------------------------------------------------------------------
_CONFIG_PATH = Path(__file__).resolve().parent.parent / "config" / "pipeline_config.json"

def _load_config():
    try:
        with open(_CONFIG_PATH) as f:
            return json.load(f)
    except FileNotFoundError:
        logger.warning("pipeline_config.json not found at %s — using empty config", _CONFIG_PATH)
        return {"pipelines": [], "global_settings": {}}
    except json.JSONDecodeError as e:
        logger.error("Invalid JSON in pipeline_config.json: %s", e)
        return {"pipelines": [], "global_settings": {}}


CONFIG = _load_config()
GLOBAL = CONFIG.get("global_settings", {})


# ---------------------------------------------------------------------------
# Task callables — parameterised so each dynamic DAG can reuse them
# ---------------------------------------------------------------------------

def make_extract_task(pipeline_cfg):
    """Return an extract callable bound to this pipeline's config."""

    def extract(**context):
        ti = context["ti"]
        sources = pipeline_cfg["sources"]
        dag_id = f"etl_{pipeline_cfg['name']}"
        run_id = context.get('run_id', 'unknown')
        logger.info(json.dumps({
            "event": "extract_start",
            "dag_id": dag_id,
            "run_id": run_id,
            "task_id": "extract",
            "timestamp": datetime.now(UTC).isoformat(),
            "pipeline": pipeline_cfg["name"],
            "source_count": len(sources),
        }))

        # Simulate parallel source extraction
        source_results = []
        total_rows = 0
        for source in sources:
            rows = 1000 + hash(source.get("connection_id", "")) % 9000
            source_results.append({
                "connection_id": source.get("connection_id"),
                "type": source["type"],
                "rows_extracted": rows,
            })
            total_rows += rows

        ti.xcom_push(key="source_results", value=source_results)
        ti.xcom_push(key="total_extracted_rows", value=total_rows)
        logger.info(json.dumps({
            "event": "extract_complete",
            "dag_id": dag_id,
            "run_id": run_id,
            "task_id": "extract",
            "timestamp": datetime.now(UTC).isoformat(),
            "pipeline": pipeline_cfg["name"],
            "total_rows": total_rows,
        }))
        return {"total_rows": total_rows, "sources": source_results}

    extract.__name__ = f"extract_{pipeline_cfg['name']}"
    extract.__doc__ = f"Extract data for pipeline: {pipeline_cfg['name']}"
    return extract


def make_validate_task(pipeline_cfg):
    """Return a validation callable for this pipeline."""

    def validate(**context):
        ti = context["ti"]
        dag_id = f"etl_{pipeline_cfg['name']}"
        run_id = context.get('run_id', 'unknown')
        total_rows = ti.xcom_pull(task_ids="extract", key="total_extracted_rows")

        # Generic DQ checks
        checks = {
            "min_row_count": total_rows >= 10,
            "not_empty": total_rows > 0,
        }
        all_passed = all(checks.values())
        status = "pass" if all_passed else "fail"

        ti.xcom_push(key="validation_status", value=status)
        ti.xcom_push(key="validation_checks", value=checks)
        logger.info(json.dumps({
            "event": "validate_complete",
            "dag_id": dag_id,
            "run_id": run_id,
            "task_id": "validate",
            "timestamp": datetime.now(UTC).isoformat(),
            "pipeline": pipeline_cfg["name"],
            "validation_status": status,
            "row_count": total_rows,
        }))
        return {"status": status, "checks": checks}

    validate.__name__ = f"validate_{pipeline_cfg['name']}"
    return validate


def make_transform_task(pipeline_cfg):
    """Return a transform callable for this pipeline."""

    def transform(**context):
        ti = context["ti"]
        dag_id = f"etl_{pipeline_cfg['name']}"
        run_id = context.get('run_id', 'unknown')
        total_rows = ti.xcom_pull(task_ids="extract", key="total_extracted_rows")

        output_rows = int(total_rows * 0.97)    # 3 % attrition from dedup/filter
        summary = {
            "pipeline": pipeline_cfg["name"],
            "input_rows": total_rows,
            "output_rows": output_rows,
            "destination": pipeline_cfg.get("destination", {}),
            "transform_ts": datetime.now(UTC).isoformat(),
        }
        ti.xcom_push(key="transform_summary", value=summary)
        logger.info(json.dumps({
            "event": "transform_complete",
            "dag_id": dag_id,
            "run_id": run_id,
            "task_id": "transform",
            "timestamp": datetime.now(UTC).isoformat(),
            "pipeline": pipeline_cfg["name"],
            "input_rows": total_rows,
            "output_rows": output_rows,
        }))
        return summary

    transform.__name__ = f"transform_{pipeline_cfg['name']}"
    return transform


def make_load_task(pipeline_cfg):
    """Return a load callable for this pipeline."""

    def load(**context):
        ti = context["ti"]
        summary = ti.xcom_pull(task_ids="transform", key="transform_summary")
        dest = pipeline_cfg.get("destination", {})
        rows = summary.get("output_rows", 0) if summary else 0

        dag_id = f"etl_{pipeline_cfg['name']}"
        run_id = context.get('run_id', 'unknown')

        load_result = {
            "pipeline": pipeline_cfg["name"],
            "rows_loaded": rows,
            "destination_type": dest.get("type"),
            "destination_table": dest.get("table"),
            "load_ts": datetime.now(UTC).isoformat(),
        }
        ti.xcom_push(key="load_result", value=load_result)
        logger.info(json.dumps({
            "event": "load_complete",
            "dag_id": dag_id,
            "run_id": run_id,
            "task_id": "load",
            "timestamp": datetime.now(UTC).isoformat(),
            "pipeline": pipeline_cfg["name"],
            "rows_loaded": rows,
            "destination_table": dest.get("table"),
        }))
        return load_result

    load.__name__ = f"load_{pipeline_cfg['name']}"
    return load


# ---------------------------------------------------------------------------
# DAG factory
# ---------------------------------------------------------------------------

def create_pipeline_dag(pipeline_cfg: dict, global_cfg: dict) -> DAG:
    """
    Build and return a complete DAG for one pipeline config entry.

    Parameters
    ----------
    pipeline_cfg:
        A single entry from config["pipelines"]
    global_cfg:
        Shared defaults from config["global_settings"]

    Returns
    -------
    airflow.DAG  (or stub DAG in simulator mode)
    """
    dag_id = f"etl_{pipeline_cfg['name']}"

    default_args = {
        "owner": pipeline_cfg.get("owner", "data-engineering"),
        "depends_on_past": False,
        "email": [global_cfg.get("alert_email", "data-alerts@company.com")],
        "email_on_failure": global_cfg.get("email_on_failure", True),
        "email_on_retry": global_cfg.get("email_on_retry", False),
        "retries": pipeline_cfg.get("retries", 2),
        "retry_delay": timedelta(minutes=pipeline_cfg.get("retry_delay_minutes", 5)),
    }

    sla_hours = pipeline_cfg.get("sla_hours", 4)

    pipeline_dag = DAG(
        dag_id=dag_id,
        description=pipeline_cfg.get("description", f"ETL pipeline for {pipeline_cfg['name']}"),
        default_args=default_args,
        schedule_interval=pipeline_cfg.get("schedule", "@daily"),
        start_date=days_ago(1),
        catchup=global_cfg.get("catchup", False),
        max_active_runs=global_cfg.get("max_active_runs", 1),
        tags=pipeline_cfg.get("tags", []) + ["dynamic", "poc-07"],
        doc_md=f"""
## Dynamic DAG: {dag_id}

Auto-generated from `pipeline_config.json`.

**Pipeline**: {pipeline_cfg["name"]}
**Schedule**: {pipeline_cfg.get("schedule", "@daily")}
**SLA**: {sla_hours} hours
**Sources**: {len(pipeline_cfg.get("sources", []))} source(s)
**Destination**: {pipeline_cfg.get("destination", {}).get("table", "unknown")}
        """,
    )

    # Build tasks inside the DAG context
    with pipeline_dag:
        t_extract = PythonOperator(
            task_id="extract",
            python_callable=make_extract_task(pipeline_cfg),
            sla=timedelta(hours=sla_hours // 2),
        )

        t_validate = PythonOperator(
            task_id="validate",
            python_callable=make_validate_task(pipeline_cfg),
        )

        t_transform = PythonOperator(
            task_id="transform",
            python_callable=make_transform_task(pipeline_cfg),
            sla=timedelta(hours=sla_hours),
        )

        t_load = PythonOperator(
            task_id="load",
            python_callable=make_load_task(pipeline_cfg),
        )

        # Linear dependency: extract → validate → transform → load
        t_extract >> t_validate >> t_transform >> t_load

    return pipeline_dag


# ---------------------------------------------------------------------------
# Generate all DAGs at module import time
# This is the pattern Airflow's scheduler looks for: any DAG object in the
# module's global namespace gets picked up automatically.
# ---------------------------------------------------------------------------

_generated_dags = {}

for _pipeline in CONFIG.get("pipelines", []):
    try:
        _dag_id = f"etl_{_pipeline['name']}"
        _dag = create_pipeline_dag(_pipeline, GLOBAL)
        globals()[_dag_id] = _dag          # Airflow discovers DAGs via globals()
        _generated_dags[_dag_id] = _dag
        logger.debug("Registered dynamic DAG: %s", _dag_id)
    except Exception as exc:
        logger.error("Failed to create DAG for pipeline '%s': %s", _pipeline.get("name"), exc)


# ---------------------------------------------------------------------------
# Public interface used by the simulator
# ---------------------------------------------------------------------------

def get_generated_dag_ids() -> list:
    """Return the list of dag_ids generated by this factory."""
    return list(_generated_dags.keys())


def get_generated_dags() -> dict:
    """Return dict of {dag_id: dag_object} generated by this factory."""
    return dict(_generated_dags)


__all__ = ["create_pipeline_dag", "get_generated_dag_ids", "get_generated_dags", "CONFIG"]
