# BigQuery Visual Architecture and Diagrams

## Overview

This document provides visual representations of BigQuery's architecture, data flows, and integration patterns using Mermaid diagrams.

## Core Architecture

### BigQuery Service Architecture

```mermaid
graph TB
    subgraph "Client Layer"
        API[BigQuery API]
        CLI[BigQuery CLI]
        UI[BigQuery Web UI]
        SDK[Client Libraries<br/>Python, Java, Go]
    end

    subgraph "Control Plane"
        QueryPlanner[Query Planner]
        JobScheduler[Job Scheduler]
        MetadataManager[Metadata Manager]
        AccessControl[IAM & Access Control]
    end

    subgraph "Data Plane"
        StorageLayer[Storage Layer<br/>Colossus File System]
        ComputeLayer[Compute Layer<br/>Dremel Query Engine]
        ShuffleLayer[Shuffle Layer<br/>Data Movement]
    end

    subgraph "Storage Backend"
        RegionalStorage[Regional Storage]
        MultiRegionalStorage[Multi-Regional Storage]
        LongTermStorage[Long-term Storage<br/>Coldline/Nearline]
    end

    API --> QueryPlanner
    CLI --> QueryPlanner
    UI --> QueryPlanner
    SDK --> QueryPlanner

    QueryPlanner --> JobScheduler
    JobScheduler --> MetadataManager
    MetadataManager --> AccessControl

    JobScheduler --> ComputeLayer
    ComputeLayer --> StorageLayer
    ComputeLayer --> ShuffleLayer

    StorageLayer --> RegionalStorage
    StorageLayer --> MultiRegionalStorage
    StorageLayer --> LongTermStorage

    style API fill:#2196f3
    style QueryPlanner fill:#ffb74d
    style StorageLayer fill:#4caf50
```

### Data Ingestion Architecture

```mermaid
graph TD
    subgraph "Data Sources"
        GCS[Cloud Storage]
        PubSub[Pub/Sub]
        Dataflow[Dataflow]
        TransferService[Data Transfer Service]
        Apps[Applications]
        IoT[IoT Devices]
    end

    subgraph "Ingestion Methods"
        BatchLoad[Batch Loading<br/>LOAD DATA]
        StreamingInsert[Streaming Inserts<br/>insertAll()]
        TransferJobs[Transfer Jobs<br/>Scheduled Imports]
        ExternalTables[External Tables<br/>Federated Queries]
    end

    subgraph "BigQuery Processing"
        IngestionService[Ingestion Service]
        StreamingBuffer[Streaming Buffer<br/>Temporary Storage]
        StorageManager[Storage Manager]
    end

    subgraph "BigQuery Tables"
        NativeTables[Native Tables<br/>Managed Storage]
        PartitionedTables[Partitioned Tables<br/>Time-based/Range]
        ClusteredTables[Clustered Tables<br/>Sorted Storage]
    end

    GCS --> BatchLoad
    PubSub --> StreamingInsert
    Dataflow --> StreamingInsert
    TransferService --> TransferJobs
    Apps --> StreamingInsert
    IoT --> StreamingInsert
    GCS --> ExternalTables

    BatchLoad --> IngestionService
    StreamingInsert --> IngestionService
    TransferJobs --> IngestionService
    ExternalTables --> IngestionService

    IngestionService --> StreamingBuffer
    StreamingBuffer --> StorageManager
    IngestionService --> StorageManager

    StorageManager --> NativeTables
    StorageManager --> PartitionedTables
    StorageManager --> ClusteredTables

    style GCS fill:#2196f3
    style IngestionService fill:#ffb74d
    style NativeTables fill:#4caf50
```

## Data Organization

### Dataset and Table Hierarchy

