# Snowflake Visual Playbook

## Platform Architecture
```mermaid
flowchart LR
    subgraph Landing
        S3[S3 / ADLS / GCS]
        Apps[SaaS / OLTP]
    end
    S3 --> Snowpipe[Snowpipe / Streams]
    Apps --> Snowpipe
    Snowpipe --> Storage[Central Storage Layer]
    Storage --> Warehouses[Virtual Warehouses]
    Warehouses --> BI[BI / Dashboards]
    Warehouses --> ML[Snowpark / Feature Store]
    Storage --> Sharing[Secure Shares / Marketplace]
```

## Warehouse & Workload Isolation
```mermaid
graph LR
    Users --> BI_WH[BI Warehouse]
    Pipelines --> ETL_WH[ETL Warehouse]
    DataScientists --> ML_WH[ML Warehouse]
    BI_WH --> Storage
    ETL_WH --> Storage
    ML_WH --> Storage
    ETL_WH --> StreamsTasks[Streams & Tasks]
```

## Data Lifecycle
```mermaid
stateDiagram-v2
    [*] --> Ingest: COPY / Snowpipe
    Ingest --> Stage: RAW schema
    Stage --> Transform: Streams + Tasks
    Transform --> Curate: MARTS schema
    Curate --> Share: Secure Shares / Marketplace
    Curate --> MLServing: Snowpark / External Functions
```

## Time Travel & Cloning Flow
```mermaid
sequenceDiagram
    participant Dev
    participant Snowflake
    Dev->>Snowflake: CREATE TABLE t CLONE prod.t;
    Snowflake-->>Dev: Instant clone (metadata only)
    Dev->>Snowflake: UPDATE dev copy
    Dev->>Snowflake: Time travel query AT TIMESTAMP => '2024-11-21 10:00';
    Snowflake-->>Dev: Historical snapshot
```

## Multi-Cloud Replication
```mermaid
graph TB
    Primary[(Primary Region)]
    Secondary[(Secondary Region)]
    Tertiary[(Marketplace / Reader Account)]

    Primary --> Secondary: Database Replication
    Secondary --> Primary: Failover
    Primary --> Tertiary: Secure Share
```

## Comparison Grid
| Mode | Layout | State Strategy | Deployment |
| --- | --- | --- | --- |
| Speed Cards | Single warehouse, dashboards | Result cache + auto-suspend | Small warehouse, Streamlit BI |
| Deep Dive | Streams + Tasks + curated marts | Streams, Tasks, clustering | Dedicated ETL + BI warehouses |
| Architect | Multi-region replication, sharing | Resource monitors, tagging, policies | Multi-cloud, Infrastructure-as-code |

## Visual Cues
- Highlight separation between storage and compute.
- Emphasize Streams + Tasks for incremental pipelines.
- Show masking/row policies layered on curated schemas.
- Use annotation callouts for credit-saving levers (auto-suspend, multi-cluster).

