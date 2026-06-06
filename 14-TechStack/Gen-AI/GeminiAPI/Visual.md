# Gemini API: Visual Guide & Architecture Diagrams

## 1. Gemini Model Family

```mermaid
flowchart LR
    subgraph Models["🌟 Gemini Models (2025)"]
        PRO["🧠 Gemini 2.5 Pro<br/>Best reasoning<br/>2M context preview<br/>$$$"]
        FLASH["⚡ Gemini 2.5 Flash<br/>Best balance<br/>Thinking mode<br/>$$"]
        FREE["🆓 Gemini 2.0 Flash<br/>Free tier<br/>15 RPM / 1.5K daily<br/>$0"]
    end

    PRO -->|"Complex"| U1["📚 Research<br/>Long documents<br/>Multi-step analysis"]
    FLASH -->|"Standard"| U2["💻 Coding, chat<br/>Function calling<br/>Structured output"]
    FREE -->|"Simple"| U3["🏷️ Classification<br/>Extraction<br/>Prototyping"]

    style Models fill:#1a1a2e,color:#fff,stroke:#e94560
    style PRO fill:#E63946,color:#fff,stroke:#D62828
    style FLASH fill:#F39C12,color:#fff,stroke:#E67E22
    style FREE fill:#2ECC71,color:#fff,stroke:#27AE60
    style U1 fill:#C0392B,color:#fff
    style U2 fill:#E67E22,color:#fff
    style U3 fill:#27AE60,color:#fff
```

## 2. Native Multimodal Architecture

```mermaid
flowchart TD
    subgraph Inputs["📥 All Modalities → Single Model"]
        TEXT["📝 Text"]
        IMAGE["🖼️ Images"]
        AUDIO["🔊 Audio"]
        VIDEO["🎥 Video"]
        PDF["📄 PDFs"]
        CODE["💻 Code"]
    end

    GEMINI["🌟 Gemini Model<br/>(Natively Multimodal)"]

    TEXT & IMAGE & AUDIO & VIDEO & PDF & CODE --> GEMINI

    subgraph Outputs["📤 Output Capabilities"]
        GEN["📝 Text Generation"]
        JSON["📋 Structured JSON"]
        FC["🔧 Function Calls"]
        THINK["💭 Thinking Process"]
    end

    GEMINI --> GEN & JSON & FC & THINK

    style Inputs fill:#0f3460,color:#fff,stroke:#533483
    style Outputs fill:#1a1a2e,color:#fff,stroke:#e94560
    style GEMINI fill:#4285F4,color:#fff,stroke:#3367D6
    style TEXT fill:#3498DB,color:#fff
    style IMAGE fill:#9B59B6,color:#fff
    style AUDIO fill:#E74C3C,color:#fff
    style VIDEO fill:#E67E22,color:#fff
    style PDF fill:#2ECC71,color:#fff
    style CODE fill:#1ABC9C,color:#fff
    style GEN fill:#F39C12,color:#fff
    style JSON fill:#2ECC71,color:#fff
    style FC fill:#E74C3C,color:#fff
    style THINK fill:#9B59B6,color:#fff
```

## 3. Function Calling Flow

```mermaid
sequenceDiagram
    participant U as 👤 User
    participant G as 🌟 Gemini Model
    participant T as 🔧 Your Functions

    U->>G: "What's RELIANCE at?" + tool definitions
    G->>G: Decides to call get_stock_price
    G-->>U: FunctionCall(name="get_stock_price", args={"symbol": "RELIANCE"})
    U->>T: get_stock_price("RELIANCE")
    T-->>U: {"price": 2850.50, "change": "+1.2%"}
    U->>G: FunctionResponse(result={"price": 2850.50})
    G-->>U: "RELIANCE is trading at ₹2,850.50, up 1.2% today."
```

## 4. Context Caching Flow