```mermaid
graph TD
    subgraph "Project"
        Project[BigQuery Project<br/>billing & quotas]
    end

    subgraph "Datasets"
        Dataset1[Dataset 1<br/>us-central1<br/>Labels: env=prod]
        Dataset2[Dataset 2<br/>eu-west1<br/>Labels: env=dev]
        Dataset3[Dataset 3<br/>asia-east1<br/>Labels: env=test]
    end

    subgraph "Tables in Dataset 1"
        Table1[users<br/>Native Table<br/>1.2 TB]
        Table2[orders<br/>Partitioned by date<br/>500 GB]
        Table3[products<br/>Clustered by category<br/>100 GB]
        Table4[sales_summary<br/>External Table<br/>Cloud Storage]
    end

    subgraph "Table Details"
        Schema[Schema<br/>Columns & Types]
        Partitioning[Partitioning<br/>Strategy]
        Clustering[Clustering<br/>Columns]
        Metadata[Metadata<br/>Created, Modified]
    end

    Project --> Dataset1
    Project --> Dataset2
    Project --> Dataset3

    Dataset1 --> Table1
    Dataset1 --> Table2
    Dataset1 --> Table3
    Dataset1 --> Table4

    Table1 --> Schema
    Table2 --> Partitioning
    Table3 --> Clustering
    Table4 --> Metadata

    style Project fill:#2196f3
    style Dataset1 fill:#ffb74d
    style Table1 fill:#4caf50
```

### Partitioning and Clustering

```mermaid
graph TD
    subgraph "Partitioned Table"
        Partition1[Partition 2023-01<br/>Jan Data]
        Partition2[Partition 2023-02<br/>Feb Data]
        Partition3[Partition 2023-03<br/>Mar Data]
        Partition4[Partition 2023-04<br/>Apr Data]
    end

    subgraph "Clustered Data within Partition"
        ClusterA[Cluster A<br/>category = 'Electronics'<br/>Sorted by product_id]
        ClusterB[Cluster B<br/>category = 'Books'<br/>Sorted by product_id]
        ClusterC[Cluster C<br/>category = 'Clothing'<br/>Sorted by product_id]
    end

    subgraph "Query Optimization"
        Pruning[Partition Pruning<br/>WHERE date = '2023-01']
        Clustering[Clustering Benefits<br/>WHERE category = 'Books']
        Combined[Combined Optimization<br/>Both Pruning & Clustering]
    end

    Partition1 --> ClusterA
    Partition1 --> ClusterB
    Partition1 --> ClusterC

    Partition2 --> ClusterA
    Partition2 --> ClusterB
    Partition2 --> ClusterC

    ClusterA --> Pruning
    ClusterB --> Clustering
    Pruning --> Combined
    Clustering --> Combined

    style Partition1 fill:#2196f3
    style ClusterA fill:#ffb74d
    style Pruning fill:#4caf50
```

## Query Execution Flow

### BigQuery Query Processing

```mermaid
graph LR
    subgraph "Query Submission"
        Client[Client Application]
        SQL[SQL Query]
        Parameters[Query Parameters]
    end

    subgraph "Query Planning"
        Parser[SQL Parser]
        Validator[Query Validator]
        Optimizer[Query Optimizer]
        PlanGenerator[Execution Plan Generator]
    end

    subgraph "Execution Engine"
        Coordinator[Query Coordinator]
        Workers[Dremel Workers<br/>Distributed Processing]
        Shuffler[Shuffle Service<br/>Data Movement]
    end

    subgraph "Storage Access"
        Storage[Colossus Storage]
        Cache[Query Result Cache]
        Metadata[Metadata Service]
    end

    subgraph "Result Processing"
        Aggregator[Result Aggregator]
        Formatter[Result Formatter]
        Streaming[Streaming Results]
    end

    Client --> SQL
    SQL --> Parser
    Parser --> Validator
    Validator --> Optimizer
    Optimizer --> PlanGenerator

    PlanGenerator --> Coordinator
    Coordinator --> Workers
    Workers --> Shuffler
    Shuffler --> Workers

    Workers --> Storage
    Workers --> Cache
    Workers --> Metadata

    Workers --> Aggregator
    Aggregator --> Formatter
    Formatter --> Streaming
    Streaming --> Client

    style Client fill:#2196f3
    style Optimizer fill:#ffb74d
    style Workers fill:#4caf50
```

