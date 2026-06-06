# AI Guardrails: Visual Guide & Architecture Diagrams

## 1. Guardrail Pipeline Architecture

```mermaid
graph TD
    UI["👤 User Input"] --> IR["🛡️ Input Rails"]
    IR --> JB["🔒 Jailbreak<br/>Detector"]
    IR --> TC["🏷️ Topic<br/>Classifier"]
    IR --> PII["🔐 PII<br/>Redactor"]
    IR --> INJ["💉 Injection<br/>Scanner"]

    JB -->|"✅ Pass"| LLM["🧠 LLM Generation"]
    TC -->|"✅ Pass"| LLM
    PII -->|"✅ Pass"| LLM
    INJ -->|"✅ Pass"| LLM
    JB -->|"🚫 Block"| BLK["❌ Blocked Response"]
    TC -->|"🚫 Block"| BLK
    INJ -->|"🚫 Block"| BLK

    LLM --> OR["🛡️ Output Rails"]
    OR --> HAL["🔍 Hallucination<br/>Check"]
    OR --> TOX["⚠️ Toxicity<br/>Filter"]
    OR --> VAL["📋 Schema<br/>Validation"]
    OR --> SEBI["🏛️ SEBI<br/>Compliance"]
    OR --> AUD["📝 Audit<br/>Logger"]

    HAL -->|"✅ Pass"| RESP["✅ Safe Response"]
    TOX -->|"✅ Pass"| RESP
    VAL -->|"✅ Pass"| RESP
    HAL -->|"❌ Fail"| BLK
    SEBI -->|"❌ Fail"| BLK

    style UI fill:#3498DB,color:#fff
    style IR fill:#00B4D8,color:#fff,stroke:#0096C7
    style OR fill:#E63946,color:#fff,stroke:#D62828
    style LLM fill:#9B59B6,color:#fff,stroke:#8E44AD
    style BLK fill:#C0392B,color:#fff,stroke:#922B21
    style RESP fill:#2ECC71,color:#fff,stroke:#27AE60
    style JB fill:#48CAE4,color:#fff
    style TC fill:#48CAE4,color:#fff
    style PII fill:#48CAE4,color:#fff
    style INJ fill:#48CAE4,color:#fff
    style HAL fill:#FF6B6B,color:#fff
    style TOX fill:#FF6B6B,color:#fff
    style VAL fill:#FF6B6B,color:#fff
    style SEBI fill:#FF6B6B,color:#fff
    style AUD fill:#FF6B6B,color:#fff
```

## 2. Defense-in-Depth Layers

```mermaid
graph TD
    subgraph L1["⚡ Layer 1: Fast Rules — < 1ms"]
        R1["📝 Regex Patterns<br/>SQL injection, XSS"]
        R2["🚫 Blocklist Match<br/>Banned words/topics"]
        R3["📏 Length Limits<br/>Max tokens, size"]
        R4["🔢 Rate Limiting<br/>Per-user throttle"]
    end

    subgraph L2["🤖 Layer 2: ML Classifiers — 5-20ms"]
        M1["🔒 Jailbreak Classifier<br/>BERT-based detector"]
        M2["🏷️ Topic Classifier<br/>Off-topic routing"]
        M3["👤 NER / PII<br/>Entity recognition"]
        M4["😡 Toxicity Scorer<br/>Perspective API"]
    end

    subgraph L3["🧠 Layer 3: LLM-Based — 200-2000ms"]
        F1["🔍 Self-Check Input<br/>Intent analysis"]
        F2["📊 Hallucination Detect<br/>Factual grounding"]
        F3["✅ Fact Verification<br/>Source cross-check"]
        F4["🏛️ Compliance Check<br/>SEBI/regulatory"]
    end

    L1 -->|"if passes"| L2
    L2 -->|"if passes"| L3

    style L1 fill:#2ECC71,color:#fff,stroke:#27AE60
    style L2 fill:#F39C12,color:#fff,stroke:#E67E22
    style L3 fill:#E74C3C,color:#fff,stroke:#C0392B
    style R1 fill:#27AE60,color:#fff
    style R2 fill:#27AE60,color:#fff
    style R3 fill:#27AE60,color:#fff
    style R4 fill:#27AE60,color:#fff
    style M1 fill:#E67E22,color:#fff
    style M2 fill:#E67E22,color:#fff
    style M3 fill:#E67E22,color:#fff
    style M4 fill:#E67E22,color:#fff
    style F1 fill:#C0392B,color:#fff
    style F2 fill:#C0392B,color:#fff
    style F3 fill:#C0392B,color:#fff
    style F4 fill:#C0392B,color:#fff
```