```mermaid
flowchart TD
    subgraph Upload["📤 Step 1: Upload & Cache"]
        DOC["📄 Large Document<br/>500K tokens<br/>(Annual Report)"]
        UPLOAD["⬆️ genai.upload_file()"]
        CACHE["💾 CachedContent.create()<br/>TTL: 2 hours"]
        DOC --> UPLOAD --> CACHE
    end

    subgraph Query["❓ Step 2: Query (Multiple Times)"]
        Q1["Query 1: Revenue?<br/>💰 Cached rate"]
        Q2["Query 2: Margins?<br/>💰 Cached rate"]
        Q3["Query 3: Debt ratio?<br/>💰 Cached rate"]
    end

    CACHE --> Q1 & Q2 & Q3

    subgraph Cost["💵 Cost Comparison"]
        NC["❌ Without cache:<br/>3 × 500K = 1.5M tokens"]
        WC["✅ With cache:<br/>500K (once) + 3 × query = ~510K"]
        SAVE["🎉 ~65% savings"]
    end

    style Upload fill:#0f3460,color:#fff,stroke:#533483
    style Query fill:#1a1a2e,color:#fff,stroke:#e94560
    style Cost fill:#1a1a2e,color:#fff,stroke:#2ECC71
    style DOC fill:#3498DB,color:#fff
    style UPLOAD fill:#9B59B6,color:#fff
    style CACHE fill:#2ECC71,color:#fff
    style Q1 fill:#F39C12,color:#fff
    style Q2 fill:#F39C12,color:#fff
    style Q3 fill:#F39C12,color:#fff
    style NC fill:#E74C3C,color:#fff
    style WC fill:#2ECC71,color:#fff
    style SAVE fill:#27AE60,color:#fff
```

## 5. Google Search Grounding

```mermaid
flowchart LR
    QUERY["❓ User Query:<br/>'Latest SEBI F&O rules?'"]

    GEMINI2["🌟 Gemini +<br/>Search Tool"]
    SEARCH["🔍 Google Search<br/>Real-time web data"]

    QUERY --> GEMINI2
    GEMINI2 --> SEARCH
    SEARCH --> SOURCES["📎 Grounding Sources<br/>• sebi.gov.in<br/>• moneycontrol.com<br/>• economictimes.com"]
    SOURCES --> RESPONSE["✅ Grounded Response<br/>+ Source citations<br/>+ Confidence scores"]

    style QUERY fill:#3498DB,color:#fff
    style GEMINI2 fill:#4285F4,color:#fff
    style SEARCH fill:#E74C3C,color:#fff
    style SOURCES fill:#F39C12,color:#fff
    style RESPONSE fill:#2ECC71,color:#fff
```

## 6. Thinking Mode Flow

```mermaid
sequenceDiagram
    participant U as 👤 User
    participant F as ⚡ Gemini 2.5 Flash
    participant T as 💭 Thinking Budget

    U->>F: Complex question + thinking_budget=8192
    F->>T: Internal reasoning (hidden from output)
    Note over T: 1. Break down problem<br/>2. Explore approaches<br/>3. Calculate options<br/>4. Verify logic<br/>5. Form conclusion
    T->>F: Reasoning complete
    F-->>U: thought parts + text parts
    Note over U: [Thought]: "First, I need to..."<br/>[Answer]: "The optimal strategy is..."
```

## 7. Gemini Trading Sentiment Pipeline

```mermaid
flowchart TD
    subgraph Sources["📰 Free Data Sources"]
        RSS["📡 Google News RSS<br/>NSE/BSE headlines"]
        BSE["📊 BSE Announcements<br/>Corporate actions"]
        GOV["🏛️ SEBI Circulars<br/>Regulatory updates"]
    end

    subgraph Pipeline["⚡ Gemini Flash Pipeline"]
        INGEST["📥 Collect Headlines<br/>(Last 24 hours)"]
        BATCH["📦 Batch 50 Headlines<br/>Per API call"]
        ANALYZE["🌟 Gemini 2.0 Flash<br/>Sentiment extraction"]
        STRUCT["📋 Structured JSON<br/>{symbol, score, reason}"]
    end

    subgraph Output["📊 Signal Generation"]
        AGG["📈 Aggregate by Symbol<br/>Weighted sentiment"]
        SIG["🚦 Trading Signal<br/>BUY / SELL / HOLD"]
        BQ["💾 BigQuery<br/>sjarvis_signals_fact"]
    end

    Sources --> INGEST --> BATCH --> ANALYZE --> STRUCT --> AGG --> SIG --> BQ

    style Sources fill:#0f3460,color:#fff,stroke:#533483
    style Pipeline fill:#1a1a2e,color:#fff,stroke:#e94560
    style Output fill:#1a1a2e,color:#fff,stroke:#2ECC71
    style RSS fill:#E74C3C,color:#fff
    style BSE fill:#F39C12,color:#fff
    style GOV fill:#9B59B6,color:#fff
    style INGEST fill:#3498DB,color:#fff
    style BATCH fill:#00B4D8,color:#fff
    style ANALYZE fill:#4285F4,color:#fff
    style STRUCT fill:#2ECC71,color:#fff
    style AGG fill:#E67E22,color:#fff
    style SIG fill:#27AE60,color:#fff
    style BQ fill:#1ABC9C,color:#fff
```

