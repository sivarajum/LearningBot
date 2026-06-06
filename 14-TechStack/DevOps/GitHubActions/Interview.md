# GitHub Actions Interview Questions & Answers

## Beginner Level Questions

### 1. What is GitHub Actions?
**Answer:** GitHub Actions is a CI/CD platform that allows you to automate your software development workflows directly in your GitHub repository. It enables you to create workflows that build, test, and deploy your code right from GitHub.

**Key Points:**
- Built into GitHub (no external services needed)
- Uses YAML files stored in `.github/workflows/`
- Triggered by GitHub events (push, PR, releases, etc.)
- Supports multiple languages and frameworks

### 2. What are the main components of a GitHub Actions workflow?
**Answer:** A GitHub Actions workflow consists of:
- **Events**: What triggers the workflow (push, pull_request, schedule, etc.)
- **Jobs**: A set of steps that execute on the same runner
- **Steps**: Individual tasks within a job (run commands, use actions)
- **Actions**: Reusable units of code that perform tasks
- **Runners**: Machines that execute the jobs (GitHub-hosted or self-hosted)

### 3. How do you define a basic workflow file?
**Answer:** A basic workflow file is a YAML file stored in `.github/workflows/` directory:

```yaml
name: CI
on: [push, pull_request]
jobs:
  build:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - name: Run tests
        run: npm test
```

### 4. What are GitHub-hosted runners?
**Answer:** GitHub-hosted runners are virtual machines provided by GitHub that run your workflows. They come pre-configured with:
- Ubuntu Linux, Windows, and macOS
- Common tools and software pre-installed
- Automatic updates and maintenance
- No setup required from users

### 5. How do you run jobs on different operating systems?
**Answer:** Use the `runs-on` key with different values:

```yaml
jobs:
  test:
    runs-on: ${{ matrix.os }}
    strategy:
      matrix:
        os: [ubuntu-latest, windows-latest, macos-latest]
```

## Intermediate Level Questions

### 6. Explain the difference between `run` and `uses` in workflow steps.
**Answer:**
- **`run`**: Executes shell commands directly on the runner
- **`uses`**: References a GitHub Action from the marketplace or a local action

**Example:**
```yaml
steps:
  - name: Checkout code
    uses: actions/checkout@v4  # Uses an action

  - name: Install dependencies
    run: npm install  # Runs a shell command
```

### 7. How do you handle secrets in GitHub Actions?
**Answer:** Secrets are encrypted environment variables stored at:
- Repository level (Settings → Secrets and variables → Actions)
- Organization level
- Environment level

**Usage:**
```yaml
steps:
  - name: Deploy
    run: |
      echo "Deploying with ${{ secrets.API_KEY }}"
    env:
      API_KEY: ${{ secrets.API_KEY }}
```

### 8. What are workflow triggers and how do you configure them?
**Answer:** Workflow triggers define when workflows run. Common triggers:

```yaml
on:
  push:
    branches: [main, develop]
  pull_request:
    branches: [main]
  schedule:
    - cron: '0 0 * * 0'  # Weekly
  workflow_dispatch:  # Manual trigger
  release:
    types: [published]
```

### 9. How do you cache dependencies in GitHub Actions?
**Answer:** Use the `actions/cache` action to cache dependencies:

```yaml
steps:
  - uses: actions/cache@v3
    with:
      path: ~/.npm
      key: ${{ runner.os }}-node-${{ hashFiles('**/package-lock.json') }}
      restore-keys: |
        ${{ runner.os }}-node-
```

### 10. Explain job dependencies with `needs`.
**Answer:** The `needs` keyword creates job dependencies:

```yaml
jobs:
  build:
    runs-on: ubuntu-latest
    steps:
      - run: echo "Building..."

  test:
    needs: build  # Waits for build to complete
    runs-on: ubuntu-latest
    steps:
      - run: echo "Testing..."

  deploy:
    needs: [build, test]  # Waits for both
    runs-on: ubuntu-latest
    steps:
      - run: echo "Deploying..."
```

## Advanced Level Questions

### 11. How do you implement matrix builds for testing across multiple environments?
**Answer:** Use the `strategy.matrix` to test across combinations:

