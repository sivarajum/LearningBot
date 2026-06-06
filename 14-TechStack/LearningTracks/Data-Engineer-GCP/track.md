# Data Engineer on GCP — 3-Week Track

## Overview
- Duration: 21 days
- Goal: Build and operate batch + streaming analytics on GCP with governance.
- Stack: Cloud Storage → BigQuery → Dataflow → Pub/Sub → Airflow/Composer → dbt (SQL) → Logging/Monitoring/IAM.
- Prerequisites: Python basics, SQL fundamentals, Git, GCP project access.

## Week 1 — Storage, Query, Foundations
- Day 1: GCP setup, IAM basics, enable APIs, CLI (gcloud/bq/gsutil).
- Day 2: Cloud Storage buckets (region/retention/CMEK), lifecycle, uniform access.
- Day 3: BigQuery basics: datasets, tables, partitions/clusters; avoid SELECT *.
- Day 4: Loading data (CSV/Parquet/ORC), schema/auto-detect, external tables.
- Day 5: Query plans, bytes processed, cost controls; scheduled queries.
- Day 6: Data modeling intro (staging vs curated), time travel/snapshots.
- Day 7: Mini-project: land data in GCS, load to BQ (partitioned), scheduled summary.
- Milestone: Reliable ingest + partitioned/clustered BQ tables with cost awareness.

## Week 2 — Processing & Orchestration
- Day 8: Pub/Sub fundamentals; attributes; ordering; DLQ basics.
- Day 9: Dataflow batch pipeline: GCS → BQ, windowing basics.
- Day 10: Dataflow streaming pipeline: Pub/Sub → BQ; at-least-once handling.
- Day 11: dbt with BigQuery: models, tests, snapshots, docs.
- Day 12: Airflow/Composer: DAG authoring, dependencies, retries, backoff.
- Day 13: Orchestrate Dataflow + dbt in Airflow; templating; secrets.
- Day 14: Mini-project: streaming ingest to BQ + dbt transforms on schedule.
- Milestone: Orchestrated batch + streaming with dbt tests.

## Week 3 — Streaming, Quality, Governance, Observability
- Day 15: Data quality: dbt tests, Great Expectations (optional), anomaly checks.
- Day 16: Monitoring: log-based metrics, Cloud Monitoring dashboards, alerts on lag/errors.
- Day 17: Reliability: idempotency, replay/seek in Pub/Sub, DLQ handling, backfill playbook.
- Day 18: Security/Governance: IAM least privilege, row/column security in BQ, CMEK, VPC-SC considerations.
- Day 19: Cost/performance tuning: slots vs on-demand, partition pruning, storage classes.
- Day 20: Documentation + runbooks: incident playbooks, SLOs (latency, freshness), error budgets.
- Day 21: Capstone build + review.
- Milestone: Production-ready pipeline with SLOs, monitoring, governance.

## Capstone (Week 3)
**E-commerce analytics pipeline**  
- Batch: GCS landing → Dataflow (batch) → BQ curated → dbt transforms/tests.  
- Streaming: Pub/Sub orders → Dataflow streaming → BQ realtime table.  
- Orchestration: Airflow DAG triggering batch + dbt; handle retries/backoff.  
- Observability: Dashboards for lag/error rate; alerts on failures; runbook for replays.  
- Governance: IAM scoped roles, partition/cluster strategy, CMEK where applicable, retention/lifecycle.  
- Acceptance: Meets SLOs (freshness/latency), cost guardrails, replay tested.

## Links to Core Docs
- Storage: `GCP/Cloud-Storage/guide.md`, `GCP/Cloud-Storage/roadmap.md`
- BigQuery: `GCP/BigQuery/guide.md`, `GCP/BigQuery/roadmap.md`
- Dataflow: `GCP/Dataflow/guide.md`, `GCP/Dataflow/roadmap.md`
- Pub/Sub: `GCP/PubSub/guide.md`, `GCP/PubSub/roadmap.md`
- Airflow: `DataEngineering/ApacheAirflow/guide.md`, `.../roadmap.md`
- dbt: `dbt/guide.md`, `dbt/roadmap.md`
- Monitoring: `GCP/CloudMonitoring/guide.md`, `.../roadmap.md`

