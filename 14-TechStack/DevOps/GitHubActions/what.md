# GitHub Actions - Complete CI/CD Guide

## What is GitHub Actions?

GitHub Actions is a continuous integration and continuous deployment (CI/CD) platform built directly into GitHub that allows you to automate your software development workflows. It enables you to create custom workflows that build, test, package, release, and deploy your code right from your GitHub repository.

## Core Concepts and Architecture

### Workflows
Workflows are automated processes defined in YAML files that run one or more jobs. They're triggered by events in your repository.

**Key characteristics:**
- Defined in `.github/workflows/` directory
- Written in YAML syntax
- Can be triggered by multiple events
- Support for manual triggers
- Can reference other workflows

### Jobs
Jobs are sets of steps that execute on the same runner. Workflows can contain multiple jobs that run in parallel or sequentially.

**Job properties:**
- **runs-on**: Specifies the runner environment
- **needs**: Defines job dependencies
- **strategy**: Matrix builds for multiple configurations
- **steps**: Individual commands or actions

### Steps
Steps are individual tasks within a job. Each step can run commands, use actions, or set up the environment.

**Step types:**
- **run**: Execute shell commands
- **uses**: Use pre-built actions
- **name**: Descriptive name for the step
- **with**: Parameters for actions
- **env**: Environment variables

### Actions
Actions are reusable units of code that perform specific tasks. They can be written in JavaScript, Docker containers, or shell scripts.

**Types of actions:**
- **Docker actions**: Containerized actions
- **JavaScript actions**: Node.js based actions
- **Composite actions**: Combine multiple steps

### Runners
Runners are servers that execute your workflows. GitHub provides hosted runners, or you can host your own.

**Runner types:**
- **GitHub-hosted**: Ubuntu, Windows, macOS
- **Self-hosted**: Your own infrastructure
- **Larger runners**: More powerful hosted runners

### Events
Events trigger workflows to run. They can be based on repository activity or scheduled.

**Common events:**
- **push**: Code pushed to repository
- **pull_request**: Pull request opened/updated
- **schedule**: Cron-based scheduling
- **workflow_dispatch**: Manual trigger
- **release**: Release published

## Workflow Syntax

### Basic Workflow Structure
```yaml
name: CI Pipeline

on:
  push:
    branches: [ main ]
  pull_request:
    branches: [ main ]

jobs:
  test:
    runs-on: ubuntu-latest

    steps:
    - uses: actions/checkout@v4

    - name: Setup Node.js
      uses: actions/setup-node@v4
      with:
        node-version: '18'

    - name: Install dependencies
      run: npm ci

    - name: Run tests
      run: npm test
```

### Event Configuration
```yaml
on:
  # Run on pushes to main branch
  push:
    branches: [ main, develop ]

  # Run on pull requests
  pull_request:
    branches: [ main ]
    types: [opened, synchronize, reopened]

  # Manual trigger
  workflow_dispatch:
    inputs:
      environment:
        description: 'Environment to deploy to'
        required: true
        default: 'staging'

  # Scheduled runs
  schedule:
    - cron: '0 2 * * 1'  # Every Monday at 2 AM

  # Run on releases
  release:
    types: [published]
```

### Job Configuration
```yaml
jobs:
  build:
    runs-on: ubuntu-latest

    # Job dependencies
    needs: test

    # Environment variables
    env:
      NODE_ENV: production

    # Job strategy for matrix builds
    strategy:
      matrix:
        node-version: [16, 18, 20]
        os: [ubuntu-latest, windows-latest]

    steps:
    - name: Setup Node.js ${{ matrix.node-version }}
      uses: actions/setup-node@v4
      with:
        node-version: ${{ matrix.node-version }}
```

## Actions Ecosystem

### Official Actions
GitHub provides official actions for common tasks:

- **actions/checkout**: Check out repository code
- **actions/setup-node**: Setup Node.js environment
- **actions/setup-python**: Setup Python environment
- **actions/setup-go**: Setup Go environment
- **actions/upload-artifact**: Upload build artifacts
- **actions/download-artifact**: Download artifacts
- **actions/cache**: Cache dependencies

### Community Actions
Thousands of community-contributed actions available on GitHub Marketplace:

- **codecov/codecov-action**: Code coverage reporting
- **docker/build-push-action**: Build and push Docker images
- **aws-actions/configure-aws-credentials**: AWS authentication
- **google-github-actions/setup-gcloud**: GCP authentication

### Custom Actions
Create your own actions for specific needs:

**JavaScript Action:**
```javascript
const core = require('@actions/core');
const github = require('@actions/github');

try {
  const name = core.getInput('name');
  core.setOutput('greeting', `Hello ${name}!`);
} catch (error) {
  core.setFailed(error.message);
}
```

**Docker Action:**
```dockerfile
FROM alpine:latest
COPY entrypoint.sh /entrypoint.sh
RUN chmod +x /entrypoint.sh
ENTRYPOINT ["/entrypoint.sh"]
```

## Environment and Context

### Contexts
Contexts provide information about the workflow run, runner environment, and job.

**Common contexts:**
- **github**: Information about the workflow run
- **env**: Environment variables
- **vars**: Repository variables
- **secrets**: Repository secrets
- **runner**: Runner information
- **strategy**: Matrix strategy information

**Usage:**
```yaml
steps:
- name: Print context
  run: |
    echo "Repository: ${{ github.repository }}"
    echo "Branch: ${{ github.ref_name }}"
    echo "SHA: ${{ github.sha }}"
    echo "Actor: ${{ github.actor }}"
```

### Environment Variables
Set environment variables at workflow, job, or step level.

```yaml
env:
  GLOBAL_ENV: global_value

jobs:
  test:
    runs-on: ubuntu-latest
    env:
      JOB_ENV: job_value

    steps:
    - name: Step with env
      env:
        STEP_ENV: step_value
      run: |
        echo $GLOBAL_ENV
        echo $JOB_ENV
        echo $STEP_ENV
```

### Secrets Management
Securely store sensitive information like API keys and passwords.

**Types of secrets:**
- **Repository secrets**: Available to all workflows
- **Environment secrets**: Scoped to specific environments
- **Organization secrets**: Available to all repositories in org

**Usage:**
```yaml
steps:
- name: Deploy
  env:
    API_KEY: ${{ secrets.API_KEY }}
  run: ./deploy.sh
```

## Advanced Features

### Matrix Strategies
Run jobs with different configurations in parallel.

```yaml
strategy:
  matrix:
    os: [ubuntu-latest, windows-latest]
    node: [16, 18]
    include:
      - os: ubuntu-latest
        node: 18
        experimental: true
    exclude:
      - os: windows-latest
        node: 16
```

### Conditional Execution
Control when steps or jobs run based on conditions.

```yaml
steps:
- name: Deploy to production
  if: github.ref == 'refs/heads/main' && github.event_name == 'push'
  run: ./deploy-prod.sh

- name: Deploy to staging
  if: github.ref == 'refs/heads/develop' || contains(github.event.pull_request.labels.*.name, 'deploy-staging')
  run: ./deploy-staging.sh
```

### Artifacts and Caching
Share data between jobs and cache dependencies.

**Artifacts:**
```yaml
- name: Upload build artifacts
  uses: actions/upload-artifact@v3
  with:
    name: build-files
    path: dist/

- name: Download artifacts
  uses: actions/download-artifact@v3
  with:
    name: build-files
```

**Caching:**
```yaml
- name: Cache node modules
  uses: actions/cache@v3
  with:
    path: ~/.npm
    key: ${{ runner.os }}-node-${{ hashFiles('**/package-lock.json') }}
    restore-keys: |
      ${{ runner.os }}-node-
```

### Self-Hosted Runners
Run workflows on your own infrastructure for more control.

**Setup:**
```bash
# Download and configure runner
./config.sh --url https://github.com/owner/repo --token <token>
./run.sh
```

**Configuration:**
```yaml
runs-on: self-hosted
# or with labels
runs-on: [self-hosted, linux, x64]
```

### Environments
Group resources and secrets for different deployment targets.

```yaml
jobs:
  deploy:
    runs-on: ubuntu-latest
    environment: production
    steps:
    - name: Deploy
      run: ./deploy.sh
```

## CI/CD Patterns

