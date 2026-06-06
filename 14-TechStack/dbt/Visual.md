# dbt: Visual Guide

## Table of Contents
1. [Basic Architecture](#basic-architecture)
2. [Core Components](#core-components)
3. [Data Flow](#data-flow)
4. [Project Structure](#project-structure)
5. [Model Dependencies](#model-dependencies)
6. [Transformation Pipeline](#transformation-pipeline)
7. [Testing Framework](#testing-framework)
8. [Documentation System](#documentation-system)
9. [Advanced Patterns](#advanced-patterns)
10. [Deployment Workflow](#deployment-workflow)

---

## Basic Architecture

### dbt High-Level Architecture

```mermaid
graph TB
    subgraph "Data Sources"
        S1[Raw Data Sources]
        S2[External APIs]
        S3[Files]
    end
    
    subgraph "Data Warehouse"
        DW[(Data Warehouse<br/>BigQuery/Snowflake/Redshift)]
    end
    
    subgraph "dbt Layer"
        DBT[dbt Core]
        MODELS[SQL Models]
        TESTS[Tests]
        DOCS[Documentation]
    end
    
    subgraph "Output"
        O1[Transformed Tables]
        O2[Views]
        O3[Marts]
    end
    
    S1 --> DW
    S2 --> DW
    S3 --> DW
    DW --> DBT
    DBT --> MODELS
    MODELS --> TESTS
    MODELS --> DOCS
    MODELS --> O1
    MODELS --> O2
    MODELS --> O3
    O1 --> DW
    O2 --> DW
    O3 --> DW
    
    style DBT fill:#FF6B6B
    style MODELS fill:#4ECDC4
    style DW fill:#95E1D3
```

### dbt Core Components

```mermaid
graph LR
    subgraph "dbt Core"
        A[dbt CLI]
        B[Project Config]
        C[Profiles Config]
    end
    
    subgraph "Project Files"
        D[models/]
        E[macros/]
        F[tests/]
        G[snapshots/]
        H[seeds/]
    end
    
    subgraph "Execution"
        I[Parser]
        J[Compiler]
        K[Runner]
    end
    
    A --> B
    A --> C
    B --> D
    B --> E
    B --> F
    B --> G
    B --> H
    A --> I
    I --> J
    J --> K
    K --> D
    K --> E
    
    style A fill:#FF6B6B
    style I fill:#4ECDC4
    style J fill:#4ECDC4
    style K fill:#4ECDC4
```

---

## Core Components

### dbt Project Structure

```mermaid
graph TD
    ROOT[dbt_project/] --> CONFIG[dbt_project.yml]
    ROOT --> MODELS[models/]
    ROOT --> MACROS[macros/]
    ROOT --> TESTS[tests/]
    ROOT --> SNAPSHOTS[snapshots/]
    ROOT --> SEEDS[seeds/]
    ROOT --> ANALYSES[analyses/]
    ROOT --> DOCS[docs/]
    
    MODELS --> STAGING[staging/]
    MODELS --> INTERMEDIATE[intermediate/]
    MODELS --> MARTS[marts/]
    
    STAGING --> ST1[stg_customers.sql]
    STAGING --> ST2[stg_orders.sql]
    
    INTERMEDIATE --> INT1[int_order_items.sql]
    INTERMEDIATE --> INT2[int_customer_metrics.sql]
    
    MARTS --> M1[mart_customers.sql]
    MARTS --> M2[mart_orders.sql]
    MARTS --> M3[mart_products.sql]
    
    style ROOT fill:#FF6B6B
    style MODELS fill:#4ECDC4
    style MARTS fill:#95E1D3
```

### dbt Configuration Layers

```mermaid
graph TB
    subgraph "Configuration Hierarchy"
        L1[Command Line Args<br/>Highest Priority]
        L2[profiles.yml<br/>Connection Info]
        L3[dbt_project.yml<br/>Project Config]
        L4[Model Config<br/>Lowest Priority]
    end
    
    L1 --> L2
    L2 --> L3
    L3 --> L4
    
    L2 --> CONN[Database Connection]
    L3 --> PROJ[Project Settings]
    L4 --> MODEL[Model Settings]
    
    style L1 fill:#FF6B6B
    style L2 fill:#FFD93D
    style L3 fill:#4ECDC4
    style L4 fill:#95E1D3
```

---

## Data Flow

### Basic dbt Transformation Flow

```mermaid
flowchart LR
    START([Raw Data]) --> STAGE[Staging Models<br/>Clean & Standardize]
    STAGE --> INTER[Intermediate Models<br/>Business Logic]
    INTER --> MART[Mart Models<br/>Final Output]
    MART --> END([Analytics Ready])
    
    STAGE --> TEST1[Data Tests]
    INTER --> TEST2[Data Tests]
    MART --> TEST3[Data Tests]
    
    TEST1 --> DOCS[Documentation]
    TEST2 --> DOCS
    TEST3 --> DOCS
    
    style START fill:#FF6B6B
    style STAGE fill:#FFD93D
    style INTER fill:#4ECDC4
    style MART fill:#95E1D3
    style END fill:#6BCB77
```

### ELT vs ETL with dbt

```mermaid
graph TB
    subgraph "Traditional ETL"
        E1[Extract] --> T1[Transform]
        T1 --> L1[Load]
        L1 --> DW1[(Data Warehouse)]
    end
    
    subgraph "Modern ELT with dbt"
        E2[Extract] --> L2[Load]
        L2 --> DW2[(Data Warehouse)]
        DW2 --> T2[dbt Transform]
        T2 --> DW3[(Transformed Data)]
    end
    
    style T2 fill:#FF6B6B
    style DW2 fill:#4ECDC4
    style DW3 fill:#95E1D3
```

### Data Lineage Flow

```mermaid
graph TD
    RAW1[raw_customers] --> STG1[stg_customers]
    RAW2[raw_orders] --> STG2[stg_orders]
    RAW3[raw_products] --> STG3[stg_products]
    
    STG1 --> INT1[int_customer_orders]
    STG2 --> INT1
    STG3 --> INT2[int_product_sales]
    STG2 --> INT2
    
    INT1 --> MART1[mart_customer_metrics]
    INT2 --> MART2[mart_product_performance]
    INT1 --> MART3[mart_sales_summary]
    INT2 --> MART3
    
    style RAW1 fill:#FF6B6B
    style RAW2 fill:#FF6B6B
    style RAW3 fill:#FF6B6B
    style STG1 fill:#FFD93D
    style STG2 fill:#FFD93D
    style STG3 fill:#FFD93D
    style INT1 fill:#4ECDC4
    style INT2 fill:#4ECDC4
    style MART1 fill:#95E1D3
    style MART2 fill:#95E1D3
    style MART3 fill:#95E1D3
```

---

## Project Structure

### dbt Project Organization

```mermaid
graph TD
    PROJ[dbt_project/] --> YML[dbt_project.yml]
    PROJ --> MODELS[models/]
    PROJ --> MACROS[macros/]
    PROJ --> TESTS[tests/]
    PROJ --> SNAPSHOTS[snapshots/]
    PROJ --> SEEDS[seeds/]
    PROJ --> ANALYSES[analyses/]
    PROJ --> DOCS[docs/]
    PROJ --> TARGET[target/]
    PROJ --> LOGS[logs/]
    
    MODELS --> SCHEMA1[schema.yml]
    MODELS --> STAGING[staging/]
    MODELS --> INTERMEDIATE[intermediate/]
    MODELS --> MARTS[marts/]
    
    MACROS --> MAC1[macros/helpers.sql]
    MACROS --> MAC2[macros/utils.sql]
    
    TESTS --> TEST1[tests/assertions.sql]
    
    style PROJ fill:#FF6B6B
    style MODELS fill:#4ECDC4
    style MACROS fill:#FFD93D
```

### Model Layers Architecture

```mermaid
graph TB
    subgraph "Layer 1: Staging"
        ST1[stg_customers<br/>Source: raw.customers]
        ST2[stg_orders<br/>Source: raw.orders]
        ST3[stg_products<br/>Source: raw.products]
    end
    
    subgraph "Layer 2: Intermediate"
        INT1[int_customer_orders<br/>Joins customers + orders]
        INT2[int_order_items<br/>Joins orders + products]
        INT3[int_product_metrics<br/>Aggregates product data]
    end
    
    subgraph "Layer 3: Marts"
        MART1[mart_customers<br/>Customer analytics]
        MART2[mart_orders<br/>Order analytics]
        MART3[mart_products<br/>Product analytics]
    end
    
    ST1 --> INT1
    ST2 --> INT1
    ST2 --> INT2
    ST3 --> INT2
    ST3 --> INT3
    
    INT1 --> MART1
    INT1 --> MART2
    INT2 --> MART2
    INT2 --> MART3
    INT3 --> MART3
    
    style ST1 fill:#FF6B6B
    style ST2 fill:#FF6B6B
    style ST3 fill:#FF6B6B
    style INT1 fill:#FFD93D
    style INT2 fill:#FFD93D
    style INT3 fill:#FFD93D
    style MART1 fill:#4ECDC4
    style MART2 fill:#4ECDC4
    style MART3 fill:#4ECDC4
```

---

## Model Dependencies

### Dependency Graph

```mermaid
graph TD
    RAW1[raw.customers] --> STG1[stg_customers]
    RAW2[raw.orders] --> STG2[stg_orders]
    RAW3[raw.items] --> STG3[stg_order_items]
    
    STG1 --> INT1[int_customer_orders]
    STG2 --> INT1
    STG2 --> INT2[int_order_summary]
    STG3 --> INT2
    
    INT1 --> MART1[mart_customer_lifetime_value]
    INT2 --> MART2[mart_daily_sales]
    INT1 --> MART2
    
    MART1 --> DASH1[Dashboard: Customer Analytics]
    MART2 --> DASH2[Dashboard: Sales Analytics]
    
    style RAW1 fill:#FF6B6B
    style RAW2 fill:#FF6B6B
    style RAW3 fill:#FF6B6B
    style STG1 fill:#FFD93D
    style STG2 fill:#FFD93D
    style STG3 fill:#FFD93D
    style INT1 fill:#4ECDC4
    style INT2 fill:#4ECDC4
    style MART1 fill:#95E1D3
    style MART2 fill:#95E1D3
```

### Model Selection and Dependencies

```mermaid
flowchart TD
    START([dbt run]) --> SELECT{Model Selection}
    
    SELECT --> ALL[All Models]
    SELECT --> TAG[By Tag]
    SELECT --> PATH[By Path]
    SELECT --> CONFIG[By Config]
    
    ALL --> PARSE[Parse Dependencies]
    TAG --> PARSE
    PATH --> PARSE
    CONFIG --> PARSE
    
    PARSE --> BUILD[Build DAG]
    BUILD --> ORDER[Topological Sort]
    ORDER --> EXEC[Execute Models]
    
    EXEC --> SUCCESS{Success?}
    SUCCESS -->|Yes| NEXT[Next Model]
    SUCCESS -->|No| FAIL[Fail & Stop]
    
    NEXT --> EXEC
    FAIL --> END([End])
    EXEC --> END
    
    style START fill:#FF6B6B
    style PARSE fill:#4ECDC4
    style EXEC fill:#95E1D3
```

---

## Transformation Pipeline

### Complete Transformation Pipeline

```mermaid
flowchart LR
    subgraph "Source Layer"
        S1[Source 1]
        S2[Source 2]
        S3[Source 3]
    end
    
    subgraph "Staging Layer"
        ST1[Clean & Cast]
        ST2[Standardize]
        ST3[Validate]
    end
    
    subgraph "Intermediate Layer"
        INT1[Business Logic]
        INT2[Aggregations]
        INT3[Calculations]
    end
    
    subgraph "Mart Layer"
        M1[Customer Mart]
        M2[Sales Mart]
        M3[Product Mart]
    end
    
    S1 --> ST1
    S2 --> ST2
    S3 --> ST3
    
    ST1 --> INT1
    ST2 --> INT1
    ST3 --> INT2
    
    INT1 --> M1
    INT2 --> M2
    INT3 --> M3
    
    style S1 fill:#FF6B6B
    style ST1 fill:#FFD93D
    style INT1 fill:#4ECDC4
    style M1 fill:#95E1D3
```

### Incremental Model Strategy

```mermaid
flowchart TD
    START([dbt run --models incremental_model]) --> CHECK{Table Exists?}
    
    CHECK -->|No| FULL[Full Refresh<br/>Create Table]
    CHECK -->|Yes| INCR[Incremental Load]
    
    INCR --> FILTER[Filter New Records<br/>WHERE updated_at > max_updated_at]
    FILTER --> MERGE[Merge Strategy]
    
    MERGE --> DELETE[Delete+Insert]
    MERGE --> APPEND[Append Only]
    MERGE --> MERGE_STRAT[Merge Update]
    
    DELETE --> INSERT[Insert New Data]
    APPEND --> INSERT
    MERGE_STRAT --> UPDATE[Update Existing]
    MERGE_STRAT --> INSERT
    
    FULL --> INSERT
    INSERT --> END([Complete])
    UPDATE --> END
    
    style START fill:#FF6B6B
    style INCR fill:#4ECDC4
    style MERGE fill:#FFD93D
    style END fill:#95E1D3
```

---

## Testing Framework

### dbt Testing Architecture

```mermaid
graph TB
    subgraph "Test Types"
        T1[Generic Tests]
        T2[Singular Tests]
        T3[Custom Tests]
    end
    
    subgraph "Generic Tests"
        GT1[unique]
        GT2[not_null]
        GT3[accepted_values]
        GT4[relationships]
        GT5[expressions]
    end
    
    subgraph "Test Execution"
        EXEC[dbt test] --> PARSE[Parse Tests]
        PARSE --> RUN[Run Tests]
        RUN --> RESULT[Results]
    end
    
    T1 --> GT1
    T1 --> GT2
    T1 --> GT3
    T1 --> GT4
    T1 --> GT5
    
    GT1 --> EXEC
    GT2 --> EXEC
    GT3 --> EXEC
    GT4 --> EXEC
    GT5 --> EXEC
    T2 --> EXEC
    T3 --> EXEC
    
    RESULT --> PASS{Pass?}
    PASS -->|Yes| SUCCESS[Success]
    PASS -->|No| FAIL[Failure Report]
    
    style T1 fill:#FF6B6B
    style EXEC fill:#4ECDC4
    style SUCCESS fill:#95E1D3
    style FAIL fill:#FF6B6B
```

### Test Coverage Strategy

```mermaid
flowchart TD
    MODEL[Model] --> TESTS[Tests]
    
    TESTS --> COLUMN[Column Tests]
    TESTS --> ROW[Row Tests]
    TESTS --> RELATIONSHIP[Relationship Tests]
    TESTS --> CUSTOM[Custom Tests]
    
    COLUMN --> C1[not_null]
    COLUMN --> C2[unique]
    COLUMN --> C3[accepted_values]
    
    ROW --> R1[expressions]
    ROW --> R2[dbt_utils.expression_is_true]
    
    RELATIONSHIP --> REL1[relationships]
    RELATIONSHIP --> REL2[referential_integrity]
    
    CUSTOM --> CUST1[SQL Assertions]
    CUSTOM --> CUST2[Macro Tests]
    
    C1 --> REPORT[Test Report]
    C2 --> REPORT
    C3 --> REPORT
    R1 --> REPORT
    R2 --> REPORT
    REL1 --> REPORT
    REL2 --> REPORT
    CUST1 --> REPORT
    CUST2 --> REPORT
    
    style MODEL fill:#FF6B6B
    style TESTS fill:#4ECDC4
    style REPORT fill:#95E1D3
```

---

## Documentation System

### dbt Documentation Flow

```mermaid
flowchart LR
    CODE[SQL Models] --> YML[schema.yml]
    MACROS[Macros] --> YML
    TESTS[Tests] --> YML
    
    YML --> DOCS[Documentation]
    CODE --> DOCS
    
    DOCS --> GEN[dbt docs generate]
    GEN --> SERVE[dbt docs serve]
    
    SERVE --> WEB[Web Interface]
    
    WEB --> LINEAGE[Lineage Graph]
    WEB --> DESCR[Descriptions]
    WEB --> COLUMNS[Column Docs]
    WEB --> TESTS_DOC[Test Docs]
    
    style CODE fill:#FF6B6B
    style YML fill:#FFD93D
    style DOCS fill:#4ECDC4
    style WEB fill:#95E1D3
```

### Documentation Structure

```mermaid
graph TD
    DOCS[dbt Documentation] --> PROJECT[Project Docs]
    DOCS --> MODELS[Model Docs]
    DOCS --> SOURCES[Source Docs]
    DOCS --> MACROS[Macro Docs]
    DOCS --> TESTS[Test Docs]
    
    PROJECT --> PROJ_DESC[Description]
    PROJECT --> VERSION[Version]
    
    MODELS --> MODEL_DESC[Model Description]
    MODELS --> COL_DESC[Column Descriptions]
    MODELS --> META[Metadata]
    
    SOURCES --> SOURCE_DESC[Source Description]
    SOURCES --> TABLE_DESC[Table Descriptions]
    
    MACROS --> MACRO_DESC[Macro Description]
    MACROS --> PARAMS[Parameters]
    
    TESTS --> TEST_DESC[Test Description]
    TESTS --> EXPECTED[Expected Results]
    
    style DOCS fill:#FF6B6B
    style MODELS fill:#4ECDC4
    style SOURCES fill:#FFD93D
```

---

## Advanced Patterns

### Snapshot Strategy

```mermaid
flowchart TD
    START([dbt snapshot]) --> LOAD[Load Source Data]
    LOAD --> CHECK{Snapshot Table Exists?}
    
    CHECK -->|No| CREATE[Create Snapshot Table]
    CHECK -->|Yes| COMPARE[Compare with Existing]
    
    CREATE --> INSERT[Insert All Records]
    
    COMPARE --> CHANGED{Records Changed?}
    CHANGED -->|Yes| UPDATE[Update dbt_valid_to]
    CHANGED -->|No| SKIP[Skip]
    
    UPDATE --> INSERT_NEW[Insert New Records]
    INSERT_NEW --> SET_VALID[Set dbt_valid_from]
    
    INSERT --> END([Complete])
    SKIP --> END
    SET_VALID --> END
    
    style START fill:#FF6B6B
    style COMPARE fill:#4ECDC4
    style UPDATE fill:#FFD93D
    style END fill:#95E1D3
```

### Materialization Strategies

```mermaid
graph TB
    subgraph "Materialization Types"
        M1[table]
        M2[view]
        M3[incremental]
        M4[ephemeral]
        M5[snapshot]
    end
    
    subgraph "Table"
        T1[Creates Physical Table]
        T2[Fastest Query Performance]
        T3[Slower Build Time]
    end
    
    subgraph "View"
        V1[Creates SQL View]
        V2[Always Up-to-Date]
        V3[Slower Query Performance]
    end
    
    subgraph "Incremental"
        I1[Appends/Updates Table]
        I2[Fast Build for Large Data]
        I3[Requires Unique Key]
    end
    
    M1 --> T1
    M1 --> T2
    M1 --> T3
    
    M2 --> V1
    M2 --> V2
    M2 --> V3
    
    M3 --> I1
    M3 --> I2
    M3 --> I3
    
    style M1 fill:#FF6B6B
    style M2 fill:#FFD93D
    style M3 fill:#4ECDC4
```

### Macro Usage Pattern

```mermaid
flowchart LR
    MACRO[Macro Definition] --> PARAMS[Parameters]
    PARAMS --> LOGIC[SQL Logic]
    LOGIC --> COMPILE[Compile SQL]
    
    MODEL[Model] --> CALL[Call Macro]
    CALL --> COMPILE
    COMPILE --> SQL[Generated SQL]
    SQL --> EXEC[Execute]
    
    MACRO --> REUSE[Reusable Logic]
    REUSE --> MODEL1[Model 1]
    REUSE --> MODEL2[Model 2]
    REUSE --> MODEL3[Model 3]
    
    style MACRO fill:#FF6B6B
    style COMPILE fill:#4ECDC4
    style EXEC fill:#95E1D3
```

### Hook Execution Flow

```mermaid
flowchart TD
    START([dbt Command]) --> PRE_HOOK[Pre-Hooks]
    
    PRE_HOOK --> ON_RUN_START[on-run-start]
    ON_RUN_START --> RUN[Run Models]
    
    RUN --> MODEL1[Model 1]
    RUN --> MODEL2[Model 2]
    RUN --> MODEL3[Model 3]
    
    MODEL1 --> POST_HOOK1[Post-Hook 1]
    MODEL2 --> POST_HOOK2[Post-Hook 2]
    MODEL3 --> POST_HOOK3[Post-Hook 3]
    
    POST_HOOK1 --> ON_RUN_END[on-run-end]
    POST_HOOK2 --> ON_RUN_END
    POST_HOOK3 --> ON_RUN_END
    
    ON_RUN_END --> END([Complete])
    
    style START fill:#FF6B6B
    style PRE_HOOK fill:#FFD93D
    style RUN fill:#4ECDC4
    style ON_RUN_END fill:#95E1D3
```

---

## Deployment Workflow

### CI/CD Pipeline with dbt

```mermaid
flowchart LR
    DEV[Development] --> COMMIT[Git Commit]
    COMMIT --> CI[CI Pipeline]
    
    CI --> LINT[dbt parse]
    CI --> TEST[dbt test]
    CI --> BUILD[dbt build]
    
    LINT --> LINT_RESULT{Lint Pass?}
    TEST --> TEST_RESULT{Tests Pass?}
    BUILD --> BUILD_RESULT{Build Success?}
    
    LINT_RESULT -->|No| FAIL1[Fail CI]
    TEST_RESULT -->|No| FAIL2[Fail CI]
    BUILD_RESULT -->|No| FAIL3[Fail CI]
    
    LINT_RESULT -->|Yes| MERGE
    TEST_RESULT -->|Yes| MERGE
    BUILD_RESULT -->|Yes| MERGE
    
    MERGE[Merge to Main] --> PROD[Production]
    PROD --> DEPLOY[dbt run --target prod]
    DEPLOY --> MONITOR[Monitor]
    
    style DEV fill:#FF6B6B
    style CI fill:#FFD93D
    style PROD fill:#4ECDC4
    style MONITOR fill:#95E1D3
```

### Environment Strategy

```mermaid
graph TB
    subgraph "Environments"
        DEV[Development]
        STAGING[Staging]
        PROD[Production]
    end
    
    subgraph "Development"
        DEV_PROF[dev profile]
        DEV_SCHEMA[dev schema]
        DEV_TARGET[dev target]
    end
    
    subgraph "Staging"
        STAGE_PROF[staging profile]
        STAGE_SCHEMA[staging schema]
        STAGE_TARGET[staging target]
    end
    
    subgraph "Production"
        PROD_PROF[prod profile]
        PROD_SCHEMA[prod schema]
        PROD_TARGET[prod target]
    end
    
    DEV --> DEV_PROF
    DEV --> DEV_SCHEMA
    DEV --> DEV_TARGET
    
    STAGING --> STAGE_PROF
    STAGING --> STAGE_SCHEMA
    STAGING --> STAGE_TARGET
    
    PROD --> PROD_PROF
    PROD --> PROD_SCHEMA
    PROD --> PROD_TARGET
    
    style DEV fill:#FF6B6B
    style STAGING fill:#FFD93D
    style PROD fill:#4ECDC4
```

### dbt Cloud Workflow

```mermaid
flowchart TD
    TRIGGER[Trigger] --> QUEUE[Queue Job]
    
    TRIGGER --> SCHEDULE[Scheduled]
    TRIGGER --> MANUAL[Manual]
    TRIGGER --> API[API Call]
    TRIGGER --> WEBHOOK[Webhook]
    
    QUEUE --> EXECUTE[Execute Job]
    
    EXECUTE --> STEP1[Install dbt]
    STEP1 --> STEP2[Install Dependencies]
    STEP2 --> STEP3[Run dbt Commands]
    
    STEP3 --> RUN[dbt run]
    STEP3 --> TEST[dbt test]
    STEP3 --> DOCS[dbt docs generate]
    
    RUN --> RESULT[Results]
    TEST --> RESULT
    DOCS --> RESULT
    
    RESULT --> NOTIFY[Notifications]
    NOTIFY --> EMAIL[Email]
    NOTIFY --> SLACK[Slack]
    NOTIFY --> WEB[Web UI]
    
    style TRIGGER fill:#FF6B6B
    style EXECUTE fill:#4ECDC4
    style RESULT fill:#95E1D3
```

---

## Summary

This visual guide covers dbt from basic concepts to advanced patterns:

1. **Basic Architecture**: Understanding how dbt fits into the data stack
2. **Core Components**: Project structure and configuration
3. **Data Flow**: How data moves through transformations
4. **Model Dependencies**: Understanding the DAG and execution order
5. **Transformation Pipeline**: Staging → Intermediate → Marts pattern
6. **Testing Framework**: Comprehensive testing strategies
7. **Documentation System**: Auto-generated documentation
8. **Advanced Patterns**: Snapshots, macros, hooks, and materializations
9. **Deployment Workflow**: CI/CD and environment management

Each diagram illustrates key concepts and relationships in dbt, helping you understand both the fundamentals and advanced usage patterns.
