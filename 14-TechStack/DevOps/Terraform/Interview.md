# Terraform Interview Questions & Answers

## 🔰 Beginner Level

### Q1: What is Terraform and why is it important?
**Answer:**
Terraform is an open-source Infrastructure as Code (IaC) tool developed by HashiCorp that allows you to define, provision, and manage infrastructure resources across multiple cloud providers using declarative configuration files.

**Why important:**
- **Version control**: Infrastructure changes tracked in Git
- **Consistency**: Same configuration across environments
- **Automation**: Eliminates manual infrastructure setup
- **Multi-cloud**: Works with AWS, Azure, GCP, etc.
- **Reproducibility**: Infrastructure can be recreated identically
- **Collaboration**: Teams can work together on infrastructure

### Q2: Explain the basic Terraform workflow
**Answer:**
The standard Terraform workflow consists of four main steps:

1. **Write**: Create `.tf` configuration files describing desired infrastructure
2. **Initialize**: `terraform init` - Download providers and modules
3. **Plan**: `terraform plan` - Preview changes before applying
4. **Apply**: `terraform apply` - Create/modify/destroy resources

**Optional fifth step:**
- **Destroy**: `terraform destroy` - Clean up all resources

**Key principle**: Always review the plan before applying changes.

### Q3: What is the difference between Terraform and other IaC tools like CloudFormation?
**Answer:**

| Aspect | Terraform | CloudFormation |
|--------|-----------|----------------|
| **Language** | HCL (declarative) | JSON/YAML (declarative) |
| **Multi-cloud** | ✅ Yes | ❌ AWS only |
| **State management** | ✅ Built-in | ❌ No built-in state |
| **Modularity** | ✅ Modules | ❌ Stack references |
| **Community** | ✅ Large ecosystem | ❌ AWS-focused |
| **Learning curve** | 🟡 Medium | 🟡 Medium |

**When to choose Terraform:**
- Multi-cloud deployments
- Complex infrastructure with dependencies
- Team collaboration with version control
- Existing non-AWS infrastructure

### Q4: Explain Terraform providers and resources
**Answer:**
- **Providers**: Plugins that implement resource types for specific platforms (AWS, Azure, GCP)
- **Resources**: Individual infrastructure components (EC2 instance, S3 bucket, etc.)

**Example:**
```hcl
# Provider configuration
provider "aws" {
  region = "us-east-1"
}

# Resource definition
resource "aws_instance" "web" {
  ami           = "ami-12345"
  instance_type = "t2.micro"
}
```

**Key points:**
- Providers must be configured before use
- Resources have unique identifiers: `<provider>_<type>.<name>`
- Each resource type has specific arguments and attributes

### Q5: What are Terraform variables and how do you use them?
**Answer:**
Variables parameterize Terraform configurations, making them reusable and flexible.

**Declaration:**
```hcl
variable "instance_type" {
  description = "EC2 instance type"
  type        = string
  default     = "t2.micro"
}
```

**Usage:**
```hcl
resource "aws_instance" "web" {
  instance_type = var.instance_type
}
```

**Value assignment:**
- `terraform.tfvars` file
- Environment variables: `TF_VAR_instance_type`
- Command line: `terraform apply -var="instance_type=t3.small"`

## 🏗️ Intermediate Level

### Q6: Explain Terraform state and why it's important
**Answer:**
Terraform state is a JSON file (`terraform.tfstate`) that tracks the current state of managed infrastructure.

**Why important:**
- **Mapping**: Maps configuration to real-world resources
- **Dependencies**: Tracks resource relationships
- **Performance**: Avoids re-creating existing resources
- **Collaboration**: Enables team collaboration

**State commands:**
```bash
terraform state list    # List resources
terraform state show    # Show resource details
terraform state rm      # Remove from state
terraform state mv      # Rename resources
```

**Best practices:**
- Store state remotely (S3, GCS, etc.)
- Enable state locking to prevent concurrent modifications
- Never edit state file manually

### Q7: What are Terraform modules and when should you use them?
**Answer:**
Modules are reusable, shareable packages of Terraform configuration that encapsulate related resources.

**Benefits:**
- **Code reuse**: Avoid duplication
- **Organization**: Break complex configs into manageable pieces
- **Consistency**: Standardize infrastructure patterns
- **Versioning**: Control module versions