## 8. Model Routing Strategy (Cost Optimization)

```mermaid
flowchart TD
    REQ["📨 Incoming Request"] --> CLASS{"🏷️ Classify<br/>Complexity"}

    CLASS -->|"Simple<br/>(extraction, classify)"| T1["🆓 Gemini 2.0 Flash<br/>$0 — Free tier<br/>15 RPM limit"]
    CLASS -->|"Medium<br/>(coding, analysis)"| T2["⚡ Gemini 2.5 Flash<br/>$0.15/1M input<br/>Thinking mode"]
    CLASS -->|"Complex<br/>(research, 1M+ ctx)"| T3["🧠 Gemini 2.5 Pro<br/>$1.25/1M input<br/>Full reasoning"]

    T1 --> FALLBACK{"🔀 Rate<br/>Limited?"}
    FALLBACK -->|"Yes"| T2
    FALLBACK -->|"No"| OUT1["✅ Response"]

    T2 --> TB{"💭 Thinking<br/>Needed?"}
    TB -->|"Yes +8K budget"| THINK["💭 Extended Thinking"]
    TB -->|"No"| OUT2["✅ Response"]
    THINK --> OUT3["✅ Response + Thoughts"]

    style REQ fill:#3498DB,color:#fff
    style CLASS fill:#9B59B6,color:#fff
    style T1 fill:#2ECC71,color:#fff,stroke:#27AE60
    style T2 fill:#F39C12,color:#fff,stroke:#E67E22
    style T3 fill:#E74C3C,color:#fff,stroke:#C0392B
    style FALLBACK fill:#E67E22,color:#fff
    style TB fill:#8E44AD,color:#fff
    style THINK fill:#9B59B6,color:#fff
    style OUT1 fill:#27AE60,color:#fff
    style OUT2 fill:#27AE60,color:#fff
    style OUT3 fill:#27AE60,color:#fff
```

## 9. Gemini vs Claude vs GPT Decision Guide

```mermaid
flowchart TD
    START["🤔 Choose API"] --> Q1{"🎯 Key<br/>Requirement?"}

    Q1 -->|"Long context 1M+"| GEM["✅ Gemini<br/>2M tokens"]
    Q1 -->|"Best reasoning"| CLAUDE["✅ Claude<br/>Extended thinking"]
    Q1 -->|"Ecosystem/plugins"| GPT["✅ GPT-4<br/>Largest ecosystem"]
    Q1 -->|"Free tier needed"| GEM2["✅ Gemini 2.0 Flash<br/>$0"]
    Q1 -->|"Video/audio"| GEM3["✅ Gemini<br/>Native multimodal"]
    Q1 -->|"Code generation"| EITHER["✅ Claude or Gemini<br/>Both excellent"]
    Q1 -->|"Real-time web"| GEM4["✅ Gemini<br/>Search grounding"]

    style START fill:#3498DB,color:#fff
    style Q1 fill:#9B59B6,color:#fff
    style GEM fill:#4285F4,color:#fff
    style CLAUDE fill:#D97706,color:#fff
    style GPT fill:#10A37F,color:#fff
    style GEM2 fill:#2ECC71,color:#fff
    style GEM3 fill:#4285F4,color:#fff
    style EITHER fill:#F39C12,color:#fff
    style GEM4 fill:#4285F4,color:#fff
```

## 10. Learning Path

```mermaid
graph TD
    subgraph W1["📗 Week 1: Basics"]
        W1A["📝 generate_content()<br/>Basic text generation"]
        W1B["⚙️ System instructions<br/>Persona + rules"]
        W1C["💬 Multi-turn chat<br/>start_chat()"]
    end

    subgraph W2["📘 Week 2: Multimodal"]
        W2A["🖼️ Image analysis<br/>Charts, documents"]
        W2B["📄 PDF + Audio<br/>File upload API"]
        W2C["📋 Structured output<br/>JSON schema"]
    end

    subgraph W3["📙 Week 3: Advanced"]
        W3A["🔧 Function calling<br/>Tool integration"]
        W3B["🔍 Search grounding<br/>Real-time data"]
        W3C["💭 Thinking mode<br/>Complex reasoning"]
    end

    subgraph W4["📕 Week 4: Production"]
        W4A["💾 Context caching<br/>Cost optimization"]
        W4B["🔀 Model routing<br/>Free → Flash → Pro"]
        W4C["☁️ Vertex AI<br/>Enterprise deployment"]
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
