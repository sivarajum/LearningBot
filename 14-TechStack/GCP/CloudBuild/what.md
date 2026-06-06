# Cloud Build - What You Need to Know

## Overview

Cloud Build is Google's fully managed continuous integration and continuous deployment (CI/CD) platform that executes builds using containers. It allows you to build, test, and deploy applications across multiple environments using a serverless architecture.

## Core Architecture

### Build Execution Model

**Container-Based Builds**
- **Build Steps**: Executed in Docker containers
- **Custom Images**: Use any Docker image as build environment
- **Isolated Execution**: Each step runs in clean container
- **Artifact Storage**: Build outputs stored in Cloud Storage

**Build Configuration**
```yaml
steps:
- name: 'gcr.io/cloud-builders/docker'
  args: ['build', '-t', 'gcr.io/$PROJECT_ID/my-image', '.']
- name: 'gcr.io/cloud-builders/kubectl'
  args: ['apply', '-f', 'k8s.yaml']
  env:
  - 'CLOUDSDK_COMPUTE_ZONE=us-central1-a'
  - 'CLOUDSDK_CONTAINER_CLUSTER=my-cluster'
```

### Trigger System

**Build Triggers**
- **Push Triggers**: Automatic builds on git push
- **Pull Request Triggers**: Build on PR creation/update
- **Manual Triggers**: On-demand builds
- **Scheduled Triggers**: Time-based builds

**Source Integration**
- **Cloud Source Repositories**: Native Git integration
- **GitHub**: External repository support
- **Bitbucket**: Third-party Git integration
- **Custom Sources**: Direct upload or Cloud Storage

## Key Features

### Build Steps and Images

**Pre-built Builders**
- **Official Builders**: Google-maintained images
- **Community Builders**: Open-source contributions
- **Custom Builders**: Organization-specific images

**Common Builders**
```yaml
# Docker operations
- name: 'gcr.io/cloud-builders/docker'

# Kubernetes deployment
- name: 'gcr.io/cloud-builders/kubectl'

# Go application
- name: 'gcr.io/cloud-builders/go'

# Node.js application
- name: 'gcr.io/cloud-builders/npm'

# Python application
- name: 'gcr.io/cloud-builders/pip'
```

### Build Environment

**Compute Resources**
- **CPU/Memory**: Configurable compute allocation
- **Disk Space**: 100GB default, expandable
- **Network**: Full internet access
- **Privileged Mode**: Docker-in-Docker support

**Environment Variables**
- **Built-in Variables**: PROJECT_ID, BUILD_ID, etc.
- **Custom Variables**: User-defined environment
- **Secrets**: Encrypted sensitive data
- **Substitutions**: Dynamic value replacement

### Artifact Management

**Build Artifacts**
- **Container Images**: Push to Container Registry
- **Binaries**: Store in Cloud Storage
- **Packages**: Upload to Artifact Registry
- **Test Results**: Archive test outputs

**Artifact Registry Integration**
```yaml
steps:
- name: 'gcr.io/cloud-builders/docker'
  args: ['push', 'gcr.io/$PROJECT_ID/my-app:$COMMIT_SHA']
- name: 'gcr.io/cloud-builders/gsutil'
  args: ['cp', 'artifacts/*', 'gs://my-bucket/builds/$BUILD_ID/']
```

## Build Configuration

### Cloud Build Config Files

**cloudbuild.yaml**
```yaml
# Build configuration
steps:
- name: 'gcr.io/cloud-builders/go'
  args: ['build', '.']
  env: ['GOPATH=.']

# Test execution
- name: 'gcr.io/cloud-builders/go'
  args: ['test', './...']

# Docker build and push
- name: 'gcr.io/cloud-builders/docker'
  args: ['build', '-t', 'gcr.io/$PROJECT_ID/app:$SHORT_SHA', '.']

# Deploy to Cloud Run
- name: 'gcr.io/cloud-builders/gcloud'
  args: ['run', 'deploy', 'my-service', '--image', 'gcr.io/$PROJECT_ID/app:$SHORT_SHA', '--region', 'us-central1']

# Store build artifacts
artifacts:
  objects:
    location: 'gs://my-bucket/'
    paths: ['artifacts/*']
```

