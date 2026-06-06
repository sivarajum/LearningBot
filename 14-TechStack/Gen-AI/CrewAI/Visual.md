# CrewAI: Visual Guide & Architecture Diagrams

## 1. CrewAI Architecture Overview

```mermaid
graph TD
    CW["🚀 CrewAI Framework"]
    CW --> AG["🤖 Agents<br/>Role + Goal + Backstory"]
    CW --> TK["📋 Tasks<br/>Description + Expected Output"]
    CW --> CR["👥 Crews<br/>Team Orchestration"]
    CW --> FL["🔀 Flows<br/>Multi-Crew Pipelines"]

    AG --> TOOLS["🔧 Tools<br/>60+ Built-in"]
    AG --> LLM["🧠 LLM<br/>GPT-4o, Claude, Gemini"]
    AG --> MEM["💾 Memory<br/>Short/Long/Entity"]
    AG --> DELEG["🤝 Delegation<br/>Agent → Agent"]

    TK --> ASYNC["⚡ Async Tasks"]
    TK --> PYDANTIC["📦 Structured Output<br/>Pydantic Models"]
    TK --> CALLBACK["🔔 Callbacks"]

    CR --> SEQ["📏 Sequential Process"]
    CR --> HIER["🏛️ Hierarchical Process"]
    CR --> COND["🔀 Consensual Process"]

    FL --> START["🟢 @start"]
    FL --> LISTEN["👂 @listen"]
    FL --> ROUTER["🔀 @router"]

    style CW fill:#0078D4,color:#fff,stroke:#005A9E
    style AG fill:#00B4D8,color:#fff,stroke:#0096C7
    style TK fill:#E63946,color:#fff,stroke:#D62828
    style CR fill:#FFB703,color:#000,stroke:#FB8500
    style FL fill:#9B59B6,color:#fff,stroke:#8E44AD
    style TOOLS fill:#48CAE4,color:#fff
    style LLM fill:#48CAE4,color:#fff
    style MEM fill:#48CAE4,color:#fff
    style DELEG fill:#48CAE4,color:#fff
    style ASYNC fill:#FF6B6B,color:#fff
    style PYDANTIC fill:#FF6B6B,color:#fff
    style CALLBACK fill:#FF6B6B,color:#fff
    style SEQ fill:#FFCA3A,color:#000
    style HIER fill:#FFCA3A,color:#000
    style COND fill:#FFCA3A,color:#000
    style START fill:#8E44AD,color:#fff
    style LISTEN fill:#8E44AD,color:#fff
    style ROUTER fill:#8E44AD,color:#fff
```

## 2. Sequential vs Hierarchical Process

```mermaid
flowchart TD
    subgraph SEQ["📏 Sequential Process — Tasks Execute in Order"]
        S1["📊 Task 1<br/>→ Researcher"] -->|"context passes"| S2["📈 Task 2<br/>→ Analyst"]
        S2 -->|"context passes"| S3["✍️ Task 3<br/>→ Writer"]
        S3 --> S4["✅ Final Output"]
    end

    subgraph HIER["🏛️ Hierarchical Process — Manager Delegates"]
        MGR["👔 Manager Agent<br/>(auto-created by CrewAI)"]
        MGR -->|"assigns research"| H1["🔍 Researcher"]
        MGR -->|"assigns analysis"| H2["📊 Analyst"]
        MGR -->|"assigns writing"| H3["✍️ Writer"]
        H1 -->|"reports back"| MGR
        H2 -->|"reports back"| MGR
        H3 -->|"reports back"| MGR
        MGR --> HF["✅ Final Output"]
    end

    style SEQ fill:#0f3460,color:#fff,stroke:#16213e
    style HIER fill:#533483,color:#fff,stroke:#2b1055
    style S1 fill:#00B4D8,color:#fff
    style S2 fill:#48CAE4,color:#fff
    style S3 fill:#90E0EF,color:#000
    style S4 fill:#2ECC71,color:#fff
    style MGR fill:#E63946,color:#fff
    style H1 fill:#F39C12,color:#fff
    style H2 fill:#E67E22,color:#fff
    style H3 fill:#D35400,color:#fff
    style HF fill:#2ECC71,color:#fff
```

## 3. Flow Orchestration Pattern

```mermaid
flowchart TD
    START["🟢 @start<br/>gather_data()"] --> ANALYZE["🔄 @listen('data_ready')<br/>analyze()"]
    ANALYZE --> ROUTER{"🔀 @router<br/>quality_check()"}
    ROUTER -->|"score > 0.9"| PUBLISH["📤 @listen('publish')<br/>distribute()"]
    ROUTER -->|"score ≤ 0.9"| REVIEW["🔧 @listen('reprocess')<br/>fix_issues()"]
    REVIEW --> ANALYZE
    PUBLISH --> NOTIFY["📧 @listen('published')<br/>send_notification()"]
    NOTIFY --> DONE["✅ Complete"]

    style START fill:#2ECC71,color:#fff,stroke:#27AE60
    style ANALYZE fill:#3498DB,color:#fff,stroke:#2980B9
    style ROUTER fill:#F39C12,color:#fff,stroke:#E67E22
    style PUBLISH fill:#00B4D8,color:#fff,stroke:#0096C7
    style REVIEW fill:#E74C3C,color:#fff,stroke:#C0392B
    style NOTIFY fill:#9B59B6,color:#fff,stroke:#8E44AD
    style DONE fill:#27AE60,color:#fff,stroke:#1E8449
```