### Basic CI Pipeline
```yaml
name: CI

on: [push, pull_request]

jobs:
  test:
    runs-on: ubuntu-latest
    steps:
    - uses: actions/checkout@v4
    - uses: actions/setup-node@v4
      with:
        node-version: '18'
    - run: npm ci
    - run: npm test
    - run: npm run lint
```

### Build and Deploy
```yaml
name: Build and Deploy

on:
  push:
    branches: [main]

jobs:
  build:
    runs-on: ubuntu-latest
    steps:
    - uses: actions/checkout@v4
    - name: Build
      run: npm run build
    - name: Upload build artifacts
      uses: actions/upload-artifact@v3
      with:
        name: build-files
        path: dist/

  deploy:
    needs: build
    runs-on: ubuntu-latest
    steps:
    - name: Download build artifacts
      uses: actions/download-artifact@v3
      with:
        name: build-files
    - name: Deploy to staging
      run: ./deploy-staging.sh
```

### Multi-Environment Deployment
```yaml
name: Deploy

on:
  workflow_dispatch:
    inputs:
      environment:
        description: 'Environment to deploy to'
        required: true
        default: 'staging'
        type: choice
        options:
        - staging
        - production

jobs:
  deploy:
    runs-on: ubuntu-latest
    environment: ${{ inputs.environment }}
    steps:
    - name: Deploy
      run: ./deploy.sh ${{ inputs.environment }}
```

### Security Scanning
```yaml
name: Security Scan

on: [push, pull_request]

jobs:
  security:
    runs-on: ubuntu-latest
    steps:
    - uses: actions/checkout@v4
    - name: Run SAST
      uses: github/super-linter/slim@v5
    - name: Run dependency check
      uses: dependency-check/Dependency-Check_Action@main
    - name: Upload SARIF file
      uses: github/codeql-action/upload-sarif@v2
      with:
        sarif_file: reports/results.sarif
```

## Integration with Cloud Platforms

### AWS Integration
```yaml
- name: Configure AWS credentials
  uses: aws-actions/configure-aws-credentials@v4
  with:
    aws-access-key-id: ${{ secrets.AWS_ACCESS_KEY_ID }}
    aws-secret-access-key: ${{ secrets.AWS_SECRET_ACCESS_KEY }}
    aws-region: us-east-1

- name: Deploy to ECS
  run: |
    aws ecs update-service --cluster my-cluster --service my-service --force-new-deployment
```

### Azure Integration
```yaml
- name: Login to Azure
  uses: azure/login@v1
  with:
    creds: ${{ secrets.AZURE_CREDENTIALS }}

- name: Deploy to Azure Web App
  uses: azure/webapps-deploy@v2
  with:
    app-name: my-webapp
    package: .
```

### Google Cloud Integration
```yaml
- name: Authenticate to Google Cloud
  uses: google-github-actions/auth@v1
  with:
    credentials_json: ${{ secrets.GCP_SA_KEY }}

- name: Deploy to Cloud Run
  run: |
    gcloud run deploy my-service --source . --region us-central1
```

## Docker Integration

### Build and Push Images
```yaml
- name: Login to Docker Hub
  uses: docker/login-action@v3
  with:
    username: ${{ secrets.DOCKER_USERNAME }}
    password: ${{ secrets.DOCKER_PASSWORD }}

- name: Build and push Docker image
  uses: docker/build-push-action@v5
  with:
    context: .
    push: true
    tags: myapp:${{ github.sha }}, myapp:latest
```

### Multi-Stage Docker Build
```yaml
- name: Build and push
  uses: docker/build-push-action@v5
  with:
    context: .
    file: ./Dockerfile
    push: true
    tags: myapp:latest
    cache-from: type=gha
    cache-to: type=gha,mode=max
```

## Advanced Workflows

### Reusable Workflows
Create workflows that can be called from other workflows.

**Reusable workflow:**
```yaml
# .github/workflows/reusable.yml
name: Reusable workflow

on:
  workflow_call:
    inputs:
      environment:
        required: true
        type: string

jobs:
  deploy:
    runs-on: ubuntu-latest
    steps:
    - name: Deploy to ${{ inputs.environment }}
      run: echo "Deploying to ${{ inputs.environment }}"
```

