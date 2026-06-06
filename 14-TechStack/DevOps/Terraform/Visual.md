# Terraform Visual Architecture Guide

## Terraform Core Architecture

```mermaid
graph TB
    %% Define styles
    classDef coreClass fill:#e3f2fd,stroke:#1976d2,stroke-width:3px,color:#0d47a1
    classDef providerClass fill:#f3e5f5,stroke:#7b1fa2,stroke-width:3px,color:#4a148c
    classDef stateClass fill:#e8f5e8,stroke:#388e3c,stroke-width:3px,color:#1b5e20
    classDef configClass fill:#fff3e0,stroke:#f57c00,stroke-width:3px,color:#e65100

    subgraph "🧠 Terraform Core"
        CORE[🔧 Core Engine<br/>Configuration Parser<br/>State Manager<br/>Plan Generator<br/>Graph Builder]
    end

    subgraph "🔌 Providers"
        AWS[☁️ AWS Provider<br/>EC2, S3, RDS]
        AZURE[☁️ Azure Provider<br/>VMs, Storage, Networks]
        GCP[☁️ GCP Provider<br/>Compute, Storage, BigQuery]
        K8S[🐳 Kubernetes Provider<br/>Pods, Services, Deployments]
        OTHER[📦 Other Providers<br/>GitHub, Docker, Cloudflare]
    end

    subgraph "💾 State Management"
        LOCAL[📁 Local State<br/>terraform.tfstate]
        REMOTE[☁️ Remote State<br/>S3, GCS, Azure Blob]
        LOCKING[🔒 State Locking<br/>DynamoDB, Consul]
    end

    subgraph "📄 Configuration"
        HCL[📝 HCL Files<br/>.tf files]
        VARIABLES[🔧 Variables<br/>variables.tf]
        OUTPUTS[📤 Outputs<br/>outputs.tf]
        MODULES[📦 Modules<br/>Reusable components]
    end

    CORE --> AWS
    CORE --> AZURE
    CORE --> GCP
    CORE --> K8S
    CORE --> OTHER

    CORE --> LOCAL
    CORE --> REMOTE
    REMOTE --> LOCKING

    HCL --> CORE
    VARIABLES --> CORE
    OUTPUTS --> CORE
    MODULES --> CORE

    %% Apply styles
    class CORE coreClass
    class AWS,AZURE,GCP,K8S,OTHER providerClass
    class LOCAL,REMOTE,LOCKING stateClass
    class HCL,VARIABLES,OUTPUTS,MODULES configClass
```

## Terraform Workflow

```mermaid
flowchart TD
    A[👨‍💻 Developer] --> B[📝 Write Configuration<br/>.tf files]
    B --> C[🔧 terraform init<br/>Download providers & modules]
    C --> D[📋 terraform plan<br/>Generate execution plan]
    D --> E{Plan Review}

    E -->|❌ Issues Found| F[🐛 Fix Configuration]
    F --> D

    E -->|✅ Approved| G[🚀 terraform apply<br/>Execute changes]
    G --> H[💾 Update State<br/>terraform.tfstate]
    H --> I[📊 Monitor Resources]

    I --> J{Maintenance Needed?}
    J -->|Yes| K[🔄 Update Configuration]
    K --> D
    J -->|No| L[✅ Infrastructure Stable]

    L --> M[🗑️ terraform destroy<br/>Optional cleanup]
```

## Resource Dependency Graph