## 3. NeMo Guardrails Colang Flow

```mermaid
sequenceDiagram
    participant U as 👤 User
    participant IR as 🛡️ Input Rails
    participant CE as ⚙️ Colang Engine
    participant LLM as 🧠 LLM
    participant OR as 🛡️ Output Rails

    U->>IR: "How to hack a trading account?"
    IR->>CE: Classify intent
    CE->>CE: Match "jailbreak attempt" flow
    CE-->>U: "I cannot assist with that."
    Note right of CE: 🚫 LLM never called!

    U->>IR: "What's RELIANCE Q3 earnings?"
    IR->>CE: Classify intent
    CE->>CE: Match "financial query" flow
    CE->>LLM: Generate response (with rails context)
    LLM-->>OR: "RELIANCE Q3 revenue was ₹2.4L Cr..."
    OR->>OR: ✅ Hallucination check
    OR->>OR: ✅ Toxicity filter
    OR->>OR: ✅ SEBI compliance
    OR-->>U: "RELIANCE Q3 revenue: ₹2.4L Cr (verified)"
```

## 4. RAG Guardrail Flow

```mermaid
flowchart TD
    Q["📝 User Query"] --> RET["🔍 Retriever<br/>Vector Search"]
    RET --> DOCS["📄 Retrieved<br/>Documents"]
    DOCS --> RR["🛡️ Retrieval Rails"]

    RR --> REL{"📊 Relevance<br/>Score > 0.7?"}
    REL -->|"✅ Yes"| GROUND_Q["🔍 Check Query<br/>Groundable?"]
    REL -->|"❌ No"| FALLBACK["💬 Fallback:<br/>'No relevant info found'"]

    GROUND_Q --> GEN["🧠 LLM Generation<br/>with context"]
    GEN --> GROUND["📋 Groundedness<br/>Check"]
    GROUND -->|"✅ Grounded"| CITE["📎 Add Citations"]
    GROUND -->|"❌ Hallucinated"| REGEN["🔄 Regenerate<br/>Stricter prompt"]
    REGEN --> GEN

    CITE --> OUT["✅ Response<br/>+ Source Citations"]

    style Q fill:#3498DB,color:#fff
    style RET fill:#9B59B6,color:#fff
    style RR fill:#00B4D8,color:#fff
    style REL fill:#F39C12,color:#fff
    style GEN fill:#8E44AD,color:#fff
    style GROUND fill:#E74C3C,color:#fff
    style OUT fill:#2ECC71,color:#fff,stroke:#27AE60
    style FALLBACK fill:#95A5A6,color:#fff
    style CITE fill:#1ABC9C,color:#fff
    style REGEN fill:#E67E22,color:#fff
```

## 5. PII Protection Flow

