# Load Balancing - Visual Architecture

## Load Balancer Types Overview

```mermaid
graph TD
    subgraph "Global Load Balancers"
        A[HTTP/HTTPS Load Balancer<br/>Layer 7 • Global • Content-based]
        B[SSL Proxy Load Balancer<br/>Layer 4 • Global • SSL termination]
        C[TCP Proxy Load Balancer<br/>Layer 4 • Global • TCP optimization]
    end

    subgraph "Regional Load Balancers"
        D[Internal Load Balancer<br/>Layer 4 • Regional • Private IP]
        E[Network Load Balancer<br/>Layer 4 • Regional • Pass-through]
        F[Internal HTTP/S Load Balancer<br/>Layer 7 • Regional • Internal traffic]
    end

    subgraph "Traffic Types"
        G[HTTP/HTTPS Traffic<br/>Web applications]
        H[SSL Traffic<br/>Encrypted TCP]
        I[TCP/UDP Traffic<br/>Any protocol]
        J[Internal Traffic<br/>VPC-only]
    end

    A --> G
    B --> H
    C --> I
    D --> J
    E --> I
    F --> G

    style A fill:#e1f5fe
    style D fill:#fff3e0
    style G fill:#e8f5e8
```

## HTTP Load Balancer Architecture

```mermaid
graph TD
    subgraph "Client"
        A[User Request<br/>client.example.com]
    end

    subgraph "Google Edge Network"
        B[Edge POP<br/>Anycast IP: 1.2.3.4]
        C[SSL Termination<br/>Certificate validation]
        D[Content-Based Routing<br/>URL maps & headers]
    end

    subgraph "Backend Services"
        E[Backend Service 1<br/>us-central1]
        F[Backend Service 2<br/>europe-west1]
        G[Backend Service 3<br/>asia-east1]
    end

    subgraph "Backends"
        H[Instance Group A<br/>us-central1-a]
        I[Instance Group B<br/>us-central1-b]
        J[Cloud Run Service<br/>us-central1]
    end

    A --> B
    B --> C
    C --> D
    D --> E
    D --> F
    D --> G
    E --> H
    E --> I
    F --> J

    style B fill:#e3f2fd
    style E fill:#fff3e0
    style H fill:#e8f5e8
```

## Global Load Balancing Flow

```mermaid
graph TD
    subgraph "Global Distribution"
        A[Client NYC]
        B[Client London]
        C[Client Tokyo]
    end

    subgraph "Edge Network"
        D[PoP NYC<br/>74.125.0.0/16]
        E[PoP London<br/>74.125.0.0/16]
        F[PoP Tokyo<br/>74.125.0.0/16]
    end

    subgraph "Regional Backends"
        G[us-east1<br/>Backend Service]
        H[europe-west1<br/>Backend Service]
        I[asia-northeast1<br/>Backend Service]
    end

    subgraph "Instance Groups"
        J[us-east1-a<br/>VMs]
        K[europe-west1-b<br/>VMs]
        L[asia-northeast1-c<br/>VMs]
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

    style D fill:#e3f2fd
    style G fill:#fff3e0
    style J fill:#e8f5e8
```

## Backend Configuration

```mermaid
graph TD
    subgraph "Backend Service"
        A[Backend Service<br/>Load balancing config]
    end

    subgraph "Backend Types"
        B[Instance Groups<br/>Compute Engine VMs]
        C[Network Endpoint Groups<br/>GKE services, Cloud Run]
        D[Serverless NEGs<br/>Cloud Functions, App Engine]
    end

    subgraph "Health Checks"
        E[HTTP Health Check<br/>/health endpoint]
        F[TCP Health Check<br/>Port connectivity]
        G[SSL Health Check<br/>Certificate validation]
    end

    subgraph "Load Balancing"
        H[Round Robin<br/>Equal distribution]
        I[Least Connections<br/>Connection count]
        J[IP Affinity<br/>Session stickiness]
    end

    A --> B
    A --> C
    A --> D
    B --> E
    C --> F
    D --> G
    E --> H
    F --> I
    G --> J

    style A fill:#e3f2fd
    style E fill:#fff3e0
    style H fill:#e8f5e8
```

## Content-Based Routing

