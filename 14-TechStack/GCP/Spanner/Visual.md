# Cloud Spanner Visual Guide

## Cloud Spanner Global Architecture

```mermaid
graph TB
    subgraph "Global Infrastructure"
        US[US Multi-Region<br/>us-central1, us-east1, us-west1]
        EU[EU Multi-Region<br/>europe-north1, europe-west1, europe-west4]
        ASIA[Asia Multi-Region<br/>asia-east1, asia-northeast1, asia-southeast1]
    end

    subgraph "Spanner Instance"
        INSTANCE[Spanner Instance<br/>Multi-Regional]
        ZONES[Zones within Regions<br/>Data Centers]
        NODES[Spanner Nodes<br/>Compute & Storage]
    end

    subgraph "Data Distribution"
        PAXOS[Paxos Groups<br/>Replication Units]
        TABLETS[Tablets<br/>Data Shards]
        LEADER[Leaders<br/>Write Coordination]
        REPLICAS[Replicas<br/>Read Serving]
    end

    subgraph "TrueTime System"
        ATOMIC_CLOCKS[Atomic Clocks<br/>GPS & Atomic Time]
        TIME_MASTER[Time Master<br/>Per Data Center]
        UNCERTAINTY[Time Uncertainty<br/>±ε bounds]
        SYNCHRONIZATION[Clock Synchronization<br/>Global Coordination]
    end

    US --> INSTANCE
    EU --> INSTANCE
    ASIA --> INSTANCE

    INSTANCE --> ZONES
    ZONES --> NODES

    NODES --> PAXOS
    PAXOS --> TABLETS
    TABLETS --> LEADER
    TABLETS --> REPLICAS

    ATOMIC_CLOCKS --> TIME_MASTER
    TIME_MASTER --> UNCERTAINTY
    UNCERTAINTY --> SYNCHRONIZATION
    SYNCHRONIZATION --> INSTANCE

    style US fill:#2196f3
    style INSTANCE fill:#ffb74d
    style PAXOS fill:#4caf50
    style ATOMIC_CLOCKS fill:#ba68c8
```

## TrueTime and External Consistency

```mermaid
graph LR
    subgraph "TrueTime Architecture"
        GPS_CLOCKS[GPS Clocks<br/>Satellite Time]
        ATOMIC_CLOCKS[Atomic Clocks<br/>Ground-based Time]
        TIME_MASTERS[Time Masters<br/>Per Data Center]
        DAEMONS[Time Daemons<br/>Per Machine]
    end

    subgraph "Time Coordination"
        EARLIEST[Earliest Time<br/>T_earliest]
        LATEST[Latest Time<br/>T_latest]
        UNCERTAINTY[Uncertainty<br/>ε = T_latest - T_earliest]
        SYNCHRONIZED[Synchronized Time<br/>Global Consistency]
    end

    subgraph "Transaction Ordering"
        START[Transaction Start<br/>Get Timestamp]
        EXECUTE[Execute Operations<br/>Within ε bounds]
        COMMIT[Commit Timestamp<br/>T_commit ∈ [T_earliest, T_latest]]
        EXTERNAL[External Consistency<br/>Serializable Order]
    end

    GPS_CLOCKS --> TIME_MASTERS
    ATOMIC_CLOCKS --> TIME_MASTERS
    TIME_MASTERS --> DAEMONS

    DAEMONS --> EARLIEST
    DAEMONS --> LATEST
    EARLIEST --> UNCERTAINTY
    LATEST --> UNCERTAINTY
    UNCERTAINTY --> SYNCHRONIZED

    SYNCHRONIZED --> START
    START --> EXECUTE
    EXECUTE --> COMMIT
    COMMIT --> EXTERNAL

    style GPS_CLOCKS fill:#2196f3
    style EARLIEST fill:#ffb74d
    style START fill:#4caf50
    style COMMIT fill:#ba68c8
```

## Paxos-Based Replication

