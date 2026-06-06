# Capstone: E-commerce Analytics on GCP
- Batch: GCS landing -> Dataflow batch -> BQ curated -> dbt incremental + tests.
- Streaming: Pub/Sub orders -> Dataflow streaming -> BQ realtime table.
- Orchestration: Airflow DAG (backfill, retries, sla);
- Observability: lag/error dashboards; alerts; replay playbook.
- Governance: IAM least privilege; partition/cluster; retention; CMEK optional.
- Acceptance: Meets freshness/latency SLO; replay tested; cost report included.
