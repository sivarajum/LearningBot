# BigQuery Guide – Basic → Architect

## Level 1 – Launch & Basics

### 1. Quick Setup
```bash
gcloud config set project <PROJECT_ID>
bq query --use_legacy_sql=false 'SELECT "hello" as msg'
```

### 2. Core Concepts
- Datasets, tables, views, materialized views
- Storage vs compute separation; slots and reservations
- Standard SQL; partitions (time/ingestion), clustering

### 3. First Table & Query
```bash
bq load --source_format=CSV dataset.table gs://bucket/data.csv
bq query --use_legacy_sql=false 'SELECT COUNT(*) FROM dataset.table'
```

## Level 2 – Production Patterns

### Performance & Cost
- Prefer partitioned + clustered tables for pruning
- Use approximate functions where acceptable; LIMIT doesn’t save cost
- Avoid SELECT *; prune columns; filter early
- Slot reservations for predictable cost; flex slots for bursts

### Data Modeling & Storage
- Columnar parquet/ORC external tables when needed
- Materialized views for hot aggregations
- Time-travel and snapshots for recovery; table expiration policies

### Security & Governance
- IAM at project/dataset/table; authorized views; row-level/column security
- CMEK for sensitive data; audit logs enabled

## Level 3 – Architect Playbook

### Pipelines & Integrations
- Ingest via Dataflow/DBT/Composer; use load jobs over streaming when possible
- Use staging datasets; quality checks before publish

### Reliability & SLOs
- Monitor slots usage, shuffle size, query latency/error rates
- Quotas/limits monitoring; alert on failed scheduled queries

### Operations
- Versioned schemas; documented breaking changes
- DR: export to GCS; snapshot/restore patterns

## Ops Cheat Sheet

| Task | Command | Note |
| --- | --- | --- |
| Query | `bq query '...'` | standard SQL |
| Load | `bq load ...` | batch ingest |
| Export | `bq extract ...` | to GCS |
| Slots | `bq show --reservation` | capacity |
| Info | `bq show --schema --format=prettyjson` | table schema |

## Architecture Patterns

```mermaid
flowchart LR
  Sources --> Ingest[Ingest (Dataflow/DBT/Composer)]
  Ingest --> Stage[Staging Dataset]
  Stage --> Refined[Refined/Pub Dataset]
  Refined --> BQ[BigQuery Tables/Views/MVs]
  BQ --> Serve[Dashboards/ML/Exports]
  BQ --> Governance[IAM/Row-Col Security/Audit]
```

## Checklist Before Production
- [ ] Tables partitioned/clustered; no SELECT *
- [ ] Slot strategy defined (on-demand vs reservations)
- [ ] Authorized views/row/column security where needed
- [ ] Schemas versioned; time-travel/snapshots understood
- [ ] Monitoring on slots, latency, failures; audit logs on

## Learning Path Links
- Track: `LearningTracks/Data-Engineer-GCP/track.md`
- Projects: `Projects/GCP-DataEngineer/` and `Projects/Integrated/data-engineer-gcp-capstone.md`
- Mastery: `Mastery/GCP-BigQuery/` (quiz, scenarios, flashcards)

