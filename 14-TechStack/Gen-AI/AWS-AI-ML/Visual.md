# AWS AI/ML: Visual Guide & Architecture Diagrams

## 1. AWS AI/ML Service Tiers

```mermaid
flowchart TD
    subgraph Tier1["🟢 Tier 1: AI Services (No ML Needed)"]
        COMP["🧠 Comprehend<br/>NLP / Sentiment"]
        REK["👁️ Rekognition<br/>Vision / Faces"]
        TEXT["📄 Textract<br/>Document OCR"]
        POLLY["🔊 Polly<br/>Text-to-Speech"]
        LEX["💬 Lex<br/>Chatbots"]
        TRANS2["🌍 Translate<br/>Multi-language"]
    end

    subgraph Tier2["🔵 Tier 2: ML Platform"]
        SM["🏗️ SageMaker<br/>Train / Deploy / Monitor"]
        AUTO["🤖 Autopilot<br/>AutoML"]
        PIPE["⚙️ Pipelines<br/>MLOps"]
    end

    subgraph Tier3["🟣 Tier 3: Foundation Models"]
        BR["🧠 Bedrock<br/>Claude, Llama, Titan"]
        KB["📚 Knowledge Bases<br/>RAG"]
        GUARD["🛡️ Guardrails<br/>Safety"]
    end

    subgraph Tier4["⚡ Tier 4: Infrastructure"]
        GPU["🖥️ EC2 GPU<br/>p4d, p5"]
        INF["🔲 Inferentia<br/>AWS custom chip"]
        TRAIN["🚀 Trainium<br/>Training chip"]
    end

    style Tier1 fill:#2ECC71,color:#fff,stroke:#27AE60
    style Tier2 fill:#3498DB,color:#fff,stroke:#2980B9
    style Tier3 fill:#9B59B6,color:#fff,stroke:#8E44AD
    style Tier4 fill:#E74C3C,color:#fff,stroke:#C0392B
    style COMP fill:#27AE60,color:#fff
    style REK fill:#27AE60,color:#fff
    style TEXT fill:#27AE60,color:#fff
    style POLLY fill:#27AE60,color:#fff
    style LEX fill:#27AE60,color:#fff
    style TRANS2 fill:#27AE60,color:#fff
    style SM fill:#2980B9,color:#fff
    style AUTO fill:#2980B9,color:#fff
    style PIPE fill:#2980B9,color:#fff
    style BR fill:#8E44AD,color:#fff
    style KB fill:#8E44AD,color:#fff
    style GUARD fill:#8E44AD,color:#fff
    style GPU fill:#C0392B,color:#fff
    style INF fill:#C0392B,color:#fff
    style TRAIN fill:#C0392B,color:#fff
```

## 2. SageMaker Workflow

```mermaid
flowchart LR
    subgraph Prepare["📥 Prepare"]
        S3["💾 S3 Data Lake"]
        NB["📓 SageMaker Notebook"]
        PROC["⚙️ Processing Job<br/>Feature engineering"]
    end

    subgraph Train["🏋️ Train"]
        TRAIN2["🎯 Training Job<br/>ml.m5/p3/p4"]
        TUNE["🔧 Hyperparameter<br/>Tuning"]
        MODEL["📦 Model Artifacts<br/>→ S3"]
    end

    subgraph Deploy["🚀 Deploy"]
        REG["📋 Model Registry<br/>Version control"]
        EP["⚡ Real-time Endpoint"]
        BATCH["📦 Batch Transform"]
        SL["☁️ Serverless Inference"]
    end

    subgraph Monitor["📊 Monitor"]
        MON["📈 Model Monitor<br/>Data drift"]
        CLAR["⚖️ Clarify<br/>Bias detection"]
        CW["📊 CloudWatch<br/>Metrics & logs"]
    end

    S3 --> NB --> PROC --> TRAIN2
    TRAIN2 --> TUNE --> MODEL
    MODEL --> REG --> EP & BATCH & SL
    EP --> MON --> CLAR --> CW

    style Prepare fill:#0f3460,color:#fff,stroke:#533483
    style Train fill:#1a1a2e,color:#fff,stroke:#e94560
    style Deploy fill:#1a1a2e,color:#fff,stroke:#2ECC71
    style Monitor fill:#1a1a2e,color:#fff,stroke:#F39C12
    style S3 fill:#3498DB,color:#fff
    style NB fill:#9B59B6,color:#fff
    style PROC fill:#00B4D8,color:#fff
    style TRAIN2 fill:#E74C3C,color:#fff
    style TUNE fill:#E67E22,color:#fff
    style MODEL fill:#F39C12,color:#fff
    style REG fill:#2ECC71,color:#fff
    style EP fill:#27AE60,color:#fff
    style BATCH fill:#1ABC9C,color:#fff
    style SL fill:#16A085,color:#fff
    style MON fill:#E67E22,color:#fff
    style CLAR fill:#D35400,color:#fff
    style CW fill:#F39C12,color:#fff
```

## 3. Amazon Bedrock Architecture