```mermaid
graph TD
    subgraph "URL Map"
        A[URL Map<br/>Routing rules]
    end

    subgraph "Host Rules"
        B[api.example.com<br/>→ API Backend]
        C[web.example.com<br/>→ Web Backend]
        D[static.example.com<br/>→ CDN Backend]
    end

    subgraph "Path Rules"
        E[/api/*<br/>→ API Service]
        F[/web/*<br/>→ Web Service]
        G[/static/*<br/>→ Storage Service]
    end

    subgraph "Backend Services"
        H[API Backend<br/>Cloud Run]
        I[Web Backend<br/>GKE]
        J[Storage Backend<br/>Cloud Storage]
    end

    A --> B
    A --> C
    A --> D
    B --> E
    C --> F
    D --> G
    E --> H
    F --> I
    G --> J

    style A fill:#e3f2fd
    style E fill:#fff3e0
    style H fill:#e8f5e8
```

## Multi-Region Deployment

```mermaid
graph TD
    subgraph "Global Load Balancer"
        A[Global IP<br/>203.0.113.1]
    end

    subgraph "Region 1: us-central1"
        B[Backend Service<br/>us-central1]
        C[Instance Group A<br/>us-central1-a]
        D[Instance Group B<br/>us-central1-b]
    end

    subgraph "Region 2: europe-west1"
        E[Backend Service<br/>europe-west1]
        F[Instance Group C<br/>europe-west1-b]
        G[Instance Group D<br/>europe-west1-c]
    end

    subgraph "Region 3: asia-east1"
        H[Backend Service<br/>asia-east1]
        I[Instance Group E<br/>asia-east1-a]
        J[Instance Group F<br/>asia-east1-b]
    end

    subgraph "Traffic Distribution"
        K[Geo-based Routing<br/>Closest region]
        L[Load-based Routing<br/>Health & capacity]
        M[Failover Routing<br/>Unhealthy regions]
    end

    A --> B
    A --> E
    A --> H
    B --> C
    B --> D
    E --> F
    E --> G
    H --> I
    H --> J
    K --> A
    L --> A
    M --> A

    style A fill:#e3f2fd
    style B fill:#fff3e0
    style C fill:#e8f5e8
```

## Health Check Architecture

```mermaid
graph TD
    subgraph "Health Check Configuration"
        A[Health Check<br/>Protocol & endpoint]
    end

    subgraph "Check Types"
        B[HTTP/HTTPS<br/>Status code check]
        C[TCP<br/>Connection check]
        D[SSL<br/>Certificate check]
        E[UDP<br/>Response check]
    end

    subgraph "Check Execution"
        F[Regional Probes<br/>Distributed checks]
        G[Check Interval<br/>10-300 seconds]
        H[Timeout<br/>1-60 seconds]
        I[Healthy Threshold<br/>2-10 checks]
    end

    subgraph "Backend Status"
        J[Healthy<br/>Serve traffic]
        K[Unhealthy<br/>Drain connections]
        L[Unknown<br/>Limited traffic]
    end

    subgraph "Auto-Healing"
        M[Instance Recreation<br/>Managed instance groups]
        N[Pod Restart<br/>GKE deployments]
        O[Function Redeploy<br/>Cloud Run revisions]
    end

    A --> B
    A --> C
    A --> D
    A --> E
    B --> F
    C --> G
    D --> H
    E --> I
    F --> J
    G --> K
    H --> L
    I --> J
    J --> M
    K --> N
    L --> O

    style A fill:#e3f2fd
    style F fill:#fff3e0
    style J fill:#e8f5e8
```

## SSL Termination Flow

```mermaid
graph TD
    subgraph "Client"
        A[HTTPS Request<br/>TLS 1.3]
    end

    subgraph "Load Balancer"
        B[SSL Termination<br/>Certificate validation]
        C[SSL Policy<br/>TLS version control]
        D[Certificate Manager<br/>Auto-renewal]
    end

    subgraph "Backend Communication"
        E[HTTP to Backend<br/>Plain text]
        F[Health Checks<br/>SSL or plain]
        G[Session Reuse<br/>Connection pooling]
    end

    subgraph "Security Features"
        H[Cloud Armor<br/>WAF & DDoS]
        I[Identity-Aware Proxy<br/>User authentication]
        J[VPC Service Controls<br/>Network security]
    end

    A --> B
    B --> C
    B --> D
    C --> E
    D --> F
    E --> G
    B --> H
    H --> I
    I --> J

    style B fill:#ffebee
    style E fill:#e8f5e8
```

