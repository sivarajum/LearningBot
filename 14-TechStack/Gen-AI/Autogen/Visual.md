# AutoGen: Visual Guide & Architecture Diagrams

## 1. AutoGen Architecture Overview

```mermaid
graph TD
    AG["🤖 AutoGen Framework<br/>Microsoft Multi-Agent"]
    AG --> CHAT["💬 AgentChat<br/>High-level multi-agent"]
    AG --> CORE["⚙️ Core<br/>Event-driven runtime"]
    AG --> EXT["🔌 Extensions<br/>Integrations"]

    CHAT --> RR["🔄 RoundRobinGroupChat"]
    CHAT --> SEL["🎯 SelectorGroupChat"]
    CHAT --> SWM["🐝 Swarm"]
    CHAT --> MAG["👤 MagenticOne"]

    CORE --> RT["SingleThreadedRuntime"]
    CORE --> GRT["GrpcWorkerRuntime"]
    CORE --> MSG["Message Protocol"]
    CORE --> SUB["Topic Subscriptions"]

    EXT --> OAI["OpenAI / Anthropic"]
    EXT --> MCP["MCP Servers"]
    EXT --> DOCK["Docker Executor"]
    EXT --> GRPC["gRPC Distributed"]
    EXT --> AZ["Azure AI"]

    style AG fill:#0078D4,color:#fff,stroke:#005A9E
    style CHAT fill:#00B4D8,color:#fff,stroke:#0096C7
    style CORE fill:#E63946,color:#fff,stroke:#D62828
    style EXT fill:#FFB703,color:#000,stroke:#FB8500
    style RR fill:#48CAE4,color:#fff
    style SEL fill:#48CAE4,color:#fff
    style SWM fill:#48CAE4,color:#fff
    style MAG fill:#48CAE4,color:#fff
    style RT fill:#FF6B6B,color:#fff
    style GRT fill:#FF6B6B,color:#fff
    style MSG fill:#FF6B6B,color:#fff
    style SUB fill:#FF6B6B,color:#fff
    style OAI fill:#FFCA3A,color:#000
    style MCP fill:#FFCA3A,color:#000
    style DOCK fill:#FFCA3A,color:#000
    style GRPC fill:#FFCA3A,color:#000
    style AZ fill:#FFCA3A,color:#000
```

## 2. Multi-Agent Conversation Patterns

```mermaid
flowchart TB
    subgraph RR["🔄 Round Robin — Fixed Turn Order"]
        direction LR
        RR_A["🧑‍💻 Coder"] -->|"turn 1"| RR_B["🔍 Reviewer"]
        RR_B -->|"turn 2"| RR_C["✅ Approver"]
        RR_C -->|"turn 3"| RR_A
    end

    subgraph SEL["🎯 Selector — LLM Routes Dynamically"]
        SEL_LLM["🧠 LLM Router"]
        SEL_LLM -->|"needs data"| SEL_A["📊 Analyst"]
        SEL_LLM -->|"needs code"| SEL_B["💻 Developer"]
        SEL_LLM -->|"needs review"| SEL_C["🔒 Security"]
    end

    subgraph SW["🐝 Swarm — Dynamic Handoffs"]
        SW_A["🎫 Triage<br/>Agent"]
        SW_A -->|"billing issue"| SW_B["💳 Billing<br/>Agent"]
        SW_A -->|"tech issue"| SW_C["🔧 Tech<br/>Agent"]
        SW_B -->|"escalate"| SW_A
        SW_C -->|"resolved"| SW_D["📝 Summary<br/>Agent"]
    end

    subgraph MO["🌟 MagenticOne — Orchestrator Pattern"]
        MO_O["🎭 Orchestrator"] --> MO_W["🌐 WebSurfer"]
        MO_O --> MO_F["📁 FileSurfer"]
        MO_O --> MO_C["💻 Coder"]
        MO_O --> MO_T["🖥️ Terminal"]
    end

    style RR fill:#0f3460,color:#fff,stroke:#16213e
    style SEL fill:#533483,color:#fff,stroke:#2b1055
    style SW fill:#e94560,color:#fff,stroke:#c81d4e
    style MO fill:#0a8754,color:#fff,stroke:#086841
    style RR_A fill:#00B4D8,color:#fff
    style RR_B fill:#48CAE4,color:#fff
    style RR_C fill:#90E0EF,color:#000
    style SEL_LLM fill:#9B5DE5,color:#fff
    style SEL_A fill:#F15BB5,color:#fff
    style SEL_B fill:#FEE440,color:#000
    style SEL_C fill:#00BBF9,color:#fff
    style SW_A fill:#FF6B6B,color:#fff
    style SW_B fill:#4ECDC4,color:#fff
    style SW_C fill:#FFE66D,color:#000
    style SW_D fill:#A8E6CF,color:#000
    style MO_O fill:#2ECC71,color:#fff
    style MO_W fill:#3498DB,color:#fff
    style MO_F fill:#E67E22,color:#fff
    style MO_C fill:#9B59B6,color:#fff
    style MO_T fill:#1ABC9C,color:#fff
```

