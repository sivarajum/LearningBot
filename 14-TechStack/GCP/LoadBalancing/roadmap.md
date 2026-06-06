# Load Balancing Roadmap – 6 Weeks

## Weeks 1-2: Foundations (🟢)
- [ ] Day 1: LB types (HTTP(S), TCP/UDP, Internal/External)
- [ ] Day 2: Create simple global HTTP(S) LB with MIG backend
- [ ] Day 3: Health checks; backend services; URL maps
- [ ] Day 4: Managed certs; HTTPS redirect
- [ ] Day 5: NEGs intro (GKE/Run/Functions)
- [ ] Day 6: Logs/metrics basics
- [ ] Day 7: Mini-project: simple global LB
- [ ] Day 8: Regional vs global scoping; when to use each
- [ ] Day 9: Firewall rules for health checks
- [ ] Day 10: Review + tidy config
- [ ] Day 11-12: Basic Cloud Armor rule
- [ ] Day 13-14: Path/host routing rules

**Milestone**: Secure HTTPS LB with health checks and routing.

## Weeks 3-4: Intermediate (🟡)
- [ ] Day 15: NEGs for serverless; GKE/Run backends
- [ ] Day 16: Internal HTTP(S)/TCP/UDP LBs
- [ ] Day 17: CDN enablement; caching rules
- [ ] Day 18: Session affinity; connection draining
- [ ] Day 19: Failover/multi-region backends
- [ ] Day 20: Armor WAF policies; rate limits
- [ ] Day 21: Monitoring/alerts on latency/4xx/5xx
- [ ] Day 22-23: Mini-project: multi-backend LB with Armor
- [ ] Day 24-25: Performance tuning: timeouts, capacity
- [ ] Day 26-28: Cost: regional vs global, CDN savings

**Milestone**: Multi-backend LB with WAF, observability, and tuning.

## Weeks 5-6: Advanced (🔴)
- [ ] Day 29: Canary/blue-green via weighted backends
- [ ] Day 30: SLOs and synthetic probes
- [ ] Day 31: Private Service Connect patterns
- [ ] Day 32: Governance: IaC for LB; cert IAM; external IP policies
- [ ] Day 33: DR: failover tests; rollback plans
- [ ] Day 34: Security: bot management, geo blocks if needed
- [ ] Day 35: Large-scale patterns; cache keys; TLS policies
- [ ] Day 36: Incident runbooks; dashboards
- [ ] Day 37-38: Capstone: global LB with WAF, canary, CDN, observability
- [ ] Day 39-42: Documentation, SOPs, postmortems

**Milestone**: Production-grade LB with WAF, canary, CDN, and governance.

## Resources
- Docs: https://cloud.google.com/load-balancing/docs
- NEGs: https://cloud.google.com/load-balancing/docs/negs
- Armor: https://cloud.google.com/armor/docs

