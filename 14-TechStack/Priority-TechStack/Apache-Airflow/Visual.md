# Apache Airflow - Visual Learning Guide

## 🎨 Visual Learning: DAG Flows, Architecture, Execution Patterns

---

## 📊 Airflow Architecture

### High-Level System Architecture

```mermaid
graph TB
    subgraph "Airflow Components"
        A[Scheduler<br/>Parses DAGs & Schedules Tasks]
        B[Webserver<br/>UI & API]
        C[Metadata Database<br/>PostgreSQL/MySQL]
    end
    
    subgraph "Executors"
        D[Sequential Executor<br/>Development]
        E[Local Executor<br/>Single Machine]
        F[Celery Executor<br/>Distributed]
        G[K8s Executor<br/>Cloud-Native]
    end
    
    subgraph "Workers"
        H[Worker 1]
        I[Worker 2]
        J[Worker N]
    end
    
    subgraph "External Systems"
        K[Databases]
        L[APIs]
        M[File Systems]
        N[Cloud Services]
    end
    
    A --> C
    B --> C
    A --> D
    A --> E
    A --> F
    A --> G
    F --> H
    F --> I
    G --> J
    H --> K
    H --> L
    I --> M
    J --> N
    
    style A fill:#4285f4,stroke:#1976d2,stroke-width:3px
    style B fill:#34a853,stroke:#2e7d32,stroke-width:3px
    style C fill:#ea4335,stroke:#c62828,stroke-width:3px
    style F fill:#fbbc04,stroke:#f57c00,stroke-width:3px
```

---

## 🔄 DAG Execution Patterns

### Pattern 1: Simple Linear Pipeline

```mermaid
flowchart LR
    A[Extract] --> B[Transform]
    B --> C[Load]
    
    style A fill:#4285f4,stroke:#1976d2,stroke-width:2px
    style B fill:#34a853,stroke:#2e7d32,stroke-width:2px
    style C fill:#ea4335,stroke:#c62828,stroke-width:2px
```

**Use Case**: Simple ETL jobs, data migration

---

### Pattern 2: Parallel Processing

```mermaid
graph TB
    A[Extract API] --> D[Transform]
    B[Extract Database] --> D
    C[Extract Files] --> D
    D --> E[Load]
    
    style A fill:#4285f4,stroke:#1976d2,stroke-width:2px
    style B fill:#4285f4,stroke:#1976d2,stroke-width:2px
    style C fill:#4285f4,stroke:#1976d2,stroke-width:2px
    style D fill:#34a853,stroke:#2e7d32,stroke-width:2px
    style E fill:#ea4335,stroke:#c62828,stroke-width:2px
```

**Use Case**: Multiple data sources, independent extractions

---

### Pattern 3: Conditional Branching

```mermaid
flowchart TD
    A[Extract] --> B{Data Volume}
    B -->|High| C[Process High Volume]
    B -->|Medium| D[Process Medium Volume]
    B -->|Low| E[Process Low Volume]
    C --> F[Load]
    D --> F
    E --> F
    
    style B fill:#fbbc04,stroke:#f57c00,stroke-width:2px
    style F fill:#ea4335,stroke:#c62828,stroke-width:2px
```

**Use Case**: Different processing based on data characteristics

---

### Pattern 4: Fan-Out Fan-In

```mermaid
graph TB
    A[Extract] --> B[Process Region 1]
    A --> C[Process Region 2]
    A --> D[Process Region 3]
    B --> E[Aggregate]
    C --> E
    D --> E
    E --> F[Load]
    
    style A fill:#4285f4,stroke:#1976d2,stroke-width:2px
    style E fill:#34a853,stroke:#2e7d32,stroke-width:2px
    style F fill:#ea4335,stroke:#c62828,stroke-width:2px
```

**Use Case**: Parallel processing with aggregation

---

### Pattern 5: Event-Driven with Sensors

```mermaid
flowchart LR
    A[File Sensor] --> B[Extract]
    B --> C[Transform]
    C --> D[Load]
    D --> E[Notify]
    
    style A fill:#9c27b0,stroke:#7b1fa2,stroke-width:2px
    style E fill:#ea4335,stroke:#c62828,stroke-width:2px
```

**Use Case**: File-based pipelines, API-driven workflows

