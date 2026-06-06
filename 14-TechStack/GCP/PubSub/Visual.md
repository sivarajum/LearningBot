# Pub/Sub Visual Architecture and Diagrams

## Overview

This document provides visual representations of Cloud Pub/Sub's architecture, message flows, and integration patterns using Mermaid diagrams.

## Core Architecture

### Pub/Sub Service Architecture

```mermaid
graph TB
    subgraph "Publisher Layer"
        P1[Publisher App 1]
        P2[Publisher App 2]
        P3[IoT Device]
        P4[Mobile App]
    end

    subgraph "Pub/Sub Service"
        TOPIC[Topic<br/>Message Storage]
        SUB1[Subscription 1<br/>Pull Mode]
        SUB2[Subscription 2<br/>Push Mode]
        SCHEMA[Schema<br/>Validation]
        DEAD[Dead Letter<br/>Topic]
    end

    subgraph "Subscriber Layer"
        S1[Dataflow Pipeline]
        S2[Cloud Function]
        S3[App Engine]
        S4[GKE Service]
    end

    subgraph "Storage & Processing"
        GCS[(Cloud Storage<br/>Archive)]
        BQ[(BigQuery<br/>Analytics)]
        DF[Dataflow<br/>Processing]
    end

    P1 --> TOPIC
    P2 --> TOPIC
    P3 --> TOPIC
    P4 --> TOPIC

    TOPIC --> SUB1
    TOPIC --> SUB2

    SUB1 --> S1
    SUB2 --> S2
    SUB2 --> S3
    SUB2 --> S4

    S1 --> GCS
    S1 --> BQ
    S2 --> DF
    S3 --> BQ
    S4 --> GCS

    SUB1 -.-> DEAD
    SUB2 -.-> DEAD

    style P1 fill:#2196f3
    style TOPIC fill:#ffb74d
    style S1 fill:#4caf50
    style GCS fill:#2196f3
```

### Message Lifecycle

```mermaid
stateDiagram-v2
    [*] --> Published: Message Published
    Published --> Stored: Stored in Topic
    Stored --> Delivered: Delivered to Subscription
    Delivered --> Processing: Being Processed by Subscriber
    Processing --> Acked: Message Acknowledged
    Acked --> [*]: Message Removed

    Processing --> Nacked: Message Not Acknowledged
    Nacked --> Redelivered: Redelivered to Subscriber
    Redelivered --> Processing

    Processing --> Expired: Lease Expired
    Expired --> Redelivered

    Redelivered --> DeadLetter: Max Delivery Attempts
    DeadLetter --> [*]

    style Published fill:#2196f3
    style Stored fill:#ffb74d
    style Delivered fill:#4caf50
    style Processing fill:#2196f3
    style Acked fill:#ffb74d
    style Nacked fill:#4caf50
    style Redelivered fill:#2196f3
    style Expired fill:#ffb74d
    style DeadLetter fill:#4caf50
```

## Message Flow Patterns

### Basic Publish-Subscribe Pattern

```mermaid
graph LR
    subgraph "Publishers"
        P1[Web App]
        P2[Mobile App]
        P3[IoT Sensor]
        P4[Backend Service]
    end

    subgraph "Pub/Sub"
        T[orders Topic]
        S1[user-events Sub]
        S2[order-processing Sub]
        S3[analytics Sub]
    end

    subgraph "Subscribers"
        CF1[Cloud Function<br/>Email Service]
        CF2[Cloud Function<br/>Order Processor]
        DF[Dataflow<br/>Analytics Pipeline]
    end

    P1 --> T
    P2 --> T
    P3 --> T
    P4 --> T

    T --> S1
    T --> S2
    T --> S3

    S1 --> CF1
    S2 --> CF2
    S3 --> DF

    style P1 fill:#2196f3
    style T fill:#ffb74d
    style S1 fill:#4caf50
    style CF1 fill:#2196f3
```

### Fan-out Pattern

