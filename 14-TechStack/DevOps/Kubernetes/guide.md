# Kubernetes Guide – Basic → Architect

## Level 1 – Launch & Basics

### 1. Quick Setup
```bash
# Local cluster (choose one)
minikube start --driver=docker
kind create cluster --name dev

# Verify
kubectl get nodes
kubectl get pods -A
```

### 2. First Deployment & Service
```bash
kubectl create deploy web --image=nginx:1.25
kubectl expose deploy web --port=80 --target-port=80 --type=ClusterIP
kubectl port-forward deploy/web 8080:80
```

### 3. Core Concepts
- Objects: Pod, ReplicaSet, Deployment, Service (ClusterIP/NodePort/LoadBalancer), Namespace
- Config: ConfigMap, Secret; Probes: readiness/liveness; Resources: requests/limits
- Scheduling: labels/selectors, affinity/anti-affinity, taints/tolerations

## Level 2 – Production Patterns

### Networking & Ingress
- Use Ingress + controller (Nginx/Traefik) for L7 routing, TLS termination
- DNS via CoreDNS; CNI choice matters (Calico/Cilium/Weave)

### Config & Secrets Management
- Mount ConfigMaps/Secrets as env or files; avoid baking secrets in images
- External secrets operator for cloud KMS/SM integration

### Autoscaling & Reliability
- HPA with CPU/Memory/custom metrics
- PodDisruptionBudget for availability during maintenance
- Readiness gates; graceful shutdown with preStop/terminationGracePeriod

## Level 3 – Architect Playbook

### Multi-Tenancy & Security
- Namespaces per team; ResourceQuotas/LimitRanges
- NetworkPolicies to restrict east-west traffic
- Pod Security (PSA) or OPA Gatekeeper/Kyverno for policy
- Run non-root, drop capabilities, seccomp/apparmor, read-only rootfs

### GitOps & Progressive Delivery
- Argo CD/Flux for declarative sync
- Canary/Blue-Green with Ingress/Service mesh (Istio/Linkerd)
- Helm/Kustomize for packaging/overlays

### Observability & Operations
- Logs: EFK/PLG stacks; Metrics: Prometheus + Grafana
- Tracing: OpenTelemetry/Jaeger
- Backups: etcd backups, Velero for workloads

## Ops Cheat Sheet

| Task | Command | Note |
| --- | --- | --- |
| Contexts | `kubectl config get-contexts` | switch clusters |
| List pods | `kubectl get pods -A -o wide` | overview |
| Describe | `kubectl describe pod <p> -n <ns>` | debug |
| Logs | `kubectl logs -f <p> -n <ns>` | stream |
| Exec | `kubectl exec -it <p> -n <ns> -- sh` | shell |
| Events | `kubectl get events -A --sort-by=.lastTimestamp` | issues |
| Top | `kubectl top pod -A` | resources |

## Architecture Patterns

```mermaid
flowchart LR
  Dev[Git] --> CI[CI Build Image]
  CI --> Scan[Scan/SBOM/Sign]
  Scan --> Registry[Private Registry]
  Registry --> GitOps[GitOps (Argo/Flux)]
  GitOps --> Cluster[Kubernetes Cluster]
  Cluster --> Obs[Logging/Monitoring/Tracing]
  Cluster --> Mesh[Service Mesh]
```

## Checklist Before Production
- [ ] Use Deployment/StatefulSet as appropriate; set probes and resource limits
- [ ] NetworkPolicies enforced; secrets via KMS/External Secrets
- [ ] Ingress with TLS, cert-manager or managed certs
- [ ] HPA + PDB in place; graceful shutdown configured
- [ ] Images scanned/signed; run as non-root with PSP/PSA/OPA policies
- [ ] Backups for etcd/state; disaster recovery tested
- [ ] Observability stack deployed (logs/metrics/traces)

## Learning Path Links
- Track: `LearningTracks/DevOps-Full/track.md`
- Projects: `Projects/DevOps-Full/starter/02-k8s-deploy-hpa.md` and `Projects/Integrated/devops-full-capstone.md`
- Mastery: `Mastery/Kubernetes/` (quiz, scenarios, flashcards)