```mermaid
graph TD
    subgraph "Paxos Group"
        LEADER[Leader Replica<br/>Write Coordinator]
        REPLICA1[Replica 1<br/>Read Serving]
        REPLICA2[Replica 2<br/>Read Serving]
        REPLICA3[Replica 3<br/>Read Serving]
    end

    subgraph "Write Protocol"
        PROPOSE[Propose Value<br/>Client Write]
        PREPARE[Prepare Phase<br/>Majority Agreement]
        ACCEPT[Accept Phase<br/>Value Commitment]
        LEARN[Learn Phase<br/>Replication Complete]
    end

    subgraph "Read Protocol"
        TIMESTAMP[Read Timestamp<br/>From TrueTime]
        QUORUM[Quorum Read<br/>Latest Committed]
        CONSISTENT[Consistent Data<br/>External Consistency]
    end

    subgraph "Failure Handling"
        LEADER_FAIL[Leader Failure<br/>Detection]
        ELECTION[Leader Election<br/>Paxos Protocol]
        RECOVERY[Log Recovery<br/>State Synchronization]
        CONTINUE[Continue Operations<br/>Automatic Failover]
    end

    LEADER --> PROPOSE
    PROPOSE --> PREPARE
    PREPARE --> ACCEPT
    ACCEPT --> LEARN

    LEADER --> TIMESTAMP
    TIMESTAMP --> QUORUM
    QUORUM --> CONSISTENT

    LEADER_FAIL --> ELECTION
    ELECTION --> RECOVERY
    RECOVERY --> CONTINUE

    style LEADER fill:#2196f3
    style PROPOSE fill:#ffb74d
    style TIMESTAMP fill:#4caf50
    style LEADER_FAIL fill:#ba68c8
```

## Data Model and Interleaving

```mermaid
graph TD
    subgraph "Table Hierarchy"
        ROOT[Root Table<br/>Users]
        CHILD1[Child Table 1<br/>UserPosts<br/>INTERLEAVE IN PARENT Users]
        CHILD2[Child Table 2<br/>UserComments<br/>INTERLEAVE IN PARENT UserPosts]
        GRANDCHILD[Grandchild Table<br/>CommentLikes<br/>INTERLEAVE IN PARENT UserComments]
    end

    subgraph "Physical Storage"
        SPLIT1[Split 1<br/>UserId: 1-1000]
        SPLIT2[Split 2<br/>UserId: 1001-2000]
        SPLIT3[Split 3<br/>UserId: 2001-3000]
    end

    subgraph "Data Distribution"
        TABLET1[Tablet 1<br/>Split 1 Data]
        TABLET2[Tablet 2<br/>Split 2 Data]
        TABLET3[Tablet 3<br/>Split 3 Data]
    end

    subgraph "Query Optimization"
        PARENT_SCAN[Parent Scan<br/>Users Table]
        CHILD_JOIN[Child Join<br/>Co-located Data]
        INDEX_SCAN[Index Scan<br/>Secondary Indexes]
        EFFICIENT[Efficient Joins<br/>No Network Calls]
    end

    ROOT --> CHILD1
    CHILD1 --> CHILD2
    CHILD2 --> GRANDCHILD

    ROOT --> SPLIT1
    ROOT --> SPLIT2
    ROOT --> SPLIT3

    SPLIT1 --> TABLET1
    SPLIT2 --> TABLET2
    SPLIT3 --> TABLET3

    TABLET1 --> PARENT_SCAN
    TABLET2 --> CHILD_JOIN
    TABLET3 --> INDEX_SCAN
    CHILD_JOIN --> EFFICIENT

    style ROOT fill:#2196f3
    style SPLIT1 fill:#ffb74d
    style TABLET1 fill:#4caf50
    style PARENT_SCAN fill:#ba68c8
```

## Multi-Region Deployment Architecture

```mermaid
graph LR
    subgraph "Region A (US-West)"
        ZONE_A1[Zone A1<br/>Leader Paxos Group]
        ZONE_A2[Zone A2<br/>Replica Paxos Group]
        ZONE_A3[Zone A3<br/>Witness Paxos Group]
    end

    subgraph "Region B (US-Central)"
        ZONE_B1[Zone B1<br/>Replica Paxos Group]
        ZONE_B2[Zone B2<br/>Replica Paxos Group]
        ZONE_B3[Zone B3<br/>Witness Paxos Group]
    end

    subgraph "Region C (US-East)"
        ZONE_C1[Zone C1<br/>Replica Paxos Group]
        ZONE_C2[Zone C2<br/>Replica Paxos Group]
        ZONE_C3[Zone C3<br/>Witness Paxos Group]
    end

    subgraph "Global Load Balancing"
        GLB[Cloud Load Balancer<br/>Global Anycast IP]
        DNS[Cloud DNS<br/>Geographic Routing]
        HEALTH[Health Checks<br/>Regional Failover]
    end

    subgraph "Client Applications"
        APP_WEST[West Coast App<br/>Low Latency]
        APP_EAST[East Coast App<br/>Low Latency]
        APP_GLOBAL[Global App<br/>Anycast Routing]
    end

    ZONE_A1 --> ZONE_B1
    ZONE_A1 --> ZONE_C1
    ZONE_B1 --> ZONE_C1

    GLB --> DNS
    DNS --> HEALTH

    APP_WEST --> GLB
    APP_EAST --> GLB
    APP_GLOBAL --> GLB

    GLB --> ZONE_A1
    GLB --> ZONE_B1
    GLB --> ZONE_C1

    style ZONE_A1 fill:#2196f3
    style GLB fill:#ffb74d
    style APP_WEST fill:#4caf50
    style APP_GLOBAL fill:#ba68c8
```