```mermaid
graph TD
    %% Define styles
    classDef resourceClass fill:#e3f2fd,stroke:#1976d2,stroke-width:2px,color:#0d47a1
    classDef dataClass fill:#f3e5f5,stroke:#7b1fa2,stroke-width:2px,color:#4a148c
    classDef moduleClass fill:#e8f5e8,stroke:#388e3c,stroke-width:2px,color:#1b5e20
    classDef outputClass fill:#fff3e0,stroke:#f57c00,stroke-width:2px,color:#e65100

    subgraph "🏗️ Infrastructure Resources"
        VPC[🌐 VPC<br/>aws_vpc.main]
        SUBNET[🏘️ Subnet<br/>aws_subnet.public]
        IGW[🌉 Internet Gateway<br/>aws_internet_gateway.main]
        RT[🛣️ Route Table<br/>aws_route_table.public]
        SG[🛡️ Security Group<br/>aws_security_group.web]
        EC2[💻 EC2 Instance<br/>aws_instance.web]
    end

    subgraph "📊 Data Sources"
        AMI[📦 AMI Data<br/>data.aws_ami.ubuntu]
        AZ[🗺️ Availability Zones<br/>data.aws_availability_zones.available]
    end

    subgraph "📦 Modules"
        NETWORK[🌐 Network Module<br/>module.network]
        COMPUTE[💻 Compute Module<br/>module.compute]
    end

    subgraph "📤 Outputs"
        VPC_ID[🆔 VPC ID<br/>output.vpc_id]
        INSTANCE_IP[🌐 Instance IP<br/>output.instance_ip]
    end

    AMI --> EC2
    AZ --> SUBNET

    NETWORK --> VPC
    NETWORK --> SUBNET
    NETWORK --> IGW
    NETWORK --> RT

    COMPUTE --> SG
    COMPUTE --> EC2

    VPC --> SUBNET
    IGW --> RT
    RT --> SUBNET
    SUBNET --> EC2
    SG --> EC2

    VPC --> VPC_ID
    EC2 --> INSTANCE_IP

    %% Apply styles
    class VPC,SUBNET,IGW,RT,SG,EC2 resourceClass
    class AMI,AZ dataClass
    class NETWORK,COMPUTE moduleClass
    class VPC_ID,INSTANCE_IP outputClass
```

## State Management Architecture

```mermaid
graph TD
    %% Define styles
    classDef localClass fill:#e3f2fd,stroke:#1976d2,stroke-width:2px,color:#0d47a1
    classDef remoteClass fill:#f3e5f5,stroke:#7b1fa2,stroke-width:2px,color:#4a148c
    classDef lockingClass fill:#e8f5e8,stroke:#388e3c,stroke-width:2px,color:#1b5e20
    classDef backupClass fill:#fff3e0,stroke:#f57c00,stroke-width:2px,color:#e65100

    subgraph "💻 Local Development"
        LOCAL_STATE[📁 terraform.tfstate<br/>Local file]
        LOCAL_LOCK[🔒 .terraform.lock.hcl<br/>Provider versions]
    end

    subgraph "☁️ Remote State Backends"
        S3[🪣 AWS S3<br/>Bucket storage]
        GCS[☁️ Google Cloud Storage<br/>Bucket storage]
        AZURE[🗄️ Azure Blob Storage<br/>Container storage]
        CONSUL[🔍 HashiCorp Consul<br/>KV storage]
        TF_CLOUD[🌐 Terraform Cloud<br/>Managed service]
    end

    subgraph "🔐 State Locking"
        DYNAMODB[📊 AWS DynamoDB<br/>Lock table]
        CONSUL_LOCK[🔍 Consul Sessions<br/>Lock mechanism]
        TF_LOCK[🌐 Terraform Cloud<br/>Built-in locking]
    end

    subgraph "💾 Backup & Recovery"
        VERSIONING[📚 S3 Versioning<br/>State history]
        BACKUP[💼 Manual Backups<br/>terraform state pull/push]
        RECOVERY[🔄 Disaster Recovery<br/>State restoration]
    end

    LOCAL_STATE --> S3
    LOCAL_STATE --> GCS
    LOCAL_STATE --> AZURE
    LOCAL_STATE --> CONSUL
    LOCAL_STATE --> TF_CLOUD

    S3 --> DYNAMODB
    GCS --> TF_LOCK
    AZURE --> TF_LOCK
    CONSUL --> CONSUL_LOCK
    TF_CLOUD --> TF_LOCK

    S3 --> VERSIONING
    GCS --> BACKUP
    AZURE --> BACKUP
    CONSUL --> RECOVERY
    TF_CLOUD --> RECOVERY

    %% Apply styles
    class LOCAL_STATE,LOCAL_LOCK localClass
    class S3,GCS,AZURE,CONSUL,TF_CLOUD remoteClass
    class DYNAMODB,CONSUL_LOCK,TF_LOCK lockingClass
    class VERSIONING,BACKUP,RECOVERY backupClass
```

## Module Architecture

