# Few-Shot & Zero-Shot Learning: Visual Guide & Architecture Diagrams

## 1. Learning Paradigm Spectrum

```mermaid
graph LR
    subgraph Paradigms["🎯 Learning Paradigms"]
        ZS["🔴 Zero-Shot<br/>0 examples"]
        OS["🟠 One-Shot<br/>1 example"]
        FS["🟡 Few-Shot<br/>2-10 examples"]
        FT["🟢 Fine-Tuning<br/>1000+ examples"]
    end

    ZS -->|"add 1 example"| OS
    OS -->|"add more"| FS
    FS -->|"collect large dataset"| FT

    subgraph Tradeoffs["⚖️ Tradeoffs"]
        ZS -.->|"Cheapest, least accurate"| T1["⚡ Fast Setup"]
        FT -.->|"Most accurate, expensive"| T2["📊 High Data Need"]
    end

    style Paradigms fill:#1a1a2e,color:#fff,stroke:#e94560
    style Tradeoffs fill:#0f3460,color:#fff,stroke:#533483
    style ZS fill:#E74C3C,color:#fff
    style OS fill:#E67E22,color:#fff
    style FS fill:#F39C12,color:#fff
    style FT fill:#2ECC71,color:#fff
    style T1 fill:#3498DB,color:#fff
    style T2 fill:#9B59B6,color:#fff
```

## 2. Zero-Shot Classification Flow (NLI-Based)

```mermaid
sequenceDiagram
    participant U as 📄 User Input
    participant T as ✂️ Tokenizer
    participant N as 🧠 NLI Model (BART-MNLI)
    participant S as 📊 Score Aggregator
    participant R as ✅ Result

    U->>T: "SEBI bans insider trading"
    Note over T: Create premise-hypothesis pairs

    T->>N: Premise: "SEBI bans insider trading"<br/>Hypothesis: "This is about regulatory"
    N-->>S: entailment: 0.92

    T->>N: Premise: "SEBI bans insider trading"<br/>Hypothesis: "This is about earnings"
    N-->>S: entailment: 0.05

    T->>N: Premise: "SEBI bans insider trading"<br/>Hypothesis: "This is about M&A"
    N-->>S: entailment: 0.03

    S->>R: Label: regulatory (0.92)
```

## 3. Few-Shot In-Context Learning Flow

```mermaid
flowchart TD
    Q["📄 Query Text"] --> R["🔍 Retrieve Similar<br/>Examples from Pool"]
    R --> F["📝 Format Prompt<br/>with Examples"]

    subgraph ExamplePool["📚 Example Pool"]
        E1["'TCS beats' → positive"]
        E2["'Crash 20%' → negative"]
        E3["'Market flat' → neutral"]
        E4["'Guidance raised' → positive"]
        EN["... 100+ examples"]
    end

    ExamplePool --> R

    F --> LLM["🧠 LLM Inference"]
    LLM --> P["📊 Prediction + Confidence"]
    P --> C{"✅ Confidence > threshold?"}
    C -->|"✅ Yes"| Accept["🟢 Accept Result"]
    C -->|"❌ No"| Fallback["🔴 Escalate to<br/>Fine-Tuned Model"]

    style Q fill:#3498DB,color:#fff
    style R fill:#00B4D8,color:#fff
    style F fill:#9B59B6,color:#fff
    style ExamplePool fill:#0f3460,color:#fff,stroke:#533483
    style LLM fill:#8E44AD,color:#fff
    style P fill:#F39C12,color:#fff
    style C fill:#E67E22,color:#fff
    style Accept fill:#2ECC71,color:#fff
    style Fallback fill:#E74C3C,color:#fff
```

## 4. SetFit Training Pipeline

```mermaid
flowchart LR
    subgraph Stage1["🔬 Stage 1: Contrastive Learning"]
        D["📊 8 Labeled<br/>Examples"] --> PP["🔀 Generate<br/>Sentence Pairs"]
        PP --> POS["🟢 Positive Pairs<br/>Same class"]
        PP --> NEG["🔴 Negative Pairs<br/>Different class"]
        POS --> CL["📉 Contrastive<br/>Loss Training"]
        NEG --> CL
        CL --> FE["🧠 Fine-Tuned<br/>Encoder"]
    end

    subgraph Stage2["🎯 Stage 2: Classification Head"]
        FE --> EMB["🔢 Compute<br/>Embeddings"]
        EMB --> LR["📊 Train Logistic<br/>Regression Head"]
        LR --> MODEL["✅ SetFit Model"]
    end

    MODEL --> INF["⚡ Fast Inference<br/>No LLM needed"]

    style Stage1 fill:#1a1a2e,color:#fff,stroke:#e94560
    style Stage2 fill:#1a1a2e,color:#fff,stroke:#2ECC71
    style D fill:#E74C3C,color:#fff
    style PP fill:#9B59B6,color:#fff
    style POS fill:#2ECC71,color:#fff
    style NEG fill:#E74C3C,color:#fff
    style CL fill:#F39C12,color:#fff
    style FE fill:#3498DB,color:#fff
    style EMB fill:#00B4D8,color:#fff
    style LR fill:#E67E22,color:#fff
    style MODEL fill:#27AE60,color:#fff
    style INF fill:#2980B9,color:#fff
```

