# SQL Data Engineering Visual Guide

## Database Architecture Diagrams

### Relational Database Schema
```mermaid
erDiagram
    CUSTOMERS ||--o{ ORDERS : places
    CUSTOMERS {
        integer customer_id PK
        varchar first_name
        varchar last_name
        varchar email UK
        varchar phone
        date created_at
        date updated_at
    }
    ORDERS ||--|{ ORDER_ITEMS : contains
    ORDERS {
        integer order_id PK
        integer customer_id FK
        date order_date
        decimal total_amount
        varchar status
    }
    ORDER_ITEMS {
        integer order_item_id PK
        integer order_id FK
        integer product_id FK
        integer quantity
        decimal unit_price
    }
    PRODUCTS ||--o{ ORDER_ITEMS : "ordered in"
    PRODUCTS {
        integer product_id PK
        varchar product_name
        varchar category
        decimal price
        integer stock_quantity
    }
```

### Data Warehouse Star Schema
```mermaid
erDiagram
    FACT_SALES ||--o{ DIM_CUSTOMER : "sold to"
    FACT_SALES ||--o{ DIM_PRODUCT : "product sold"
    FACT_SALES ||--o{ DIM_DATE : "sale date"
    FACT_SALES ||--o{ DIM_STORE : "store location"
    FACT_SALES {
        integer sales_key PK
        integer customer_key FK
        integer product_key FK
        integer date_key FK
        integer store_key FK
        integer quantity
        decimal unit_price
        decimal total_amount
        decimal discount_amount
    }
    DIM_CUSTOMER {
        integer customer_key PK
        integer customer_id
        varchar first_name
        varchar last_name
        varchar city
        varchar state
        date effective_date
        date expiry_date
        boolean is_current
    }
    DIM_PRODUCT {
        integer product_key PK
        integer product_id
        varchar product_name
        varchar category
        varchar subcategory
        decimal price
        date effective_date
        date expiry_date
        boolean is_current
    }
    DIM_DATE {
        integer date_key PK
        date date_actual
        integer day_of_week
        varchar day_name
        integer month_actual
        varchar month_name
        integer quarter_actual
        integer year_actual
        boolean is_weekend
        boolean is_holiday
    }
    DIM_STORE {
        integer store_key PK
        integer store_id
        varchar store_name
        varchar city
        varchar state
        varchar region
        date effective_date
        date expiry_date
        boolean is_current
    }
```

## Query Execution Flow

### SQL Query Processing Pipeline
```mermaid
flowchart TD
    A[SQL Query] --> B[Parser]
    B --> C[Query Optimizer]
    C --> D[Execution Plan]
    D --> E[Query Executor]
    E --> F[Storage Engine]
    F --> G[Result Set]

    B --> B1[Syntax Check]
    B --> B2[Semantic Analysis]

    C --> C1[Access Path Selection]
    C --> C2[Join Order Optimization]
    C --> C3[Index Selection]

    E --> E1[Table Scan]
    E --> E2[Index Scan]
    E --> E3[Join Operations]
    E --> E4[Sort Operations]
    E --> E5[Aggregation]

    F --> F1[Buffer Manager]
    F --> F2[Lock Manager]
    F --> F3[Log Manager]
```

### Join Types Visualization
```mermaid
flowchart TD
    subgraph "Table A"
        A1[id: 1<br/>name: Alice]
        A2[id: 2<br/>name: Bob]
        A3[id: 3<br/>name: Charlie]
    end

    subgraph "Table B"
        B1[id: 1<br/>dept: Engineering]
        B2[id: 2<br/>dept: Sales]
        B4[id: 4<br/>dept: Marketing]
    end

    subgraph "INNER JOIN<br/>A.id = B.id"
        I1[1, Alice, Engineering]
        I2[2, Bob, Sales]
    end

    subgraph "LEFT JOIN<br/>A.id = B.id"
        L1[1, Alice, Engineering]
        L2[2, Bob, Sales]
        L3[3, Charlie, NULL]
    end

    subgraph "RIGHT JOIN<br/>A.id = B.id"
        R1[1, Alice, Engineering]
        R2[2, Bob, Sales]
        R4[4, NULL, Marketing]
    end

    subgraph "FULL OUTER JOIN<br/>A.id = B.id"
        F1[1, Alice, Engineering]
        F2[2, Bob, Sales]
        F3[3, Charlie, NULL]
        F4[4, NULL, Marketing]
    end

    A1 --> I1
    A2 --> I2
    B1 --> I1
    B2 --> I2

    A1 --> L1
    A2 --> L2
    A3 --> L3
    B1 --> L1
    B2 --> L2

    A1 --> R1
    A2 --> R2
    B1 --> R1
    B2 --> R2
    B4 --> R4

    A1 --> F1
    A2 --> F2
    A3 --> F3
    B1 --> F1
    B2 --> F2
    B4 --> F4
```

