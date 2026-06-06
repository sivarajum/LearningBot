# Hugging Face: Visual Guide & Architecture Diagrams

## Table of Contents
1. [Ecosystem Overview](#ecosystem-overview)
2. [Transformers Library Architecture](#transformers-library-architecture)
3. [PEFT — Fine-Tuning Methods](#peft--fine-tuning-methods)
4. [LoRA Mathematical Flow](#lora-mathematical-flow)
5. [QLoRA Architecture](#qlora-architecture)
6. [RLHF Training Pipeline](#rlhf-training-pipeline)
7. [Pipeline API Flow](#pipeline-api-flow)
8. [Training with Trainer API](#training-with-trainer-api)
9. [Distributed Training Architecture](#distributed-training-architecture)
10. [Model Hub Workflow](#model-hub-workflow)
11. [PEFT Methods Comparison](#peft-methods-comparison)
12. [Financial Sentiment with HuggingFace](#financial-sentiment-with-huggingface)
13. [Learning Path](#learning-path)

---

## Ecosystem Overview

```mermaid
graph TD
    HF["🤗 Hugging Face"]

    HF --> Hub["🌐 Hub<br/>1M+ Model Checkpoints<br/>100K+ Datasets"]
    HF --> Libs["📚 Core Libraries"]
    HF --> Infra["🚀 Deployment / Infra"]

    Libs --> L1["🔄 transformers<br/>Architectures, Pipelines, Trainer"]
    Libs --> L2["🎯 peft<br/>LoRA, QLoRA, Adapters"]
    Libs --> L3["📊 datasets<br/>100K+ datasets, Arrow"]
    Libs --> L4["⚡ accelerate<br/>Multi-GPU, DeepSpeed, FSDP"]
    Libs --> L5["🎮 trl<br/>RLHF, PPO, SFT, DPO"]
    Libs --> L6["📏 evaluate<br/>ROUGE, BLEU, BERTScore"]
    Libs --> L7["✂️ tokenizers<br/>Rust-based fast"]
    Libs --> L8["🎨 diffusers<br/>Stable Diffusion, DALL-E"]

    Infra --> I1["☁️ Inference API<br/>Managed hosting"]
    Infra --> I2["🎮 Inference Endpoints<br/>Dedicated GPU"]
    Infra --> I3["🖥️ Spaces<br/>Gradio / Streamlit"]
    Infra --> I4["🤖 AutoTrain<br/>No-code fine-tuning"]

    style HF fill:#F39C12,color:#fff,stroke:#E67E22
    style Libs fill:#E74C3C,color:#fff,stroke:#C0392B
    style Hub fill:#1ABC9C,color:#fff,stroke:#16A085
    style Infra fill:#3498DB,color:#fff,stroke:#2980B9
    style L1 fill:#2ECC71,color:#fff
    style L2 fill:#9B59B6,color:#fff
    style L3 fill:#E67E22,color:#fff
    style L4 fill:#00B4D8,color:#fff
    style L5 fill:#E74C3C,color:#fff
    style L6 fill:#27AE60,color:#fff
    style L7 fill:#8E44AD,color:#fff
    style L8 fill:#D35400,color:#fff
    style I1 fill:#2980B9,color:#fff
    style I2 fill:#1ABC9C,color:#fff
    style I3 fill:#F39C12,color:#fff
    style I4 fill:#E74C3C,color:#fff
```

---

## Transformers Library Architecture

```mermaid
graph TD
    U["👤 User Request"] --> P["🔧 Pipeline API<br/>highest-level abstraction"]
    U --> T["🏋️ Trainer API<br/>training abstraction"]
    U --> R["🔬 Raw Model + Tokenizer<br/>full control"]

    P --> PP["✂️ Pre-processing<br/>Tokenizer → Tensors"]
    T --> PP
    R --> PP

    PP --> M["🧠 Model Architecture Classes"]

    M --> A1["📝 AutoModelForCausalLM"]
    M --> A2["🏷️ AutoModelForSeqClassification"]
    M --> A3["❓ AutoModelForQA"]
    M --> A4["🔖 AutoModelForTokenClassification"]
    M --> A5["📦 AutoModel (raw)"]

    A1 --> BK["🧱 Backbone<br/>Transformer Blocks"]
    A2 --> BK
    A3 --> BK

    BK --> ATT["👁️ Self-Attention<br/>Multi-head attention"]
    BK --> FFN["⚡ Feed-Forward Network<br/>(MLP)"]
    BK --> LN["📏 Layer Normalization"]

    FFN --> OUT2["📤 Output"]
    OUT2 --> POST["🎯 Post-processing<br/>Output Parser → Structured Result"]

    style U fill:#3498DB,color:#fff,stroke:#2980B9
    style P fill:#1ABC9C,color:#fff,stroke:#16A085
    style T fill:#E74C3C,color:#fff,stroke:#C0392B
    style R fill:#9B59B6,color:#fff,stroke:#8E44AD
    style PP fill:#F39C12,color:#fff
    style M fill:#8E44AD,color:#fff
    style BK fill:#0f3460,color:#fff,stroke:#533483
    style ATT fill:#E74C3C,color:#fff
    style FFN fill:#E67E22,color:#fff
    style LN fill:#2ECC71,color:#fff
    style OUT2 fill:#27AE60,color:#fff
    style POST fill:#1ABC9C,color:#fff
    style A1 fill:#2980B9,color:#fff
    style A2 fill:#2980B9,color:#fff
    style A3 fill:#2980B9,color:#fff
    style A4 fill:#2980B9,color:#fff
    style A5 fill:#2980B9,color:#fff
```

---

## PEFT — Fine-Tuning Methods

```mermaid
graph LR
    subgraph Frozen["🧊 Base Model (FROZEN)"]
        W["🔴 Weight Matrix W<br/>d × d<br/>(NEVER updated)"]
    end

    subgraph Adapter["🎯 LoRA Adapter (TRAINED &lt;1%)"]
        B["🟢 Matrix B<br/>d × r"]
        A["🟢 Matrix A<br/>r × d"]
        B --> BA["⊗ ΔW = B × A<br/>Low-rank update"]
    end

    subgraph Infer["🚀 Inference"]
        W --> MERGE["⊕ W_eff = W + (α/r)·ΔW"]
        BA --> MERGE
        MERGE --> OUT3["✅ Output<br/>(zero overhead after merge)"]
    end

    style Frozen fill:#1a1a2e,color:#fff,stroke:#E74C3C
    style Adapter fill:#1a1a2e,color:#fff,stroke:#2ECC71
    style Infer fill:#1a1a2e,color:#fff,stroke:#3498DB
    style W fill:#E74C3C,color:#fff
    style B fill:#2ECC71,color:#fff
    style A fill:#2ECC71,color:#fff
    style BA fill:#F39C12,color:#fff
    style MERGE fill:#1ABC9C,color:#fff
    style OUT3 fill:#27AE60,color:#fff
```

---

## LoRA Mathematical Flow

```mermaid
flowchart TD
    INPUT["📥 Input x<br/>(batch × seq × d_model)"]

    INPUT --> FROZEN["❄️ W₀ · x<br/>(frozen pre-trained weights)<br/>Full rank: d × d"]
    INPUT --> LORA_A["🟢 A · x<br/>(LoRA matrix A)<br/>Shape: r × d, r=16"]

    LORA_A --> LORA_B["🟢 B · (Ax)<br/>(LoRA matrix B)<br/>Shape: d × r"]

    FROZEN --> ADD["⊕ Sum<br/>h = W₀x + (α/r)·BAx"]
    LORA_B --> SCALE["📐 Scale by α/r<br/>(α=32, r=16 → ×2)"]
    SCALE --> ADD

    ADD --> OUTPUT2["📤 Output h<br/>Same shape as W₀x"]

    subgraph Memory["💾 Memory Comparison"]
        FM["🔴 Full Fine-tune<br/>7B params × 8B = 56GB"]
        LM["🟢 LoRA Fine-tune<br/>0.06% params = 0.03GB"]
    end

    style INPUT fill:#3498DB,color:#fff
    style FROZEN fill:#E74C3C,color:#fff
    style LORA_A fill:#2ECC71,color:#fff
    style LORA_B fill:#2ECC71,color:#fff
    style ADD fill:#1ABC9C,color:#fff
    style SCALE fill:#F39C12,color:#fff
    style OUTPUT2 fill:#27AE60,color:#fff
    style Memory fill:#1a1a2e,color:#fff,stroke:#e94560
    style FM fill:#C0392B,color:#fff
    style LM fill:#27AE60,color:#fff
```

---

## QLoRA Architecture

```mermaid
flowchart TD
    BASE["🧠 Base Model<br/>(e.g. LLaMA 3.1 70B)"]

    BASE --> Q4["📦 4-bit NF4 Quantization<br/>bitsandbytes<br/>87% memory reduction"]

    Q4 --> PREP["🔧 prepare_model_for_kbit_training()<br/>Gradient checkpointing<br/>Enable input grad"]

    PREP --> LORA2["🎯 Wrap with LoRA (PEFT)<br/>get_peft_model(model, config)<br/>Adapters in BF16"]

    LORA2 --> TRAIN2["🏋️ SFTTrainer / Trainer<br/>Only LoRA adapters updated<br/>Base weights frozen in 4-bit"]

    TRAIN2 --> SAVE2["💾 Save Adapter Only<br/>model.save_pretrained()<br/>~50MB instead of 140GB"]

    SAVE2 --> DEPLOY2["🚀 Deployment Options"]
    DEPLOY2 --> OPT1["🔗 Merge adapter<br/>merge_and_unload()"]
    DEPLOY2 --> OPT2["📥 Load on-demand<br/>PeftModel.from_pretrained()"]
    DEPLOY2 --> OPT3["🌐 Stack on Hub<br/>Base + multiple adapters"]

    subgraph GPUReq["🎮 GPU Requirements"]
        FT2["🔴 Full Fine-tune 70B<br/>8× A100 (640GB)"]
        QL2["🟡 QLoRA 70B<br/>1× A100 (80GB)"]
        QLQ2["🟢 QLoRA 7B<br/>1× RTX 3090 (24GB)"]
    end

    style BASE fill:#9B59B6,color:#fff
    style Q4 fill:#F39C12,color:#fff
    style PREP fill:#E67E22,color:#fff
    style LORA2 fill:#1ABC9C,color:#fff
    style TRAIN2 fill:#E74C3C,color:#fff
    style SAVE2 fill:#2ECC71,color:#fff
    style DEPLOY2 fill:#3498DB,color:#fff
    style OPT1 fill:#2980B9,color:#fff
    style OPT2 fill:#00B4D8,color:#fff
    style OPT3 fill:#48CAE4,color:#fff
    style GPUReq fill:#1a1a2e,color:#fff,stroke:#e94560
    style FT2 fill:#C0392B,color:#fff
    style QL2 fill:#E67E22,color:#fff
    style QLQ2 fill:#27AE60,color:#fff
```

---

## RLHF Training Pipeline

```mermaid
flowchart TD
    subgraph Stage1["📗 Stage 1: SFT — Supervised Fine-Tuning"]
        D1["📝 Curated Demonstrations<br/>(human-written Q&A)"]
        D1 --> SFT2["🏋️ SFTTrainer<br/>(trl library)<br/>Fine-tune base LLM"]
        SFT2 --> SFT_M2["✅ SFT Model<br/>follows instructions"]
    end

    subgraph Stage2["📘 Stage 2: Reward Model"]
        D2["⚖️ Preference Dataset<br/>chosen vs rejected pairs"]
        SFT_M2 --> RM_BASE2["🔄 Initialize from SFT"]
        D2 --> RM_BASE2
        RM_BASE2 --> RM2["🎯 Reward Model<br/>Outputs scalar reward"]
    end

    subgraph Stage3["📕 Stage 3: PPO Fine-Tuning"]
        SFT_M2 --> POLICY2["🎮 Policy Model<br/>(starts from SFT)"]
        SFT_M2 --> REF2["❄️ Reference Model<br/>(frozen SFT copy)"]

        PROMPT2["💬 User Prompts"] --> POLICY2
        POLICY2 --> RESP2["📝 Generated Response"]
        RESP2 --> RM2
        RM2 --> REWARD2["⭐ Reward r(x,y)"]

        REF2 --> KL2["📐 KL Penalty<br/>prevent reward hacking"]
        REWARD2 --> TOTAL2["🏆 Total Reward<br/>r(x,y) - β·KL(π||π_ref)"]
        KL2 --> TOTAL2

        TOTAL2 --> PPO2["🔄 PPO Update"]
        PPO2 --> POLICY2
    end

    style Stage1 fill:#0f3460,color:#fff,stroke:#2ECC71
    style Stage2 fill:#1a1a2e,color:#fff,stroke:#3498DB
    style Stage3 fill:#1a1a2e,color:#fff,stroke:#E74C3C
    style SFT2 fill:#1ABC9C,color:#fff
    style RM2 fill:#E74C3C,color:#fff
    style POLICY2 fill:#2ECC71,color:#fff
    style REF2 fill:#3498DB,color:#fff
    style TOTAL2 fill:#F39C12,color:#fff
    style PPO2 fill:#9B59B6,color:#fff
    style REWARD2 fill:#E67E22,color:#fff
    style KL2 fill:#8E44AD,color:#fff
```

---

## Pipeline API Flow

```mermaid
sequenceDiagram
    participant U2 as 👤 User
    participant P2 as 🔧 Pipeline
    participant T2 as ✂️ Tokenizer
    participant M2 as 🧠 Model
    participant PP2 as 🎯 PostProcessor

    U2->>P2: pipeline("task", model="name")
    P2->>T2: AutoTokenizer.from_pretrained()
    P2->>M2: AutoModelForXxx.from_pretrained()

    U2->>P2: pipe(raw_input)
    P2->>T2: tokenize(raw_input)
    T2-->>P2: input_ids, attention_mask

    P2->>M2: forward(input_ids)
    M2-->>P2: logits / hidden_states

    P2->>PP2: decode / argmax / extract
    PP2-->>U2: [{label, score, ...}]
```

---

## Training with Trainer API

```mermaid
flowchart LR
    subgraph Setup2["🛠️ Setup"]
        M3["🧠 Model<br/>AutoModelForXxx"]
        T3["✂️ Tokenizer<br/>+ DataCollator"]
        D3["📊 Datasets<br/>train/eval"]
        A3["⚙️ TrainingArguments<br/>lr, epochs, fp16"]
        MT3["📏 compute_metrics()"]
    end

    subgraph Trainer2["🏋️ Trainer"]
        TR2["🔄 Trainer(<br/>model, args,<br/>train_dataset,<br/>eval_dataset)"]
    end

    subgraph Loop2["🔁 Training Loop"]
        TL2["⚡ Train Loop<br/>gradient accumulation"]
        EV2["📊 Eval Loop<br/>every N steps"]
        CK2["💾 Checkpoint<br/>best model saved"]
        LG2["📈 Logging<br/>WandB / TensorBoard"]
    end

    M3 --> TR2
    T3 --> TR2
    D3 --> TR2
    A3 --> TR2
    MT3 --> TR2

    TR2 --> TL2
    TL2 --> EV2
    EV2 --> CK2
    TL2 --> LG2

    style Setup2 fill:#0f3460,color:#fff,stroke:#533483
    style Trainer2 fill:#1a1a2e,color:#fff,stroke:#e94560
    style Loop2 fill:#1a1a2e,color:#fff,stroke:#2ECC71
    style TR2 fill:#9B59B6,color:#fff
    style TL2 fill:#E74C3C,color:#fff
    style CK2 fill:#2ECC71,color:#fff
    style LG2 fill:#F39C12,color:#fff
    style M3 fill:#3498DB,color:#fff
    style T3 fill:#1ABC9C,color:#fff
    style D3 fill:#E67E22,color:#fff
    style A3 fill:#8E44AD,color:#fff
```

---

## Distributed Training Architecture

```mermaid
graph TD
    subgraph DDP["📡 Single Machine Multi-GPU (DDP)"]
        G1["🎮 GPU 0<br/>Full Model Copy"]
        G2["🎮 GPU 1<br/>Full Model Copy"]
        G3["🎮 GPU 2<br/>Full Model Copy"]
        G4["🎮 GPU 3<br/>Full Model Copy"]

        G1 --> ALL_REDUCE2["🔗 All-Reduce<br/>Sync Gradients"]
        G2 --> ALL_REDUCE2
        G3 --> ALL_REDUCE2
        G4 --> ALL_REDUCE2
    end

    subgraph ZERO["🔀 DeepSpeed ZeRO Stage 3 (Sharded)"]
        ZG1["🎮 GPU 0<br/>1/4 Params+Grads+Optim"]
        ZG2["🎮 GPU 1<br/>1/4 Params+Grads+Optim"]
        ZG3["🎮 GPU 2<br/>1/4 Params+Grads+Optim"]
        ZG4["🎮 GPU 3<br/>1/4 Params+Grads+Optim"]

        ZG1 --> GATHER2["📥 Gather Params<br/>for Forward/Backward"]
        ZG2 --> GATHER2
        ZG3 --> GATHER2
        ZG4 --> GATHER2
    end

    ACC2["⚡ Accelerate / DeepSpeed<br/>One-line launch"] --> ALL_REDUCE2
    ACC2 --> GATHER2

    style DDP fill:#0f3460,color:#fff,stroke:#E74C3C
    style ZERO fill:#1a1a2e,color:#fff,stroke:#2ECC71
    style ALL_REDUCE2 fill:#E74C3C,color:#fff
    style GATHER2 fill:#1ABC9C,color:#fff
    style ACC2 fill:#9B59B6,color:#fff
    style G1 fill:#3498DB,color:#fff
    style G2 fill:#2980B9,color:#fff
    style G3 fill:#00B4D8,color:#fff
    style G4 fill:#48CAE4,color:#fff
    style ZG1 fill:#2ECC71,color:#fff
    style ZG2 fill:#27AE60,color:#fff
    style ZG3 fill:#1ABC9C,color:#fff
    style ZG4 fill:#16A085,color:#fff
```

---

## Model Hub Workflow

```mermaid
flowchart LR
    subgraph Dev["🛠️ Development"]
        TRAIN3["🏋️ Train / Fine-tune<br/>locally or Colab"]
        EVAL3["📊 Evaluate<br/>lm-eval-harness"]
        TRAIN3 --> EVAL3
    end

    subgraph HubOps["🌐 Hub Operations"]
        PUSH3["📤 push_to_hub()<br/>model + tokenizer + config"]
        CARD3["📄 Model Card<br/>biases, metrics, usage"]
        TAG3["🏷️ Tags & Metadata<br/>task, language, library"]
        PUSH3 --> CARD3
        CARD3 --> TAG3
    end

    subgraph Community["👥 Community Use"]
        DISC3["🔍 Discover<br/>huggingface.co"]
        LOAD3["📥 from_pretrained()<br/>3 lines to use"]
        PIPE3["🔧 pipeline(task, model=)"]
        DISC3 --> LOAD3
        LOAD3 --> PIPE3
    end

    subgraph Deploy3["🚀 Deployment"]
        IE3["🎮 Inference Endpoints<br/>Dedicated GPU"]
        TGI3["🐳 TGI Self-hosted<br/>Docker"]
        VLLM3["⚡ vLLM<br/>Production throughput"]
    end

    EVAL3 --> PUSH3
    TAG3 --> DISC3
    PIPE3 --> IE3
    PIPE3 --> TGI3
    PIPE3 --> VLLM3

    style Dev fill:#0f3460,color:#fff,stroke:#533483
    style HubOps fill:#1a1a2e,color:#fff,stroke:#F39C12
    style Community fill:#1a1a2e,color:#fff,stroke:#2ECC71
    style Deploy3 fill:#1a1a2e,color:#fff,stroke:#E74C3C
    style PUSH3 fill:#F39C12,color:#fff
    style LOAD3 fill:#1ABC9C,color:#fff
    style IE3 fill:#2ECC71,color:#fff
    style TGI3 fill:#E67E22,color:#fff
    style VLLM3 fill:#E74C3C,color:#fff
    style TRAIN3 fill:#3498DB,color:#fff
    style EVAL3 fill:#9B59B6,color:#fff
```

---

## PEFT Methods Comparison

```mermaid
graph TD
    subgraph Selector["🎯 PEFT Method Selector"]
        Q1{"🎮 GPU Memory<br/>Constraint?"}

        Q1 -->|"< 24GB"| QLORA3["📦 QLoRA<br/>4-bit + LoRA<br/>7B on RTX 3090"]
        Q1 -->|"24-80GB"| LORA3["🎯 LoRA<br/>Full precision<br/>7B on A100"]
        Q1 -->|"No constraint"| FT3["🏋️ Full Fine-Tuning<br/>best performance"]

        QLORA3 --> Q2{"🔀 Multi-task?"}
        LORA3 --> Q2

        Q2 -->|"Yes"| ADAPT3["🧩 Adapter Tuning<br/>Modular, composable"]
        Q2 -->|"No"| Q3{"📝 NLG task?"}

        Q3 -->|"Yes"| PREFIX3["📌 Prefix Tuning<br/>Soft prompts prepended"]
        Q3 -->|"Classification"| LORA4["🎯 LoRA standard<br/>Simplest & most popular"]
    end

    style Selector fill:#1a1a2e,color:#fff,stroke:#e94560
    style QLORA3 fill:#1ABC9C,color:#fff
    style LORA3 fill:#2ECC71,color:#fff
    style FT3 fill:#E74C3C,color:#fff
    style ADAPT3 fill:#F39C12,color:#fff
    style PREFIX3 fill:#9B59B6,color:#fff
    style LORA4 fill:#3498DB,color:#fff
    style Q1 fill:#8E44AD,color:#fff
    style Q2 fill:#E67E22,color:#fff
    style Q3 fill:#D35400,color:#fff
```

---

## Performance Characteristics

```mermaid
xychart-beta
    title "Memory vs Performance Trade-off"
    x-axis ["Full FT 70B", "LoRA 70B", "QLoRA 70B", "Prompt Tuning", "Prefix Tuning"]
    y-axis "GPU Memory (GB)" 0 --> 640
    bar [640, 160, 40, 10, 15]
```

| Technique | VRAM (70B model) | Performance vs Full FT | Train Time |
|-----------|-----------------|------------------------|-----------|
| Full Fine-Tuning | 640GB (8× A100) | 100% baseline | 100% baseline |
| LoRA (r=64) | 160GB (2× A100) | ~97% | ~40% |
| QLoRA (4-bit) | 40GB (1× A100) | ~93% | ~70% |
| Adapter Tuning | 80GB (1× A100) | ~95% | ~50% |
| Prefix Tuning | 40GB | ~85% | ~30% |
| Prompt Tuning | 40GB | ~78% | ~20% |

---

## Financial Sentiment with HuggingFace

```mermaid
flowchart TD
    subgraph DataSources["📥 Financial Data Sources"]
        NEWS3["📰 NSE News<br/>Corporate filings"]
        TWEETS["🐦 FinTwit<br/>Market sentiment"]
        REPORTS["📊 Analyst Reports<br/>Earnings calls"]
    end

    subgraph HFPipeline["🤗 HuggingFace Pipeline"]
        TOK["✂️ FinBERT Tokenizer<br/>Financial vocab"]
        MODEL3["🧠 FinBERT Model<br/>ProsusAI/finbert"]
        SENT["🎯 Sentiment Score<br/>Bullish | Bearish | Neutral"]
    end

    subgraph Trading["📈 sjarvis Trading Integration"]
        AGG["📊 Sentiment Aggregator<br/>Time-weighted signals"]
        SIG["📡 Trading Signal<br/>Direction + Confidence"]
        EXEC["⚡ Signal Worker<br/>Paper → Live execution"]
    end

    NEWS3 & TWEETS & REPORTS --> TOK
    TOK --> MODEL3 --> SENT
    SENT --> AGG --> SIG --> EXEC

    style DataSources fill:#0f3460,color:#fff,stroke:#533483
    style HFPipeline fill:#1a1a2e,color:#fff,stroke:#F39C12
    style Trading fill:#1a1a2e,color:#fff,stroke:#2ECC71
    style NEWS3 fill:#3498DB,color:#fff
    style TWEETS fill:#00B4D8,color:#fff
    style REPORTS fill:#E67E22,color:#fff
    style TOK fill:#F39C12,color:#fff
    style MODEL3 fill:#E74C3C,color:#fff
    style SENT fill:#9B59B6,color:#fff
    style AGG fill:#1ABC9C,color:#fff
    style SIG fill:#2ECC71,color:#fff
    style EXEC fill:#27AE60,color:#fff
```

---

## Learning Path

```mermaid
flowchart LR
    subgraph Beginner["📗 Beginner"]
        B1["🔧 Pipeline API<br/>2 lines to run"]
        B2["📥 AutoModel + Tokenizer<br/>load any model"]
        B3["📊 Datasets library<br/>load standard data"]
        B1 --> B2 --> B3
    end

    subgraph Intermediate["📘 Intermediate"]
        I1["🏋️ Trainer API<br/>full fine-tuning"]
        I2["🎯 LoRA with PEFT<br/>parameter-efficient FT"]
        I3["📦 QLoRA<br/>4-bit quantized FT"]
        I1 --> I2 --> I3
    end

    subgraph Advanced["📕 Advanced"]
        A1["🎮 RLHF with TRL<br/>PPO + Reward Model"]
        A2["⚡ Accelerate + DeepSpeed<br/>distributed training"]
        A3["🔬 Custom Architecture<br/>write your own transformer"]
        A1 --> A2 --> A3
    end

    B3 --> I1
    I3 --> A1

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
