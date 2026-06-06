# Prompt Engineering: Visual Guide & Architecture Diagrams

## 1. Prompting Techniques Landscape

```mermaid
graph TD
    PE["🎯 Prompt Engineering"]
    PE --> BASIC["📗 Basic"]
    PE --> ADV["📙 Advanced"]
    PE --> META["📕 Meta"]

    BASIC --> ZS["🎯 Zero-Shot"]
    BASIC --> FS["📝 Few-Shot"]
    BASIC --> COT["🔗 Chain-of-Thought"]

    ADV --> SC["🔄 Self-Consistency"]
    ADV --> TOT["🌳 Tree-of-Thought"]
    ADV --> REACT["⚡ ReAct"]
    ADV --> CHAIN["🔗 Prompt Chaining"]

    META --> AUTO["🤖 Auto-Prompt<br/>(LLM generates prompt)"]
    META --> OPT["📊 Prompt Optimization<br/>(Iterative A/B)"]
    META --> CACHE["💾 Prompt Caching<br/>(Cost reduction)"]

    style PE fill:#0078D4,color:#fff,stroke:#005A9E
    style BASIC fill:#2ECC71,color:#fff,stroke:#27AE60
    style ADV fill:#E74C3C,color:#fff,stroke:#C0392B
    style META fill:#F39C12,color:#fff,stroke:#E67E22
    style ZS fill:#27AE60,color:#fff
    style FS fill:#27AE60,color:#fff
    style COT fill:#27AE60,color:#fff
    style SC fill:#C0392B,color:#fff
    style TOT fill:#C0392B,color:#fff
    style REACT fill:#C0392B,color:#fff
    style CHAIN fill:#C0392B,color:#fff
    style AUTO fill:#E67E22,color:#fff
    style OPT fill:#E67E22,color:#fff
    style CACHE fill:#E67E22,color:#fff
```

## 2. Chain-of-Thought Flow

```mermaid
sequenceDiagram
    participant U as 👤 User
    participant L as 🧠 LLM

    U->>L: "Is RELIANCE overvalued?<br/>P/E=28.5, Sector avg=22"
    Note right of L: 🔗 Step 1: P/E = 28.5
    Note right of L: 🔗 Step 2: Sector avg = 22
    Note right of L: 🔗 Step 3: Premium = (28.5-22)/22 = 29.5%
    Note right of L: 🔗 Step 4: >20% premium = overvalued
    L-->>U: "Yes, 29.5% premium indicates overvaluation"
```

## 3. Self-Consistency Pattern

```mermaid
flowchart TD
    Q["❓ Complex Question"] --> P1["🔀 Path 1<br/>(Temperature 0.7)"]
    Q --> P2["🔀 Path 2<br/>(Temperature 0.7)"]
    Q --> P3["🔀 Path 3<br/>(Temperature 0.7)"]

    P1 --> A1["📊 Answer: BUY"]
    P2 --> A2["📊 Answer: BUY"]
    P3 --> A3["📊 Answer: HOLD"]

    A1 --> VOTE["🗳️ Majority Vote"]
    A2 --> VOTE
    A3 --> VOTE

    VOTE --> FINAL["✅ Final: BUY (2/3)"]

    style Q fill:#3498DB,color:#fff,stroke:#2980B9
    style P1 fill:#9B59B6,color:#fff
    style P2 fill:#9B59B6,color:#fff
    style P3 fill:#9B59B6,color:#fff
    style A1 fill:#2ECC71,color:#fff
    style A2 fill:#2ECC71,color:#fff
    style A3 fill:#F39C12,color:#fff
    style VOTE fill:#E67E22,color:#fff,stroke:#D35400
    style FINAL fill:#27AE60,color:#fff,stroke:#1E8449
```

## 4. Tree-of-Thought (ToT) Reasoning

