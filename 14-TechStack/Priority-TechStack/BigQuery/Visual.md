# BigQuery - Visual Learning Guide

## 🎨 Visual Learning: Data Flow, Architecture, Query Processing

---

## 📊 BigQuery Architecture

### High-Level Architecture

```mermaid
graph TB
    subgraph "Data Sources"
        A[CSV Files]
        B[JSON Files]
        C[Streaming Data]
        D[Other GCP Services]
    end
    
    subgraph "BigQuery"
        E[Storage Layer<br/>Columnar Storage]
        F[Compute Layer<br/>Query Engine]
        G[Metadata Layer<br/>Catalog]
    end
    
    subgraph "Output"
        H[Query Results]
        I[Exported Data]
        J[ML Models]
    end
    
    A --> E
    B --> E
    C --> E
    D --> E
    
    E --> F
    G --> F
    F --> H
    F --> I
    F --> J
    
    style E fill:#4285f4
    style F fill:#34a853
    style G fill:#fbbc04
```

### Storage and Compute Separation

```mermaid
graph LR
    A[Storage Layer] --> B[Columnar Format]
    B --> C[Automatic Compression]
    C --> D[Partitioning]
    D --> E[Clustering]
    
    F[Compute Layer] --> G[Query Engine]
    G --> H[Automatic Scaling]
    H --> I[Distributed Processing]
    
    E --> G
    I --> J[Fast Queries]
    
    style A fill:#4285f4
    style F fill:#34a853
    style J fill:#ea4335
```

---

## 🔄 Data Ingestion Flow

### Batch Loading Flow

```mermaid
sequenceDiagram
    participant Source
    participant GCS
    participant BigQuery
    participant Table
    
    Source->>GCS: Upload File
    GCS->>BigQuery: Load Job
    BigQuery->>BigQuery: Validate Schema
    BigQuery->>BigQuery: Process Data
    BigQuery->>Table: Write Data
    Table-->>BigQuery: Confirm
    BigQuery-->>Source: Job Complete
```

### Streaming Insert Flow

```mermaid
flowchart TD
    A[Application] --> B[Streaming Insert API]
    B --> C[BigQuery Buffer]
    C --> D[Batch Write]
    D --> E[Table]
    
    E --> F[Queryable After Buffer]
    
    style B fill:#4285f4
    style C fill:#fbbc04
    style E fill:#34a853
```

---

## 🔍 Query Processing Flow

### Query Execution Flow

```mermaid
sequenceDiagram
    participant Client
    participant BigQuery
    participant Planner
    participant Workers
    participant Storage
    participant Results
    
    Client->>BigQuery: SQL Query
    BigQuery->>Planner: Parse & Plan
    Planner->>Planner: Optimize Query
    Planner->>Workers: Distribute Tasks
    Workers->>Storage: Read Data
    Storage-->>Workers: Data Chunks
    Workers->>Workers: Process & Aggregate
    Workers-->>Planner: Partial Results
    Planner->>Results: Combine Results
    Results-->>Client: Final Results
```

### Query Optimization

```mermaid
graph TB
    A[SQL Query] --> B[Query Parser]
    B --> C[Query Optimizer]
    C --> D{Optimizations}
    
    D --> E[Partition Pruning]
    D --> F[Clustering Filter]
    D --> G[Predicate Pushdown]
    D --> H[Column Selection]
    
    E --> I[Optimized Plan]
    F --> I
    G --> I
    H --> I
    
    I --> J[Execute Query]
    
    style C fill:#4285f4
    style I fill:#34a853
```

---

## 📊 Partitioning and Clustering

### Partitioning Strategy

```mermaid
graph TB
    A[Table: transactions] --> B[Partition by Date]
    B --> C[2024-01-01]
    B --> D[2024-01-02]
    B --> E[2024-01-03]
    B --> F[2024-01-N]
    
    G[Query: WHERE date = '2024-01-01'] --> H[Only Scan Partition C]
    H --> I[Fast Query]
    
    style B fill:#4285f4
    style H fill:#34a853
    style I fill:#ea4335
```

### Clustering Strategy

```mermaid
graph LR
    A[Partition] --> B[Clustered by customer_id]
    B --> C[Sorted Data]
    C --> D[Fast Filtering]
    
    E[Query: WHERE customer_id = '123'] --> F[Binary Search]
    F --> G[Fast Retrieval]
    
    style B fill:#4285f4
    style F fill:#34a853
```

---

## 🔄 ETL Pipeline Flow

### Data Transformation Pipeline

```mermaid
graph TB
    A[Raw Data] --> B[Bronze Layer<br/>Raw Data]
    B --> C[Transform]
    C --> D[Silver Layer<br/>Cleaned Data]
    D --> E[Aggregate]
    E --> F[Gold Layer<br/>Analytics Tables]
    
    F --> G[Reports]
    F --> H[ML Training]
    
    style B fill:#ea4335
    style D fill:#fbbc04
    style F fill:#34a853
```

---

## 🎯 Query Types

### Query Execution Comparison

```mermaid
graph TB
    A[Query Type] --> B[SELECT Query]
    A --> C[INSERT Query]
    A --> D[UPDATE Query]
    A --> E[DELETE Query]
    
    B --> F[Read from Storage]
    C --> G[Write to Storage]
    D --> H[Read + Write]
    E --> I[Mark for Deletion]
    
    style B fill:#4285f4
    style C fill:#34a853
```

---

## 💰 Cost Optimization Flow

### Cost Optimization Strategies

```mermaid
mindmap
  root((Cost Optimization))
    Query Optimization
      Use WHERE Clauses
        Filter Early
      Use LIMIT
        Reduce Data Scanned
      Avoid SELECT *
        Select Only Needed
    Storage Optimization
      Partitioning
        Scan Less Data
      Clustering
        Faster Queries
      Compression
        Reduce Storage
    Caching
      Query Cache
        Reuse Results
      Table Cache
        Hot Data
```

---

## 🎯 Key Visual Takeaways

1. **Storage + Compute Separation**: Independent scaling
2. **Columnar Storage**: Fast analytical queries
3. **Partitioning**: Query only relevant data
4. **Clustering**: Faster filtering
5. **Automatic Optimization**: Query engine optimizes

---

## 📚 Next Steps

1. ✅ Review these diagrams
2. 🏗️ Draw them yourself
3. 💬 Use in interviews
4. 🔗 Connect to your POCs

---

**Visual learning helps!** Use these to explain BigQuery in interviews.