### Advanced Configuration

**Build Substitutions**
```yaml
# Dynamic substitutions
substitutions:
  _SERVICE_NAME: my-app
  _REGION: us-central1

steps:
- name: 'gcr.io/cloud-builders/gcloud'
  args: ['run', 'deploy', '${_SERVICE_NAME}', '--region', '${_REGION}']
```

**Conditional Steps**
```yaml
steps:
- name: 'gcr.io/cloud-builders/go'
  args: ['test', './...']
  # Only run tests on main branch
  when:
    branch: '^main$'
```

**Parallel Execution**
```yaml
steps:
# Parallel test execution
- name: 'gcr.io/cloud-builders/go'
  args: ['test', './pkg/...']
  id: 'test-pkg'
- name: 'gcr.io/cloud-builders/go'
  args: ['test', './cmd/...']
  id: 'test-cmd'
  waitFor: ['-']  # Run in parallel
```

## Integration Capabilities

### Source Control Integration

**GitHub Integration**
- **Automatic Triggers**: Build on push/PR
- **Status Checks**: Update PR status
- **Comments**: Post build results
- **Webhooks**: Custom integration points

**Repository Configuration**
```yaml
# .cloudbuild/github-triggers.yaml
triggers:
- name: 'main-branch-trigger'
  github:
    owner: 'my-org'
    name: 'my-repo'
    push:
      branch: '^main$'
  build:
    steps:
    - name: 'gcr.io/cloud-builders/go'
      args: ['build', '.']
```

### Cloud Deploy Integration

**Delivery Pipelines**
```yaml
# Cloud Deploy configuration
apiVersion: deploy.cloud.google.com/v1
kind: DeliveryPipeline
metadata:
  name: my-app-pipeline
spec:
  serialPipeline:
    stages:
    - targetId: dev
      profiles: [dev]
    - targetId: staging
      profiles: [staging]
    - targetId: prod
      profiles: [prod]
```

**Progressive Delivery**
- **Canary Deployments**: Gradual traffic shifting
- **Blue-Green Deployments**: Zero-downtime updates
- **Rollbacks**: Automated failure recovery
- **Approval Gates**: Manual deployment controls

### Multi-Environment Deployment

**Environment Configuration**
```yaml
# dev environment
- name: 'gcr.io/cloud-builders/gcloud'
  args: ['run', 'deploy', 'my-app-dev', '--image', 'gcr.io/$PROJECT_ID/app:$SHORT_SHA']
  env:
  - 'ENV=dev'
  - 'DATABASE_URL=dev-db-url'

# prod environment
- name: 'gcr.io/cloud-builders/gcloud'
  args: ['run', 'deploy', 'my-app-prod', '--image', 'gcr.io/$PROJECT_ID/app:$SHORT_SHA']
  env:
  - 'ENV=prod'
  - 'DATABASE_URL=prod-db-url'
```

## Security and Compliance

### Identity and Access Management

**Service Accounts**
- **Build Service Account**: Default execution identity
- **Custom Service Accounts**: Granular permissions
- **Workload Identity**: Kubernetes integration
- **External Accounts**: Third-party system access

**Permissions Model**
```yaml
# Required IAM roles
roles:
- roles/cloudbuild.builds.builder    # Execute builds
- roles/storage.objectAdmin          # Access Cloud Storage
- roles/container.developer          # Push to GCR
- roles/cloudfunctions.developer     # Deploy functions
```

### Secret Management

**Secret Manager Integration**
```yaml
# Available secrets
availableSecrets:
  secretManager:
  - versionName: projects/$PROJECT_ID/secrets/my-secret/versions/latest
    env: 'API_KEY'

steps:
- name: 'gcr.io/cloud-builders/docker'
  secretEnv: ['API_KEY']
```

