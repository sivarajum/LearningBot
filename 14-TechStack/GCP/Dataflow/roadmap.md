# Dataflow Roadmap – 6 Weeks

## Weeks 1-2: Foundations (🟢)
- [ ] Day 1: Beam model; PCollection/PTransform
- [ ] Day 2: Batch pipeline (wordcount); GCS I/O
- [ ] Day 3: Runners; Dataflow Runner specifics
- [ ] Day 4: Windowing basics; fixed windows
- [ ] Day 5: Triggers; lateness
- [ ] Day 6: Streaming vs batch differences
- [ ] Day 7: Mini-project: batch pipeline to BQ
- [ ] Day 8: Options: staging/temp, region, workers
- [ ] Day 9: Logging/monitoring basics
- [ ] Day 10: Review + cleanup
- [ ] Day 11-12: Side inputs; combiners
- [ ] Day 13-14: Intro to templates (classic)

**Milestone**: Run batch pipeline with basic windows/triggers understanding.

## Weeks 3-4: Intermediate (🟡)
- [ ] Day 15: Streaming pipeline; Pub/Sub source; watermark/backlog
- [ ] Day 16: State and timers basics
- [ ] Day 17: Hot key mitigation; key sharding; combiner usage
- [ ] Day 18: Dataflow Shuffle vs default; FlexRS for batch
- [ ] Day 19: Exactly-once sinks; idempotent writes
- [ ] Day 20: DLQ pattern for poison messages
- [ ] Day 21: Autoscaling; worker sizing; disk considerations
- [ ] Day 22-23: Mini-project: streaming pipeline with DLQ
- [ ] Day 24-25: Monitoring/alerts on watermarks/backlog/errors
- [ ] Day 26-28: Templates (flex); parameterized deploys

**Milestone**: Production-ready streaming pipeline with DLQ and monitoring.

## Weeks 5-6: Advanced (🔴)
- [ ] Day 29: Drains vs cancels; snapshot/restore
- [ ] Day 30: Governance: IAM least privilege, VPC-SC, CMEK
- [ ] Day 31: Performance: fused pipelines; avoiding large state
- [ ] Day 32: Cost: FlexRS, Shuffle choices, worker types
- [ ] Day 33: Testing: unit/integration/load tests
- [ ] Day 34: CI/CD for pipelines; versioning
- [ ] Day 35: CDC/ETL patterns to BQ/Spanner/BT
- [ ] Day 36: Incident runbooks; backfill strategies
- [ ] Day 37-38: Capstone: end-to-end streaming/batch with DR plan
- [ ] Day 39-42: Documentation, SOPs, dashboards

**Milestone**: Observable, governed Dataflow with DR, cost and performance controls.

## Resources
- Beam: https://beam.apache.org/documentation/
- Dataflow: https://cloud.google.com/dataflow/docs
- Flex templates: https://cloud.google.com/dataflow/docs/guides/templates/using-flex-templates

