# 🏗️ Project 6: Domain-Specific Fine-Tuned LLM (Medical NLP)

> **Gen-ChitChat Initiative** — Alice (MIT) vs. Bob (Stanford) Architectural Design Session

***

## 📋 Project Description

Fine-tune a base LLM for medical Q&A — the model must understand medical terminology, follow clinical reasoning patterns, and produce physician-preferred responses. Uses **Transfer Learning** (BioLLaMA), **LoRA fine-tuning**, and **DPO/RLHF alignment**. Deployed on GCP with Vertex AI.

***

## 🏛️ System Architecture

```mermaid
flowchart TD
    BASE3["🤗 BioLLaMA 8B\n(HuggingFace Hub)\nTransfer Learning base"] --> LORA3["LoRA Adapters\nRank=16, Alpha=32\nTarget: q_proj, v_proj\n8.4M trainable params"]
    LORA3 --> SFT2["SFT Training\n50K MedQA pairs\nHuggingFace TRL SFTTrainer\nVertex AI (A100)"]
    SFT2 --> DPO3["DPO Alignment\n5K physician preference pairs\nTRL DPOTrainer"]
    DPO3 --> EVAL6["Evaluation\nMedBench: target >75\nUSMLE: target >70%\nKeras TensorBoard"]
    EVAL6 --> QUANT2["QLoRA NF4 Quantization\n16GB → 4.5GB\nbitsandbytes"]
    QUANT2 --> DEPLOY2["Vertex AI Endpoint\nvLLM serving\nA/B test: SFT vs DPO"]

    style LORA3 fill:#E74C3C,color:#fff
    style DPO3 fill:#9B59B6,color:#fff
```

### 📐 Transfer Learning Stages

```mermaid
flowchart LR
    subgraph "Stage 1: Transfer Learning (Pre-done)"
        BASE2["LLaMA 3.1 8B\nGeneral knowledge\n'patient' = person waiting"]
        BASE2 --> BIO2["BioLLaMA\n+55B biomedical tokens\n'patient' = medical subject\nKnows drugs, diseases, treatments"]
    end

    subgraph "Stage 2: Our Work"
        BIO2 --> LORA2["LoRA Fine-Tuning\n+50K MedQA instruction pairs\nLearns clinical reasoning\nLearns response format"]
        LORA2 --> ALIGN["DPO/RLHF Alignment\nPhysician preferences\nSafe, accurate responses"]
    end

    style BIO2 fill:#3498DB,color:#fff
    style LORA2 fill:#E74C3C,color:#fff
    style ALIGN fill:#9B59B6,color:#fff
```

### 📐 LoRA Weight Injection — Visualized

```mermaid
flowchart TD
    subgraph "Frozen Attention Layer"
        IN2["Input x"] --> W2["Weight Matrix W\n❄️ 8B params frozen"]
        W2 --> OUT6["Wx"]
    end

    subgraph "LoRA Adapter (Trainable)"
        IN3["Input x"] --> A2["Down-Project A\n4096 → 16 dims\n🔥 Trainable"]
        A2 --> B2["Up-Project B\n16 → 4096 dims\n🔥 Trainable"]
        B2 --> SCALE2["Scale by α/r = 2"]
    end

    OUT6 --> ADD2["➕ Wx + 2·BAx\nBase knowledge + Medical adaptation"]
    SCALE2 --> ADD2

    style W2 fill:#3498DB,color:#fff
    style A2 fill:#E74C3C,color:#fff
    style B2 fill:#E74C3C,color:#fff
```

### 📐 Alignment Method Decision Tree

```mermaid
flowchart TD
    START["Alignment Method?"] --> Q1{"Budget for\nphysician annotation?"}
    Q1 -->|"< $50K\n< 5K pairs"| DPO["✅ Use DPO\nDirect Preference Optimization"]
    Q1 -->|"> $50K\n> 10K pairs"| Q2{"Need iterative\nalignment updates?"}
    Q2 -->|"Yes"| RLHF["✅ Use RLHF\nReward model + PPO"]
    Q2 -->|"No"| DPO

    DPO --> DPO_D["DPOTrainer\nNo reward model needed\nClassification loss on\npreferred vs rejected\n60% less compute"]

    RLHF --> RLHF_D["PPOTrainer\nSeparate reward model\nLive feedback loops\nIterative improvement\n2x compute cost"]

    style DPO fill:#27AE60,color:#fff
    style RLHF fill:#9B59B6,color:#fff
```

