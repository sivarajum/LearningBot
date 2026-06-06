# Apache Kafka: Visual Guide

## Architecture Diagrams

### Kafka Cluster Architecture

```mermaid
graph TD
    subgraph "Kafka Cluster"
        B1[Broker 1<br/>Controller]
        B2[Broker 2]
        B3[Broker 3]
        B4[Broker 4]

        B1 --- B2
        B2 --- B3
        B3 --- B4
        B4 --- B1
    end

    subgraph "Zookeeper Ensemble"
        Z1[Zookeeper 1<br/>Leader]
        Z2[Zookeeper 2]
        Z3[Zookeeper 3]

        Z1 --- Z2
        Z2 --- Z3
        Z3 --- Z1
    end

    B1 -.-> Z1
    B2 -.-> Z2
    B3 -.-> Z3
    B4 -.-> Z1

    P[Producers] --> B1
    B1 --> C[Consumers]

    style B1 fill:#e8f5e8
    style Z1 fill:#fff3e0
```

### Topic Partitioning and Replication

```mermaid
graph TD
    subgraph "Topic: user-events (Replication Factor: 3)"
        subgraph "Partition 0"
            L0[Leader<br/>Broker 1]
            R0_1[Replica<br/>Broker 2]
            R0_2[Replica<br/>Broker 3]
        end

        subgraph "Partition 1"
            L1[Leader<br/>Broker 2]
            R1_1[Replica<br/>Broker 3]
            R1_2[Replica<br/>Broker 1]
        end

        subgraph "Partition 2"
            L2[Leader<br/>Broker 3]
            R2_1[Replica<br/>Broker 1]
            R2_2[Replica<br/>Broker 2]
        end
    end

    P[Producer] --> L0
    P --> L1
    P --> L2

    L0 --> ISR0[ISR: B1, B2, B3]
    L1 --> ISR1[ISR: B2, B3, B1]
    L2 --> ISR2[ISR: B3, B1, B2]

    style L0 fill:#e8f5e8
    style L1 fill:#e8f5e8
    style L2 fill:#e8f5e8
```

### Producer-Consumer Flow

```mermaid
graph TD
    A[Application] --> B[Producer]
    B --> C[Partitioner]
    C --> D[Serializer]
    D --> E[Record Accumulator]

    E --> F{Send Condition}
    F -->|Batch Full| G[Send to Broker]
    F -->|Time Elapsed| G
    F -->|Force Flush| G

    G --> H[Network Layer]
    H --> I[Kafka Broker]

    I --> J[Topic Partition]
    J --> K[Log Segments]
    K --> L[Commit Log]

    M[Consumer Group] --> N[Consumer 1]
    M --> O[Consumer 2]
    M --> P[Consumer 3]

    N --> Q[Partition 0]
    O --> R[Partition 1]
    P --> S[Partition 2]

    Q --> T[Deserializer]
    R --> T
    S --> T

    T --> U[Application]

    style B fill:#e3f2fd
    style N fill:#f3e5f5
    style O fill:#f3e5f5
    style P fill:#f3e5f5
```

## Consumer Patterns

### Consumer Group Rebalancing

```mermaid
graph TD
    subgraph "Before Rebalancing"
        CG[Consumer Group]
        CG --> C1[Consumer 1<br/>P0, P1]
        CG --> C2[Consumer 2<br/>P2, P3]
        CG --> C3[Consumer 3<br/>P4, P5]
    end

    subgraph "After Consumer 2 Leaves"
        CG2[Consumer Group]
        CG2 --> C1_2[Consumer 1<br/>P0, P1, P2]
        CG2 --> C3_2[Consumer 3<br/>P3, P4, P5]
    end

    subgraph "Coordinator"
        Coord[Group Coordinator<br/>Broker 1]
        Coord --> HB[Heartbeat Monitor]
        Coord --> Rebal[Rebalancing Logic]
    end

    style C1 fill:#e8f5e8
    style C2 fill:#ffebee
    style C1_2 fill:#e8f5e8
    style C3_2 fill:#e8f5e8
```

### Consumer Offset Management

