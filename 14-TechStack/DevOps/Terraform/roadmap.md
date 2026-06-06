# Terraform Roadmap – 6 Weeks

## Weeks 1-2: Foundations (🟢)
- [ ] Day 1: Install Terraform; understand providers/resources
- [ ] Day 2: Write first resource; init/plan/apply/destroy
- [ ] Day 3: Variables, outputs, locals
- [ ] Day 4: Data sources; file/template functions
- [ ] Day 5: State basics; refresh; taint/replace
- [ ] Day 6: Input validation; count/for_each; depends_on
- [ ] Day 7: Workspaces vs directory-per-env
- [ ] Day 8: Remote state intro (S3+Dynamo or GCS+lock)
- [ ] Day 9: Format/validate commands; lint habits
- [ ] Day 10: Basic IAM roles for TF
- [ ] Day 11-12: Mini-project: VPC + EC2/VM + SG
- [ ] Day 13-14: Review and refactor

**Milestone**: Confident authoring simple stacks; safe plan/apply/destroy.

## Weeks 3-4: Intermediate (🟡)
- [ ] Day 15: Modules (inputs/outputs, versioning)
- [ ] Day 16: Registry modules; private module sources
- [ ] Day 17: Backend hardening (locks, encryption, versioning)
- [ ] Day 18: Workspace/env patterns; tfvars per env
- [ ] Day 19: CI basics: fmt/validate/plan on PR
- [ ] Day 20: Secrets handling patterns (Vault/KMS/SM)
- [ ] Day 21: Import existing resources; drift handling
- [ ] Day 22: Refactor to modules; composition
- [ ] Day 23: Tagging/convention enforcement
- [ ] Day 24: Cost/SLO awareness in infra design
- [ ] Day 25-26: Mini-project: 3-tier app infra with modules
- [ ] Day 27-28: Add tests (terraform validate/opa/conftest)

**Milestone**: Modular, environment-aware stacks with CI and basic policy.

## Weeks 5-6: Advanced (🔴)
- [ ] Day 29: Policy-as-code (OPA/Conftest/Sentinel)
- [ ] Day 30: Multi-account/org patterns; landing zones
- [ ] Day 31: Blue/green or parallel stacks for safe changes
- [ ] Day 32: Zero-downtime updates (ASG rolling, ALB failover)
- [ ] Day 33: Supply chain: lock provider versions; checksum verification
- [ ] Day 34: Security: least-privilege TF role, state access controls
- [ ] Day 35: Observability: TF logs, cost visibility, drift alerts
- [ ] Day 36: Caching providers/plugins in CI; remote runners
- [ ] Day 37: State recovery/runbooks; backup/restore drills
- [ ] Day 38: Performance: graph inspection, targeted plans/applies
- [ ] Day 39-40: Capstone: fully automated CI/CD with policy gates
- [ ] Day 41-42: Documentation + handover

**Milestone**: Policy-enforced, multi-env infra with safe deployments.

## Resources
- Terraform Docs: https://developer.hashicorp.com/terraform/docs
- Registry: https://registry.terraform.io/
- AWS/GCP/Azure provider docs
- Policy as code: OPA/Conftest, Sentinel