```mermaid
flowchart TD
    ROOT["🌳 Problem: Optimal Portfolio Allocation<br/>₹10L across 5 sectors"]

    ROOT --> B1["💭 Branch 1:<br/>Equal weight 20% each"]
    ROOT --> B2["💭 Branch 2:<br/>Risk-parity based"]
    ROOT --> B3["💭 Branch 3:<br/>Momentum weighted"]

    B1 --> E1["📊 Evaluate:<br/>Sharpe=0.8, MaxDD=15%"]
    B2 --> E2["📊 Evaluate:<br/>Sharpe=1.1, MaxDD=10%"]
    B3 --> E3["📊 Evaluate:<br/>Sharpe=1.3, MaxDD=22%"]

    E1 --> PRUNE1["❌ Pruned<br/>Low Sharpe"]
    E2 --> EXPAND["🔍 Expand Best 2"]
    E3 --> EXPAND

    EXPAND --> SUB1["💡 Risk-parity +<br/>momentum tilt"]
    EXPAND --> SUB2["💡 Pure momentum +<br/>stop-loss"]

    SUB1 --> WIN["✅ Best: Sharpe=1.4, MaxDD=12%"]

    style ROOT fill:#3498DB,color:#fff
    style B1 fill:#9B59B6,color:#fff
    style B2 fill:#9B59B6,color:#fff
    style B3 fill:#9B59B6,color:#fff
    style E1 fill:#E74C3C,color:#fff
    style E2 fill:#2ECC71,color:#fff
    style E3 fill:#F39C12,color:#fff
    style PRUNE1 fill:#95A5A6,color:#fff
    style EXPAND fill:#00B4D8,color:#fff
    style SUB1 fill:#1ABC9C,color:#fff
    style SUB2 fill:#1ABC9C,color:#fff
    style WIN fill:#27AE60,color:#fff,stroke:#1E8449
```

## 5. Prompt Chaining Pipeline

```mermaid
flowchart LR
    INPUT["📄 Earnings Report<br/>(Raw PDF)"] --> S1["🔍 Step 1: Extract<br/>(Haiku — cheap)"]
    S1 --> D1["📋 Metrics JSON"]
    D1 --> S2["📊 Step 2: Analyze<br/>(Sonnet — smart)"]
    S2 --> D2["📝 Analysis"]
    D2 --> S3["🔄 Step 3: Compare<br/>(Sonnet — smart)"]
    S3 --> D3["📊 Comparison"]
    D3 --> S4["🎯 Step 4: Recommend<br/>(Opus — deep)"]
    S4 --> OUTPUT["✅ BUY/HOLD/SELL<br/>+ Rationale"]

    style INPUT fill:#3498DB,color:#fff
    style S1 fill:#2ECC71,color:#fff,stroke:#27AE60
    style S2 fill:#E74C3C,color:#fff,stroke:#C0392B
    style S3 fill:#F39C12,color:#fff,stroke:#E67E22
    style S4 fill:#9B59B6,color:#fff,stroke:#8E44AD
    style D1 fill:#48CAE4,color:#fff
    style D2 fill:#48CAE4,color:#fff
    style D3 fill:#48CAE4,color:#fff
    style OUTPUT fill:#27AE60,color:#fff,stroke:#1E8449
```

## 6. System Prompt Structure (RCTFCE)

```mermaid
graph TD
    SP["📝 System Prompt"] --> R["👤 Role<br/>'SEBI-registered analyst'"]
    SP --> C["🌍 Context<br/>'NSE/BSE, Indian markets'"]
    SP --> T["🎯 Task<br/>'Data-driven analysis'"]
    SP --> F["📋 Format<br/>'JSON, bullet points'"]
    SP --> CO["🚫 Constraints<br/>'No personal advice'"]
    SP --> E["📝 Examples<br/>'TCS analysis demo'"]

    R --> PRIME["🎭 Primes model behavior"]
    F --> CONTROL["📊 Controls output structure"]
    CO --> SAFETY["🛡️ Prevents unsafe outputs"]

    style SP fill:#0078D4,color:#fff,stroke:#005A9E
    style R fill:#2ECC71,color:#fff,stroke:#27AE60
    style C fill:#3498DB,color:#fff,stroke:#2980B9
    style T fill:#9B59B6,color:#fff,stroke:#8E44AD
    style F fill:#F39C12,color:#fff,stroke:#E67E22
    style CO fill:#E74C3C,color:#fff,stroke:#C0392B
    style E fill:#1ABC9C,color:#fff,stroke:#16A085
    style PRIME fill:#27AE60,color:#fff
    style CONTROL fill:#E67E22,color:#fff
    style SAFETY fill:#C0392B,color:#fff
```

