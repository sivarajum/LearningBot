# Cloud Build Roadmap – 6 Weeks

## Weeks 1-2: Foundations (🟢)
- [ ] Day 1: Enable API; run simple build (docker)
- [ ] Day 2: cloudbuild.yaml basics; steps/images
- [ ] Day 3: Triggers (GitHub/CSR); branch filters
- [ ] Day 4: Service account + permissions; logs
- [ ] Day 5: Artifacts/images; push to Artifact Registry
- [ ] Day 6: Notifications (Pub/Sub/Slack)
- [ ] Day 7: Mini-project: build+push on PR
- [ ] Day 8: Substitutions; env handling
- [ ] Day 9: Timeouts; approvals basics
- [ ] Day 10: Review + refactor
- [ ] Day 11-12: Cache strategies overview
- [ ] Day 13-14: Basic security: pin base images

**Milestone**: Reliable CI builds with triggers and logging.

## Weeks 3-4: Intermediate (🟡)
- [ ] Day 15: Kaniko/docker caching; parallel steps
- [ ] Day 16: Tests + lint + SCA in pipeline
- [ ] Day 17: SBOM + signing (cosign) basics
- [ ] Day 18: Policy checks (Conftest/OPA) before deploy
- [ ] Day 19: Workload Identity Federation for external repos
- [ ] Day 20: Multi-region/regional builds; artifact locality
- [ ] Day 21: Approvals for protected branches
- [ ] Day 22-23: Mini-project: full CI (build/test/scan/sign)
- [ ] Day 24-25: Cloud Deploy integration (staged rollout)
- [ ] Day 26-28: Cost tuning: timeouts, caching, parallelism

**Milestone**: Secure, scanned, signed artifacts with staged delivery.

## Weeks 5-6: Advanced (🔴)
- [ ] Day 29: Private pools; org policies on builders/regions
- [ ] Day 30: Advanced signing + attestations; provenance
- [ ] Day 31: Binary Authorization integration
- [ ] Day 32: Large builds split; fan-out/fan-in patterns
- [ ] Day 33: DR: logs/artifacts retention, backups
- [ ] Day 34: SLOs and alerts on build duration/failures
- [ ] Day 35: Governance: approved base images; template libraries
- [ ] Day 36: Budget alerts; per-project quotas
- [ ] Day 37-38: Capstone: enterprise CI with policy gates and deploy
- [ ] Day 39-42: Documentation, SOPs, pipeline library

**Milestone**: Enterprise CI with governance, provenance, and cost controls.

## Resources
- Docs: https://cloud.google.com/build/docs
- Triggers: https://cloud.google.com/build/docs/automating-builds/create-github-app-triggers
- Security: https://cloud.google.com/build/docs/securing-builds

