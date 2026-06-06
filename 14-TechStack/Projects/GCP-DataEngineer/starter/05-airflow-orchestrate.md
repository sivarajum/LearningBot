# Starter: Airflow DAG for Ingest + Transform
- Goal: DAG triggers load (Dataflow template) then BQ transform.
- Steps: author DAG with retries/backoff; use secrets; schedule daily.
- Validation: DAG success; idempotent rerun; logs captured.