**Example usage:**
```hcl
module "vpc" {
  source  = "terraform-aws-modules/vpc/aws"
  version = "~> 3.0"

  name = "my-vpc"
  cidr = "10.0.0.0/16"
}
```

**When to use:**
- Repeated infrastructure patterns
- Complex configurations
- Team collaboration
- Sharing with community

### Q8: Explain data sources in Terraform
**Answer:**
Data sources allow Terraform to fetch information from external sources without managing those resources.

**Use cases:**
- Query existing infrastructure
- Get AMI IDs, VPC IDs, availability zones
- Reference resources created outside Terraform
- Dynamic configuration based on existing resources

**Example:**
```hcl
data "aws_ami" "ubuntu" {
  most_recent = true
  owners      = ["099720109477"] # Canonical

  filter {
    name   = "name"
    values = ["ubuntu/images/hvm-ssd/ubuntu-focal-20.04-amd64-server-*"]
  }
}

resource "aws_instance" "web" {
  ami = data.aws_ami.ubuntu.id
}
```

**Key difference from resources:** Data sources are read-only and don't create infrastructure.

### Q9: How do you handle resource dependencies in Terraform?
**Answer:**
Terraform automatically infers dependencies but provides explicit control mechanisms.

**Implicit dependency:**
```hcl
resource "aws_instance" "web" {
  subnet_id = aws_subnet.public.id  # Depends on subnet
}
```

**Explicit dependency:**
```hcl
resource "aws_instance" "web" {
  depends_on = [aws_internet_gateway.gw]
}
```

**Dependency types:**
- **Configuration dependencies**: Based on attribute references
- **Explicit dependencies**: Using `depends_on`
- **Hidden dependencies**: Not visible in configuration

**Best practices:**
- Let Terraform infer dependencies when possible
- Use `depends_on` sparingly
- Understand resource creation order

### Q10: Explain Terraform workspaces
**Answer:**
Workspaces isolate environments within the same configuration, allowing multiple deployments from the same code.

**Use cases:**
- Multiple environments (dev, staging, prod)
- Feature branches
- Customer-specific deployments

**Commands:**
```bash
terraform workspace new dev      # Create workspace
terraform workspace select dev   # Switch workspace
terraform workspace list         # List workspaces
terraform workspace delete dev   # Delete workspace
```

**Key features:**
- Separate state files
- Shared configuration
- Environment-specific variables
- Isolated deployments

## 🚀 Advanced Level

### Q11: How do you implement remote state with locking?
**Answer:**
Remote state stores Terraform state in shared storage with locking to prevent concurrent modifications.

**Backend configuration:**
```hcl
terraform {
  backend "s3" {
    bucket         = "my-terraform-state"
    key            = "prod/terraform.tfstate"
    region         = "us-east-1"
    dynamodb_table = "terraform-locks"
    encrypt        = true
  }
}
```

**Supported backends:**
- S3 (with DynamoDB for locking)
- GCS
- Azure Blob Storage
- Terraform Cloud
- Consul

**Benefits:**
- Team collaboration
- State locking
- Backup and recovery
- Access control

### Q12: Explain count and for_each meta-arguments
**Answer:**
Both create multiple instances of resources, but with different use cases.

**Count:**
```hcl
resource "aws_instance" "web" {
  count = 3

  ami           = "ami-12345"
  instance_type = "t2.micro"
  tags = {
    Name = "web-${count.index}"
  }
}
```

**For_each:**
```hcl
resource "aws_instance" "web" {
  for_each = var.instance_configs

  ami           = each.value.ami
  instance_type = each.value.instance_type
  tags = {
    Name = each.key
  }
}
```

**When to use:**
- **Count**: When you need a fixed number of identical resources
- **For_each**: When you need different configurations or string-based iteration

### Q13: How do you handle secrets in Terraform?
**Answer:**
**Security best practices for secrets:**

1. **Never hardcode secrets:**
   ```hcl
   # ❌ Bad
   resource "aws_db_instance" "db" {
     password = "supersecretpassword"
   }

   # ✅ Good
   resource "aws_db_instance" "db" {
     password = var.db_password
   }
   ```

2. **Use environment variables:**
   ```bash
   export TF_VAR_db_password="secret"
   terraform apply
   ```

3. **External secret management:**
   - AWS Secrets Manager
   - Azure Key Vault
   - HashiCorp Vault
   - Terraform Cloud variable sets