```mermaid
graph TD
    A[Consumer] --> B[Poll Messages]
    B --> C[Process Batch]
    C --> D{Processing<br/>Successful?}

    D -->|Yes| E[Commit Offsets]
    D -->|No| F[Retry Logic]

    E --> G[Offset Storage]
    G --> H{Storage Type}
    H -->|ZooKeeper| I[ZooKeeper]
    H -->|Kafka| J[__consumer_offsets<br/>Topic]

    F --> K{Max Retries<br/>Exceeded?}
    K -->|No| C
    K -->|Yes| L[Send to DLQ]

    L --> M[Dead Letter Queue]

    style E fill:#c8e6c9
    style L fill:#ffcdd2
```

## Stream Processing

### Kafka Streams Topology

```mermaid
graph TD
    A[Source Topic] --> B[KStream<br/>Filter]
    B --> C[KTable<br/>Aggregate]
    C --> D[KStream<br/>Map]
    D --> E[Join<br/>KStream + KTable]
    E --> F[Processor<br/>Transform]
    F --> G[State Store<br/>Windowed Store]
    G --> H[Sink Topic]

    I[External Store] -.-> E
    G -.-> J[Interactive Queries]

    style A fill:#e8f5e8
    style H fill:#c8e6c9
    style G fill:#fff3e0
```

### Stream Processing Patterns

```mermaid
graph TD
    subgraph "Event Filtering"
        A1[Input Stream] --> B1[Filter Predicate]
        B1 --> C1[Filtered Stream]
    end

    subgraph "Event Aggregation"
        A2[Input Stream] --> B2[Window Function]
        B2 --> C2[Group By Key]
        C2 --> D2[Aggregate]
        D2 --> E2[Aggregated Stream]
    end

    subgraph "Stream Join"
        A3[Stream A] --> C3[Join]
        A4[Stream B] --> C3
        C3 --> D3[Joined Stream]
    end

    subgraph "Event Enrichment"
        A5[Input Stream] --> B5[Lookup<br/>External Data]
        B5 --> C5[Enrich Event]
        C5 --> D5[Enriched Stream]
    end

    style A1 fill:#e3f2fd
    style A2 fill:#f3e5f5
    style A3 fill:#fff3e0
    style A5 fill:#e8f5e8
```

### Windowing Operations

```mermaid
graph TD
    A[Event Stream] --> B{Window Type}

    B -->|Tumbling| C[Tumbling Window<br/>Fixed Size, No Overlap]
    B -->|Sliding| D[Sliding Window<br/>Fixed Size, Overlapping]
    B -->|Session| E[Session Window<br/>Dynamic Size, Gap-based]

    C --> F[Window 1<br/>00:00-00:05]
    C --> G[Window 2<br/>00:05-00:10]

    D --> H[Window 1<br/>00:00-00:05]
    D --> I[Window 2<br/>00:01-00:06]
    D --> J[Window 3<br/>00:02-00:07]

    E --> K[Session 1<br/>Gap < 30min]
    E --> L[Session 2<br/>Gap < 30min]

    style C fill:#e3f2fd
    style D fill:#f3e5f5
    style E fill:#fff3e0
```

## Kafka Connect

### Connect Architecture

```mermaid
graph TD
    subgraph "Kafka Connect Cluster"
        W1[Worker 1]
        W2[Worker 2]
        W3[Worker 3]

        W1 --> REST[REST API]
        W2 --> REST
        W3 --> REST
    end

    subgraph "Source Connectors"
        S1[PostgreSQL<br/>Connector]
        S2[MongoDB<br/>Connector]
        S3[File<br/>Connector]
    end

    subgraph "Sink Connectors"
        SK1[Elasticsearch<br/>Connector]
        SK2[S3<br/>Connector]
        SK3[JDBC<br/>Connector]
    end

    S1 --> W1
    S2 --> W2
    S3 --> W3

    W1 --> SK1
    W2 --> SK2
    W3 --> SK3

    subgraph "External Systems"
        DB[(Database)]
        ES[(Elasticsearch)]
        S3[(S3 Bucket)]
    end

    S1 --> DB
    SK1 --> ES
    SK3 --> DB
    SK2 --> S3

    subgraph "Kafka Topics"
        T1[user-events]
        T2[order-events]
        T3[file-data]
    end

    S1 --> T1
    S2 --> T2
    S3 --> T3

    T1 --> SK1
    T2 --> SK2
    T3 --> SK3

    style W1 fill:#e8f5e8
    style REST fill:#fff3e0
```

