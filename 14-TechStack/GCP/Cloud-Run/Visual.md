# Cloud Run Visual Architecture and Diagrams

## Overview

This document provides visual representations of Cloud Run architecture, scaling patterns, and integration flows using Mermaid diagrams.

## Core Architecture

### Cloud Run Service Architecture

```mermaid
graph TB
    subgraph "Client Layer"
        HTTP[HTTP/HTTPS Clients]
        gRPC[gRPC Clients]
        Mobile[Mobile Apps]
        Web[Web Applications]
        API[API Gateways]
    end

    subgraph "Global Load Balancer"
        GLB[Global Load Balancer<br/>Anycast IP]
        SSL[SSL Termination<br/>Managed Certificates]
        CDN[Cloud CDN<br/>Edge Caching]
    end

    subgraph "Cloud Run Control Plane"
        ControlPlane[Control Plane<br/>Service Management]
        Autoscaler[Autoscaler<br/>Instance Management]
        Scheduler[Scheduler<br/>Resource Allocation]
        Config[Configuration<br/>Service Settings]
    end

    subgraph "Container Runtime"
        Container1[Container Instance 1<br/>Running Application]
        Container2[Container Instance 2<br/>Running Application]
        Container3[Container Instance 3<br/>Running Application]
        Scale[Auto-scaling<br/>0 to N instances]
    end

    subgraph "Data & Integration"
        CloudSQL[Cloud SQL<br/>Databases]
        Firestore[Firestore<br/>NoSQL Database]
        CloudStorage[Cloud Storage<br/>Object Storage]
        PubSub[Pub/Sub<br/>Event Streaming]
        BigQuery[BigQuery<br/>Data Analytics]
    end

    subgraph "Supporting Services"
        IAM[IAM<br/>Access Control]
        VPC[VPC Network<br/>Private Networking]
        SecretManager[Secret Manager<br/>Secrets]
        Monitoring[Cloud Monitoring<br/>Observability]
    end

    HTTP --> GLB
    gRPC --> GLB
    Mobile --> GLB
    Web --> GLB
    API --> GLB

    GLB --> SSL
    SSL --> CDN
    CDN --> ControlPlane

    ControlPlane --> Autoscaler
    ControlPlane --> Scheduler
    ControlPlane --> Config

    Autoscaler --> Container1
    Autoscaler --> Container2
    Autoscaler --> Container3
    Scheduler --> Scale

    Container1 --> CloudSQL
    Container2 --> Firestore
    Container3 --> CloudStorage
    Container1 --> PubSub
    Container2 --> BigQuery

    ControlPlane --> IAM
    Container1 --> VPC
    Container2 --> SecretManager
    Container3 --> Monitoring

    style HTTP fill:#e3f2fd
    style GLB fill:#fff3e0
    style ControlPlane fill:#e8f5e8
```

### Request Flow Architecture

```mermaid
sequenceDiagram
    participant Client
    participant GLB as Global Load Balancer
    participant ControlPlane as Cloud Run Control Plane
    participant Autoscaler
    participant Container as Container Instance
    participant Backend as Backend Services

    Client->>GLB: HTTP Request
    GLB->>ControlPlane: Route Request
    ControlPlane->>Autoscaler: Check Capacity
    Autoscaler->>Autoscaler: Scale Instances if needed
    Autoscaler->>Container: Forward Request
    Container->>Container: Process Request
    Container->>Backend: Call Backend Services
    Backend->>Container: Return Response
    Container->>GLB: Send Response
    GLB->>Client: HTTP Response

    style Client fill:#e3f2fd
    style GLB fill:#fff3e0
    style ControlPlane fill:#e8f5e8
    style Autoscaler fill:#e3f2fd
    style Container fill:#fff3e0
    style Backend fill:#e8f5e8
```

## Scaling Patterns

### Autoscaling Architecture