***

## 🎙️ Tech Talk — Alice vs. Bob

### Round 1: Why LoRA — The Math

**Alice (MIT):** "**LoRA** (Low-Rank Adaptation) is the only sane way to fine-tune in 2026. The core insight: weight updates during fine-tuning have low intrinsic rank — ΔW = BA where B ∈ ℝ^(d×r) and A ∈ ℝ^(r×d), with r << d.

For LLaMA 3.1 8B:
- d = 4096, r = 16
- Full weight matrix: 4096 × 4096 = 16.7M params per layer
- LoRA matrices: (4096 × 16) + (16 × 4096) = 131K params per layer
- Target `q_proj` + `v_proj` across 32 layers = 8.4M trainable (0.1%)"

**Bob (Stanford):** "But let's be precise about **Transfer Learning** first. We start from **BioLLaMA** — pre-trained on 55B biomedical tokens (PubMed, MIMIC-III, medical textbooks). The medical knowledge is ALREADY in the weights. LoRA then teaches HOW TO RESPOND — format, tone, clinical reasoning. Two-stage training, not one."

**Alice:** "Without the transfer learning base, LoRA alone would need 10x more data. BioLLaMA already knows 'metformin', 'HbA1c', 'contraindication'. LoRA teaches response patterns."

### Round 2: RLHF vs. DPO

**Bob:** "After SFT, the model generates plausible medical responses but not always physician-preferred. **RLHF**: physicians rank 4 responses — train a **Bradley-Terry reward model** r(x,y) with binary cross-entropy. Then PPO optimizes: maximize E[r(y)] - λ × KL(π_new || π_sft). The KL penalty (λ=0.05) prevents reward hacking."

**Alice:** "RLHF is EXPENSIVE — physician annotation $200K+ for 10K pairs. PPO needs 2 models in memory (80GB VRAM). Consider **DPO (Direct Preference Optimization)** — same preference pairs, no reward model, no PPO loop. Classification loss on preferred vs. rejected. 60% less compute, 5 lines of code with `DPOTrainer`."

**Bob:** "DPO is cleaner for static preferences. But RLHF gives **live feedback loops** — update reward model as guidelines evolve. For medical AI where guidelines change annually, iterative alignment matters."

### Round 3: LoRA Hyperparameters & Catastrophic Forgetting

**Alice:** "LoRA rank `r` is critical:
- Rank 4: MedBench 68 (too low)
- Rank 16: MedBench 75 (sweet spot)
- Rank 64: MedBench 75.5 (overfitting)

Alpha should be 2× rank. For rank=16, alpha=32. The adapter has meaningful but not overwhelming influence."

**Bob:** "Even with frozen weights, LoRA can cause **functional catastrophic forgetting** — correct on medical questions but forgets coherent formatting or 'I don't know' responses. Maintain a sanity suite: 50 general knowledge + 50 formatting + 50 'I don't know' triggers. Run after each checkpoint. If accuracy drops below 95%, stop training."

### Round 4: DPO Data Collection & Deployment

**Alice:** "DPO needs preference pairs. The trick: **synthetic negative generation**. Take physician-approved response, introduce ONE systematic flaw (remove safety caveat, change dosage, omit contraindication). One physician validates 100 synthetic negatives per hour. 5K pairs in ~25 physician-hours = **$3,750 instead of $25K**."

**Bob:** "Deploy with A/B testing on Vertex AI Endpoints: 90% → SFT model, 10% → DPO model. Evaluate after 1 week on physician ratings, hallucination rate, safety caveat presence, user satisfaction. The key: A/B testing in medical AI needs **safety gates**, not just quality metrics. A model that writes better but occasionally omits drug interactions is WORSE."

### Round 5: Quantization & Keras Monitoring

**Bob:** "Post-training, **QLoRA NF4** quantization — model from 16GB to 4.5GB. NF4 is information-theoretically optimal for normally-distributed weights. **Double Quantization** quantizes the quantization constants themselves, saving another 0.5GB."

