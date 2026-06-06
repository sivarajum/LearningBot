# IAM - Visual Architecture

## Resource Hierarchy & Policy Inheritance

```mermaid
graph TD
    subgraph "Organization Level"
        A[Organization<br/>org-policies]
    end

    subgraph "Folder Level"
        B[Folder A<br/>folder-policies]
        C[Folder B<br/>folder-policies]
    end

    subgraph "Project Level"
        D[Project 1<br/>project-policies]
        E[Project 2<br/>project-policies]
        F[Project 3<br/>project-policies]
    end

    subgraph "Resource Level"
        G[VM Instance<br/>resource-policies]
        H[Storage Bucket<br/>resource-policies]
        I[BigQuery Dataset<br/>resource-policies]
    end

    A --> B
    A --> C
    B --> D
    B --> E
    C --> F
    D --> G
    D --> H
    E --> I

    style A fill:#e1f5fe
    style D fill:#fff3e0
    style G fill:#e8f5e8
```

## IAM Policy Structure

```mermaid
graph TD
    subgraph "IAM Policy"
        A[Policy Document]
    end

    subgraph "Bindings Array"
        B[Binding 1]
        C[Binding 2]
        D[Binding 3]
    end

    subgraph "Role Binding"
        E[Role:<br/>roles/storage.admin]
        F[Members Array]
    end

    subgraph "Members"
        G[user:alice@domain.com]
        H[serviceAccount:sa@project.iam.gserviceaccount.com]
        I[group:developers@domain.com]
        J[domain:domain.com]
    end

    A --> B
    A --> C
    A --> D
    B --> E
    E --> F
    F --> G
    F --> H
    F --> I
    F --> J

    style A fill:#e3f2fd
    style E fill:#fff3e0
    style G fill:#e8f5e8
```

## Role Types & Permissions

```mermaid
graph TD
    subgraph "Basic Roles"
        A[Owner<br/>Full control + IAM management]
        B[Editor<br/>Full control, no IAM]
        C[Viewer<br/>Read-only access]
    end

    subgraph "Predefined Roles"
        D[Service-specific<br/>Curated by Google]
        E[Job functions<br/>Common use cases]
        F[Primitive roles<br/>Broad permissions]
    end

    subgraph "Custom Roles"
        G[Organization-specific<br/>User-defined permissions]
        H[Fine-grained control<br/>Exact permissions needed]
        I[Compliance requirements<br/>Regulatory needs]
    end

    subgraph "Permissions"
        J[storage.buckets.*]
        K[compute.instances.*]
        L[bigquery.datasets.*]
        M[Custom permissions]
    end

    A --> D
    B --> E
    C --> F
    D --> J
    E --> K
    F --> L
    G --> M
    H --> M
    I --> M

    style A fill:#ffebee
    style D fill:#e3f2fd
    style G fill:#fff3e0
```

## Access Control Flow

```mermaid
sequenceDiagram
    participant U as User
    participant A as Authentication
    participant I as IAM
    participant R as Resource
    participant P as Permission Check

    U->>A: Request access with credentials
    A->>I: Validate identity
    I->>I: Check role bindings
    I->>P: Evaluate permissions
    P->>P: Check conditions
    P->>R: Allow/Deny access
    R->>U: Grant access or return error

    Note over I,P: Policy evaluation includes<br/>role permissions + conditions
```

## Service Account Architecture

```mermaid
graph TD
    subgraph "Service Account Types"
        A[User-managed<br/>Created by users]
        B[Google-managed<br/>Created by GCP services]
        C[Default compute<br/>Automatic for GCE]
    end

    subgraph "Key Management"
        D[Google-managed keys<br/>Auto-rotated]
        E[User-managed keys<br/>Manual rotation]
        F[Workload Identity<br/>Kubernetes integration]
    end

    subgraph "Authentication Methods"
        G[OAuth 2.0 tokens<br/>Short-lived tokens]
        H[Service account keys<br/>Long-lived credentials]
        I[Workload Identity<br/>Pod identity]
    end

    subgraph "Use Cases"
        J[Application authentication]
        K[GKE pod authentication]
        L[CI/CD pipeline access]
        M[Cross-project access]
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
    J --> M

    style A fill:#e3f2fd
    style D fill:#fff3e0
    style G fill:#e8f5e8
```

## Conditional Access Policies

```mermaid
graph TD
    subgraph "Role Binding"
        A[Role: roles/storage.admin]
        B[Members: user:alice@domain.com]
    end

    subgraph "Condition"
        C[title: "Business Hours Only"]
        D[expression: "request.time.getHours() >= 9 &&<br/>request.time.getHours() <= 17"]
    end

    subgraph "Context Attributes"
        E[request.time<br/>Timestamp of request]
        F[request.ip<br/>Source IP address]
        G[resource.name<br/>Resource identifier]
        H[resource.service<br/>GCP service name]
    end

    subgraph "Evaluation"
        I[Check condition]
        J[Allow/Deny access]
        K[Log decision]
    end

    A --> C
    B --> C
    C --> D
    D --> E
    D --> F
    D --> G
    D --> H
    E --> I
    F --> I
    G --> I
    H --> I
    I --> J
    J --> K

    style C fill:#ffebee
    style I fill:#e8f5e8
```