**Encrypted Variables**
- **Build-time Secrets**: Injected during execution
- **Runtime Secrets**: Available to running containers
- **Audit Logging**: Secret access tracking

### Network Security

**Private Pools**
- **VPC Networks**: Private build execution
- **Private Google Access**: Internal resource access
- **VPC Service Controls**: Network perimeter security

**Private Pool Configuration**
```yaml
# Private pool setup
privatePool:
  networking:
    peeredNetwork: projects/host-project/global/networks/my-network
  workerConfig:
    diskSizeGb: 100
    machineType: e2-medium
```

## Performance and Scaling

### Build Optimization

**Caching Strategies**
```yaml
# Docker layer caching
steps:
- name: 'gcr.io/cloud-builders/docker'
  args: ['build', '--cache-from', 'gcr.io/$PROJECT_ID/my-app:cache', '-t', 'gcr.io/$PROJECT_ID/my-app:$SHORT_SHA', '.']

# Go module caching
- name: 'gcr.io/cloud-builders/go'
  args: ['mod', 'download']
  env: ['GOPATH=/workspace/go']
```

**Parallel Builds**
- **Matrix Builds**: Multiple build configurations
- **Concurrent Steps**: Parallel execution within build
- **Build Sharding**: Split large builds

**Resource Optimization**
- **Machine Types**: n1-standard-1 to n1-highcpu-32
- **Timeout Configuration**: Maximum build duration
- **Retry Logic**: Automatic failure recovery

### Monitoring and Observability

**Build Metrics**
- **Build Duration**: Execution time tracking
- **Success/Failure Rates**: Build reliability metrics
- **Resource Usage**: CPU/memory consumption
- **Queue Times**: Build scheduling delays

**Logging Integration**
- **Cloud Logging**: Centralized log aggregation
- **Structured Logs**: JSON-formatted build logs
- **Custom Metrics**: Application-specific monitoring

## Build Patterns and Best Practices

### Multi-Stage Docker Builds

**Efficient Image Building**
```dockerfile
# Multi-stage Dockerfile
FROM golang:1.19 AS builder
WORKDIR /app
COPY go.mod go.sum ./
RUN go mod download
COPY . .
RUN go build -o main .

FROM alpine:latest
RUN apk --no-cache add ca-certificates
WORKDIR /root/
COPY --from=builder /app/main .
CMD ["./main"]
```

**Cloud Build Configuration**
```yaml
steps:
- name: 'gcr.io/cloud-builders/docker'
  args: ['build', '-t', 'gcr.io/$PROJECT_ID/my-app:$SHORT_SHA', '.']
- name: 'gcr.io/cloud-builders/docker'
  args: ['push', 'gcr.io/$PROJECT_ID/my-app:$SHORT_SHA']
```

### Testing Integration

**Automated Testing Pipeline**
```yaml
steps:
# Unit tests
- name: 'gcr.io/cloud-builders/go'
  args: ['test', '-v', './...']
  env: ['GO111MODULE=on']

# Integration tests
- name: 'gcr.io/cloud-builders/docker'
  args: ['run', '--network', 'cloudbuild', 'postgres:13']
  id: 'start-db'
- name: 'gcr.io/cloud-builders/go'
  args: ['test', '-tags=integration', './...']
  waitFor: ['start-db']

# Load tests (optional)
- name: 'gcr.io/cloud-builders/k6'
  args: ['run', 'load-test.js']
  when:
    branch: '^main$'
```

### Deployment Strategies

**Blue-Green Deployment**
```yaml
steps:
# Deploy to green environment
- name: 'gcr.io/cloud-builders/gcloud'
  args: ['run', 'deploy', 'my-app-green', '--image', 'gcr.io/$PROJECT_ID/app:$SHORT_SHA']

# Run smoke tests
- name: 'gcr.io/cloud-builders/curl'
  args: ['my-app-green-url/health']

# Switch traffic (manual approval)
- name: 'gcr.io/cloud-builders/gcloud'
  args: ['run', 'services', 'update-traffic', 'my-app', '--to-revisions', 'green=100']
```

