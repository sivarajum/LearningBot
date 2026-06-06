# Workflows Roadmap – 6 Weeks

## Weeks 1-2: Foundations (🟢)
- [ ] Day 1: Deploy basic workflow (HTTP call)
- [ ] Day 2: Inputs/outputs; expressions
- [ ] Day 3: Control flow; try/retry/except
- [ ] Day 4: Connectors for GCP services (BQ, GCS, Pub/Sub)
- [ ] Day 5: Service account and IAM basics
- [ ] Day 6: Logging/execution details
- [ ] Day 7: Mini-project: orchestrate two HTTP calls
- [ ] Day 8: Error handling basics; timeouts
- [ ] Day 9: Scheduling (via Cloud Scheduler/HTTP trigger)
- [ ] Day 10: Review + cleanup
- [ ] Day 11-12: Secure secrets with Secret Manager
- [ ] Day 13-14: Idempotency considerations

**Milestone**: Reliable small workflow with error handling and secure auth.

## Weeks 3-4: Intermediate (🟡)
- [ ] Day 15: Subworkflows; modular design
- [ ] Day 16: Event-driven via Eventarc trigger
- [ ] Day 17: Retries with backoff; circuit breaker patterns
- [ ] Day 18: DLQ via Pub/Sub on failure
- [ ] Day 19: Observability: structured logs, alerts
- [ ] Day 20: Orchestrating Cloud Run/Functions/Dataflow
- [ ] Day 21: Testing workflows (dev/prod separation)
- [ ] Day 22-23: Mini-project: orchestrate ETL job (BQ/Dataflow)
- [ ] Day 24-25: IAM hardening; least privilege per call
- [ ] Day 26-28: Cost review; avoid long-running steps

**Milestone**: Modular, event-driven workflow with DLQ and alerts.

## Weeks 5-6: Advanced (🔴)
- [ ] Day 29: GitOps deployment; versioning strategy
- [ ] Day 30: SLIs/SLOs for execution latency/failures
- [ ] Day 31: DR and rollback; safe deployment
- [ ] Day 32: VPC-SC considerations; CMEK for called services
- [ ] Day 33: Large payload patterns; pagination
- [ ] Day 34: Compliance: audit logs, access reviews
- [ ] Day 35: Incident runbooks; chaos testing
- [ ] Day 36: Integration with CI pipelines; lint/validate
- [ ] Day 37-38: Capstone: production orchestrator with DLQ + monitoring
- [ ] Day 39-42: Documentation, SOPs, governance

**Milestone**: Production-grade orchestrations with governance and SLOs.

## Resources
- Docs: https://cloud.google.com/workflows/docs
- Connectors: https://cloud.google.com/workflows/docs/reference/googleapis