## 3. Code Execution Flow

```mermaid
sequenceDiagram
    participant U as 👤 User
    participant C as 🧑‍💻 Coder Agent
    participant R as 🔍 Reviewer Agent
    participant E as ⚡ Code Executor
    participant D as 🐳 Docker Sandbox

    U->>C: "Analyze NIFTY50 returns"
    C->>C: Generate Python code
    C->>R: Code for review
    R-->>C: "Add error handling for missing data"
    C->>C: Revise code
    C->>E: ```python code block```
    E->>D: Execute in isolated container
    D-->>E: stdout + figures
    E->>C: "Output: Sharpe=1.2, MaxDD=15%"
    C->>U: Final analysis with charts

    Note over D: ⚠️ Sandboxed: no network, limited CPU/RAM
```

## 4. Agent Tool Calling Flow

```mermaid
flowchart TD
    MSG["📩 User Message"] --> AG["🤖 AssistantAgent"]
    AG --> LLM["🧠 LLM Decides Action"]
    LLM --> TC{"Tool Call<br/>Required?"}

    TC -->|"Yes"| TOOL["🔧 Execute Tool"]
    TC -->|"No"| RESP["💬 Text Response"]

    TOOL --> T1["📊 fetch_market_data()"]
    TOOL --> T2["🔢 calculate_risk()"]
    TOOL --> T3["📧 send_alert()"]

    T1 --> RES["📋 Tool Result"]
    T2 --> RES
    T3 --> RES

    RES --> LLM2["🧠 LLM Processes Result"]
    LLM2 --> TC2{"More Tools<br/>Needed?"}
    TC2 -->|"Yes"| TOOL
    TC2 -->|"No"| FINAL["✅ Final Response"]

    style MSG fill:#3498DB,color:#fff
    style AG fill:#0078D4,color:#fff
    style LLM fill:#9B59B6,color:#fff
    style TOOL fill:#E67E22,color:#fff
    style RESP fill:#2ECC71,color:#fff
    style T1 fill:#F39C12,color:#fff
    style T2 fill:#F39C12,color:#fff
    style T3 fill:#F39C12,color:#fff
    style RES fill:#1ABC9C,color:#fff
    style LLM2 fill:#9B59B6,color:#fff
    style FINAL fill:#27AE60,color:#fff
    style TC fill:#8E44AD,color:#fff
    style TC2 fill:#8E44AD,color:#fff
```

## 5. Distributed Agent Architecture (gRPC)