```yaml
jobs:
  test:
    runs-on: ${{ matrix.os }}
    strategy:
      matrix:
        os: [ubuntu-latest, windows-latest]
        node: [16, 18, 20]
        include:
          - os: ubuntu-latest
            node: 18
            experimental: true
        exclude:
          - os: windows-latest
            node: 16
    steps:
      - uses: actions/setup-node@v4
        with:
          node-version: ${{ matrix.node }}
      - run: npm test
```

### 12. How do you create reusable workflows?
**Answer:** Create a workflow in `.github/workflows/` and call it from other workflows:

**Reusable workflow (called-workflow.yml):**
```yaml
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
      - run: echo "Deploying to ${{ inputs.environment }}"
```

**Caller workflow:**
```yaml
name: CI
on: [push]

jobs:
  call-workflow:
    uses: ./.github/workflows/called-workflow.yml
    with:
      environment: production
```

### 13. Explain self-hosted runners and when to use them.
**Answer:** Self-hosted runners are machines you provide and manage:
- Run on your own infrastructure
- Support custom hardware/software requirements
- Better for GPU workloads, specialized tools
- Required for accessing private networks

**Setup:**
```bash
# Download and configure runner
./config.sh --url https://github.com/owner/repo --token <token>
./run.sh
```

**Labels for targeting:**
```yaml
jobs:
  gpu-job:
    runs-on: [self-hosted, gpu, linux]
```

### 14. How do you implement conditional logic in workflows?
**Answer:** Use conditional expressions with `if`:

```yaml
jobs:
  deploy:
    if: github.ref == 'refs/heads/main' && github.event_name == 'push'
    runs-on: ubuntu-latest
    steps:
      - run: echo "Deploying to production"

  staging:
    if: github.ref == 'refs/heads/develop' || contains(github.event.pull_request.labels.*.name, 'deploy-staging')
    runs-on: ubuntu-latest
    steps:
      - run: echo "Deploying to staging"
```

### 15. How do you handle artifacts in GitHub Actions?
**Answer:** Use `actions/upload-artifact` and `actions/download-artifact`:

**Upload:**
```yaml
steps:
  - name: Upload build artifacts
    uses: actions/upload-artifact@v3
    with:
      name: build-files
      path: dist/
      retention-days: 30
```

**Download:**
```yaml
steps:
  - name: Download build artifacts
    uses: actions/download-artifact@v3
    with:
      name: build-files
      path: artifacts/
```

### 16. Explain the security model of GitHub Actions.
**Answer:** GitHub Actions security includes:
- **GITHUB_TOKEN**: Automatic token with repository permissions
- **Secrets**: Encrypted environment variables
- **Permissions**: Granular control over token permissions
- **CodeQL**: Security vulnerability scanning
- **Dependency review**: Checks for vulnerable dependencies

**Permissions example:**
```yaml
permissions:
  contents: read
  issues: write
  pull-requests: write
  id-token: write  # For OIDC
```

### 17. How do you implement OIDC (OpenID Connect) for cloud deployments?
**Answer:** Use OIDC to authenticate with cloud providers without long-lived secrets:

```yaml
permissions:
  id-token: write
  contents: read

jobs:
  deploy:
    runs-on: ubuntu-latest
    steps:
      - uses: aws-actions/configure-aws-credentials@v4
        with:
          role-to-assume: arn:aws:iam::123456789012:role/GitHubActionsRole
          aws-region: us-east-1
```

### 18. How do you optimize workflow performance?
**Answer:** Performance optimization techniques:

1. **Caching:**
```yaml
- uses: actions/cache@v3
  with:
    path: ~/.npm
    key: npm-${{ hashFiles('package-lock.json') }}
```

2. **Parallel jobs:**
```yaml
jobs:
  test1:
    runs-on: ubuntu-latest
  test2:
    runs-on: ubuntu-latest
  test3:
    runs-on: ubuntu-latest
```

3. **Conditional execution:**
```yaml
steps:
  - name: Skip on documentation
    if: "!contains(github.event.head_commit.modified, 'src/')"
    run: echo "No code changes, skipping tests"
```

4. **Larger runners:**
```yaml
runs-on: ubuntu-latest-8-cores  # More CPU cores
```

### 19. How do you create custom actions?
**Answer:** Create actions in three ways:

1. **Docker container action:**
```yaml
name: 'Hello World'
description: 'Greet someone'
inputs:
  who-to-greet:
    description: 'Who to greet'
    required: true
runs:
  using: 'docker'
  image: 'Dockerfile'
```