---

### Pattern 6: Task Groups Organization

```mermaid
graph TB
    subgraph "Data Ingestion Group"
        A1[Extract API]
        A2[Extract DB]
        A3[Extract Files]
        A1 --> A2 --> A3
    end
    
    subgraph "Data Processing Group"
        B1[Validate]
        B2[Transform]
        B3[Enrich]
        B1 --> B2 --> B3
    end
    
    subgraph "Data Loading Group"
        C1[Load Warehouse]
        C2[Load Analytics]
    end
    
    A3 --> B1
    B3 --> C1
    B3 --> C2
    
    style A1 fill:#4285f4,stroke:#1976d2,stroke-width:2px
    style B1 fill:#34a853,stroke:#2e7d32,stroke-width:2px
    style C1 fill:#ea4335,stroke:#c62828,stroke-width:2px
```

**Use Case**: Complex pipelines with logical grouping

---

## 🔄 Task Lifecycle and State Flow

### Task State Transitions

```mermaid
stateDiagram-v2
    [*] --> None
    None --> Scheduled
    Scheduled --> Queued
    Queued --> Running
    Running --> Success
    Running --> Failed
    Failed --> Retry
    Retry --> Queued
    Running --> Skipped
    Failed --> Upstream_Failed
    Success --> [*]
    Skipped --> [*]
    Upstream_Failed --> [*]
```

---

## 🏗️ DAG Execution Flow

### Complete Execution Lifecycle

```mermaid
sequenceDiagram
    participant Scheduler
    participant Metadata DB
    participant Executor
    participant Worker
    participant Task
    
    Scheduler->>Metadata DB: Parse DAG
    Scheduler->>Metadata DB: Create DAG Run
    Scheduler->>Metadata DB: Schedule Tasks
    Scheduler->>Executor: Queue Tasks
    Executor->>Worker: Assign Task
    Worker->>Task: Execute Task
    Task->>Worker: Return Result
    Worker->>Metadata DB: Update Task State
    Metadata DB->>Scheduler: Task Complete
```

---

## 📦 XCom Data Flow

### Cross-Task Communication

```mermaid
flowchart LR
    A[Task 1<br/>Push Data] -->|XCom Push| B[(XCom Store<br/>Metadata DB)]
    B -->|XCom Pull| C[Task 2<br/>Pull Data]
    C -->|Process| D[Task 3<br/>Use Data]
    
    style A fill:#4285f4,stroke:#1976d2,stroke-width:2px
    style B fill:#fbbc04,stroke:#f57c00,stroke-width:2px
    style C fill:#34a853,stroke:#2e7d32,stroke-width:2px
    style D fill:#ea4335,stroke:#c62828,stroke-width:2px
```

---

## 🔍 Sensor Operation Flow

### File Sensor Waiting Pattern

```mermaid
sequenceDiagram
    participant Sensor
    participant File System
    participant Scheduler
    
    loop Every Poke Interval
        Sensor->>File System: Check File Exists
        File System-->>Sensor: Not Found
        Sensor->>Scheduler: Reschedule
    end
    
    Sensor->>File System: Check File Exists
    File System-->>Sensor: Found!
    Sensor->>Scheduler: Task Success
    Scheduler->>Sensor: Trigger Downstream Tasks
```

---

## 🎯 Executor Comparison

### Executor Architecture Comparison

```mermaid
graph TB
    subgraph "Sequential Executor"
        A1[Scheduler] --> A2[Single Task Queue]
        A2 --> A3[Task Execution]
    end
    
    subgraph "Local Executor"
        B1[Scheduler] --> B2[Multiprocessing Queue]
        B2 --> B3[Worker 1]
        B2 --> B4[Worker 2]
        B2 --> B5[Worker N]
    end
    
    subgraph "Celery Executor"
        C1[Scheduler] --> C2[Redis/RabbitMQ<br/>Message Queue]
        C2 --> C3[Celery Worker 1]
        C2 --> C4[Celery Worker 2]
        C2 --> C5[Celery Worker N]
    end
    
    subgraph "K8s Executor"
        D1[Scheduler] --> D2[Kubernetes API]
        D2 --> D3[Pod 1]
        D2 --> D4[Pod 2]
        D2 --> D5[Pod N]
    end
    
    style A1 fill:#ea4335,stroke:#c62828,stroke-width:2px
    style B1 fill:#fbbc04,stroke:#f57c00,stroke-width:2px
    style C1 fill:#34a853,stroke:#2e7d32,stroke-width:2px
    style D1 fill:#4285f4,stroke:#1976d2,stroke-width:2px
```