```mermaid
graph TD
    subgraph ORCH["🏢 Orchestrator Node"]
        RT["⚙️ Agent Runtime Host<br/>(gRPC Server)"]
        TR["🗺️ Topic Router"]
        REG["📋 Agent Registry"]
    end

    subgraph W1["🖥️ Worker Node 1 (GPU)"]
        A1["🧪 Research Agent"]
        A2["📈 ML Inference Agent"]
    end

    subgraph W2["🖥️ Worker Node 2 (CPU)"]
        A3["📊 Data Analysis Agent"]
        A4["📝 Report Writer Agent"]
    end

    subgraph W3["🖥️ Worker Node 3 (Docker)"]
        A5["💻 Code Executor Agent"]
        A6["🧪 Test Runner Agent"]
    end

    RT --> TR
    TR -->|"topic: research"| A1
    TR -->|"topic: ml"| A2
    TR -->|"topic: analysis"| A3
    TR -->|"topic: report"| A4
    TR -->|"topic: code"| A5
    TR -->|"topic: test"| A6
    REG -.->|"register"| W1
    REG -.->|"register"| W2
    REG -.->|"register"| W3

    style ORCH fill:#1a1a2e,color:#fff,stroke:#e94560
    style W1 fill:#0f3460,color:#fff,stroke:#16213e
    style W2 fill:#533483,color:#fff,stroke:#2b1055
    style W3 fill:#e94560,color:#fff,stroke:#c81d4e
    style RT fill:#0078D4,color:#fff
    style TR fill:#00B4D8,color:#fff
    style REG fill:#48CAE4,color:#fff
    style A1 fill:#2ECC71,color:#fff
    style A2 fill:#27AE60,color:#fff
    style A3 fill:#9B59B6,color:#fff
    style A4 fill:#8E44AD,color:#fff
    style A5 fill:#E74C3C,color:#fff
    style A6 fill:#C0392B,color:#fff
```

## 6. AutoGen vs CrewAI vs LangGraph

```mermaid
graph TB
    subgraph Compare["🔍 Multi-Agent Framework Comparison"]
        direction LR
        subgraph AG["🤖 AutoGen"]
            AG1["✅ Code execution"]
            AG2["✅ Distributed gRPC"]
            AG3["✅ MagenticOne"]
            AG4["⚠️ Complex async API"]
        end

        subgraph CR["🚀 CrewAI"]
            CR1["✅ Simple YAML config"]
            CR2["✅ Role-based agents"]
            CR3["✅ Built-in memory"]
            CR4["⚠️ No code sandbox"]
        end

        subgraph LG["🔗 LangGraph"]
            LG1["✅ State machines"]
            LG2["✅ Durable execution"]
            LG3["✅ LangSmith tracing"]
            LG4["⚠️ Steep learning curve"]
        end
    end

    style Compare fill:#1a1a2e,color:#fff,stroke:#e94560
    style AG fill:#0078D4,color:#fff
    style CR fill:#FF6B6B,color:#fff
    style LG fill:#2ECC71,color:#fff
    style AG1 fill:#00B4D8,color:#fff
    style AG2 fill:#00B4D8,color:#fff
    style AG3 fill:#00B4D8,color:#fff
    style AG4 fill:#FFB703,color:#000
    style CR1 fill:#E74C3C,color:#fff
    style CR2 fill:#E74C3C,color:#fff
    style CR3 fill:#E74C3C,color:#fff
    style CR4 fill:#FFB703,color:#000
    style LG1 fill:#27AE60,color:#fff
    style LG2 fill:#27AE60,color:#fff
    style LG3 fill:#27AE60,color:#fff
    style LG4 fill:#FFB703,color:#000
```

## 7. Termination & Control Flow

```mermaid
flowchart TD
    START["🚀 Team.run(task)"] --> LOOP["🔄 Conversation Loop"]
    LOOP --> NEXT["📣 Next Agent Speaks"]
    NEXT --> CHECK{"🛑 Termination<br/>Condition?"}

    CHECK -->|"TextMention: APPROVED"| DONE["✅ Task Complete"]
    CHECK -->|"MaxMessages: 20"| DONE
    CHECK -->|"TokenUsage: 10K"| DONE
    CHECK -->|"Handoff: human"| HUMAN["👤 Human Review"]
    CHECK -->|"None met"| LOOP

    HUMAN --> APPROVE{"Approved?"}
    APPROVE -->|"Yes"| LOOP
    APPROVE -->|"No"| CANCEL["❌ Task Cancelled"]

    style START fill:#3498DB,color:#fff
    style LOOP fill:#9B59B6,color:#fff
    style NEXT fill:#E67E22,color:#fff
    style CHECK fill:#F39C12,color:#fff
    style DONE fill:#2ECC71,color:#fff
    style HUMAN fill:#00B4D8,color:#fff
    style APPROVE fill:#E74C3C,color:#fff
    style CANCEL fill:#C0392B,color:#fff
```