```mermaid
graph TD
    subgraph "Single Publisher"
        P[Order Service]
    end

    subgraph "Pub/Sub Topic"
        T[orders Topic]
    end

    subgraph "Multiple Subscriptions"
        S1[Email Sub<br/>Fan-out 1]
        S2[Inventory Sub<br/>Fan-out 2]
        S3[Shipping Sub<br/>Fan-out 3]
        S4[Analytics Sub<br/>Fan-out 4]
        S5[Notification Sub<br/>Fan-out 5]
    end

    subgraph "Multiple Subscribers"
        CF1[Email Service]
        CF2[Inventory System]
        CF3[Shipping Service]
        DF1[Analytics Pipeline]
        CF4[Push Notification]
    end

    P --> T
    T --> S1
    T --> S2
    T --> S3
    T --> S4
    T --> S5

    S1 --> CF1
    S2 --> CF2
    S3 --> CF3
    S4 --> DF1
    S5 --> CF4

    style P fill:#2196f3
    style T fill:#ffb74d
    style S1 fill:#4caf50
    style CF1 fill:#2196f3
```

### Message Ordering Flow

```mermaid
graph LR
    subgraph "Ordered Publishing"
        P1[Publisher<br/>Order Key: user123<br/>Seq: 1,2,3]
        P2[Publisher<br/>Order Key: user456<br/>Seq: 1,2,3]
    end

    subgraph "Pub/Sub Topic"
        T[Topic with Ordering<br/>Enabled]
    end

    subgraph "Ordered Delivery"
        S[Subscription<br/>Maintains Order]
    end

    subgraph "Ordered Processing"
        PROC1[Process user123-msg1]
        PROC2[Process user123-msg2]
        PROC3[Process user123-msg3]
        PROC4[Process user456-msg1]
        PROC5[Process user456-msg2]
        PROC6[Process user456-msg3]
    end

    P1 --> T
    P2 --> T
    T --> S
    S --> PROC1
    PROC1 --> PROC2
    PROC2 --> PROC3
    PROC3 --> PROC4
    PROC4 --> PROC5
    PROC5 --> PROC6

    style P1 fill:#2196f3
    style T fill:#ffb74d
    style S fill:#4caf50
    style PROC1 fill:#2196f3
```

## Integration Architectures

### Real-time Data Pipeline

```mermaid
graph LR
    subgraph "Data Sources"
        IoT[IoT Devices<br/>Sensors]
        Apps[Mobile/Web Apps<br/>User Events]
        Logs[Application Logs<br/>System Events]
        DB[Database Changes<br/>CDC Events]
    end

    subgraph "Ingestion Layer"
        PS[Cloud Pub/Sub<br/>Message Queue]
        GW[API Gateway<br/>Event Ingestion]
    end

    subgraph "Processing Layer"
        DF[Dataflow<br/>Stream Processing]
        CF[Cloud Functions<br/>Event Processing]
        GKE[GKE<br/>Container Processing]
    end

    subgraph "Storage Layer"
        BQ[(BigQuery<br/>Data Warehouse)]
        GCS[(Cloud Storage<br/>Data Lake)]
        CBT[(Bigtable<br/>NoSQL Store)]
    end

    subgraph "Consumption Layer"
        DS[Data Studio<br/>Dashboards]
        API[APIs<br/>Real-time Data]
        ML[Vertex AI<br/>ML Models]
    end

    IoT --> PS
    Apps --> PS
    Logs --> GW
    DB --> GW

    GW --> PS
    PS --> DF
    PS --> CF
    PS --> GKE

    DF --> BQ
    CF --> GCS
    GKE --> CBT

    BQ --> DS
    GCS --> API
    CBT --> ML

    style IoT fill:#2196f3
    style PS fill:#ffb74d
    style DF fill:#4caf50
    style BQ fill:#2196f3
```

### Event-Driven Microservices

```mermaid
graph TD
    subgraph "API Layer"
        API[API Gateway]
        AUTH[Authentication Service]
    end

    subgraph "Event Bus"
        PS[Cloud Pub/Sub]
        TOPIC1[User Events Topic]
        TOPIC2[Order Events Topic]
        TOPIC3[Payment Events Topic]
    end

    subgraph "Microservices"
        USER[User Service<br/>Cloud Run]
        ORDER[Order Service<br/>GKE]
        PAYMENT[Payment Service<br/>Cloud Functions]
        NOTIF[Notification Service<br/>App Engine]
        ANALYTICS[Analytics Service<br/>Dataflow]
    end

    subgraph "Data Layer"
        DB[(Cloud Spanner<br/>Transactional)]
        CACHE[(Memorystore<br/>Cache)]
        SEARCH[(Elasticsearch<br/>Search)]
    end

    API --> AUTH
    AUTH --> TOPIC1
    AUTH --> TOPIC2

    TOPIC1 --> USER
    TOPIC2 --> ORDER
    TOPIC2 --> PAYMENT

    ORDER --> TOPIC3
    PAYMENT --> TOPIC3

    TOPIC3 --> NOTIF
    TOPIC3 --> ANALYTICS

    USER --> DB
    ORDER --> DB
    PAYMENT --> CACHE
    ANALYTICS --> SEARCH

    style API fill:#2196f3
    style PS fill:#ffb74d
    style USER fill:#4caf50
    style DB fill:#2196f3
```