```mermaid
flowchart LR
    IN["📨 Raw Input<br/>'Email: john@ex.com<br/>PAN: ABCDE1234F<br/>Aadhaar: 1234-5678-9012'"]
    IN --> DETECT["🔍 PII Detector<br/>(Presidio / Regex)"]

    DETECT --> E1["📧 EMAIL<br/>john@ex.com"]
    DETECT --> E2["🪪 PAN<br/>ABCDE1234F"]
    DETECT --> E3["🆔 AADHAAR<br/>1234-5678-9012"]

    E1 --> STRAT{"🔀 Strategy?"}
    E2 --> STRAT
    E3 --> STRAT

    STRAT -->|"Redact"| RED["[REDACTED]"]
    STRAT -->|"Mask"| MASK["john@[MASKED]<br/>ABCD****34F"]
    STRAT -->|"Encrypt"| ENC["🔒 Encrypted Vault"]

    RED --> LLM["🧠 LLM processes<br/>sanitized text"]
    MASK --> LLM
    ENC --> LLM

    style IN fill:#3498DB,color:#fff
    style DETECT fill:#E74C3C,color:#fff
    style E1 fill:#F39C12,color:#fff
    style E2 fill:#F39C12,color:#fff
    style E3 fill:#F39C12,color:#fff
    style STRAT fill:#9B59B6,color:#fff
    style RED fill:#2ECC71,color:#fff
    style MASK fill:#27AE60,color:#fff
    style ENC fill:#1ABC9C,color:#fff
    style LLM fill:#8E44AD,color:#fff
```

## 6. Framework Comparison

```mermaid
graph TB
    subgraph CMP["🔍 Guardrails Framework Comparison"]
        direction LR
        subgraph NM["🟢 NeMo Guardrails"]
            N1["Colang 2.0 DSL"]
            N2["Dialog + Topic Rails"]
            N3["Multi-modal support"]
            N4["NVIDIA backed"]
        end

        subgraph GA["🔵 Guardrails AI"]
            G1["Validator Hub (100+)"]
            G2["Pydantic structured output"]
            G3["On-fail strategies"]
            G4["Open source + cloud"]
        end

        subgraph LL["🟣 Llama Guard"]
            L1["Fine-tuned safety model"]
            L2["Multi-category taxonomy"]
            L3["Open source (Meta)"]
            L4["Fast inference"]
        end

        subgraph AZ["🔷 Azure AI Safety"]
            A1["Cloud API"]
            A2["Multi-modal safety"]
            A3["Severity scoring 0-7"]
            A4["Jailbreak detection"]
        end
    end

    style CMP fill:#1a1a2e,color:#fff,stroke:#e94560
    style NM fill:#76B900,color:#fff
    style GA fill:#00B4D8,color:#fff
    style LL fill:#9B59B6,color:#fff
    style AZ fill:#0078D4,color:#fff
    style N1 fill:#5A9E00,color:#fff
    style N2 fill:#5A9E00,color:#fff
    style N3 fill:#5A9E00,color:#fff
    style N4 fill:#5A9E00,color:#fff
    style G1 fill:#0096C7,color:#fff
    style G2 fill:#0096C7,color:#fff
    style G3 fill:#0096C7,color:#fff
    style G4 fill:#0096C7,color:#fff
    style L1 fill:#8E44AD,color:#fff
    style L2 fill:#8E44AD,color:#fff
    style L3 fill:#8E44AD,color:#fff
    style L4 fill:#8E44AD,color:#fff
    style A1 fill:#005A9E,color:#fff
    style A2 fill:#005A9E,color:#fff
    style A3 fill:#005A9E,color:#fff
    style A4 fill:#005A9E,color:#fff
```

## 7. SEBI Compliance Guardrail for Trading

