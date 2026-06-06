# Apache Spark Guide – Basic → Architect

## Level 1 – Launch & Basics

### 1. Quick Setup
```bash
pip install pyspark
python -c "import pyspark; print(pyspark.__version__)"
```

### 2. First Job
```python
from pyspark.sql import SparkSession
spark = SparkSession.builder.appName("demo").getOrCreate()
df = spark.read.json("data.json")
df.groupBy("country").count().show()
```

### 3. Core Concepts
- RDD vs DataFrame vs Dataset; lazy evaluation; lineage
- Transformations vs actions; narrow vs wide deps
- Shuffle, partitions, catalyst optimizer, tungsten

## Level 2 – Production Patterns

### DataFrames & Performance
- Use DataFrames; avoid UDFs; prefer built-ins
- Partitioning: input and output; repartition vs coalesce
- File formats: Parquet/ORC; column pruning; predicate pushdown

### Resource Tuning
- Driver/executor memory/cores; dynamic allocation
- Shuffle service; broadcast joins; skew mitigation (salting)

### Streaming
- Structured Streaming; triggers; watermarking; exactly-once sinks
- Checkpointing; idempotent sinks; state store tuning

## Level 3 – Architect Playbook

### Reliability & Governance
- Job retries; speculative execution; SLA alerts
- Data quality checks (Deequ/great_expectations)
- Schema evolution management; ACID tables (Delta/Iceberg/Hudi)

### Deployment & Ops
- Submit via spark-submit, YARN/K8s/Standalone
- CI/CD: unit tests (pytest), integration tests on sample cluster
- Observability: Spark UI/history server; metrics to Prom/Grafana

### Cost & Scale
- Right-size executors; spot/preemptible where safe
- Optimize shuffle (AQE); cache only when reused

## Ops Cheat Sheet

| Task | Command | Note |
| --- | --- | --- |
| Submit | `spark-submit --master k8s://...` | run job |
| Repartition | `df.repartition(n)` | reshuffle |
| Cache | `df.cache()` | reuse cautiously |
| Explain | `df.explain("formatted")` | plan |
| Skew fix | `spark.sql.autoBroadcastJoinThreshold` | adjust |

## Architecture Patterns

```mermaid
flowchart LR
  Source[Batch/Streams] --> Ingest[Ingest]
  Ingest --> Spark[Structured Streaming/DataFrames]
  Spark --> Quality[Data Quality Checks]
  Spark --> Storage[Lakehouse (Parquet/Delta/Iceberg)]
  Storage --> Serve[Warehouse/ML]
  Spark --> Metrics[Metrics/Logs]
```

## Checklist Before Production
- [ ] DataFrames over RDD; avoid UDFs unless needed
- [ ] Partitioning tuned; shuffle minimized; AQE on
- [ ] Broadcast joins/skew mitigation applied
- [ ] Structured Streaming: checkpoints, watermark, idempotent sink
- [ ] Metrics/logs retained; history server accessible
- [ ] Tests in CI; schemas managed; data quality checks in place

## Learning Path Links
- Track: `LearningTracks/Data-Engineering/track.md`
- Projects: `Projects/Data-Engineering/starter/01-spark-batch.md` and `Projects/Integrated/data-engineering-capstone.md`
- Mastery: `Mastery/ApacheSpark/` (quiz, scenarios, flashcards)