## 8. Financial Trading Multi-Agent System

```mermaid
graph TD
    subgraph TRADING["📈 AutoGen Trading System"]
        MKT["📊 Market Data<br/>Agent"] -->|"OHLCV data"| SIG["🎯 Signal<br/>Generator"]
        SIG -->|"buy/sell signals"| RISK["🛡️ Risk<br/>Manager"]
        RISK -->|"validated orders"| EXEC["⚡ Execution<br/>Agent"]
        EXEC -->|"fills"| PORT["💼 Portfolio<br/>Tracker"]
        PORT -->|"P&L updates"| MON["📡 Monitor<br/>& Alert"]
        MON -->|"anomaly"| RISK
    end

    subgraph TOOLS["🔧 Agent Tools"]
        T1["Kite API<br/>Market Data"]
        T2["BigQuery<br/>Historical"]
        T3["SEBI Validator<br/>Compliance"]
        T4["Telegram<br/>Alerts"]
    end

    MKT --> T1
    SIG --> T2
    RISK --> T3
    MON --> T4

    style TRADING fill:#1a1a2e,color:#fff,stroke:#e94560
    style MKT fill:#3498DB,color:#fff
    style SIG fill:#2ECC71,color:#fff
    style RISK fill:#E74C3C,color:#fff
    style EXEC fill:#F39C12,color:#fff
    style PORT fill:#9B59B6,color:#fff
    style MON fill:#1ABC9C,color:#fff
    style TOOLS fill:#0f3460,color:#fff
    style T1 fill:#00B4D8,color:#fff
    style T2 fill:#48CAE4,color:#fff
    style T3 fill:#90E0EF,color:#000
    style T4 fill:#CAF0F8,color:#000
```

## 9. Learning Path

```mermaid
graph TD
    subgraph W1["📗 Week 1: Foundations"]
        B1["🤖 Single Agent<br/>AssistantAgent.run()"]
        B2["💬 Two Agents<br/>RoundRobinGroupChat"]
        B3["🛑 Termination<br/>Conditions"]
    end

    subgraph W2["📘 Week 2: Intermediate"]
        I1["🔧 Tool Use<br/>Function calling"]
        I2["🐳 Code Execution<br/>Docker sandbox"]
        I3["🎯 SelectorGroupChat<br/>LLM routing"]
    end

    subgraph W3["📙 Week 3: Advanced"]
        A1["🐝 Swarm Pattern<br/>Dynamic handoffs"]
        A2["👤 Human-in-Loop<br/>Approval workflows"]
        A3["🌟 MagenticOne<br/>Orchestrator"]
    end

    subgraph W4["📕 Week 4: Production"]
        P1["📡 Distributed gRPC<br/>Multi-node agents"]
        P2["⚙️ Custom Runtime<br/>Event-driven"]
        P3["🏭 AutoGen Studio<br/>No-code UI"]
    end

    W1 --> W2 --> W3 --> W4

    style W1 fill:#2ECC71,color:#fff
    style W2 fill:#3498DB,color:#fff
    style W3 fill:#E67E22,color:#fff
    style W4 fill:#E74C3C,color:#fff
    style B1 fill:#27AE60,color:#fff
    style B2 fill:#27AE60,color:#fff
    style B3 fill:#27AE60,color:#fff
    style I1 fill:#2980B9,color:#fff
    style I2 fill:#2980B9,color:#fff
    style I3 fill:#2980B9,color:#fff
    style A1 fill:#D35400,color:#fff
    style A2 fill:#D35400,color:#fff
    style A3 fill:#D35400,color:#fff
    style P1 fill:#C0392B,color:#fff
    style P2 fill:#C0392B,color:#fff
    style P3 fill:#C0392B,color:#fff
```
