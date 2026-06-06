# Container Registry - Visual Architecture

## Registry Architecture

```mermaid
graph TB
    subgraph "Client Layer"
        A[Docker CLI]
        B[Cloud Build]
        C[Kubernetes]
        D[CI/CD Tools]
    end

    subgraph "Container Registry Service"
        E[Registry API]
        F[Metadata Service]
        G[Vulnerability Scanner]
        H[Binary Authorization]
    end

    subgraph "Storage Layer"
        I[Cloud Storage Buckets]
        J[Regional Storage]
        K[Global Replication]
    end

    subgraph "Security Layer"
        L[IAM Policies]
        M[VPC Service Controls]
        N[Audit Logging]
    end

    A --> E
    B --> E
    C --> E
    D --> E
    E --> F
    E --> G
    E --> H
    F --> I
    G --> I
    H --> I
    I --> J
    J --> K
    E --> L
    E --> M
    E --> N

    style E fill:#e1f5fe
    style I fill:#fff3e0
    style L fill:#e8f5e8
```

## Image Lifecycle Flow

```mermaid
sequenceDiagram
    participant Dev as Developer
    participant Build as Cloud Build
    participant Registry as Container Registry
    participant Scan as Vulnerability Scanner
    participant Deploy as Kubernetes

    Dev->>Build: Push Code
    Build->>Build: Build Image
    Build->>Registry: Push Image
    Registry->>Scan: Trigger Scan
    Scan->>Registry: Vulnerability Report
    Deploy->>Registry: Pull Image
    Registry->>Deploy: Serve Image
```

## Storage Architecture

```mermaid
graph TD
    subgraph "Global Registry (gcr.io)"
        A[US Multi-region]
        B[Images]
        C[Metadata]
    end

    subgraph "Regional Registry (region-gcr.io)"
        D[Single Region]
        E[Images]
        F[Metadata]
    end

    subgraph "Cloud Storage Backend"
        G[artifacts.project.appspot.com]
        H[Regional Buckets]
        I[Storage Classes]
    end

    A --> G
    D --> H
    B --> I
    E --> I
    C --> G
    F --> H

    style A fill:#e3f2fd
    style D fill:#fff3e0
    style G fill:#e8f5e8
```

## Security Architecture

```mermaid
graph TB
    subgraph "Access Control"
        A[IAM Roles]
        B[Service Accounts]
        C[Network Policies]
    end

    subgraph "Security Services"
        D[Vulnerability Scanner]
        E[Binary Authorization]
        F[Container Analysis]
    end

    subgraph "Monitoring"
        G[Audit Logs]
        H[Security Command Center]
        I[Cloud Monitoring]
    end

    subgraph "Enforcement"
        J[Admission Controllers]
        K[Policy Engine]
        L[Block/Audit Actions]
    end

    A --> D
    B --> E
    C --> F
    D --> G
    E --> H
    F --> I
    G --> J
    H --> K
    I --> L

    style D fill:#ffebee
    style E fill:#ffebee
    style J fill:#ffebee
```

## CI/CD Integration

```mermaid
graph LR
    subgraph "Source Control"
        A[Git Push]
        B[Pull Request]
    end

    subgraph "Build Phase"
        C[Cloud Build]
        D[Docker Build]
        E[Test Execution]
    end

    subgraph "Registry Phase"
        F[Push to GCR]
        G[Vulnerability Scan]
        H[Binary Authorization]
    end

    subgraph "Deploy Phase"
        I[GKE Deployment]
        J[Cloud Run]
        K[Cloud Functions]
    end

    A --> C
    B --> C
    C --> D
    D --> E
    E --> F
    F --> G
    G --> H
    H --> I
    H --> J
    H --> K

    style C fill:#e3f2fd
    style F fill:#fff3e0
    style I fill:#e8f5e8
```

## Vulnerability Scanning Workflow

```mermaid
graph TD
    A[Image Push] --> B[Trigger Scan]
    B --> C[Extract Packages]
    C --> D[Check Vulnerabilities]
    D --> E[Generate Report]
    E --> F{Severity Check}
    F -->|Critical| G[Block Deployment]
    F -->|High| H[Alert Team]
    F -->|Medium| I[Monitor]
    F -->|Low| J[Log Only]

    G --> K[Require Fix]
    H --> L[Plan Update]
    I --> M[Track Trends]
    J --> N[Archive]

    style B fill:#ffebee
    style G fill:#ffebee
```

## Binary Authorization Flow