## Transaction Processing Flow

```mermaid
graph TD
    subgraph "Read-Write Transaction"
        BEGIN[BEGIN TRANSACTION]
        READ[Read Operations<br/>Snapshot Isolation]
        COMPUTE[Compute Changes<br/>Application Logic]
        MUTATE[Mutation Operations<br/>INSERT/UPDATE/DELETE]
        COMMIT[COMMIT<br/>Two-Phase Commit]
    end

    subgraph "Two-Phase Commit Protocol"
        PREPARE[Prepare Phase<br/>Lock Resources]
        LOG[Write-ahead Log<br/>Transaction Record]
        VOTE[Vote Request<br/>To All Participants]
        DECISION[Commit Decision<br/>Coordinator Decision]
        ACKNOWLEDGE[Acknowledge<br/>All Participants]
    end

    subgraph "Concurrency Control"
        OPTIMISTIC[Optimistic Locking<br/>Version Checking]
        PESSIMISTIC[Pessimistic Locking<br/>Resource Locking]
        CONFLICT[Conflict Detection<br/>Version Mismatch]
        RETRY[Automatic Retry<br/>Exponential Backoff]
    end

    subgraph "Consistency Guarantees"
        SERIALIZABLE[Serializable Isolation<br/>Default Level]
        EXTERNAL_CONSISTENCY[External Consistency<br/>TrueTime-based]
        READ_YOUR_WRITES[Read Your Writes<br/>Session Consistency]
        MONOTONIC_READS[Monotonic Reads<br/>Timestamp Ordering]
    end

    BEGIN --> READ
    READ --> COMPUTE
    COMPUTE --> MUTATE
    MUTATE --> COMMIT

    COMMIT --> PREPARE
    PREPARE --> LOG
    LOG --> VOTE
    VOTE --> DECISION
    DECISION --> ACKNOWLEDGE

    MUTATE --> OPTIMISTIC
    MUTATE --> PESSIMISTIC
    OPTIMISTIC --> CONFLICT
    PESSIMISTIC --> CONFLICT
    CONFLICT --> RETRY

    COMMIT --> SERIALIZABLE
    SERIALIZABLE --> EXTERNAL_CONSISTENCY
    EXTERNAL_CONSISTENCY --> READ_YOUR_WRITES
    READ_YOUR_WRITES --> MONOTONIC_READS

    style BEGIN fill:#2196f3
    style PREPARE fill:#ffb74d
    style OPTIMISTIC fill:#4caf50
    style SERIALIZABLE fill:#ba68c8
```

## Query Execution and Optimization

```mermaid
graph LR
    subgraph "Query Processing"
        PARSE[Parse SQL<br/>Syntax Analysis]
        ANALYZE[Analyze<br/>Semantic Analysis]
        OPTIMIZE[Optimize<br/>Query Planning]
        EXECUTE[Execute<br/>Distributed Processing]
    end

    subgraph "Query Optimization"
        STATISTICS[Statistics<br/>Table/Index Stats]
        COST_MODEL[Cost Model<br/>Execution Cost]
        PLAN_SELECTION[Plan Selection<br/>Best Strategy]
        INDEX_CHOICE[Index Choice<br/>Access Methods]
    end

    subgraph "Distributed Execution"
        COORDINATOR[Coordinator<br/>Query Planning]
        WORKERS[Worker Nodes<br/>Data Processing]
        SHUFFLE[Shuffle Phase<br/>Data Redistribution]
        AGGREGATE[Aggregate<br/>Result Combination]
    end

    subgraph "Performance Monitoring"
        EXECUTION_STATS[Execution Stats<br/>Time, CPU, I/O]
        QUERY_PLAN[Query Plan<br/>Visualization]
        BOTTLENECK[Bottleneck Analysis<br/>Slowest Operations]
        RECOMMENDATIONS[Optimization<br/>Recommendations]
    end

    PARSE --> ANALYZE
    ANALYZE --> OPTIMIZE
    OPTIMIZE --> EXECUTE

    OPTIMIZE --> STATISTICS
    STATISTICS --> COST_MODEL
    COST_MODEL --> PLAN_SELECTION
    PLAN_SELECTION --> INDEX_CHOICE

    EXECUTE --> COORDINATOR
    COORDINATOR --> WORKERS
    WORKERS --> SHUFFLE
    SHUFFLE --> AGGREGATE

    EXECUTE --> EXECUTION_STATS
    EXECUTION_STATS --> QUERY_PLAN
    QUERY_PLAN --> BOTTLENECK
    BOTTLENECK --> RECOMMENDATIONS

    style PARSE fill:#2196f3
    style STATISTICS fill:#ffb74d
    style COORDINATOR fill:#4caf50
    style EXECUTION_STATS fill:#ba68c8
```