### Distributed Query Execution

```mermaid
graph TD
    subgraph "Query Coordinator"
        Coordinator[Query Coordinator<br/>Single Node]
    end

    subgraph "Worker Nodes"
        Worker1[Worker 1<br/>Process Slice 1]
        Worker2[Worker 2<br/>Process Slice 2]
        Worker3[Worker 3<br/>Process Slice 3]
        Worker4[Worker 4<br/>Process Slice 4]
    end

    subgraph "Shuffle Service"
        Shuffle1[Shuffle 1<br/>Data Exchange]
        Shuffle2[Shuffle 2<br/>Data Exchange]
        Shuffle3[Shuffle 3<br/>Data Exchange]
    end

    subgraph "Storage Layer"
        Storage1[Storage Node 1<br/>Data Slice 1]
        Storage2[Storage Node 2<br/>Data Slice 2]
        Storage3[Storage Node 3<br/>Data Slice 3]
        Storage4[Storage Node 4<br/>Data Slice 4]
    end

    Coordinator --> Worker1
    Coordinator --> Worker2
    Coordinator --> Worker3
    Coordinator --> Worker4

    Worker1 --> Shuffle1
    Worker2 --> Shuffle1
    Worker3 --> Shuffle2
    Worker4 --> Shuffle2

    Shuffle1 --> Shuffle3
    Shuffle2 --> Shuffle3

    Shuffle3 --> Worker1
    Shuffle3 --> Worker2
    Shuffle3 --> Worker3
    Shuffle3 --> Worker4

    Worker1 --> Storage1
    Worker2 --> Storage2
    Worker3 --> Storage3
    Worker4 --> Storage4

    style Coordinator fill:#2196f3
    style Shuffle1 fill:#ffb74d
    style Storage1 fill:#4caf50
```

## Integration Patterns

### BigQuery with Google Cloud Ecosystem

```mermaid
graph TD
    subgraph "Data Sources"
        GCS[Cloud Storage<br/>Data Lake]
        PubSub[Pub/Sub<br/>Streaming Data]
        Bigtable[Bigtable<br/>NoSQL Data]
        Spanner[Spanner<br/>Relational Data]
    end

    subgraph "Data Processing"
        Dataflow[Dataflow<br/>ETL/ELT]
        Dataproc[Dataproc<br/>Hadoop/Spark]
        Dataprep[Dataprep<br/>Data Preparation]
    end

    subgraph "BigQuery"
        BQ[BigQuery<br/>Data Warehouse]
        BQML[BigQuery ML<br/>Machine Learning]
        BI[BI Engine<br/>Fast Analytics]
    end

    subgraph "Analytics & ML"
        Looker[Looker<br/>Business Intelligence]
        VertexAI[Vertex AI<br/>ML Platform]
        AutoML[AutoML<br/>Automated ML]
    end

    subgraph "Consumption"
        Sheets[Sheets<br/>Ad-hoc Analysis]
        DataStudio[Data Studio<br/>Dashboards]
        Apps[Custom Applications<br/>APIs]
    end

    GCS --> Dataflow
    PubSub --> Dataflow
    Bigtable --> Dataflow
    Spanner --> Dataflow

    Dataflow --> Dataproc
    Dataproc --> Dataflow

    Dataflow --> BQ
    Dataproc --> BQ
    Dataprep --> BQ

    BQ --> BQML
    BQ --> BI

    BQ --> Looker
    BQML --> VertexAI
    BI --> Looker

    Looker --> Sheets
    Looker --> DataStudio
    VertexAI --> Apps
    AutoML --> Apps

    style GCS fill:#2196f3
    style BQ fill:#ffb74d
    style Looker fill:#4caf50
```

### Real-time Analytics Pipeline

