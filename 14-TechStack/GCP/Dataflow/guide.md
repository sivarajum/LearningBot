# Dataflow Guide – Basic → Architect

## Level 1 – Launch & Basics

### 1. Quick Setup
```bash
pip install apache-beam[gcp]
python -m apache_beam.examples.wordcount \ 
  --runner=DataflowRunner \
  --project=$PROJECT_ID \
  --temp_location=gs://$BUCKET/tmp \
  --region=us-central1
```

### 2. Core Concepts
- Apache Beam model: PCollection, PTransforms, runners
- Batch vs streaming; windowing; triggers; watermarks
- Workers, autoscaling, temp location, staging files

### 3. First Pipeline (Python)
```python
import apache_beam as beam
with beam.Pipeline(options=beam.options.pipeline_options.PipelineOptions()) as p:
    (p
     | "Read" >> beam.io.ReadFromText("gs://bucket/input.txt")
     | "Words" >> beam.FlatMap(lambda l: l.split())
     | "Count" >> beam.combiners.Count.PerElement()
     | "Write" >> beam.io.WriteToText("gs://bucket/output"))
```

## Level 2 – Production Patterns

### Pipelines
- Use schemas; avoid giant DoFns; prefer composites
- Windowing/triggering for streaming; watermark monitoring
- State and timers when needed; beware large state

### I/O and Performance
- Use GCS/BQ/Spanner/BT connectors; exactly-once sinks where possible
- Right-size workers; autoscaling; Dataflow Shuffle (for batch)
- Hot keys mitigation; combiner usage; side inputs carefully

### Reliability
- Dead-letter queues for poison messages
- Idempotent writes; retries with backoff
- FlexRS/Shuffle for cost reduction (batch)

## Level 3 – Architect Playbook

### Observability
- Dataflow logs/metrics; Error Reporting; Cloud Monitoring dashboards
- Backlog and watermark alerts for streaming

### Governance & Security
- Service account least privilege; VPC-SC if required
- CMEK for temp/data if needed; worker disk sizing; IP ranges

### Operations
- Templates (classic/flex) for reuse
- Versioned pipelines; CI/CD; perf tests
- Drains vs cancels; snapshot/restore for streaming

## Ops Cheat Sheet

| Task | Command | Note |
| --- | --- | --- |
| Run pipeline | `python -m ... --runner=DataflowRunner ...` | submit |
| List jobs | `gcloud dataflow jobs list` | status |
| Drain | `gcloud dataflow jobs drain JOB_ID` | graceful stop |
| Update | Flex templates updates | rolling |
| Templates | `gcloud dataflow flex-template build/run` | reusable |

## Architecture Patterns

```mermaid
flowchart LR
  Source[Source (Pub/Sub/GCS/DB)] --> Beam[Beam Pipeline]
  Beam --> Window[Windows/Triggers]
  Beam --> DLQ[Dead Letter]
  Beam --> Sink[Sinks (BQ/GCS/BT/Spanner)]
  Beam --> Metrics[Monitoring/Alerts]
```

## Checklist Before Production
- [ ] Pipelines windowed/triggered correctly; hot keys addressed
- [ ] DLQ strategy; idempotent writes; retries/backoff
- [ ] Worker sizing, autoscaling, Shuffle/FlexRS decisions
- [ ] IAM least privilege; VPC-SC/CMEK if required
- [ ] Monitoring on backlog/watermarks/errors; runbooks for drains

## Learning Path Links
- Track: `LearningTracks/Data-Engineer-GCP/track.md`
- Projects: `Projects/GCP-DataEngineer/starter/03-dataflow-batch.md` and `Projects/Integrated/data-engineer-gcp-capstone.md`
- Mastery: `Mastery/GCP-Dataflow/` (quiz, scenarios, flashcards)