## Change Streams and Real-Time Processing

```mermaid
graph TD
    subgraph "Change Stream Creation"
        TABLE[Source Table<br/>UserPosts]
        CHANGE_STREAM[Change Stream<br/>CREATE CHANGE STREAM]
        RETENTION[Retention Period<br/>Data Retention]
        FILTER[Value Capture<br/>OLD/NEW Values]
    end

    subgraph "Change Data Capture"
        TRANSACTION[Transaction Commit<br/>Data Changes]
        RECORD[Change Record<br/>Timestamp, Keys, Values]
        BUFFER[Buffer Changes<br/>In-Memory Queue]
        PUBLISH[Publish to Pub/Sub<br/>Real-Time Streaming]
    end

    subgraph "Stream Processing"
        DATAFLOW[Dataflow Pipeline<br/>Stream Processing]
        BIGQUERY[BigQuery<br/>Data Warehouse]
        FUNCTIONS[Cloud Functions<br/>Event Processing]
        SPARK[Dataproc Spark<br/>Real-Time Analytics]
    end

    subgraph "Use Cases"
        AUDIT[Audit Logging<br/>Compliance]
        CACHE[Cache Invalidation<br/>Application Cache]
        SEARCH[Search Indexing<br/>Elasticsearch]
        ML[ML Model Updates<br/>Feature Stores]
    end

    TABLE --> CHANGE_STREAM
    CHANGE_STREAM --> RETENTION
    RETENTION --> FILTER

    TRANSACTION --> RECORD
    RECORD --> BUFFER
    BUFFER --> PUBLISH

    PUBLISH --> DATAFLOW
    PUBLISH --> BIGQUERY
    PUBLISH --> FUNCTIONS
    PUBLISH --> SPARK

    DATAFLOW --> AUDIT
    BIGQUERY --> CACHE
    FUNCTIONS --> SEARCH
    SPARK --> ML

    style TABLE fill:#2196f3
    style TRANSACTION fill:#ffb74d
    style DATAFLOW fill:#4caf50
    style AUDIT fill:#ba68c8
```

## Backup and Recovery Architecture

```mermaid
graph LR
    subgraph "Backup Creation"
        SCHEDULED[Scheduled Backup<br/>Daily Automated]
        ON_DEMAND[On-Demand Backup<br/>Manual Creation]
        POINT_IN_TIME[PITR Backup<br/>Continuous Backup]
        EXPORT[Export to GCS<br/>SQL Dump/CSV]
    end

    subgraph "Backup Storage"
        REGIONAL[Regional Storage<br/>Same Region]
        MULTI_REGIONAL[Multi-Regional<br/>Cross-Region]
        VERSIONED[Versioned Backups<br/>Retention Policy]
        ENCRYPTED[Encrypted Storage<br/>AES-256]
    end

    subgraph "Recovery Process"
        RESTORE[Restore Instance<br/>New Instance]
        PITR_RECOVERY[PITR Recovery<br/>Timestamp Restore]
        VALIDATE[Data Validation<br/>Integrity Checks]
        CUTOVER[Application Cutover<br/>Traffic Switch]
    end

    subgraph "Disaster Recovery"
        REGIONAL_FAILOVER[Regional Failover<br/>Automatic]
        MANUAL_FAILOVER[Manual Failover<br/>Planned Maintenance]
        CROSS_REGION[Cross-Region Recovery<br/>Disaster Scenarios]
        BUSINESS_CONTINUITY[Business Continuity<br/>RTO/RPO Compliance]
    end

    SCHEDULED --> REGIONAL
    ON_DEMAND --> MULTI_REGIONAL
    POINT_IN_TIME --> VERSIONED
    EXPORT --> ENCRYPTED

    REGIONAL --> RESTORE
    MULTI_REGIONAL --> PITR_RECOVERY
    VERSIONED --> VALIDATE
    ENCRYPTED --> CUTOVER

    RESTORE --> REGIONAL_FAILOVER
    PITR_RECOVERY --> MANUAL_FAILOVER
    VALIDATE --> CROSS_REGION
    CUTOVER --> BUSINESS_CONTINUITY

    style SCHEDULED fill:#2196f3
    style REGIONAL fill:#ffb74d
    style RESTORE fill:#4caf50
    style REGIONAL_FAILOVER fill:#ba68c8
```

