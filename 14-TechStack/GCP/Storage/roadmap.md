# Cloud Storage (Legacy Variant) Roadmap – 6 Weeks

> Note: Prefer `GCP/Cloud-Storage`. This roadmap mirrors the main storage plan for completeness.

## Weeks 1-2: Foundations (🟢)
- [ ] Day 1: Create bucket; upload/list objects
- [ ] Day 2: Uniform access vs ACL; IAM roles
- [ ] Day 3: Storage classes; pick per workload
- [ ] Day 4: Versioning; object generations
- [ ] Day 5: Lifecycle rules basics
- [ ] Day 6: Signed URLs intro
- [ ] Day 7: Mini-project: static assets bucket
- [ ] Day 8: Permissions review; least privilege
- [ ] Day 9: Logging/monitoring basics
- [ ] Day 10: Review + tidy policies
- [ ] Day 11-12: Performance basics; parallel uploads
- [ ] Day 13-14: Retention policies; holds

**Milestone**: Secure bucket with lifecycle and monitoring.

## Weeks 3-4: Intermediate (🟡)
- [ ] Day 15: VPC-SC basics; egress controls
- [ ] Day 16: CMEK configuration (if needed)
- [ ] Day 17: Event notifications (Pub/Sub/Eventarc)
- [ ] Day 18: Integration with BQ/Dataflow
- [ ] Day 19: Tiering rules (Nearline/Coldline/Archive)
- [ ] Day 20: Inventory/audit of objects/ACLs
- [ ] Day 21: Performance: composite/parallel uploads
- [ ] Day 22-23: Mini-project: landing + processed buckets
- [ ] Day 24-25: Cost review: egress, ops, class mix
- [ ] Day 26-28: Reliability: dual-region, backup/restore patterns

**Milestone**: Production-ready storage with governance.

## Weeks 5-6: Advanced (🔴)
- [ ] Day 29: CDN fronting; caching
- [ ] Day 30: Static site hosting pattern with HTTPS
- [ ] Day 31: Org policies: uniform access, CMEK, TLS
- [ ] Day 32: Data residency/compliance checks
- [ ] Day 33: Hot object mitigation for high-traffic items
- [ ] Day 34: DR runbooks; version restore; snapshot exports
- [ ] Day 35: Observability: alerts on 4xx/5xx/egress anomalies
- [ ] Day 36: Cost guardrails: lifecycle reviews, retention pruning
- [ ] Day 37-38: Capstone: compliant, monitored, cost-controlled storage tiering
- [ ] Day 39-42: Documentation, SOPs, access review cadence

**Milestone**: Secure, compliant, cost-optimized storage tiering.

## Resources
- Docs: https://cloud.google.com/storage/docs
- Security: https://cloud.google.com/storage/docs/access-control
- Lifecycle: https://cloud.google.com/storage/docs/lifecycle

