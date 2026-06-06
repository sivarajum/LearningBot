# Cloud Functions Guide – Basic → Architect

## Level 1 – Launch & Basics

### 1. Quick Deploy (2nd gen)
```bash
gcloud config set project <PROJECT_ID>
gcloud services enable cloudfunctions.googleapis.com run.googleapis.com
gcloud functions deploy hello \
  --gen2 \
  --runtime=python311 \
  --region=us-central1 \
  --entry-point=hello_world \
  --source=. \
  --trigger-http \
  --allow-unauthenticated
```

### 2. Core Concepts
- Gen2 runs on Cloud Run + Eventarc; auto-scale to zero
- Triggers: HTTP, CloudEvents (Pub/Sub, Storage, etc.)
- Concurrency and instance settings

### 3. First Function
```python
def hello_world(request):
    return "Hello"
```

## Level 2 – Production Patterns

### Reliability & Performance
- Set max instances to protect downstreams; min instances for warm
- Idempotent handlers; retries/backoff on events
- Timeouts and memory tuned; structured logging

### Security
- Require auth for HTTP; IAM roles; signed calls if needed
- VPC connector for private egress; egress controls
- Secrets via Secret Manager or env; no plaintext

### CI/CD
- Build with Cloud Build; tests in CI; deploy via Cloud Deploy/GH Actions
- Version via revisions; rollback to previous revision

## Level 3 – Architect Playbook

### Eventing
- Use Eventarc filters; avoid fan-out storms
- Dead-letter topics for Pub/Sub triggers
- Ordering keys if ordering required (Pub/Sub)

### Observability & Ops
- Cloud Logging/Monitoring/Tracing; alerts on latency/errors/invocations
- Traces via OpenTelemetry where supported

### Cost & Governance
- Control concurrency and max instances; use min instances carefully
- Org policies for regions, allowed triggers; audit logs enabled

## Ops Cheat Sheet

| Task | Command | Note |
| --- | --- | --- |
| Deploy | `gcloud functions deploy ... --gen2` | deploy |
| List | `gcloud functions list --gen2` | inventory |
| Logs | `gcloud functions logs read <fn>` | view logs |
| Describe | `gcloud functions describe <fn> --gen2` | details |

## Architecture Patterns

```mermaid
flowchart LR
  Events[Events (HTTP/PubSub/Storage)] --> CF[Cloud Function]
  CF --> Downstream[APIs/DBs/Services]
  CF --> Logs[Logging/Monitoring]
  CF --> DLQ[DLQ (Pub/Sub)]
```

## Checklist Before Production
- [ ] Auth enforced (unless intentionally public); IAM least privilege
- [ ] Concurrency/max/min instances tuned; timeouts/memory set
- [ ] Idempotent handlers; retries/backoff; DLQ for events
- [ ] Secrets via Secret Manager; no plaintext
- [ ] Observability: logs/metrics/traces; alerts on errors/latency