## Performance Monitoring Dashboard

```mermaid
graph TD
    subgraph "System Metrics"
        CPU_UTIL[CPU Utilization<br/>Processing Units]
        STORAGE_UTIL[Storage Utilization<br/>GB Used/Total]
        NETWORK_IO[Network I/O<br/>Read/Write Throughput]
        LATENCY[Query Latency<br/>P50, P95, P99]
    end

    subgraph "Database Metrics"
        ACTIVE_CONNECTIONS[Active Connections<br/>Concurrent Sessions]
        TRANSACTION_RATE[Transaction Rate<br/>TPS/QPS]
        LOCK_CONFLICTS[Lock Conflicts<br/>Deadlocks/Timeouts]
        QUERY_DISTRIBUTION[Query Distribution<br/>Read/Write Mix]
    end

    subgraph "SLA Compliance"
        AVAILABILITY[Availability<br/>Uptime Percentage]
        LATENCY_SLA[Latency SLA<br/>Response Time]
        THROUGHPUT_SLA[Throughput SLA<br/>Operations/Second]
        ERROR_RATE[Error Rate<br/>Failed Operations]
    end

    subgraph "Optimization Insights"
        SLOW_QUERIES[Slow Queries<br/>Top 10 by Time]
        INDEX_EFFICIENCY[Index Efficiency<br/>Usage Statistics]
        SCHEMA_RECOMMENDATIONS[Schema Recommendations<br/>Interleaving/Indexing]
        CAPACITY_PLANNING[Capacity Planning<br/>Scaling Recommendations]
    end

    CPU_UTIL --> AVAILABILITY
    STORAGE_UTIL --> THROUGHPUT_SLA
    NETWORK_IO --> LATENCY_SLA
    LATENCY --> ERROR_RATE

    ACTIVE_CONNECTIONS --> SLOW_QUERIES
    TRANSACTION_RATE --> INDEX_EFFICIENCY
    LOCK_CONFLICTS --> SCHEMA_RECOMMENDATIONS
    QUERY_DISTRIBUTION --> CAPACITY_PLANNING

    style CPU_UTIL fill:#2196f3
    style ACTIVE_CONNECTIONS fill:#ffb74d
    style AVAILABILITY fill:#4caf50
    style SLOW_QUERIES fill:#ba68c8
```

## Cost Optimization Strategies

```mermaid
graph TD
    A[Spanner Cost Optimization] --> B[Compute Optimization]
    A --> C[Storage Optimization]
    A --> D[Query Optimization]
    A --> E[Architecture Optimization]

    B --> B1[Processing Units<br/>Right-size capacity]
    B --> B2[Auto-scaling<br/>Scale with demand]
    B --> B3[Regional vs Multi-regional<br/>Cost vs availability]
    B --> B4[Peak/off-peak usage<br/>Schedule heavy operations]

    C --> C1[Data compression<br/>Automatic optimization]
    C --> C2[Backup retention<br/>Configure appropriate periods]
    C --> C3[Data lifecycle<br/>Archive old data]
    C --> C4[Storage efficiency<br/>Schema optimization]

    D --> D1[Query optimization<br/>Efficient SQL]
    D --> D2[Index usage<br/>Proper indexing]
    D --> D3[Read-only transactions<br/>For analytics]
    D --> D4[Batch operations<br/>Partitioned DML]

    E --> E1[Schema design<br/>Interleaved tables]
    E --> E2[Data distribution<br/>Key design]
    E --> E3[Workload isolation<br/>Separate instances]
    E --> E4[Change streams<br/>Efficient CDC]

    style A fill:#2196f3
    style B fill:#ffb74d
    style C fill:#4caf50
    style D fill:#ba68c8
    style E fill:#2196f3
```