## 5. Demonstration Selection Strategies

```mermaid
flowchart TD
    Q2["📄 New Query"] --> S{"🎯 Selection Strategy"}

    S -->|"Similarity"| SIM["🔍 kNN Retrieval"]
    SIM --> S1["Find k most similar<br/>examples to query"]

    S -->|"Diversity"| DIV["📐 Max-Margin Selection"]
    DIV --> S2["Cover all classes<br/>maximize spread"]

    S -->|"Balanced"| BAL["⚖️ Stratified Sampling"]
    BAL --> S3["Equal examples<br/>per class"]

    S -->|"Random"| RND["🎲 Random Sampling"]
    RND --> S4["Baseline comparison"]

    S1 --> BEST["✅ Best: Similarity + Balance<br/>kNN per class"]
    S2 --> BEST
    S3 --> BEST

    style Q2 fill:#3498DB,color:#fff
    style S fill:#9B59B6,color:#fff
    style SIM fill:#8E44AD,color:#fff
    style DIV fill:#E67E22,color:#fff
    style BAL fill:#F39C12,color:#fff
    style RND fill:#7F8C8D,color:#fff
    style S1 fill:#00B4D8,color:#fff
    style S2 fill:#D35400,color:#fff
    style S3 fill:#D4AC0D,color:#fff
    style S4 fill:#95A5A6,color:#fff
    style BEST fill:#2ECC71,color:#fff
```

## 6. Prototypical Network Architecture

```mermaid
flowchart TB
    subgraph Support["📚 Support Set — 3 shots per class"]
        B1["🟢 Bullish Ex 1"] --> EB1["🔢 Embedding"]
        B2["🟢 Bullish Ex 2"] --> EB2["🔢 Embedding"]
        B3["🟢 Bullish Ex 3"] --> EB3["🔢 Embedding"]
        N1["🔴 Bearish Ex 1"] --> EN1["🔢 Embedding"]
        N2["🔴 Bearish Ex 2"] --> EN2["🔢 Embedding"]
        N3["🔴 Bearish Ex 3"] --> EN3["🔢 Embedding"]
    end

    EB1 & EB2 & EB3 --> PB["🟢 Prototype Bullish<br/>Mean Embedding"]
    EN1 & EN2 & EN3 --> PN["🔴 Prototype Bearish<br/>Mean Embedding"]

    subgraph Query["❓ Query"]
        QT["📄 New Text"] --> QE["🔢 Query Embedding"]
    end

    QE --> D1["📏 Distance to<br/>Bullish Prototype"]
    QE --> D2["📏 Distance to<br/>Bearish Prototype"]
    PB --> D1
    PN --> D2

    D1 --> CLS2{"🎯 Nearest Prototype"}
    D2 --> CLS2
    CLS2 --> PRED["✅ Prediction: Bullish"]

    style Support fill:#0f3460,color:#fff,stroke:#533483
    style Query fill:#1a1a2e,color:#fff,stroke:#e94560
    style PB fill:#2ECC71,color:#fff
    style PN fill:#E74C3C,color:#fff
    style PRED fill:#3498DB,color:#fff
    style D1 fill:#F39C12,color:#fff
    style D2 fill:#F39C12,color:#fff
    style CLS2 fill:#9B59B6,color:#fff
    style QT fill:#00B4D8,color:#fff
    style QE fill:#E67E22,color:#fff
```

## 7. Method Comparison Matrix

```mermaid
quadrantChart
    title Few-Shot Methods: Accuracy vs Data Efficiency
    x-axis "More Data Needed" --> "Less Data Needed"
    y-axis "Lower Accuracy" --> "Higher Accuracy"

    Full Fine-Tuning: [0.15, 0.95]
    SetFit: [0.65, 0.88]
    Few-Shot ICL: [0.75, 0.82]
    Prototypical Net: [0.70, 0.80]
    PET: [0.55, 0.85]
    Zero-Shot NLI: [0.95, 0.75]
    Zero-Shot LLM: [0.90, 0.78]
```

## 8. Cascade Classification System