### Connector Lifecycle

```mermaid
graph TD
    A[Connector Config<br/>Submitted] --> B[Validate Config]
    B --> C{Create Tasks}
    C --> D[Task 1]
    C --> E[Task 2]
    C --> F[Task N]

    D --> G[Initialize]
    E --> G
    F --> G

    G --> H[Start Processing]
    H --> I[Poll Data]
    I --> J[Transform Data]
    J --> K[Send to Kafka]

    K --> L{Monitor Health}
    L -->|Healthy| I
    L -->|Unhealthy| M[Restart Task]

    M --> G

    style A fill:#e8f5e8
    style K fill:#c8e6c9
```

## Schema Registry

### Schema Evolution

```mermaid
graph TD
    A[Producer] --> B[Schema Registry]
    B --> C{Validate Schema}

    C -->|Valid| D[Register Schema<br/>Version 1]
    C -->|Invalid| E[Schema Error]

    D --> F[Serialize Message<br/>with Schema ID]

    G[Consumer] --> H[Schema Registry]
    H --> I[Fetch Schema<br/>by ID]

    I --> J[Deserialize Message]

    K[Schema Change] --> L[Backward Compatible?]
    L -->|Yes| M[Register New Version]
    L -->|No| N[Breaking Change<br/>Error]

    style B fill:#fff3e0
    style D fill:#c8e6c9
    style M fill:#c8e6c9
```

### Schema Compatibility Modes

```mermaid
graph TD
    A[Schema Compatibility] --> B{Mode}

    B -->|BACKWARD| C[New Schema<br/>can read<br/>Old Data]
    B -->|FORWARD| D[Old Schema<br/>can read<br/>New Data]
    B -->|FULL| E[Both Backward<br/>and Forward]
    B -->|NONE| F[No Compatibility<br/>Checks]

    C --> G[Safe Evolution]
    D --> G
    E --> G
    F --> H[Breaking Changes<br/>Allowed]

    style C fill:#e8f5e8
    style D fill:#e8f5e8
    style E fill:#e8f5e8
    style F fill:#ffebee
```

## Monitoring and Operations

### Kafka Metrics Dashboard

```mermaid
graph TD
    subgraph "Broker Metrics"
        A1[Bytes In/Out]
        A2[Messages In/Out]
        A3[Request Rate]
        A4[Error Rate]
        A5[Partition Count]
    end

    subgraph "Topic Metrics"
        B1[Log Size]
        B2[Message Count]
        B3[Replication Lag]
        B4[Under-Replicated<br/>Partitions]
    end

    subgraph "Consumer Metrics"
        C1[Consumer Lag]
        C2[Records Consumed<br/>Rate]
        C3[Commit Rate]
        C4[Rebalance Count]
    end

    subgraph "System Metrics"
        D1[CPU Usage]
        D2[Memory Usage]
        D3[Disk I/O]
        D4[Network I/O]
    end

    M[Monitoring System] --> A1
    M --> B1
    M --> C1
    M --> D1

    A1 --> P[Prometheus]
    B1 --> P
    C1 --> P
    D1 --> P

    P --> G[Grafana<br/>Dashboard]

    style M fill:#e8f5e8
    style P fill:#fff3e0
    style G fill:#c8e6c9
```

### Alerting Rules

```mermaid
graph TD
    A[Metrics Collector] --> B{Evaluate Rules}

    B --> C{Consumer Lag<br/>> 10000?}
    B --> D{Broker Count<br/>< 3?}
    B --> E{Disk Usage<br/>> 85%?}
    B --> F{Error Rate<br/>> 5%?}

    C -->|Yes| G[High Lag Alert]
    D -->|Yes| H[Broker Down Alert]
    E -->|Yes| I[Disk Full Alert]
    F -->|Yes| J[Error Rate Alert]

    G --> K[Send Alert]
    H --> K
    I --> K
    J --> K

    K --> L{Alert Channel}
    L -->|Email| M[SMTP Server]
    L -->|Slack| N[Slack Webhook]
    L -->|PagerDuty| O[PagerDuty API]

    style G fill:#ffebee
    style H fill:#ffebee
    style I fill:#ffebee
    style J fill:#ffebee
```