```mermaid
flowchart TD
    APP["🖥️ Your Application"]

    subgraph Bedrock["🧠 Amazon Bedrock"]
        API["📡 Bedrock Runtime API"]

        subgraph Models["🌟 Foundation Models"]
            CLAUDE["🟠 Anthropic Claude"]
            LLAMA["🟣 Meta Llama"]
            TITAN["🔵 Amazon Titan"]
            SD["🎨 Stability AI"]
        end

        subgraph Features["⚙️ Features"]
            KB2["📚 Knowledge Bases<br/>(RAG)"]
            AGENTS["🤖 Agents<br/>(Tool use)"]
            GUARD2["🛡️ Guardrails<br/>(Safety)"]
            FT["🎯 Fine-tuning"]
        end
    end

    subgraph Data["💾 Data Layer"]
        S3_2["📄 S3 Documents"]
        OS["🔍 OpenSearch<br/>Vector DB"]
    end

    APP --> API
    API --> CLAUDE & LLAMA & TITAN & SD
    API --> KB2 & AGENTS & GUARD2
    KB2 --> S3_2 --> OS

    style Bedrock fill:#1a1a2e,color:#fff,stroke:#e94560
    style Models fill:#0f3460,color:#fff,stroke:#533483
    style Features fill:#0f3460,color:#fff,stroke:#533483
    style Data fill:#1a1a2e,color:#fff,stroke:#2ECC71
    style APP fill:#3498DB,color:#fff
    style API fill:#F39C12,color:#fff
    style CLAUDE fill:#D97706,color:#fff
    style LLAMA fill:#9B59B6,color:#fff
    style TITAN fill:#2980B9,color:#fff
    style SD fill:#E74C3C,color:#fff
    style KB2 fill:#2ECC71,color:#fff
    style AGENTS fill:#E67E22,color:#fff
    style GUARD2 fill:#E74C3C,color:#fff
    style FT fill:#1ABC9C,color:#fff
    style S3_2 fill:#3498DB,color:#fff
    style OS fill:#00B4D8,color:#fff
```

## 4. SageMaker Pipeline Flow

```mermaid
flowchart TD
    TRIGGER["⏰ EventBridge<br/>Daily 6PM IST"] --> P1

    P1["⚙️ Step 1: Preprocess<br/>Feature engineering"]
    P2["🏋️ Step 2: Train<br/>XGBoost / custom"]
    P3["📊 Step 3: Evaluate<br/>Accuracy, F1, ROC"]
    P4{"✅ Accuracy > 0.6?"}
    P5["📋 Step 4: Register<br/>Model Registry"]
    P6["🚀 Step 5: Deploy<br/>Update endpoint"]
    FAIL["🚨 Step: Alert<br/>SNS notification"]

    P1 --> P2 --> P3 --> P4
    P4 -->|"✅ Yes"| P5 --> P6
    P4 -->|"❌ No"| FAIL

    style TRIGGER fill:#9B59B6,color:#fff
    style P1 fill:#3498DB,color:#fff
    style P2 fill:#E74C3C,color:#fff
    style P3 fill:#F39C12,color:#fff
    style P4 fill:#E67E22,color:#fff
    style P5 fill:#2ECC71,color:#fff
    style P6 fill:#27AE60,color:#fff
    style FAIL fill:#C0392B,color:#fff
```

## 5. AI Services for Financial NLP

```mermaid
sequenceDiagram
    participant N as 📰 Financial News
    participant C as 🧠 Comprehend
    participant X as 🏷️ Custom NER
    participant A as 📊 Trading App

    N->>C: "SEBI fined RELIANCE ₹25Cr"
    C->>C: detect_sentiment() → NEGATIVE
    C->>C: detect_entities() → [SEBI:ORG, ₹25Cr:QUANTITY]
    C->>X: Custom entity model
    X->>X: detect_entities() → [RELIANCE:STOCK_SYMBOL]
    X->>A: {symbol: RELIANCE, sentiment: negative, confidence: 0.92}
```

## 6. Deployment Options Comparison

```mermaid
flowchart TD
    MODEL2["📦 Trained Model"] --> Q{"🔍 Deployment<br/>Need?"}

    Q -->|"Real-time,<br/>low latency"| RT["⚡ Real-time Endpoint<br/>Always running<br/>ml.m5.large<br/>~$50/month"]
    Q -->|"Occasional,<br/>cost-sensitive"| SL2["☁️ Serverless<br/>Scale to zero<br/>Pay per request<br/>~$5/month"]
    Q -->|"Batch scoring"| BT["📦 Batch Transform<br/>Process S3 files<br/>Pay per job"]
    Q -->|"Multiple models"| MM["🔀 Multi-Model Endpoint<br/>One instance, N models<br/>Memory-shared"]
    Q -->|"A/B testing"| AB["📊 Production Variants<br/>Traffic splitting<br/>Canary deploys"]

    style MODEL2 fill:#3498DB,color:#fff
    style Q fill:#9B59B6,color:#fff
    style RT fill:#E74C3C,color:#fff
    style SL2 fill:#2ECC71,color:#fff
    style BT fill:#F39C12,color:#fff
    style MM fill:#E67E22,color:#fff
    style AB fill:#00B4D8,color:#fff
```