---

## 🔄 Dynamic DAG Generation Flow

### Configuration-Driven DAG Creation

```mermaid
flowchart TD
    A[Configuration Files<br/>JSON/YAML] --> B[DAG Parser]
    B --> C{For Each Config}
    C --> D[Create DAG Function]
    D --> E[Generate Tasks]
    E --> F[Set Dependencies]
    F --> G[Register DAG]
    G --> H[Scheduler Picks Up]
    H --> I[Execute DAG]
    
    style A fill:#4285f4,stroke:#1976d2,stroke-width:2px
    style D fill:#34a853,stroke:#2e7d32,stroke-width:2px
    style I fill:#ea4335,stroke:#c62828,stroke-width:2px
```

---

## 🏛️ Production Architecture

### Scalable Production Setup

```mermaid
graph TB
    subgraph "Load Balancer"
        LB[NGINX/ALB]
    end
    
    subgraph "Webserver Cluster"
        WS1[Webserver 1]
        WS2[Webserver 2]
    end
    
    subgraph "Scheduler Cluster"
        SCH1[Scheduler 1]
        SCH2[Scheduler 2]
    end
    
    subgraph "Message Queue"
        MQ[Redis/RabbitMQ]
    end
    
    subgraph "Worker Cluster"
        W1[Worker 1]
        W2[Worker 2]
        W3[Worker N]
    end
    
    subgraph "Database"
        DB[(PostgreSQL<br/>Primary)]
        DB_REPLICA[(PostgreSQL<br/>Replica)]
    end
    
    subgraph "Monitoring"
        PROM[Prometheus]
        GRAF[Grafana]
    end
    
    LB --> WS1
    LB --> WS2
    WS1 --> DB
    WS2 --> DB
    SCH1 --> DB
    SCH2 --> DB
    SCH1 --> MQ
    SCH2 --> MQ
    MQ --> W1
    MQ --> W2
    MQ --> W3
    W1 --> DB
    W2 --> DB
    W3 --> DB
    DB --> DB_REPLICA
    SCH1 --> PROM
    SCH2 --> PROM
    W1 --> PROM
    PROM --> GRAF
    
    style LB fill:#4285f4,stroke:#1976d2,stroke-width:3px
    style DB fill:#ea4335,stroke:#c62828,stroke-width:3px
    style MQ fill:#fbbc04,stroke:#f57c00,stroke-width:3px
```

---

## 🔐 Security Architecture

### Authentication and Authorization Flow

```mermaid
sequenceDiagram
    participant User
    participant Webserver
    participant Auth Backend
    participant Metadata DB
    participant Executor
    
    User->>Webserver: Login Request
    Webserver->>Auth Backend: Authenticate
    Auth Backend->>Metadata DB: Check Credentials
    Metadata DB-->>Auth Backend: User Roles
    Auth Backend-->>Webserver: Auth Token
    Webserver-->>User: Session Created
    
    User->>Webserver: DAG Trigger Request
    Webserver->>Auth Backend: Check Permissions
    Auth Backend-->>Webserver: Authorized
    Webserver->>Executor: Trigger DAG
    Executor-->>Webserver: DAG Queued
```

---

## 📊 Monitoring and Observability

### Monitoring Stack

```mermaid
graph TB
    subgraph "Airflow Components"
        A[Scheduler]
        B[Webserver]
        C[Workers]
    end
    
    subgraph "Metrics Collection"
        D[Prometheus<br/>Exporter]
        E[StatsD]
    end
    
    subgraph "Log Aggregation"
        F[Elasticsearch]
        G[Logstash]
    end
    
    subgraph "Visualization"
        H[Grafana<br/>Dashboards]
        I[Kibana<br/>Logs]
    end
    
    subgraph "Alerting"
        J[AlertManager]
        K[PagerDuty]
        L[Slack]
    end
    
    A --> D
    B --> D
    C --> D
    A --> E
    B --> E
    C --> E
    A --> G
    B --> G
    C --> G
    D --> H
    E --> H
    G --> F
    F --> I
    D --> J
    J --> K
    J --> L
    
    style D fill:#4285f4,stroke:#1976d2,stroke-width:2px
    style H fill:#34a853,stroke:#2e7d32,stroke-width:2px
    style J fill:#ea4335,stroke:#c62828,stroke-width:2px
```

