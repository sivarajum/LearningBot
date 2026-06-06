# Transfer Learning: Visual Guide & Architecture Diagrams

## 1. Transfer Learning Overview

```mermaid
flowchart LR
    subgraph Source["📚 Source Task (Pre-trained)"]
        S_DATA["📊 Large Dataset<br/>ImageNet: 14M images<br/>Wikipedia: 3B words"]
        S_MODEL["🧠 Trained Model<br/>ResNet / BERT"]
        S_DATA --> S_MODEL
    end

    subgraph Transfer["🔄 Transfer"]
        FREEZE["♻️ Reuse learned<br/>representations"]
    end

    subgraph Target["🎯 Target Task (Your Task)"]
        T_DATA["📋 Small Dataset<br/>1K-10K samples"]
        T_MODEL["⚡ Adapted Model<br/>Fine-tuned"]
        T_DATA --> T_MODEL
    end

    S_MODEL --> FREEZE --> T_MODEL

    style Source fill:#0f3460,color:#fff,stroke:#533483
    style Transfer fill:#F39C12,color:#fff,stroke:#E67E22
    style Target fill:#2ECC71,color:#fff,stroke:#27AE60
    style S_DATA fill:#3498DB,color:#fff
    style S_MODEL fill:#9B59B6,color:#fff
    style FREEZE fill:#E67E22,color:#fff
    style T_DATA fill:#E74C3C,color:#fff
    style T_MODEL fill:#27AE60,color:#fff
```

## 2. What Layers Learn (CNN Example)

```mermaid
flowchart TD
    subgraph Early["🔒 Early Layers (Universal)"]
        L1["Layer 1-2<br/>Edges, colors, textures<br/>🔒 Almost always frozen"]
    end

    subgraph Middle["🔒/🔓 Middle Layers (General)"]
        L2["Layer 3-6<br/>Shapes, patterns, parts<br/>Freeze for small data"]
    end

    subgraph Late["🔓 Late Layers (Task-Specific)"]
        L3["Layer 7-10<br/>Object parts, domain features<br/>Usually fine-tuned"]
    end

    subgraph Head["🆕 Classification Head (New)"]
        L4["New Dense layers<br/>Your specific classes<br/>🔓 Always trained"]
    end

    L1 --> L2 --> L3 --> L4

    style Early fill:#2ECC71,color:#fff,stroke:#27AE60
    style Middle fill:#F39C12,color:#fff,stroke:#E67E22
    style Late fill:#E74C3C,color:#fff,stroke:#C0392B
    style Head fill:#9B59B6,color:#fff,stroke:#8E44AD
    style L1 fill:#27AE60,color:#fff
    style L2 fill:#E67E22,color:#fff
    style L3 fill:#C0392B,color:#fff
    style L4 fill:#8E44AD,color:#fff
```

## 3. Strategy Decision Flow

```mermaid
flowchart TD
    START["📊 Dataset Size?"] --> SMALL{"< 1K samples"}
    START --> MED{"1K - 50K"}
    START --> LARGE{"> 50K"}

    SMALL --> DOM1{"🔍 Domain similar<br/>to source?"}
    DOM1 -->|"✅ Yes"| FE["🔒 Feature Extraction<br/>Freeze base, train head only"]
    DOM1 -->|"❌ No"| FE2["🔒 Feature Extraction<br/>+ Data augmentation"]

    MED --> DOM2{"🔍 Domain similar?"}
    DOM2 -->|"✅ Yes"| FT_TOP["🔓 Fine-tune Top Layers<br/>Freeze bottom, train top + head"]
    DOM2 -->|"❌ No"| FT_MORE["🔓 Fine-tune More Layers<br/>Gradual unfreezing"]

    LARGE --> FULL["🔓 Full Fine-tuning<br/>or Train from scratch"]

    style START fill:#3498DB,color:#fff
    style SMALL fill:#9B59B6,color:#fff
    style MED fill:#9B59B6,color:#fff
    style LARGE fill:#9B59B6,color:#fff
    style DOM1 fill:#F39C12,color:#fff
    style DOM2 fill:#F39C12,color:#fff
    style FE fill:#2ECC71,color:#fff,stroke:#27AE60
    style FE2 fill:#27AE60,color:#fff
    style FT_TOP fill:#E67E22,color:#fff
    style FT_MORE fill:#E74C3C,color:#fff
    style FULL fill:#C0392B,color:#fff
```

