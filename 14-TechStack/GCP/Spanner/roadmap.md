# Spanner Roadmap – 6 Weeks

## Weeks 1-2: Foundations (🟢)
- [ ] Day 1: Create regional instance; basic table
- [ ] Day 2: Strong vs bounded-staleness reads
- [ ] Day 3: DDL basics; primary keys; interleaved tables
- [ ] Day 4: Inserts/queries; mutation limits
- [ ] Day 5: Indexes; covering queries
- [ ] Day 6: Query plans; latency basics
- [ ] Day 7: Mini-project: small schema + queries
- [ ] Day 8: Backup/export basics
- [ ] Day 9: IAM roles; audit logs
- [ ] Day 10: Review + refactor
- [ ] Day 11-12: Hotspot basics; key design
- [ ] Day 13-14: Client retries/backoff

**Milestone**: Basic app on regional Spanner with secure access.

## Weeks 3-4: Intermediate (🟡)
- [ ] Day 15: Multi-region configs; tradeoffs
- [ ] Day 16: Interleaving patterns; when to avoid
- [ ] Day 17: Secondary indexes; staleness reads for scale
- [ ] Day 18: Change streams intro; Dataflow sink
- [ ] Day 19: Performance tuning via EXPLAIN
- [ ] Day 20: Capacity sizing; scaling nodes
- [ ] Day 21: Schema change strategies; avoid locks
- [ ] Day 22-23: Mini-project: multi-table schema with indexes
- [ ] Day 24-25: Monitoring/alerts on latency/CPU
- [ ] Day 26-28: Cost controls; autoscaling (if available)

**Milestone**: Tuned schema with scale/cost awareness and monitoring.

## Weeks 5-6: Advanced (🔴)
- [ ] Day 29: DR/HA drills; failover behavior
- [ ] Day 30: Large schema changes; batching DDL
- [ ] Day 31: CDC via change streams to BQ/Storage
- [ ] Day 32: Governance: IAM least privilege, CMEK
- [ ] Day 33: Compliance: audit logs, access reviews
- [ ] Day 34: Performance: hotspot mitigation, request routing
- [ ] Day 35: Client patterns: idempotent mutations, staleness configs
- [ ] Day 36: Capacity forecasting; cost dashboards
- [ ] Day 37-38: Capstone: multi-region app with DR and CDC
- [ ] Day 39-42: Documentation, SOPs, runbooks

**Milestone**: Multi-region, monitored, governed Spanner with CDC/DR.

## Resources
- Docs: https://cloud.google.com/spanner/docs
- Best practices: https://cloud.google.com/spanner/docs/best-practices
- Change streams: https://cloud.google.com/spanner/docs/change-streams

