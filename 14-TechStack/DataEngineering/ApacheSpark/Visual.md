# Apache Spark Visual Architecture Guide

## Spark Application Architecture

```mermaid
graph TB
    %% Define styles
    classDef driverClass fill:#e3f2fd,stroke:#1976d2,stroke-width:3px,color:#0d47a1
    classDef clusterClass fill:#f3e5f5,stroke:#7b1fa2,stroke-width:3px,color:#4a148c
    classDef executorClass fill:#e8f5e8,stroke:#388e3c,stroke-width:2px,color:#1b5e20
    classDef storageClass fill:#fff3e0,stroke:#f57c00,stroke-width:2px,color:#e65100

    subgraph "🎯 Driver Program"
        DRIVER[📊 SparkContext<br/>SparkSession<br/>DAG Scheduler]
        CATALYST[⚡ Catalyst Optimizer<br/>Logical → Physical Plan]
        TASK_SCHEDULER[📋 Task Scheduler<br/>Resource Allocation]
    end

    subgraph "🏗️ Cluster Manager"
        STANDALONE[💻 Standalone<br/>Built-in Manager]
        YARN[🧵 YARN<br/>Hadoop Resource Manager]
        K8S[☸️ Kubernetes<br/>Container Orchestrator]
        MESOS[🔄 Mesos<br/>General-purpose Manager]
    end

    subgraph "⚙️ Worker Nodes"
        WORKER1[🖥️ Worker Node 1]
        WORKER2[🖥️ Worker Node 2]
        WORKERN[🖥️ Worker Node N]
    end

    subgraph "🚀 Executors"
        EXECUTOR1[⚡ Executor 1<br/>JVM Process<br/>Task Execution]
        EXECUTOR2[⚡ Executor 2<br/>JVM Process<br/>Task Execution]
        EXECUTOR3[⚡ Executor 3<br/>JVM Process<br/>Task Execution]
        EXECUTOR4[⚡ Executor 4<br/>JVM Process<br/>Task Execution]
    end

    subgraph "💾 Storage Systems"
        HDFS[📁 HDFS<br/>Distributed File System]
        S3[☁️ S3<br/>Object Storage]
        KAFKA[📨 Kafka<br/>Streaming Platform]
        CASSANDRA[🔗 Cassandra<br/>NoSQL Database]
    end

    DRIVER --> STANDALONE
    DRIVER --> YARN
    DRIVER --> K8S
    DRIVER --> MESOS

    STANDALONE --> WORKER1
    STANDALONE --> WORKER2
    STANDALONE --> WORKERN

    WORKER1 --> EXECUTOR1
    WORKER1 --> EXECUTOR2
    WORKER2 --> EXECUTOR3
    WORKER2 --> EXECUTOR4

    EXECUTOR1 --> HDFS
    EXECUTOR2 --> S3
    EXECUTOR3 --> KAFKA
    EXECUTOR4 --> CASSANDRA

    TASK_SCHEDULER --> EXECUTOR1
    TASK_SCHEDULER --> EXECUTOR2
    TASK_SCHEDULER --> EXECUTOR3
    TASK_SCHEDULER --> EXECUTOR4

    %% Apply styles
    class DRIVER,CATALYST,TASK_SCHEDULER driverClass
    class STANDALONE,YARN,K8S,MESOS clusterClass
    class EXECUTOR1,EXECUTOR2,EXECUTOR3,EXECUTOR4 executorClass
    class HDFS,S3,KAFKA,CASSANDRA storageClass
```

## RDD Execution Model

