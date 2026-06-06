# Cloud Functions Roadmap – 6 Weeks

## Weeks 1-2: Foundations (🟢)
- [ ] Day 1: Enable APIs; deploy first HTTP function (gen2)
- [ ] Day 2: Triggers overview (HTTP, Pub/Sub, Storage)
- [ ] Day 3: Concurrency/instances/timeouts/memory
- [ ] Day 4: Logging basics; structured logs
- [ ] Day 5: Auth for HTTP; IAM roles; allow/deny public
- [ ] Day 6: Mini-project: simple API + secured endpoint
- [ ] Day 7: Review + cleanup
- [ ] Day 8: Eventarc basics; Pub/Sub trigger
- [ ] Day 9: Error handling/retries; idempotency
- [ ] Day 10: DLQ concept for Pub/Sub
- [ ] Day 11-12: VPC connector intro; private egress
- [ ] Day 13-14: Secrets via Secret Manager

**Milestone**: Secure, basic HTTP + event-driven functions.

## Weeks 3-4: Intermediate (🟡)
- [ ] Day 15: CI/CD with Cloud Build; tests in pipeline
- [ ] Day 16: Deploy via Cloud Deploy or GH Actions
- [ ] Day 17: Rollback via revisions; traffic controls
- [ ] Day 18: Observability: alerts on errors/latency/invocations
- [ ] Day 19: Event filtering with Eventarc; avoid fan-out
- [ ] Day 20: Ordering keys with Pub/Sub triggers
- [ ] Day 21: Resource tuning: max/min instances, concurrency
- [ ] Day 22-23: Mini-project: event-driven pipeline with DLQ
- [ ] Day 24-25: Security: IAM least privilege, signed calls
- [ ] Day 26-28: Cost: tune instances/concurrency, region choice

**Milestone**: Production-ready event/HTTP functions with CI/CD and observability.

## Weeks 5-6: Advanced (🔴)
- [ ] Day 29: VPC-SC and org policies for regions/triggers
- [ ] Day 30: DR/rollback runbooks; chaos tests
- [ ] Day 31: Performance: cold start mitigation (min instances)
- [ ] Day 32: Tracing with OTel; correlation IDs
- [ ] Day 33: Governance: audit logs, access reviews
- [ ] Day 34: Input validation/sanitization; SSRF/command injection guards
- [ ] Day 35: High-throughput patterns; backpressure
- [ ] Day 36: Multi-env promotion workflow
- [ ] Day 37-38: Capstone: full event-driven app with DLQ, alerts, VPC egress
- [ ] Day 39-42: Documentation, SOPs, cost/perf reports

**Milestone**: Secure, governed, observable event platform on Cloud Functions.

## Resources
- Docs: https://cloud.google.com/functions/docs
- Gen2: https://cloud.google.com/functions/docs/concepts/version-comparison
- Security: https://cloud.google.com/functions/docs/securing/authenticating

