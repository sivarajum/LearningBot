# POC-04 End-to-End ML Pipeline Architecture Plan

## Overview
This POC builds a complete machine learning pipeline for customer churn prediction, from real-time data ingestion through model deployment, demonstrating production-ready MLOps practices.

## System Architecture

```mermaid
graph TB
    %% Define styles
    classDef dataClass fill:#e3f2fd,stroke:#1976d2,stroke-width:3px,color:#0d47a1
    classDef processClass fill:#f3e5f5,stroke:#7b1fa2,stroke-width:3px,color:#4a148c
    classDef serveClass fill:#e8f5e8,stroke:#388e3c,stroke-width:3px,color:#1b5e20
    classDef monitorClass fill:#fff3e0,stroke:#f57c00,stroke-width:3px,color:#e65100
    classDef infraClass fill:#fce4ec,stroke:#c2185b,stroke-width:3px,color:#880e4f

    subgraph "📥 Data Ingestion Layer"
        PUBSUB[📡 Google Cloud Pub/Sub]
        PUBSUB --> DF[🌊 Dataflow Streaming]
        DF --> BQ[📊 BigQuery Data Warehouse]
    end

    subgraph "⚙️ Processing Layer"
        BQ --> ML[🤖 ML Pipeline]
        ML --> VERTEX[🚀 Vertex AI Training]
        VERTEX --> MODEL[🏆 Trained Model]
    end

    subgraph "🔮 Serving Layer"
        MODEL --> ENDPOINT[🔌 Vertex AI Endpoint]
        ENDPOINT --> API[🔗 REST API]
        API --> APP[📊 Streamlit Dashboard]
    end

    subgraph "📊 Monitoring Layer"
        MONITOR[📊 Cloud Monitoring]
        MONITOR --> ALERTS[🚨 Alerting System]
        ALERTS --> NOTIF[📱 Notifications]
    end

    subgraph "🏗️ Infrastructure"
        GKE[🚢 GKE Cluster]
        GKE --> WORKLOADS[🐳 Container Workloads]
        CLOUD_BUILD[🔨 Cloud Build]
        CLOUD_BUILD --> CI_CD[🔄 CI/CD Pipeline]
    end

    %% Apply styles
    class PUBSUB,DF,BQ dataClass
    class ML,VERTEX,MODEL processClass
    class ENDPOINT,API,APP serveClass
    class MONITOR,ALERTS,NOTIF monitorClass
    class GKE,WORKLOADS,CLOUD_BUILD,CI_CD infraClass
```

## Complete Data Pipeline Flow

```mermaid
flowchart TD
    %% Define styles
    classDef dataClass fill:#e3f2fd,stroke:#1976d2,stroke-width:2px,color:#0d47a1
    classDef processClass fill:#f3e5f5,stroke:#7b1fa2,stroke-width:2px,color:#4a148c
    classDef trainingClass fill:#e8f5e8,stroke:#388e3c,stroke-width:2px,color:#1b5e20
    classDef deployClass fill:#fff3e0,stroke:#f57c00,stroke-width:2px,color:#e65100
    classDef monitorClass fill:#fce4ec,stroke:#c2185b,stroke-width:2px,color:#880e4f

    A[📊 Customer Events] --> B[📡 Pub/Sub Topics]
    B --> C[🌊 Dataflow Streaming Pipeline]

    C --> D[✅ Data Validation]
    D --> E{✅ Valid Data?}
    E -->|❌ No| F[📭 Dead Letter Queue]
    E -->|✅ Yes| G[🔄 Data Transformation]

    G --> H[⚙️ Feature Engineering]
    H --> I[📊 BigQuery Tables]
    I --> J[💾 Historical Data Store]

    J --> K[🎯 Training Data Preparation]
    K --> L[🏪 Feature Store Population]
    L --> M[🚀 Model Training Trigger]

    M --> N[🤖 Vertex AI Custom Training]
    N --> O[⚙️ Hyperparameter Tuning]
    O --> P[📊 Model Evaluation]

    P --> Q{⭐ Model Approved?}
    Q -->|❌ No| R[🔄 Model Iteration]
    R --> N
    Q -->|✅ Yes| S[📝 Model Registration]

    S --> T[🚀 Model Deployment]
    T --> U[🔌 Vertex AI Endpoint]
    U --> V[🌐 API Gateway]

    V --> W[⚡ Real-time Predictions]
    W --> X[📝 Prediction Logging]
    X --> Y[📊 Performance Monitoring]

    Y --> Z[🔍 Drift Detection]
    Z --> AA{🚨 Drift Detected?}
    AA -->|✅ Yes| BB[🔄 Retraining Trigger]
    BB --> M
    AA -->|❌ No| CC[▶️ Continue Serving]

    %% Apply styles
    class A,B,C dataClass
    class D,E,F,G,H,I,J,K,L processClass
    class M,N,O,P,R,S trainingClass
    class Q,T,U,V,W deployClass
    class X,Y,Z,AA,BB,CC monitorClass
```

