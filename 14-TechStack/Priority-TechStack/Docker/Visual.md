# Docker - Visual Learning Guide

## 🎨 Visual Learning: Container Architecture, Build Process, Deployment

---

## 📊 Docker Architecture

### High-Level Architecture

```mermaid
graph TB
    subgraph Client
        CLI[Docker CLI / API]
    end
    subgraph Host
        Daemon[Docker Daemon]
        Images
        Containers
        Volumes
        Networks
    end
    CLI --> Daemon
    Daemon --> Images
    Daemon --> Containers
    Daemon --> Volumes
    Daemon --> Networks
    style Daemon fill:#3b82f6
    style Containers fill:#22c55e
    style Images fill:#facc15
```

### Container vs VM

```mermaid
graph TB
    subgraph "Virtual Machine"
        A[App] --> B[Guest OS]
        B --> C[Hypervisor]
        C --> D[Host OS]
        D --> E[Hardware]
    end
    
    subgraph "Docker Container"
        F[App] --> G[Container Runtime]
        G --> H[Host OS]
        H --> I[Hardware]
    end
    
    style C fill:#ea4335
    style G fill:#34a853
```

---

## 🔨 Build Process & Pipelines

### Docker Build Flow

```mermaid
sequenceDiagram
    participant Developer
    participant Dockerfile
    participant Docker
    participant Image
    participant Registry
    
    Developer->>Dockerfile: Write Dockerfile
    Developer->>Docker: docker build
    Docker->>Dockerfile: Read Instructions
    Docker->>Docker: Create Layers
    Docker->>Image: Build Image
    Image->>Registry: Push (optional)
    Registry-->>Developer: Image Available
```

### Image Layers

```mermaid
graph TB
    Base[Base Image<br/>python:3.11-slim] --> Layer1[Layer 1<br/>Install OS deps]
    Layer1 --> Layer2[Layer 2<br/>Copy requirements.txt]
    Layer2 --> Layer3[Layer 3<br/>pip install]
    Layer3 --> Layer4[Layer 4<br/>Copy app code]
    Layer4 --> Final[Final Image]
    style Base fill:#22d3ee
    style Final fill:#22c55e
```

---

## 🚀 Container Lifecycle & Promotion

### Container States

```mermaid
stateDiagram-v2
    [*] --> Created: docker create
    Created --> Running: docker start
    Running --> Paused: docker pause
    Paused --> Running: docker unpause
    Running --> Stopped: docker stop
    Stopped --> Running: docker start
    Stopped --> [*]: docker rm
    Running --> [*]: docker rm -f
```

---

## 🔄 Docker Compose & Orchestrators

### Compose vs K8s (High-Level)
```mermaid
graph LR
    subgraph Compose (Local)
        Yaml[docker-compose.yml]
        Yaml --> ServiceA
        Yaml --> ServiceB
        ServiceA --> LocalNet
        ServiceB --> LocalNet
    end
    subgraph Kubernetes (Prod)
        Deploy[Deployment]
        Service[Service]
        Ingress[Ingress]
    end
    ServiceA -.container image.-> Deploy
    Deploy --> Service --> Ingress
```

### Multi-Container Architecture

```mermaid
graph TB
    Compose[docker-compose.yml] --> API[api]
    Compose --> DB[postgres]
    Compose --> Cache[redis]
    API --> SharedNet[Overlay Network]
    DB --> SharedNet
    Cache --> SharedNet
    API --> AppVol[(app_data)]
    DB --> DBVol[(db_data)]
    style SharedNet fill:#3b82f6
    style AppVol fill:#facc15
    style DBVol fill:#facc15
```

---

## 🎯 Key Visual Takeaways

1. **Image = Template**
2. **Container = Running Instance**
3. **Layers = Efficient Storage**
4. **Compose = Multi-Container**
5. **Volumes = Persistent Data**

---

## 📚 Next Steps

1. ✅ Review these diagrams
2. 🏗️ Draw them yourself
3. 💬 Use in interviews
4. 🔗 Connect to your POCs

---

**Visual learning helps!** Use these to explain Docker in interviews.

