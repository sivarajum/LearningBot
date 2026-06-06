# Cloud SQL Roadmap – 6 Weeks

## Weeks 1-2: Foundations (🟢)
- [ ] Day 1: Create instance; connect via Auth Proxy
- [ ] Day 2: Users/passwords; roles/privileges
- [ ] Day 3: Public vs private IP; prefer private
- [ ] Day 4: Backups; PITR basics
- [ ] Day 5: Maintenance window; flags intro
- [ ] Day 6: Basic monitoring (CPU/mem/connections)
- [ ] Day 7: Mini-project: secure single instance
- [ ] Day 8: SSL enforcement; IAM DB auth basics
- [ ] Day 9: Storage auto-grow; alerts
- [ ] Day 10: Review + cleanup
- [ ] Day 11-12: Connection pooling intro
- [ ] Day 13-14: Read replicas overview

**Milestone**: Secure instance with backups and monitoring.

## Weeks 3-4: Intermediate (🟡)
- [ ] Day 15: Regional HA; failover test
- [ ] Day 16: Read replicas; promotion; lag monitoring
- [ ] Day 17: Connection pooling (pgbouncer/proxy)
- [ ] Day 18: Flags tuning (work_mem, max_connections, autovacuum)
- [ ] Day 19: IAM/SM for secrets; audit logs
- [ ] Day 20: VPC + private IP end-to-end
- [ ] Day 21: Alerts on storage/lag/failover
- [ ] Day 22-23: Mini-project: HA with replica + pooling
- [ ] Day 24-25: Performance profiling; indexes; query plans
- [ ] Day 26-28: Cost controls: rightsizing, off-hour schedules for non-prod

**Milestone**: HA, pooled connections, monitored and tuned.

## Weeks 5-6: Advanced (🔴)
- [ ] Day 29: Cross-region replicas; DR runbooks
- [ ] Day 30: Backup/restore drills; PITR validation
- [ ] Day 31: CMEK; org policies for public IP
- [ ] Day 32: DMS migration plan; minimal downtime strategy
- [ ] Day 33: Security hardening: TLS, IAM auth, least privilege
- [ ] Day 34: Performance: autovacuum tuning, vacuums, bloat control
- [ ] Day 35: Compliance: audit, access reviews, retention
- [ ] Day 36: SLOs/alerts for latency/errors
- [ ] Day 37-38: Capstone: prod-grade HA with DR + monitoring
- [ ] Day 39-42: Documentation, SOPs, cost/perf reports

**Milestone**: Production-grade HA Cloud SQL with DR and governance.

## Resources
- Docs: https://cloud.google.com/sql/docs
- Auth Proxy: https://cloud.google.com/sql/docs/mysql/sql-proxy
- Postgres tuning: https://cloud.google.com/sql/docs/postgres/flags