## Real-time Data Ingestion Architecture

```mermaid
graph TD
    %% Define styles
    classDef sourceClass fill:#e3f2fd,stroke:#1976d2,stroke-width:3px,color:#0d47a1
    classDef ingestClass fill:#f3e5f5,stroke:#7b1fa2,stroke-width:3px,color:#4a148c
    classDef processClass fill:#e8f5e8,stroke:#388e3c,stroke-width:3px,color:#1b5e20
    classDef streamClass fill:#fff3e0,stroke:#f57c00,stroke-width:3px,color:#e65100
    classDef storageClass fill:#fce4ec,stroke:#c2185b,stroke-width:3px,color:#880e4f

    subgraph "📱 Data Sources"
        APP[📱 Mobile App]
        WEB[🌐 Web Application]
        API[🔌 External APIs]
        IOT[📡 IoT Devices]
    end

    subgraph "📥 Ingestion Layer"
        PS[📡 Pub/Sub]
        PS --> DF[🌊 Dataflow]
        DF --> BQ[📊 BigQuery]
    end

    subgraph "⚙️ Processing Pipeline"
        BQ --> DQ[✅ Data Quality Checks]
        DQ --> FE[⚙️ Feature Engineering]
        FE --> FS[🏪 Feature Store]
    end

    subgraph "🌊 Streaming Components"
        DF --> WINDOW[🪟 Windowing]
        WINDOW --> AGG[📊 Aggregation]
        AGG --> TRANS[🔄 Transformation]
    end

    subgraph "💾 Storage"
        FS --> REDIS[⚡ Redis Cache]
        FS --> BQ_WH[📊 BigQuery Warehouse]
        BQ_WH --> GCS[☁️ Cloud Storage]
    end

    APP --> PS
    WEB --> PS
    API --> PS
    IOT --> PS

    %% Apply styles
    class APP,WEB,API,IOT sourceClass
    class PS,DF,BQ ingestClass
    class DQ,FE,FS processClass
    class WINDOW,AGG,TRANS streamClass
    class REDIS,BQ_WH,GCS storageClass
```

## ML Pipeline Architecture

```mermaid
graph TD
    %% Define styles
    classDef orchestrateClass fill:#e3f2fd,stroke:#1976d2,stroke-width:4px,color:#0d47a1
    classDef dataClass fill:#f3e5f5,stroke:#7b1fa2,stroke-width:3px,color:#4a148c
    classDef mlClass fill:#e8f5e8,stroke:#388e3c,stroke-width:3px,color:#1b5e20
    classDef infraClass fill:#fff3e0,stroke:#f57c00,stroke-width:2px,color:#e65100
    classDef metadataClass fill:#fce4ec,stroke:#c2185b,stroke-width:3px,color:#880e4f

    subgraph "🎼 Pipeline Orchestration"
        KF[🎼 Kubeflow Pipelines]
        KF --> COMPONENTS[🧩 Pipeline Components]
    end

    subgraph "📊 Data Components"
        COMPONENTS --> DATA_INGEST[📥 Data Ingestion]
        COMPONENTS --> DATA_VALID[✅ Data Validation]
        COMPONENTS --> DATA_SPLIT[✂️ Train/Val/Test Split]
    end

    subgraph "🤖 ML Components"
        COMPONENTS --> FEATURE_ENG[⚙️ Feature Engineering]
        COMPONENTS --> MODEL_TRAIN[🚀 Model Training]
        COMPONENTS --> MODEL_EVAL[📊 Model Evaluation]
        COMPONENTS --> MODEL_DEPLOY[🚀 Model Deployment]
    end

    subgraph "🏗️ Infrastructure"
        GKE --> KF
        GCS --> COMPONENTS
        BQ --> COMPONENTS
        VERTEX --> MODEL_DEPLOY
    end

    subgraph "📋 Metadata"
        MLMD[📋 ML Metadata]
        MLMD --> LINEAGE[🔗 Model Lineage]
        MLMD --> METRICS[📊 Performance Metrics]
    end

    %% Apply styles
    class KF,COMPONENTS orchestrateClass
    class DATA_INGEST,DATA_VALID,DATA_SPLIT dataClass
    class FEATURE_ENG,MODEL_TRAIN,MODEL_EVAL,MODEL_DEPLOY mlClass
    class GKE,GCS,BQ,VERTEX infraClass
    class MLMD,LINEAGE,METRICS metadataClass
```