## Index Architecture

### B-Tree Index Structure
```mermaid
flowchart TD
    subgraph "Root Node"
        R[50<br/>| 25 | 50 | 75 |]
    end

    subgraph "Level 1"
        L1[25<br/>| 10 | 25 | 40 |]
        L2[75<br/>| 50 | 60 | 75 | 90 |]
    end

    subgraph "Leaf Nodes"
        LF1[10, 15, 20]
        LF2[25, 30, 35]
        LF3[40, 45]
        LF4[50, 55]
        LF5[60, 65, 70]
        LF6[75, 80, 85]
        LF7[90, 95, 100]
    end

    R --> L1
    R --> L2

    L1 --> LF1
    L1 --> LF2
    L1 --> LF3

    L2 --> LF4
    L2 --> LF5
    L2 --> LF6
    L2 --> LF7

    style R fill:#e1f5fe
    style L1 fill:#f3e5f5
    style L2 fill:#f3e5f5
    style LF1 fill:#e8f5e8
    style LF2 fill:#e8f5e8
    style LF3 fill:#e8f5e8
    style LF4 fill:#e8f5e8
    style LF5 fill:#e8f5e8
    style LF6 fill:#e8f5e8
    style LF7 fill:#e8f5e8
```

### Index Types Comparison
```mermaid
flowchart TD
    subgraph "B-Tree Index"
        BT[Balanced Tree Structure<br/>- Fast lookups<br/>- Range queries<br/>- Ordered data<br/>- Default choice]
    end

    subgraph "Hash Index"
        HI[Hash Table<br/>- O(1) lookups<br/>- Equality only<br/>- No range queries<br/>- Fast inserts]
    end

    subgraph "GIN Index<br/>(Generalized Inverted Index)"
        GIN[Inverted Index<br/>- Full-text search<br/>- Array elements<br/>- JSON paths<br/>- Complex types]
    end

    subgraph "GiST Index<br/>(Generalized Search Tree)"
        GIST[Tree Structure<br/>- Spatial data<br/>- Text search<br/>- Custom operators<br/>- Flexible indexing]
    end

    subgraph "BRIN Index<br/>(Block Range Index)"
        BRIN[Block Ranges<br/>- Large tables<br/>- Correlated data<br/>- Minimal storage<br/>- Fast scans]
    end

    BT --> D[Use Case:<br/>Primary keys,<br/>foreign keys,<br/>general queries]
    HI --> E[Use Case:<br/>Exact matches,<br/>high cardinality]
    GIN --> F[Use Case:<br/>JSON, arrays,<br/>full-text search]
    GIST --> G[Use Case:<br/>Geospatial,<br/>text search,<br/>custom types]
    BRIN --> H[Use Case:<br/>Time-series,<br/>large sorted tables]
```

## ETL Pipeline Architecture

### ETL Process Flow
```mermaid
flowchart TD
    subgraph "Extract"
        E1[Source Systems] --> E2[Change Detection]
        E2 --> E3[Data Extraction]
        E3 --> E4[Staging Area]
    end

    subgraph "Transform"
        T1[Data Validation] --> T2[Data Cleansing]
        T2 --> T3[Data Standardization]
        T3 --> T4[Business Rules]
        T4 --> T5[Data Aggregation]
        T5 --> T6[Staging Tables]
    end

    subgraph "Load"
        L1[Slowly Changing<br/>Dimensions] --> L2[Fact Tables]
        L2 --> L3[Data Warehouse]
        L3 --> L4[Data Marts]
    end

    E4 --> T1
    T6 --> L1

    subgraph "Monitoring & Control"
        M1[Error Handling] --> M2[Logging]
        M2 --> M3[Alerting]
        M3 --> M4[Recovery]
    end

    T1 -.-> M1
    T2 -.-> M1
    L1 -.-> M1
```