## 7. ReAct (Reasoning + Acting) Pattern

```mermaid
flowchart TD
    Q["❓ 'Should I buy TCS at ₹3800?'"] --> T1["💭 Thought 1:<br/>Need current P/E and sector avg"]
    T1 --> A1["⚡ Action 1:<br/>get_fundamentals('TCS')"]
    A1 --> O1["📊 Observation 1:<br/>P/E=32.1, ROE=45%, Debt/Eq=0.1"]

    O1 --> T2["💭 Thought 2:<br/>P/E high but ROE excellent, check peers"]
    T2 --> A2["⚡ Action 2:<br/>get_sector_peers('IT')"]
    A2 --> O2["📊 Observation 2:<br/>Sector avg P/E=28, TCS premium=14.6%"]

    O2 --> T3["💭 Thought 3:<br/>Premium justified by superior ROE, check SEBI limits"]
    T3 --> A3["⚡ Action 3:<br/>check_position_limit('TCS')"]
    A3 --> O3["📊 Observation 3:<br/>Current=2.1%, Limit=5%, OK"]

    O3 --> FINAL["✅ Final Answer:<br/>'BUY TCS — premium justified,<br/>ROE 45% vs sector 22%, SEBI ok'"]

    style Q fill:#3498DB,color:#fff
    style T1 fill:#9B59B6,color:#fff
    style T2 fill:#9B59B6,color:#fff
    style T3 fill:#9B59B6,color:#fff
    style A1 fill:#E74C3C,color:#fff
    style A2 fill:#E74C3C,color:#fff
    style A3 fill:#E74C3C,color:#fff
    style O1 fill:#F39C12,color:#fff
    style O2 fill:#F39C12,color:#fff
    style O3 fill:#F39C12,color:#fff
    style FINAL fill:#2ECC71,color:#fff,stroke:#27AE60
```

## 8. Prompt Injection Defense

```mermaid
flowchart TD
    USER["👤 User Input"] --> L1["🛡️ Layer 1: Regex Filter<br/>(Block known patterns)"]
    L1 -->|"✅ Pass"| L2["🔒 Layer 2: Delimiter Isolation<br/>XML tags wrapping"]
    L2 --> L3["📝 Layer 3: Instruction Sandwich<br/>(Repeat constraints at end)"]
    L3 --> LLM["🧠 LLM Processing"]
    LLM --> L4["🔍 Layer 4: Output Validation<br/>(Check format + topic)"]
    L4 -->|"✅ Valid"| OUT["✅ Safe Response"]
    L4 -->|"🚨 Suspicious"| BLOCK["❌ Blocked"]
    L1 -->|"🚫 Injection"| BLOCK

    style USER fill:#3498DB,color:#fff
    style L1 fill:#E74C3C,color:#fff,stroke:#C0392B
    style L2 fill:#00B4D8,color:#fff,stroke:#0096C7
    style L3 fill:#F39C12,color:#fff,stroke:#E67E22
    style L4 fill:#9B59B6,color:#fff,stroke:#8E44AD
    style LLM fill:#8E44AD,color:#fff
    style OUT fill:#2ECC71,color:#fff,stroke:#27AE60
    style BLOCK fill:#C0392B,color:#fff
```

## 9. Temperature & Sampling Guide