## 4. Memory System Architecture

```mermaid
graph TD
    subgraph STM["💭 Short-Term Memory"]
        S1["Current Task Context"]
        S2["Agent Outputs This Run"]
        S3["Tool Call Results"]
    end

    subgraph LTM["🧠 Long-Term Memory"]
        L1["Past Run Learnings<br/>(SQLite + Embeddings)"]
        L2["Successful Strategies"]
        L3["Error Patterns to Avoid"]
    end

    subgraph EM["🏢 Entity Memory"]
        E1["Company Profiles<br/>TCS, RELIANCE, INFY"]
        E2["Person Profiles<br/>CEO, CFO relationships"]
        E3["Market Events<br/>SEBI rulings, AGMs"]
    end

    subgraph USER["👤 User Memory"]
        U1["Preferences"]
        U2["Interaction History"]
    end

    STM -->|"persist learnings"| LTM
    STM -->|"extract entities"| EM
    LTM -->|"inform new runs"| STM
    EM -->|"provide context"| STM
    USER -->|"personalize"| STM

    style STM fill:#00B4D8,color:#fff,stroke:#0096C7
    style LTM fill:#E63946,color:#fff,stroke:#D62828
    style EM fill:#FFB703,color:#000,stroke:#FB8500
    style USER fill:#9B59B6,color:#fff,stroke:#8E44AD
    style S1 fill:#48CAE4,color:#fff
    style S2 fill:#48CAE4,color:#fff
    style S3 fill:#48CAE4,color:#fff
    style L1 fill:#FF6B6B,color:#fff
    style L2 fill:#FF6B6B,color:#fff
    style L3 fill:#FF6B6B,color:#fff
    style E1 fill:#FFCA3A,color:#000
    style E2 fill:#FFCA3A,color:#000
    style E3 fill:#FFCA3A,color:#000
    style U1 fill:#8E44AD,color:#fff
    style U2 fill:#8E44AD,color:#fff
```

## 5. Tool Execution & Agent Delegation Flow

```mermaid
sequenceDiagram
    participant U as 👤 User
    participant C as 🚀 Crew
    participant A1 as 📊 Analyst Agent
    participant A2 as 🧮 Quant Agent
    participant LLM as 🧠 LLM
    participant T as 🔧 Tools

    U->>C: kickoff(inputs={"symbol": "TCS"})
    C->>A1: Execute research task
    A1->>LLM: "Analyze TCS fundamentals"
    LLM-->>A1: Need price data → call tool
    A1->>T: get_stock_price("TCS")
    T-->>A1: "₹4200.75, PE=28.5"
    A1->>LLM: Process results
    LLM-->>A1: Need deeper analysis → delegate
    A1->>A2: delegate("Calculate Sharpe ratio for TCS")
    A2->>T: get_historical_returns("TCS", "1y")
    T-->>A2: Returns data
    A2-->>A1: "Sharpe=1.3, MaxDD=12%"
    A1->>LLM: "Combine all analysis"
    LLM-->>A1: Final recommendation
    A1-->>C: StockAnalysis(rec="BUY", target=₹4500)
    C-->>U: Formatted report
```

## 6. YAML Configuration Flow

```mermaid
flowchart LR
    subgraph CONFIG["📝 YAML Configuration"]
        direction TB
        AY["agents.yaml<br/>Define roles, goals,<br/>backstories, tools"]
        TY["tasks.yaml<br/>Define descriptions,<br/>outputs, agents"]
    end

    subgraph CODE["💻 Python Code"]
        direction TB
        CF["crew.py<br/>@CrewBase class<br/>@agent, @task, @crew"]
        MAIN["main.py<br/>crew.kickoff()"]
    end

    subgraph RUN["🏃 Runtime"]
        direction TB
        R1["Load YAML"]
        R2["Create Agents"]
        R3["Create Tasks"]
        R4["Execute Crew"]
        R5["Return Results"]
    end

    AY --> CF
    TY --> CF
    CF --> MAIN
    MAIN --> R1
    R1 --> R2 --> R3 --> R4 --> R5

    style CONFIG fill:#0f3460,color:#fff,stroke:#16213e
    style CODE fill:#533483,color:#fff,stroke:#2b1055
    style RUN fill:#e94560,color:#fff,stroke:#c81d4e
    style AY fill:#3498DB,color:#fff
    style TY fill:#E67E22,color:#fff
    style CF fill:#9B59B6,color:#fff
    style MAIN fill:#8E44AD,color:#fff
    style R1 fill:#FF6B6B,color:#fff
    style R2 fill:#FF6B6B,color:#fff
    style R3 fill:#FF6B6B,color:#fff
    style R4 fill:#FF6B6B,color:#fff
    style R5 fill:#2ECC71,color:#fff
```