## Deployment Patterns

### Multi-Cluster Architecture

```mermaid
graph TD
    subgraph "Data Center 1"
        K1[Kafka Cluster 1]
        K1 --> Z1[Zookeeper]
        K1 --> MM1[MirrorMaker]
    end

    subgraph "Data Center 2"
        K2[Kafka Cluster 2]
        K2 --> Z2[Zookeeper]
        K2 --> MM2[MirrorMaker]
    end

    subgraph "Data Center 3"
        K3[Kafka Cluster 3]
        K3 --> Z3[Zookeeper]
    end

    MM1 --> K2
    MM2 --> K3
    MM1 --> K3

    P1[Producers DC1] --> K1
    P2[Producers DC2] --> K2
    P3[Producers DC3] --> K3

    K1 --> C1[Consumers DC1]
    K2 --> C2[Consumers DC2]
    K3 --> C3[Consumers DC3]

    style K1 fill:#e3f2fd
    style K2 fill:#f3e5f5
    style K3 fill:#fff3e0
```

### Kubernetes Deployment

```mermaid
graph TD
    subgraph "Kubernetes Cluster"
        subgraph "Kafka Namespace"
            STS[StatefulSet<br/>Kafka Brokers]
            STS --> PVC1[PVC Broker-0]
            STS --> PVC2[PVC Broker-1]
            STS --> PVC3[PVC Broker-2]

            SVC[Service<br/>kafka-service]
            STS --> SVC

            CM[ConfigMap<br/>kafka-config]
            STS --> CM
        end

        subgraph "Zookeeper"
            ZSTS[StatefulSet<br/>Zookeeper]
            ZSTS --> ZPVC1[PVC zk-0]
            ZSTS --> ZPVC2[PVC zk-1]
            ZSTS --> ZPVC3[PVC zk-2]

            ZSVC[Service<br/>zk-service]
            ZSTS --> ZSVC
        end
    end

    subgraph "External Access"
        LB[LoadBalancer<br/>Service]
        SVC --> LB
    end

    P[Producers] --> LB
    LB --> C[Consumers]

    style STS fill:#e8f5e8
    style ZSTS fill:#fff3e0
```

### Tiered Storage Architecture

```mermaid
graph TD
    A[Hot Storage<br/>Local SSD] --> B[Recent Data<br/>High Performance]
    A --> C[Active Segments]

    D[Cold Storage<br/>Object Store] --> E[Historical Data<br/>Cost Effective]
    D --> F[Archived Segments]

    G[Kafka Broker] --> H{Tiered Storage<br/>Manager}

    H --> I{Data Age<br/>< Threshold?}
    I -->|Recent| J[Write to Hot]
    I -->|Old| K[Move to Cold]

    L[Consumer] --> M{Data Location}
    M -->|Hot| N[Read from Local]
    M -->|Cold| O[Read from Remote]

    style A fill:#e8f5e8
    style D fill:#fff3e0
    style J fill:#c8e6c9
    style K fill:#c8e6c9
```

## Security Architecture

### Authentication and Authorization

```mermaid
graph TD
    A[Client] --> B{Authentication}
    B -->|SASL/PLAIN| C[Username/Password]
    B -->|SASL/SCRAM| D[SCRAM Challenge]
    B -->|SASL/GSSAPI| E[Kerberos Ticket]
    B -->|SSL| F[Client Certificate]

    C --> G[Validate Credentials]
    D --> G
    E --> G
    F --> G

    G --> H{Authorized?}
    H -->|Yes| I[Access Granted]
    H -->|No| J[Access Denied]

    I --> K[ACL Check]
    K --> L{Resource Access<br/>Allowed?}
    L -->|Yes| M[Operation Allowed]
    L -->|No| N[Operation Denied]

    style I fill:#c8e6c9
    style M fill:#c8e6c9
```

### End-to-End Encryption

