# Claude API: Visual Guide & Architecture Diagrams

## 1. Claude Model Family

```mermaid
flowchart LR
    subgraph Models["🧠 Claude Model Family (2025)"]
        OPUS["🧠 Opus 4<br/>Complex reasoning<br/>Agentic coding<br/>Research"]
        SONNET["⚡ Sonnet 4<br/>Best balance<br/>Coding & analysis<br/>Most popular"]
        HAIKU["🚀 Haiku 3.5<br/>Fastest<br/>Classification<br/>Cost-efficient"]
    end

    OPUS -->|"Hard problems<br/>$15/$75 per 1M"| USE1["🔬 Research<br/>Complex agents"]
    SONNET -->|"Default choice<br/>$3/$15 per 1M"| USE2["💻 Coding, analysis<br/>General tasks"]
    HAIKU -->|"Simple tasks<br/>$0.25/$1.25 per 1M"| USE3["🏷️ Classification<br/>Extraction, routing"]

    style Models fill:#1a1a2e,color:#fff,stroke:#e94560
    style OPUS fill:#E63946,color:#fff,stroke:#D62828
    style SONNET fill:#F39C12,color:#fff,stroke:#E67E22
    style HAIKU fill:#2ECC71,color:#fff,stroke:#27AE60
    style USE1 fill:#C0392B,color:#fff
    style USE2 fill:#E67E22,color:#fff
    style USE3 fill:#27AE60,color:#fff
```

## 2. Messages API Flow

```mermaid
sequenceDiagram
    participant A as 🖥️ Your App
    participant API as 🧠 Claude API
    participant C as 💾 Prompt Cache

    A->>API: messages.create(model, system, messages, tools)
    API->>C: Check cached system prompt
    C-->>API: 💰 Cache hit (90% cheaper)
    API->>API: Process with model

    alt stop_reason = end_turn
        API-->>A: ✅ Final text response
    else stop_reason = tool_use
        API-->>A: 🔧 Tool call request
        A->>A: Execute tool locally
        A->>API: tool_result
        API-->>A: ✅ Final response with tool data
    end
```

## 3. Tool Use Agentic Loop

```mermaid
flowchart TD
    START["❓ User Query"] --> CALL["📡 API Call<br/>(with tools defined)"]
    CALL --> CHECK{"🔍 stop_reason?"}

    CHECK -->|"end_turn"| DONE["✅ Return final answer"]
    CHECK -->|"tool_use"| EXEC["🔧 Execute Tool(s)<br/>get_stock_price(RELIANCE)"]
    CHECK -->|"max_tokens"| TRUNC["⚠️ Response truncated<br/>Continue or increase tokens"]

    EXEC --> RESULT["📤 Send tool_result<br/>back to Claude"]
    RESULT --> CALL

    CALL -->|"Max iterations"| SAFETY["🛑 Safety stop<br/>Return partial answer"]

    style START fill:#3498DB,color:#fff
    style CALL fill:#9B59B6,color:#fff,stroke:#8E44AD
    style CHECK fill:#F39C12,color:#fff
    style DONE fill:#2ECC71,color:#fff,stroke:#27AE60
    style EXEC fill:#E74C3C,color:#fff,stroke:#C0392B
    style RESULT fill:#00B4D8,color:#fff
    style TRUNC fill:#E67E22,color:#fff
    style SAFETY fill:#C0392B,color:#fff
```

## 4. Prompt Caching Cost Flow

```mermaid
flowchart TD
    subgraph First["💵 First Call (Cache Write)"]
        SYS1["📝 System Prompt<br/>50K tokens<br/>cache_control: ephemeral"]
        COST1["💰 Cost: 1.25x normal<br/>(write premium)"]
        SYS1 --> COST1
    end

    subgraph Subsequent["✅ Subsequent Calls (Cache Read)"]
        SYS2["📝 Same System Prompt<br/>50K tokens<br/>Read from cache"]
        COST2["🎉 Cost: 0.1x normal<br/>(90% savings!)"]
        SYS2 --> COST2
    end

    subgraph Savings["📊 5 calls × 50K cached tokens"]
        NORMAL["❌ Without cache:<br/>5 × 50K × $3 = $0.75"]
        CACHED["✅ With cache:<br/>1 × 62.5K + 4 × 5K = $0.14"]
        SAVE["🎉 Savings: 81%"]
        NORMAL --> SAVE
        CACHED --> SAVE
    end

    First --> Subsequent

    style First fill:#E67E22,color:#fff,stroke:#D35400
    style Subsequent fill:#2ECC71,color:#fff,stroke:#27AE60
    style Savings fill:#1a1a2e,color:#fff,stroke:#e94560
    style SYS1 fill:#D35400,color:#fff
    style COST1 fill:#E74C3C,color:#fff
    style SYS2 fill:#27AE60,color:#fff
    style COST2 fill:#2ECC71,color:#fff
    style NORMAL fill:#E74C3C,color:#fff
    style CACHED fill:#2ECC71,color:#fff
    style SAVE fill:#F39C12,color:#fff
```