## Model Training and Evaluation Flow

```mermaid
flowchart TD
    %% Define styles
    classDef dataClass fill:#e3f2fd,stroke:#1976d2,stroke-width:2px,color:#0d47a1
    classDef preprocessClass fill:#f3e5f5,stroke:#7b1fa2,stroke-width:2px,color:#4a148c
    classDef trainingClass fill:#e8f5e8,stroke:#388e3c,stroke-width:2px,color:#1b5e20
    classDef evalClass fill:#fff3e0,stroke:#f57c00,stroke-width:2px,color:#e65100
    classDef deployClass fill:#fce4ec,stroke:#c2185b,stroke-width:2px,color:#880e4f

    A[📊 Training Data] --> B[🔄 Data Preprocessing]
    B --> C[⚙️ Feature Engineering]
    C --> D[🎯 Feature Selection]

    D --> E[✂️ Train-Validation Split]
    E --> F[🎯 Model Selection]
    F --> G1[💡 LightGBM]
    F --> G2[🚀 XGBoost]
    F --> G3[🌲 Random Forest]
    F --> G4[🧠 Neural Network]

    G1 --> H1[🔄 Cross Validation]
    G2 --> H2[🔄 Cross Validation]
    G3 --> H3[🔄 Cross Validation]
    G4 --> H4[🔄 Cross Validation]

    H1 --> I1[⚙️ Hyperparameter Tuning]
    H2 --> I2[⚙️ Hyperparameter Tuning]
    H3 --> I3[⚙️ Hyperparameter Tuning]
    H4 --> I4[⚙️ Hyperparameter Tuning]

    I1 --> J[📊 Model Evaluation]
    I2 --> J
    I3 --> J
    I4 --> J

    J --> K[📈 Performance Metrics]
    K --> L[🎯 Accuracy, Precision, Recall]
    L --> M[📊 AUC-ROC, F1-Score]
    M --> N[💼 Business Metrics]

    N --> O[🏆 Model Selection]
    O --> P[📦 Model Packaging]
    P --> Q[🐳 Container Image]
    Q --> R[📚 Model Registry]

    R --> S[🚀 Staging Deployment]
    S --> T[🧪 Integration Testing]
    T --> U[🎉 Production Deployment]

    %% Apply styles
    class A,B,C,D,E dataClass
    class F,G1,G2,G3,G4,H1,H2,H3,H4,I1,I2,I3,I4 preprocessClass
    class J,K,L,M,N trainingClass
    class O,P,Q,R evalClass
    class S,T,U deployClass
```

## Model Serving and API Architecture