## Multi-Project Access Patterns

```mermaid
graph TD
    subgraph "Organization"
        A[Organization Root]
    end

    subgraph "Shared Projects"
        B[Project A<br/>Service: Storage]
        C[Project B<br/>Service: BigQuery]
        D[Project C<br/>Service: Compute]
    end

    subgraph "Team Projects"
        E[Dev Project<br/>Environment: Development]
        F[Test Project<br/>Environment: Testing]
        G[Prod Project<br/>Environment: Production]
    end

    subgraph "Access Patterns"
        H[Organization-level roles<br/>Cross-project access]
        I[Project-level roles<br/>Environment-specific access]
        J[Service accounts<br/>Application access]
        K[Groups<br/>Team-based access]
    end

    A --> B
    A --> C
    A --> D
    A --> E
    A --> F
    A --> G
    H --> A
    I --> E
    I --> F
    I --> G
    J --> B
    J --> C
    J --> D
    K --> E
    K --> F
    K --> G

    style A fill:#e3f2fd
    style E fill:#fff3e0
    style H fill:#e8f5e8
```

## Identity Federation

```mermaid
graph TD
    subgraph "External Identity Providers"
        A[Google Workspace]
        B[Active Directory]
        C[Azure AD]
        D[Okta]
        E[Custom SAML]
    end

    subgraph "Federation Layer"
        F[SAML 2.0]
        G[OIDC]
        H[LDAP]
        I[SCIM]
    end

    subgraph "Cloud Identity"
        J[User Accounts]
        K[Groups]
        L[Devices]
        M[Custom Attributes]
    end

    subgraph "GCP IAM"
        N[Google Accounts]
        O[Cloud Identity Users]
        P[External Users]
        Q[Service Accounts]
    end

    A --> F
    B --> H
    C --> G
    D --> F
    E --> F
    F --> J
    G --> K
    H --> L
    I --> M
    J --> N
    K --> O
    L --> P
    M --> Q

    style F fill:#e3f2fd
    style J fill:#fff3e0
    style N fill:#e8f5e8
```

## Audit & Compliance Monitoring

```mermaid
graph TD
    subgraph "Audit Sources"
        A[Admin Activity Logs<br/>IAM policy changes]
        B[Data Access Logs<br/>Resource access]
        C[System Event Logs<br/>GCP system events]
    end

    subgraph "Monitoring"
        D[Policy Changes<br/>Role binding modifications]
        E[Access Patterns<br/>Unusual access attempts]
        F[Privilege Escalation<br/>Permission changes]
        G[Compliance Violations<br/>Policy breaches]
    end

    subgraph "Analysis"
        H[IAM Recommender<br/>Access optimization]
        I[Policy Analyzer<br/>Effective permissions]
        J[Security Command Center<br/>Security insights]
        K[Custom Dashboards<br/>Access metrics]
    end

    subgraph "Response"
        L[Automated Alerts<br/>Policy violations]
        M[Access Reviews<br/>Manual verification]
        N[Remediation<br/>Policy corrections]
        O[Reporting<br/>Compliance reports]
    end

    A --> D
    B --> E
    C --> F
    D --> H
    E --> I
    F --> J
    G --> K
    H --> L
    I --> M
    J --> N
    K --> O

    style D fill:#ffebee
    style H fill:#e8f5e8
```

## DevOps Access Patterns

```mermaid
graph TD
    subgraph "Development Teams"
        A[Frontend Team]
        B[Backend Team]
        C[DevOps Team]
        D[Security Team]
    end

    subgraph "Environments"
        E[Development<br/>Project]
        F[Staging<br/>Project]
        G[Production<br/>Project]
    end

    subgraph "Access Levels"
        H[Full Access<br/>Development]
        I[Limited Access<br/>Staging]
        J[Read-Only + Approvals<br/>Production]
        K[Audit Access<br/>All Environments]
    end

    subgraph "Tools & Automation"
        L[CI/CD Pipelines<br/>Service accounts]
        M[Infrastructure as Code<br/>Terraform service accounts]
        N[Monitoring Tools<br/>Read-only service accounts]
        O[Security Scanners<br/>Limited service accounts]
    end

    A --> H
    B --> H
    C --> I
    D --> K
    H --> E
    I --> F
    J --> G
    K --> E
    K --> F
    K --> G
    L --> E
    L --> F
    L --> G
    M --> E
    M --> F
    M --> G
    N --> E
    N --> F
    N --> G
    O --> E
    O --> F
    O --> G

    style A fill:#e3f2fd
    style E fill:#fff3e0
    style H fill:#e8f5e8
```

## Zero Trust Architecture