## 5. Extended Thinking Flow

```mermaid
sequenceDiagram
    participant U as 👤 User
    participant C as ⚡ Claude (Sonnet 4)
    participant T as 💭 Thinking Block
    participant A as 📝 Final Answer

    U->>C: Complex question + thinking enabled
    C->>T: Internal reasoning (budget_tokens)
    Note over T: Step 1: Analyze constraints<br/>Step 2: Consider approaches<br/>Step 3: Evaluate tradeoffs<br/>Step 4: Form recommendation
    T->>A: Structured, well-reasoned response
    A->>U: thinking blocks + text blocks
```

## 6. Cost Optimization Strategy

```mermaid
flowchart TD
    QUERY["📨 Incoming Query"] --> ROUTER{"🏷️ Query<br/>Complexity?"}

    ROUTER -->|"Simple:<br/>classify, extract"| HAIKU2["🚀 Haiku 3.5<br/>$0.25/1M input<br/>~100ms"]
    ROUTER -->|"Standard:<br/>analysis, coding"| SONNET2["⚡ Sonnet 4<br/>$3/1M input<br/>~2s"]
    ROUTER -->|"Complex:<br/>research, math"| OPUS2["🧠 Opus 4<br/>$15/1M input<br/>~10s"]

    HAIKU2 --> CACHE{"💾 Repeated<br/>context?"}
    SONNET2 --> CACHE
    OPUS2 --> CACHE

    CACHE -->|"Yes"| PROMPT_CACHE["💰 Prompt Caching<br/>90% savings"]
    CACHE -->|"No"| DIRECT["📡 Direct call"]

    DIRECT --> URGENT{"⏰ Time-<br/>sensitive?"}
    URGENT -->|"No"| BATCH["📦 Batches API<br/>50% savings<br/>24h delivery"]
    URGENT -->|"Yes"| STREAM["🌊 Streaming<br/>Real-time response"]

    style QUERY fill:#3498DB,color:#fff
    style ROUTER fill:#9B59B6,color:#fff
    style HAIKU2 fill:#2ECC71,color:#fff,stroke:#27AE60
    style SONNET2 fill:#F39C12,color:#fff,stroke:#E67E22
    style OPUS2 fill:#E74C3C,color:#fff,stroke:#C0392B
    style CACHE fill:#00B4D8,color:#fff
    style PROMPT_CACHE fill:#27AE60,color:#fff
    style DIRECT fill:#3498DB,color:#fff
    style URGENT fill:#8E44AD,color:#fff
    style BATCH fill:#2ECC71,color:#fff
    style STREAM fill:#E67E22,color:#fff
```

## 7. Financial Trading Agent Architecture

```mermaid
flowchart TD
    subgraph Agent["🤖 Claude Trading Agent"]
        PROMPT["📝 System Prompt<br/>cache_control: ephemeral<br/>SEBI rules + market context"]
        TOOLS["🔧 Tools Defined<br/>get_price, place_order,<br/>get_portfolio, check_risk"]
    end

    USER["📊 User: 'Analyze RELIANCE'"] --> Agent

    Agent --> T1["🔧 get_stock_price<br/>RELIANCE → ₹2850"]
    T1 --> T2["🔧 get_fundamentals<br/>P/E=28.5, ROE=12%"]
    T2 --> T3["🔧 check_risk<br/>Position=3.2%, Sector=18%"]
    T3 --> THINK["💭 Extended Thinking<br/>Analyze all data points"]
    THINK --> RESP["✅ 'BUY RELIANCE 50 shares<br/>P/E below 5yr avg, SEBI compliant'"]

    style Agent fill:#1a1a2e,color:#fff,stroke:#e94560
    style USER fill:#3498DB,color:#fff
    style T1 fill:#E67E22,color:#fff
    style T2 fill:#F39C12,color:#fff
    style T3 fill:#E74C3C,color:#fff
    style THINK fill:#9B59B6,color:#fff
    style RESP fill:#2ECC71,color:#fff
    style PROMPT fill:#8E44AD,color:#fff
    style TOOLS fill:#00B4D8,color:#fff
```