2. **JavaScript action:**
```yaml
name: 'Hello World'
description: 'Greet someone'
runs:
  using: 'node16'
  main: 'index.js'
```

3. **Composite action:**
```yaml
name: 'Hello World'
description: 'Greet someone'
runs:
  using: 'composite'
  steps:
    - run: echo "Hello ${{ inputs.who }}"
      shell: bash
```

### 20. How do you handle workflow failures and retries?
**Answer:** Implement error handling and retries:

```yaml
jobs:
  deploy:
    runs-on: ubuntu-latest
    steps:
      - name: Deploy with retry
        uses: nick-invision/retry@v2
        with:
          timeout_minutes: 10
          max_attempts: 3
          command: npm run deploy

      - name: Notify on failure
        if: failure()
        run: |
          curl -X POST -H 'Content-type: application/json' \
          --data '{"text":"Deployment failed"}' \
          ${{ secrets.SLACK_WEBHOOK }}
```

## Expert Level Questions

### 21. How do you implement advanced deployment strategies?
**Answer:** Implement blue-green and canary deployments:

**Blue-Green Deployment:**
```yaml
jobs:
  deploy-blue:
    if: github.ref == 'refs/heads/main'
    runs-on: ubuntu-latest
    steps:
      - name: Deploy to blue environment
        run: kubectl set image deployment/myapp myapp=${{ github.sha }}

  route-traffic:
    needs: deploy-blue
    runs-on: ubuntu-latest
    steps:
      - name: Switch traffic to blue
        run: kubectl patch service myapp -p '{"spec":{"selector":{"version":"blue"}}}'

  health-check:
    needs: route-traffic
    runs-on: ubuntu-latest
    steps:
      - name: Health check
        run: |
          if curl -f http://myapp.com/health; then
            echo "Health check passed"
          else
            exit 1
          fi
```

### 22. Explain GitHub Actions for monorepos.
**Answer:** Handle monorepos with path filtering and conditional execution:

```yaml
name: Monorepo CI
on:
  push:
    paths:
      - 'packages/**'
      - '.github/workflows/**'

jobs:
  changed-packages:
    runs-on: ubuntu-latest
    outputs:
      packages: ${{ steps.changes.outputs.packages }}
    steps:
      - uses: actions/checkout@v4
      - name: Get changed packages
        id: changes
        run: |
          echo "packages=$(git diff --name-only HEAD~1 | grep -E 'packages/' | cut -d'/' -f2 | uniq | jq -R -s -c 'split("\n")[:-1]')" >> $GITHUB_OUTPUT

  test:
    needs: changed-packages
    runs-on: ubuntu-latest
    strategy:
      matrix:
        package: ${{ fromJson(needs.changed-packages.outputs.packages) }}
    steps:
      - uses: actions/checkout@v4
      - name: Test ${{ matrix.package }}
        run: |
          cd packages/${{ matrix.package }}
          npm test
```

### 23. How do you implement compliance and audit requirements?
**Answer:** Implement compliance controls:

```yaml
name: Compliance Pipeline
on:
  push:
    branches: [main]
  pull_request:

env:
  COMPLIANCE_LEVEL: high

jobs:
  security-scan:
    runs-on: ubuntu-latest
    permissions:
      security-events: write
    steps:
      - uses: actions/checkout@v4
      - name: Run CodeQL Analysis
        uses: github/codeql-action/init@v2
        with:
          languages: javascript
      - name: Autobuild
        uses: github/codeql-action/autobuild@v2
      - name: Perform CodeQL Analysis
        uses: github/codeql-action/analyze@v2

  dependency-review:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - name: Dependency Review
        uses: actions/dependency-review-action@v3

  license-check:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - name: License Check
        run: |
          npx license-checker --failOn GPL --failOn LGPL
```

### 24. How do you handle large-scale GitHub Actions usage?
**Answer:** Optimize for scale:

1. **Workflow reusability:**
```yaml
# .github/workflows/reusable-deploy.yml
name: Reusable Deploy
on:
  workflow_call:
    inputs:
      environment:
        required: true
        type: string
    secrets:
      api-key:
        required: true

jobs:
  deploy:
    runs-on: ubuntu-latest
    environment: ${{ inputs.environment }}
    steps:
      - uses: actions/checkout@v4
      - name: Deploy
        run: deploy --env ${{ inputs.environment }} --key ${{ secrets.api-key }}
```