**Calling workflow:**
```yaml
jobs:
  call-workflow:
    uses: ./.github/workflows/reusable.yml
    with:
      environment: production
```

### Composite Actions
Create actions that combine multiple steps.

**Composite action:**
```yaml
# .github/actions/setup-env/action.yml
name: Setup Environment
description: Setup development environment

runs:
  using: composite
  steps:
    - name: Setup Node.js
      uses: actions/setup-node@v4
      with:
        node-version: '18'

    - name: Install dependencies
      run: npm ci
      shell: bash
```

### Workflow Templates
Use workflow templates for consistent CI/CD across repositories.

**Organization template:**
```yaml
# .github/workflow-templates/ci.yml
name: CI Pipeline
description: Standard CI pipeline for Node.js projects

jobs:
  test:
    runs-on: ubuntu-latest
    steps:
    - uses: actions/checkout@v4
    - uses: actions/setup-node@v4
      with:
        node-version: '18'
    - run: npm ci
    - run: npm test
```

## Security Best Practices

### Secret Management
- Use GitHub secrets for sensitive data
- Rotate secrets regularly
- Use environment-specific secrets
- Audit secret usage

### Access Control
- Use branch protection rules
- Require code reviews for workflows
- Limit workflow permissions
- Use GITHUB_TOKEN appropriately

### Dependency Scanning
- Scan for vulnerable dependencies
- Keep actions updated
- Use trusted actions only
- Review third-party action code

### Network Security
- Use private repositories for sensitive workflows
- Implement IP allowlisting
- Use VPN for self-hosted runners
- Encrypt communication channels

## Monitoring and Debugging

### Workflow Logs
- View logs in GitHub Actions tab
- Download logs for local analysis
- Use debug logging for troubleshooting

### Debugging Techniques
```yaml
steps:
- name: Debug
  run: |
    echo "GitHub context: ${{ toJSON(github) }}"
    echo "Runner context: ${{ toJSON(runner) }}"
    echo "Environment: ${{ env }}"
```

### Workflow Telemetry
- Monitor workflow duration and success rates
- Set up alerts for failed workflows
- Track resource usage
- Analyze performance bottlenecks

## Performance Optimization

### Caching Strategies
```yaml
- name: Cache dependencies
  uses: actions/cache@v3
  with:
    path: |
      ~/.npm
      node_modules
    key: ${{ runner.os }}-node-${{ hashFiles('**/package-lock.json') }}
```

### Parallel Execution
```yaml
jobs:
  test:
    runs-on: ubuntu-latest
    strategy:
      matrix:
        test-suite: [unit, integration, e2e]
    steps:
    - name: Run ${{ matrix.test-suite }} tests
      run: npm run test:${{ matrix.test-suite }}
```

### Self-Hosted Runners
- Use for better performance
- Custom hardware specifications
- Persistent build environments
- Cost optimization

## Enterprise Features

### GitHub Enterprise Server
- Self-hosted GitHub instance
- Advanced security and compliance
- Custom integrations
- Enterprise support

### Advanced Security
- Code scanning
- Secret scanning
- Dependency review
- Security advisories

### Organization Features
- Organization-wide secrets
- Required workflows
- Workflow templates
- Team-based access control

## Integration with Development Tools

### Code Quality Tools
```yaml
- name: Run ESLint
  run: npx eslint . --ext .js,.jsx,.ts,.tsx

- name: Run Prettier
  run: npx prettier --check .

- name: SonarCloud Scan
  uses: SonarSource/sonarqube-scan-action@v1
```

### Testing Frameworks
```yaml
- name: Run unit tests
  run: npm test -- --coverage

- name: Upload coverage to Codecov
  uses: codecov/codecov-action@v3
  with:
    file: ./coverage/lcov.info
```

### Documentation
```yaml
- name: Build docs
  run: npm run docs:build

- name: Deploy docs
  uses: peaceiris/actions-gh-pages@v3
  with:
    github_token: ${{ secrets.GITHUB_TOKEN }}
    publish_dir: ./docs
```

GitHub Actions represents the evolution of CI/CD by integrating deeply with the development workflow. Its YAML-based configuration, extensive marketplace of actions, and tight integration with GitHub make it a powerful platform for automating software delivery pipelines across the entire development lifecycle.
