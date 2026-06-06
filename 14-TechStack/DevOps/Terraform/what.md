# Terraform - Complete Infrastructure as Code Guide

## What is Terraform?

Terraform is an open-source Infrastructure as Code (IaC) tool developed by HashiCorp that enables you to define, provision, and manage infrastructure resources across multiple cloud providers and on-premises environments. It uses declarative configuration files to describe the desired state of your infrastructure, then automatically creates, updates, or destroys resources to match that state.

## Core Concepts and Architecture

### Infrastructure as Code (IaC)
IaC is the practice of managing and provisioning infrastructure through machine-readable definition files, rather than physical hardware configuration or interactive configuration tools.

**Benefits:**
- **Version Control**: Infrastructure changes tracked in Git
- **Consistency**: Same configuration across environments
- **Reproducibility**: Infrastructure can be recreated identically
- **Collaboration**: Teams can work together on infrastructure
- **Automation**: CI/CD integration for infrastructure deployment

### Declarative vs Imperative
- **Declarative**: Specify what you want (desired state)
- **Imperative**: Specify how to achieve it (step-by-step commands)

Terraform is declarative - you describe the end state, Terraform figures out how to get there.

### Terraform Architecture

#### Terraform Core
The main Terraform binary that handles:
- Configuration parsing
- State management
- Plan generation
- Resource graph building
- Execution orchestration

#### Providers
Plugins that implement resource types for specific platforms:
- **Cloud providers**: AWS, Azure, GCP, DigitalOcean
- **Infrastructure**: VMware, OpenStack
- **SaaS platforms**: GitHub, Datadog, Cloudflare
- **On-premises**: Kubernetes, Docker

#### State
Terraform maintains state to track resources and their configurations:
- **Local state**: Single file (`terraform.tfstate`)
- **Remote state**: Shared storage (S3, Consul, Terraform Cloud)
- **State locking**: Prevents concurrent modifications

### Configuration Language (HCL)
HashiCorp Configuration Language - JSON-compatible syntax designed for infrastructure configuration.

**Basic structure:**
```hcl
# Block type and labels
resource "aws_instance" "example" {
  # Arguments
  ami           = "ami-12345"
  instance_type = "t2.micro"

  # Nested blocks
  tags = {
    Name = "Example"
  }
}
```

## Terraform Workflow

### 1. Write Configuration
Create `.tf` files describing desired infrastructure.

### 2. Initialize
```bash
terraform init
```
- Downloads providers and modules
- Initializes backend for state storage
- Sets up working directory

### 3. Plan
```bash
terraform plan
```
- Compares current state with desired configuration
- Shows what will be created, modified, or destroyed
- Safe preview of changes

### 4. Apply
```bash
terraform apply
```
- Executes the plan
- Creates/modifies/destroys resources
- Updates state file

### 5. Destroy (optional)
```bash
terraform destroy
```
- Removes all resources managed by configuration

## Resource Management

### Resources
The basic building blocks representing infrastructure objects.

**Syntax:**
```hcl
resource "<PROVIDER>_<TYPE>" "<NAME>" {
  # Configuration arguments
  argument1 = "value1"
  argument2 = "value2"

  # Nested blocks
  nested_block {
    nested_argument = "value"
  }
}
```

**Example:**
```hcl
resource "aws_instance" "web" {
  ami           = "ami-12345"
  instance_type = "t2.micro"

  tags = {
    Name = "WebServer"
  }
}
```

### Data Sources
Allow Terraform to fetch information from external sources.

**Use cases:**
- Query existing infrastructure
- Get AMI IDs, VPC IDs, etc.
- Reference resources not managed by Terraform

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
```

### Resource Dependencies
Terraform automatically infers dependencies but can be explicit.

**Implicit dependency:**
```hcl
resource "aws_instance" "web" {
  subnet_id = aws_subnet.public.id  # Depends on subnet
}

resource "aws_subnet" "public" {
  vpc_id = aws_vpc.main.id
}
```

**Explicit dependency:**
```hcl
resource "aws_instance" "web" {
  depends_on = [aws_internet_gateway.gw]
}
```

## State Management

### Local State
- Stored in `terraform.tfstate`
- Single developer, single environment
- Simple but not collaborative

### Remote State
- Stored in shared backend (S3, GCS, Azure Blob, etc.)
- Enables team collaboration
- Supports state locking

**Backend configuration:**
```hcl
terraform {
  backend "s3" {
    bucket = "my-terraform-state"
    key    = "prod/terraform.tfstate"
    region = "us-east-1"
  }
}
```

### State Locking
Prevents multiple users from modifying state simultaneously.

**Supported backends:**
- S3 with DynamoDB
- Azure Blob Storage
- GCS
- Terraform Cloud

## Modules

### What are Modules?
Reusable, shareable packages of Terraform configuration.

**Benefits:**
- Code reuse
- Organization
- Consistency across projects
- Version control

### Module Structure
```
my-module/
├── main.tf          # Main configuration
├── variables.tf     # Input variables
├── outputs.tf       # Output values
├── README.md        # Documentation
└── terraform.tf     # Backend and provider config
```

### Using Modules
```hcl
module "vpc" {
  source  = "./modules/vpc"
  version = "1.0.0"

