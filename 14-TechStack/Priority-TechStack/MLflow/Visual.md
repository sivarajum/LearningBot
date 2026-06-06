# MLflow - Visual Learning Guide

## 🎨 Visual Learning: Experiment Tracking, Model Registry, Lifecycle

---

## 📊 MLflow Architecture

### High-Level Architecture

```mermaid
graph TB
    subgraph "MLflow Components"
        A[Tracking Server<br/>Experiments & Runs]
        B[Model Registry<br/>Version Control]
        C[Artifact Store<br/>Models & Files]
        D[UI Dashboard<br/>Visualization]
    end
    
    subgraph "Training"
        E[Training Script]
        F[MLflow Client]
    end
    
    subgraph "Deployment"
        G[Model Serving]
        H[Production]
    end
    
    E --> F
    F --> A
    F --> C
    A --> D
    A --> B
    B --> G
    G --> H
    
    style A fill:#4285f4
    style B fill:#34a853
    style C fill:#fbbc04
    style D fill:#ea4335
```

---

## 🔬 Experiment Tracking Flow

### Run Lifecycle

```mermaid
sequenceDiagram
    participant Script
    participant MLflow
    participant Tracking
    participant Artifacts
    participant UI
    
    Script->>MLflow: Start Run
    MLflow->>Tracking: Create Run Record
    
    Script->>MLflow: Log Parameters
    MLflow->>Tracking: Store Parameters
    
    Script->>MLflow: Log Metrics
    MLflow->>Tracking: Store Metrics
    
    Script->>MLflow: Log Artifacts
    MLflow->>Artifacts: Store Files
    
    Script->>MLflow: Log Model
    MLflow->>Artifacts: Store Model
    
    Script->>MLflow: End Run
    MLflow->>Tracking: Mark Complete
    
    Tracking->>UI: Update Dashboard
```

### Experiment Comparison

```mermaid
graph TB
    A[Experiment: Churn Prediction] --> B[Run 1: RF, lr=0.01]
    A --> C[Run 2: RF, lr=0.05]
    A --> D[Run 3: XGB, lr=0.01]
    A --> E[Run 4: XGB, lr=0.05]
    
    B --> F[Accuracy: 0.92]
    C --> G[Accuracy: 0.94]
    D --> H[Accuracy: 0.95]
    E --> I[Accuracy: 0.93]
    
    F --> J[Compare Runs]
    G --> J
    H --> J
    I --> J
    
    J --> K[Best: Run 3]
    
    style K fill:#34a853
```

---

## 📦 Model Registry Flow

### Model Lifecycle

```mermaid
flowchart TD
    A[Training Run] --> B[Log Model]
    B --> C[Register Model]
    C --> D[Version 1: None]
    
    D --> E{Evaluate}
    E -->|Good| F[Stage: Staging]
    E -->|Bad| G[Stage: Archived]
    
    F --> H[Testing]
    H --> I{Production Ready?}
    I -->|Yes| J[Stage: Production]
    I -->|No| K[New Version]
    
    K --> L[Version 2: Staging]
    L --> H
    
    J --> M[Deploy to Production]
    M --> N[Monitor]
    N --> O{Drift Detected?}
    O -->|Yes| K
    O -->|No| N
    
    style J fill:#34a853
    style G fill:#ea4335
```

### Model Versioning

```mermaid
graph LR
    A[Model: ChurnModel] --> B[v1.0: None]
    A --> C[v2.0: Staging]
    A --> D[v3.0: Production]
    A --> E[v4.0: Staging]
    
    B --> F[Archived]
    C --> G[Testing]
    D --> H[Live]
    E --> I[Testing]
    
    style D fill:#34a853
    style H fill:#34a853
```

---

## 🔄 ML Lifecycle with MLflow

### Complete Lifecycle