## 7. AWS vs GCP vs Azure ML

```mermaid
graph TB
    subgraph CMP["🔍 Cloud ML Platform Comparison"]
        direction LR
        subgraph AWS["🟠 AWS"]
            SM2["🏗️ SageMaker<br/>Most mature"]
            BR2["🧠 Bedrock<br/>Multi-model"]
            COMP2["📝 Comprehend<br/>Best NLP APIs"]
        end

        subgraph GCP["🔵 GCP"]
            VAI["🚀 Vertex AI<br/>Integrated platform"]
            GEM["🌟 Gemini<br/>Best multimodal"]
            BQ["📊 BigQuery ML<br/>SQL-based ML"]
        end

        subgraph Azure["🟣 Azure"]
            AML["🏢 Azure ML Studio<br/>Enterprise focus"]
            AOAI["🤖 Azure OpenAI<br/>GPT-4 access"]
            COG["🧠 Cognitive Services<br/>Pre-built APIs"]
        end
    end

    style CMP fill:#1a1a2e,color:#fff,stroke:#e94560
    style AWS fill:#FF9900,color:#fff
    style GCP fill:#4285F4,color:#fff
    style Azure fill:#0078D4,color:#fff
    style SM2 fill:#CC7A00,color:#fff
    style BR2 fill:#CC7A00,color:#fff
    style COMP2 fill:#CC7A00,color:#fff
    style VAI fill:#3367D6,color:#fff
    style GEM fill:#3367D6,color:#fff
    style BQ fill:#3367D6,color:#fff
    style AML fill:#005A9E,color:#fff
    style AOAI fill:#005A9E,color:#fff
    style COG fill:#005A9E,color:#fff
```

## 8. Financial ML on AWS (Trading Pipeline)

```mermaid
flowchart TD
    subgraph Ingest["📥 Data Ingestion"]
        KINESIS["📡 Kinesis<br/>Real-time ticks"]
        S3_DATA["💾 S3<br/>Historical OHLCV"]
    end

    subgraph Process["⚙️ Feature Engineering"]
        GLUE["🔧 Glue ETL<br/>Transform data"]
        SM_PROC["⚡ SageMaker Processing<br/>Technical indicators"]
    end

    subgraph Train_Deploy["🏋️ Train & Deploy"]
        SM_TRAIN["🎯 SageMaker Training<br/>XGBoost momentum model"]
        SM_EP["🚀 SageMaker Endpoint<br/>Real-time predictions"]
    end

    subgraph Signal["📊 Signal Generation"]
        LAMBDA["⚡ Lambda<br/>Generate signals"]
        DYNAMO["💾 DynamoDB<br/>Signal store"]
        SNS["📨 SNS<br/>Alert → Telegram"]
    end

    KINESIS --> GLUE
    S3_DATA --> GLUE
    GLUE --> SM_PROC --> SM_TRAIN --> SM_EP
    SM_EP --> LAMBDA --> DYNAMO
    LAMBDA --> SNS

    style Ingest fill:#0f3460,color:#fff,stroke:#533483
    style Process fill:#1a1a2e,color:#fff,stroke:#e94560
    style Train_Deploy fill:#1a1a2e,color:#fff,stroke:#2ECC71
    style Signal fill:#1a1a2e,color:#fff,stroke:#F39C12
    style KINESIS fill:#E74C3C,color:#fff
    style S3_DATA fill:#3498DB,color:#fff
    style GLUE fill:#9B59B6,color:#fff
    style SM_PROC fill:#00B4D8,color:#fff
    style SM_TRAIN fill:#E67E22,color:#fff
    style SM_EP fill:#2ECC71,color:#fff
    style LAMBDA fill:#F39C12,color:#fff
    style DYNAMO fill:#3498DB,color:#fff
    style SNS fill:#E74C3C,color:#fff
```

## 9. Learning Path

```mermaid
graph TD
    subgraph W1["📗 Week 1: AI Services"]
        W1A["🧠 Comprehend<br/>NLP APIs"]
        W1B["📄 Textract / Rekognition<br/>Document & vision"]
        W1C["💻 boto3 basics<br/>SDK usage"]
    end

    subgraph W2["📘 Week 2: SageMaker"]
        W2A["📓 Studio notebooks<br/>Data exploration"]
        W2B["🎯 Built-in algorithms<br/>XGBoost, Linear"]
        W2C["🚀 Training + Deploy<br/>Estimator API"]
    end

    subgraph W3["📙 Week 3: MLOps"]
        W3A["⚙️ SageMaker Pipelines<br/>Automated workflows"]
        W3B["📋 Model Registry<br/>Versioning"]
        W3C["📈 Model Monitor<br/>Drift detection"]
    end

    subgraph W4["📕 Week 4: GenAI"]
        W4A["🧠 Bedrock basics<br/>Foundation models"]
        W4B["📚 Knowledge Bases<br/>RAG pipelines"]
        W4C["🤖 Agents + Guardrails<br/>Production GenAI"]
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
