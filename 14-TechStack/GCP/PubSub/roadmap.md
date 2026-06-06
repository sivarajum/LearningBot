# Pub/Sub Roadmap – 6 Weeks

## Weeks 1-2: Foundations (🟢)
- [ ] Day 1: Create topic/sub; publish/pull basics
- [ ] Day 2: Push vs pull; ack deadlines
- [ ] Day 3: Ordering keys basics; when to use
- [ ] Day 4: Message attributes; filtering
- [ ] Day 5: Retention settings; seek to time/snapshot
- [ ] Day 6: Mini-project: simple producer/consumer
- [ ] Day 7: Review; error handling basics
- [ ] Day 8: IAM basics; roles for topics/subs
- [ ] Day 9: Client lib setup; retries/backoff
- [ ] Day 10: Review + refactor
- [ ] Day 11-12: DLQ basics
- [ ] Day 13-14: Backlog monitoring intro

**Milestone**: Reliable basic pub/sub with retry and DLQ awareness.

## Weeks 3-4: Intermediate (🟡)
- [ ] Day 15: Streaming pull; flow control; concurrency tuning
- [ ] Day 16: Ack deadline extensions; visibility
- [ ] Day 17: DLQ implementation; poison pill handling
- [ ] Day 18: Idempotent consumer patterns; dedupe keys
- [ ] Day 19: Filtering subscriptions; reduce consumer load
- [ ] Day 20: Ordering: single consumer per key
- [ ] Day 21: Monitoring: backlog, oldest message age
- [ ] Day 22-23: Mini-project: high-throughput consumer with DLQ
- [ ] Day 24-25: Security: private endpoints, JWT validation for push
- [ ] Day 26-28: Cost/throughput tuning; batch sizing

**Milestone**: High-throughput, ordered (where needed), DLQ-enabled pipeline.

## Weeks 5-6: Advanced (🔴)
- [ ] Day 29: Schema registry; message validation
- [ ] Day 30: Eventarc/Cloud Run/Functions integration
- [ ] Day 31: SLOs for end-to-end latency; alerting
- [ ] Day 32: Compliance: audit logs, access reviews
- [ ] Day 33: DR: retention/seek strategy; backup/restore patterns
- [ ] Day 34: Performance tests; soak tests
- [ ] Day 35: Governance: org policies restricting public topics
- [ ] Day 36: Multi-tenant considerations; quotas
- [ ] Day 37-38: Capstone: event platform with DLQ, schemas, monitoring
- [ ] Day 39-42: Documentation, runbooks, ops reviews

**Milestone**: Governed, observable Pub/Sub with schema validation and SLOs.

## Resources
- Docs: https://cloud.google.com/pubsub/docs
- Schemas: https://cloud.google.com/pubsub/docs/schemas