```mermaid
graph TD
    subgraph "Traffic Sources"
        WebTraffic[Web Traffic<br/>HTTP Requests]
        APITraffic[API Traffic<br/>REST/gRPC Calls]
        EventTraffic[Event Traffic<br/>Pub/Sub Messages]
        Scheduled[Scheduled Traffic<br/>Cloud Scheduler]
    end

    subgraph "Load Balancing"
        GlobalLB[Global Load Balancer<br/>Traffic Distribution]
        RegionalLB[Regional Load Balancer<br/>Failover]
    end

    subgraph "Scaling Engine"
        RequestQueue[Request Queue<br/>Incoming Requests]
        ConcurrencyCheck[Concurrency Check<br/>Per Instance]
        CPUCheck[CPU Utilization<br/>Target Threshold]
        CustomMetrics[Custom Metrics<br/>Application Metrics]
    end

    subgraph "Instance Management"
        ScaleDecision[Scale Decision<br/>Add/Remove Instances]
        InstancePool[Instance Pool<br/>Running Containers]
        WarmPool[Warm Pool<br/>Pre-warmed Instances]
        ColdPool[Cold Pool<br/>Scale-to-Zero]
    end

    subgraph "Resource Limits"
        MaxInstances[Max Instances<br/>Service Limit]
        RegionalQuota[Regional Quota<br/>Platform Limit]
        ResourceQuota[Resource Quota<br/>CPU/Memory]
    end

    WebTraffic --> GlobalLB
    APITraffic --> GlobalLB
    EventTraffic --> GlobalLB
    Scheduled --> GlobalLB

    GlobalLB --> RegionalLB
    RegionalLB --> RequestQueue

    RequestQueue --> ConcurrencyCheck
    RequestQueue --> CPUCheck
    RequestQueue --> CustomMetrics

    ConcurrencyCheck --> ScaleDecision
    CPUCheck --> ScaleDecision
    CustomMetrics --> ScaleDecision

    ScaleDecision --> InstancePool
    ScaleDecision --> WarmPool
    ScaleDecision --> ColdPool

    InstancePool --> MaxInstances
    WarmPool --> RegionalQuota
    ColdPool --> ResourceQuota

    style WebTraffic fill:#e3f2fd
    style GlobalLB fill:#fff3e0
    style RequestQueue fill:#e8f5e8
    style ScaleDecision fill:#e3f2fd
    style MaxInstances fill:#fff3e0
```

### Scale-to-Zero Flow

```mermaid
stateDiagram-v2
    [*] --> Active: Traffic Detected
    Active --> Scaling: Load Increases
    Scaling --> Scaled: Target Instances Reached
    Scaled --> Active: Steady State

    Active --> Idle: No Traffic
    Idle --> Cooldown: Cooldown Period
    Cooldown --> Shutdown: Timeout Expired
    Shutdown --> [*]: Scale-to-Zero

    note right of Idle
        Keep-alive period
        Configurable timeout
        Resource cleanup
    end note

    note right of Shutdown
        Container termination
        Resource release
        Cold start preparation
    end note

    style Active fill:#e3f2fd
    style Scaling fill:#fff3e0
    style Scaled fill:#e8f5e8
    style Idle fill:#e3f2fd
    style Cooldown fill:#fff3e0
    style Shutdown fill:#e8f5e8
```

## Deployment Patterns

### Rolling Deployment Architecture

