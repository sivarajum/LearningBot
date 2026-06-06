# Node.js Visual Architecture Guide

## Node.js Architecture Overview

```mermaid
graph TB
    A[JavaScript Code] --> B[V8 Engine]
    B --> C[Node.js Bindings]
    C --> D[libuv]
    D --> E[Event Loop]
    D --> F[Thread Pool]
    D --> G[Async I/O]

    E --> H[Timers]
    E --> I[Pending Callbacks]
    E --> J[Idle/Prepare]
    E --> K[Poll]
    E --> L[Check]
    E --> M[Close Callbacks]

    F --> N[File System]
    F --> O[DNS Lookup]
    F --> P[Crypto Operations]
    F --> Q[Zlib Compression]

    G --> R[Network I/O]
    G --> S[Database Queries]
    G --> T[External APIs]

    style B fill:#e3f2fd
    style D fill:#f3e5f5
    style E fill:#e8f5e8
    style F fill:#fff3e0
    style G fill:#fce4ec
```

## Event Loop Phases

```mermaid
stateDiagram-v2
    [*] --> Timers
    Timers --> PendingCallbacks: execute expired timers
    PendingCallbacks --> IdlePrepare: execute I/O callbacks
    IdlePrepare --> Poll: internal operations
    Poll --> Check: poll for I/O events
    Check --> CloseCallbacks: execute setImmediate
    CloseCallbacks --> Timers: execute close callbacks

    note right of Timers
        - setTimeout()
        - setInterval()
    end note

    note right of PendingCallbacks
        - TCP errors
        - unresolved DNS lookups
    end note

    note right of Poll
        - Most I/O operations
        - Incoming connections
        - Data reads
    end note

    note right of Check
        - setImmediate() callbacks
        - process.nextTick()
    end note
```

## Express.js Request-Response Flow

```mermaid
sequenceDiagram
    participant Client
    participant Express
    participant Middleware1
    participant Middleware2
    participant RouteHandler
    participant Database
    participant Response

    Client->>Express: HTTP Request
    Express->>Middleware1: Process Request
    Middleware1->>Middleware2: Next()
    Middleware2->>RouteHandler: Next()
    RouteHandler->>Database: Query Data
    Database-->>RouteHandler: Return Data
    RouteHandler-->>Response: Format Response
    Response-->>Middleware2: Response Processing
    Middleware2-->>Middleware1: Response Processing
    Middleware1-->>Express: Final Response
    Express-->>Client: HTTP Response
```

## Middleware Stack Architecture

```mermaid
graph LR
    A[Client Request] --> B[CORS Middleware]
    B --> C[Body Parser<br/>express.json()]
    C --> D[Cookie Parser]
    D --> E[Session Middleware]
    E --> F[Authentication<br/>JWT Verify]
    F --> G[Authorization<br/>Role Check]
    G --> H[Logging<br/>Morgan]
    H --> I[Route Handler]
    I --> J[Error Handler]
    J --> K[Response<br/>to Client]

    style B fill:#e3f2fd
    style E fill:#f3e5f5
    style G fill:#e8f5e8
    style I fill:#fff3e0
    style J fill:#ffebee
```

## REST API Architecture

```mermaid
classDiagram
    class ExpressApp {
        +use(middleware)
        +get(path, handler)
        +post(path, handler)
        +put(path, handler)
        +delete(path, handler)
        +listen(port, callback)
    }

    class Router {
        +use(middleware)
        +get(path, handler)
        +post(path, handler)
        +route(path)
        +param(name, callback)
    }

    class Middleware {
        +function(req, res, next)
        +error handling
        +authentication
        +validation
    }

    class RouteHandler {
        +function(req, res)
        +req.params
        +req.query
        +req.body
        +res.json()
        +res.status()
    }

    ExpressApp *-- Router
    ExpressApp *-- Middleware
    Router *-- RouteHandler
    Router *-- Middleware
```

## Database Integration Patterns

```mermaid
graph TB
    A[Express Route] --> B{Database Type}
    B -->|MongoDB| C[Mongoose ODM]
    B -->|PostgreSQL| D[Sequelize ORM]
    B -->|MySQL| E[TypeORM]
    B -->|Redis| F[Redis Client]

    C --> G[Schema Definition]
    D --> H[Model Definition]
    E --> I[Entity Definition]
    F --> J[Key-Value Operations]

    G --> K[CRUD Operations]
    H --> K
    I --> K
    J --> L[Caching Operations]

    K --> M[Response Formatting]
    L --> M

    style C fill:#e3f2fd
    style D fill:#f3e5f5
    style E fill:#e8f5e8
    style F fill:#fff3e0
```

