# Terraform Guide – Basic → Architect

## Level 1 – Launch & Basics

### 1. Quick Setup
```bash
curl -fsSL https://apt.releases.hashicorp.com/gpg | sudo apt-key add -
sudo apt-add-repository "deb [arch=amd64] https://apt.releases.hashicorp.com $(lsb_release -cs) main"
sudo apt-get update && sudo apt-get install terraform

terraform -help
```

### 2. First Configuration
```hcl
# main.tf
provider "aws" { region = "us-east-1" }

resource "aws_s3_bucket" "demo" { bucket = "tf-demo-12345" }
```
```bash
terraform init
terraform plan
terraform apply -auto-approve
terraform destroy -auto-approve
```

### 3. Core Concepts
- Providers, resources, data sources, variables, outputs
- State: `terraform.tfstate`; never hand-edit; protect with locks
- Execution: plan -> apply; refresh, drift, taint/replace

## Level 2 – Production Patterns

### Modules & Reuse
- Create modules per component (vpc, eks, rds)
- Version modules via git/tag/registry; pin versions

### State Management
- Remote state (S3+DynamoDB, GCS+locking, Terraform Cloud)
- State permissions: read-only for most; locks mandatory

### Workspaces & Environments
- Use workspaces or directory-per-env; keep variables per env
- Naming/tagging conventions; outputs consumed by downstream apps

### CI/CD Integration
- Validate/format: `terraform fmt -check`, `terraform validate`
- Plan on PR, apply on main with approvals
- Cache providers/plugins; store plan files securely

## Level 3 – Architect Playbook

### Policy & Governance
- Policy-as-code: Sentinel/OPA/Conftest; block non-compliant plans
- Enforce tagging, encryption, instance types, network rules

### Scaling & Complexity
- Multi-account landing zones; org-level guardrails
- Dependency graph awareness; target apply with care
- Zero-downtime changes; blue/green infra for risky components

### Security & Supply Chain
- Lock provider versions; checksum verification
- Secrets via vault/KMS/SM, not TF vars/state
- Rotate backend creds; least privilege IAM

## Ops Cheat Sheet

| Task | Command | Note |
| --- | --- | --- |
| Init | `terraform init` | download providers |
| Validate | `terraform validate` | syntax/type |
| Format | `terraform fmt -recursive` | style |
| Plan | `terraform plan -out=tfplan` | review |
| Apply | `terraform apply tfplan` | execute |
| State list | `terraform state list` | resources |
| Import | `terraform import <addr> <id>` | adopt |
| Taint | `terraform taint <addr>` | force replace |

## Architecture Patterns

```mermaid
flowchart LR
  Dev[Developer] --> VCS[Git Repo]
  VCS --> CI[CI Plan]
  CI --> Policy[Policy as Code]
  Policy -->|Pass| Apply[Apply (Prod)]
  Apply --> State[Remote State + Lock]
  State --> Cloud[Cloud Resources]
```

## Checklist Before Production
- [ ] Remote state with locking; backups enabled
- [ ] Provider and module versions pinned
- [ ] fmt/validate/plan in CI; manual approval for apply
- [ ] Sensitive vars via Vault/KMS/SM; not in state/plain text
- [ ] Policies enforced (tagging, encryption, sizes, network)
- [ ] Rollback/runbook; drift detection; state access controlled

## Learning Path Links
- Track: `LearningTracks/DevOps-Full/track.md`
- Projects: `Projects/DevOps-Full/starter/03-terraform-module.md` and `Projects/Integrated/devops-full-capstone.md`
- Mastery: `Mastery/Terraform/` (quiz, scenarios, flashcards)