```mermaid
graph TD
    A[Producer] --> B[Encrypt Message]
    B --> C[SSL/TLS Channel]
    C --> D[Kafka Broker]

    D --> E[Store Encrypted<br/>Message]
    E --> F[SSL/TLS Channel]
    F --> G[Consumer]

    G --> H[Decrypt Message]

    I[KMS] --> B
    I --> H

    J[Key Rotation<br/>Service] --> I

    style B fill:#e8f5e8
    style H fill:#c8e6c9
    style I fill:#fff3e0
```

## Performance Optimization

### Throughput Optimization

```mermaid
graph TD
    A[High Throughput<br/>Requirements] --> B[Batch Settings]

    B --> C[batch.size<br/>Larger Batches]
    B --> D[linger.ms<br/>Wait for Batch]
    B --> E[compression.type<br/>Enable Compression]

    A --> F[Partition Strategy]
    F --> G[More Partitions]
    F --> H[Good Key Distribution]

    A --> I[Consumer Tuning]
    I --> J[fetch.min.bytes<br/>Larger Fetches]
    I --> K[max.poll.records<br/>More Records/Batch]

    A --> L[Broker Config]
    L --> M[num.replica.fetchers<br/>Parallel Fetching]
    L --> N[replica.fetch.max.bytes<br/>Larger Replicas]

    style C fill:#e8f5e8
    style G fill:#e8f5e8
    style J fill:#e8f5e8
    style M fill:#e8f5e8
```

### Latency Optimization

```mermaid
graph TD
    A[Low Latency<br/>Requirements] --> B[Producer Settings]

    B --> C[acks=1<br/>Leader Only]
    B --> D[compression.type=none<br/>No Compression]
    B --> E[batch.size=0<br/>No Batching]

    A --> F[Consumer Settings]
    F --> G[fetch.min.bytes=1<br/>Immediate Fetch]
    F --> H[max.poll.records=1<br/>Single Record]

    A --> I[Broker Settings]
    I --> J[num.partitions<br/>Fewer Partitions]
    I --> K[replica.lag.time.max.ms<br/>Tighter Lag]

    A --> L[Network]
    L --> M[Dedicated Network]
    L --> N[Close Proximity]

    style C fill:#e8f5e8
    style G fill:#e8f5e8
    style J fill:#e8f5e8
    style M fill:#e8f5e8
```

## Disaster Recovery

### Backup and Recovery

```mermaid
graph TD
    A[Primary Cluster] --> B[MirrorMaker 2]
    B --> C[Backup Cluster]

    A --> D[Regular Backups]
    D --> E[S3/GCS Backup]

    F[Disaster Event] --> G{Failover<br/>Required?}

    G -->|Yes| H[Stop Primary]
    H --> I[Promote Backup]
    I --> J[Update DNS/Clients]

    G -->|No| K[Continue Normal<br/>Operation]

    L[Recovery Complete] --> M[Rebuild Primary]
    M --> N[Resync Data]
    N --> O[Failback]

    style A fill:#e8f5e8
    style C fill:#fff3e0
    style I fill:#c8e6c9
```

### Cross-Region Replication

```mermaid
graph TD
    subgraph "Region 1 (Primary)"
        K1[Kafka Cluster]
        MM1[MirrorMaker]
        P1[Producers]
        C1[Consumers]
    end

    subgraph "Region 2 (DR)"
        K2[Kafka Cluster]
        MM2[MirrorMaker]
        P2[Producers]
        C2[Consumers]
    end

    P1 --> K1
    K1 --> C1
    K1 --> MM1
    MM1 --> K2
    K2 --> C2

    P2 --> K2
    K2 --> MM2
    MM2 --> K1

    RTO[RTO: 1 hour] --> DR[DR Strategy]
    RPO[RPO: 5 minutes] --> DR

    style K1 fill:#e8f5e8
    style K2 fill:#fff3e0
```

This visual guide provides comprehensive diagrams covering Apache Kafka's architecture, data flow patterns, deployment strategies, monitoring approaches, and operational best practices. Each diagram illustrates complex concepts in an accessible way, helping developers and operators understand Kafka's fundamental building blocks and advanced features for building robust event streaming systems.