```mermaid
graph LR
    subgraph "Data Sources"
        IoT[IoT Devices]
        Apps[Mobile Apps]
        Web[Web Events]
        Logs[Application Logs]
    end

    subgraph "Streaming Ingestion"
        PubSub[Cloud Pub/Sub<br/>Message Queue]
        Dataflow[Dataflow<br/>Stream Processing]
    end

    subgraph "BigQuery"
        StreamingBuffer[Streaming Buffer<br/>Real-time Data]
        NativeTables[Native Tables<br/>Historical Data]
        MaterializedViews[Materialized Views<br/>Pre-computed Results]
    end

    subgraph "Real-time Analytics"
        BI[BQ BI Engine<br/>Sub-second Queries]
        ML[BQ ML<br/>Real-time Predictions]
    end

    subgraph "Consumption"
        Dashboards[Real-time Dashboards]
        Alerts[Real-time Alerts]
        APIs[Real-time APIs]
    end

    IoT --> PubSub
    Apps --> PubSub
    Web --> PubSub
    Logs --> PubSub

    PubSub --> Dataflow
    Dataflow --> StreamingBuffer
    StreamingBuffer --> NativeTables
    NativeTables --> MaterializedViews

    StreamingBuffer --> BI
    MaterializedViews --> BI
    StreamingBuffer --> ML

    BI --> Dashboards
    BI --> Alerts
    ML --> APIs

    style IoT fill:#2196f3
    style StreamingBuffer fill:#ffb74d
    style BI fill:#4caf50
```

## Security Architecture

### BigQuery Security Model

```mermaid
graph TD
    subgraph "Identity Management"
        IAM[IAM<br/>Identity & Access Management]
        ServiceAccounts[Service Accounts<br/>Programmatic Access]
        Groups[Google Groups<br/>User Groups]
    end

    subgraph "Access Control"
        ProjectLevel[Project Level<br/>Viewer, Editor, Owner]
        DatasetLevel[Dataset Level<br/>BigQuery Data Viewer/Editor]
        TableLevel[Table Level<br/>Column-level Security]
        RowLevel[Row Level<br/>Row Access Policies]
    end

    subgraph "Data Protection"
        Encryption[Encryption at Rest<br/>Google-managed Keys]
        CMEK[Customer-Managed<br/>Encryption Keys]
        TLS[TLS in Transit<br/>Encrypted Communication]
    end

    subgraph "Audit & Compliance"
        AuditLogs[Cloud Audit Logs<br/>All Operations]
        DataAccess[Data Access Logs<br/>Query Auditing]
        Compliance[SOC 2, HIPAA, PCI DSS<br/>Compliance Certifications]
    end

    IAM --> ProjectLevel
    ServiceAccounts --> ProjectLevel
    Groups --> ProjectLevel

    ProjectLevel --> DatasetLevel
    DatasetLevel --> TableLevel
    TableLevel --> RowLevel

    RowLevel --> Encryption
    RowLevel --> CMEK
    RowLevel --> TLS

    Encryption --> AuditLogs
    CMEK --> DataAccess
    TLS --> Compliance

    style IAM fill:#2196f3
    style DatasetLevel fill:#ffb74d
    style Encryption fill:#4caf50
```

### Data Encryption Flow

```mermaid
graph TD
    subgraph "Data at Rest"
        RawData[Raw Data]
        Compression[Compression<br/>Snappy/Zstandard]
        Encryption[Encryption<br/>AES-256]
        Storage[Storage<br/>Colossus]
    end

    subgraph "Key Management"
        GoogleKeys[Google-Managed Keys<br/>Automatic Rotation]
        CMEK[Customer-Managed Keys<br/>Cloud KMS]
        CSEK[Customer-Supplied Keys<br/>Application Level]
    end

    subgraph "Data in Transit"
        TLS12[TLS 1.2/1.3<br/>API Communication]
        ClientEncryption[Client-side Encryption<br/>Before Upload]
    end

    subgraph "Query Processing"
        Decryption[Decryption<br/>Query Time]
        Processing[Query Processing<br/>In Memory]
        ReEncryption[Re-encryption<br/>Results]
    end

    RawData --> Compression
    Compression --> Encryption
    Encryption --> Storage

    Storage --> GoogleKeys
    Storage --> CMEK
    Storage --> CSEK

    Storage --> TLS12
    RawData --> ClientEncryption
    ClientEncryption --> TLS12

    Storage --> Decryption
    Decryption --> Processing
    Processing --> ReEncryption

    style RawData fill:#2196f3
    style Encryption fill:#ffb74d
    style Decryption fill:#4caf50
```