---

## 🔄 Error Handling and Retry Flow

### Task Failure and Retry Pattern

```mermaid
stateDiagram-v2
    [*] --> Running
    Running --> Success: Task Completes
    Running --> Failed: Exception Raised
    Failed --> CheckRetries: Retries Available?
    CheckRetries --> Retry: Yes
    CheckRetries --> FinalFailure: No
    Retry --> Waiting: Wait Retry Delay
    Waiting --> Running: Retry Task
    Success --> [*]
    FinalFailure --> [*]
    
    note right of Failed
        On Failure Callback
        Log Error
        Send Alert
    end note
```

---

## 🎯 Best Practices Visualization

### DAG Design Best Practices

```mermaid
mindmap
  root((DAG Best Practices))
    Idempotency
      Same Result on Rerun
      Deterministic Logic
      Handle Partial Failures
    Task Granularity
      Single Responsibility
      Focused Operations
      Easy to Debug
    Error Handling
      Appropriate Retries
      Exponential Backoff
      Proper Callbacks
    Resource Management
      Task Pools
      Queue Management
      Resource Limits
    Configuration
      Variables for Config
      Connections for Credentials
      No Hardcoding
    Monitoring
      SLAs
      Task Duration
      Failure Rates
      Alerts
```

---

## 📈 Performance Optimization Flow

### DAG Parsing Optimization

```mermaid
flowchart TD
    A[DAG File] --> B{Heavy Imports?}
    B -->|Yes| C[Move to Functions<br/>Lazy Imports]
    B -->|No| D[Fast Parsing]
    C --> D
    D --> E[Scheduler Picks Up]
    E --> F[Task Execution]
    
    style C fill:#fbbc04,stroke:#f57c00,stroke-width:2px
    style D fill:#34a853,stroke:#2e7d32,stroke-width:2px
```

---

## 🔗 Integration Patterns

### Airflow with External Systems

```mermaid
graph TB
    subgraph "Airflow"
        A[DAG]
        B[Operators]
        C[Hooks]
    end
    
    subgraph "Data Sources"
        D[Databases<br/>PostgreSQL, MySQL]
        E[APIs<br/>REST, GraphQL]
        F[File Systems<br/>S3, HDFS]
        G[Message Queues<br/>Kafka, RabbitMQ]
    end
    
    subgraph "Data Destinations"
        H[Data Warehouses<br/>Snowflake, BigQuery]
        I[Data Lakes<br/>S3, ADLS]
        J[Analytics<br/>Tableau, PowerBI]
    end
    
    A --> B
    B --> C
    C --> D
    C --> E
    C --> F
    C --> G
    C --> H
    C --> I
    C --> J
    
    style A fill:#4285f4,stroke:#1976d2,stroke-width:3px
    style C fill:#34a853,stroke:#2e7d32,stroke-width:3px
```

---

## 🎯 Key Visual Takeaways

1. **Architecture = Components** - Scheduler, Webserver, Executor, Workers
2. **DAG Patterns = Workflow Types** - Linear, Parallel, Branching, Event-Driven
3. **State Flow = Lifecycle** - None → Scheduled → Queued → Running → Success/Failed
4. **XComs = Communication** - Cross-task data exchange
5. **Sensors = Event-Driven** - Wait for conditions
6. **Executors = Scalability** - Choose based on scale needs
7. **Monitoring = Observability** - Metrics, logs, alerts
8. **Integration = Ecosystem** - Connect to external systems

---

## 📚 Next Steps

1. ✅ Review these visual diagrams
2. 🏗️ Draw them yourself to reinforce learning
3. 💬 Use in interviews to explain concepts
4. 🔗 Connect to your real projects
5. 📊 Create custom diagrams for your use cases

---

**Visual learning accelerates understanding!** Use these diagrams to master Airflow concepts. 🚀