```mermaid
graph TD
    subgraph "Trust Boundaries"
        A[Public Internet]
        B[Corporate Network]
        C[GCP Network]
        D[Service Mesh]
    end

    subgraph "Access Controls"
        E[Identity Verification<br/>MFA, Device Trust]
        F[Context Evaluation<br/>Time, Location, Device]
        G[Continuous Verification<br/>Ongoing assessment]
        H[Least Privilege<br/>Minimal access]
    end

    subgraph "Enforcement Points"
        I[VPN Gateway<br/>Network access]
        J[IAM Policies<br/>Resource access]
        K[VPC Service Controls<br/>Data access]
        L[Binary Authorization<br/>Code execution]
    end

    subgraph "Monitoring"
        M[Access Logging<br/>All access attempts]
        N[Anomaly Detection<br/>Unusual patterns]
        O[Automated Response<br/>Suspicious activity]
        P[Compliance Reporting<br/>Access reviews]
    end

    A --> E
    B --> F
    C --> G
    D --> H
    E --> I
    F --> J
    G --> K
    H --> L
    I --> M
    J --> N
    K --> O
    L --> P

    style E fill:#ffebee
    style I fill:#e8f5e8
```

## Incident Response Access

```mermaid
graph TD
    subgraph "Normal Operations"
        A[Standard Access<br/>Day-to-day permissions]
        B[Just-in-Time Access<br/>Temporary elevated access]
        C[Approval Workflows<br/>Manager approval required]
    end

    subgraph "Incident Detection"
        D[Monitoring Alerts<br/>Automated detection]
        E[Security Events<br/>Suspicious activity]
        F[Performance Issues<br/>System degradation]
    end

    subgraph "Incident Response"
        G[On-call Engineer<br/>Immediate access granted]
        H[Incident Commander<br/>Full access coordination]
        I[Subject Matter Experts<br/>Specialized access]
        J[Security Team<br/>Investigation access]
    end

    subgraph "Access Management"
        K[Break Glass Procedures<br/>Emergency access]
        L[Access Logging<br/>All actions recorded]
        M[Post-Incident Review<br/>Access audit]
        N[Access Revocation<br/>Automatic cleanup]
    end

    A --> D
    B --> E
    C --> F
    D --> G
    E --> H
    F --> I
    G --> K
    H --> L
    I --> M
    J --> N

    style D fill:#ffebee
    style G fill:#e8f5e8
```

## Cost Management & Optimization

```mermaid
graph TD
    subgraph "Access Analysis"
        A[Unused Roles<br/>90-day inactivity]
        B[Over-privileged Access<br/>Excessive permissions]
        C[Service Account Usage<br/>Active vs inactive]
        D[Policy Complexity<br/>Number of bindings]
    end

    subgraph "IAM Recommender"
        E[Role Recommendations<br/>Suggest appropriate roles]
        F[Remove Redundant Access<br/>Clean up unused bindings]
        G[Custom Role Optimization<br/>Consolidate permissions]
        H[Security Improvements<br/>Enhanced access controls]
    end

    subgraph "Optimization Actions"
        I[Policy Cleanup<br/>Remove unused bindings]
        J[Role Consolidation<br/>Use predefined roles]
        K[Just-in-Time Access<br/>Temporary permissions]
        L[Automated Approval<br/>Workflow-based access]
    end

    subgraph "Monitoring"
        M[Cost Impact<br/>Access-related costs]
        N[Compliance Status<br/>Policy adherence]
        O[Security Posture<br/>Access risk assessment]
        P[Audit Reports<br/>Access change history]
    end

    A --> E
    B --> F
    C --> G
    D --> H
    E --> I
    F --> J
    G --> K
    H --> L
    I --> M
    J --> N
    K --> O
    L --> P

    style E fill:#e3f2fd
    style I fill:#fff3e0
    style M fill:#e8f5e8
```

## Cross-Cloud Identity Management

```mermaid
graph TD
    subgraph "Cloud Identity"
        A[Central Identity Store]
        B[Unified User Management]
        C[Group-based Access]
        D[SSO Integration]
    end

    subgraph "Google Cloud"
        E[GCP IAM<br/>Roles & Permissions]
        F[Project Access<br/>Resource hierarchy]
        G[Service Accounts<br/>Application identity]
        H[Workload Identity<br/>Kubernetes integration]
    end

    subgraph "AWS"
        I[AWS IAM<br/>Users & Roles]
        J[Account Access<br/>Cross-account roles]
        K[EC2 Instance Profiles<br/>Compute identity]
        L[AWS Organizations<br/>Multi-account management]
    end

    subgraph "Azure"
        M[Azure AD<br/>Users & Groups]
        N[Subscription Access<br/>RBAC roles]
        O[Managed Identities<br/>Service principals]
        P[Azure AD Connect<br/>Directory sync]
    end

    A --> E
    B --> I
    C --> M
    D --> E
    D --> I
    D --> M
    E --> F
    I --> J
    M --> N
    F --> G
    J --> K
    N --> O
    G --> H
    K --> L
    O --> P

    style A fill:#bbdefb
    style E fill:#c8e6c9
    style I fill:#ffcdd2
    style M fill:#fff3e0
```

These diagrams illustrate the comprehensive access control architecture of IAM, showing how identities, roles, and policies work together to provide secure, governed access to Google Cloud resources across different organizational structures and use cases.