**Alice:** "**Keras callbacks** for monitoring: `CSVLogger` for per-step metrics, `TensorBoard` sent to Vertex AI, `ReduceLROnPlateau` for auto learning rate, `EarlyStopping` to kill wasteful runs. Vertex AI `CustomTrainingJob` with `a2-highgpu-1g` (A100 80GB) handles infrastructure."

***

## 📊 Full Fine-Tuning vs. LoRA (PEFT) vs. QLoRA

| Feature | **Full Fine-Tuning** | **LoRA (PEFT)** | **QLoRA** |
|---|---|---|---|
| **Trainable Params** | 100% (8B) | ~0.1% (8.4M) | ~0.1% (8.4M) |
| **GPU Memory** | 80GB+ (A100) | 24GB (A10G) | 12GB (RTX 3090 / L4) |
| **Training Speed** | Baseline | 8x faster | 8x faster |
| **Training Cost (GCP)** | ~$500/run (A100 80GB) | ~$60/run (A10G) | ~$30/run (L4) |
| **Accuracy vs. Full FT** | Baseline | -0.5 to -1.5% | -1 to -2% |
| **Catastrophic Forgetting** | ⚠️ Risk | ✅ No (base frozen) | ✅ No (base frozen) |
| **Best For** | Max accuracy, big budget | Production fine-tuning | Consumer GPU / cost-sensitive |

## 📊 RLHF vs. DPO — Alignment Methods

| Feature | **RLHF (PPO)** | **DPO** |
|---|---|---|
| **Reward Model** | ✅ Required (separate model) | ❌ Not needed |
| **Training Loop** | PPO (complex, 2 models) | Single-pass classification |
| **Compute Cost** | High (2x models in memory) | 60% less |
| **Data Requirement** | 10K+ preference pairs | 5K+ preference pairs |
| **Iterative Update** | ✅ Update reward model, re-align | ❌ Retrain from scratch |
| **Code Complexity** | `PPOTrainer` (100+ lines config) | `DPOTrainer` (5 lines) |
| **Best For** | Evolving preferences, medical/legal | Static preferences, cost-sensitive |

## 📊 Transfer Learning Checkpoints — Medical LLMs

| Base Model | **BioLLaMA** | **MedAlpaca** | **PMC-LLaMA** |
|---|---|---|---|
| **Base Architecture** | LLaMA 3.1 8B | LLaMA 2 7B | LLaMA 2 7B |
| **Pre-train Corpus** | PubMed + MIMIC-III (55B tokens) | MedQA + HealthcareMagic | PubMed Central (4.8M papers) |
| **USMLE Pass Rate** | 67% | 58% | 54% |
| **Best For** | Clinical QA | Patient interaction | Research synthesis |

***

## 🏗️ GCP Architecture

```mermaid
flowchart TD
    subgraph "GCP Project"
        subgraph "Training"
            GCS4["Cloud Storage\nMedQA + Preferences"]
            VT2["Vertex AI Training\nA100 80GB"]
            TB3["Vertex AI TensorBoard"]
            EXP3["Vertex AI Experiments"]
        end

        subgraph "Model Management"
            MR3["Vertex AI Model Registry\nSFT v1 → DPO v1 → DPO v2"]
            AB2["Vertex AI Endpoint\nA/B Traffic Split"]
        end

        subgraph "Evaluation"
            EVAL7["Cloud Run Job\nMedBench + USMLE\nNightly"]
            BQ9["BigQuery\nModel Metrics"]
        end
    end

    GCS4 --> VT2 --> TB3 & EXP3
    VT2 --> MR3 --> AB2
    EVAL7 --> BQ9
```

***

## 🔑 Key Takeaways

1. **Transfer Learning is the foundation** — BioLLaMA provides medical vocabulary; LoRA teaches clinical reasoning
2. **LoRA trains 0.1% of parameters** — 8x cheaper, no catastrophic forgetting, mergeable into base model
3. **Start with DPO** (cheaper, simpler) → migrate to RLHF when budget + iterative needs justify it
4. **Synthetic negative generation** cuts DPO annotation cost from $25K to $3,750
5. **QLoRA NF4** for deployment reduces model from 16GB to 4.5GB with minimal accuracy loss
6. **A/B testing with safety gates** — medical AI needs safety metrics, not just quality metrics

***

*← Back to [TODO.MD](./TODO.MD)*