```mermaid
graph TD
    %% Define styles
    classDef rootClass fill:#e3f2fd,stroke:#1976d2,stroke-width:3px,color:#0d47a1
    classDef moduleClass fill:#f3e5f5,stroke:#7b1fa2,stroke-width:2px,color:#4a148c
    classDef registryClass fill:#e8f5e8,stroke:#388e3c,stroke-width:2px,color:#1b5e20
    classDef gitClass fill:#fff3e0,stroke:#f57c00,stroke-width:2px,color:#e65100

    subgraph "🏠 Root Configuration"
        MAIN[📄 main.tf<br/>Root module]
        VARS[🔧 variables.tf<br/>Input variables]
        OUTPUTS[📤 outputs.tf<br/>Output values]
        PROVIDERS[🔌 versions.tf<br/>Provider versions]
    end

    subgraph "📦 Child Modules"
        VPC_MOD[🌐 VPC Module<br/>module.vpc]
        EC2_MOD[💻 EC2 Module<br/>module.ec2]
        RDS_MOD[💾 RDS Module<br/>module.rds]
    end

    subgraph "📚 Module Sources"
        REGISTRY[🏪 Terraform Registry<br/>terraform-aws-modules/*]
        GIT_REPO[📖 Git Repository<br/>github.com/example/module]
        LOCAL_PATH[📁 Local Path<br/>./modules/vpc]
        HTTP_URL[🌐 HTTP Archive<br/>https://example.com/module.zip]
    end

    subgraph "🔧 Module Components"
        MOD_MAIN[📄 main.tf<br/>Module logic]
        MOD_VARS[🔧 variables.tf<br/>Module inputs]
        MOD_OUTPUTS[📤 outputs.tf<br/>Module outputs]
        MOD_README[📖 README.md<br/>Documentation]
    end

    MAIN --> VPC_MOD
    MAIN --> EC2_MOD
    MAIN --> RDS_MOD

    VPC_MOD --> REGISTRY
    EC2_MOD --> GIT_REPO
    RDS_MOD --> LOCAL_PATH

    REGISTRY --> MOD_MAIN
    GIT_REPO --> MOD_VARS
    LOCAL_PATH --> MOD_OUTPUTS
    HTTP_URL --> MOD_README

    %% Apply styles
    class MAIN,VARS,OUTPUTS,PROVIDERS rootClass
    class VPC_MOD,EC2_MOD,RDS_MOD moduleClass
    class REGISTRY registryClass
    class GIT_REPO,LOCAL_PATH,HTTP_URL gitClass
```

## Multi-Environment Setup

```mermaid
graph TD
    %% Define styles
    classDef envClass fill:#e3f2fd,stroke:#1976d2,stroke-width:2px,color:#0d47a1
    classDef sharedClass fill:#f3e5f5,stroke:#7b1fa2,stroke-width:2px,color:#4a148c
    classDef workspaceClass fill:#e8f5e8,stroke:#388e3c,stroke-width:2px,color:#1b5e20
    classDef backendClass fill:#fff3e0,stroke:#f57c00,stroke-width:2px,color:#e65100

    subgraph "🌍 Environments"
        DEV[🧪 Development<br/>dev.tfvars<br/>Small instances]
        STAGING[🧪 Staging<br/>staging.tfvars<br/>Medium instances]
        PROD[🚀 Production<br/>prod.tfvars<br/>Large instances]
    end

    subgraph "📦 Shared Modules"
        NETWORK[🌐 Network Module<br/>VPC, subnets, security]
        COMPUTE[💻 Compute Module<br/>EC2 instances, ASG]
        STORAGE[💾 Storage Module<br/>RDS, S3 buckets]
    end

    subgraph "🏢 Workspaces"
        DEV_WS[🧪 dev workspace<br/>terraform workspace select dev]
        STAGING_WS[🧪 staging workspace<br/>terraform workspace select staging]
        PROD_WS[🚀 prod workspace<br/>terraform workspace select prod]
    end

    subgraph "💾 Remote Backend"
        S3_BACKEND[🪣 S3 Backend<br/>bucket/terraform-states]
        WORKSPACE_KEY[🔑 Workspace Keys<br/>dev/terraform.tfstate<br/>prod/terraform.tfstate]
    end

    DEV --> NETWORK
    STAGING --> NETWORK
    PROD --> NETWORK

    DEV --> COMPUTE
    STAGING --> COMPUTE
    PROD --> COMPUTE

    DEV --> STORAGE
    STAGING --> STORAGE
    PROD --> STORAGE

    NETWORK --> DEV_WS
    COMPUTE --> STAGING_WS
    STORAGE --> PROD_WS

    DEV_WS --> S3_BACKEND
    STAGING_WS --> S3_BACKEND
    PROD_WS --> S3_BACKEND

    S3_BACKEND --> WORKSPACE_KEY

    %% Apply styles
    class DEV,STAGING,PROD envClass
    class NETWORK,COMPUTE,STORAGE sharedClass
    class DEV_WS,STAGING_WS,PROD_WS workspaceClass
    class S3_BACKEND,WORKSPACE_KEY backendClass
```

