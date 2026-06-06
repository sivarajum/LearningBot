# GitHub Actions Roadmap – 6 Weeks

## Weeks 1-2: Foundations (🟢)
- [ ] Day 1: Workflow syntax; events (push/PR/schedule)
- [ ] Day 2: Jobs/steps; runners; checkout + setup-language
- [ ] Day 3: Basic CI for one language (lint/test)
- [ ] Day 4: Artifacts upload/download
- [ ] Day 5: Secrets/vars; environments overview
- [ ] Day 6: Matrix builds (versions/os)
- [ ] Day 7: Cache dependencies (actions/cache)
- [ ] Day 8: Reusable actions from Marketplace
- [ ] Day 9: Manual triggers (workflow_dispatch)
- [ ] Day 10: Cron schedules
- [ ] Day 11-12: Mini-project: end-to-end CI for one repo
- [ ] Day 13-14: Review + harden basics

**Milestone**: Reliable CI for a single repo with caching.

## Weeks 3-4: Intermediate (🟡)
- [ ] Day 15: Reusable workflows (`workflow_call`)
- [ ] Day 16: Job outputs, needs, conditionals
- [ ] Day 17: Environments with protections/approvals
- [ ] Day 18: Branch protection + required checks
- [ ] Day 19: Build + publish artifacts/images
- [ ] Day 20: Release workflows (versioning, changelog)
- [ ] Day 21: Test coverage reporting; status checks
- [ ] Day 22: Security scanning (SAST/SCA/secret scan)
- [ ] Day 23: Dependency review gate
- [ ] Day 24: Slack/Teams notifications
- [ ] Day 25-26: Mini-project: reusable CI template across repos
- [ ] Day 27-28: Self-hosted runner basics (if needed)

**Milestone**: Org-wide reusable CI with gates and approvals.

## Weeks 5-6: Advanced (🔴)
- [ ] Day 29: OIDC to cloud (AWS/GCP/Azure) for deploys
- [ ] Day 30: Hardened self-hosted runners (isolation, autoscale)
- [ ] Day 31: Supply chain: pin actions by SHA; provenance
- [ ] Day 32: Policy enforcement (allowlist/denylist, codeowners)
- [ ] Day 33: Performance tuning (concurrency, caching strategy)
- [ ] Day 34: Cost controls (artifact retention, concurrency limits)
- [ ] Day 35: Observability (metrics, logs, failure triage)
- [ ] Day 36: DR runbooks; rollback workflows
- [ ] Day 37: Multi-environment promotion flows
- [ ] Day 38-40: Capstone: secure CI/CD with OIDC deploy + approvals
- [ ] Day 41-42: Documentation + handover

**Milestone**: Secure, compliant CI/CD with hardened runners and OIDC.

## Resources
- Docs: https://docs.github.com/actions
- Reusable workflows: https://docs.github.com/actions/using-workflows/reusing-workflows
- Security hardening: https://docs.github.com/actions/security-guides/security-hardening-for-github-actions