## Authentication Flow

```mermaid
sequenceDiagram
    participant Client
    participant Express
    participant AuthMiddleware
    participant UserModel
    participant JWT
    participant Database

    Client->>Express: POST /api/login
    Express->>AuthMiddleware: Validate Input
    AuthMiddleware->>UserModel: Find User
    UserModel->>Database: Query User
    Database-->>UserModel: User Data
    UserModel-->>AuthMiddleware: Verify Password
    AuthMiddleware->>JWT: Generate Token
    JWT-->>Express: Signed Token
    Express-->>Client: Token + User Data

    Client->>Express: GET /api/protected (with token)
    Express->>AuthMiddleware: Verify Token
    AuthMiddleware->>JWT: Decode Token
    JWT-->>AuthMiddleware: User Claims
    AuthMiddleware-->>Express: Authenticated User
    Express-->>Client: Protected Resource
```

## File Upload Architecture

```mermaid
graph TD
    A[Client] --> B[Multipart Form Data]
    B --> C[Multer Middleware]
    C --> D[Storage Engine]
    D --> E{Disk Storage}
    D --> F[Cloud Storage<br/>AWS S3]

    E --> G[Local File System]
    F --> H[Cloud Bucket]

    C --> I[File Validation]
    I --> J{Valid?}
    J -->|Yes| K[Process File]
    J -->|No| L[Return Error]

    K --> M[Database Record]
    M --> N[Response with<br/>File Metadata]

    style C fill:#e3f2fd
    style D fill:#f3e5f5
    style I fill:#e8f5e8
    style K fill:#fff3e0
```

## Real-time Communication with Socket.io

```mermaid
graph TB
    A[Client Browser] --> B[WebSocket Connection]
    B --> C[Socket.io Server]
    C --> D[Express App]

    C --> E[Connection Event]
    E --> F[Room Management]
    E --> G[Message Handling]

    F --> H[Join Room]
    F --> I[Leave Room]
    F --> J[Broadcast to Room]

    G --> K[Private Messages]
    G --> L[Broadcast Messages]
    G --> M[Typing Indicators]

    D --> N[HTTP API]
    N --> O[Send Notifications]
    O --> C

    style B fill:#e3f2fd
    style C fill:#f3e5f5
    style F fill:#e8f5e8
    style G fill:#fff3e0
```

## Error Handling Flow

```mermaid
flowchart TD
    A[Error Occurs] --> B{Error Type}
    B --> C[Synchronous Error]
    B --> D[Asynchronous Error]
    B --> E[Promise Rejection]
    B --> F[Unhandled Exception]

    C --> G[Express Error Handler]
    D --> H[Callback Error]
    E --> I[catch() Block]
    F --> J[process.on('uncaughtException')]

    G --> K[Error Response]
    H --> L[Callback Function]
    I --> M[Error Handling Logic]
    J --> N[Graceful Shutdown]

    K --> O[Client Response]
    L --> O
    M --> O
    N --> P[Process Exit]

    style G fill:#e3f2fd
    style H fill:#f3e5f5
    style I fill:#e8f5e8
    style J fill:#ffebee
```

## Testing Pyramid

```mermaid
graph TD
    A[Testing Strategy] --> B[Unit Tests]
    A --> C[Integration Tests]
    A --> D[End-to-End Tests]

    B --> B1[Function Tests]
    B --> B2[Class Tests]
    B --> B3[Module Tests]

    C --> C1[API Endpoint Tests]
    C --> C2[Database Integration]
    C --> C3[Middleware Tests]

    D --> D1[Full Application Tests]
    D --> D2[User Journey Tests]
    D --> D3[Performance Tests]

    E[Jest] --> B
    E --> C

    F[Supertest] --> C
    F --> D

    G[Sinon] --> B
    G --> C

    H[Selenium<br/>Puppeteer] --> D

    style B fill:#e3f2fd
    style C fill:#f3e5f5
    style D fill:#e8f5e8
    style E fill:#fff3e0
    style F fill:#fce4ec
```

## Deployment Architecture