## CI/CD Integration

```mermaid
flowchart TD
    A[👨‍💻 Code Commit] --> B[🔄 CI Pipeline Trigger]
    B --> C[📥 Checkout Code]
    C --> D[🔧 Terraform Init]
    D --> E[✅ Terraform Validate]
    E --> F[📋 Terraform Plan]

    F --> G{Plan Valid?}
    G -->|❌ Issues| H[🚨 Fail Pipeline]

    G -->|✅ OK| I[👥 Plan Review]
    I --> J{Approved?}
    J -->|❌ Rejected| K[🔄 Request Changes]
    K --> A

    J -->|✅ Approved| L[🚀 Terraform Apply]
    L --> M[🧪 Integration Tests]
    M --> N{Tests Pass?}
    N -->|❌ Failed| O[🔄 Rollback]
    O --> L

    N -->|✅ Passed| P[📊 Update Documentation]
    P --> Q[✅ Deployment Success]
```

## Provider Ecosystem

```mermaid
graph TD
    %% Define styles
    classDef majorClass fill:#e3f2fd,stroke:#1976d2,stroke-width:3px,color:#0d47a1
    classDef cloudClass fill:#f3e5f5,stroke:#7b1fa2,stroke-width:2px,color:#4a148c
    classDef infraClass fill:#e8f5e8,stroke:#388e3c,stroke-width:2px,color:#1b5e20
    classDef saasClass fill:#fff3e0,stroke:#f57c00,stroke-width:2px,color:#e65100
    classDef customClass fill:#fce4ec,stroke:#c2185b,stroke-width:2px,color:#880e4f

    subgraph "🏢 Major Cloud Providers"
        AWS[☁️ AWS<br/>200+ resources]
        AZURE[☁️ Azure<br/>150+ resources]
        GCP[☁️ GCP<br/>100+ resources]
        DIGITALOCEAN[🌊 DigitalOcean<br/>50+ resources]
        LINODE[📊 Linode<br/>30+ resources]
    end

    subgraph "🏗️ Infrastructure Platforms"
        VMWARE[🖥️ VMware vSphere<br/>VM management]
        OPENSTACK[☁️ OpenStack<br/>Private cloud]
        KUBERNETES[🐳 Kubernetes<br/>Container orchestration]
        DOCKER[🐳 Docker<br/>Container management]
    end

    subgraph "📱 SaaS & Platform Providers"
        GITHUB[🐙 GitHub<br/>Repositories, teams]
        DATABRICKS[🔶 Databricks<br/>Data platforms]
        CLOUDFLARE[🌐 Cloudflare<br/>CDN, DNS]
        DATABRICKS[🔶 Databricks<br/>Analytics]
        NEW_RELIC[📊 New Relic<br/>Monitoring]
    end

    subgraph "🔧 Custom & Community"
        CUSTOM[🏗️ Custom Providers<br/>Internal systems]
        COMMUNITY[👥 Community Providers<br/>Open source]
    end

    AWS --> VMWARE
    AZURE --> OPENSTACK
    GCP --> KUBERNETES
    DIGITALOCEAN --> DOCKER
    LINODE --> VMWARE

    VMWARE --> GITHUB
    OPENSTACK --> DATABRICKS
    KUBERNETES --> CLOUDFLARE
    DOCKER --> NEW_RELIC

    GITHUB --> CUSTOM
    DATABRICKS --> COMMUNITY
    CLOUDFLARE --> CUSTOM
    NEW_RELIC --> COMMUNITY

    %% Apply styles
    class AWS,AZURE,GCP,DIGITALOCEAN,LINODE majorClass
    class VMWARE,OPENSTACK,KUBERNETES,DOCKER infraClass
    class GITHUB,DATABRICKS,CLOUDFLARE,NEW_RELIC saasClass
    class CUSTOM,COMMUNITY customClass
```