### IoT Data Architecture

```mermaid
graph TD
    subgraph "IoT Devices"
        SENSORS[Smart Sensors<br/>Temperature, Pressure]
        GATEWAYS[Edge Gateways<br/>Local Processing]
        CAMERAS[IP Cameras<br/>Video Streams]
        VEHICLES[Connected Vehicles<br/>GPS, Telemetry]
    end

    subgraph "Edge Processing"
        IoTCore[IoT Core<br/>Device Management]
        EdgeAI[Edge AI<br/>Local Inference]
    end

    subgraph "Cloud Ingestion"
        PS[Cloud Pub/Sub<br/>Message Queue]
        IoTTopic[IoT Data Topic]
        VideoTopic[Video Stream Topic]
    end

    subgraph "Stream Processing"
        DF[Dataflow<br/>Real-time Processing]
        AnomalyDetect[Anomaly Detection<br/>ML Models]
        VideoAnalysis[Video Analytics<br/>AI Vision]
    end

    subgraph "Storage & Analytics"
        TS[Bigtable<br/>Time Series Data]
        BQ[(BigQuery<br/>Analytics)]
        GCS[(Cloud Storage<br/>Raw Data)]
    end

    subgraph "Applications"
        DASH[Real-time Dashboard<br/>Data Studio]
        ALERTS[Alert System<br/>Cloud Functions]
        PREDICT[ML Predictions<br/>Vertex AI]
    end

    SENSORS --> IoTCore
    GATEWAYS --> IoTCore
    CAMERAS --> IoTCore
    VEHICLES --> IoTCore

    IoTCore --> EdgeAI
    EdgeAI --> PS

    PS --> IoTTopic
    PS --> VideoTopic

    IoTTopic --> DF
    VideoTopic --> VideoAnalysis

    DF --> AnomalyDetect
    VideoAnalysis --> AnomalyDetect

    DF --> TS
    DF --> BQ
    VideoAnalysis --> GCS

    TS --> DASH
    BQ --> PREDICT
    AnomalyDetect --> ALERTS

    style SENSORS fill:#2196f3
    style IoTCore fill:#ffb74d
    style PS fill:#4caf50
    style DF fill:#2196f3
```

## Security Architecture

### Authentication and Authorization

```mermaid
graph TD
    subgraph "Identity Management"
        IAM[IAM<br/>Identity & Access Management]
        SA[Service Accounts<br/>Programmatic Access]
        OIDC[OIDC Tokens<br/>Token-based Auth]
    end

    subgraph "Access Control"
        PROJECT[Project Level<br/>Publisher/Subscriber]
        TOPIC[Topic Level<br/>Publish Permission]
        SUB[Subscription Level<br/>Subscribe Permission]
        SCHEMA[Schema Level<br/>Validation Permission]
    end

    subgraph "Network Security"
        VPC[VPC Networks<br/>Private Access]
        PSC[Private Service Connect<br/>Secure Connections]
        CMEK[Customer-Managed Keys<br/>Data Encryption]
    end

    subgraph "Audit & Compliance"
        AUDIT[Cloud Audit Logs<br/>All Operations]
        DL[Data Loss Prevention<br/>Sensitive Data]
        COMPLIANCE[SOC 2, HIPAA, PCI DSS<br/>Compliance]
    end

    IAM --> PROJECT
    SA --> PROJECT
    OIDC --> PROJECT

    PROJECT --> TOPIC
    PROJECT --> SUB
    PROJECT --> SCHEMA

    TOPIC --> VPC
    SUB --> PSC
    SCHEMA --> CMEK

    VPC --> AUDIT
    PSC --> DL
    CMEK --> COMPLIANCE

    style IAM fill:#2196f3
    style PROJECT fill:#ffb74d
    style TOPIC fill:#4caf50
    style VPC fill:#2196f3
```