## Internal Load Balancing

```mermaid
graph TD
    subgraph "Internal Clients"
        A[VPC Network<br/>10.0.0.0/8]
        B[GKE Cluster<br/>Internal services]
        C[Compute Engine<br/>VM instances]
    end

    subgraph "Internal Load Balancer"
        D[Regional Internal LB<br/>10.128.0.100]
        E[Backend Service<br/>Internal only]
        F[Internal IP<br/>No external access]
    end

    subgraph "Backend Instances"
        G[Instance Group A<br/>us-central1-a]
        H[Instance Group B<br/>us-central1-b]
        I[GKE Services<br/>Internal endpoints]
    end

    subgraph "Traffic Flow"
        J[VPC Routing<br/>Internal routing]
        K[Firewall Rules<br/>Internal traffic only]
        L[Network Tags<br/>Backend identification]
    end

    A --> D
    B --> D
    C --> D
    D --> E
    E --> F
    F --> G
    F --> H
    F --> I
    D --> J
    J --> K
    K --> L

    style D fill:#e3f2fd
    style F fill:#fff3e0
    style G fill:#e8f5e8
```

## Traffic Splitting & A/B Testing

```mermaid
graph TD
    subgraph "Traffic Split"
        A[Load Balancer<br/>Traffic distribution]
    end

    subgraph "Backend Services"
        B[Production Backend<br/>90% traffic]
        C[Canary Backend<br/>10% traffic]
        D[Test Backend<br/>0% traffic - header based]
    end

    subgraph "Splitting Methods"
        E[Percentage Split<br/>90/10 distribution]
        F[Header-based<br/>x-canary: true]
        G[Cookie-based<br/>canary=test]
        H[IP-based<br/>Internal testing]
    end

    subgraph "Monitoring"
        I[Traffic Metrics<br/>Split ratios]
        J[Performance Comparison<br/>Latency, errors]
        K[A/B Test Results<br/>Conversion rates]
        L[Gradual Rollout<br/>Increase canary %]
    end

    A --> B
    A --> C
    A --> D
    B --> E
    C --> F
    D --> G
    E --> H
    E --> I
    F --> J
    G --> K
    H --> L

    style A fill:#e3f2fd
    style E fill:#fff3e0
    style I fill:#e8f5e8
```

## Auto-Scaling Integration

```mermaid
graph TD
    subgraph "Load Balancer"
        A[Traffic Monitoring<br/>Request rate, latency]
    end

    subgraph "Auto-Scaling Signals"
        B[CPU Utilization<br/>Target: 70%]
        C[Request Rate<br/>Target: 1000 req/min]
        D[Queue Length<br/>Target: 10 items]
        E[Custom Metrics<br/>Application-specific]
    end

    subgraph "Managed Instance Groups"
        F[Instance Group A<br/>us-central1-a]
        G[Instance Group B<br/>us-central1-b]
        H[Instance Group C<br/>us-central1-c]
    end

    subgraph "Scaling Actions"
        I[Scale Out<br/>Add instances]
        J[Scale In<br/>Remove instances]
        K[Regional Distribution<br/>Balance across zones]
        L[Cooldown Period<br/>Prevent thrashing]
    end

    A --> B
    A --> C
    A --> D
    A --> E
    B --> F
    C --> G
    D --> H
    E --> F
    F --> I
    G --> J
    H --> K
    I --> L
    J --> L
    K --> L

    style A fill:#e3f2fd
    style F fill:#fff3e0
    style I fill:#e8f5e8
```

## CDN Integration

```mermaid
graph TD
    subgraph "Client Request"
        A[Static Asset Request<br/>image.jpg]
    end

    subgraph "Cloud CDN"
        B[Edge Cache Check<br/>Global PoPs]
        C[Cache Hit<br/>Serve from edge]
        D[Cache Miss<br/>Forward to LB]
    end

    subgraph "Load Balancer"
        E[HTTP Load Balancer<br/>Content routing]
        F[Backend Selection<br/>Origin servers]
    end

    subgraph "Origin Backends"
        G[Cloud Storage<br/>Static content]
        H[Compute Engine<br/>Dynamic content]
        I[Cloud Run<br/>API responses]
    end

    subgraph "Cache Control"
        J[Cache Headers<br/>max-age, etag]
        K[Invalidation<br/>Purge cache]
        L[Custom Origins<br/>Backend buckets]
    end

    A --> B
    B --> C
    B --> D
    D --> E
    E --> F
    F --> G
    F --> H
    F --> I
    G --> J
    H --> K
    I --> L

    style B fill:#e3f2fd
    style E fill:#fff3e0
    style G fill:#e8f5e8
```