  vpc_cidr = "10.0.0.0/16"
  name     = "production"
}
```

### Module Sources
- **Local paths**: `./modules/vpc`
- **Git repositories**: `git::https://github.com/example/terraform-vpc.git`
- **Terraform Registry**: `terraform-aws-modules/vpc/aws`
- **HTTP URLs**: `https://example.com/module.zip`

## Variables and Outputs

### Input Variables
Parameters that make modules flexible and reusable.

**Declaration:**
```hcl
variable "instance_type" {
  description = "EC2 instance type"
  type        = string
  default     = "t2.micro"

  validation {
    condition     = contains(["t2.micro", "t3.small", "t3.medium"], var.instance_type)
    error_message = "Instance type must be t2.micro, t3.small, or t3.medium."
  }
}
```

**Usage:**
```hcl
resource "aws_instance" "example" {
  instance_type = var.instance_type
}
```

### Output Values
Expose information about created resources.

**Declaration:**
```hcl
output "instance_ip" {
  description = "Public IP of the EC2 instance"
  value       = aws_instance.example.public_ip
  sensitive   = false
}

output "instance_id" {
  description = "ID of the EC2 instance"
  value       = aws_instance.example.id
}
```

## Providers

### Provider Configuration
Configure how Terraform interacts with APIs.

**Basic configuration:**
```hcl
terraform {
  required_providers {
    aws = {
      source  = "hashicorp/aws"
      version = "~> 4.0"
    }
  }
}

provider "aws" {
  region = "us-east-1"
}
```

### Provider Aliases
Use multiple configurations of the same provider.

```hcl
provider "aws" {
  region = "us-east-1"
  alias  = "primary"
}

provider "aws" {
  region = "us-west-2"
  alias  = "secondary"
}

resource "aws_instance" "primary" {
  provider = aws.primary
  # ...
}
```

### Provider Versioning
```hcl
terraform {
  required_providers {
    aws = {
      source  = "hashicorp/aws"
      version = ">= 4.0, < 5.0"
    }
  }
}
```

## Resource Lifecycle

### Create Before Destroy
Ensure new resources exist before destroying old ones.

```hcl
resource "aws_instance" "example" {
  lifecycle {
    create_before_destroy = true
  }
}
```

### Prevent Destroy
Protect critical resources from accidental deletion.

```hcl
resource "aws_db_instance" "production" {
  lifecycle {
    prevent_destroy = true
  }
}
```

### Ignore Changes
Allow manual modifications to specific attributes.

```hcl
resource "aws_instance" "example" {
  lifecycle {
    ignore_changes = [
      tags["LastModified"],
    ]
  }
}
```

## Workspaces

### What are Workspaces?
Isolated environments within the same configuration.

**Use cases:**
- Multiple environments (dev, staging, prod)
- Feature branches
- Customer-specific deployments

### Workspace Commands
```bash
# Create workspace
terraform workspace new production

# Switch workspace
terraform workspace select development

# List workspaces
terraform workspace list

# Delete workspace
terraform workspace delete development
```

### Workspace-specific Variables
- `terraform.tfvars` - All workspaces
- `dev.tfvars` - Development workspace
- `prod.tfvars` - Production workspace

## Advanced Features

### Dynamic Blocks
Generate nested blocks dynamically.

```hcl
resource "aws_security_group" "example" {
  dynamic "ingress" {
    for_each = var.ingress_rules

    content {
      from_port   = ingress.value.from_port
      to_port     = ingress.value.to_port
      protocol    = ingress.value.protocol
      cidr_blocks = ingress.value.cidr_blocks
    }
  }
}
```

### For Expressions
Transform collections.

```hcl
locals {
  instance_ids = [for instance in aws_instance.example : instance.id]

  instance_map = {for instance in aws_instance.example :
    instance.tags["Name"] => instance.id}
}
```

### Count and For Each
Create multiple instances of resources.

**Count:**
```hcl
resource "aws_instance" "web" {
  count = 3

  ami           = "ami-12345"
  instance_type = "t2.micro"

  tags = {
    Name = "WebServer-${count.index}"
  }
}
```

**For Each:**
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

## Terraform Cloud and Enterprise

### Terraform Cloud
HashiCorp's managed service for Terraform.

**Features:**
- Remote execution
- State management
- Team collaboration
- Policy enforcement
- Cost estimation
- Private module registry

### Sentinel Policies
Policy as Code for infrastructure governance.