```mermaid
graph TB
    A[Data Preparation] --> B[Training]
    B --> C[MLflow Tracking]
    C --> D[Log Parameters]
    C --> E[Log Metrics]
    C --> F[Log Model]
    
    F --> G[Model Evaluation]
    G --> H{Good Enough?}
    H -->|No| B
    H -->|Yes| I[Register Model]
    
    I --> J[Model Registry]
    J --> K[Version Control]
    K --> L[Stage Management]
    
    L --> M[Deploy to Staging]
    M --> N[Testing]
    N --> O{Pass Tests?}
    O -->|No| P[Create New Version]
    O -->|Yes| Q[Deploy to Production]
    
    P --> B
    Q --> R[Monitor]
    R --> S{Drift?}
    S -->|Yes| P
    S -->|No| R
    
    style C fill:#4285f4
    style J fill:#34a853
    style Q fill:#34a853
```

---

## 📊 Metric Tracking Over Time

### Training Metrics Visualization

```mermaid
graph LR
    A[Epoch 1] --> B[Epoch 2]
    B --> C[Epoch 3]
    C --> D[Epoch N]
    
    A --> E[Log: train_loss=0.5]
    B --> F[Log: train_loss=0.3]
    C --> G[Log: train_loss=0.2]
    D --> H[Log: train_loss=0.1]
    
    E --> I[MLflow UI]
    F --> I
    G --> I
    H --> I
    
    I --> J[Training Curve]
    
    style I fill:#4285f4
    style J fill:#34a853
```

---

## 🎯 Model Comparison Flow

### Comparing Multiple Runs

```mermaid
flowchart TD
    A[Multiple Training Runs] --> B[Run 1: RF, lr=0.01]
    A --> C[Run 2: RF, lr=0.05]
    A --> D[Run 3: XGB, lr=0.01]
    
    B --> E[Accuracy: 0.92]
    C --> F[Accuracy: 0.94]
    D --> G[Accuracy: 0.95]
    
    E --> H[MLflow Compare]
    F --> H
    G --> H
    
    H --> I[Best Model: Run 3]
    I --> J[Register Best Model]
    
    style I fill:#34a853
    style J fill:#4285f4
```

---

## 🚀 Deployment Flow

### Model Serving Architecture

```mermaid
graph TB
    A[Model Registry] --> B[Select Model Version]
    B --> C[Load Model]
    C --> D[Model Server]
    
    E[Client Request] --> D
    D --> F[Preprocess]
    F --> G[Model Prediction]
    G --> H[Postprocess]
    H --> I[Response]
    I --> E
    
    D --> J[Log Prediction]
    J --> K[MLflow Tracking]
    
    style D fill:#4285f4
    style G fill:#34a853
    style K fill:#fbbc04
```

---

## 🔄 Integration with Vertex AI (Your POC)

### MLflow + Vertex AI Flow

```mermaid
graph TB
    A[Training Script] --> B[MLflow Tracking]
    B --> C[Log Metrics/Params]
    B --> D[Log Model]
    
    D --> E[Model Registry]
    E --> F[Best Model]
    
    F --> G[Export to GCS]
    G --> H[Vertex AI Model]
    H --> I[Vertex AI Endpoint]
    
    I --> J[Production Serving]
    
    style B fill:#4285f4
    style E fill:#34a853
    style I fill:#ea4335
```

---

## 📈 Experiment Organization

### Experiment Structure

```mermaid
mindmap
  root((MLflow Experiments))
    Experiment 1
      Run 1
        Parameters
        Metrics
        Model
      Run 2
        Parameters
        Metrics
        Model
    Experiment 2
      Run 1
      Run 2
    Model Registry
      Model A
        Version 1
        Version 2
      Model B
        Version 1
```

---

## 🎯 Key Visual Takeaways

1. **Tracking**: Log experiments, compare runs
2. **Registry**: Version models, manage lifecycle
3. **Artifacts**: Store models, plots, files
4. **UI**: Visualize and compare
5. **Deployment**: Serve models from registry

---

## 📚 Next Steps

1. ✅ Review these diagrams
2. 🏗️ Draw them yourself
3. 💬 Use in interviews
4. 🔗 Connect to your POCs

---

**Visual learning helps!** Use these to explain MLflow in interviews.