## Monitoring & Observability

```mermaid
graph TD
    subgraph "Load Balancer Metrics"
        A[Request Count<br/>Total requests]
        B[Response Time<br/>Latency percentiles]
        C[Error Rates<br/>4xx/5xx percentages]
        D[Throughput<br/>Requests per second]
    end

    subgraph "Backend Metrics"
        E[Healthy Backends<br/>Available capacity]
        F[Backend Latency<br/>End-to-end response time]
        G[Connection Count<br/>Active connections]
        H[Queue Depth<br/>Pending requests]
    end

    subgraph "Cloud Monitoring"
        I[Dashboards<br/>Real-time metrics]
        J[Alerting<br/>Threshold-based alerts]
        K[Anomaly Detection<br/>ML-powered insights]
        L[SLO Tracking<br/>Service level objectives]
    end

    subgraph "Logging"
        M[Access Logs<br/>Request/response details]
        N[Cloud Logging<br/>Centralized logging]
        O[Log Analytics<br/>BigQuery analysis]
        P[Security Events<br/>Attack detection]
    end

    A --> I
    B --> J
    C --> K
    D --> L
    E --> I
    F --> J
    G --> K
    H --> L
    I --> M
    J --> N
    K --> O
    L --> P

    style A fill:#e3f2fd
    style I fill:#fff3e0
    style M fill:#e8f5e8
```

## Disaster Recovery

```mermaid
graph TD
    subgraph "Primary Region"
        A[Primary Load Balancer<br/>us-central1]
        B[Active Backends<br/>us-central1 instances]
        C[Primary Database<br/>us-central1]
    end

    subgraph "Secondary Region"
        D[Secondary Load Balancer<br/>us-west1]
        E[Standby Backends<br/>us-west1 instances]
        F[Replica Database<br/>us-west1]
    end

    subgraph "Failover Mechanisms"
        G[Health Check Failure<br/>Automatic detection]
        H[DNS Update<br/>Route to secondary]
        I[Database Failover<br/>Promote replica]
        J[Data Synchronization<br/>Cross-region replication]
    end

    subgraph "Recovery Process"
        K[Failback Planning<br/>Return to primary]
        L[Data Consistency<br/>Verify replication]
        M[Load Testing<br/>Validate secondary]
        N[Gradual Cutover<br/>Minimize disruption]
    end

    A --> G
    B --> G
    C --> G
    G --> H
    H --> D
    H --> E
    H --> I
    I --> F
    G --> J
    J --> K
    K --> L
    L --> M
    M --> N

    style A fill:#ffebee
    style D fill:#e8f5e8
```

## Cost Optimization

```mermaid
graph TD
    subgraph "Traffic Analysis"
        A[Data Transfer Volume<br/>GB per month]
        B[Request Count<br/>Million requests]
        C[Peak Hours<br/>Traffic patterns]
        D[Regional Distribution<br/>Geographic spread]
    end

    subgraph "Optimization Strategies"
        E[CDN Integration<br/>Reduce LB traffic]
        F[Regional vs Global<br/>Right-size LB type]
        G[Backend Optimization<br/>Efficient instances]
        H[Caching Strategy<br/>Reduce dynamic requests]
    end

    subgraph "Cost Monitoring"
        I[Cost Breakdown<br/>By service/component]
        J[Budget Alerts<br/>Cost threshold warnings]
        K[Usage Analytics<br/>Identify optimization opportunities]
        L[Reserved Instances<br/>Compute cost reduction]
    end

    subgraph "Automation"
        M[Auto-scaling<br/>Match capacity to demand]
        N[Scheduled Scaling<br/>Off-hours reduction]
        O[Load Testing<br/>Capacity planning]
        P[Cost Optimization<br/>Automated recommendations]
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

These diagrams illustrate the comprehensive load balancing architecture in Google Cloud, showing how different load balancer types handle various traffic patterns, integrate with backend services, and provide high availability and scalability for applications.
