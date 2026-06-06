# GCP Compute: Cloud Run vs GKE vs Cloud Functions vs Compute Engine
- Cloud Run: serverless containers, 0->N, good for stateless HTTP.
- GKE: full control, stateful/daemonsets, higher ops.
- Cloud Functions: event-driven, lightweight, short tasks.
- Compute Engine: VMs, max control, lift-and-shift.
- Decision: latency? control? ops budget? stateful? if stateful/daemonset -> GKE/CE; if HTTP stateless -> Run; if event tiny -> CF.