4. **Provider-specific secrets:**
   ```hcl
   data "aws_secretsmanager_secret_version" "db" {
     secret_id = "prod/db/password"
   }
   ```

**Best practices:**
- Use `.gitignore` for sensitive files
- Rotate secrets regularly
- Audit secret usage
- Use least privilege access

### Q14: Explain resource lifecycle management
**Answer:**
Resource lifecycle controls how Terraform handles resource creation, updates, and destruction.

**Create before destroy:**
```hcl
resource "aws_instance" "web" {
  lifecycle {
    create_before_destroy = true
  }
}
```

**Prevent destroy:**
```hcl
resource "aws_db_instance" "production" {
  lifecycle {
    prevent_destroy = true
  }
}
```

**Ignore changes:**
```hcl
resource "aws_instance" "web" {
  lifecycle {
    ignore_changes = [
      tags["LastModified"],
    ]
  }
}
```

**Use cases:**
- Zero-downtime deployments
- Protecting critical resources
- Allowing manual modifications

### Q15: How do you debug Terraform issues?
**Answer:**
**Debugging techniques:**

1. **Verbose logging:**
   ```bash
   export TF_LOG=DEBUG
   terraform apply
   ```

2. **Targeted execution:**
   ```bash
   terraform plan -target=aws_instance.web
   terraform apply -target=aws_instance.web
   ```

3. **State inspection:**
   ```bash
   terraform state show aws_instance.web
   terraform state list
   ```

4. **Validate configuration:**
   ```bash
   terraform validate
   terraform fmt
   ```

5. **Import existing resources:**
   ```bash
   terraform import aws_instance.web i-1234567890abcdef0
   ```

6. **Refresh state:**
   ```bash
   terraform refresh  # Update state with real infrastructure
   ```

**Common issues:**
- State file corruption
- Provider authentication
- Resource dependencies
- Configuration syntax errors

## 🎯 Scenario-Based Questions

### Q16: You need to deploy infrastructure across dev, staging, and prod. How would you structure this?
**Answer:**
**Multi-environment setup strategies:**

1. **Workspaces approach:**
   ```hcl
   # Single configuration, multiple workspaces
   terraform workspace new dev
   terraform workspace new staging
   terraform workspace new prod
   ```

2. **Directory structure:**
   ```
   environments/
   ├── dev/
   │   ├── main.tf
   │   └── terraform.tfvars
   ├── staging/
   │   ├── main.tf
   │   └── terraform.tfvars
   └── prod/
       ├── main.tf
       └── terraform.tfvars
   ```

3. **Shared modules:**
   ```hcl
   # environments/dev/main.tf
   module "vpc" {
     source = "../../modules/vpc"
     environment = "dev"
     instance_size = "small"
   }
   ```

4. **Variable files:**
   ```hcl
   # dev.tfvars
   environment = "dev"
   instance_count = 1
   instance_type = "t2.micro"

   # prod.tfvars
   environment = "prod"
   instance_count = 5
   instance_type = "m5.large"
   ```

**Best practices:**
- Use remote state with workspace isolation
- Environment-specific variable files
- Shared modules for consistency
- Automated testing per environment

### Q17: Terraform apply fails midway. How do you recover?
**Answer:**
**Recovery strategies:**

1. **Check the error:**
   ```bash
   terraform apply  # Re-run (idempotent)
   ```

2. **If state is corrupted:**
   ```bash
   terraform refresh  # Sync state with real infrastructure
   ```

3. **Manual state repair:**
   ```bash
   # Remove failed resource from state
   terraform state rm aws_instance.failed

   # Import if resource exists
   terraform import aws_instance.web i-1234567890abcdef0
   ```

4. **Partial apply:**
   ```bash
   # Apply only successful changes
   terraform apply -target=aws_vpc.main
   ```

5. **Clean up and retry:**
   ```bash
   # Destroy failed resources manually
   # Fix configuration
   terraform apply
   ```

**Prevention:**
- Test plans thoroughly
- Use small, incremental changes
- Implement proper error handling
- Backup state files

### Q18: How do you implement CI/CD with Terraform?
**Answer:**
**CI/CD pipeline integration:**

1. **GitHub Actions example:**
   ```yaml
   name: Terraform
   on: [push]

   jobs:
     terraform:
       runs-on: ubuntu-latest
       steps:
       - uses: actions/checkout@v2

       - name: Setup Terraform
         uses: hashicorp/setup-terraform@v1

       - name: Terraform Init
         run: terraform init

       - name: Terraform Plan
         run: terraform plan -out=tfplan

       - name: Terraform Apply
         if: github.ref == 'refs/heads/main'
         run: terraform apply tfplan
   ```