```mermaid
graph TD
    subgraph "Deployment Sources"
        Git[Git Repository<br/>Source Code]
        ContainerRegistry[Container Registry<br/>Built Images]
        CloudBuild[Cloud Build<br/>CI/CD Pipeline]
    end

    subgraph "Deployment Strategy"
        Revision1[Revision 1<br/>Current Production<br/>80% Traffic]
        Revision2[Revision 2<br/>New Version<br/>20% Traffic]
        TrafficSplit[Traffic Split<br/>Canary Deployment]
    end

    subgraph "Validation"
        HealthCheck[Health Checks<br/>Startup/Liveness]
        Metrics[Performance Metrics<br/>Latency, Errors]
        Monitoring[Monitoring<br/>Custom Dashboards]
    end

    subgraph "Promotion"
        GradualRollout[Gradual Rollout<br/>Increase Traffic]
        FullPromotion[Full Promotion<br/>100% Traffic]
        Rollback[Rollback<br/>Revert to Previous]
    end

    Git --> CloudBuild
    CloudBuild --> ContainerRegistry

    ContainerRegistry --> Revision1
    ContainerRegistry --> Revision2

    Revision1 --> TrafficSplit
    Revision2 --> TrafficSplit

    TrafficSplit --> HealthCheck
    HealthCheck --> Metrics
    Metrics --> Monitoring

    Monitoring --> GradualRollout
    GradualRollout --> FullPromotion
    Monitoring --> Rollback

    style Git fill:#e3f2fd
    style CloudBuild fill:#fff3e0
    style Revision1 fill:#e8f5e8
    style HealthCheck fill:#e3f2fd
    style GradualRollout fill:#fff3e0
```

### Blue-Green Deployment

```mermaid
graph TD
    subgraph "Environment A (Blue)"
        BlueService[Service v1<br/>Current Production]
        BlueTraffic[Traffic 100%<br/>Active Environment]
    end

    subgraph "Environment B (Green)"
        GreenService[Service v2<br/>New Version]
        GreenTraffic[Traffic 0%<br/>Staging Environment]
    end

    subgraph "Traffic Management"
        LoadBalancer[Load Balancer<br/>Traffic Router]
        DNS[DNS Switch<br/>Environment Switch]
        Validation[Validation Tests<br/>Smoke Tests]
    end

    subgraph "Switch Process"
        DeployGreen[Deploy to Green<br/>Full Deployment]
        TestGreen[Test Green Environment<br/>Integration Tests]
        SwitchTraffic[Switch Traffic<br/>DNS Update]
        MonitorGreen[Monitor Green<br/>Performance]
    end

    BlueService --> BlueTraffic
    GreenService --> GreenTraffic

    BlueTraffic --> LoadBalancer
    GreenTraffic --> LoadBalancer

    LoadBalancer --> DNS

    DNS --> DeployGreen
    DeployGreen --> TestGreen
    TestGreen --> SwitchTraffic
    SwitchTraffic --> MonitorGreen

    style BlueService fill:#e3f2fd
    style GreenService fill:#fff3e0
    style LoadBalancer fill:#e8f5e8
    style DeployGreen fill:#e3f2fd
    style TestGreen fill:#fff3e0
```

## Integration Patterns

### Event-Driven Architecture

```mermaid
graph TD
    subgraph "Event Sources"
        CloudStorage[Cloud Storage<br/>Object Events]
        PubSub[Pub/Sub<br/>Message Events]
        Firestore[Firestore<br/>Document Events]
        Firebase[Firebase<br/>Auth Events]
        CloudBuild[Cloud Build<br/>Build Events]
    end

    subgraph "Eventarc"
        EventIngestion[Event Ingestion<br/>Eventarc]
        EventFiltering[Event Filtering<br/>Rules Engine]
        EventRouting[Event Routing<br/>Target Selection]
    end

    subgraph "Cloud Run Services"
        Service1[Service 1<br/>Image Processing]
        Service2[Service 2<br/>Data Processing]
        Service3[Service 3<br/>Notification]
        Job1[Cloud Run Job<br/>Batch Processing]
    end

    subgraph "Processing Flow"
        AsyncProcessing[Asynchronous Processing<br/>Non-blocking]
        ParallelProcessing[Parallel Processing<br/>Multiple Instances]
        SequentialProcessing[Sequential Processing<br/>Chained Services]
    end

    CloudStorage --> EventIngestion
    PubSub --> EventIngestion
    Firestore --> EventIngestion
    Firebase --> EventIngestion
    CloudBuild --> EventIngestion

    EventIngestion --> EventFiltering
    EventFiltering --> EventRouting

    EventRouting --> Service1
    EventRouting --> Service2
    EventRouting --> Service3
    EventRouting --> Job1

    Service1 --> AsyncProcessing
    Service2 --> ParallelProcessing
    Service3 --> SequentialProcessing
    Job1 --> AsyncProcessing

    style CloudStorage fill:#e3f2fd
    style EventIngestion fill:#fff3e0
    style Service1 fill:#e8f5e8
    style AsyncProcessing fill:#e3f2fd
```