```mermaid
graph TD
    A[👨‍💻 User Code] --> B[SparkContext]
    B --> C{Transformations<br/>vs Actions}

    C -->|Transformations<br/>map, filter, join| D[🔄 Lazy Evaluation<br/>Build DAG]
    C -->|Actions<br/>collect, count, save| E[🚀 Trigger Execution<br/>DAG → Physical Plan]

    D --> F[📊 DAG Scheduler<br/>Stage Division]
    F --> G[📋 Task Scheduler<br/>Task Assignment]

    G --> H[⚡ Task Execution<br/>on Executors]
    H --> I{Data Locality<br/>Optimization}

    I -->|Local Data| J[💾 Local Read<br/>Fast Access]
    I -->|Remote Data| K[🌐 Network Transfer<br/>Shuffle Required]

    J --> L[⚙️ Task Processing<br/>Map/Filter/Reduce]
    K --> L

    L --> M[📤 Result Aggregation<br/>Reduce Operations]
    M --> N[💾 Storage<br/>HDFS/S3/Cache]

    E --> O[🎯 Result Return<br/>to Driver]
    N --> O
```

## Data Abstraction Layers

```mermaid
graph TD
    %% Define styles
    classDef rddClass fill:#e3f2fd,stroke:#1976d2,stroke-width:3px,color:#0d47a1
    classDef dataframeClass fill:#f3e5f5,stroke:#7b1fa2,stroke-width:3px,color:#4a148c
    classDef datasetClass fill:#e8f5e8,stroke:#388e3c,stroke-width:3px,color:#1b5e20
    classDef sqlClass fill:#fff3e0,stroke:#f57c00,stroke-width:2px,color:#e65100

    subgraph "🔧 RDD (Low-Level)"
        RDD_CORE[⚡ RDD Core<br/>Transformations & Actions]
        RDD_OPS[🔄 Operations<br/>map, filter, reduceByKey]
        RDD_PART[📦 Partitioning<br/>Hash, Range, Custom]
        RDD_DEP[🔗 Dependencies<br/>Narrow & Wide]
    end

    subgraph "📊 DataFrame (High-Level)"
        DF_SCHEMA[📋 Schema<br/>Column Names & Types]
        DF_OPT[⚡ Catalyst Optimizer<br/>Query Optimization]
        DF_API[🔧 DataFrame API<br/>SQL-like Operations]
        DF_TUNGSTEN[🏗️ Tungsten<br/>Memory Management]
    end

    subgraph "🔒 Dataset (Type-Safe)"
        DS_TYPE[✅ Type Safety<br/>Compile-time Checks]
        DS_ENCODER[🔄 Encoders<br/>Serialization/Deserialization]
        DS_OPT[⚡ Optimizer<br/>Same as DataFrame]
        DS_API[🔧 Dataset API<br/>Functional Programming]
    end

    subgraph "📝 Spark SQL"
        SQL_PARSER[🔍 SQL Parser<br/>Parse Queries]
        SQL_ANALYZER[📊 Analyzer<br/>Resolve References]
        SQL_OPTIMIZER[⚡ Logical Optimizer<br/>Rule-based Optimization]
        SQL_PLANNER[📋 Physical Planner<br/>Cost-based Selection]
        SQL_CODEGEN[🏗️ Code Generator<br/>Whole-Stage CodeGen]
    end

    RDD_CORE --> DF_SCHEMA
    DF_SCHEMA --> DS_TYPE

    DF_OPT --> SQL_PARSER
    SQL_PARSER --> SQL_ANALYZER
    SQL_ANALYZER --> SQL_OPTIMIZER
    SQL_OPTIMIZER --> SQL_PLANNER
    SQL_PLANNER --> SQL_CODEGEN

    DF_API --> DS_API

    %% Apply styles
    class RDD_CORE,RDD_OPS,RDD_PART,RDD_DEP rddClass
    class DF_SCHEMA,DF_OPT,DF_API,DF_TUNGSTEN dataframeClass
    class DS_TYPE,DS_ENCODER,DS_OPT,DS_API datasetClass
    class SQL_PARSER,SQL_ANALYZER,SQL_OPTIMIZER,SQL_PLANNER,SQL_CODEGEN sqlClass
```

## Catalyst Query Optimization Pipeline

