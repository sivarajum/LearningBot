# Cloud Run Roadmap – 6 Weeks

## Weeks 1-2: Foundations (🟢)
- [ ] Day 1: Enable API; deploy hello service (public)
- [ ] Day 2: Revisions; traffic splitting basics
- [ ] Day 3: Concurrency; min/max instances; cold start basics
- [ ] Day 4: Request/response timeouts; CPU allocation on idle
- [ ] Day 5: Logs/metrics defaults; explore console
- [ ] Day 6: Custom domain + managed certs
- [ ] Day 7: Mini-project: simple API deploy from source
- [ ] Day 8: IAM for invoker; lock down to auth-only
- [ ] Day 9: VPC connector intro
- [ ] Day 10: Review + refactor configs
- [ ] Day 11-12: Cost basics; region choice; scaling behaviors
- [ ] Day 13-14: Health/readiness endpoints

**Milestone**: Secure basic service with tuned concurrency/timeouts.

## Weeks 3-4: Intermediate (🟡)
- [ ] Day 15: Build pipeline with Cloud Build/Artifacts
- [ ] Day 16: CI/CD via Cloud Deploy or GH Actions
- [ ] Day 17: Traffic splitting for canary; rollback to prior rev
- [ ] Day 18: Observability: alerts on latency/errors
- [ ] Day 19: VPC egress controls; private services
- [ ] Day 20: Cloud Armor for public endpoints
- [ ] Day 21: Secrets/env handling; service accounts per service
- [ ] Day 22-23: Mini-project: staging+prod with canary
- [ ] Day 24-25: Performance tuning: concurrency tests, OOM tuning
- [ ] Day 26-28: Cost controls: min instances, region, CPU idle

**Milestone**: CI/CD, canary, private egress, observability in place.

## Weeks 5-6: Advanced (🔴)
- [ ] Day 29: Multi-service architecture; shared libs
- [ ] Day 30: SLOs; alert policies; error budgets
- [ ] Day 31: DR and rollback runbooks; revision pinning
- [ ] Day 32: Org policies: allowed regions, domain restrictions
- [ ] Day 33: Security: JWT auth, rate limits, WAF with Armor
- [ ] Day 34: Latency optimization: keep-warm strategy, caching
- [ ] Day 35: Testing: load tests; chaos drills
- [ ] Day 36: Feature flags, config per env
- [ ] Day 37-38: Capstone: multi-env, canaried, observable service
- [ ] Day 39-42: Documentation, SOPs, perf/cost reports

**Milestone**: Production-grade Cloud Run platform with governance.

## Resources
- Docs: https://cloud.google.com/run/docs
- Deploy from source: https://cloud.google.com/run/docs/deploying-source-code
- Security: https://cloud.google.com/run/docs/securing

