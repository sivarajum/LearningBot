# Bigtable Roadmap – 6 Weeks

## Weeks 1-2: Foundations (🟢)
- [ ] Day 1: Create instance; cbt CLI basics
- [ ] Day 2: Table/column family; set/get cells
- [ ] Day 3: Row key basics; hotspot awareness
- [ ] Day 4: Reads/scans; filters
- [ ] Day 5: GC rules; TTL
- [ ] Day 6: Dev vs prod instances; sizing intro
- [ ] Day 7: Mini-project: simple table with sensible keys
- [ ] Day 8: IAM basics; least privilege
- [ ] Day 9: Monitoring: latency/throughput
- [ ] Day 10: Review + refine key design
- [ ] Day 11-12: Backup/export basics
- [ ] Day 13-14: HBase API awareness

**Milestone**: Basic table with clean key design and monitoring.

## Weeks 3-4: Intermediate (🟡)
- [ ] Day 15: Advanced key design (salting/prefix, reverse timestamps)
- [ ] Day 16: Multi-cluster routing basics
- [ ] Day 17: Performance tuning; node sizing; compression
- [ ] Day 18: GC rule optimization; storage vs cost
- [ ] Day 19: Dataflow pipelines for export/import
- [ ] Day 20: Quotas/alerts; audit logs
- [ ] Day 21: Avoiding full scans; targeted access patterns
- [ ] Day 22-23: Mini-project: HA-ready design with exports
- [ ] Day 24-25: Security: VPC-SC, CMEK
- [ ] Day 26-28: Cost controls; labels; rightsizing

**Milestone**: Well-partitioned, monitored, cost-aware Bigtable.

## Weeks 5-6: Advanced (🔴)
- [ ] Day 29: Multi-cluster failover drills
- [ ] Day 30: CDC/analytics via export to BQ
- [ ] Day 31: Client patterns: retries/backoff/idempotency
- [ ] Day 32: Runbooks for hotspot remediation
- [ ] Day 33: Governance: key design review process
- [ ] Day 34: Performance/load testing at scale
- [ ] Day 35: DR strategy: backups, restore tests
- [ ] Day 36: Automation: Terraform modules; CI for schema/key checks
- [ ] Day 37-38: Capstone: HA, governed Bigtable with exports
- [ ] Day 39-42: Documentation, SOPs, dashboards

**Milestone**: HA Bigtable with DR, governance, and tested performance.

## Resources
- Docs: https://cloud.google.com/bigtable/docs
- Key design: https://cloud.google.com/bigtable/docs/schema-design
- HBase: https://cloud.google.com/bigtable/docs/hbase-client