### Service Mesh Integration

```mermaid
graph TD
    subgraph "Service Mesh"
        Istio[Istio Service Mesh<br/>Traffic Management]
        Envoy[Envoy Proxy<br/>Sidecar Pattern]
        ControlPlane[Istio Control Plane<br/>Configuration]
    end

    subgraph "Cloud Run Services"
        Frontend[Frontend Service<br/>Web Interface]
        API[API Gateway Service<br/>Request Routing]
        Backend[Backend Service<br/>Business Logic]
        Worker[Worker Service<br/>Background Tasks]
    end

    subgraph "Traffic Policies"
        Routing[Traffic Routing<br/>Canary, Blue-Green]
        LoadBalancing[Load Balancing<br/>Round Robin, Least Loaded]
        CircuitBreaker[Circuit Breaker<br/>Fault Tolerance]
        Retry[Retry Logic<br/>Transient Failures]
    end

    subgraph "Security Policies"
        Authentication[Authentication<br/>JWT, API Keys]
        Authorization[Authorization<br/>RBAC, Policies]
        Encryption[Encryption<br/>mTLS, TLS]
        RateLimiting[Rate Limiting<br/>Request Throttling]
    end

    subgraph "Observability"
        Tracing[Distributed Tracing<br/>Request Flow]
        Metrics[Service Metrics<br/>Performance]
        Logging[Structured Logging<br/>Request Logs]
    end

    Istio --> Envoy
    Envoy --> ControlPlane

    Frontend --> Istio
    API --> Istio
    Backend --> Istio
    Worker --> Istio

    Istio --> Routing
    Istio --> LoadBalancing
    Istio --> CircuitBreaker
    Istio --> Retry

    Istio --> Authentication
    Istio --> Authorization
    Istio --> Encryption
    Istio --> RateLimiting

    Istio --> Tracing
    Istio --> Metrics
    Istio --> Logging

    style Istio fill:#e3f2fd
    style Frontend fill:#fff3e0
    style Routing fill:#e8f5e8
    style Authentication fill:#e3f2fd
    style Tracing fill:#fff3e0
```

## Networking Architecture

### VPC Integration

```mermaid
graph TD
    subgraph "Cloud Run Service"
        Container[Container Instance<br/>Application]
        VPCConnector[VPC Connector<br/>Private Networking]
    end

    subgraph "VPC Network"
        Subnet1[Subnet 1<br/>Private Subnet]
        Subnet2[Subnet 2<br/>Private Subnet]
        Firewall[Firewall Rules<br/>Network Security]
    end

    subgraph "Private Services"
        CloudSQL[Cloud SQL<br/>Private IP]
        Redis[Memorystore Redis<br/>Private IP]
        GKE[GKE Clusters<br/>Private Cluster]
        ComputeEngine[Compute Engine<br/>Private VM]
    end

    subgraph "Private Google APIs"
        PrivateAPIs[Private Google APIs<br/>VPC Access]
        ServiceNetworking[Service Networking<br/>Private Connections]
    end

    Container --> VPCConnector
    VPCConnector --> Subnet1
    VPCConnector --> Subnet2

    Subnet1 --> Firewall
    Subnet2 --> Firewall

    Firewall --> CloudSQL
    Firewall --> Redis
    Firewall --> GKE
    Firewall --> ComputeEngine

    Firewall --> PrivateAPIs
    PrivateAPIs --> ServiceNetworking

    style Container fill:#e3f2fd
    style VPCConnector fill:#fff3e0
    style Subnet1 fill:#e8f5e8
    style CloudSQL fill:#e3f2fd
    style PrivateAPIs fill:#fff3e0
```

### Multi-Region Deployment