## 8. Claude vs GPT vs Gemini Comparison

```mermaid
graph TB
    subgraph CMP["🔍 LLM API Comparison"]
        direction LR
        subgraph CL["🟠 Claude (Anthropic)"]
            C1["✅ Best reasoning"]
            C2["✅ Prompt caching 90%"]
            C3["✅ Extended thinking"]
            C4["✅ 200K context"]
            C5["⚠️ No web search"]
        end

        subgraph GP["🟢 GPT-4 (OpenAI)"]
            G1["✅ Largest ecosystem"]
            G2["✅ Plugins / GPTs"]
            G3["✅ DALL-E integration"]
            G4["✅ 128K context"]
            G5["⚠️ No prompt caching"]
        end

        subgraph GM["🔵 Gemini (Google)"]
            GM1["✅ 2M context window"]
            GM2["✅ Best multimodal"]
            GM3["✅ Search grounding"]
            GM4["✅ Free tier"]
            GM5["⚠️ Less battle-tested"]
        end
    end

    style CMP fill:#1a1a2e,color:#fff,stroke:#e94560
    style CL fill:#D97706,color:#fff
    style GP fill:#10A37F,color:#fff
    style GM fill:#4285F4,color:#fff
    style C1 fill:#B8860B,color:#fff
    style C2 fill:#B8860B,color:#fff
    style C3 fill:#B8860B,color:#fff
    style C4 fill:#B8860B,color:#fff
    style C5 fill:#B8860B,color:#fff
    style G1 fill:#0D8C5F,color:#fff
    style G2 fill:#0D8C5F,color:#fff
    style G3 fill:#0D8C5F,color:#fff
    style G4 fill:#0D8C5F,color:#fff
    style G5 fill:#0D8C5F,color:#fff
    style GM1 fill:#3367D6,color:#fff
    style GM2 fill:#3367D6,color:#fff
    style GM3 fill:#3367D6,color:#fff
    style GM4 fill:#3367D6,color:#fff
    style GM5 fill:#3367D6,color:#fff
```

## 9. Learning Path

```mermaid
graph TD
    subgraph W1["📗 Week 1: Basics"]
        W1A["📡 Messages API<br/>Basic calls"]
        W1B["📝 System prompts<br/>Prompt engineering"]
        W1C["🌊 Streaming<br/>Real-time output"]
    end

    subgraph W2["📘 Week 2: Tools"]
        W2A["🔧 Tool definitions<br/>JSON schema"]
        W2B["🔄 Tool use loop<br/>Multi-step agents"]
        W2C["👁️ Vision<br/>Image analysis"]
    end

    subgraph W3["📙 Week 3: Optimization"]
        W3A["💾 Prompt caching<br/>90% cost savings"]
        W3B["💭 Extended thinking<br/>Complex reasoning"]
        W3C["📦 Batches API<br/>50% cost savings"]
    end

    subgraph W4["📕 Week 4: Production"]
        W4A["🔀 Model routing<br/>Haiku/Sonnet/Opus"]
        W4B["🛡️ Error handling<br/>Rate limits, retries"]
        W4C["📊 Monitoring<br/>Usage tracking, costs"]
    end

    W1 --> W2 --> W3 --> W4

    style W1 fill:#2ECC71,color:#fff,stroke:#27AE60
    style W2 fill:#3498DB,color:#fff,stroke:#2980B9
    style W3 fill:#E67E22,color:#fff,stroke:#D35400
    style W4 fill:#E74C3C,color:#fff,stroke:#C0392B
    style W1A fill:#27AE60,color:#fff
    style W1B fill:#27AE60,color:#fff
    style W1C fill:#27AE60,color:#fff
    style W2A fill:#2980B9,color:#fff
    style W2B fill:#2980B9,color:#fff
    style W2C fill:#2980B9,color:#fff
    style W3A fill:#D35400,color:#fff
    style W3B fill:#D35400,color:#fff
    style W3C fill:#D35400,color:#fff
    style W4A fill:#C0392B,color:#fff
    style W4B fill:#C0392B,color:#fff
    style W4C fill:#C0392B,color:#fff
```