## 7. Financial Trading Crew Example

```mermaid
graph TD
    subgraph CREW["📈 Trading Analysis Crew"]
        direction TB
        A1["🔍 Market Researcher<br/>Scrapes news, filings"] -->|"research report"| A2["📊 Technical Analyst<br/>Charts, indicators"]
        A2 -->|"TA signals"| A3["🧮 Risk Manager<br/>SEBI limits, portfolio risk"]
        A3 -->|"validated signals"| A4["✍️ Report Writer<br/>Investment memo"]
    end

    subgraph TOOLS2["🔧 Tools Used"]
        T1["🌐 SerperDevTool<br/>Web Search"]
        T2["📰 ScrapeWebTool<br/>News Extraction"]
        T3["📊 Custom YFinanceTool<br/>Price Data"]
        T4["📑 FileWriterTool<br/>Save Report"]
    end

    A1 --> T1
    A1 --> T2
    A2 --> T3
    A4 --> T4

    style CREW fill:#1a1a2e,color:#fff,stroke:#e94560
    style TOOLS2 fill:#0f3460,color:#fff
    style A1 fill:#3498DB,color:#fff
    style A2 fill:#E67E22,color:#fff
    style A3 fill:#E74C3C,color:#fff
    style A4 fill:#2ECC71,color:#fff
    style T1 fill:#48CAE4,color:#fff
    style T2 fill:#48CAE4,color:#fff
    style T3 fill:#48CAE4,color:#fff
    style T4 fill:#48CAE4,color:#fff
```

## 8. CrewAI vs AutoGen vs LangGraph

```mermaid
graph TB
    subgraph CMP["🔍 Multi-Agent Framework Comparison"]
        direction LR
        subgraph CR["🚀 CrewAI"]
            C1["✅ Role-based agents"]
            C2["✅ YAML configuration"]
            C3["✅ 60+ built-in tools"]
            C4["✅ Low learning curve"]
            C5["⚠️ No code sandbox"]
        end

        subgraph AG["🤖 AutoGen"]
            A1["✅ Code execution"]
            A2["✅ Distributed gRPC"]
            A3["✅ AutoGen Studio"]
            A4["⚠️ Complex async API"]
            A5["⚠️ MS ecosystem"]
        end

        subgraph LG["🔗 LangGraph"]
            L1["✅ State machines"]
            L2["✅ Durable execution"]
            L3["✅ LangSmith tracing"]
            L4["⚠️ Steep learning curve"]
            L5["⚠️ Vendor lock-in"]
        end
    end

    style CMP fill:#1a1a2e,color:#fff,stroke:#e94560
    style CR fill:#00B4D8,color:#fff
    style AG fill:#E63946,color:#fff
    style LG fill:#2ECC71,color:#fff
    style C1 fill:#0096C7,color:#fff
    style C2 fill:#0096C7,color:#fff
    style C3 fill:#0096C7,color:#fff
    style C4 fill:#0096C7,color:#fff
    style C5 fill:#FFB703,color:#000
    style A1 fill:#D62828,color:#fff
    style A2 fill:#D62828,color:#fff
    style A3 fill:#D62828,color:#fff
    style A4 fill:#FFB703,color:#000
    style A5 fill:#FFB703,color:#000
    style L1 fill:#27AE60,color:#fff
    style L2 fill:#27AE60,color:#fff
    style L3 fill:#27AE60,color:#fff
    style L4 fill:#FFB703,color:#000
    style L5 fill:#FFB703,color:#000
```

## 9. Learning Path

```mermaid
graph TD
    subgraph W1["📗 Week 1: Foundations"]
        B1["🤖 Single Agent<br/>Role + Goal + Backstory"]
        B2["📋 Tasks<br/>Description + Output"]
        B3["👥 Two-Agent Crew<br/>Sequential process"]
    end

    subgraph W2["📘 Week 2: Tools & Output"]
        I1["🔧 Built-in Tools<br/>Search, Scrape, File"]
        I2["🛠️ Custom @tool<br/>Function decorators"]
        I3["📦 Structured Output<br/>Pydantic models"]
    end

    subgraph W3["📙 Week 3: Advanced"]
        A1["🏛️ Hierarchical<br/>Manager agents"]
        A2["💾 Memory<br/>Short/Long/Entity"]
        A3["🤝 Delegation<br/>Agent-to-agent"]
    end

    subgraph W4["📕 Week 4: Production"]
        P1["🔀 Flows<br/>Multi-crew pipelines"]
        P2["📝 YAML Config<br/>@CrewBase class"]
        P3["🏭 CrewAI Enterprise<br/>Deployment"]
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