```mermaid
graph TD
    subgraph "Region 1 (us-central1)"
        Service1[Cloud Run Service<br/>Active]
        LB1[Regional Load Balancer<br/>Primary]
        DNS1[Cloud DNS<br/>Global DNS]
    end

    subgraph "Region 2 (us-east1)"
        Service2[Cloud Run Service<br/>Standby]
        LB2[Regional Load Balancer<br/>Secondary]
    end

    subgraph "Region 3 (europe-west1)"
        Service3[Cloud Run Service<br/>Standby]
        LB3[Regional Load Balancer<br/>Tertiary]
    end

    subgraph "Global Load Balancing"
        GlobalLB[Global Load Balancer<br/>Anycast IP]
        HealthChecks[Health Checks<br/>Global Monitoring]
        Failover[Automatic Failover<br/>DNS Updates]
    end

    subgraph "Traffic Distribution"
        GeoRouting[Geo-based Routing<br/>Latency-based]
        Weighted[Weighted Distribution<br/>Load Distribution]
        Anycast[Anycast Routing<br/>Optimal Path]
    end

    Service1 --> LB1
    Service2 --> LB2
    Service3 --> LB3

    LB1 --> DNS1
    LB2 --> DNS1
    LB3 --> DNS1

    DNS1 --> GlobalLB

    GlobalLB --> HealthChecks
    HealthChecks --> Failover

    Failover --> GeoRouting
    Failover --> Weighted
    Failover --> Anycast

    style Service1 fill:#e3f2fd
    style LB1 fill:#fff3e0
    style GlobalLB fill:#e8f5e8
    style HealthChecks fill:#e3f2fd
    style GeoRouting fill:#fff3e0
```

## Security Architecture

### Identity and Access Management

```mermaid
graph TD
    subgraph "Authentication"
        IAM[IAM<br/>Identity Management]
        ServiceAccounts[Service Accounts<br/>Application Identity]
        WorkloadIdentity[Workload Identity<br/>Kubernetes Integration]
    end

    subgraph "Authorization"
        IAMRoles[IAM Roles<br/>Permissions]
        PrivateServices[Private Services<br/>IAM-based Access]
        VPCServiceControls[VPC Service Controls<br/>Context-aware Access]
    end

    subgraph "Cloud Run Service"
        PublicService[Public Service<br/>No Authentication]
        PrivateService[Private Service<br/>IAM Required]
        InternalService[Internal Service<br/>VPC-only]
    end

    subgraph "Security Policies"
        BinaryAuth[Binary Authorization<br/>Container Security]
        OrgPolicies[Organization Policies<br/>Compliance]
        AccessPolicies[Access Policies<br/>Context-aware]
    end

    IAM --> ServiceAccounts
    IAM --> WorkloadIdentity

    ServiceAccounts --> IAMRoles
    WorkloadIdentity --> IAMRoles

    IAMRoles --> PrivateServices
    IAMRoles --> VPCServiceControls

    PublicService --> IAM
    PrivateService --> IAMRoles
    InternalService --> VPCServiceControls

    BinaryAuth --> PublicService
    OrgPolicies --> PrivateService
    AccessPolicies --> InternalService

    style IAM fill:#e3f2fd
    style IAMRoles fill:#fff3e0
    style PublicService fill:#e8f5e8
    style BinaryAuth fill:#e3f2fd
```

### Data Protection