```mermaid
graph TD
    A[Build Image] --> B[Generate Attestation]
    B --> C[Sign with Private Key]
    C --> D[Upload to Binary Auth]
    D --> E[Store Attestation]

    E --> F[Deploy Request]
    F --> G[Check Policy]
    G --> H{Attestation Valid?}
    H -->|Yes| I[Allow Deployment]
    H -->|No| J[Block Deployment]

    I --> K[Successful Deploy]
    J --> L[Require Attestation]

    style B fill:#e8f5e8
    style H fill:#fff3e0
    style J fill:#ffebee
```

## Multi-Region Architecture

```mermaid
graph TB
    subgraph "US-Central1"
        A1[Registry Service]
        B1[Storage Bucket]
        C1[Images]
    end

    subgraph "Europe-West1"
        A2[Registry Service]
        B2[Storage Bucket]
        C2[Images]
    end

    subgraph "Asia-Northeast1"
        A3[Registry Service]
        B3[Storage Bucket]
        C3[Images]
    end

    subgraph "Replication"
        D[Cross-Region Sync]
        E[Metadata Sync]
        F[Consistency Check]
    end

    A1 --> D
    A2 --> D
    A3 --> D
    B1 --> E
    B2 --> E
    B3 --> E
    D --> F
    E --> F

    style D fill:#e3f2fd
    style F fill:#fff3e0
```

## Image Layer Caching

```mermaid
graph TD
    A[Base Image Layer] --> B[App Layer 1]
    A --> C[App Layer 2]
    A --> D[App Layer 3]

    B --> E[Final Image A]
    C --> F[Final Image B]
    D --> G[Final Image C]

    H[Registry Cache] --> A
    H --> B
    H --> C
    H --> D

    I[Client Pull] --> H
    I --> E
    I --> F
    I --> G

    style A fill:#e8f5e8
    style H fill:#fff3e0
```

## Pull-Through Cache

```mermaid
graph TD
    A[Docker Hub] --> B[Pull-through Cache]
    C[Quay.io] --> B
    D[Harbor] --> B

    B --> E[Local Cache]
    E --> F[Security Scan]
    F --> G[Local Clients]

    G --> H[Fast Pulls]
    G --> I[Offline Access]
    G --> J[Security Compliance]

    style B fill:#e3f2fd
    style E fill:#fff3e0
    style F fill:#e8f5e8
```

## Cost Optimization

```mermaid
graph TD
    A[Image Storage] --> B{Access Frequency?}
    B -->|Daily| C[Standard Storage]
    B -->|Weekly| D[Nearline Storage]
    B -->|Monthly| E[Coldline Storage]
    B -->|Yearly| F[Archive Storage]

    G[Network Costs] --> H{Region Match?}
    H -->|Same Region| I[Low Cost]
    H -->|Cross Region| J[High Cost]

    K[Optimization] --> L[Layer Caching]
    K --> M[Image Optimization]
    K --> N[Lifecycle Policies]

    C --> O[Cost Monitoring]
    I --> O
    L --> O
    M --> O
    N --> O

    style O fill:#e3f2fd
```

## Migration Patterns

```mermaid
graph TD
    A[Docker Hub] --> B[Export Images]
    C[Quay.io] --> B
    D[Harbor] --> B

    B --> E[Import to GCR]
    E --> F[Update References]
    F --> G[Test Deployments]
    G --> H[Go Live]

    I[Gradual Migration] --> J[Mirror Images]
    J --> K[Update Some Apps]
    K --> L[Full Migration]

    H --> M[Cleanup Old Registry]
    L --> M

    style B fill:#fff3e0
    style E fill:#e3f2fd
    style J fill:#e8f5e8
```

## Monitoring Dashboard

```mermaid
graph TB
    subgraph "Usage Metrics"
        A[Pull Count]
        B[Push Count]
        C[Storage Used]
        D[Bandwidth]
    end

    subgraph "Performance Metrics"
        E[Pull Latency]
        F[Push Latency]
        G[Error Rate]
        H[Throughput]
    end

    subgraph "Security Metrics"
        I[Vulnerabilities]
        J[Policy Violations]
        K[Access Attempts]
        L[Audit Events]
    end

    subgraph "Cost Metrics"
        M[Storage Cost]
        N[Network Cost]
        O[Total Cost]
    end

    A --> P[Cloud Monitoring]
    B --> P
    C --> P
    D --> P
    E --> P
    F --> P
    G --> P
    H --> P
    I --> P
    J --> P
    K --> P
    L --> P
    M --> P
    N --> P
    O --> P

    P --> Q[Dashboards]
    P --> R[Alerts]
    P --> S[Reports]

    style P fill:#fff3e0
    style Q fill:#e3f2fd
```