```mermaid
flowchart TD
    INPUT["📄 Financial Document"] --> ZS2["🔵 Zero-Shot Classifier<br/>BART-MNLI"]
    ZS2 --> C1{"📊 Confidence ≥ 0.9?"}
    C1 -->|"✅ Yes"| R1["🟢 Return Result<br/>Cost: $0.001"]
    C1 -->|"❌ No"| FS2["🟣 Few-Shot ICL<br/>Claude Haiku + 5 examples"]
    FS2 --> C2{"📊 Confidence ≥ 0.8?"}
    C2 -->|"✅ Yes"| R2["🟡 Return Result<br/>Cost: $0.01"]
    C2 -->|"❌ No"| SF["🟠 SetFit Model<br/>Fine-tuned locally"]
    SF --> C3{"📊 Confidence ≥ 0.7?"}
    C3 -->|"✅ Yes"| R3["🟠 Return Result<br/>Cost: $0.0001"]
    C3 -->|"❌ No"| HUM["🔴 Human Review Queue"]

    R1 --> LOG["💾 Log to BigQuery<br/>for future training"]
    R2 --> LOG
    R3 --> LOG
    HUM --> LOG

    style INPUT fill:#3498DB,color:#fff
    style ZS2 fill:#2980B9,color:#fff
    style FS2 fill:#9B59B6,color:#fff
    style SF fill:#E67E22,color:#fff
    style R1 fill:#2ECC71,color:#fff
    style R2 fill:#F39C12,color:#fff
    style R3 fill:#D35400,color:#fff
    style HUM fill:#E74C3C,color:#fff
    style LOG fill:#1ABC9C,color:#fff
    style C1 fill:#00B4D8,color:#fff
    style C2 fill:#00B4D8,color:#fff
    style C3 fill:#00B4D8,color:#fff
```

## 9. Financial Few-Shot Trading Classifier

```mermaid
flowchart TD
    subgraph Ingest["📥 Data Ingestion"]
        HEADLINES["📰 NSE Headlines<br/>RSS + News API"]
        EARNINGS["📊 Earnings Calls<br/>BSE filings"]
    end

    subgraph Classify["🧠 Few-Shot Pipeline"]
        EMBED["🔢 Sentence-BERT<br/>all-MiniLM-L6-v2"]
        KNN["🔍 kNN Retriever<br/>8 labeled examples"]
        PROMPT_B["📝 Prompt Builder<br/>System + Few-Shot"]
        GEMINI["🌟 Gemini Flash<br/>Classification call"]
    end

    subgraph Signal["📊 Signal Output"]
        LABEL["🏷️ Label<br/>Bullish / Bearish / Neutral"]
        CONF["📊 Confidence<br/>0.0 - 1.0"]
        SYMBOL["🔗 Symbol Map<br/>Entity → NSE Ticker"]
        SIG["🚀 Trading Signal<br/>Direction + Size"]
    end

    HEADLINES & EARNINGS --> EMBED
    EMBED --> KNN --> PROMPT_B --> GEMINI
    GEMINI --> LABEL --> CONF --> SYMBOL --> SIG

    style Ingest fill:#0f3460,color:#fff,stroke:#533483
    style Classify fill:#1a1a2e,color:#fff,stroke:#e94560
    style Signal fill:#1a1a2e,color:#fff,stroke:#2ECC71
    style HEADLINES fill:#E74C3C,color:#fff
    style EARNINGS fill:#3498DB,color:#fff
    style EMBED fill:#9B59B6,color:#fff
    style KNN fill:#00B4D8,color:#fff
    style PROMPT_B fill:#E67E22,color:#fff
    style GEMINI fill:#F39C12,color:#fff
    style LABEL fill:#2ECC71,color:#fff
    style CONF fill:#27AE60,color:#fff
    style SYMBOL fill:#1ABC9C,color:#fff
    style SIG fill:#16A085,color:#fff
```

## 10. Learning Path

```mermaid
graph TD
    subgraph Week1["📗 Week 1: Foundations"]
        A1["🔵 Zero-shot with<br/>HuggingFace pipeline"]
        A2["🧠 NLI-based<br/>classification"]
        A3["🤖 LLM prompt-based<br/>zero-shot"]
    end

    subgraph Week2["📘 Week 2: Few-Shot Basics"]
        B1["📝 In-Context Learning<br/>with LLMs"]
        B2["🔍 Example selection<br/>strategies"]
        B3["🎯 SetFit for<br/>few-shot fine-tuning"]
    end

    subgraph Week3["📙 Week 3: Advanced"]
        C1["🧬 Prototypical Networks"]
        C2["📋 PET & Pattern-Based"]
        C3["📊 Confidence calibration"]
    end

    subgraph Week4["📕 Week 4: Production"]
        D1["🏗️ Cascade classifier<br/>system design"]
        D2["💰 Cost optimization<br/>routing"]
        D3["📈 Monitoring &<br/>active learning"]
    end

    Week1 --> Week2 --> Week3 --> Week4

    style Week1 fill:#2ECC71,color:#fff,stroke:#27AE60
    style Week2 fill:#3498DB,color:#fff,stroke:#2980B9
    style Week3 fill:#E67E22,color:#fff,stroke:#D35400
    style Week4 fill:#E74C3C,color:#fff,stroke:#C0392B
    style A1 fill:#27AE60,color:#fff
    style A2 fill:#27AE60,color:#fff
    style A3 fill:#27AE60,color:#fff
    style B1 fill:#2980B9,color:#fff
    style B2 fill:#2980B9,color:#fff
    style B3 fill:#2980B9,color:#fff
    style C1 fill:#D35400,color:#fff
    style C2 fill:#D35400,color:#fff
    style C3 fill:#D35400,color:#fff
    style D1 fill:#C0392B,color:#fff
    style D2 fill:#C0392B,color:#fff
    style D3 fill:#C0392B,color:#fff
```