```mermaid
flowchart TD
    A[📝 SQL Query / DataFrame Code] --> B[🔍 Parser]
    B --> C{Valid Syntax?}

    C -->|❌ No| D[🚨 Syntax Error<br/>Query Failed]
    C -->|✅ Yes| E[📊 Analyzer]

    E --> F[🔗 Catalog<br/>Table/Column Resolution]
    F --> G[📋 Unresolved Logical Plan]

    G --> H[⚡ Logical Optimizer]
    H --> I[🔄 Optimization Rules]

    I --> J[📊 Optimized Logical Plan]
    J --> K[🏗️ Physical Planner]

    K --> L[💰 Cost-based Optimization<br/>Join Strategies, etc.]
    L --> M[📋 Physical Plan]

    M --> N[🏭 Code Generator<br/>Whole-Stage CodeGen]
    N --> O[⚡ Executable Code<br/>JVM Bytecode]

    O --> P[🚀 Execution Engine]
    P --> Q[📤 Results]

    D --> R[🔧 Fix Query]
    R --> A
```

## Spark Streaming Architecture

```mermaid
graph TD
    %% Define styles
    classDef streamClass fill:#e3f2fd,stroke:#1976d2,stroke-width:3px,color:#0d47a1
    classDef dstreamClass fill:#f3e5f5,stroke:#7b1fa2,stroke-width:2px,color:#4a148c
    classDef structuredClass fill:#e8f5e8,stroke:#388e3c,stroke-width:2px,color:#1b5e20
    classDef sourceClass fill:#fff3e0,stroke:#f57c00,stroke-width:2px,color:#e65100

    subgraph "📊 DStreams (Original)"
        RECEIVER[📡 Receiver<br/>Data Ingestion]
        BLOCKS[📦 Blocks<br/>Data Batches]
        DSTREAM[🌊 DStream<br/>Sequence of RDDs]
        TRANSFORM[🔄 Transformations<br/>map, filter, window]
        OUTPUT[📤 Output Operations<br/>foreachRDD, saveAsTextFiles]
    end

    subgraph "🏗️ Structured Streaming"
        SOURCE[🔌 Source<br/>Kafka, File, Socket]
        DATAFRAME[📊 DataFrame<br/>Streaming DataFrame]
        QUERY[🔍 Streaming Query<br/>Continuous Processing]
        SINK[💾 Sink<br/>Console, File, Kafka]
        CHECKPOINT[📍 Checkpoint<br/>Fault Tolerance]
    end

    subgraph "🔄 Processing Models"
        MICRO_BATCH[⚡ Micro-batch<br/>Batch Interval Processing]
        CONTINUOUS[🌊 Continuous<br/>Row-by-row Processing]
        TRIGGER[⏰ Trigger<br/>Processing Triggers]
    end

    subgraph "💾 State Management"
        STATE_STORE[🏪 State Store<br/>Key-value Store]
        WATERMARK[🌊 Watermarking<br/>Late Data Handling]
        CHECKPOINTING[📋 Checkpointing<br/>Recovery Mechanism]
    end

    RECEIVER --> BLOCKS
    BLOCKS --> DSTREAM
    DSTREAM --> TRANSFORM
    TRANSFORM --> OUTPUT

    SOURCE --> DATAFRAME
    DATAFRAME --> QUERY
    QUERY --> SINK
    QUERY --> CHECKPOINT

    MICRO_BATCH --> CONTINUOUS
    CONTINUOUS --> TRIGGER

    STATE_STORE --> WATERMARK
    WATERMARK --> CHECKPOINTING

    %% Apply styles
    class RECEIVER,BLOCKS,DSTREAM,TRANSFORM,OUTPUT dstreamClass
    class SOURCE,DATAFRAME,QUERY,SINK,CHECKPOINT structuredClass
    class MICRO_BATCH,CONTINUOUS,TRIGGER streamClass
    class STATE_STORE,WATERMARK,CHECKPOINTING sourceClass
```

## MLlib Pipeline Architecture

