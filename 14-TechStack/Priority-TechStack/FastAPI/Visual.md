# FastAPI - Visual Learning Guide

## 🎨 Visual Learning: Request Flows, Architecture, and Patterns

---

## 📊 Request Flow Diagrams

### Basic Request Flow

```mermaid
sequenceDiagram
    participant Client
    participant FastAPI
    participant Handler
    participant Model
    participant Response
    
    Client->>FastAPI: HTTP Request
    FastAPI->>FastAPI: Route Matching
    FastAPI->>FastAPI: Request Validation
    FastAPI->>Handler: Call Handler Function
    Handler->>Model: Process Request
    Model-->>Handler: Return Result
    Handler->>Response: Format Response
    Response-->>FastAPI: JSON Response
    FastAPI-->>Client: HTTP Response
```

### Request with Validation

```mermaid
flowchart TD
    A[HTTP Request] --> B[FastAPI Receives]
    B --> C{Validate Path?}
    C -->|Invalid| D[404 Not Found]
    C -->|Valid| E{Validate Query Params?}
    E -->|Invalid| F[422 Validation Error]
    E -->|Valid| G{Validate Body?}
    G -->|Invalid| F
    G -->|Valid| H[Call Handler]
    H --> I[Process Request]
    I --> J[Return Response]
    J --> K[200 OK]
    
    style D fill:#ea4335
    style F fill:#ea4335
    style K fill:#34a853
```

### Request with Dependencies

```mermaid
graph TB
    A[Request] --> B[FastAPI]
    B --> C[Resolve Dependencies]
    C --> D[Dependency 1: get_db]
    C --> E[Dependency 2: get_model]
    C --> F[Dependency 3: verify_token]
    
    D --> G[Handler Function]
    E --> G
    F --> G
    
    G --> H[Process]
    H --> I[Response]
    
    style C fill:#4285f4
    style G fill:#34a853
```

---

## 🏗️ Architecture Patterns

### Simple API Architecture

```mermaid
graph LR
    A[Client] --> B[FastAPI App]
    B --> C[Route Handler]
    C --> D[Business Logic]
    D --> E[Response]
    E --> A
    
    style B fill:#4285f4
    style C fill:#34a853
```

### API with Database

```mermaid
graph TB
    A[Client] --> B[FastAPI]
    B --> C[Route Handler]
    C --> D[Dependency: get_db]
    D --> E[Database Session]
    C --> F[Business Logic]
    F --> E
    E --> G[(Database)]
    G --> E
    E --> H[Response]
    H --> A
    
    style B fill:#4285f4
    style E fill:#ea4335
    style G fill:#fbbc04
```

### API with Caching

```mermaid
graph TB
    A[Request] --> B[FastAPI]
    B --> C[Route Handler]
    C --> D{Cache Hit?}
    D -->|Yes| E[Return Cached]
    D -->|No| F[Process Request]
    F --> G[Model/Service]
    G --> H[Store in Cache]
    H --> I[Return Response]
    E --> J[Response]
    I --> J
    J --> A
    
    style D fill:#4285f4
    style G fill:#34a853
```

### Microservices Architecture
### Event-Driven Pipeline

```mermaid
graph LR
    Producer[FastAPI Producer] --> Queue[Kafka / PubSub Topic]
    Queue --> Worker1[Background Worker 1]
    Queue --> Worker2[Worker 2]
    Worker1 --> DB[(OLTP DB)]
    Worker2 --> FeatureStore[(Feature Store)]
    DB --> Analytics[Analytics / Dashboard]
    
    style Queue fill:#3b82f6
    style Worker1 fill:#22c55e
    style Worker2 fill:#22c55e
```

```mermaid
graph TB
    A[Client] --> B[API Gateway]
    B --> C[FastAPI Service 1<br/>User Service]
    B --> D[FastAPI Service 2<br/>ML Service]
    B --> E[FastAPI Service 3<br/>Data Service]
    
    C --> F[(User DB)]
    D --> G[ML Model]
    E --> H[(Data DB)]
    
    style B fill:#4285f4
    style C fill:#34a853
    style D fill:#34a853
    style E fill:#34a853
```