```mermaid
graph TD
    %% Define styles
    classDef gatewayClass fill:#e3f2fd,stroke:#1976d2,stroke-width:3px,color:#0d47a1
    classDef serveClass fill:#f3e5f5,stroke:#7b1fa2,stroke-width:3px,color:#4a148c
    classDef responseClass fill:#e8f5e8,stroke:#388e3c,stroke-width:3px,color:#1b5e20
    classDef monitorClass fill:#fff3e0,stroke:#f57c00,stroke-width:3px,color:#e65100
    classDef cacheClass fill:#fce4ec,stroke:#c2185b,stroke-width:3px,color:#880e4f

    subgraph "🌐 API Gateway"
        GATEWAY[🌐 API Gateway]
        GATEWAY --> AUTH[🔐 Authentication]
        AUTH --> RATE_LIMIT[⏱️ Rate Limiting]
        RATE_LIMIT --> ROUTING[🛣️ Request Routing]
    end

    subgraph "🚀 Serving Infrastructure"
        ROUTING --> VERTEX_EP[🔌 Vertex AI Endpoint]
        VERTEX_EP --> MODEL[🤖 ML Model]
        MODEL --> PREDICTION[🔮 Prediction Service]
    end

    subgraph "⚙️ Response Processing"
        PREDICTION --> POST_PROC[🔄 Post-processing]
        POST_PROC --> FORMAT[🎨 Response Formatting]
        FORMAT --> LOGGING[📝 Request Logging]
    end

    subgraph "📊 Monitoring"
        LOGGING --> METRICS[📊 Performance Metrics]
        METRICS --> DASHBOARD[📊 Monitoring Dashboard]
        DASHBOARD --> ALERTS[🚨 Alert System]
    end

    subgraph "💾 Caching Layer"
        CACHE[⚡ Redis Cache]
        CACHE --> FAST_PATH[⚡ Fast Path Serving]
        FAST_PATH --> GATEWAY
    end

    %% Apply styles
    class GATEWAY,AUTH,RATE_LIMIT,ROUTING gatewayClass
    class VERTEX_EP,MODEL,PREDICTION serveClass
    class POST_PROC,FORMAT,LOGGING responseClass
    class METRICS,DASHBOARD,ALERTS monitorClass
    class CACHE,FAST_PATH cacheClass
```

## Monitoring and Observability Architecture

```mermaid
graph TD
    %% Define styles
    classDef appMetricsClass fill:#e3f2fd,stroke:#1976d2,stroke-width:3px,color:#0d47a1
    classDef modelMetricsClass fill:#f3e5f5,stroke:#7b1fa2,stroke-width:3px,color:#4a148c
    classDef infraMetricsClass fill:#e8f5e8,stroke:#388e3c,stroke-width:3px,color:#1b5e20
    classDef monitorClass fill:#fff3e0,stroke:#f57c00,stroke-width:3px,color:#e65100
    classDef loggingClass fill:#fce4ec,stroke:#c2185b,stroke-width:3px,color:#880e4f

    subgraph "📱 Application Metrics"
        APP_METRICS[📱 Application Metrics]
        APP_METRICS --> LATENCY[⏱️ Response Latency]
        APP_METRICS --> THROUGHPUT[📈 Request Throughput]
        APP_METRICS --> ERROR_RATE[❌ Error Rate]
    end

    subgraph "🤖 Model Metrics"
        MODEL_METRICS[🤖 Model Metrics]
        MODEL_METRICS --> ACCURACY[🎯 Model Accuracy]
        MODEL_METRICS --> DRIFT[📊 Data Drift]
        MODEL_METRICS --> QUALITY[⭐ Prediction Quality]
    end

    subgraph "🏗️ Infrastructure Metrics"
        INFRA_METRICS[🏗️ Infrastructure Metrics]
        INFRA_METRICS --> CPU[💻 CPU Usage]
        INFRA_METRICS --> MEMORY[🧠 Memory Usage]
        INFRA_METRICS --> DISK[💾 Disk Usage]
    end

    subgraph "📊 Monitoring Stack"
        PROMETHEUS[📊 Prometheus]
        PROMETHEUS --> GRAFANA[📊 Grafana Dashboards]
        GRAFANA --> ALERTS[🚨 Alert Manager]
    end

    subgraph "📝 Logging"
        LOGS[📝 Application Logs]
        LOGS --> CLOUD_LOGGING[☁️ Cloud Logging]
        CLOUD_LOGGING --> ANALYSIS[🔍 Log Analysis]
    end

    LATENCY --> PROMETHEUS
    ACCURACY --> PROMETHEUS
    CPU --> PROMETHEUS
    LOGS --> CLOUD_LOGGING

    %% Apply styles
    class APP_METRICS,LATENCY,THROUGHPUT,ERROR_RATE appMetricsClass
    class MODEL_METRICS,ACCURACY,DRIFT,QUALITY modelMetricsClass
    class INFRA_METRICS,CPU,MEMORY,DISK infraMetricsClass
    class PROMETHEUS,GRAFANA,ALERTS monitorClass
    class LOGS,CLOUD_LOGGING,ANALYSIS loggingClass
```

