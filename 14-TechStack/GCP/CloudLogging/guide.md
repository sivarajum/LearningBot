# Cloud Logging Guide – Basic → Architect

## Level 1 – Launch & Basics

### 1. Core Concepts
- Logs ingestion from GCP services and applications
- Log buckets (region, retention), views, sinks
- Resource types and labels; severity levels; structured JSON preferred

### 2. Basic Ops
```bash
gcloud logging read "resource.type=gce_instance" --limit=5
gcloud logging sinks create exportsink storage.googleapis.com/my-bucket --log-filter="severity>=ERROR"
```

### 3. Structured Logging
- Emit JSON with consistent keys (trace, span, severity, message)
- Correlate with traces via trace_id/span_id

## Level 2 – Production Patterns

### Retention & Export
- Custom buckets per env/team; set retention
- Sinks to BigQuery/Storage/PubSub for analytics/alerts
- Views to scope access; least privilege IAM on buckets

### Noise & Cost Control
- Filter noisy logs; drop debug in prod; sampling where appropriate
- Aggregated sinks to central projects; org-level sinks for compliance

### Security & Compliance
- VPC-SC for sensitive projects; CMEK for buckets
- Audit logs retention; access transparency (if enabled)

## Level 3 – Architect Playbook

### Observability & SLOs
- Dashboards for error/severity rates; alerting via Monitoring
- Correlate logs with metrics/traces; parse fields for metrics

### Governance
- Standard log schema; ownership labels
- Access control via views; separation by env/team

### Operations
- Log-based metrics for alerts (latency/error counts)
- Export pipelines (Pub/Sub -> SIEM/ELK)

## Ops Cheat Sheet

| Task | Command | Note |
| --- | --- | --- |
| Read | `gcloud logging read 'filter'` | query |
| Write (app) | structured JSON | correlation |
| Sink | `gcloud logging sinks create ...` | export |
| Buckets | `gcloud logging buckets list` | retention |

## Architecture Patterns

```mermaid
flowchart LR
  Services --> Logging[Cloud Logging Buckets]
  Logging --> Sinks[BigQuery/Storage/PubSub Sinks]
  Logging --> Metrics[Log-based Metrics]
  Logging --> Views[Views (Access Control)]
  Logging --> SIEM[SIEM/ELK via PubSub]
```

## Checklist Before Production
- [ ] Structured JSON logs with trace/span IDs
- [ ] Buckets per env/team; retention set; CMEK/VPC-SC if needed
- [ ] Sinks to BQ/GCS/PubSub; views for access control
- [ ] Log-based metrics + alerts for errors/latency
- [ ] Noise and cost controls in place; audit logs retained

## Learning Path Links
- Track: `LearningTracks/Backend-GCP/track.md`
- Projects: `Projects/GCP-Backend/starter/06-logging-monitoring.md` and `Projects/Integrated/backend-gcp-capstone.md`
- Mastery: `Mastery/GCP-CloudLogging/` (quiz, scenarios, flashcards)

