# Data Engineering Stack — 4-Week Track

## Overview
- Duration: 28 days
- Goal: Build batch + streaming pipelines with orchestration, quality, and governance.
- Stack: Spark → Kafka → Airflow → dbt → Data Quality (tests) → Observability → Storage/DB targets.
- Prerequisites: Python, SQL, basic Linux, Git.

## Week 1 — Processing Foundations (Spark)
- Day 1: Spark basics; DataFrames; schemas; partitions; lazy eval.
- Day 2: IO formats (Parquet/ORC/Delta); partitioning strategies.
- Day 3: Performance: predicate pushdown, caching, shuffle awareness.
- Day 4: Structured Streaming intro; watermarking; exactly-once patterns with idempotency.
- Day 5: Spark on k8s or managed (Dataproc) basics; cost/perf levers.
- Day 6: Mini-project: batch job ingest + transform to Parquet.
- Day 7: Mini-project: simple streaming job with checkpointing.
- Milestone: Batch + basic streaming with correct partitioning and checkpoints.

## Week 2 — Messaging & Orchestration (Kafka + Airflow)
- Day 8: Kafka fundamentals: topics, partitions, offsets, consumer groups.
- Day 9: Producers: batching, compression, keys; schema registry basics.
- Day 10: Consumers: offset mgmt, idempotency, retries/DLQ pattern.
- Day 11: Airflow basics: DAGs, operators, retries, SLAs.
- Day 12: Airflow + Spark submit; backfill strategy; templating; secrets.
- Day 13: Mini-project: Kafka ingest → Spark streaming → sink to warehouse.
- Day 14: Mini-project: Airflow DAG orchestrating batch + quality checks.
- Milestone: Orchestrated Kafka+Spark pipelines with backfill and retries.

## Week 3 — Transformation & Quality (dbt + Tests)
- Day 15: dbt basics: models, tests, snapshots, docs.
- Day 16: Environments: dev/prod targets; CI for dbt tests.
- Day 17: Data quality: custom tests; anomaly checks; freshness.
- Day 18: Lineage and docs; exposures; ownership tags.
- Day 19: Mini-project: dbt models on warehouse (BQ/Redshift/Snowflake), tests + snapshots.
- Day 20: Cost/perf: incremental models; clustering/partitioning; caching.
- Milestone: Tested, incremental dbt models with lineage and CI.

## Week 4 — Observability, Governance, Capstone
- Day 21: Monitoring: pipeline SLIs (freshness, latency, failure rate); alerts.
- Day 22: Reliability: replay/backfill playbooks; DLQ handling; idempotent sinks.
- Day 23: Security/governance: access controls, secrets mgmt, PII handling, retention.
- Day 24: DR: backups/exports; restore drills; infra as code alignment.
- Day 25: Cost controls: right-size clusters, optimize storage, schedule jobs.
- Day 26-27: Capstone build.
- Day 28: Capstone review + documentation/runbooks.
- Milestone: Production-ready data platform patterns with runbooks and SLOs.

## Capstone (Week 4)
**Hybrid batch + streaming analytics**  
- Sources: Kafka (streaming) + batch files.  
- Processing: Spark batch + Spark streaming with checkpoints and idempotent sinks.  
- Orchestration: Airflow DAG triggers batch + validates streaming health.  
- Transform: dbt incremental models with tests/snapshots, freshness checks.  
- Observability: SLIs/SLOs, alerts, dashboards; DLQ/replay playbooks.  
- Governance: Access controls, secrets, retention, PII handling.  
- Acceptance: Meets freshness/latency SLOs; replay tested; costs documented.

## Links to Core Docs
- Spark: `DataEngineering/ApacheSpark/guide.md`, `.../roadmap.md`
- Kafka: `DataEngineering/Kafka/guide.md`, `.../roadmap.md`
- Airflow: `DataEngineering/ApacheAirflow/guide.md`, `.../roadmap.md`
- dbt: `dbt/guide.md`, `.../roadmap.md`
- Observability: `DevOps/Monitoring/guide.md`