```hcl
# Require encryption for S3 buckets
import "tfplan"

main = rule {
  all tfplan.resource_changes as rc;
  rc.type is "aws_s3_bucket" implies
    rc.change.after.server_side_encryption_configuration exists
}
```

## Best Practices

### Code Organization
```
project/
├── main.tf                 # Main configuration
├── variables.tf           # Input variables
├── outputs.tf             # Output values
├── terraform.tfvars       # Variable values
├── versions.tf            # Provider versions
├── backend.tf             # Backend configuration
└── modules/               # Custom modules
    ├── vpc/
    ├── ec2/
    └── rds/
```

### Naming Conventions
- Use lowercase with hyphens: `web-server-prod`
- Consistent resource naming
- Use descriptive names
- Follow provider naming conventions

### Security Best Practices
- Store state securely (encrypted, access controlled)
- Use remote state with locking
- Avoid hardcoding secrets
- Use Terraform Cloud/Enterprise for secrets management
- Implement least privilege access

### Version Control
- Commit `.tf` files (configuration)
- Never commit `.tfstate` files
- Use `.gitignore` for sensitive files
- Tag releases for infrastructure versions

## Common Patterns

### Multi-Environment Setup
```hcl
# environments/dev/main.tf
module "vpc" {
  source = "../../modules/vpc"

  environment = "dev"
  vpc_cidr    = "10.0.0.0/16"
}

# environments/prod/main.tf
module "vpc" {
  source = "../../modules/vpc"

  environment = "prod"
  vpc_cidr    = "10.0.0.0/16"
}
```

### Infrastructure Testing
- **Static analysis**: `terraform validate`, `terraform fmt`
- **Policy checking**: Sentinel, OPA
- **Integration testing**: Kitchen-Terraform, Terratest
- **Manual testing**: Plan reviews, staged deployments

### CI/CD Integration
```yaml
# GitHub Actions example
- name: Terraform Plan
  run: |
    terraform init
    terraform plan -out=tfplan

- name: Terraform Apply
  run: |
    terraform apply tfplan
```

## Troubleshooting

### Common Issues

#### State File Corruption
```bash
# Force unlock (use carefully)
terraform force-unlock LOCK_ID

# Recover from backup
terraform state push backup.tfstate
```

#### Resource Dependencies
```bash
# Show dependency graph
terraform graph

# Target specific resources
terraform plan -target=aws_instance.example
```

#### Provider Issues
```bash
# Reinitialize providers
terraform init -upgrade

# Debug provider communication
TF_LOG=DEBUG terraform apply
```

### Debugging Commands
```bash
# Show current state
terraform show

# List resources in state
terraform state list

# Import existing resources
terraform import aws_instance.example i-1234567890abcdef0

# Remove resources from state
terraform state rm aws_instance.example
```

## Integration with Other Tools

### Terragrunt
Thin wrapper that provides extra tools for keeping configurations DRY.

**Features:**
- Remote state management
- Module dependency management
- Multi-account setups
- Keep configurations DRY

### Atlantis
Self-hosted GitHub app for Terraform automation.

**Features:**
- Plan and apply via pull requests
- Policy checking
- Multi-environment support

### Terraform CDK
Infrastructure as Code using familiar programming languages.

**Supported languages:**
- TypeScript
- Python
- Java
- C#
- Go

## Migration Strategies

### From Manual Infrastructure
1. **Inventory existing resources**
2. **Import resources to Terraform state**
3. **Write configuration matching current state**
4. **Test changes with plan**
5. **Gradual migration**

### From Other IaC Tools
- **CloudFormation**: Use Terraform AWS provider
- **ARM Templates**: Use Terraform Azure provider
- **Pulumi**: Export state or rewrite configurations

## Performance Optimization

### Parallelism
```bash
# Increase parallel operations
terraform apply -parallelism=10
```

### Resource Targeting
```bash
# Apply only specific resources
terraform apply -target=aws_instance.web
```

### Module Optimization
- Use `count` and `for_each` efficiently
- Minimize resource dependencies
- Use data sources for read-only operations

## Enterprise Considerations

### Governance
- **Policy as Code**: Sentinel, OPA
- **Approval workflows**: Terraform Cloud
- **Audit trails**: Version control, Terraform Cloud
- **Cost management**: Cost estimation, budget alerts

### Compliance
- **Security scanning**: Checkov, tfsec
- **Compliance frameworks**: CIS, NIST
- **Automated remediation**: Policy enforcement

### Disaster Recovery
- **State backups**: Regular state file backups
- **Multi-region**: Cross-region state replication
- **Recovery procedures**: Documented recovery steps

Terraform represents the evolution of infrastructure management, enabling teams to treat infrastructure as code with the same rigor applied to application development. Its declarative approach, combined with powerful automation capabilities, makes it the standard for modern infrastructure provisioning across cloud and on-premises environments.