## Performance Optimization

### Query Performance Patterns

```mermaid
graph TD
    subgraph "Query Types"
        Interactive[Interactive Queries<br/>Ad-hoc Analysis]
        Batch[Batch Queries<br/>ETL Processes]
        Reporting[Reporting Queries<br/>Scheduled Reports]
        Dashboard[Dashboard Queries<br/>Real-time Dashboards]
    end

    subgraph "Optimization Strategies"
        Partitioning[Partition Pruning<br/>Time-based Filters]
        Clustering[Clustering Benefits<br/>Sorted Data Access]
        Caching[Query Result Cache<br/>Repeated Queries]
        BI[BI Engine<br/>Sub-second Latency]
    end

    subgraph "Performance Metrics"
        BytesProcessed[Bytes Processed<br/>Cost Indicator]
        SlotTime[Slot Time<br/>Compute Usage]
        CacheHit[Cache Hit Rate<br/>Efficiency Metric]
        QueryTime[Query Execution Time<br/>User Experience]
    end

    Interactive --> Partitioning
    Batch --> Clustering
    Reporting --> Caching
    Dashboard --> BI

    Partitioning --> BytesProcessed
    Clustering --> SlotTime
    Caching --> CacheHit
    BI --> QueryTime

    style Interactive fill:#2196f3
    style Partitioning fill:#ffb74d
    style BytesProcessed fill:#4caf50
```

### Cost Optimization Architecture

```mermaid
graph TD
    subgraph "Cost Factors"
        StorageCost[Storage Cost<br/>Active vs Long-term]
        QueryCost[Query Cost<br/>Bytes Processed]
        StreamingCost[Streaming Cost<br/>Inserts per Month]
        DMLCost[DML Cost<br/>Modifications]
    end

    subgraph "Optimization Techniques"
        Partitioning[Partitioning<br/>Reduce Data Scanned]
        Clustering[Clustering<br/>Improve Compression]
        MaterializedViews[Materialized Views<br/>Pre-compute Results]
        QueryOptimization[Query Optimization<br/>Efficient SQL]
    end

    subgraph "Cost Monitoring"
        BillingExport[Billing Export<br/>Cost Analysis]
        AuditLogs[Audit Logs<br/>Usage Tracking]
        QueryHistory[Query History<br/>Performance Analysis]
    end

    subgraph "Cost Controls"
        Budgets[Budgets & Alerts<br/>Spending Limits]
        Quotas[Quotas<br/>Usage Limits]
        Reservations[Reservations<br/>Committed Use Discount]
    end

    StorageCost --> Partitioning
    QueryCost --> Clustering
    StreamingCost --> MaterializedViews
    DMLCost --> QueryOptimization

    Partitioning --> BillingExport
    Clustering --> AuditLogs
    MaterializedViews --> QueryHistory
    QueryOptimization --> BillingExport

    BillingExport --> Budgets
    AuditLogs --> Quotas
    QueryHistory --> Reservations

    style StorageCost fill:#2196f3
    style Partitioning fill:#ffb74d
    style BillingExport fill:#4caf50
```

## Machine Learning Integration

### BigQuery ML Workflow