```mermaid
graph LR
    subgraph T0["❄️ T=0.0 (Deterministic)"]
        T0A["📊 Factual Q&A"]
        T0B["💻 Code Generation"]
        T0C["📋 Structured Data"]
    end

    subgraph T3["⚖️ T=0.3-0.5 (Balanced)"]
        T3A["📈 Analysis"]
        T3B["📝 Summarization"]
        T3C["📊 Reporting"]
    end

    subgraph T7["🔥 T=0.7-0.9 (Creative)"]
        T7A["💡 Brainstorming"]
        T7B["✍️ Content Writing"]
        T7C["🎨 Idea Generation"]
    end

    style T0 fill:#3498DB,color:#fff,stroke:#2980B9
    style T3 fill:#F39C12,color:#fff,stroke:#E67E22
    style T7 fill:#E74C3C,color:#fff,stroke:#C0392B
    style T0A fill:#2980B9,color:#fff
    style T0B fill:#2980B9,color:#fff
    style T0C fill:#2980B9,color:#fff
    style T3A fill:#E67E22,color:#fff
    style T3B fill:#E67E22,color:#fff
    style T3C fill:#E67E22,color:#fff
    style T7A fill:#C0392B,color:#fff
    style T7B fill:#C0392B,color:#fff
    style T7C fill:#C0392B,color:#fff
```

## 10. Model-Specific Prompt Formats

```mermaid
graph TD
    subgraph CL["🟠 Claude (Anthropic)"]
        CLA["📋 XML Tags<br/>&lt;system&gt;, &lt;context&gt;<br/>&lt;instructions&gt;"]
        CLB["🔒 cache_control for caching"]
    end

    subgraph GP["🟢 GPT-4o (OpenAI)"]
        GPA["📝 Markdown Headers<br/>## Role, ## Task<br/>JSON mode built-in"]
        GPB["🔧 Function calling schema"]
    end

    subgraph GE["🔵 Gemini (Google)"]
        GEA["📄 Plain Text + JSON<br/>Grounding via Search<br/>Multimodal native"]
        GEB["💭 Thinking mode budget"]
    end

    style CL fill:#D97706,color:#fff
    style GP fill:#10A37F,color:#fff
    style GE fill:#4285F4,color:#fff
    style CLA fill:#B8860B,color:#fff
    style CLB fill:#B8860B,color:#fff
    style GPA fill:#0D8C5F,color:#fff
    style GPB fill:#0D8C5F,color:#fff
    style GEA fill:#3367D6,color:#fff
    style GEB fill:#3367D6,color:#fff
```

## 11. Learning Path

```mermaid
graph TD
    subgraph W1["📗 Week 1: Foundations"]
        B1["🎯 Zero/Few-Shot<br/>Basic prompting"]
        B2["📝 System Prompts<br/>RCTFCE framework"]
    end

    subgraph W2["📘 Week 2: Reasoning"]
        I1["🔗 Chain-of-Thought<br/>Step-by-step"]
        I2["🌳 Tree-of-Thought<br/>Branching logic"]
        I3["⚡ ReAct Pattern<br/>Reason + Act"]
    end

    subgraph W3["📙 Week 3: Production"]
        A1["🔗 Prompt Chaining<br/>Multi-step pipelines"]
        A2["📋 Structured Output<br/>JSON, Pydantic"]
        A3["🔄 Self-Consistency<br/>Majority voting"]
    end

    subgraph W4["📕 Week 4: Security & Scale"]
        P1["📊 A/B Optimization<br/>Prompt testing"]
        P2["💾 Caching<br/>Cost reduction"]
        P3["🛡️ Injection Defense<br/>Security layers"]
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
    style I3 fill:#2980B9,color:#fff
    style A1 fill:#D35400,color:#fff
    style A2 fill:#D35400,color:#fff
    style A3 fill:#D35400,color:#fff
    style P1 fill:#C0392B,color:#fff
    style P2 fill:#C0392B,color:#fff
    style P3 fill:#C0392B,color:#fff
```