```mermaid
flowchart TD
    SIG["📊 Trading Signal<br/>BUY RELIANCE 100 shares"] --> CHAIN["🔗 Guardrail Chain"]

    CHAIN --> P1["📏 Position Limit<br/>Max 5% per stock"]
    CHAIN --> P2["🏢 Sector Limit<br/>Max 25% per sector"]
    CHAIN --> P3["⏰ Trading Hours<br/>09:15-15:30 IST"]
    CHAIN --> P4["🏛️ SEBI Restricted<br/>Insider trading check"]
    CHAIN --> P5["💰 Margin Requirement<br/>Sufficient collateral"]

    P1 -->|"✅"| AGG{"All Pass?"}
    P2 -->|"✅"| AGG
    P3 -->|"✅"| AGG
    P4 -->|"✅"| AGG
    P5 -->|"✅"| AGG

    AGG -->|"All ✅"| EXEC["⚡ Execute Order"]
    AGG -->|"Any ❌"| REJECT["🚫 Reject + Log<br/>Reason + Audit Trail"]

    EXEC --> AUDIT["📝 Audit Log<br/>BigQuery 8yr retention"]
    REJECT --> AUDIT

    style SIG fill:#3498DB,color:#fff
    style CHAIN fill:#9B59B6,color:#fff
    style P1 fill:#E67E22,color:#fff
    style P2 fill:#E67E22,color:#fff
    style P3 fill:#E67E22,color:#fff
    style P4 fill:#E67E22,color:#fff
    style P5 fill:#E67E22,color:#fff
    style AGG fill:#F39C12,color:#fff
    style EXEC fill:#2ECC71,color:#fff
    style REJECT fill:#E74C3C,color:#fff
    style AUDIT fill:#1ABC9C,color:#fff
```

## 8. Monitoring & Red Teaming Dashboard

```mermaid
graph TD
    subgraph METRICS["📊 Guardrail Metrics Pipeline"]
        LOG["📝 Guardrail Logs"] --> AGG["📈 Time-Series<br/>Aggregation"]
        AGG --> TPR["✅ True Positive Rate<br/>Attack Detection: 98%"]
        AGG --> FPR["⚠️ False Positive Rate<br/>Overblocking: 1.2%"]
        AGG --> LAT["⏱️ Latency Overhead<br/>P99: 45ms"]
        AGG --> VOL["📊 Trigger Volume<br/>2.3K/day"]
    end

    TPR --> A1{"TPR < 95%?"}
    FPR --> A2{"FPR > 2%?"}
    LAT --> A3{"P99 > 100ms?"}

    A1 -->|"🚨 Yes"| ALARM["🚨 Update Rules<br/>Retrain classifiers"]
    A2 -->|"🚨 Yes"| TUNE["⚙️ Tune Sensitivity<br/>Adjust thresholds"]
    A3 -->|"🚨 Yes"| OPT["⚡ Optimize<br/>Cache, batch, prune"]

    style METRICS fill:#1a1a2e,color:#fff,stroke:#e94560
    style LOG fill:#3498DB,color:#fff
    style AGG fill:#9B59B6,color:#fff
    style TPR fill:#2ECC71,color:#fff
    style FPR fill:#F39C12,color:#fff
    style LAT fill:#E67E22,color:#fff
    style VOL fill:#3498DB,color:#fff
    style ALARM fill:#E74C3C,color:#fff
    style TUNE fill:#E67E22,color:#fff
    style OPT fill:#F39C12,color:#fff
    style A1 fill:#8E44AD,color:#fff
    style A2 fill:#8E44AD,color:#fff
    style A3 fill:#8E44AD,color:#fff
```

## 9. Learning Path

```mermaid
graph TD
    subgraph W1["📗 Week 1: Foundations"]
        B1["🔍 Understand Risks<br/>Hallucination, injection, PII"]
        B2["📋 Basic Validation<br/>Pydantic + regex"]
        B3["🛡️ Guardrails AI<br/>Validator Hub"]
    end

    subgraph W2["📘 Week 2: NeMo Guardrails"]
        I1["📝 Colang DSL<br/>Dialog flows"]
        I2["🔒 Input/Output Rails<br/>Topic + safety"]
        I3["🔗 RAG Integration<br/>Retrieval rails"]
    end

    subgraph W3["📙 Week 3: Production"]
        A1["🔐 PII Detection<br/>Presidio + custom"]
        A2["🏛️ Compliance Rails<br/>SEBI, regulatory"]
        A3["🔴 Red Teaming<br/>Adversarial testing"]
    end

    subgraph W4["📕 Week 4: Scale"]
        P1["📊 Monitoring<br/>Metrics dashboard"]
        P2["⚡ Optimization<br/>Latency, caching"]
        P3["🏭 Enterprise<br/>Multi-model safety"]
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