2. **Organization-level management:**
```yaml
# .github/workflows/org-ci.yml (organization level)
name: Organization CI
on:
  push:
    branches: [main]

jobs:
  call-repo-workflow:
    uses: myorg/.github@main  # Organization workflow
```

3. **Resource optimization:**
```yaml
jobs:
  test:
    runs-on: ubuntu-latest-16-cores  # Larger runners
    container:
      image: node:18  # Container for isolation
    services:
      postgres:
        image: postgres:13
        env:
          POSTGRES_PASSWORD: postgres
    steps:
      - uses: actions/checkout@v4
      - name: Cache node modules
        uses: actions/cache@v3
        with:
          path: ~/.npm
          key: npm-${{ hashFiles('package-lock.json') }}
```

### 25. Explain advanced security patterns in GitHub Actions.
**Answer:** Implement advanced security:

1. **Token permissions:**
```yaml
permissions:
  contents: read
  pull-requests: write
  id-token: write  # For OIDC
  security-events: write  # For CodeQL

jobs:
  security:
    runs-on: ubuntu-latest
    permissions:
      contents: read
      security-events: write
    steps:
      - uses: actions/checkout@v4
      - name: CodeQL Analysis
        uses: github/codeql-action/init@v2
        with:
          languages: javascript
      - uses: github/codeql-action/analyze@v2
```

2. **Supply chain security:**
```yaml
jobs:
  supply-chain:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
        with:
          fetch-depth: 0  # Full history for better analysis

      - name: Dependency Review
        uses: actions/dependency-review-action@v3

      - name: Scorecard
        uses: ossf/scorecard-action@v2
        with:
          results_file: results.sarif
          results_format: sarif
          publish_results: true
```

3. **Runtime security:**
```yaml
jobs:
  runtime-security:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - name: Build and scan
        run: |
          docker build -t myapp .
          trivy image --exit-code 1 --no-progress myapp
```

## Scenario-Based Questions

### 26. How would you design a CI/CD pipeline for a microservices architecture?
**Answer:** Design a comprehensive microservices pipeline:

```yaml
name: Microservices CI/CD
on:
  push:
    branches: [main]
  pull_request:

jobs:
  detect-changes:
    runs-on: ubuntu-latest
    outputs:
      services: ${{ steps.services.outputs.changed }}
    steps:
      - uses: actions/checkout@v4
      - name: Detect changed services
        id: services
        run: |
          # Logic to detect which services changed
          echo "changed=$(git diff --name-only HEAD~1 | grep -E 'services/' | cut -d'/' -f2 | uniq | jq -R -s -c 'split("\n")[:-1]')" >> $GITHUB_OUTPUT

  build-and-test:
    needs: detect-changes
    runs-on: ubuntu-latest
    strategy:
      matrix:
        service: ${{ fromJson(needs.detect-changes.outputs.services) }}
    steps:
      - uses: actions/checkout@v4
      - name: Build ${{ matrix.service }}
        run: |
          cd services/${{ matrix.service }}
          docker build -t ${{ matrix.service }}:${{ github.sha }} .
      - name: Test ${{ matrix.service }}
        run: |
          cd services/${{ matrix.service }}
          docker run ${{ matrix.service }}:${{ github.sha }} npm test

  deploy-staging:
    needs: [detect-changes, build-and-test]
    if: github.ref == 'refs/heads/main'
    runs-on: ubuntu-latest
    strategy:
      matrix:
        service: ${{ fromJson(needs.detect-changes.outputs.services) }}
    steps:
      - name: Deploy to staging
        run: |
          kubectl set image deployment/${{ matrix.service }}-staging ${{ matrix.service }}=${{ matrix.service }}:${{ github.sha }}

  integration-test:
    needs: deploy-staging
    runs-on: ubuntu-latest
    steps:
      - name: Run integration tests
        run: |
          npm run test:integration

  deploy-production:
    needs: integration-test
    if: github.ref == 'refs/heads/main'
    runs-on: ubuntu-latest
    strategy:
      matrix:
        service: ${{ fromJson(needs.detect-changes.outputs.services) }}
    steps:
      - name: Deploy to production
        run: |
          kubectl set image deployment/${{ matrix.service }} ${{ matrix.service }}=${{ matrix.service }}:${{ github.sha }}
```

