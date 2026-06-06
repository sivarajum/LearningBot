# Agentic AI: Visual Guide & Architecture Diagrams

## 1. Agent Architecture Overview

```mermaid
graph TD
    GOAL["🎯 User Goal"] --> PLAN["📋 Planning<br/>(Decompose)"]
    PLAN --> ACT["⚡ Action<br/>(Tool Use)"]
    ACT --> OBS["👁️ Observation<br/>(Results)"]
    OBS --> REFLECT["🔍 Reflection<br/>(Evaluate)"]
    REFLECT -->|"🔄 Not done"| PLAN
    REFLECT -->|"✅ Done"| OUTPUT["✅ Final Output"]

    TOOLS["🔧 Tools<br/>APIs, DBs, Code"] --> ACT
    MEM["🧠 Memory<br/>Short + Long term"] --> PLAN
    MEM --> REFLECT

    style GOAL fill:#3498DB,color:#fff,stroke:#2980B9
    style PLAN fill:#9B59B6,color:#fff,stroke:#8E44AD
    style ACT fill:#E74C3C,color:#fff,stroke:#C0392B
    style OBS fill:#F39C12,color:#fff,stroke:#E67E22
    style REFLECT fill:#E67E22,color:#fff,stroke:#D35400
    style OUTPUT fill:#2ECC71,color:#fff,stroke:#27AE60
    style TOOLS fill:#00B4D8,color:#fff
    style MEM fill:#1ABC9C,color:#fff
```

## 2. ReAct Pattern Flow

```mermaid
sequenceDiagram
    participant U as 👤 User
    participant A as 🤖 LLM Agent
    participant T1 as 📊 Stock API
    participant T2 as 🔢 Calculator

    U->>A: "Analyze RELIANCE valuation"
    A->>A: 💭 Thought: Need P/E ratio
    A->>T1: get_stock_data("RELIANCE")
    T1-->>A: {price: 2850, pe: 28.5}
    A->>A: 💭 Thought: Need sector average
    A->>T1: get_sector_avg("Oil & Gas")
    T1-->>A: {avg_pe: 22.3}
    A->>A: 💭 Thought: Calculate premium
    A->>T2: calculate((28.5-22.3)/22.3*100)
    T2-->>A: 27.8%
    A->>A: 💭 Thought: Have all data
    A-->>U: "RELIANCE P/E 28.5 = 28% premium to sector"
```

## 3. Multi-Agent Patterns

```mermaid
flowchart TD
    subgraph SA["🤖 Single Agent"]
        SAA["Agent + N Tools"]
    end

    subgraph SUP_G["👔 Supervisor Pattern"]
        SUP["🎯 Supervisor"] --> W1["🤖 Agent A"]
        SUP --> W2["🤖 Agent B"]
        SUP --> W3["🤖 Agent C"]
    end

    subgraph HIE["🏢 Hierarchical"]
        MGR["👔 Manager"]
        MGR --> LEAD1["👨‍💼 Team Lead"]
        MGR --> LEAD2["👨‍💼 Team Lead"]
        LEAD1 --> E1["🤖 Worker"]
        LEAD1 --> E2["🤖 Worker"]
        LEAD2 --> E3["🤖 Worker"]
    end

    subgraph SWA["🔄 Swarm (OpenAI)"]
        P1["🤖 Agent A"] -->|"handoff"| P2["🤖 Agent B"]
        P2 -->|"handoff"| P3["🤖 Agent C"]
        P3 -->|"handoff"| P1
    end

    style SA fill:#2ECC71,color:#fff,stroke:#27AE60
    style SUP_G fill:#3498DB,color:#fff,stroke:#2980B9
    style HIE fill:#E74C3C,color:#fff,stroke:#C0392B
    style SWA fill:#F39C12,color:#fff,stroke:#E67E22
    style SAA fill:#27AE60,color:#fff
    style SUP fill:#2980B9,color:#fff
    style MGR fill:#C0392B,color:#fff
    style W1 fill:#48CAE4,color:#fff
    style W2 fill:#48CAE4,color:#fff
    style W3 fill:#48CAE4,color:#fff
    style LEAD1 fill:#E67E22,color:#fff
    style LEAD2 fill:#E67E22,color:#fff
    style E1 fill:#F39C12,color:#fff
    style E2 fill:#F39C12,color:#fff
    style E3 fill:#F39C12,color:#fff
    style P1 fill:#E67E22,color:#fff
    style P2 fill:#E67E22,color:#fff
    style P3 fill:#E67E22,color:#fff
```

## 4. Plan-and-Execute Pattern