## Security and Compliance Architecture

```mermaid
graph TB
    subgraph "Access Control"
        IAM[IAM Roles<br/>spanner.databaseAdmin]
        DATABASE_USERS[Database Users<br/>GRANT/REVOKE]
        SERVICE_ACCOUNTS[Service Accounts<br/>Application Identity]
        AUDIT_LOGS[Audit Logs<br/>Cloud Logging]
    end

    subgraph "Data Protection"
        ENCRYPTION_AT_REST[Encryption at Rest<br/>AES-256]
        ENCRYPTION_IN_TRANSIT[Encryption in Transit<br/>TLS 1.2+]
        CMEK[Customer-Managed Keys<br/>Cloud KMS]
        BACKUP_ENCRYPTION[Backup Encryption<br/>Automatic]
    end

    subgraph "Network Security"
        VPC_NETWORK[VPC Networks<br/>Private Connectivity]
        SERVICE_CONTROLS[VPC Service Controls<br/>Data Exfiltration Prevention]
        PRIVATE_ENDPOINTS[Private Endpoints<br/>Secure Access]
        FIREWALL_RULES[Firewall Rules<br/>Access Control]
    end

    subgraph "Compliance"
        SOC2[SOC 2 Compliance<br/>Security Controls]
        HIPAA[HIPAA Compliance<br/>Healthcare Data]
        PCI_DSS[PCI DSS Compliance<br/>Payment Data]
        GDPR[GDPR Compliance<br/>Data Privacy]
    end

    IAM --> SERVICE_ACCOUNTS
    SERVICE_ACCOUNTS --> DATABASE_USERS
    DATABASE_USERS --> AUDIT_LOGS

    ENCRYPTION_AT_REST --> CMEK
    ENCRYPTION_IN_TRANSIT --> BACKUP_ENCRYPTION

    VPC_NETWORK --> SERVICE_CONTROLS
    SERVICE_CONTROLS --> PRIVATE_ENDPOINTS
    PRIVATE_ENDPOINTS --> FIREWALL_RULES

    SOC2 --> HIPAA
    HIPAA --> PCI_DSS
    PCI_DSS --> GDPR

    style IAM fill:#2196f3
    style ENCRYPTION_AT_REST fill:#ffb74d
    style VPC_NETWORK fill:#4caf50
    style SOC2 fill:#ba68c8
```

## Integration with GCP Ecosystem

```mermaid
graph TD
    SPANNER[Cloud Spanner] --> BIGQUERY
    SPANNER --> DATAFLOW
    SPANNER --> PUBSUB
    SPANNER --> AI_PLATFORM

    BIGQUERY --> FEDERATED[Federated Queries<br/>SQL Analytics]
    BIGQUERY --> DATA_TRANSFER[Data Transfer Service<br/>Automated ETL]

    DATAFLOW --> SPANNER_IO[SpannerIO<br/>Read/Write Operations]
    DATAFLOW --> CHANGE_STREAMS[Change Streams<br/>Real-time Processing]

    PUBSUB --> STREAMING[Streaming Analytics<br/>Real-time Events]
    PUBSUB --> MESSAGING[Event-driven<br/>Applications]

    AI_PLATFORM --> VERTEX_AI[Vertex AI<br/>ML Pipelines]
    AI_PLATFORM --> FEATURE_STORE[Feature Store<br/>ML Features]

    FEDERATED --> ANALYTICS[Real-time Analytics<br/>Transactional Data]
    DATA_TRANSFER --> WAREHOUSE[Data Warehouse<br/>Historical Data]

    SPANNER_IO --> ETL[ETL Pipelines<br/>Data Processing]
    CHANGE_STREAMS --> CDC[Change Data Capture<br/>Event Streaming]

    STREAMING --> DASHBOARDS[Real-time Dashboards<br/>Live Metrics]
    MESSAGING --> MICROSERVICES[Event-driven<br/>Microservices]

    VERTEX_AI --> ML_MODELS[ML Model Training<br/>Spanner Data]
    FEATURE_STORE --> FEATURES[Feature Engineering<br/>Real-time Features]

    style SPANNER fill:#2196f3
    style BIGQUERY fill:#ffb74d
    style FEDERATED fill:#4caf50
    style SPANNER_IO fill:#ba68c8
```

This visual guide illustrates Cloud Spanner's unique architecture combining relational database semantics with global scale, highlighting its TrueTime-based consistency, Paxos replication, and integration with the broader Google Cloud ecosystem.
