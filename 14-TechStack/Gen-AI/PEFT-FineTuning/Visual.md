# PEFT & Fine-Tuning: Visual Guide & Architecture Diagrams

## 1. PEFT Ecosystem Overview

```mermaid
graph TD
    PEFT["🔧 PEFT Library"]
    PEFT --> LORA["🔴 LoRA<br/>Low-Rank Adaptation"]
    PEFT --> QLORA["🟢 QLoRA<br/>4-bit + LoRA"]
    PEFT --> ADAPTER["🔵 Adapter Tuning<br/>Bottleneck FFN"]
    PEFT --> PREFIX["🟣 Prefix Tuning<br/>Virtual prefix tokens"]
    PEFT --> PROMPT["🟡 Prompt Tuning<br/>Soft prompt vectors"]
    PEFT --> DORA["🟠 DoRA<br/>Direction + Magnitude"]
    PEFT --> ADALORA["⚡ AdaLoRA<br/>Adaptive rank"]
    PEFT --> IA3["🔬 (IA)³<br/>Activation rescaling"]

    LORA --> TRL["🎓 TRL<br/>SFT / DPO / PPO"]
    QLORA --> BNB["📦 bitsandbytes<br/>4-bit quantization"]
    LORA --> VLLM["🚀 vLLM<br/>Multi-LoRA serving"]
    PEFT --> HUB["🌐 HF Hub<br/>100K+ adapters"]

    style PEFT fill:#F39C12,color:#fff,stroke:#D68910
    style LORA fill:#E74C3C,color:#fff
    style QLORA fill:#2ECC71,color:#fff
    style ADAPTER fill:#3498DB,color:#fff
    style PREFIX fill:#9B59B6,color:#fff
    style PROMPT fill:#F1C40F,color:#000
    style DORA fill:#E67E22,color:#fff
    style ADALORA fill:#00B4D8,color:#fff
    style IA3 fill:#1ABC9C,color:#fff
    style TRL fill:#27AE60,color:#fff
    style BNB fill:#16A085,color:#fff
    style VLLM fill:#C0392B,color:#fff
    style HUB fill:#8E44AD,color:#fff
```

## 2. LoRA Architecture — Inside a Transformer Layer

```mermaid
flowchart LR
    X["📥 Input x"] --> FROZEN["❄️ W₀ · x<br/>(Frozen, d×d)"]
    X --> A["🟢 A · x<br/>(Trained, r×d)"]
    A --> B["🟢 B · (Ax)<br/>(Trained, d×r)"]
    B --> SCALE["⚡ × α/r<br/>Scaling"]
    FROZEN --> SUM["⊕ Add"]
    SCALE --> SUM
    SUM --> OUT["📤 Output h"]

    style FROZEN fill:#E74C3C,color:#fff
    style A fill:#2ECC71,color:#fff
    style B fill:#2ECC71,color:#fff
    style SCALE fill:#F39C12,color:#fff
    style SUM fill:#3498DB,color:#fff
    style X fill:#9B59B6,color:#fff
    style OUT fill:#00B4D8,color:#fff
```

## 3. QLoRA Pipeline

```mermaid
flowchart TD
    BASE["🏗️ Base Model<br/>(LLaMA 70B, FP16)"] --> QUANT["📦 4-bit NF4 Quantization<br/>bitsandbytes<br/>140GB → 35GB"]
    QUANT --> PREP["⚙️ prepare_model_for_kbit_training()<br/>Enable gradients + checkpointing"]
    PREP --> LORA2["🔧 Apply LoRA adapters<br/>get_peft_model(model, config)<br/>Adapters in BF16, base in 4-bit"]
    LORA2 --> TRAIN["🏋️ SFTTrainer / Trainer<br/>Train only adapter weights"]
    TRAIN --> SAVE["💾 Save Adapter<br/>~50MB (not 140GB)"]
    SAVE --> MERGE["✅ Option A: merge_and_unload()<br/>Zero inference overhead"]
    SAVE --> SERVE["🚀 Option B: Load on-demand<br/>Multi-adapter serving"]

    style BASE fill:#9B59B6,color:#fff
    style QUANT fill:#F39C12,color:#fff
    style PREP fill:#3498DB,color:#fff
    style LORA2 fill:#2ECC71,color:#fff
    style TRAIN fill:#E74C3C,color:#fff
    style SAVE fill:#E67E22,color:#fff
    style MERGE fill:#27AE60,color:#fff
    style SERVE fill:#00B4D8,color:#fff
```

