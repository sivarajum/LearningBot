# Backend Engineer on GCP — 3-Week Track

## Overview
- Duration: 21 days
- Goal: Ship production-grade microservices on GCP with CI/CD, security, and observability.
- Stack: Cloud Build → Cloud Run → Cloud SQL/Spanner → IAM/VPC → Load Balancing → Logging/Monitoring.
- Prerequisites: Python/Node.js, REST basics, Git.

## Week 1 — Foundations & Deploy
- Day 1: Project/IAM setup; enable APIs; service accounts; least privilege.
- Day 2: Cloud Build basics; build triggers; artifact storage.
- Day 3: Cloud Run fundamentals; revisions; traffic split; rollbacks.
- Day 4: Cloud SQL vs Spanner: choose one; connect securely (IAM DB auth, private IP if applicable).
- Day 5: Secrets (Secret Manager); config via env/params; 12-factor alignment.
- Day 6: Health checks, readiness/liveness; concurrency and scaling knobs.
- Day 7: Mini-project: REST service → Cloud Run; CI/CD via Cloud Build; connects to Cloud SQL/Spanner.
- Milestone: Service deployed with CI/CD and database connectivity.

## Week 2 — Reliability, Security, Networking
- Day 8: VPC, Serverless VPC Access, egress control; ingress settings on Cloud Run.
- Day 9: IAM policies per service; Workload Identity Federation for CI; short-lived creds.
- Day 10: Load Balancing for Cloud Run; custom domains; TLS.
- Day 11: Caching/queueing patterns (optional: Redis/Memorystore, Pub/Sub for async).
- Day 12: Zero-downtime deploys; canary with traffic splitting; rollback playbook.
- Day 13: Cost/perf tuning: min/max instances, concurrency, CPU/RAM sizing; perf tests.
- Day 14: Mini-project: blue/green or canary deploy with LB + SSL + rollback drill.
- Milestone: Secure, networked, canary-able service with rollback.

## Week 3 — Observability, Compliance, Capstone
- Day 15: Cloud Logging structure; trace/span correlation; log-based metrics; error reporting.
- Day 16: Cloud Monitoring dashboards; SLOs and burn-rate alerts (latency, error rate).
- Day 17: Compliance: audit logs, org policies, CMEK (where relevant), access reviews.
- Day 18: DR/HA: multi-region strategy (DB choice implications), backups, restore drills.
- Day 19: Performance hardening: load tests; profiling; cold-start mitigation.
- Day 20: Documentation/runbooks: incident checklists, on-call playbook.
- Day 21: Capstone build + review.
- Milestone: Production-grade backend with SLOs, security, observability, rollback.

## Capstone (Week 3)
**E-commerce API**  
- Services on Cloud Run with CI/CD (Cloud Build).  
- Data layer: Cloud SQL (private IP + IAM DB auth) or Spanner (if multi-region).  
- Routing: External HTTP(S) LB with SSL, custom domain; optional CDN caching layer.  
- Observability: Structured logs with trace IDs; dashboards + burn-rate alerts.  
- Reliability: Canary deploy + rollback; DB backup/restore tested.  
- Security: Least-privilege IAM; secrets in Secret Manager; ingress locked down.  
- Acceptance: Meets latency/error SLO; rollback validated; cost within budget.

## Links to Core Docs
- Cloud Run: `GCP/Cloud-Run/guide.md`, `.../roadmap.md`
- Cloud Build: `GCP/CloudBuild/guide.md`, `.../roadmap.md`
- Cloud SQL: `GCP/CloudSQL/guide.md`, `.../roadmap.md`
- Spanner: `GCP/Spanner/guide.md`, `.../roadmap.md`
- IAM: `GCP/IAM/guide.md`
- VPC/Load Balancing: `GCP/VPC/guide.md`, `GCP/LoadBalancing/guide.md`
- Logging/Monitoring: `GCP/CloudLogging/guide.md`, `GCP/CloudMonitoring/guide.md`