```mermaid
graph LR
    subgraph "Data Preparation"
        RawData[Raw Data<br/>BigQuery Tables]
        FeatureEng[Feature Engineering<br/>SQL Transformations]
        TrainTestSplit[Train/Test Split<br/>Data Partitioning]
    end

    subgraph "Model Training"
        ModelTypes[Model Types<br/>Linear Reg, DNN, etc.]
        Hyperparameters[Hyperparameter Tuning<br/>Automated]
        Training[Distributed Training<br/>Dremel Engine]
    end

    subgraph "Model Management"
        ModelStorage[Model Storage<br/>BigQuery Models]
        Versioning[Model Versioning<br/>Timestamps]
        Evaluation[Model Evaluation<br/>Metrics & Validation]
    end

    subgraph "Inference"
        BatchPrediction[Batch Prediction<br/>SQL Functions]
        OnlinePrediction[Online Prediction<br/>Vertex AI]
        RealTime[Real-time Scoring<br/>Streaming Data]
    end

    RawData --> FeatureEng
    FeatureEng --> TrainTestSplit

    TrainTestSplit --> ModelTypes
    ModelTypes --> Hyperparameters
    Hyperparameters --> Training

    Training --> ModelStorage
    ModelStorage --> Versioning
    Versioning --> Evaluation

    Evaluation --> BatchPrediction
    Evaluation --> OnlinePrediction
    Evaluation --> RealTime

    style RawData fill:#2196f3
    style Training fill:#ffb74d
    style BatchPrediction fill:#4caf50
```

### ML Model Lifecycle

```mermaid
stateDiagram-v2
    [*] --> DataPrep: Prepare Training Data
    DataPrep --> ModelCreation: Create Model (CREATE MODEL)
    ModelCreation --> Training: Train Model
    Training --> Evaluation: Evaluate Performance
    Evaluation --> Deployed: Deploy Model
    Deployed --> Inference: Run Predictions
    Inference --> Monitoring: Monitor Performance
    Monitoring --> Retraining: Model Drift Detected
    Retraining --> Evaluation
    Monitoring --> [*]: Model Retired
```

## Multi-Cloud and Hybrid Architectures

### BigQuery Omni Architecture

```mermaid
graph TD
    subgraph "Google Cloud"
        BQGoogle[BigQuery<br/>Google Cloud]
        GCSGoogle[Cloud Storage<br/>Google Cloud]
    end

    subgraph "AWS"
        S3AWS[S3<br/>AWS]
        Athena[Athena<br/>AWS]
        Redshift[Redshift<br/>AWS]
    end

    subgraph "Azure"
        BlobAzure[Blob Storage<br/>Azure]
        Synapse[Synapse<br/>Azure]
        SQLDW[SQL Data Warehouse<br/>Azure]
    end

    subgraph "BigQuery Omni"
        OmniEngine[Omni Query Engine<br/>Cross-Cloud]
        FederatedQueries[Federated Queries<br/>External Tables]
        CrossCloudTransfer[Cross-Cloud Data Transfer]
    end

    BQGoogle --> OmniEngine
    GCSGoogle --> OmniEngine

    S3AWS --> FederatedQueries
    Athena --> FederatedQueries
    Redshift --> FederatedQueries

    BlobAzure --> FederatedQueries
    Synapse --> FederatedQueries
    SQLDW --> FederatedQueries

    FederatedQueries --> OmniEngine
    OmniEngine --> CrossCloudTransfer

    style BQGoogle fill:#2196f3
    style FederatedQueries fill:#ffb74d
    style OmniEngine fill:#4caf50
```

## Summary

These diagrams illustrate the key architectural patterns and data flows in BigQuery:

1. **Service Architecture**: Separation of storage and compute, distributed processing
2. **Data Ingestion**: Multiple methods for batch and streaming data
3. **Data Organization**: Hierarchical structure with partitioning and clustering
4. **Query Execution**: Distributed processing with Dremel engine
5. **Integration Patterns**: Deep integration with Google Cloud ecosystem
6. **Security Model**: Multi-layered security with encryption and access control
7. **Performance Optimization**: Partitioning, clustering, and caching strategies
8. **ML Integration**: End-to-end ML workflow within BigQuery
9. **Multi-Cloud**: Cross-cloud analytics with BigQuery Omni

These visual representations help understand how BigQuery components interact and how to design efficient data warehouse architectures.