### Incremental Load Patterns
```mermaid
flowchart TD
    subgraph "Timestamp-based"
        TS1[Source Table<br/>updated_at] --> TS2[Target Table<br/>max(updated_at)]
        TS2 --> TS3[Extract records<br/>WHERE updated_at > max_target]
        TS3 --> TS4[Load to Target]
    end

    subgraph "Change Data Capture"
        CDC1[Transaction Log] --> CDC2[Change Events]
        CDC2 --> CDC3[Event Processing]
        CDC3 --> CDC4[Apply Changes<br/>INSERT/UPDATE/DELETE]
    end

    subgraph "Hash-based"
        H1[Source Records] --> H2[Calculate Row Hash]
        H2 --> H3[Compare with<br/>Target Hashes]
        H3 --> H4[Identify Changes]
        H4 --> H5[Update Changed Rows]
    end

    subgraph "Trigger-based"
        TR1[Source Table] --> TR2[Database Triggers]
        TR2 --> TR3[Change Log Table]
        TR3 --> TR4[Process Changes]
        TR4 --> TR5[Update Target]
    end
```

## Window Functions Visualization

### Window Function Concepts
```mermaid
flowchart LR
    subgraph "Window Frame"
        W1[Row 1<br/>value: 10]
        W2[Row 2<br/>value: 20]
        W3[Row 3<br/>value: 30<br/>CURRENT ROW]
        W4[Row 4<br/>value: 40]
        W5[Row 5<br/>value: 50]
    end

    subgraph "Aggregations"
        A1[SUM: 10+20+30=60<br/>ROWS 3 PRECEDING]
        A2[AVG: 20+30+40=30<br/>ROWS BETWEEN 1 PRECEDING<br/>AND 1 FOLLOWING]
        A3[RANK: 3<br/>ORDER BY value]
    end

    W1 --> A1
    W2 --> A1
    W3 --> A1

    W2 --> A2
    W3 --> A2
    W4 --> A2

    W3 --> A3
```

### Running Totals Example
```mermaid
flowchart TD
    subgraph "Sales Data"
        D1[Jan: $1000]
        D2[Feb: $1200]
        D3[Mar: $900]
        D4[Apr: $1500]
        D5[May: $1100]
    end

    subgraph "Running Total"
        R1[Jan: $1000]
        R2[Feb: $2200<br/>1000+1200]
        R3[Mar: $3100<br/>2200+900]
        R4[Apr: $4600<br/>3100+1500]
        R5[May: $5700<br/>4600+1100]
    end

    subgraph "Moving Average<br/>(3-month)"
        M1[Jan: NULL<br/>insufficient data]
        M2[Feb: NULL<br/>insufficient data]
        M3[Mar: $1033<br/>(1000+1200+900)/3]
        M4[Apr: $1200<br/>(1200+900+1500)/3]
        M5[May: $1200<br/>(900+1500+1100)/3]
    end

    D1 --> R1
    D1 --> R2
    D2 --> R2
    D1 --> R3
    D2 --> R3
    D3 --> R3
    D1 --> R4
    D2 --> R4
    D3 --> R4
    D4 --> R4
    D1 --> R5
    D2 --> R5
    D3 --> R5
    D4 --> R5
    D5 --> R5

    D1 --> M3
    D2 --> M3
    D3 --> M3
    D2 --> M4
    D3 --> M4
    D4 --> M4
    D3 --> M5
    D4 --> M5
    D5 --> M5
```

## Partitioning Strategies

### Table Partitioning Architecture
```mermaid
flowchart TD
    subgraph "Partitioned Table: sales"
        P0[sales<br/>Parent Table]
    end

    subgraph "Range Partitions"
        P1[sales_2023_q1<br/>2023-01-01 to 2023-03-31]
        P2[sales_2023_q2<br/>2023-04-01 to 2023-06-30]
        P3[sales_2023_q3<br/>2023-07-01 to 2023-09-30]
        P4[sales_2023_q4<br/>2023-10-01 to 2023-12-31]
    end

    subgraph "List Partitions"
        P5[sales_us<br/>country = 'US']
        P6[sales_eu<br/>country = 'EU']
        P7[sales_asia<br/>country = 'ASIA']
    end

    subgraph "Hash Partitions"
        P8[sales_hash_0<br/>hash % 4 = 0]
        P9[sales_hash_1<br/>hash % 4 = 1]
        P10[sales_hash_2<br/>hash % 4 = 2]
        P11[sales_hash_3<br/>hash % 4 = 3]
    end

    P0 --> P1
    P0 --> P2
    P0 --> P3
    P0 --> P4

    P0 --> P5
    P0 --> P6
    P0 --> P7

    P0 --> P8
    P0 --> P9
    P0 --> P10
    P0 --> P11
```