2. **Plan approval workflow:**
   ```yaml
   - name: Update Pull Request
     uses: actions/github-script@v5
     if: github.event_name == 'pull_request'
     with:
       script: |
         github.rest.issues.createComment({
           issue_number: context.issue.number,
           owner: context.repo.owner,
           repo: context.repo.repo,
           body: 'Terraform plan generated'
         })
   ```

3. **Security scanning:**
   ```yaml
   - name: Terraform Security Scan
     uses: tfsec/tfsec-action@main
     with:
       working_directory: terraform/
   ```

**Best practices:**
- Separate plan and apply stages
- Require manual approval for production
- Use protected branches
- Implement security scanning
- Store state remotely

### Q19: How do you migrate existing infrastructure to Terraform?
**Answer:**
**Migration process:**

1. **Inventory existing resources:**
   - List all resources manually or via API
   - Document dependencies and relationships

2. **Import resources:**
   ```bash
   # Import existing EC2 instance
   terraform import aws_instance.web i-1234567890abcdef0

   # Import VPC
   terraform import aws_vpc.main vpc-12345
   ```

3. **Write configuration:**
   - Match existing resource configurations
   - Use data sources for dependencies
   - Start with minimal configuration

4. **Validate and plan:**
   ```bash
   terraform plan  # Should show no changes
   ```

5. **Gradual migration:**
   - Import in small batches
   - Test thoroughly
   - Update configurations incrementally

**Tools:**
- `terraformer`: Generate Terraform from existing infrastructure
- `terraform import`: Manual import of resources

### Q20: How do you optimize Terraform performance?
**Answer:**
**Performance optimization techniques:**

1. **Parallel execution:**
   ```bash
   terraform apply -parallelism=10
   ```

2. **Resource targeting:**
   ```bash
   terraform plan -target=aws_instance.web
   terraform apply -target=aws_instance.web
   ```

3. **Module optimization:**
   - Break large configurations into smaller modules
   - Use remote modules for caching
   - Minimize module dependencies

4. **Provider configuration:**
   ```hcl
   provider "aws" {
     region = "us-east-1"
     # Optimize API calls
     skip_metadata_api_check = true
     skip_region_validation  = true
   }
   ```

5. **State optimization:**
   - Use remote state
   - Enable provider caching
   - Minimize state file size

6. **Code optimization:**
   - Use `count` and `for_each` efficiently
   - Prefer data sources over resources when possible
   - Use dynamic blocks for repetitive configurations

## 🧠 Expert Level

### Q21: Explain Terraform's graph engine and execution planning
**Answer:**
Terraform uses a directed acyclic graph (DAG) to model resource dependencies and execution order.

**Graph building process:**
1. **Parse configuration**: Read all `.tf` files
2. **Identify resources**: Create nodes for each resource
3. **Analyze dependencies**: Build edges based on attribute references
4. **Topological sorting**: Order nodes for execution
5. **Parallel execution**: Run independent resources concurrently

**Graph visualization:**
```bash
terraform graph > graph.dot
# Convert to PNG: dot -Tpng graph.dot -o graph.png
```

**Execution phases:**
- **Refresh**: Update state with current infrastructure
- **Plan**: Calculate changes needed
- **Apply**: Execute changes in dependency order

### Q22: How do you implement custom providers?
**Answer:**
**Custom provider development:**

1. **Choose language:** Go (recommended) or any language with gRPC
2. **Define schema:** Resource and data source schemas
3. **Implement CRUD operations:** Create, Read, Update, Delete
4. **Handle configuration:** Provider configuration block
5. **Build and distribute:** Compile and publish

**Basic structure:**
```go
func Provider() *schema.Provider {
  return &schema.Provider{
    Schema: map[string]*schema.Schema{
      "api_key": {
        Type:        schema.TypeString,
        Required:    true,
        Sensitive:   true,
      },
    },
    ResourcesMap: map[string]*schema.Resource{
      "example_resource": resourceExample(),
    },
  }
}
```

**Use cases:**
- Internal APIs
- Legacy systems
- Custom cloud platforms
- Specialized infrastructure

