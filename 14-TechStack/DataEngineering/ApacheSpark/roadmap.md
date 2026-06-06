# Apache Spark Roadmap – 6 Weeks

## Weeks 1-2: Foundations (🟢)
- [ ] Day 1: Install pyspark; spark-shell basics
- [ ] Day 2: RDD vs DataFrame; lazy evaluation
- [ ] Day 3: Transformations vs actions; lineage
- [ ] Day 4: Joins; narrow vs wide deps; shuffle intro
- [ ] Day 5: File formats (Parquet/ORC); schema inference
- [ ] Day 6: DataFrame API basics; aggregations
- [ ] Day 7: Spark UI basics; stages/tasks
- [ ] Day 8: Mini-project: simple ETL with DataFrames
- [ ] Day 9: Caching rules; when not to cache
- [ ] Day 10: Partitions: inspect and adjust
- [ ] Day 11-12: Basic tests with pytest on sample data
- [ ] Day 13-14: Review + refactor

**Milestone**: Confident with DataFrame API and execution basics.

## Weeks 3-4: Intermediate (🟡)
- [ ] Day 15: Joins optimization; broadcast threshold
- [ ] Day 16: Skew handling (salting, skew hints)
- [ ] Day 17: AQE; coalesce vs repartition
- [ ] Day 18: Predicate pushdown; column pruning
- [ ] Day 19: Structured Streaming basics; triggers; sinks
- [ ] Day 20: Checkpointing; watermarking; exactly-once design
- [ ] Day 21: Resource tuning: driver/executor mem/cores
- [ ] Day 22: File layout: partitionBy, bucketBy
- [ ] Day 23-24: Mini-project: streaming pipeline with watermark
- [ ] Day 25-27: Data quality checks (Deequ/GE); schema evolution
- [ ] Day 28: Observability: history server, metrics

**Milestone**: Optimized batch + basic streaming with quality checks.

## Weeks 5-6: Advanced (🔴)
- [ ] Day 29: Lakehouse tables (Delta/Iceberg/Hudi) basics
- [ ] Day 30: Z-order/compaction/vacuum patterns
- [ ] Day 31: Advanced streaming: stateful ops, late data
- [ ] Day 32: Cost optimization: right-size executors, spot/preemptible
- [ ] Day 33: Governance: ACLs, row/column security (if supported)
- [ ] Day 34: CI/CD for Spark jobs; packaging; spark-submit params
- [ ] Day 35: K8s/YARN deploy patterns; autoscaling
- [ ] Day 36: DR and retry strategy; speculative execution
- [ ] Day 37-38: Capstone: end-to-end batch+stream with quality + lakehouse
- [ ] Day 39-42: Documentation, runbooks, handover

**Milestone**: Production-grade batch/stream pipelines with governance and cost control.

## Resources
- Docs: https://spark.apache.org/docs/latest/
- Tuning: https://spark.apache.org/docs/latest/sql-performance-tuning.html
- Structured Streaming: https://spark.apache.org/docs/latest/structured-streaming-programming-guide.html