---

## 🔄 Async Request Flow

### Async vs Sync

```mermaid
graph LR
    subgraph "Sync (Blocking)"
        A1[Request] --> B1[Handler]
        B1 --> C1[Wait for DB]
        C1 --> D1[Wait for API]
        D1 --> E1[Response]
    end
    
    subgraph "Async (Non-blocking)"
        A2[Request] --> B2[Handler]
        B2 --> C2[DB Call]
        B2 --> D2[API Call]
        C2 --> E2[Response]
        D2 --> E2
    end
    
    style C1 fill:#ea4335
    style D1 fill:#ea4335
    style C2 fill:#34a853
    style D2 fill:#34a853
```

### Async Execution Flow

```mermaid
sequenceDiagram
    participant Client
    participant FastAPI
    participant EventLoop
    participant DB
    participant API
    
    Client->>FastAPI: Request
    FastAPI->>EventLoop: Schedule Handler
    EventLoop->>DB: Async DB Call
    EventLoop->>API: Async API Call
    DB-->>EventLoop: Result 1
    API-->>EventLoop: Result 2
    EventLoop->>FastAPI: Combined Result
    FastAPI-->>Client: Response
```

---

## 🎯 ML API Architecture (Your POCs)
### Event Streaming API (WebSocket)
```mermaid
sequenceDiagram
    participant Client
    participant FastAPI_WS as FastAPI WebSocket
    participant Broker as Event Broker
    Client->>FastAPI_WS: Connect WebSocket
    FastAPI_WS-->>Client: ACK + Token check
    loop Streaming Events
        Client->>FastAPI_WS: Send message
        FastAPI_WS->>Broker: Publish event
        Broker-->>FastAPI_WS: Broadcast update
        FastAPI_WS-->>Client: Push notification
    end
```

### Module 04: ML Pipeline API

```mermaid
graph TB
    A[Client] --> B[FastAPI App]
    B --> C[/predict endpoint]
    C --> D[Validate Request]
    D --> E[Load Model]
    E --> F[Preprocess Features]
    F --> G[Model Prediction]
    G --> H[Post-process]
    H --> I[Format Response]
    I --> J[Log Prediction]
    J --> K[Return JSON]
    K --> A
    
    style B fill:#4285f4
    style G fill:#34a853
    style J fill:#fbbc04
```

### Module 05: RAG API

```mermaid
graph TB
    A[Client] --> B[FastAPI App]
    B --> C[/query endpoint]
    C --> D[Validate Query]
    D --> E[Embed Query]
    E --> F[Vector Search]
    F --> G[Retrieve Context]
    G --> H[LLM Generation]
    H --> I[Format Response]
    I --> J[Return Answer]
    J --> A
    
    style B fill:#4285f4
    style F fill:#34a853
    style H fill:#ea4335
```

---

## 🔐 Security Flow
### Multi-Tenant Routing
```mermaid
flowchart LR
    Req[Incoming Request] --> Extract[Read JWT claims / headers]
    Extract --> Route{Tenant Known?}
    Route -->|Yes| TenantCfg[Load tenant config]
    Route -->|No| Reject[403 Forbidden]
    TenantCfg --> DBPool[Select DB/Schema]
    TenantCfg --> FeatureFlags[Load Feature Flags]
    DBPool --> Handler
    FeatureFlags --> Handler
    Handler --> Response
    
    style Route fill:#3b82f6
    style Reject fill:#f87171
```

### Authentication Flow

```mermaid
sequenceDiagram
    participant Client
    participant FastAPI
    participant Auth
    participant Handler
    
    Client->>FastAPI: Request with Token
    FastAPI->>Auth: Verify Token
    Auth->>Auth: Validate Signature
    Auth->>Auth: Check Expiry
    Auth-->>FastAPI: Token Valid/Invalid
    
    alt Token Valid
        FastAPI->>Handler: Execute Handler
        Handler-->>FastAPI: Response
        FastAPI-->>Client: 200 OK
    else Token Invalid
        FastAPI-->>Client: 401 Unauthorized
    end
```

### CORS Flow