### Partitioning Benefits
```mermaid
flowchart TD
    subgraph "Performance Benefits"
        Perf1[Query Pruning<br/>Scan only relevant partitions]
        Perf2[Parallel Processing<br/>Multiple partitions simultaneously]
        Perf3[Index Efficiency<br/>Smaller indexes per partition]
        Perf4[Maintenance Speed<br/>Partition-level operations]
    end

    subgraph "Management Benefits"
        Mgmt1[Data Lifecycle<br/>Drop old partitions easily]
        Mgmt2[Backup Flexibility<br/>Backup specific partitions]
        Mgmt3[Storage Optimization<br/>Different storage per partition]
        Mgmt4[Load Distribution<br/>Balance across storage tiers]
    end

    subgraph "Partitioning Strategies"
        Strat1[Range Partitioning<br/>Date ranges, numeric ranges]
        Strat2[List Partitioning<br/>Categorical values, regions]
        Strat3[Hash Partitioning<br/>Even distribution, parallel queries]
        Strat4[Composite Partitioning<br/>Range + List/Hash combinations]
    end

    Perf1 --> Strat1
    Perf2 --> Strat3
    Mgmt1 --> Strat1
    Mgmt2 --> Strat2
```

## Query Optimization Flow

### Execution Plan Analysis
```mermaid
flowchart TD
    A[Query] --> B[Parse]
    B --> C[Rewrite]
    C --> D[Optimize]
    D --> E[Execute]

    D --> D1[Access Methods<br/>Table Scan<br/>Index Scan<br/>Bitmap Scan]

    D --> D2[Join Methods<br/>Nested Loop<br/>Hash Join<br/>Merge Join]

    D --> D3[Physical Operators<br/>Sort<br/>Aggregate<br/>Filter]

    E --> E1[Cost Estimation<br/>I/O Cost<br/>CPU Cost<br/>Memory Usage]

    E --> E2[Statistics<br/>Table Statistics<br/>Index Statistics<br/>Histogram]

    subgraph "Optimization Goals"
        G1[Minimize I/O]
        G2[Minimize CPU]
        G3[Minimize Memory]
        G4[Maximize Parallelism]
    end

    D1 --> G1
    D2 --> G2
    D3 --> G3
    E1 --> G4
```

### Index Selection Decision Tree
```mermaid
flowchart TD
    A[Query Analysis] --> B{Selectivity?}
    B -->|High >10%| C[Full Table Scan]
    B -->|Low <10%| D{Index Exists?}

    D -->|No| E[Consider Creating Index]
    D -->|Yes| F{Index Type?}

    F -->|B-Tree| G{Clustered?}
    F -->|Hash| H{Equality Only?}
    F -->|GIN| I{Complex Types?}
    F -->|GiST| J{Spatial/Text?}

    G -->|Yes| K[Use Clustered Index]
    G -->|No| L[Use Non-Clustered Index]

    H -->|Yes| M[Use Hash Index]
    H -->|No| N[Use B-Tree]

    I -->|Yes| O[Use GIN Index]
    I -->|No| P[Use B-Tree]

    J -->|Yes| Q[Use GiST Index]
    J -->|No| R[Use B-Tree]

    C --> S[Optimize Query]
    E --> T[Create Appropriate Index]
    K --> U[Execute Query]
    L --> U
    M --> U
    N --> U
    O --> U
    P --> U
    Q --> U
    R --> U
    T --> U
```

## Data Quality Framework

### Data Quality Checks Architecture
```mermaid
flowchart TD
    subgraph "Data Sources"
        S1[Source Tables]
        S2[API Feeds]
        S3[Files]
        S4[External Systems]
    end

    subgraph "Quality Checks"
        Q1[Completeness<br/>NOT NULL checks]
        Q2[Accuracy<br/>Business rules]
        Q3[Consistency<br/>Cross-field validation]
        Q4[Timeliness<br/>Freshness checks]
        Q5[Validity<br/>Format & range checks]
        Q6[Uniqueness<br/>Duplicate detection]
        Q7[Integrity<br/>Referential checks]
    end

    subgraph "Quality Metrics"
        M1[Pass Rate %]
        M2[Error Count]
        M3[Trend Analysis]
        M4[SLA Compliance]
    end

    subgraph "Actions"
        A1[Accept Data]
        A2[Reject & Quarantine]
        A3[Auto-correct]
        A4[Alert Stakeholders]
        A5[Escalate Issues]
    end

    S1 --> Q1
    S2 --> Q2
    S3 --> Q3
    S4 --> Q4

    Q1 --> M1
    Q2 --> M2
    Q3 --> M3
    Q4 --> M4
    Q5 --> M1
    Q6 --> M2
    Q7 --> M3

    M1 --> A1
    M2 --> A2
    M3 --> A3
    M4 --> A4

    A2 --> A5
    A3 --> A5
    A4 --> A5
```