## 4. PEFT Method Placement in Transformer

```mermaid
flowchart TD
    INPUT["📥 Input Tokens"]
    INPUT --> EMB["🔢 Embedding Layer"]

    subgraph Block["🧠 Transformer Block (×N)"]
        LN1["📏 LayerNorm"] --> ATT["👁️ Self-Attention"]
        ATT --> LORA_ATT["🔴 ⊕ LoRA<br/>(on q,k,v,o projections)"]
        LORA_ATT --> ADD1["⊕ Residual"]

        ADD1 --> LN2["📏 LayerNorm"]
        LN2 --> FFN["⚡ Feed-Forward Network"]
        FFN --> LORA_FFN["🔴 ⊕ LoRA<br/>(on gate,up,down)"]
        LORA_FFN --> ADAPT["🔵 [Adapter Layer]<br/>Bottleneck FFN"]
        ADAPT --> ADD2["⊕ Residual"]
    end

    EMB --> PREFIX2["🟣 [Prefix Tokens]<br/>Virtual KV pairs"]
    PREFIX2 --> LN1

    EMB --> SOFT2["🟡 [Soft Prompt]<br/>Learned embeddings"]
    SOFT2 --> LN1

    style Block fill:#1a1a2e,color:#fff,stroke:#e94560
    style LORA_ATT fill:#E74C3C,color:#fff
    style LORA_FFN fill:#E74C3C,color:#fff
    style ADAPT fill:#3498DB,color:#fff
    style PREFIX2 fill:#9B59B6,color:#fff
    style SOFT2 fill:#F1C40F,color:#000
    style ATT fill:#E67E22,color:#fff
    style FFN fill:#00B4D8,color:#fff
    style EMB fill:#2ECC71,color:#fff
    style INPUT fill:#8E44AD,color:#fff
```

## 5. PEFT Method Decision Tree

```mermaid
flowchart TD
    START{"🤔 Choose PEFT Method"}
    START -->|"GPU < 24GB"| QLORA2["🟢 QLoRA<br/>4-bit + LoRA"]
    START -->|"GPU 24-80GB"| Q2{"🔍 Multi-task?"}
    START -->|"Budget unlimited"| FULL["🟡 Full Fine-Tuning"]

    Q2 -->|"Yes, modular"| ADAPTER2["🔵 Adapter Tuning"]
    Q2 -->|"No, single task"| LORA3["🔴 LoRA (r=16-64)"]

    LORA3 --> Q3{"🎯 Quality matters most?"}
    Q3 -->|"Yes"| DORA2["🟠 DoRA<br/>(direction + magnitude)"]
    Q3 -->|"Speed matters"| LORA4["🔴 LoRA standard"]

    style START fill:#9B59B6,color:#fff
    style QLORA2 fill:#2ECC71,color:#fff
    style Q2 fill:#3498DB,color:#fff
    style FULL fill:#F1C40F,color:#000
    style ADAPTER2 fill:#2980B9,color:#fff
    style LORA3 fill:#E74C3C,color:#fff
    style Q3 fill:#F39C12,color:#fff
    style DORA2 fill:#E67E22,color:#fff
    style LORA4 fill:#C0392B,color:#fff
```

## 6. Memory Comparison

```mermaid
xychart-beta
    title "GPU Memory Required (7B Model)"
    x-axis ["Full FT", "LoRA", "QLoRA", "Adapter", "Prefix", "Prompt"]
    y-axis "VRAM (GB)" 0 --> 60
    bar [56, 20, 12, 24, 14, 10]
```