```mermaid
flowchart TD
    GOAL["🎯 Goal: Analyze top stocks"] --> PLANNER["📋 Planner (GPT-4o)"]
    PLANNER --> PLAN["📝 Plan:<br/>1. Fetch data<br/>2. Calculate indicators<br/>3. Rank stocks<br/>4. Generate report"]

    PLAN --> E1["⚡ Executor: Step 1<br/>Fetch OHLCV data"]
    E1 --> E2["⚡ Executor: Step 2<br/>Calculate RSI, MACD"]
    E2 --> E3["⚡ Executor: Step 3<br/>Rank by momentum"]
    E3 --> E4["⚡ Executor: Step 4<br/>Generate report"]

    E2 -->|"❌ Step failed"| REPLAN["🔄 Replanner<br/>Revise remaining plan"]
    REPLAN --> E3

    E4 --> RESULT["✅ Final Report"]

    style GOAL fill:#3498DB,color:#fff
    style PLANNER fill:#9B59B6,color:#fff,stroke:#8E44AD
    style PLAN fill:#8E44AD,color:#fff
    style E1 fill:#E67E22,color:#fff
    style E2 fill:#E67E22,color:#fff
    style E3 fill:#E67E22,color:#fff
    style E4 fill:#E67E22,color:#fff
    style REPLAN fill:#E74C3C,color:#fff,stroke:#C0392B
    style RESULT fill:#2ECC71,color:#fff,stroke:#27AE60
```

## 5. Memory Architecture

```mermaid
graph TD
    AGENT["🤖 Agent"]

    subgraph WM["⚡ Working Memory"]
        WMA["📋 Current Variables<br/>Intermediate Results"]
    end

    subgraph STM["💬 Short-Term Memory"]
        STMA["📝 Conversation History<br/>(Current Session)"]
    end

    subgraph LTM["💾 Long-Term Memory"]
        LTMA["🔢 Vector DB<br/>User Prefs, Facts"]
    end

    subgraph EP["📚 Episodic Memory"]
        EPA["🔄 Past Task Outcomes<br/>Learned Patterns"]
    end

    AGENT --> WM
    AGENT --> STM
    AGENT --> LTM
    AGENT --> EP

    style WM fill:#2ECC71,color:#fff,stroke:#27AE60
    style STM fill:#F39C12,color:#fff,stroke:#E67E22
    style LTM fill:#E74C3C,color:#fff,stroke:#C0392B
    style EP fill:#9B59B6,color:#fff,stroke:#8E44AD
    style WMA fill:#27AE60,color:#fff
    style STMA fill:#E67E22,color:#fff
    style LTMA fill:#C0392B,color:#fff
    style EPA fill:#8E44AD,color:#fff
    style AGENT fill:#3498DB,color:#fff
```

## 6. Safety & Guardrails for Agents

```mermaid
flowchart TD
    INPUT["📨 User Request"] --> GUARD1["🛡️ Input Guardrails"]
    GUARD1 --> AGENT["🤖 Agent Loop"]
    AGENT --> TOOL["🔧 Tool Call"]
    TOOL --> GUARD2["⚠️ Action Guardrails"]
    GUARD2 -->|"✅ Safe"| EXEC["⚡ Execute Tool"]
    GUARD2 -->|"🚨 Dangerous"| HITL["👤 Human Approval"]
    HITL -->|"✅ Approved"| EXEC
    HITL -->|"❌ Rejected"| BLOCK["🚫 Block Action"]
    EXEC --> RESULT["📊 Result"]
    RESULT --> GUARD3["🛡️ Output Guardrails"]
    GUARD3 --> OUTPUT["✅ Response to User"]

    ITER{"⏱️ Max iterations?"}
    AGENT --> ITER
    ITER -->|"Yes"| FORCE["⚠️ Force Synthesize"]

    style INPUT fill:#3498DB,color:#fff
    style GUARD1 fill:#2ECC71,color:#fff,stroke:#27AE60
    style GUARD2 fill:#F39C12,color:#fff,stroke:#E67E22
    style GUARD3 fill:#E74C3C,color:#fff,stroke:#C0392B
    style HITL fill:#9B59B6,color:#fff,stroke:#8E44AD
    style AGENT fill:#8E44AD,color:#fff
    style EXEC fill:#00B4D8,color:#fff
    style BLOCK fill:#C0392B,color:#fff
    style OUTPUT fill:#27AE60,color:#fff
    style FORCE fill:#E67E22,color:#fff
```

## 7. Trading Agent Architecture (sjarvis)