```mermaid
graph TD
    subgraph "Data in Transit"
        TLS[TLS 1.3<br/>HTTPS Encryption]
        mTLS[Mutual TLS<br/>Client Authentication]
        VPN[VPN Tunnels<br/>Private Networks]
    end

    subgraph "Data at Rest"
        CMEK[Customer-Managed Keys<br/>Cloud KMS]
        CSEK[Customer-Supplied Keys<br/>Application Keys]
        StorageEncryption[Storage Encryption<br/>Persistent Data]
    end

    subgraph "Secret Management"
        SecretManager[Secret Manager<br/>Runtime Secrets]
        EnvironmentVars[Environment Variables<br/>Configuration]
        ConfigMaps[Config Maps<br/>Application Config]
    end

    subgraph "Compliance"
        AuditLogs[Audit Logs<br/>Access Tracking]
        DataLossPrevention[DLP<br/>Sensitive Data]
        EncryptionCompliance[Encryption Compliance<br/>Regulatory]
    end

    TLS --> mTLS
    mTLS --> VPN

    CMEK --> CSEK
    CSEK --> StorageEncryption

    SecretManager --> EnvironmentVars
    EnvironmentVars --> ConfigMaps

    AuditLogs --> DataLossPrevention
    DataLossPrevention --> EncryptionCompliance

    style TLS fill:#e3f2fd
    style CMEK fill:#fff3e0
    style SecretManager fill:#e8f5e8
    style AuditLogs fill:#e3f2fd
```

## Performance Optimization

### Cold Start Optimization

```mermaid
graph TD
    subgraph "Cold Start Causes"
        ScaleToZero[Scale-to-Zero<br/>No Active Instances]
        NewRevision[New Revision<br/>Container Update]
        ResourceLimits[Resource Limits<br/>Quota Exceeded]
        HealthCheckFailure[Health Check Failure<br/>Container Restart]
    end

    subgraph "Optimization Strategies"
        ContainerSize[Minimize Container Size<br/>Smaller Images]
        StartupTime[Optimize Startup Time<br/>Fast Initialization]
        WarmPool[Keep Warm Pool<br/>Pre-warmed Instances]
        RegionalDeployment[Regional Deployment<br/>Closer to Users]
    end

    subgraph "Monitoring"
        ColdStartMetrics[Cold Start Metrics<br/>Duration Tracking]
        StartupProbes[Startup Probes<br/>Readiness Checks]
        PerformanceMonitoring[Performance Monitoring<br/>Latency Tracking]
    end

    subgraph "Mitigation Techniques"
        ScheduledKeepAlive[Scheduled Keep-alive<br/>Cloud Scheduler]
        PreWarmInstances[Pre-warm Instances<br/>Minimum Instances]
        CDN[Caching Layer<br/>CDN Integration]
        EdgeComputing[Edge Computing<br/>Cloudflare Workers]
    end

    ScaleToZero --> ContainerSize
    NewRevision --> StartupTime
    ResourceLimits --> WarmPool
    HealthCheckFailure --> RegionalDeployment

    ContainerSize --> ColdStartMetrics
    StartupTime --> StartupProbes
    WarmPool --> PerformanceMonitoring
    RegionalDeployment --> PerformanceMonitoring

    ColdStartMetrics --> ScheduledKeepAlive
    StartupProbes --> PreWarmInstances
    PerformanceMonitoring --> CDN
    PerformanceMonitoring --> EdgeComputing

    style ScaleToZero fill:#e3f2fd
    style ContainerSize fill:#fff3e0
    style ColdStartMetrics fill:#e8f5e8
    style ScheduledKeepAlive fill:#e3f2fd
```

### Resource Optimization

```mermaid
graph TD
    subgraph "Resource Allocation"
        CPUAllocation[CPU Allocation<br/>vCPU Limits]
        MemoryAllocation[Memory Allocation<br/>GB Limits]
        Concurrency[Concurrency<br/>Requests per Instance]
        Timeout[Request Timeout<br/>Maximum Duration]
    end

    subgraph "Cost Optimization"
        PayPerUse[Pay-per-Use<br/>CPU/GB-seconds]
        IdleInstances[Minimize Idle Instances<br/>Efficient Scaling]
        ResourceRightsizing[Resource Rightsizing<br/>Optimal Allocation]
        RegionalPricing[Regional Pricing<br/>Cost Differences]
    end

    subgraph "Performance Monitoring"
        UtilizationMetrics[Utilization Metrics<br/>CPU/Memory Usage]
        LatencyMetrics[Latency Metrics<br/>Response Time]
        ThroughputMetrics[Throughput Metrics<br/>Requests/Second]
        ErrorMetrics[Error Metrics<br/>Failure Rates]
    end

    subgraph "Optimization Actions"
        AutoScaling[Auto-scaling<br/>Demand-based]
        ResourceTuning[Resource Tuning<br/>Configuration]
        LoadBalancing[Load Balancing<br/>Traffic Distribution]
        Caching[Caching Strategies<br/>Response Caching]
    end

    CPUAllocation --> PayPerUse
    MemoryAllocation --> IdleInstances
    Concurrency --> ResourceRightsizing
    Timeout --> RegionalPricing

    PayPerUse --> UtilizationMetrics
    IdleInstances --> LatencyMetrics
    ResourceRightsizing --> ThroughputMetrics
    RegionalPricing --> ErrorMetrics

    UtilizationMetrics --> AutoScaling
    LatencyMetrics --> ResourceTuning
    ThroughputMetrics --> LoadBalancing
    ErrorMetrics --> Caching

    style CPUAllocation fill:#e3f2fd
    style PayPerUse fill:#fff3e0
    style UtilizationMetrics fill:#e8f5e8
    style AutoScaling fill:#e3f2fd
```