## 4. Fine-Tuning Process

```mermaid
sequenceDiagram
    participant B as 🧠 Pre-trained Model
    participant P1 as 🔒 Phase 1: Head Only
    participant P2 as 🔓 Phase 2: + Top Layers
    participant P3 as 🔓 Phase 3: + More Layers
    participant V as 📊 Validation

    B->>P1: Freeze base, train new head
    Note over P1: LR: 1e-3, Epochs: 3-5
    P1->>V: Check val_loss
    V->>P2: If improving → unfreeze top layers
    Note over P2: LR: 1e-5 (base), 1e-4 (head)
    P2->>V: Check val_loss
    V->>P3: If still improving → unfreeze more
    Note over P3: LR: 1e-6 (bottom), 1e-5 (top)
    P3->>V: If val_loss increases → STOP & revert
```

## 5. NLP Transfer Learning Stack

```mermaid
flowchart TD
    subgraph Step1["📚 Step 1: Pre-training"]
        CORPUS["📖 Massive Text Corpus<br/>Wikipedia + Books"]
        PRETRAIN["🧠 BERT / GPT<br/>MLM / Next Token"]
        CORPUS --> PRETRAIN
    end

    subgraph Step2["🏢 Step 2: Domain Adaptation"]
        DOMAIN["📊 Domain Corpus<br/>Financial reports, news"]
        CONTINUE["🔄 Continue Pre-training<br/>Domain-specific vocab"]
        DOMAIN --> CONTINUE
    end

    subgraph Step3["🎯 Step 3: Task Fine-Tuning"]
        LABELED["🏷️ Labeled Data<br/>Sentiment, NER, QA"]
        FINETUNE["⚡ Fine-tune + Task Head"]
        LABELED --> FINETUNE
    end

    PRETRAIN --> CONTINUE --> FINETUNE
    PRETRAIN -->|"Skip if similar domain"| FINETUNE

    style Step1 fill:#0f3460,color:#fff,stroke:#533483
    style Step2 fill:#1a1a2e,color:#fff,stroke:#e94560
    style Step3 fill:#1a1a2e,color:#fff,stroke:#2ECC71
    style CORPUS fill:#3498DB,color:#fff
    style PRETRAIN fill:#9B59B6,color:#fff
    style DOMAIN fill:#E74C3C,color:#fff
    style CONTINUE fill:#E67E22,color:#fff
    style LABELED fill:#F39C12,color:#fff
    style FINETUNE fill:#2ECC71,color:#fff
```

## 6. Common Pre-trained Models

```mermaid
flowchart LR
    subgraph Vision["👁️ Vision Models"]
        RESNET["🏗️ ResNet-50<br/>ImageNet<br/>General images"]
        EFFNET["⚡ EfficientNet<br/>ImageNet<br/>Efficient"]
        VIT["🔲 ViT<br/>ImageNet<br/>Transformer"]
    end

    subgraph NLP["📝 NLP Models"]
        BERT2["🧠 BERT<br/>Wikipedia+Books<br/>Understanding"]
        FINBERT["💹 FinBERT<br/>Financial text<br/>Finance"]
        ROBERTA["💪 RoBERTa<br/>More data<br/>Robust"]
    end

    subgraph TS["📈 Time Series"]
        MOIRAI["🔮 MOIRAI<br/>Time series<br/>Forecasting"]
        CHRONOS["⏰ Chronos<br/>Amazon<br/>Foundation"]
    end

    style Vision fill:#0f3460,color:#fff,stroke:#533483
    style NLP fill:#1a1a2e,color:#fff,stroke:#e94560
    style TS fill:#1a1a2e,color:#fff,stroke:#2ECC71
    style RESNET fill:#3498DB,color:#fff
    style EFFNET fill:#2ECC71,color:#fff
    style VIT fill:#9B59B6,color:#fff
    style BERT2 fill:#E74C3C,color:#fff
    style FINBERT fill:#F39C12,color:#fff
    style ROBERTA fill:#E67E22,color:#fff
    style MOIRAI fill:#1ABC9C,color:#fff
    style CHRONOS fill:#00B4D8,color:#fff
```

