# Capstone: Multi-Env GitOps Platform
- CI: build/scan/sign images; provenance; push to registry.
- IaC: Terraform modules + envs; policy checks; remote state.
- CD: GitOps (Argo/Flux) for K8s; HPA; ingress+TLS; admission checks for signed images.
- Observability: dashboards/alerts; tracing optional.
- Security: RBAC, network policies, secret mgmt, admission control.
- Operations: dev->stage->prod promotion with approvals; rollback drill; cost + audit reports.