```mermaid
flowchart TD
    A[Browser Request] --> B{Preflight?}
    B -->|Yes| C[OPTIONS Request]
    B -->|No| D[Actual Request]
    
    C --> E[FastAPI CORS Middleware]
    E --> F{Origin Allowed?}
    F -->|Yes| G[Return CORS Headers]
    F -->|No| H[Block Request]
    
    D --> E
    E --> I[Add CORS Headers]
    I --> J[Process Request]
    J --> K[Response with CORS]
    
    style E fill:#4285f4
    style G fill:#34a853
    style H fill:#ea4335
```

---

## 📊 Error Handling Flow

### Error Handling Architecture

```mermaid
flowchart TD
    A[Request] --> B[Handler]
    B --> C{Error Occurs?}
    C -->|No| D[Success Response]
    C -->|Yes| E{Error Type?}
    
    E -->|ValidationError| F[422 Validation Error]
    E -->|NotFoundError| G[404 Not Found]
    E -->|AuthError| H[401 Unauthorized]
    E -->|ServerError| I[500 Internal Error]
    
    F --> J[Error Handler]
    G --> J
    H --> J
    I --> J
    
    J --> K[Format Error Response]
    K --> L[Return to Client]
    D --> L
    
    style C fill:#4285f4
    style J fill:#ea4335
```

---

## 🚀 Deployment Architecture

### Docker Deployment

```mermaid
graph TB
    A[FastAPI Code] --> B[Dockerfile]
    B --> C[Docker Image]
    C --> D[Container Registry]
    D --> E[Cloud Run/K8s]
    E --> F[Load Balancer]
    F --> G[FastAPI Instances]
    G --> H[Traffic Distribution]
    
    style C fill:#4285f4
    style E fill:#34a853
    style G fill:#fbbc04
```

### Scaling Architecture
### Observability Stack
```mermaid
graph TD
    FastAPI --> Logs[Structured Logs]
    FastAPI --> Metrics[Prometheus Metrics]
    FastAPI --> Traces[OpenTelemetry Traces]
    Logs --> Stackdriver[Cloud Logging / ELK]
    Metrics --> Grafana[Grafana Dashboards]
    Traces --> Jaeger[Jaeger/Tempo]
    Grafana --> Alerts[PagerDuty / OpsGenie]
    Stackdriver --> Alerts
```

```mermaid
graph LR
    A[Load Balancer] --> B[Instance 1]
    A --> C[Instance 2]
    A --> D[Instance 3]
    A --> E[Instance N]
    
    B --> F[(Shared DB)]
    C --> F
    D --> F
    E --> F
    
    style A fill:#4285f4
    style F fill:#ea4335
```

---

## 🔄 Background Tasks Flow

### Background Task Execution

```mermaid
sequenceDiagram
    participant Client
    participant FastAPI
    participant Handler
    participant Background
    participant Task
    
    Client->>FastAPI: Request
    FastAPI->>Handler: Process Request
    Handler->>Background: Add Task
    Handler-->>FastAPI: Immediate Response
    FastAPI-->>Client: 200 OK
    
    Background->>Task: Execute Task
    Task->>Task: Process (async)
    Task-->>Background: Complete
```

---

## 📈 Performance Optimization

### Caching Strategy

```mermaid
mindmap
  root((FastAPI Performance))
    Caching
      Response Cache
        Redis
        In-Memory
      Query Cache
        Database
        API Calls
    Async
      Non-blocking
      Concurrent
    Database
      Connection Pooling
      Query Optimization
    Load Balancing
      Multiple Instances
      Health Checks
```

---

## 🎯 Key Visual Takeaways

1. **Request Flow**: Client → FastAPI → Handler → Response
2. **Validation**: Automatic with Pydantic
3. **Dependencies**: Reusable, injectable logic
4. **Async**: Non-blocking, concurrent execution
5. **Security**: Authentication, CORS, validation
6. **Deployment**: Docker → Cloud → Scaling

---

## 📚 Next Steps

1. ✅ Review these diagrams
2. 🏗️ Draw them yourself
3. 💬 Use in interviews
4. 🔗 Connect to your POCs

---

**Visual learning helps!** Use these diagrams to explain FastAPI architecture in interviews.