## 7. Catastrophic Forgetting Prevention

```mermaid
flowchart TD
    PROBLEM["⚠️ Catastrophic Forgetting<br/>Model loses source knowledge"]

    PROBLEM --> S1["📉 Low Learning Rate<br/>1e-5 for base layers"]
    PROBLEM --> S2["🔓 Gradual Unfreezing<br/>Top → Bottom"]
    PROBLEM --> S3["⚖️ EWC Penalty<br/>Protect important weights"]
    PROBLEM --> S4["🔥 LR Warmup<br/>Start near zero"]
    PROBLEM --> S5["🔄 Replay Buffer<br/>Mix source data"]

    S1 --> RESULT["✅ Preserved Knowledge<br/>+ New Task Performance"]
    S2 --> RESULT
    S3 --> RESULT
    S4 --> RESULT
    S5 --> RESULT

    style PROBLEM fill:#E74C3C,color:#fff,stroke:#C0392B
    style S1 fill:#3498DB,color:#fff
    style S2 fill:#9B59B6,color:#fff
    style S3 fill:#F39C12,color:#fff
    style S4 fill:#E67E22,color:#fff
    style S5 fill:#00B4D8,color:#fff
    style RESULT fill:#2ECC71,color:#fff,stroke:#27AE60
```

## 8. Financial FinBERT Transfer Pipeline

```mermaid
flowchart TD
    subgraph Base["🧠 Pre-trained BERT"]
        BERT["BERT-base<br/>110M params<br/>Wikipedia + BooksCorpus"]
    end

    subgraph Adapt["📊 Financial Domain Adaptation"]
        FIN_CORPUS["💹 Financial Corpus<br/>10K reports, earnings calls,<br/>analyst notes"]
        CONTINUE_PT["🔄 Continue Pre-training<br/>Financial MLM"]
        FIN_CORPUS --> CONTINUE_PT
    end

    subgraph Tasks["🎯 Financial Tasks"]
        SENT["😊/😐/😟 Sentiment<br/>'Bullish on TCS'"]
        NER["🏷️ Named Entity<br/>'₹2850', 'RELIANCE'"]
        REL["🔗 Relation<br/>'TCS → competitor → Infosys'"]
    end

    BERT --> CONTINUE_PT
    CONTINUE_PT --> SENT
    CONTINUE_PT --> NER
    CONTINUE_PT --> REL

    style Base fill:#0f3460,color:#fff,stroke:#533483
    style Adapt fill:#1a1a2e,color:#fff,stroke:#e94560
    style Tasks fill:#1a1a2e,color:#fff,stroke:#2ECC71
    style BERT fill:#9B59B6,color:#fff
    style FIN_CORPUS fill:#E74C3C,color:#fff
    style CONTINUE_PT fill:#F39C12,color:#fff
    style SENT fill:#2ECC71,color:#fff
    style NER fill:#3498DB,color:#fff
    style REL fill:#E67E22,color:#fff
```

## 9. Learning Path

```mermaid
graph TD
    subgraph W1["📗 Week 1: Foundations"]
        W1A["🧠 Why transfer works<br/>Feature hierarchy"]
        W1B["🔒 Feature extraction<br/>Frozen base + new head"]
        W1C["📋 Pre-trained models<br/>ResNet, BERT, ViT"]
    end

    subgraph W2["📘 Week 2: Fine-Tuning"]
        W2A["🔓 Gradual unfreezing<br/>Layer-by-layer"]
        W2B["📉 Discriminative LR<br/>Per-layer rates"]
        W2C["🔍 When to freeze<br/>Dataset size rules"]
    end

    subgraph W3["📙 Week 3: NLP Transfer"]
        W3A["🧠 BERT fine-tuning<br/>Classification, NER"]
        W3B["🏢 Domain adaptation<br/>Continue pre-training"]
        W3C["💹 FinBERT, BioBERT<br/>Domain models"]
    end

    subgraph W4["📕 Week 4: Advanced"]
        W4A["⚠️ Catastrophic forgetting<br/>EWC, replay"]
        W4B["🔀 Multi-task learning<br/>Joint training"]
        W4C["📊 Evaluation<br/>Baselines & ablations"]
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
