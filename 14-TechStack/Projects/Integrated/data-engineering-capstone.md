# Capstone: Hybrid Batch + Streaming Analytics
- Sources: Kafka streaming + batch files.
- Processing: Spark streaming with checkpoints; Spark batch for backfill; idempotent sinks.
- Orchestration: Airflow DAGs manage batch/backfill; monitor streaming health.
- Transform: dbt incremental models + tests/snapshots; freshness checks.
- Observability: SLIs/SLOs; alerts on lag/freshness; DLQ/replay playbook.
- Governance: access controls, secrets, retention, PII handling.