```mermaid
graph TD
    %% Define styles
    classDef pipelineClass fill:#e3f2fd,stroke:#1976d2,stroke-width:3px,color:#0d47a1
    classDef transformerClass fill:#f3e5f5,stroke:#7b1fa2,stroke-width:2px,color:#4a148c
    classDef estimatorClass fill:#e8f5e8,stroke:#388e3c,stroke-width:2px,color:#1b5e20
    classDef evaluatorClass fill:#fff3e0,stroke:#f57c00,stroke-width:2px,color:#e65100

    subgraph "🔧 Pipeline Components"
        PIPELINE[📋 Pipeline<br/>Stages Orchestrator]
        STAGES[🎭 Pipeline Stages<br/>Transformers & Estimators]
        PARAMS[⚙️ Parameters<br/>Hyperparameter Tuning]
        MODEL[🤖 Fitted Model<br/>Transformer Chain]
    end

    subgraph "🔄 Transformers"
        TOKENIZER[✂️ Tokenizer<br/>Text → Words]
        VECTORIZER[🔢 VectorAssembler<br/>Features → Vector]
        SCALER[📏 StandardScaler<br/>Feature Scaling]
        ENCODER[🏷️ StringIndexer<br/>Categorical → Numeric]
    end

    subgraph "🎯 Estimators"
        LR[📈 LogisticRegression<br/>Binary Classification]
        RF[🌳 RandomForest<br/>Ensemble Learning]
        GBT[🚀 GBTClassifier<br/>Gradient Boosting]
        KMEANS[🎯 KMeans<br/>Clustering]
    end

    subgraph "📊 Evaluators"
        ACCURACY[✅ MulticlassClassificationEvaluator<br/>Accuracy Metrics]
        AUC[📈 BinaryClassificationEvaluator<br/>AUC-ROC]
        RMSE[📏 RegressionEvaluator<br/>RMSE]
        SILHOUETTE[🎭 ClusteringEvaluator<br/>Silhouette Score]
    end

    PIPELINE --> STAGES
    STAGES --> PARAMS
    PARAMS --> MODEL

    TOKENIZER --> VECTORIZER
    VECTORIZER --> SCALER
    SCALER --> ENCODER

    LR --> RF
    RF --> GBT
    GBT --> KMEANS

    ACCURACY --> AUC
    AUC --> RMSE
    RMSE --> SILHOUETTE

    %% Apply styles
    class PIPELINE,STAGES,PARAMS,MODEL pipelineClass
    class TOKENIZER,VECTORIZER,SCALER,ENCODER transformerClass
    class LR,RF,GBT,KMEANS estimatorClass
    class ACCURACY,AUC,RMSE,SILHOUETTE evaluatorClass
```

## Memory Management and Storage

```mermaid
graph TD
    A[Total Heap Memory<br/>spark.executor.memory] --> B[Execution Memory<br/>70%<br/>Shuffles, joins, sorts]
    A --> C[Storage Memory<br/>20%<br/>Cached RDDs/DataFrames]
    A --> D[User Memory<br/>10%<br/>User objects, data structures]

    B --> E[Dynamic Allocation<br/>Can borrow from storage<br/>when needed]
    C --> F[LRU Eviction<br/>When memory is full]

    G[Storage Levels] --> H[MEMORY_ONLY<br/>Fastest access]
    G --> I[MEMORY_AND_DISK<br/>Spill to disk]
    G --> J[DISK_ONLY<br/>Slowest but persistent]

    style A fill:#e3f2fd
    style B fill:#f3e5f5
    style C fill:#e8f5e8
    style D fill:#fff3e0
    style E fill:#fce4ec
    style F fill:#e1f5fe
    style G fill:#f1f8e9
    style H fill:#fff8e1
    style I fill:#fce4ec
    style J fill:#e8f5e8
```

## Shuffle Operations and Data Partitioning

