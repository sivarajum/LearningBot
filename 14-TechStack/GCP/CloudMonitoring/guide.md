# Cloud Monitoring Guide – Basic → Architect

## Level 1 – Launch & Basics

### 1. Core Concepts
- Metrics (GCP + custom), uptime checks, alerting policies
- Dashboards, SLOs/SLIs, notification channels

### 2. Basic Ops
```bash
gcloud monitoring channels list
gcloud monitoring policies list
```

### 3. Custom Metrics
- Export Prometheus/OpenTelemetry or use client libs
- Align labels; avoid high cardinality

## Level 2 – Production Patterns

### Dashboards & Alerts
- Create service dashboards; RED/USE metrics
- Multi-window, multi-burn-rate alerts for SLOs
- Notification channels with on-call routing; silence policies

### Integrations
- GKE + Cloud Ops suite; agentless for many GCP services
- Uptime checks for external endpoints; synthetic probes

### Cost & Noise
- Limit cardinality; refine alert thresholds; deduplicate routes

## Level 3 – Architect Playbook

### SLOs & Error Budgets
- Define SLIs (availability/latency); SLO targets; burn rates
- Error budget policies; alerting strategy

### Governance & Reliability
- Folder/project-level dashboards; ownership tags
- Runbooks linked in alerts; incident response drills
- Org-wide channel management; audit of policies

### Observability Stack
- Logs + metrics + traces correlation; OTel where possible
- Export metrics where needed (Prom/Grafana) or pull via API

## Ops Cheat Sheet

| Task | Location/Command | Note |
| --- | --- | --- |
| Channels | `gcloud monitoring channels list` | notif |
| Alerts | `gcloud monitoring policies list` | audit |
| Dashboards | Console/API | visualize |
| SLOs | Console/API | error budgets |

## Architecture Patterns

```mermaid
flowchart LR
  Services --> Metrics[Metrics (Cloud Monitoring)]
  Metrics --> Alerts[Alerts/SLOs]
  Metrics --> Dash[Dashboards]
  Metrics --> Channels[Notification Channels]
  Metrics --> LogsTraces[Logs/Traces Correlation]
```

## Checklist Before Production
- [ ] Service dashboards; RED/USE coverage
- [ ] Alerts with burn-rate SLOs; runbooks linked
- [ ] Notification channels owned; silences process defined
- [ ] Cardinality controlled; cost monitored
- [ ] Logs/metrics/traces correlated; uptime checks for externals

## Learning Path Links
- Tracks: `LearningTracks/Backend-GCP/track.md`, `LearningTracks/DevOps-Full/track.md`
- Projects: `Projects/GCP-Backend/starter/06-logging-monitoring.md`, `Projects/DevOps-Full/starter/06-monitoring-stack.md`
- Mastery: `Mastery/GCP-CloudMonitoring/` (quiz, scenarios, flashcards)