## Monitoring and Observability

### Cloud Run Monitoring Dashboard

```mermaid
graph TD
    subgraph "System Metrics"
        RequestCount[Request Count<br/>Total Requests]
        RequestLatency[Request Latency<br/>P50, P95, P99]
        InstanceCount[Instance Count<br/>Active Instances]
        CPUUtilization[CPU Utilization<br/>Core Usage]
        MemoryUtilization[Memory Utilization<br/>GB Usage]
    end

    subgraph "Application Metrics"
        ErrorRate[Error Rate<br/>5xx Responses]
        StatusCodes[Status Codes<br/>2xx, 4xx, 5xx]
        CustomMetrics[Custom Metrics<br/>Business Metrics]
        HealthChecks[Health Check Status<br/>Startup/Liveness]
    end

    subgraph "Infrastructure Metrics"
        ColdStarts[Cold Start Count<br/>Scale-from-Zero]
        StartupTime[Startup Time<br/>Container Init]
        NetworkTraffic[Network Traffic<br/>Ingress/Egress]
        DiskUsage[Disk Usage<br/>Ephemeral Storage]
    end

    subgraph "Alerting"
        ThresholdAlerts[Threshold Alerts<br/>Metric-based]
        AnomalyAlerts[Anomaly Detection<br/>Statistical]
        SLOAlerts[SLO Alerts<br/>Service Level]
        IncidentAlerts[Incident Alerts<br/>System Issues]
    end

    RequestCount --> ThresholdAlerts
    RequestLatency --> AnomalyAlerts
    InstanceCount --> ThresholdAlerts
    CPUUtilization --> SLOAlerts
    MemoryUtilization --> IncidentAlerts

    ErrorRate --> ThresholdAlerts
    StatusCodes --> AnomalyAlerts
    CustomMetrics --> SLOAlerts
    HealthChecks --> IncidentAlerts

    ColdStarts --> ThresholdAlerts
    StartupTime --> AnomalyAlerts
    NetworkTraffic --> SLOAlerts
    DiskUsage --> IncidentAlerts

    style RequestCount fill:#e3f2fd
    style ErrorRate fill:#fff3e0
    style ColdStarts fill:#e8f5e8
    style ThresholdAlerts fill:#e3f2fd
```

## Summary

These diagrams illustrate the key architectural patterns in Cloud Run:

1. **Service Architecture**: Global load balancing with containerized applications
2. **Scaling Patterns**: Autoscaling from zero to thousands of instances
3. **Deployment Strategies**: Rolling, blue-green, and canary deployments
4. **Event-Driven**: Integration with Google Cloud event sources
5. **Service Mesh**: Advanced traffic management and security
6. **Networking**: VPC integration and multi-region deployment
7. **Security**: Identity, authorization, and data protection
8. **Performance**: Cold start optimization and resource management
9. **Monitoring**: Comprehensive observability and alerting

These visual representations help understand how Cloud Run components interact and how to design scalable, secure serverless applications.