**Canary Deployment**
```yaml
steps:
# Deploy canary
- name: 'gcr.io/cloud-builders/gcloud'
  args: ['run', 'deploy', 'my-app-canary', '--image', 'gcr.io/$PROJECT_ID/app:$SHORT_SHA', '--no-traffic']

# Route 5% traffic
- name: 'gcr.io/cloud-builders/gcloud'
  args: ['run', 'services', 'update-traffic', 'my-app', '--to-revisions', 'canary=5,stable=95']

# Monitor and promote
- name: 'gcr.io/cloud-builders/gcloud'
  args: ['run', 'services', 'update-traffic', 'my-app', '--to-revisions', 'canary=100']
```

## Cost Optimization

### Pricing Model

**Build Minutes**
- **Concurrent Builds**: First 120 minutes free per month
- **Additional Minutes**: $0.006 per minute
- **Private Pools**: Additional compute costs

**Storage Costs**
- **Build Logs**: 30-day retention free
- **Artifacts**: Cloud Storage pricing
- **Container Images**: Container Registry pricing

### Optimization Strategies

**Build Efficiency**
- **Caching**: Reduce build times and costs
- **Parallel Execution**: Maximize resource utilization
- **Selective Builds**: Only build changed components

**Resource Management**
- **Machine Types**: Match compute to workload
- **Timeout Settings**: Prevent runaway builds
- **Build Frequency**: Balance speed vs cost

## Integration with Development Workflow

### GitOps Integration

**Infrastructure as Code**
```yaml
# Terraform deployment
steps:
- name: 'hashicorp/terraform'
  args: ['init']
- name: 'hashicorp/terraform'
  args: ['plan', '-out=tfplan']
- name: 'hashicorp/terraform'
  args: ['apply', 'tfplan']
```

**GitOps Pipeline**
- **Pull Requests**: Automated testing and validation
- **Main Branch**: Production deployment
- **Release Tags**: Versioned releases
- **Hotfixes**: Emergency deployment path

### Multi-Repository Setup

**Monorepo vs Polyrepo**
- **Monorepo**: Single repository, shared builds
- **Polyrepo**: Multiple repositories, independent builds
- **Hybrid**: Mix of shared and independent components

**Shared Libraries**
```yaml
# Build shared library
- name: 'gcr.io/cloud-builders/go'
  args: ['build', './shared-lib']
  id: 'build-lib'

# Use in dependent services
- name: 'gcr.io/cloud-builders/go'
  args: ['build', './service-a']
  waitFor: ['build-lib']
- name: 'gcr.io/cloud-builders/go'
  args: ['build', './service-b']
  waitFor: ['build-lib']
```

## Compliance and Governance

### Audit and Compliance

**Build Auditing**
- **Build History**: Complete execution logs
- **Artifact Provenance**: Build source tracking
- **Compliance Reports**: Regulatory requirements
- **Change Tracking**: Configuration drift detection

**Security Scanning**
```yaml
steps:
# Container vulnerability scanning
- name: 'gcr.io/cloud-builders/gcloud'
  args: ['artifacts', 'docker', 'images', 'scan', 'gcr.io/$PROJECT_ID/my-app:$SHORT_SHA', '--format', 'table']

# Code security scanning
- name: 'gcr.io/cloud-builders/git'
  args: ['clone', 'https://github.com/my-org/security-scanner']
- name: 'gcr.io/cloud-builders/go'
  args: ['run', './security-scanner', '--source', '.']
```

### Policy Enforcement

**Build Policies**
- **Required Tests**: Enforce test execution
- **Security Scans**: Mandatory vulnerability checks
- **Code Quality**: Static analysis requirements
- **License Compliance**: Open source license checking

Cloud Build represents the evolution of CI/CD into a serverless, container-native platform that integrates deeply with Google's cloud ecosystem while maintaining flexibility for diverse development workflows.