## Resource Lifecycle Management

```mermaid
graph TD
    %% Define styles
    classDef lifecycleClass fill:#e3f2fd,stroke:#1976d2,stroke-width:2px,color:#0d47a1
    classDef createClass fill:#f3e5f5,stroke:#7b1fa2,stroke-width:2px,color:#4a148c
    classDef updateClass fill:#e8f5e8,stroke:#388e3c,stroke-width:2px,color:#1b5e20
    classDef destroyClass fill:#fff3e0,stroke:#f57c00,stroke-width:2px,color:#e65100

    subgraph "🔄 Resource Lifecycle"
        CREATE[➕ Create<br/>terraform apply]
        UPDATE[🔄 Update<br/>Configuration change]
        REPLACE[🔁 Replace<br/>Immutable change]
        DESTROY[➖ Destroy<br/>terraform destroy]
    end

    subgraph "⚙️ Lifecycle Rules"
        CBD[🔄 Create Before Destroy<br/>Zero downtime updates]
        PREVENT[🛡️ Prevent Destroy<br/>Protect critical resources]
        IGNORE[🙈 Ignore Changes<br/>Allow manual modifications]
    end

    subgraph "📊 State Transitions"
        PENDING[⏳ Pending<br/>Waiting for dependencies]
        IN_PROGRESS[🔄 In Progress<br/>Applying changes]
        TAINTED[🚨 Tainted<br/>Failed to create/update]
        COMPLETED[✅ Completed<br/>Successfully applied]
    end

    CREATE --> CBD
    UPDATE --> PREVENT
    REPLACE --> IGNORE

    CBD --> PENDING
    PREVENT --> IN_PROGRESS
    IGNORE --> TAINTED
    PENDING --> COMPLETED
    IN_PROGRESS --> COMPLETED
    TAINTED --> COMPLETED

    %% Apply styles
    class CREATE,UPDATE,REPLACE,DESTROY lifecycleClass
    class CBD,PREVENT,IGNORE createClass
    class PENDING,IN_PROGRESS,TAINTED,COMPLETED updateClass
```

## Terraform Cloud Architecture

```mermaid
graph TD
    %% Define styles
    classDef cloudClass fill:#e3f2fd,stroke:#1976d2,stroke-width:3px,color:#0d47a1
    classDef executionClass fill:#f3e5f5,stroke:#7b1fa2,stroke-width:2px,color:#4a148c
    classDef policyClass fill:#e8f5e8,stroke:#388e3c,stroke-width:2px,color:#1b5e20
    classDef registryClass fill:#fff3e0,stroke:#f57c00,stroke-width:2px,color:#e65100

    subgraph "☁️ Terraform Cloud"
        VCS[🔗 VCS Integration<br/>GitHub, GitLab, Bitbucket]
        REMOTE_RUNS[🚀 Remote Runs<br/>Plan & Apply execution]
        STATE_STORAGE[💾 Remote State<br/>Centralized storage]
        TEAM_COLLAB[👥 Team Collaboration<br/>Workspaces, permissions]
    end

    subgraph "⚙️ Execution Environment"
        CONTAINERS[🐳 Isolated Containers<br/>Per-run execution]
        PROVIDER_CACHE[📦 Provider Caching<br/>Faster runs]
        VARIABLE_SETS[🔧 Variable Sets<br/>Shared variables]
    end

    subgraph "🛡️ Governance"
        SENTINEL[⚖️ Sentinel Policies<br/>Policy as Code]
        COST_EST[💰 Cost Estimation<br/>Resource costing]
        APPROVALS[✅ Run Approvals<br/>Governance workflows]
    end

    subgraph "📚 Private Registry"
        MODULES[📦 Private Modules<br/>Team modules]
        PROVIDERS[🔌 Private Providers<br/>Custom providers]
        VERSIONING[🏷️ Version Control<br/>Semantic versioning]
    end

    VCS --> REMOTE_RUNS
    REMOTE_RUNS --> STATE_STORAGE
    STATE_STORAGE --> TEAM_COLLAB

    REMOTE_RUNS --> CONTAINERS
    CONTAINERS --> PROVIDER_CACHE
    PROVIDER_CACHE --> VARIABLE_SETS

    TEAM_COLLAB --> SENTINEL
    SENTINEL --> COST_EST
    COST_EST --> APPROVALS

    APPROVALS --> MODULES
    MODULES --> PROVIDERS
    PROVIDERS --> VERSIONING

    %% Apply styles
    class VCS,REMOTE_RUNS,STATE_STORAGE,TEAM_COLLAB cloudClass
    class CONTAINERS,PROVIDER_CACHE,VARIABLE_SETS executionClass
    class SENTINEL,COST_EST,APPROVALS policyClass
    class MODULES,PROVIDERS,VERSIONING registryClass
```