### 27. How do you handle database migrations in CI/CD?
**Answer:** Implement database migration strategy:

```yaml
name: Database Migration Pipeline
on:
  push:
    branches: [main]
    paths:
      - 'migrations/**'

jobs:
  validate-migration:
    runs-on: ubuntu-latest
    services:
      postgres:
        image: postgres:13
        env:
          POSTGRES_PASSWORD: postgres
        options: >-
          --health-cmd pg_isready
          --health-interval 10s
          --health-timeout 5s
          --health-retries 5
    steps:
      - uses: actions/checkout@v4
      - name: Install migration tool
        run: npm install -g db-migrate
      - name: Validate migrations
        run: |
          db-migrate check
      - name: Dry run migration
        run: |
          db-migrate up --dry-run

  backup-database:
    runs-on: ubuntu-latest
    if: github.ref == 'refs/heads/main'
    steps:
      - name: Create backup
        run: |
          pg_dump -h ${{ secrets.DB_HOST }} -U ${{ secrets.DB_USER }} -d ${{ secrets.DB_NAME }} > backup.sql
      - name: Upload backup
        uses: actions/upload-artifact@v3
        with:
          name: database-backup
          path: backup.sql

  migrate-production:
    needs: [validate-migration, backup-database]
    runs-on: ubuntu-latest
    if: github.ref == 'refs/heads/main'
    steps:
      - uses: actions/checkout@v4
      - name: Run migrations
        run: |
          db-migrate up
        env:
          DATABASE_URL: ${{ secrets.DATABASE_URL }}

  rollback-plan:
    needs: migrate-production
    if: failure()
    runs-on: ubuntu-latest
    steps:
      - name: Generate rollback plan
        run: |
          echo "Rollback steps:" > rollback-plan.txt
          echo "1. Restore from backup" >> rollback-plan.txt
          echo "2. Run db-migrate down" >> rollback-plan.txt
      - name: Upload rollback plan
        uses: actions/upload-artifact@v3
        with:
          name: rollback-plan
          path: rollback-plan.txt
```

### 28. How do you implement chaos engineering in CI/CD?
**Answer:** Integrate chaos engineering into pipelines:

```yaml
name: Chaos Engineering Pipeline
on:
  schedule:
    - cron: '0 2 * * 1'  # Weekly chaos experiments
  workflow_dispatch:
    inputs:
      experiment:
        description: 'Chaos experiment to run'
        required: true
        default: 'pod-kill'

jobs:
  chaos-experiment:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - name: Setup chaos toolkit
        run: |
          pip install chaostoolkit
          pip install chaostoolkit-kubernetes

      - name: Run chaos experiment
        run: |
          chaos run experiments/${{ github.event.inputs.experiment || 'pod-kill' }}.json
        env:
          KUBECONFIG: ${{ secrets.KUBECONFIG }}

      - name: Collect metrics
        run: |
          # Collect system metrics during chaos
          kubectl top pods
          kubectl get events --sort-by=.metadata.creationTimestamp

      - name: Generate report
        run: |
          chaos report --export-format=html journal.json chaos-report.html

      - name: Upload chaos report
        uses: actions/upload-artifact@v3
        with:
          name: chaos-report
          path: chaos-report.html

  validate-resilience:
    needs: chaos-experiment
    runs-on: ubuntu-latest
    steps:
      - name: Health checks
        run: |
          # Verify system recovered
          curl -f http://myapp.com/health
          # Check error rates
          # Verify data consistency

      - name: Alert if system didn't recover
        if: failure()
        run: |
          curl -X POST -H 'Content-type: application/json' \
          --data '{"text":"Chaos experiment failed - system did not recover"}' \
          ${{ secrets.SLACK_WEBHOOK }}
```

## Summary

GitHub Actions interview questions span from basic workflow creation to advanced enterprise scenarios. Key areas to master include:

- **Core concepts**: Workflows, jobs, steps, actions, runners
- **Configuration**: YAML syntax, triggers, conditions, matrices
- **Security**: Secrets, permissions, OIDC, CodeQL
- **Optimization**: Caching, parallel execution, resource management
- **Advanced patterns**: Reusable workflows, self-hosted runners, custom actions
- **Enterprise features**: Compliance, audit, governance, integrations
- **Real-world scenarios**: Microservices, databases, chaos engineering

Understanding these concepts demonstrates proficiency in modern CI/CD practices and DevOps automation.