```mermaid
graph TD
    A[Data Partitioning] --> B[Hash Partitioning<br/>key.hashCode % numPartitions]
    A --> C[Range Partitioning<br/>Sorted key ranges]
    A --> D[Custom Partitioning<br/>User-defined logic]

    E[Shuffle Process] --> F[Map Phase<br/>Local computation]
    E --> G[Shuffle Phase<br/>Network transfer]
    E --> H[Reduce Phase<br/>Global aggregation]

    F --> I[Sort<br/>Within partition]
    G --> J[Merge<br/>Combine sorted data]
    H --> K[Combine<br/>Local aggregation]

    I --> L[Performance Impact<br/>Network I/O<br/>Disk spilling<br/>Memory pressure]
    J --> L
    K --> L

    style A fill:#e3f2fd
    style B fill:#f3e5f5
    style C fill:#e8f5e8
    style D fill:#fff3e0
    style E fill:#fce4ec
    style F fill:#e1f5fe
    style G fill:#f1f8e9
    style H fill:#fff8e1
    style I fill:#fce4ec
    style J fill:#e8f5e8
    style K fill:#f3e5f5
    style L fill:#fff3e0
```

## Adaptive Query Execution (AQE)

```mermaid
flowchart TD
    A[📝 Query Submitted] --> B[🔍 Initial Physical Plan]
    B --> C[📊 Runtime Statistics<br/>Partition Sizes, Skew]

    C --> D{Adaptive<br/>Enabled?}
    D -->|❌ No| E[🚀 Execute Original Plan]
    D -->|✅ Yes| F[🔄 Runtime Optimization]

    F --> G[📦 Dynamically Coalesce<br/>Small Partitions]
    G --> H[🔗 Switch Join Strategies<br/>Based on Size]
    H --> I[⚖️ Handle Data Skew<br/>Split Skewed Partitions]
    I --> J[📋 Optimize Sort-Merge<br/>Adjust Parallelism]

    J --> K[📊 Updated Physical Plan]
    K --> L[🚀 Execute Optimized Plan]

    E --> M[📤 Results]
    L --> M

    M --> N[📈 Performance Metrics<br/>Optimization Effectiveness]
```

## Spark 3.x Performance Features

```mermaid
graph TD
    %% Define styles
    classDef perfClass fill:#e3f2fd,stroke:#1976d2,stroke-width:3px,color:#0d47a1
    classDef dynamicClass fill:#f3e5f5,stroke:#7b1fa2,stroke-width:2px,color:#4a148c
    classDef vectorizedClass fill:#e8f5e8,stroke:#388e3c,stroke-width:2px,color:#1b5e20
    classDef binaryClass fill:#fff3e0,stroke:#f57c00,stroke-width:2px,color:#e65100

    subgraph "🔄 Dynamic Partition Pruning"
        DYNAMIC_FILTER[🔍 Dynamic Filter<br/>Runtime Partition Elimination]
        DPP_BENEFIT[⚡ Reduces I/O<br/>Prune Unnecessary Partitions]
        DPP_EXAMPLE[📊 Example: Fact-Dimension Join<br/>Prune Dimension Partitions]
    end

    subgraph "⚡ Vectorized Query Execution"
        SIMD[🚀 SIMD Instructions<br/>Parallel Data Processing]
        COLUMNAR[📊 Columnar Processing<br/>Whole Column Operations]
        VECTORIZED_BENEFIT[📈 10x Performance<br/>For Parquet/ORC]
    end

    subgraph "🏗️ Binary Data Source"
        BINARY_FORMAT[📦 Binary Format<br/>High-Performance Storage]
        NESTED_SCHEMA[🔗 Nested Schema Support<br/>Complex Data Types]
        BINARY_BENEFIT[⚡ Faster Serialization<br/>Reduced CPU Usage]
    end

    subgraph "🎯 Query Compilation"
        CODE_GEN[🏭 Enhanced CodeGen<br/>Better JVM Optimization]
        INLINING[🔧 Method Inlining<br/>Reduced Function Calls]
        COMPILATION_BENEFIT[📈 Improved Throughput<br/>Lower Latency]
    end

    DYNAMIC_FILTER --> DPP_BENEFIT
    DPP_BENEFIT --> DPP_EXAMPLE

    SIMD --> COLUMNAR
    COLUMNAR --> VECTORIZED_BENEFIT

    BINARY_FORMAT --> NESTED_SCHEMA
    NESTED_SCHEMA --> BINARY_BENEFIT

    CODE_GEN --> INLINING
    INLINING --> COMPILATION_BENEFIT

    %% Apply styles
    class DYNAMIC_FILTER,DPP_BENEFIT,DPP_EXAMPLE dynamicClass
    class SIMD,COLUMNAR,VECTORIZED_BENEFIT vectorizedClass
    class BINARY_FORMAT,NESTED_SCHEMA,BINARY_BENEFIT binaryClass
    class CODE_GEN,INLINING,COMPILATION_BENEFIT perfClass
```