### Message Encryption Flow

```mermaid
graph TD
    subgraph "Message Publishing"
        APP[Application]
        ENCRYPT[Client-side Encryption<br/>Optional]
        PUBLISH[Publish to Topic]
    end

    subgraph "Pub/Sub Processing"
        RECEIVE[Receive Message]
        VALIDATE[Schema Validation<br/>Optional]
        STORE[Store in Topic<br/>Encrypted at Rest]
    end

    subgraph "Message Delivery"
        DELIVER[Deliver to Subscriber]
        DECRYPT[Subscriber Decryption<br/>If encrypted]
        PROCESS[Process Message]
    end

    subgraph "Security Layers"
        TLS[TLS 1.2+<br/>Transport Encryption]
        CMEK[CMEK<br/>Storage Encryption]
        IAM[IAM<br/>Access Control]
        AUDIT[Audit Logs<br/>Monitoring]
    end

    APP --> ENCRYPT
    ENCRYPT --> PUBLISH
    PUBLISH --> RECEIVE
    RECEIVE --> VALIDATE
    VALIDATE --> STORE
    STORE --> DELIVER
    DELIVER --> DECRYPT
    DECRYPT --> PROCESS

    PUBLISH -.-> TLS
    RECEIVE -.-> TLS
    STORE -.-> CMEK
    DELIVER -.-> IAM
    PROCESS -.-> AUDIT

    style APP fill:#2196f3
    style ENCRYPT fill:#ffb74d
    style RECEIVE fill:#4caf50
    style TLS fill:#2196f3
```

## Performance and Monitoring

### Throughput and Latency Metrics

```mermaid
graph TD
    subgraph "Performance Metrics"
        PUBLISH_RATE[Publish Rate<br/>msg/sec]
        DELIVERY_RATE[Delivery Rate<br/>msg/sec]
        LATENCY[End-to-End Latency<br/>milliseconds]
        THROUGHPUT[Throughput<br/>MB/sec]
    end

    subgraph "System Metrics"
        CPU[CPU Utilization<br/>per region]
        MEMORY[Memory Usage<br/>per region]
        DISK[Disk I/O<br/>per region]
        NETWORK[Network I/O<br/>per region]
    end

    subgraph "Queue Metrics"
        UNACKED[Unacked Messages<br/>per subscription]
        OLDEST[Oldest Message Age<br/>per subscription]
        BACKLOG[Message Backlog<br/>per subscription]
        DEAD[Dead Letter Count<br/>per subscription]
    end

    subgraph "Error Metrics"
        PUBLISH_ERRORS[Publish Errors<br/>rate]
        DELIVERY_ERRORS[Delivery Errors<br/>rate]
        NACK_RATE[Nack Rate<br/>rate]
        EXPIRED[Expired Messages<br/>rate]
    end

    PUBLISH_RATE --> CPU
    DELIVERY_RATE --> MEMORY
    LATENCY --> NETWORK
    THROUGHPUT --> DISK

    UNACKED --> PUBLISH_ERRORS
    OLDEST --> DELIVERY_ERRORS
    BACKLOG --> NACK_RATE
    DEAD --> EXPIRED

    style PUBLISH_RATE fill:#2196f3
    style CPU fill:#ffb74d
    style UNACKED fill:#4caf50
    style PUBLISH_ERRORS fill:#2196f3
```

### Scaling Architecture