### Data Lineage Tracking
```mermaid
flowchart TD
    subgraph "Source Layer"
        SRC1[CRM System<br/>customer_data]
        SRC2[ERP System<br/>order_data]
        SRC3[Web Logs<br/>clickstream_data]
    end

    subgraph "Staging Layer"
        STG1[stg_customers<br/>FROM crm.customer_data]
        STG2[stg_orders<br/>FROM erp.order_data]
        STG3[stg_events<br/>FROM logs.clickstream_data]
    end

    subgraph "Integration Layer"
        INT1[customer_orders<br/>JOIN stg_customers + stg_orders]
        INT2[customer_events<br/>JOIN customer_orders + stg_events]
    end

    subgraph "Presentation Layer"
        PRES1[customer_summary<br/>AGGREGATE customer_events]
        PRES2[product_analytics<br/>AGGREGATE customer_orders]
    end

    subgraph "Consumption Layer"
        CONS1[BI Dashboard<br/>FROM customer_summary]
        CONS2[ML Model<br/>FROM product_analytics]
        CONS3[API Service<br/>FROM customer_events]
    end

    SRC1 --> STG1
    SRC2 --> STG2
    SRC3 --> STG3

    STG1 --> INT1
    STG2 --> INT1

    INT1 --> INT2
    STG3 --> INT2

    INT2 --> PRES1
    INT1 --> PRES2

    PRES1 --> CONS1
    PRES2 --> CONS2
    INT2 --> CONS3

    style SRC1 fill:#e3f2fd
    style SRC2 fill:#e3f2fd
    style SRC3 fill:#e3f2fd
    style STG1 fill:#f3e5f5
    style STG2 fill:#f3e5f5
    style STG3 fill:#f3e5f5
    style INT1 fill:#fff3e0
    style INT2 fill:#fff3e0
    style PRES1 fill:#e8f5e8
    style PRES2 fill:#e8f5e8
    style CONS1 fill:#ffebee
    style CONS2 fill:#ffebee
    style CONS3 fill:#ffebee
```

## Performance Monitoring Dashboard

### Query Performance Metrics
```mermaid
flowchart TD
    subgraph "Query Metrics"
        QM1[Execution Time<br/>Total runtime]
        QM2[CPU Usage<br/>Processing time]
        QM3[I/O Operations<br/>Reads/Writes]
        QM4[Memory Usage<br/>Buffer/cache usage]
        QM5[Lock Waits<br/>Concurrency conflicts]
    end

    subgraph "System Metrics"
        SM1[Buffer Hit Ratio<br/>Cache efficiency]
        SM2[Connection Count<br/>Active sessions]
        SM3[Temp File Usage<br/>Sort/hash spills]
        SM4[Deadlocks<br/>Lock conflicts]
        SM5[Replication Lag<br/>Data freshness]
    end

    subgraph "Business Metrics"
        BM1[Query Success Rate<br/>Successful executions]
        BM2[Average Response Time<br/>User experience]
        BM3[Throughput<br/>Queries per second]
        BM4[Error Rate<br/>Failed queries]
    end

    subgraph "Alerting"
        A1[Threshold Alerts<br/>Performance degradation]
        A2[Anomaly Detection<br/>Unusual patterns]
        A3[Capacity Planning<br/>Resource utilization]
        A4[SLA Monitoring<br/>Service level compliance]
    end

    QM1 --> A1
    QM2 --> A1
    SM1 --> A2
    SM2 --> A3
    BM1 --> A4
    BM2 --> A4
```

### Database Health Scorecard
```mermaid
pie title Database Health Components
    "Query Performance" : 25
    "System Resources" : 20
    "Data Quality" : 20
    "Backup & Recovery" : 15
    "Security" : 10
    "Availability" : 10
```

## Summary

SQL data engineering visualization covers:

- **Database Design**: ER diagrams, star schemas, normalization
- **Query Processing**: Execution plans, optimization strategies
- **Performance**: Indexing, partitioning, monitoring
- **ETL Patterns**: Data pipelines, quality frameworks
- **Analytics**: Window functions, time series, cohort analysis
- **Architecture**: Multi-tier systems, data lineage

Key visual concepts:
- **Flow Diagrams**: Process flows and data movement
- **Tree Structures**: Indexes, partitions, hierarchies
- **ER Diagrams**: Database relationships and schemas
- **Decision Trees**: Optimization and selection logic
- **Architecture Diagrams**: System components and interactions
- **Metrics Dashboards**: Performance monitoring and alerting

These visualizations help understand complex SQL concepts through clear, structured representations of database systems, query processing, and data engineering patterns.
