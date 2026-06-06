# Inference Engines: Visual Guide & Architecture Diagrams

## Table of Contents
1. [Inference Engine Landscape](#inference-engine-landscape)
2. [vLLM Architecture](#vllm-architecture)
3. [PagedAttention](#pagedattention)
4. [Continuous Batching](#continuous-batching)
5. [Speculative Decoding](#speculative-decoding)
6. [Multi-GPU Inference](#multi-gpu-inference)
7. [Engine Comparison](#engine-comparison)
8. [Production Deployment](#production-deployment)
9. [Financial Trading Inference Pipeline](#financial-trading-inference-pipeline)
10. [Learning Path](#learning-path)

---

## Inference Engine Landscape

```mermaid
graph TD
    LLM["🧠 LLM Inference Engines"]

    LLM --> OS["🔓 Open Source"]
    LLM --> COMM["☁️ Commercial / Managed"]

    OS --> VLLM["🚀 vLLM<br/>PagedAttention<br/>UC Berkeley"]
    OS --> TGI["🤗 TGI<br/>HuggingFace<br/>Docker-native"]
    OS --> TRTLLM["⚡ TensorRT-LLM<br/>NVIDIA<br/>Max GPU perf"]
    OS --> SGLANG["📋 SGLang<br/>Stanford<br/>Structured gen"]
    OS --> DS["🔵 DeepSpeed-Inference<br/>Microsoft<br/>Multi-node"]
    OS --> LCPP["🦙 llama.cpp<br/>CPU / Apple<br/>GGUF format"]

    COMM --> ANTH["🟠 Anthropic API<br/>Claude"]
    COMM --> OAI["🟢 OpenAI API<br/>GPT-4"]
    COMM --> GEM["🔵 Google<br/>Gemini API"]
    COMM --> AWS2["🟡 AWS Bedrock<br/>Managed"]

    style LLM fill:#9B59B6,color:#fff,stroke:#8E44AD
    style OS fill:#2ECC71,color:#fff,stroke:#27AE60
    style COMM fill:#3498DB,color:#fff,stroke:#2980B9
    style VLLM fill:#1ABC9C,color:#fff
    style TGI fill:#F39C12,color:#fff
    style TRTLLM fill:#76B900,color:#fff
    style SGLANG fill:#E74C3C,color:#fff
    style DS fill:#0078D4,color:#fff
    style LCPP fill:#27AE60,color:#fff
    style ANTH fill:#D97706,color:#fff
    style OAI fill:#10A37F,color:#fff
    style GEM fill:#4285F4,color:#fff
    style AWS2 fill:#FF9900,color:#fff
```

---

## vLLM Architecture

```mermaid
flowchart TD
    REQ["📡 Incoming Requests<br/>(OpenAI-compatible API)"]

    REQ --> SCHED["🔄 Scheduler<br/>Continuous Batching"]
    SCHED --> PA["📄 PagedAttention Engine<br/>Non-contiguous KV Cache"]

    PA --> GPU["🎮 GPU Execution"]
    GPU --> TP["🔀 Tensor Parallelism<br/>(split across GPUs)"]
    GPU --> QUANT2["📦 Quantization<br/>AWQ / GPTQ / FP8"]
    GPU --> SPEC2["🔮 Speculative Decoding<br/>Draft + Verify"]

    TP --> KV["💾 KV Cache Manager<br/>Block Tables<br/>Memory Pool"]
    QUANT2 --> KV
    SPEC2 --> KV

    KV --> OUT2["📤 Token Streaming<br/>SSE / WebSocket"]
    OUT2 --> RESP["✅ Response<br/>(incremental tokens)"]

    subgraph Optimizations["⚡ Optimizations"]
        PC["💡 Prefix Caching<br/>Reuse shared prompts"]
        CB2["📐 Chunked Prefill<br/>Overlap prefill + decode"]
        FI["🔥 FlashInfer Kernels<br/>Fused attention ops"]
    end

    KV --> PC
    KV --> CB2
    KV --> FI

    style REQ fill:#3498DB,color:#fff
    style SCHED fill:#1ABC9C,color:#fff
    style PA fill:#E74C3C,color:#fff
    style GPU fill:#9B59B6,color:#fff
    style TP fill:#8E44AD,color:#fff
    style QUANT2 fill:#E67E22,color:#fff
    style SPEC2 fill:#00B4D8,color:#fff
    style KV fill:#F39C12,color:#fff
    style OUT2 fill:#2ECC71,color:#fff
    style RESP fill:#27AE60,color:#fff
    style Optimizations fill:#0f3460,color:#fff,stroke:#533483
    style PC fill:#3498DB,color:#fff
    style CB2 fill:#9B59B6,color:#fff
    style FI fill:#E74C3C,color:#fff
```

---

## PagedAttention

```mermaid
flowchart LR
    subgraph Traditional["❌ Traditional KV Cache (Wasteful)"]
        T1["🔴 Request 1<br/>[████████░░░░░░░░]<br/>50% waste"]
        T2["🔴 Request 2<br/>[████░░░░░░░░░░░░]<br/>75% waste"]
        T3["🔴 Request 3<br/>[██░░░░░░░░░░░░░░]<br/>87% waste"]
    end

    subgraph Paged["✅ PagedAttention (Efficient)"]
        POOL["🟢 Block Pool<br/>[B0][B1][B2][B3][B4][B5][B6][B7]"]
        BT1["🔵 Req 1 → B0,B1 (8 tok)"]
        BT2["🟣 Req 2 → B2 (4 tok)"]
        BT3["🟠 Req 3 → B3 (2 tok)"]
        BT4["⬜ Free: B4,B5,B6,B7"]
    end

    T1 --> |"Evolution"| POOL

    style Traditional fill:#1a1a2e,color:#fff,stroke:#E74C3C
    style Paged fill:#1a1a2e,color:#fff,stroke:#2ECC71
    style T1 fill:#C0392B,color:#fff
    style T2 fill:#C0392B,color:#fff
    style T3 fill:#C0392B,color:#fff
    style POOL fill:#27AE60,color:#fff
    style BT1 fill:#2980B9,color:#fff
    style BT2 fill:#8E44AD,color:#fff
    style BT3 fill:#E67E22,color:#fff
    style BT4 fill:#1ABC9C,color:#fff
```

---

## Continuous Batching

```mermaid
sequenceDiagram
    participant A as 📄 Request A (10 tok)
    participant B as 📄 Request B (50 tok)
    participant C as 📄 Request C (20 tok)
    participant GPU2 as 🎮 GPU Batch

    Note over GPU2: ❌ Static Batching
    A->>GPU2: Join batch
    B->>GPU2: Join batch
    GPU2->>GPU2: Process until BOTH done
    GPU2-->>A: Response (waited 40 extra tokens)
    GPU2-->>B: Response

    Note over GPU2: ✅ Continuous Batching
    A->>GPU2: Join batch
    B->>GPU2: Join batch
    GPU2-->>A: Done after 10 tokens (immediate return)
    C->>GPU2: Fill A's slot
    GPU2-->>C: Done after 20 tokens
    GPU2-->>B: Done after 50 tokens
```

---

## Speculative Decoding

```mermaid
flowchart TD
    subgraph Standard["🐢 Standard Autoregressive"]
        S1["Token 1<br/>1 forward pass"] --> S2["Token 2<br/>1 forward pass"]
        S2 --> S3["Token 3<br/>1 forward pass"]
        S3 --> S4["Token 4<br/>1 forward pass"]
        S4 --> S5["🔴 4 passes total<br/>= slow"]
    end

    subgraph Speculative["🚀 Speculative Decoding"]
        D2["⚡ Draft Model (8B)<br/>Generate 4 candidates<br/>1 fast pass"]
        D2 --> V2["🧠 Target Model (70B)<br/>Verify all 4 in parallel<br/>1 pass"]
        V2 --> ACC2["✅ Accept: tok1 ✅ tok2 ✅ tok3 ✅"]
        V2 --> REJ2["❌ Reject: tok4 → resample"]
        ACC2 --> RES2["🟢 2 passes instead of 4<br/>~2x speedup, zero quality loss"]
    end

    style Standard fill:#1a1a2e,color:#fff,stroke:#E74C3C
    style Speculative fill:#1a1a2e,color:#fff,stroke:#2ECC71
    style S5 fill:#C0392B,color:#fff
    style D2 fill:#1ABC9C,color:#fff
    style V2 fill:#E74C3C,color:#fff
    style ACC2 fill:#2ECC71,color:#fff
    style REJ2 fill:#E67E22,color:#fff
    style RES2 fill:#27AE60,color:#fff
```

---

## Multi-GPU Inference

```mermaid
graph TD
    subgraph TP["🔀 Tensor Parallelism (within node)"]
        M["🧠 Model Layer"]
        M --> G1["🎮 GPU 0<br/>Columns 0-2047"]
        M --> G2["🎮 GPU 1<br/>Columns 2048-4095"]
        M --> G3["🎮 GPU 2<br/>Columns 4096-6143"]
        M --> G4["🎮 GPU 3<br/>Columns 6144-8191"]
        G1 --> AR["🔗 All-Reduce<br/>Combine partial results"]
        G2 --> AR
        G3 --> AR
        G4 --> AR
    end

    subgraph PP["📏 Pipeline Parallelism (across nodes)"]
        PP1["🖥️ Node 1<br/>Layers 0-19"]
        PP2["🖥️ Node 2<br/>Layers 20-39"]
        PP3["🖥️ Node 3<br/>Layers 40-59"]
        PP4["🖥️ Node 4<br/>Layers 60-79"]
        PP1 --> PP2 --> PP3 --> PP4
    end

    subgraph DP["📊 Data Parallelism (replicas)"]
        R1["🔵 Replica 1 (TP=4)"]
        R2["🟢 Replica 2 (TP=4)"]
        R3["🟣 Replica 3 (TP=4)"]
        LB2["⚖️ Load Balancer"] --> R1
        LB2 --> R2
        LB2 --> R3
    end

    style TP fill:#0f3460,color:#fff,stroke:#533483
    style PP fill:#1a1a2e,color:#fff,stroke:#e94560
    style DP fill:#1a1a2e,color:#fff,stroke:#2ECC71
    style AR fill:#E74C3C,color:#fff
    style LB2 fill:#1ABC9C,color:#fff
    style M fill:#9B59B6,color:#fff
    style G1 fill:#3498DB,color:#fff
    style G2 fill:#2980B9,color:#fff
    style G3 fill:#00B4D8,color:#fff
    style G4 fill:#48CAE4,color:#fff
    style PP1 fill:#E67E22,color:#fff
    style PP2 fill:#D35400,color:#fff
    style PP3 fill:#E74C3C,color:#fff
    style PP4 fill:#C0392B,color:#fff
    style R1 fill:#2980B9,color:#fff
    style R2 fill:#2ECC71,color:#fff
    style R3 fill:#8E44AD,color:#fff
```

---

## Engine Comparison

```mermaid
xychart-beta
    title "Throughput Comparison (LLaMA 3.1 70B, H100)"
    x-axis ["vLLM", "TGI", "TensorRT-LLM", "SGLang", "DeepSpeed"]
    y-axis "Tokens/second" 0 --> 6000
    bar [4500, 3800, 5200, 4800, 3200]
```

| Engine | Best For | Key Feature |
|--------|---------|-------------|
| vLLM | General production | PagedAttention, easy setup |
| TGI | HuggingFace ecosystem | Docker-native, watermark |
| TensorRT-LLM | Max NVIDIA perf | Kernel fusion, FP8 |
| SGLang | Structured output | RadixAttention, JSON |
| DeepSpeed | Multi-node, huge models | ZeRO-Inference |
| llama.cpp | CPU / edge / Mac | GGUF, no GPU needed |

---

## Production Deployment

```mermaid
flowchart LR
    subgraph Client["🖥️ Client Layer"]
        APP2["📱 Application"]
        SDK2["📦 OpenAI SDK<br/>(compatible)"]
    end

    subgraph Routing["🚪 Routing Layer"]
        LB3["⚖️ Load Balancer<br/>(nginx / Envoy)"]
        RATE2["🛑 Rate Limiter"]
    end

    subgraph Inference["🚀 Inference Layer"]
        V1["🎮 vLLM Pod 1<br/>2×A100 TP=2"]
        V2["🎮 vLLM Pod 2<br/>2×A100 TP=2"]
        V3["🎮 vLLM Pod 3<br/>2×A100 TP=2"]
    end

    subgraph Monitor["📊 Monitoring"]
        PROM2["📈 Prometheus<br/>Metrics"]
        GRAF2["📊 Grafana<br/>Dashboards"]
        ALERT2["🚨 Alert Manager"]
    end

    APP2 --> SDK2 --> LB3 --> RATE2
    RATE2 --> V1 & V2 & V3
    V1 & V2 & V3 --> PROM2
    PROM2 --> GRAF2 --> ALERT2

    style Client fill:#0f3460,color:#fff,stroke:#533483
    style Routing fill:#1a1a2e,color:#fff,stroke:#e94560
    style Inference fill:#1a1a2e,color:#fff,stroke:#2ECC71
    style Monitor fill:#1a1a2e,color:#fff,stroke:#F39C12
    style APP2 fill:#3498DB,color:#fff
    style SDK2 fill:#2980B9,color:#fff
    style LB3 fill:#1ABC9C,color:#fff
    style RATE2 fill:#E74C3C,color:#fff
    style V1 fill:#E67E22,color:#fff
    style V2 fill:#E67E22,color:#fff
    style V3 fill:#E67E22,color:#fff
    style PROM2 fill:#F39C12,color:#fff
    style GRAF2 fill:#9B59B6,color:#fff
    style ALERT2 fill:#C0392B,color:#fff
```

---

## Financial Trading Inference Pipeline

```mermaid
flowchart TD
    subgraph Ingest2["📥 Market Data"]
        TICK["📊 NSE Ticks<br/>Real-time OHLCV"]
        NEWS2["📰 Financial News<br/>Headlines + Filings"]
    end

    subgraph Inference2["🧠 LLM Inference Layer"]
        ROUTER2["🔀 Model Router<br/>Complexity-based"]
        SMALL["⚡ Gemini Flash<br/>Simple sentiment<br/>Free tier (15 RPM)"]
        MEDIUM["🔵 Claude Haiku<br/>Signal narration<br/>$0.25/MTok"]
        LARGE["🟣 Claude Sonnet<br/>Complex analysis<br/>$3/MTok"]
    end

    subgraph Output2["📊 Trading Output"]
        SIGNAL2["📡 Trading Signal<br/>Direction + Confidence"]
        NARRATIVE["📝 Trade Narrative<br/>Why this trade?"]
        RISK2["🛡️ Risk Assessment<br/>Greeks + Exposure"]
    end

    TICK & NEWS2 --> ROUTER2
    ROUTER2 -->|"Simple"| SMALL
    ROUTER2 -->|"Moderate"| MEDIUM
    ROUTER2 -->|"Complex"| LARGE
    SMALL & MEDIUM & LARGE --> SIGNAL2 & NARRATIVE & RISK2

    style Ingest2 fill:#0f3460,color:#fff,stroke:#533483
    style Inference2 fill:#1a1a2e,color:#fff,stroke:#e94560
    style Output2 fill:#1a1a2e,color:#fff,stroke:#2ECC71
    style TICK fill:#3498DB,color:#fff
    style NEWS2 fill:#E74C3C,color:#fff
    style ROUTER2 fill:#F39C12,color:#fff
    style SMALL fill:#2ECC71,color:#fff
    style MEDIUM fill:#2980B9,color:#fff
    style LARGE fill:#8E44AD,color:#fff
    style SIGNAL2 fill:#27AE60,color:#fff
    style NARRATIVE fill:#E67E22,color:#fff
    style RISK2 fill:#E74C3C,color:#fff
```

---

## Learning Path

```mermaid
flowchart LR
    subgraph Beginner["📗 Beginner"]
        B1["🤗 HuggingFace pipeline()<br/>baseline inference"]
        B2["🦙 llama.cpp<br/>local CPU inference"]
        B3["🚀 vLLM basics<br/>LLM() + SamplingParams"]
    end

    subgraph Intermediate["📘 Intermediate"]
        I1["🌐 vLLM OpenAI server<br/>production serving"]
        I2["📦 Quantized models<br/>AWQ/GPTQ + vLLM"]
        I3["🐳 TGI Docker<br/>containerized serving"]
    end

    subgraph Advanced["📕 Advanced"]
        A1["⚡ TensorRT-LLM<br/>max performance"]
        A2["🔀 Multi-GPU TP/PP<br/>scale to 100B+"]
        A3["🔧 Custom configs<br/>speculative, prefix cache"]
    end

    B1 --> B2 --> B3 --> I1 --> I2 --> I3 --> A1 --> A2 --> A3

    style Beginner fill:#2ECC71,color:#fff,stroke:#27AE60
    style Intermediate fill:#3498DB,color:#fff,stroke:#2980B9
    style Advanced fill:#E74C3C,color:#fff,stroke:#C0392B
    style B1 fill:#27AE60,color:#fff
    style B2 fill:#27AE60,color:#fff
    style B3 fill:#27AE60,color:#fff
    style I1 fill:#2980B9,color:#fff
    style I2 fill:#2980B9,color:#fff
    style I3 fill:#2980B9,color:#fff
    style A1 fill:#C0392B,color:#fff
    style A2 fill:#C0392B,color:#fff
    style A3 fill:#C0392B,color:#fff
```