```mermaid
graph TB
    A[Load Balancer<br/>nginx/haproxy] --> B[PM2 Cluster]
    A --> C[PM2 Cluster]
    A --> D[PM2 Cluster]

    B --> E[Node.js App]
    C --> F[Node.js App]
    D --> G[Node.js App]

    E --> H[(Database)]
    F --> H
    G --> H

    E --> I[(Redis Cache)]
    F --> I
    G --> I

    J[Monitoring] --> K[PM2 Monitoring]
    J --> L[Application Metrics]
    J --> M[Error Tracking]

    N[CI/CD] --> O[GitHub Actions]
    N --> P[GitLab CI]
    N --> Q[Jenkins]

    R[Docker Registry] --> S[Docker Images]
    S --> T[Kubernetes]
    T --> U[Pods]
    U --> V[Containers]

    style A fill:#e3f2fd
    style B fill:#f3e5f5
    style E fill:#e8f5e8
    style J fill:#fff3e0
    style N fill:#fce4ec
    style T fill:#e0f2f1
```

## Performance Optimization

```mermaid
graph TD
    A[Performance Factors] --> B[Code Optimization]
    A --> C[Memory Management]
    A --> D[Caching Strategies]
    A --> E[Database Optimization]

    B --> B1[Algorithm Efficiency]
    B --> B2[Async/Await Usage]
    B --> B3[Stream Processing]

    C --> C1[Garbage Collection]
    C --> C2[Memory Leaks Prevention]
    C --> C3[Object Pooling]

    D --> D1[Response Caching]
    D --> D2[Database Query Caching]
    D --> D3[Static Asset Caching]

    E --> E1[Connection Pooling]
    E --> E2[Query Optimization]
    E --> E3[Indexing Strategy]

    F[Monitoring] --> F1[Response Times]
    F --> F2[Memory Usage]
    F --> F3[CPU Utilization]
    F --> F4[Error Rates]

    style B fill:#e3f2fd
    style C fill:#f3e5f5
    style D fill:#e8f5e8
    style E fill:#fff3e0
    style F fill:#fce4ec
```

## Microservices Architecture

```mermaid
graph TB
    A[API Gateway] --> B[Auth Service]
    A --> C[User Service]
    A --> D[Product Service]
    A --> E[Order Service]
    A --> F[Payment Service]

    B --> G[(User DB)]
    C --> G
    D --> H[(Product DB)]
    E --> I[(Order DB)]
    F --> J[(Payment DB)]

    B --> K[Redis Cache]
    D --> K
    E --> K

    L[Service Discovery] --> B
    L --> C
    L --> D
    L --> E
    L --> F

    M[Message Queue] --> E
    M --> F
    E --> N[Email Service]
    F --> O[SMS Service]

    style A fill:#e3f2fd
    style B fill:#f3e5f5
    style L fill:#e8f5e8
    style M fill:#fff3e0
```

## Security Layers

```mermaid
graph LR
    A[Client Request] --> B[HTTPS/TLS]
    B --> C[Rate Limiting]
    C --> D[Input Validation]
    D --> E[CORS Policy]
    E --> F[Authentication]
    F --> G[Authorization]
    G --> H[Data Sanitization]
    H --> I[Output Encoding]
    I --> J[Security Headers]
    J --> K[Application Logic]

    style B fill:#e3f2fd
    style D fill:#f3e5f5
    style F fill:#e8f5e8
    style H fill:#fff3e0
    style J fill:#fce4ec
```

## Package Management Flow

```mermaid
graph TD
    A[package.json] --> B[npm install]
    B --> C[Dependency Resolution]
    C --> D[Download Packages]
    D --> E[node_modules/]
    E --> F[package-lock.json]

    G[npm update] --> H[Check Updates]
    H --> I[Update Dependencies]
    I --> J[Update package-lock.json]

    K[npm audit] --> L[Vulnerability Check]
    L --> M[Security Report]

    N[npm run script] --> O[Execute Command]
    O --> P[Build/Start App]

    style B fill:#e3f2fd
    style C fill:#f3e5f5
    style G fill:#e8f5e8
    style K fill:#fff3e0
    style N fill:#fce4ec
```

These diagrams provide a comprehensive visual representation of Node.js architecture, from the core event loop mechanics to complex deployment patterns and microservices architectures. Understanding these visual flows is crucial for building scalable and maintainable Node.js applications.