```mermaid
graph TD
    subgraph "Auto-scaling Components"
        PUBLISHERS[Publisher Fleet<br/>Auto-scaling]
        TOPICS[Topics<br/>Global Distribution]
        SUBSCRIBERS[Subscriber Fleet<br/>Auto-scaling]
        WORKERS[Worker Nodes<br/>Dynamic Scaling]
    end

    subgraph "Load Balancing"
        GLOBAL_LB[Global Load Balancer<br/>Cross-region]
        REGIONAL_LB[Regional Load Balancer<br/>Within region]
        TOPIC_SHARD[Topic Sharding<br/>Load distribution]
    end

    subgraph "Monitoring & Scaling"
        METRICS[Performance Metrics<br/>Real-time]
        AUTOSCALE[Auto-scaling Policies<br/>CPU/Memory]
        ALERTS[Scaling Alerts<br/>Threshold-based]
        PREDICTIVE[Predictive Scaling<br/>ML-based]
    end

    PUBLISHERS --> GLOBAL_LB
    GLOBAL_LB --> TOPICS
    TOPICS --> REGIONAL_LB
    REGIONAL_LB --> SUBSCRIBERS
    SUBSCRIBERS --> WORKERS

    TOPICS --> TOPIC_SHARD
    WORKERS --> TOPIC_SHARD

    METRICS --> AUTOSCALE
    AUTOSCALE --> PUBLISHERS
    AUTOSCALE --> SUBSCRIBERS
    AUTOSCALE --> WORKERS

    ALERTS --> AUTOSCALE
    PREDICTIVE --> AUTOSCALE

    style PUBLISHERS fill:#2196f3
    style GLOBAL_LB fill:#ffb74d
    style METRICS fill:#4caf50
    style AUTOSCALE fill:#2196f3
```

## Cost Optimization

### Cost Components

```mermaid
graph TD
    subgraph "Data Transfer Costs"
        PUBLISH_DATA[Data Published<br/>per GB]
        DELIVER_DATA[Data Delivered<br/>per GB]
        RETENTION[Message Retention<br/>per GB-month]
    end

    subgraph "Operation Costs"
        PUBLISH_OPS[Publish Operations<br/>per 1K operations]
        DELIVER_OPS[Deliver Operations<br/>per 1K operations]
        SEEK_OPS[Seek Operations<br/>per 1K operations]
    end

    subgraph "Storage Costs"
        SCHEMA_STORAGE[Schema Storage<br/>per GB-month]
        SNAPSHOT[Snapshots<br/>per GB-month]
    end

    subgraph "Optimization Strategies"
        BATCHING[Message Batching<br/>Reduce operations]
        COMPRESSION[Data Compression<br/>Reduce data volume]
        FILTERING[Subscription Filtering<br/>Reduce delivery]
        RETENTION_POLICY[Retention Policies<br/>Minimize storage]
    end

    PUBLISH_DATA --> BATCHING
    DELIVER_DATA --> COMPRESSION
    RETENTION --> FILTERING
    PUBLISH_OPS --> RETENTION_POLICY
    DELIVER_OPS --> BATCHING
    SEEK_OPS --> COMPRESSION
    SCHEMA_STORAGE --> FILTERING
    SNAPSHOT --> RETENTION_POLICY

    style PUBLISH_DATA fill:#2196f3
    style BATCHING fill:#ffb74d
    style COMPRESSION fill:#4caf50
    style FILTERING fill:#2196f3
```

### Cost Monitoring Dashboard

```mermaid
graph TD
    subgraph "Cost Analysis"
        TOTAL_COST[Total Pub/Sub Cost<br/>by time period]
        COST_BY_TOPIC[Cost by Topic<br/>breakdown]
        COST_BY_OPERATION[Cost by Operation<br/>publish/deliver]
        COST_TRENDS[Cost Trends<br/>over time]
    end

    subgraph "Usage Metrics"
        DATA_VOLUME[Data Volume<br/>GB processed]
        OPERATION_COUNT[Operation Count<br/>millions]
        ACTIVE_SUBS[Active Subscriptions<br/>count]
        MESSAGE_RATE[Message Rate<br/>per second]
    end

    subgraph "Optimization Insights"
        EFFICIENCY[Efficiency Score<br/>cost per message]
        WASTE[Wasted Operations<br/>unnecessary deliveries]
        OPTIMIZATION[Optimization<br/>recommendations]
        SAVINGS[Potential Savings<br/>estimated]
    end

    TOTAL_COST --> DATA_VOLUME
    COST_BY_TOPIC --> OPERATION_COUNT
    COST_BY_OPERATION --> ACTIVE_SUBS
    COST_TRENDS --> MESSAGE_RATE

    EFFICIENCY --> TOTAL_COST
    WASTE --> COST_BY_OPERATION
    OPTIMIZATION --> COST_TRENDS
    SAVINGS --> EFFICIENCY

    style TOTAL_COST fill:#2196f3
    style DATA_VOLUME fill:#ffb74d
    style EFFICIENCY fill:#4caf50
    style WASTE fill:#2196f3
```

## Integration Patterns

### Pub/Sub with Google Cloud Services

