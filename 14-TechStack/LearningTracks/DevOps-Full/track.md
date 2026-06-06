# Full DevOps Stack — 4-Week Track

## Overview
- Duration: 28 days
- Goal: Build secure, observable, automated infra and delivery across environments.
- Stack: Docker → Kubernetes → Terraform → GitHub Actions/Jenkins → Monitoring/Logging → Security/Secrets.
- Prerequisites: Linux basics, Git, basic cloud concepts.

## Week 1 — Containerization & CI
- Day 1: Docker fundamentals; images, tags, digests; slim builds.
- Day 2: Multi-stage builds; caching; SBOM/signing intro (cosign/syft).
- Day 3: Local dev UX: docker-compose; env management; secrets basics.
- Day 4: CI pipelines in GitHub Actions/Jenkins: build/test/lint; caching strategies.
- Day 5: Image scanning; policy checks; fail CI on critical vulns.
- Day 6: Push to registry (Artifact Registry/GCR); immutable tags; digests in manifests.
- Day 7: Mini-project: service built, scanned, signed, pushed via CI.
- Milestone: Reproducible, scanned, signed images built via CI.

## Week 2 — Kubernetes Foundations
- Day 8: K8s objects: Deployments, Services, Ingress; probes; resources/limits.
- Day 9: Config: ConfigMaps/Secrets; env vs files; Kustomize/Helm basics.
- Day 10: Ingress + certs; rollout strategies (rolling, canary); HPA basics.
- Day 11: Observability: logs/metrics/traces; kube-state metrics; dashboards.
- Day 12: Security: RBAC, PSP replacement (PodSecurity), network policies.
- Day 13: Storage: PVCs, SCs; stateful workloads basics.
- Day 14: Mini-project: app deployed with HPA, ingress, TLS, dashboards.
- Milestone: Observable, secure-ish K8s deploy with rollout strategy.

## Week 3 — IaC & Environments
- Day 15: Terraform basics; providers; state; remote state and locking.
- Day 16: Modules and environments; workspaces vs directory layout; DRY patterns.
- Day 17: Policies: tfsec/checkov; policy as code (OPA/Sentinel pattern).
- Day 18: Secrets: SOPS/SM; CI integration; least-privilege cloud IAM.
- Day 19: Multi-env promotion: dev/stage/prod; drift detection; change review.
- Day 20: Mini-project: Terraform module + envs; CI plan/apply with approvals.
- Milestone: IaC with modules, policies, gated promotion.

## Week 4 — Reliability, Cost, Security Hardening
- Day 21: SLOs/alerts (latency/error); on-call runbooks; chaos day basics.
- Day 22: Backup/restore drills; disaster recovery basics; quotas/limits handling.
- Day 23: Cost controls: rightsizing; autoscaling; registry cleanup; budget alerts.
- Day 24: Supply chain hardening: signatures, provenance; admission controls (Binary Authz / OPA).
- Day 25: Compliance: audit logging; access reviews; encryption; retention.
- Day 26: Performance/load testing; profiling; regression budgets.
- Day 27: Capstone build; blue/green or canary end-to-end.
- Day 28: Capstone review + documentation/runbooks.
- Milestone: Production-ready DevOps platform with policies, observability, and rollback.

## Capstone (Week 4)
**Multi-env, policy-enforced delivery**  
- CI builds, scans, signs Docker images; pushes to registry.  
- Terraform provisions cluster + networking + registry + secrets.  
- K8s manifests via Kustomize/Helm with HPA, ingress, TLS, rollout strategy.  
- Observability: dashboards/alerts; log-based metrics; tracing where applicable.  
- Security: RBAC, network policies, admission checks (scan/sign), secret management.  
- Promotion flow: dev → stage → prod with approvals and rollback drill.  
- Acceptance: Meets SLOs; policy checks enforced; rollback tested; costs monitored.

## Links to Core Docs
- Docker: `DevOps/Docker/guide.md`, `.../roadmap.md`
- Kubernetes: `DevOps/Kubernetes/guide.md`, `.../roadmap.md`
- Terraform: `DevOps/Terraform/guide.md`, `.../roadmap.md`
- CI/CD: `DevOps/GitHub-Actions/guide.md`, `DevOps/Jenkins/guide.md`
- Monitoring: `DevOps/Monitoring/guide.md`