## 7. Multi-Adapter Serving Architecture

```mermaid
flowchart LR
    subgraph Clients["🖥️ Clients"]
        C1["🏥 Medical App"]
        C2["⚖️ Legal App"]
        C3["💻 Coding App"]
    end

    subgraph Gateway["🚪 API Gateway"]
        ROUTER["🔀 Router<br/>(adapter selection<br/>based on API key)"]
    end

    subgraph Cluster["🚀 vLLM Cluster"]
        BASE2["🏗️ Base LLaMA-3.1-70B<br/>(shared, frozen)"]
        LA["🔴 LoRA: Medical<br/>50MB"]
        LB["🟢 LoRA: Legal<br/>50MB"]
        LC["🔵 LoRA: Coding<br/>80MB"]
    end

    C1 --> ROUTER
    C2 --> ROUTER
    C3 --> ROUTER
    ROUTER --> BASE2
    BASE2 --> LA
    BASE2 --> LB
    BASE2 --> LC

    style Clients fill:#0f3460,color:#fff,stroke:#533483
    style Gateway fill:#1a1a2e,color:#fff,stroke:#e94560
    style Cluster fill:#1a1a2e,color:#fff,stroke:#2ECC71
    style BASE2 fill:#9B59B6,color:#fff
    style LA fill:#E74C3C,color:#fff
    style LB fill:#2ECC71,color:#fff
    style LC fill:#3498DB,color:#fff
    style ROUTER fill:#F39C12,color:#fff
    style C1 fill:#E67E22,color:#fff
    style C2 fill:#00B4D8,color:#fff
    style C3 fill:#8E44AD,color:#fff
```

## 8. Training Pipeline

```mermaid
sequenceDiagram
    participant User as 👤 User
    participant DataPrep as 📊 DataPrep
    participant Quantize as 📦 Quantize
    participant PEFT2 as 🔧 PEFT
    participant Train2 as 🏋️ Train
    participant Eval as 📈 Eval
    participant Hub2 as 🌐 Hub

    User->>DataPrep: Upload instruction data
    DataPrep->>DataPrep: Clean, tokenize, format
    DataPrep->>Quantize: Load base model in 4-bit
    Quantize->>PEFT2: prepare_model_for_kbit_training()
    PEFT2->>PEFT2: get_peft_model(model, LoraConfig)
    PEFT2->>Train2: SFTTrainer.train()
    Train2->>Eval: Evaluate on held-out set
    Eval->>Hub2: Push adapter to HF Hub
    Hub2->>User: Adapter ready for inference
```

## 9. LoRA Rank vs Quality Tradeoff

```mermaid
xychart-beta
    title "LoRA Rank vs Quality (% of Full FT)"
    x-axis ["r=4", "r=8", "r=16", "r=32", "r=64", "r=128"]
    y-axis "Quality %" 70 --> 100
    line [78, 88, 93, 96, 97, 98]
```

## 10. Financial LoRA: Fine-Tuning for NSE Trading