```mermaid
graph TD
    subgraph "Data Sources"
        GCS[Cloud Storage<br/>File uploads]
        BQ[BigQuery<br/>Data changes]
        CF[Cloud Functions<br/>Event triggers]
        GKE[GKE<br/>Container events]
    end

    subgraph "Pub/Sub"
        TOPICS[Topics<br/>Event routing]
        SUBS[Subscriptions<br/>Event delivery]
        SCHEMAS[Schemas<br/>Data validation]
    end

    subgraph "Processing Services"
        DF[Dataflow<br/>Stream processing]
        CF_PROC[Cloud Functions<br/>Event processing]
        RUN[Cloud Run<br/>Service integration]
        AI[Vertex AI<br/>ML processing]
    end

    subgraph "Storage Services"
        BQ_STORE[BigQuery<br/>Data warehouse]
        GCS_STORE[Cloud Storage<br/>Data lake]
        BT[Bigtable<br/>Time series]
        SPANNER[Spanner<br/>Transactional]
    end

    subgraph "Analytics & ML"
        LOOKER[Looker<br/>Business intelligence]
        VIZ[Data Studio<br/>Visualization]
        ML[AutoML<br/>Automated ML]
        VERTEX[Vertex AI<br/>ML platform]
    end

    GCS --> TOPICS
    BQ --> TOPICS
    CF --> TOPICS
    GKE --> TOPICS

    TOPICS --> SUBS
    SUBS --> SCHEMAS

    SCHEMAS --> DF
    SCHEMAS --> CF_PROC
    SCHEMAS --> RUN
    SCHEMAS --> AI

    DF --> BQ_STORE
    CF_PROC --> GCS_STORE
    RUN --> BT
    AI --> SPANNER

    BQ_STORE --> LOOKER
    GCS_STORE --> VIZ
    BT --> ML
    SPANNER --> VERTEX

    style GCS fill:#2196f3
    style TOPICS fill:#ffb74d
    style DF fill:#4caf50
    style BQ_STORE fill:#2196f3
```

### Cross-Cloud Integration

```mermaid
graph TD
    subgraph "Google Cloud"
        GCP_PUBSUB[Cloud Pub/Sub<br/>Primary messaging]
        GCP_SERVICES[GCP Services<br/>BigQuery, AI, etc.]
    end

    subgraph "AWS"
        SQS[SQS<br/>Message queuing]
        KINESIS[Kinesis<br/>Stream processing]
        LAMBDA[Lambda<br/>Serverless functions]
    end

    subgraph "Azure"
        EVENT_HUBS[Event Hubs<br/>Event ingestion]
        FUNCTIONS[Functions<br/>Serverless compute]
        STREAM_ANALYTICS[Stream Analytics<br/>Real-time analytics]
    end

    subgraph "Integration Layer"
        GATEWAY[API Gateway<br/>Protocol translation]
        BRIDGE[Event Bridge<br/>Cross-cloud routing]
        TRANSLATOR[Message Translator<br/>Format conversion]
    end

    GCP_PUBSUB --> GATEWAY
    SQS --> GATEWAY
    EVENT_HUBS --> GATEWAY

    GATEWAY --> BRIDGE
    BRIDGE --> TRANSLATOR

    TRANSLATOR --> GCP_SERVICES
    TRANSLATOR --> KINESIS
    TRANSLATOR --> LAMBDA
    TRANSLATOR --> FUNCTIONS
    TRANSLATOR --> STREAM_ANALYTICS

    style GCP_PUBSUB fill:#2196f3
    style SQS fill:#ffb74d
    style GATEWAY fill:#4caf50
    style BRIDGE fill:#2196f3
```

## Summary

These diagrams illustrate the key architectural patterns and data flows in Cloud Pub/Sub:

1. **Service Architecture**: Publisher-subscriber model with topics and subscriptions
2. **Message Lifecycle**: Complete journey from publishing to acknowledgment
3. **Integration Patterns**: Real-time pipelines, microservices, and IoT architectures
4. **Security Model**: Authentication, authorization, and encryption layers
5. **Performance Monitoring**: Throughput, latency, and scaling metrics
6. **Cost Optimization**: Usage patterns and optimization strategies
7. **Cross-Cloud Integration**: Multi-cloud messaging architectures

These visual representations help understand how Pub/Sub enables event-driven architectures and supports real-time data processing at scale.
