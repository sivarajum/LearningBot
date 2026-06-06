"""
Airflow DAG-level callbacks for observability.

Provides:
- on_sla_miss: Structured WARNING log on SLA breach; shows webhook pattern.
"""

import json
import logging
from datetime import UTC, datetime

logger = logging.getLogger(__name__)


def on_sla_miss(dag, task_list, blocking_task_list, slas, blocking_tis):
    """SLA miss callback — logs structured event, shows webhook pattern.

    Airflow calls this function when any task in the DAG misses its SLA.
    Wire it in via ``sla_miss_callback=on_sla_miss`` on the DAG definition.

    Parameters
    ----------
    dag : DAG
        The DAG that owns the missed SLA.
    task_list : list
        Tasks whose SLAs were missed.
    blocking_task_list : list
        Tasks that are blocking the SLA-missed tasks.
    slas : list
        SlaMiss ORM objects with detail about each miss.
    blocking_tis : list
        TaskInstance objects currently blocking progress.
    """
    try:
        event = {
            "event": "sla_miss",
            "dag_id": dag.dag_id,
            "missed_tasks": [t.task_id for t in task_list],
            "blocking_tasks": [t.task_id for t in blocking_task_list],
            "timestamp": datetime.now(UTC).isoformat(),
            "severity": "WARNING",
        }
        logger.warning(json.dumps(event))
    except Exception as exc:  # noqa: BLE001
        logger.error(json.dumps({"event": "sla_miss_callback_error", "error": str(exc)}))

    # Production webhook pattern (uncomment and configure):
    # import requests
    # WEBHOOK_URL = os.getenv("SLACK_WEBHOOK_URL") or os.getenv("PAGERDUTY_WEBHOOK_URL")
    # if WEBHOOK_URL:
    #     requests.post(WEBHOOK_URL, json={
    #         "text": f"SLA miss: {dag.dag_id} — tasks: {event['missed_tasks']}"
    #     })