```mermaid
flowchart TD
    subgraph Data["📥 Training Data"]
        SIGNALS["📊 Historical Signals<br/>100K labeled trades"]
        EARNINGS["📰 Earnings Analysis<br/>NSE company reports"]
        SENTIMENT["😊 Sentiment Labels<br/>Bullish / Bearish"]
    end

    subgraph Train_FT["🏋️ QLoRA Fine-Tuning"]
        BASE3["🏗️ Gemini Flash / LLaMA-8B<br/>Base model (4-bit)"]
        LORA5["🔴 LoRA r=32<br/>Target: q,k,v,o + FFN"]
        SFT["🎓 SFTTrainer<br/>3 epochs, lr=2e-4"]
    end

    subgraph Deploy_FT["🚀 Deployment"]
        MERGE2["🔗 Merge Adapter<br/>merge_and_unload()"]
        ENDPOINT["⚡ Cloud Run Endpoint<br/>sjarvis-llm-narrator"]
        SIGNAL_GEN["📡 Signal Narration<br/>Explain trade rationale"]
    end

    SIGNALS & EARNINGS & SENTIMENT --> BASE3
    BASE3 --> LORA5 --> SFT
    SFT --> MERGE2 --> ENDPOINT --> SIGNAL_GEN

    style Data fill:#0f3460,color:#fff,stroke:#533483
    style Train_FT fill:#1a1a2e,color:#fff,stroke:#e94560
    style Deploy_FT fill:#1a1a2e,color:#fff,stroke:#2ECC71
    style SIGNALS fill:#3498DB,color:#fff
    style EARNINGS fill:#E74C3C,color:#fff
    style SENTIMENT fill:#F39C12,color:#fff
    style BASE3 fill:#9B59B6,color:#fff
    style LORA5 fill:#E74C3C,color:#fff
    style SFT fill:#E67E22,color:#fff
    style MERGE2 fill:#2ECC71,color:#fff
    style ENDPOINT fill:#27AE60,color:#fff
    style SIGNAL_GEN fill:#1ABC9C,color:#fff
```

## 11. PEFT Comparison Matrix

```mermaid
graph TD
    subgraph Comparison["📊 Comparison"]
        T["⚙️ Feature"]
        T1["📏 Trainable %"]
        T2["🖥️ GPU (7B)"]
        T3["🎯 Quality"]
        T4["⚡ Inference Cost"]
        T5["🔀 Multi-task"]
    end

    subgraph LoRA_C["🔴 LoRA"]
        L1["0.01-1%"]
        L2["1× A100"]
        L3["~97%"]
        L4["Zero (merged)"]
        L5["Yes ✅"]
    end

    subgraph QLoRA_C["🟢 QLoRA"]
        Q1["0.01-1%"]
        Q2["1× 3090"]
        Q3["~93%"]
        Q4["Zero (merged)"]
        Q5["Yes ✅"]
    end

    subgraph Full_C["🟡 Full FT"]
        F1["100%"]
        F2["4× A100"]
        F3["100%"]
        F4["None"]
        F5["No ❌"]
    end

    style Comparison fill:#1a1a2e,color:#fff,stroke:#e94560
    style LoRA_C fill:#E74C3C,color:#fff
    style QLoRA_C fill:#2ECC71,color:#fff
    style Full_C fill:#F1C40F,color:#000
    style L3 fill:#27AE60,color:#fff
    style Q2 fill:#2ECC71,color:#fff
    style F3 fill:#F39C12,color:#fff
```

## 12. Learning Path

```mermaid
flowchart LR
    subgraph W12["📗 Week 1-2: Basics"]
        B1["📦 Pipeline API<br/>Load pretrained"]
        B2["🔴 LoRA basics<br/>LoraConfig + get_peft_model"]
        B1 --> B2
    end

    subgraph W34["📘 Week 3-4: Production"]
        I1["🟢 QLoRA training<br/>4-bit + SFTTrainer"]
        I2["🎓 DPO alignment<br/>Preference optimization"]
        I1 --> I2
    end

    subgraph W56["📙 Week 5-6: Scale"]
        A1["🚀 Multi-adapter serving<br/>vLLM + LoRA"]
        A2["🧠 RLHF pipeline<br/>SFT → RM → PPO"]
        A1 --> A2
    end

    B2 --> I1
    I2 --> A1

    style W12 fill:#2ECC71,color:#fff,stroke:#27AE60
    style W34 fill:#3498DB,color:#fff,stroke:#2980B9
    style W56 fill:#E74C3C,color:#fff,stroke:#C0392B
    style B1 fill:#27AE60,color:#fff
    style B2 fill:#27AE60,color:#fff
    style I1 fill:#2980B9,color:#fff
    style I2 fill:#2980B9,color:#fff
    style A1 fill:#C0392B,color:#fff
    style A2 fill:#C0392B,color:#fff
```
