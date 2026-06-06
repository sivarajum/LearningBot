# Compute Engine Roadmap – 6 Weeks

## Weeks 1-2: Foundations (🟢)
- [ ] Day 1: Create VM; SSH; basic gcloud
- [ ] Day 2: Machine types; disk types; images
- [ ] Day 3: Firewall rules; tags; service accounts
- [ ] Day 4: Snapshots; images; restore basics
- [ ] Day 5: Metadata/startup scripts
- [ ] Day 6: OS Login; disable project-wide SSH keys
- [ ] Day 7: Mini-project: hardened single VM
- [ ] Day 8: Monitoring/logging agents
- [ ] Day 9: Labels for cost/owner
- [ ] Day 10: Review + harden
- [ ] Day 11-12: Spot/preemptible instances; interruptions
- [ ] Day 13-14: Instance templates basics

**Milestone**: Secure single VM with backups and monitoring.

## Weeks 3-4: Intermediate (🟡)
- [ ] Day 15: Managed Instance Groups (MIG) basics
- [ ] Day 16: Health checks; rolling updates
- [ ] Day 17: Autoscaling policies (CPU/custom)
- [ ] Day 18: Regional vs zonal MIGs
- [ ] Day 19: Cloud NAT for egress; private IP focus
- [ ] Day 20: Shielded VMs; patching with OS Config
- [ ] Day 21: Service account least privilege
- [ ] Day 22-23: Mini-project: regional MIG behind LB
- [ ] Day 24-25: Disk perf tuning; pd-ssd/extreme; snapshots schedule
- [ ] Day 26-28: Cost controls: schedules to stop dev VMs; rightsizing

**Milestone**: HA MIG with autoscaling, NAT, security hardened.

## Weeks 5-6: Advanced (🔴)
- [ ] Day 29: Blue/green or canary updates for MIG
- [ ] Day 30: DR runbooks; backup/restore tests
- [ ] Day 31: Compliance: CMEK, VPC-SC, audit logs
- [ ] Day 32: Observability SLOs; alerts on health/perf
- [ ] Day 33: Network design with VPC and LB choices
- [ ] Day 34: Mixed instance policies; spot fleets
- [ ] Day 35: Performance/load testing; capacity planning
- [ ] Day 36: Automation via Terraform/Deployment Manager
- [ ] Day 37-38: Capstone: production-ready MIG with DR and monitoring
- [ ] Day 39-42: Documentation, SOPs, cost/perf reports

**Milestone**: Production-grade compute platform with governance and DR.

## Resources
- Docs: https://cloud.google.com/compute/docs
- MIG: https://cloud.google.com/compute/docs/instance-groups
- Shielded VMs: https://cloud.google.com/shielded-vm