## CI/CD Pipeline Architecture

```mermaid
graph LR
    %% Define styles
    classDef sourceClass fill:#e3f2fd,stroke:#1976d2,stroke-width:3px,color:#0d47a1
    classDef buildClass fill:#f3e5f5,stroke:#7b1fa2,stroke-width:3px,color:#4a148c
    classDef testClass fill:#e8f5e8,stroke:#388e3c,stroke-width:3px,color:#1b5e20
    classDef deployClass fill:#fff3e0,stroke:#f57c00,stroke-width:3px,color:#e65100
    classDef monitorClass fill:#fce4ec,stroke:#c2185b,stroke-width:3px,color:#880e4f

    subgraph "📂 Source Control"
        GITHUB[📂 GitHub Repository]
        GITHUB --> WEBHOOK[🔗 Webhook Trigger]
    end

    subgraph "🏗️ Build Stage"
        CLOUDBUILD[🏗️ Cloud Build]
        CLOUDBUILD --> DOCKER[🐳 Docker Build]
        DOCKER --> ARTIFACTS[📦 Build Artifacts]
    end

    subgraph "🧪 Testing Stage"
        UNIT_TESTS[🧪 Unit Tests]
        INTEGRATION_TESTS[🔗 Integration Tests]
        MODEL_TESTS[🤖 Model Validation Tests]
    end

    subgraph "🚀 Deployment Stage"
        STAGING[🚀 Staging Environment]
        STAGING --> PRODUCTION[🎯 Production Environment]
        PRODUCTION --> ROLLBACK[↩️ Rollback Strategy]
    end

    subgraph "📊 Monitoring"
        HEALTH_CHECKS[💚 Health Checks]
        HEALTH_CHECKS --> METRICS[📊 Performance Metrics]
        METRICS --> ALERTS[🚨 Automated Alerts]
    end

    WEBHOOK --> CLOUDBUILD
    ARTIFACTS --> UNIT_TESTS
    UNIT_TESTS --> INTEGRATION_TESTS
    INTEGRATION_TESTS --> MODEL_TESTS
    MODEL_TESTS --> STAGING
    STAGING --> PRODUCTION
    PRODUCTION --> HEALTH_CHECKS

    %% Apply styles
    class GITHUB,WEBHOOK sourceClass
    class CLOUDBUILD,DOCKER,ARTIFACTS buildClass
    class UNIT_TESTS,INTEGRATION_TESTS,MODEL_TESTS testClass
    class STAGING,PRODUCTION,ROLLBACK deployClass
    class HEALTH_CHECKS,METRICS,ALERTS monitorClass
```

## Technology Stack

