# Kubernetes Roadmap – 6 Weeks

## Weeks 1-2: Foundations (🟢)
- [ ] Day 1: Install kind/minikube; kubectl basics
- [ ] Day 2: Pods, ReplicaSets, Deployments; rollouts/rollbacks
- [ ] Day 3: Services (ClusterIP/NodePort/LoadBalancer)
- [ ] Day 4: Ingress basics; deploy nginx ingress
- [ ] Day 5: ConfigMap vs Secret; mount as env/files
- [ ] Day 6: Probes (readiness/liveness), resources (requests/limits)
- [ ] Day 7: Namespaces; labels/selectors
- [ ] Day 8: RBAC basics (ServiceAccount, Role, RoleBinding)
- [ ] Day 9: Volumes (emptyDir, hostPath, PVC/PV)
- [ ] Day 10: Jobs/CronJobs; backoffLimit, concurrency
- [ ] Day 11: kubectl debug, describe, events
- [ ] Day 12: Clean-up and review
- [ ] Day 13-14: Mini-project: 2-tier app with ingress + pvc

**Milestone**: Confident creating basic workloads and services.

## Weeks 3-4: Intermediate (🟡)
- [ ] Day 15: Ingress TLS, cert-manager basics
- [ ] Day 16: HPA with CPU/Memory metrics
- [ ] Day 17: PodDisruptionBudgets; rollout strategies
- [ ] Day 18: Affinity/anti-affinity; topology spread
- [ ] Day 19: Taints/tolerations; priority classes
- [ ] Day 20: ResourceQuotas/LimitRanges (multi-tenant hygiene)
- [ ] Day 21: NetworkPolicies (isolate namespaces)
- [ ] Day 22: Config sync via Kustomize/Helm overlays
- [ ] Day 23: Secrets management patterns (external secrets)
- [ ] Day 24: Logging stack (EFK/PLG) overview
- [ ] Day 25: Metrics (Prometheus) and dashboards (Grafana)
- [ ] Day 26: Tracing (OpenTelemetry/Jaeger) basics
- [ ] Day 27: StatefulSets vs Deployments; headless services
- [ ] Day 28: Mini-project: ingress + TLS + HPA + PDB

**Milestone**: Production patterns (autoscaling, security, ops) understood.

## Weeks 5-6: Advanced (🔴)
- [ ] Day 29: GitOps (Argo CD/Flux) bootstrap
- [ ] Day 30: Progressive delivery (canary/blue-green) with mesh or ingress
- [ ] Day 31: Service Mesh intro (Istio/Linkerd)
- [ ] Day 32: Policy as Code (OPA Gatekeeper/Kyverno)
- [ ] Day 33: Seccomp/AppArmor, non-root, capabilities
- [ ] Day 34: Image scanning/signing (cosign), admission checks
- [ ] Day 35: Multi-cluster/multi-tenant strategies
- [ ] Day 36: Backups (etcd, Velero), DR drills
- [ ] Day 37: Performance tuning (CNI choice, kube-proxy mode)
- [ ] Day 38: Cost controls (limits/requests, autoscaler configs)
- [ ] Day 39: Observability SLOs, alerting, runbooks
- [ ] Day 40-42: Capstone: GitOps-managed app with mesh, policies, full observability

**Milestone**: Ready to operate secure, observable, scalable clusters.

## Resources
- Kubernetes Docs: https://kubernetes.io/docs/home/
- CKAD/CKA curricula for structured practice
- Argo CD: https://argo-cd.readthedocs.io/
- Istio: https://istio.io/