### Q23: Explain Sentinel policies in Terraform Cloud
**Answer:**
Sentinel is HashiCorp's policy as code framework for infrastructure governance.

**Policy example:**
```hcl
# Require encryption for S3 buckets
import "tfplan"

main = rule {
  all tfplan.resource_changes as rc;
  rc.type is "aws_s3_bucket" implies
    rc.change.after.server_side_encryption_configuration exists
}

# Enforce instance types
allowed_instance_types = ["t2.micro", "t3.small", "t3.medium"]

instance_type_valid = rule {
  all tfplan.resource_changes as rc;
  rc.type is "aws_instance" implies
    rc.change.after.instance_type in allowed_instance_types
}
```

**Policy types:**
- **Hard mandatory**: Block non-compliant changes
- **Soft mandatory**: Warn but allow with approval
- **Advisory**: Informational only

**Integration:**
- Runs during plan phase
- Integrated with Terraform Cloud
- Supports custom logic and external data

### Q24: How do you implement GitOps with Terraform?
**Answer:**
**GitOps workflow with Terraform:**

1. **Infrastructure as code in Git:**
   - All Terraform configurations version controlled
   - Pull requests for changes
   - Code reviews required

2. **Automated deployment:**
   - CI/CD pipelines trigger on merge
   - Automated testing and validation
   - Progressive deployment (dev → staging → prod)

3. **Drift detection:**
   - Regular reconciliation checks
   - Alert on configuration drift
   - Automated remediation

4. **Tools integration:**
   - **Atlantis**: Automated Terraform in pull requests
   - **Terraform Cloud**: Remote execution and collaboration
   - **ArgoCD**: GitOps for Kubernetes manifests

**Example workflow:**
```yaml
# Pull Request opened
# → Atlantis runs terraform plan
# → Comments plan output on PR
# → Code review and approval
# → PR merged
# → CI/CD runs terraform apply
# → Infrastructure updated
```

### Q25: How do you handle Terraform at enterprise scale?
**Answer:**
**Enterprise Terraform management:**

1. **Repository Structure:**
   ```
   terraform/
   ├── modules/           # Shared modules
   ├── environments/     # Environment configs
   ├── components/       # Service components
   └── global/          # Global resources
   ```

2. **Governance:**
   - **Policy as Code**: Sentinel policies
   - **Approval Workflows**: Required for production
   - **Cost Controls**: Budget alerts and limits
   - **Security Scanning**: Automated vulnerability checks

3. **State Management:**
   - **Remote State**: Centralized storage
   - **State Locking**: Prevent concurrent modifications
   - **Backup Strategy**: Regular state backups
   - **Access Control**: RBAC for state access

4. **CI/CD Integration:**
   - **Automated Testing**: Unit and integration tests
   - **Progressive Deployment**: Environment promotion
   - **Rollback Procedures**: Automated rollback on failure
   - **Monitoring**: Infrastructure and application monitoring

5. **Team Collaboration:**
   - **Code Reviews**: Required for all changes
   - **Documentation**: Comprehensive READMEs and docs
   - **Training**: Regular Terraform training sessions
   - **Support**: Dedicated Terraform support team

6. **Performance and Cost:**
   - **Resource Optimization**: Right-sizing instances
   - **Cost Allocation**: Tagging for cost tracking
   - **Performance Monitoring**: Execution time tracking
   - **Caching**: Provider and module caching

## 📚 Additional Resources

- [Terraform Documentation](https://www.terraform.io/docs)
- [Terraform Registry](https://registry.terraform.io/)
- [HashiCorp Learn](https://learn.hashicorp.com/terraform)
- [Terraform Best Practices](https://www.terraform-best-practices.com/)

## 🎯 Key Takeaways

- **Master the workflow**: init → plan → apply → destroy
- **Understand state**: Critical for tracking and collaboration
- **Use modules**: For reusable, maintainable code
- **Remote state with locking**: Essential for teams
- **Variables and outputs**: Make configurations flexible
- **Lifecycle management**: Control resource behavior
- **Debug effectively**: Use logging, targeting, and state commands
- **Security first**: Handle secrets properly, use remote state
- **CI/CD integration**: Automate testing and deployment
- **Enterprise scale**: Governance, policies, and collaboration

Remember: Terraform is about infrastructure as code - treat it like software development with version control, testing, and collaboration. Focus on understanding the "why" behind each feature and how it enables reliable, scalable infrastructure management.