```mermaid
graph TD
    %% Define styles
    classDef dataClass fill:#e3f2fd,stroke:#1976d2,stroke-width:3px,color:#0d47a1
    classDef mlClass fill:#f3e5f5,stroke:#7b1fa2,stroke-width:3px,color:#4a148c
    classDef infraClass fill:#e8f5e8,stroke:#388e3c,stroke-width:3px,color:#1b5e20
    classDef devopsClass fill:#fff3e0,stroke:#f57c00,stroke-width:3px,color:#e65100
    classDef monitoringClass fill:#fce4ec,stroke:#c2185b,stroke-width:3px,color:#880e4f

    subgraph "📊 Data & Storage"
        BIGQUERY[📊 BigQuery]
        GCS[☁️ Cloud Storage]
        PUBSUB[📨 Pub/Sub]
        BIGTABLE[📋 Bigtable]
    end

    subgraph "🤖 ML & AI"
        VERTEX_AI[🤖 Vertex AI]
        TENSORFLOW[🧠 TensorFlow]
        SCIKIT_LEARN[🔬 Scikit-learn]
        KUBEFLOW[⚙️ Kubeflow]
    end

    subgraph "🏗️ Infrastructure"
        GCE[💻 Compute Engine]
        GKE[🚢 Kubernetes Engine]
        CLOUD_FUNCTIONS[⚡ Cloud Functions]
        API_GATEWAY[🌐 API Gateway]
    end

    subgraph "🔧 DevOps & CI/CD"
        CLOUDBUILD[🏗️ Cloud Build]
        CONTAINER_REGISTRY[🐳 Container Registry]
        TERRAFORM[🏗️ Terraform]
        GITHUB_ACTIONS[⚙️ GitHub Actions]
    end

    subgraph "📈 Monitoring & Logging"
        CLOUD_MONITORING[📊 Cloud Monitoring]
        CLOUD_LOGGING[📝 Cloud Logging]
        PROMETHEUS[📊 Prometheus]
        GRAFANA[📊 Grafana]
    end

    BIGQUERY --> VERTEX_AI
    GCS --> VERTEX_AI
    PUBSUB --> GCE
    VERTEX_AI --> GKE
    GKE --> API_GATEWAY
    CLOUDBUILD --> GKE
    CLOUD_MONITORING --> GKE

    %% Apply styles
    class BIGQUERY,GCS,PUBSUB,BIGTABLE dataClass
    class VERTEX_AI,TENSORFLOW,SCIKIT_LEARN,KUBEFLOW mlClass
    class GCE,GKE,CLOUD_FUNCTIONS,API_GATEWAY infraClass
    class CLOUDBUILD,CONTAINER_REGISTRY,TERRAFORM,GITHUB_ACTIONS devopsClass
    class CLOUD_MONITORING,CLOUD_LOGGING,PROMETHEUS,GRAFANA monitoringClass
```

## Implementation Phases

```mermaid
gantt
    title POC-04 Implementation Timeline
    dateFormat  YYYY-MM-DD
    section Foundation
        GCP Setup             :done, 2024-11-01, 2024-11-05
        Data Pipeline         :done, 2024-11-06, 2024-11-15
        Feature Engineering   :done, 2024-11-16, 2024-11-20
    section ML Pipeline
        Model Development     :active, 2024-11-21, 2024-12-05
        Pipeline Orchestration:2024-12-06, 2024-12-15
        Model Training        :2024-12-16, 2024-12-25
    section Deployment
        Model Serving         :2024-12-26, 2024-12-30
        API Development       :2025-01-01, 2025-01-05
        UI Development        :2025-01-06, 2025-01-10
    section Production
        Monitoring Setup      :2025-01-11, 2025-01-15
        Testing & Validation  :2025-01-16, 2025-01-20
        Documentation         :2025-01-21, 2025-01-25
```

## Success Metrics Dashboard

```mermaid
graph TD
    %% Define styles
    classDef technicalClass fill:#e3f2fd,stroke:#1976d2,stroke-width:3px,color:#0d47a1
    classDef operationalClass fill:#f3e5f5,stroke:#7b1fa2,stroke-width:3px,color:#4a148c
    classDef businessClass fill:#e8f5e8,stroke:#388e3c,stroke-width:3px,color:#1b5e20
    classDef successClass fill:#fff3e0,stroke:#f57c00,stroke-width:3px,color:#e65100

    A[🎯 Success Metrics] --> B[💻 Technical Metrics]
    A --> C[⚙️ Operational Metrics]
    A --> D[💼 Business Metrics]

    B --> B1[⏱️ Pipeline Latency <5min]
    B --> B2[🎯 Model Accuracy >82%]
    B --> B3[⚡ API Response <100ms]

    C --> C1[📈 99.9% Uptime]
    C --> C2[🔄 Automated Retraining]
    C --> C3[💰 Cost Optimization]

    D --> D1[📊 Real-time Predictions]
    D --> D2[💡 Business Insights]
    D --> D3[👥 User Adoption]

    B1 --> E[🏆 Overall Success]
    B2 --> E
    B3 --> E
    C1 --> E
    C2 --> E
    C3 --> E
    D1 --> E
    D2 --> E
    D3 --> E

    %% Apply styles
    class A,B,B1,B2,B3 technicalClass
    class C,C1,C2,C3 operationalClass
    class D,D1,D2,D3 businessClass
    class E successClass
```