## Error Handling and Recovery

```mermaid
flowchart TD
    A[🚀 terraform apply] --> B{Execution}
    B --> C{❌ Error Occurs}
    B --> D{✅ Success}

    C --> E[🔍 Analyze Error]
    E --> F{Error Type}

    F -->|Configuration| G[📝 Fix Syntax/Config]
    F -->|Dependency| H[🔗 Fix Dependencies]
    F -->|Provider| I[🔌 Update Provider]
    F -->|State| J[💾 Fix State Issues]

    G --> K[🔄 Retry]
    H --> K
    I --> K
    J --> L[🛠️ State Commands]
    L --> K

    K --> M{Retry Success?}
    M -->|Yes| D
    M -->|No| N[🆘 Manual Intervention]
    N --> O[📞 Support/Expert Help]
    O --> P[✅ Resolution]

    D --> Q[💾 State Updated]
    P --> Q
```

## Performance Optimization

```mermaid
graph TD
    %% Define styles
    classDef perfClass fill:#e3f2fd,stroke:#1976d2,stroke-width:2px,color:#0d47a1
    classDef parallelClass fill:#f3e5f5,stroke:#7b1fa2,stroke-width:2px,color:#4a148c
    classDef cachingClass fill:#e8f5e8,stroke:#388e3c,stroke-width:2px,color:#1b5e20
    classDef targetingClass fill:#fff3e0,stroke:#f57c00,stroke-width:2px,color:#e65100

    subgraph "⚡ Performance Techniques"
        PARALLEL[🔀 Parallel Execution<br/>-parallelism=n]
        TARGETING[🎯 Resource Targeting<br/>-target flag]
        CACHING[📦 Provider Caching<br/>Faster subsequent runs]
        GRAPH_OPT[📊 Graph Optimization<br/>Dependency ordering]
    end

    subgraph "📈 Optimization Strategies"
        MODULE_DIV[📦 Module Division<br/>Independent modules]
        DATA_SOURCES[📊 Data Source Usage<br/>Read-only operations]
        COUNT_FOREACH[🔢 Efficient Loops<br/>count vs for_each]
        WORKSPACES[🏢 Workspace Isolation<br/>Environment separation]
    end

    subgraph "⏱️ Timing Improvements"
        PLAN_CACHE[💾 Plan Caching<br/>Reuse plans]
        INCREMENTAL[🔄 Incremental Updates<br/>Only changed resources]
        BATCHING[📦 Resource Batching<br/>Group similar resources]
    end

    PARALLEL --> MODULE_DIV
    TARGETING --> DATA_SOURCES
    CACHING --> COUNT_FOREACH
    GRAPH_OPT --> WORKSPACES

    MODULE_DIV --> PLAN_CACHE
    DATA_SOURCES --> INCREMENTAL
    COUNT_FOREACH --> BATCHING

    %% Apply styles
    class PARALLEL,TARGETING,CACHING,GRAPH_OPT perfClass
    class MODULE_DIV,DATA_SOURCES,COUNT_FOREACH,WORKSPACES parallelClass
    class PLAN_CACHE,INCREMENTAL,BATCHING cachingClass
```

## Summary

Terraform's visual architecture reveals a sophisticated, modular system designed for infrastructure automation at scale. The separation of core engine, providers, and state management enables consistent, version-controlled infrastructure across diverse platforms.

Key visual insights:
- **Declarative configuration**: HCL files define desired state
- **Provider abstraction**: Unified interface to cloud APIs
- **State management**: Critical for tracking and concurrency
- **Modular design**: Reusable components and environments
- **Workflow automation**: Plan-apply cycle with safety checks
- **Ecosystem integration**: CI/CD, cloud platforms, and tools

Understanding these visual relationships is crucial for effective Terraform usage and infrastructure management.