## Compliance Architecture

```mermaid
graph TB
    subgraph "Data Protection"
        A[Encryption at Rest]
        B[Encryption in Transit]
        C[Data Residency]
    end

    subgraph "Access Control"
        D[IAM Policies]
        E[Audit Logging]
        F[Access Reviews]
    end

    subgraph "Compliance Checks"
        G[Vulnerability Scans]
        H[License Compliance]
        I[SBOM Generation]
    end

    subgraph "Reporting"
        J[Compliance Reports]
        K[Security Posture]
        L[Audit Trails]
    end

    A --> G
    B --> H
    C --> I
    D --> J
    E --> K
    F --> L

    style G fill:#ffebee
    style J fill:#e8f5e8
```

## High Availability Setup

```mermaid
graph TD
    subgraph "Primary Region"
        A[Registry Service]
        B[Storage Bucket]
        C[Active Images]
    end

    subgraph "Secondary Region"
        D[Registry Service]
        E[Storage Bucket]
        F[Replica Images]
    end

    subgraph "Failover"
        G[Health Checks]
        H[DNS Update]
        I[Traffic Switch]
    end

    subgraph "Disaster Recovery"
        J[Backup Images]
        K[Restore Process]
        L[Validation]
    end

    A --> G
    D --> G
    G --> H
    H --> I
    B --> J
    E --> J
    J --> K
    K --> L

    style A fill:#e3f2fd
    style G fill:#fff3e0
    style J fill:#e8f5e8
```

## Integration Patterns

```mermaid
graph TD
    subgraph "GCP Services"
        A[Cloud Build]
        B[GKE]
        C[Cloud Run]
        D[Cloud Functions]
        E[AI Platform]
    end

    subgraph "Third Party"
        F[Jenkins]
        G[GitLab CI]
        H[CircleCI]
        I[ArgoCD]
        J[Tekton]
    end

    subgraph "Container Registry"
        K[Image Storage]
        L[Vulnerability Scan]
        M[Access Control]
        N[Audit Logging]
    end

    A --> K
    B --> K
    C --> K
    D --> K
    E --> K
    F --> K
    G --> K
    H --> K
    I --> K
    J --> K

    K --> L
    K --> M
    K --> N

    style K fill:#bbdefb
    style A fill:#c8e6c9
    style F fill:#ffcdd2
```

## Image Lifecycle Management

```mermaid
graph LR
    A[Image Created] --> B[Push to Registry]
    B --> C[Vulnerability Scan]
    C --> D{Approved?}
    D -->|Yes| E[Tag as Latest]
    D -->|No| F[Quarantine]

    E --> G[Deploy to Staging]
    G --> H{Staging Tests Pass?}
    H -->|Yes| I[Promote to Prod]
    H -->|No| J[Fix Issues]

    I --> K[Monitor Production]
    K --> L{Performance Good?}
    L -->|Yes| M[Keep Active]
    L -->|No| N[Rollback]

    F --> O[Fix Vulnerabilities]
    O --> P[Rescan]
    P --> Q{Reapproved?}
    Q -->|Yes| R[Release Fixed Image]
    Q -->|No| S[Archive Image]

    style C fill:#ffebee
    style D fill:#fff3e0
    style H fill:#e8f5e8
```

## Network Security

```mermaid
graph TB
    subgraph "External Access"
        A[Internet]
        B[VPN]
        C[Interconnect]
    end

    subgraph "VPC Service Controls"
        D[Service Perimeter]
        E[Access Levels]
        F[Ingress Rules]
        G[Egress Rules]
    end

    subgraph "Registry Access"
        H[Private Google Access]
        I[VPC Peering]
        J[Private Service Connect]
    end

    subgraph "Security Monitoring"
        K[Firewall Logs]
        L[VPC Flow Logs]
        M[Audit Logs]
    end

    A --> D
    B --> E
    C --> F
    D --> H
    E --> I
    F --> J
    H --> K
    I --> L
    J --> M

    style D fill:#ffebee
    style H fill:#e8f5e8
```

These diagrams illustrate the comprehensive architecture of Container Registry, showing its integration with various GCP services, security features, performance optimizations, and operational workflows. The visual representations help understand how Container Registry fits into the broader container ecosystem and DevOps pipelines.
