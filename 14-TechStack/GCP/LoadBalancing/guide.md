# Load Balancing Guide – Basic → Architect

## Level 1 – Launch & Basics

### 1. Types Overview
- External HTTP(S) (global), Internal HTTP(S) (regional)
- External TCP/UDP/SSL, Internal TCP/UDP
- Network vs proxy; Global vs Regional scopes

### 2. Quick HTTP(S) LB (global)
```bash
# Backend service (instance group) + URL map + target HTTP proxy + forwarding rule
# gcloud commands abbreviated for brevity; console wizard can be used initially.
```

### 3. Core Concepts
- Frontend (IP/port/protocol), backend service (IG/MIG/NEG), health checks
- Host/path rules; URL maps; SSL certs (managed)
- NEGs for serverless (Cloud Run/Functions/App Engine) and GKE

## Level 2 – Production Patterns

### Design & Routing
- Use NEGs for GKE/Cloud Run for pod-level health and scale
- Path/host routing; multi-region backends; CDN enablement
- Session affinity only when needed; keep stateless if possible

### Security
- HTTPS with managed certs; redirect HTTP→HTTPS
- Cloud Armor for WAF/rate limits; reCAPTCHA for bots
- Private Service Connect/ILB for internal consumers

### Performance & Cost
- Caching via Cloud CDN where appropriate
- Connection draining; backend timeouts; max rates tuned
- Use regional LBs for internal traffic to reduce egress

## Level 3 – Architect Playbook

### Reliability
- Health checks tuned to app; failover backends; capacity planning
- Blue/green/canary by weighted backends
- SLA/SLO alerts on latency/error rates; synthetic probes

### Observability
- Cloud Logging/Monitoring; request logs; export to SIEM
- Tracing (if using service mesh/serverless NEGs)

### Governance
- IAM on certificates and LB configs; org policies on external IPs
- Standard naming; infra-as-code for LB configs (Terraform)

## Ops Cheat Sheet

| Task | Command/Concept | Note |
| --- | --- | --- |
| Managed cert | `gcloud compute ssl-certificates create --domains ...` | TLS |
| Backend | `gcloud compute backend-services create ...` | targets |
| Health check | `gcloud compute health-checks create http ...` | liveness |
| URL map | `gcloud compute url-maps create ...` | routing |
| Rule | `gcloud compute forwarding-rules create ...` | frontend |

## Architecture Patterns

```mermaid
flowchart LR
  Client --> Frontend[Frontend IP/Port]
  Frontend --> LB[HTTP(S) LB]
  LB --> CDN[Cloud CDN]
  LB --> Backends[Backends (MIG/NEG/Run/GKE)]
  LB --> Armor[Cloud Armor]
  LB --> Logs[Logging/Monitoring]
```

## Checklist Before Production
- [ ] HTTPS enforced; managed certs; HTTP→HTTPS redirect
- [ ] Health checks tuned; backends sized; failover plan
- [ ] Cloud Armor/WAF as needed; rate limits
- [ ] NEGs for serverless/GKE; path/host routing validated
- [ ] Logging/metrics/alerts on 4xx/5xx/latency; IaC managed

## Learning Path Links
- Track: `LearningTracks/Backend-GCP/track.md`
- Projects: `Projects/GCP-Backend/starter/05-load-balancer.md` and `Projects/Integrated/backend-gcp-capstone.md`
- Mastery: `Mastery/GCP-LoadBalancing/` (quiz, scenarios, flashcards)