## Cluster Deployment Options

```mermaid
graph TD
    %% Define styles
    classDef standaloneClass fill:#e3f2fd,stroke:#1976d2,stroke-width:3px,color:#0d47a1
    classDef yarnClass fill:#f3e5f5,stroke:#7b1fa2,stroke-width:2px,color:#4a148c
    classDef k8sClass fill:#e8f5e8,stroke:#388e3c,stroke-width:2px,color:#1b5e20
    classDef cloudClass fill:#fff3e0,stroke:#f57c00,stroke-width:2px,color:#e65100

    subgraph "💻 Standalone Mode"
        STANDALONE_MASTER[🎯 Master Node<br/>Resource Manager]
        STANDALONE_WORKERS[👥 Worker Nodes<br/>Executor Hosts]
        STANDALONE_DEPLOY[🚀 spark-submit<br/>Direct Submission]
        STANDALONE_SCALING[📈 Manual Scaling<br/>Add/Remove Workers]
    end

    subgraph "🧵 YARN Integration"
        YARN_RM[🎛️ ResourceManager<br/>Cluster Resource Mgmt]
        YARN_NM[📊 NodeManager<br/>Per-node Resource Mgmt]
        YARN_APP_MASTER[👑 ApplicationMaster<br/>Spark App Coordinator]
        YARN_CONTAINERS[📦 Containers<br/>Executor Processes]
    end

    subgraph "☸️ Kubernetes Native"
        K8S_API[🔌 Kubernetes API<br/>Cluster Control Plane]
        K8S_PODS[📦 Pods<br/>Containerized Executors]
        K8S_SERVICES[🔗 Services<br/>Driver Communication]
        K8S_VOLUMES[💾 Persistent Volumes<br/>Data Persistence]
    end

    subgraph "☁️ Cloud Platforms"
        EMR[🌀 Amazon EMR<br/>Managed Spark Clusters]
        DATABRICKS[🔷 Databricks<br/>Unified Analytics Platform]
        DPH[🔥 Google Dataproc<br/>Managed Hadoop/Spark]
        HDINSIGHT[🔵 Azure HDInsight<br/>Cloud Hadoop/Spark]
    end

    STANDALONE_MASTER --> STANDALONE_WORKERS
    STANDALONE_WORKERS --> STANDALONE_DEPLOY
    STANDALONE_DEPLOY --> STANDALONE_SCALING

    YARN_RM --> YARN_NM
    YARN_NM --> YARN_APP_MASTER
    YARN_APP_MASTER --> YARN_CONTAINERS

    K8S_API --> K8S_PODS
    K8S_PODS --> K8S_SERVICES
    K8S_SERVICES --> K8S_VOLUMES

    EMR --> DATABRICKS
    DATABRICKS --> DPH
    DPH --> HDINSIGHT

    %% Apply styles
    class STANDALONE_MASTER,STANDALONE_WORKERS,STANDALONE_DEPLOY,STANDALONE_SCALING standaloneClass
    class YARN_RM,YARN_NM,YARN_APP_MASTER,YARN_CONTAINERS yarnClass
    class K8S_API,K8S_PODS,K8S_SERVICES,K8S_VOLUMES k8sClass
    class EMR,DATABRICKS,DPH,HDINSIGHT cloudClass
```