```mermaid
flowchart TD
    subgraph Agents["🤖 sjarvis Multi-Agent System"]
        ALPHA["🔬 AlphaLab<br/>Quant research, alpha"]
        RISK["🛡️ RiskGuard<br/>Risk analysis, SEBI"]
        EXEC_A["⚡ ExecOps<br/>Order quality, slippage"]
        DATA["📊 DataPulse<br/>Market data, regime"]
    end

    SIGNAL["📊 Trading Signal<br/>BUY RELIANCE 100"] --> RISK
    RISK --> SEBI{"🏛️ SEBI<br/>Compliant?"}
    SEBI -->|"✅ Pass"| EXEC_A
    SEBI -->|"❌ Fail"| REJECT["🚫 Reject + Log"]
    EXEC_A --> KITE["📡 Kite API<br/>Order execution"]
    KITE --> BQ["💾 BigQuery<br/>Audit trail"]

    ALPHA --> SIGNAL
    DATA --> ALPHA

    style Agents fill:#1a1a2e,color:#fff,stroke:#e94560
    style ALPHA fill:#3498DB,color:#fff
    style RISK fill:#E74C3C,color:#fff
    style EXEC_A fill:#F39C12,color:#fff
    style DATA fill:#9B59B6,color:#fff
    style SIGNAL fill:#00B4D8,color:#fff
    style SEBI fill:#E67E22,color:#fff
    style REJECT fill:#C0392B,color:#fff
    style KITE fill:#2ECC71,color:#fff
    style BQ fill:#1ABC9C,color:#fff
```

## 8. Framework Comparison

```mermaid
graph TB
    subgraph CMP["🔍 Agentic Framework Comparison"]
        direction LR
        subgraph LG["🔵 LangGraph"]
            LG1["📊 Graph State Machine"]
            LG2["💾 Checkpointing"]
            LG3["🎛️ Max Control"]
        end

        subgraph CR["🟢 CrewAI"]
            CR1["👥 Role-Based Teams"]
            CR2["📋 YAML Config"]
            CR3["⚡ Easy Setup"]
        end

        subgraph AG["🔴 AutoGen"]
            AG1["💬 Conversation-Based"]
            AG2["💻 Code Execution"]
            AG3["🌐 Distributed"]
        end
    end

    style CMP fill:#1a1a2e,color:#fff,stroke:#e94560
    style LG fill:#3498DB,color:#fff
    style CR fill:#2ECC71,color:#fff
    style AG fill:#E74C3C,color:#fff
    style LG1 fill:#2980B9,color:#fff
    style LG2 fill:#2980B9,color:#fff
    style LG3 fill:#2980B9,color:#fff
    style CR1 fill:#27AE60,color:#fff
    style CR2 fill:#27AE60,color:#fff
    style CR3 fill:#27AE60,color:#fff
    style AG1 fill:#C0392B,color:#fff
    style AG2 fill:#C0392B,color:#fff
    style AG3 fill:#C0392B,color:#fff
```

## 9. Learning Path

```mermaid
graph TD
    subgraph W1["📗 Week 1: Foundations"]
        B1["⚡ ReAct Pattern<br/>Single agent + tools"]
        B2["🧠 Memory<br/>Short + long term"]
    end

    subgraph W2["📘 Week 2: Multi-Agent"]
        I1["👔 Supervisor Pattern<br/>Orchestration"]
        I2["📋 Plan-Execute<br/>Complex workflows"]
    end

    subgraph W3["📙 Week 3: Safety"]
        A1["👤 Human-in-Loop<br/>Safety gates"]
        A2["🛡️ Guardrails<br/>Action validation"]
    end

    subgraph W4["📕 Week 4: Production"]
        P1["🌐 Distributed Agents<br/>gRPC, message queues"]
        P2["📊 Monitoring<br/>Evaluation, observability"]
    end

    W1 --> W2 --> W3 --> W4

    style W1 fill:#2ECC71,color:#fff,stroke:#27AE60
    style W2 fill:#3498DB,color:#fff,stroke:#2980B9
    style W3 fill:#E67E22,color:#fff,stroke:#D35400
    style W4 fill:#E74C3C,color:#fff,stroke:#C0392B
    style B1 fill:#27AE60,color:#fff
    style B2 fill:#27AE60,color:#fff
    style I1 fill:#2980B9,color:#fff
    style I2 fill:#2980B9,color:#fff
    style A1 fill:#D35400,color:#fff
    style A2 fill:#D35400,color:#fff
    style P1 fill:#C0392B,color:#fff
    style P2 fill:#C0392B,color:#fff
```