## Data Lakehouse Architecture with Spark

```mermaid
graph TD
    %% Define styles
    classDef ingestionClass fill:#e3f2fd,stroke:#1976d2,stroke-width:3px,color:#0d47a1
    classDef storageClass fill:#f3e5f5,stroke:#7b1fa2,stroke-width:2px,color:#4a148c
    classDef processingClass fill:#e8f5e8,stroke:#388e3c,stroke-width:2px,color:#1b5e20
    classDef consumptionClass fill:#fff3e0,stroke:#f57c00,stroke-width:2px,color:#e65100

    subgraph "📥 Data Ingestion"
        BATCH_SOURCES[📦 Batch Sources<br/>Files, Databases, APIs]
        STREAM_SOURCES[🌊 Streaming Sources<br/>Kafka, Kinesis, Event Hubs]
        INGESTION_TOOLS[🔧 Ingestion Tools<br/>Spark Streaming, Kafka Connect]
    end

    subgraph "🏪 Storage Layer"
        OBJECT_STORAGE[☁️ Object Storage<br/>S3, ADLS, GCS]
        DELTA_LAKE[Δ Delta Lake<br/>ACID Transactions]
        ICEBERG[🧊 Apache Iceberg<br/>Table Format]
        HUDI[🪶 Apache Hudi<br/>Incremental Processing]
    end

    subgraph "⚙️ Processing Layer"
        SPARK_BATCH[⚡ Spark Batch<br/>ETL, Analytics]
        SPARK_STREAMING[🌊 Spark Streaming<br/>Real-time Processing]
        SPARK_ML[🤖 Spark MLlib<br/>Machine Learning]
        SPARK_SQL[📊 Spark SQL<br/>Interactive Queries]
    end

    subgraph "📤 Consumption Layer"
        BI_TOOLS[📊 BI Tools<br/>Tableau, Power BI]
        ML_SERVING[🚀 ML Serving<br/>Model Deployment]
        APIs[🔌 REST APIs<br/>Data Services]
        ANALYTICS[📈 Analytics Platforms<br/>Databricks, EMR]
    end

    BATCH_SOURCES --> INGESTION_TOOLS
    STREAM_SOURCES --> INGESTION_TOOLS

    INGESTION_TOOLS --> OBJECT_STORAGE
    OBJECT_STORAGE --> DELTA_LAKE
    OBJECT_STORAGE --> ICEBERG
    OBJECT_STORAGE --> HUDI

    DELTA_LAKE --> SPARK_BATCH
    ICEBERG --> SPARK_STREAMING
    HUDI --> SPARK_ML
    DELTA_LAKE --> SPARK_SQL

    SPARK_BATCH --> BI_TOOLS
    SPARK_STREAMING --> ML_SERVING
    SPARK_ML --> APIs
    SPARK_SQL --> ANALYTICS

    %% Apply styles
    class BATCH_SOURCES,STREAM_SOURCES,INGESTION_TOOLS ingestionClass
    class OBJECT_STORAGE,DELTA_LAKE,ICEBERG,HUDI storageClass
    class SPARK_BATCH,SPARK_STREAMING,SPARK_ML,SPARK_SQL processingClass
    class BI_TOOLS,ML_SERVING,APIs,ANALYTICS consumptionClass
```

## Summary

Apache Spark's visual architecture reveals a sophisticated, layered system designed for scalable data processing:

- **Unified Engine**: Single platform for diverse workloads (batch, streaming, ML, graph)
- **Layered Abstractions**: RDD → DataFrame → Dataset progression with increasing optimization
- **Adaptive Optimization**: Runtime query plan adjustments based on actual data characteristics
- **Flexible Deployment**: Support for various cluster managers and cloud platforms
- **Rich Ecosystem**: Deep integration with storage systems, streaming platforms, and analytics tools

The combination of in-memory processing, advanced optimization, and high-level APIs makes Spark a cornerstone of modern big data architectures, enabling organizations to process massive datasets efficiently across diverse use cases.
