# NLP: Visual Guide & Architecture Diagrams

## 1. NLP Pipeline Architecture

```mermaid
flowchart TD
    subgraph Input["📥 Input"]
        RAW["📄 Raw Text"]
    end

    subgraph Preprocessing["⚙️ Preprocessing"]
        TOK["✂️ Tokenization"]
        STOP["🚫 Stopword Removal"]
        LEM["📝 Lemmatization"]
        NORM["📏 Normalization"]
    end

    subgraph Representation["🔢 Representation"]
        BOW["📊 Bag of Words"]
        TFIDF["📈 TF-IDF"]
        W2V["🧠 Word2Vec / GloVe"]
        BERT_EMB["🤖 BERT Embeddings"]
    end

    subgraph Tasks["🎯 Tasks"]
        CLASS["📋 Classification"]
        NER["🏷️ NER"]
        SENT["😊 Sentiment"]
        QA["❓ QA"]
        SUM["📝 Summarization"]
        TRANS["🌍 Translation"]
    end

    RAW --> TOK --> STOP --> LEM --> NORM
    NORM --> BOW & TFIDF & W2V & BERT_EMB
    BOW --> CLASS
    TFIDF --> CLASS & SENT
    W2V --> NER & CLASS
    BERT_EMB --> NER & SENT & QA & SUM & TRANS

    style Input fill:#3498DB,color:#fff,stroke:#2980B9
    style Preprocessing fill:#2ECC71,color:#fff,stroke:#27AE60
    style Representation fill:#9B59B6,color:#fff,stroke:#8E44AD
    style Tasks fill:#E74C3C,color:#fff,stroke:#C0392B
    style RAW fill:#2980B9,color:#fff
    style TOK fill:#27AE60,color:#fff
    style STOP fill:#27AE60,color:#fff
    style LEM fill:#27AE60,color:#fff
    style NORM fill:#27AE60,color:#fff
    style BOW fill:#8E44AD,color:#fff
    style TFIDF fill:#8E44AD,color:#fff
    style W2V fill:#8E44AD,color:#fff
    style BERT_EMB fill:#8E44AD,color:#fff
    style CLASS fill:#C0392B,color:#fff
    style NER fill:#C0392B,color:#fff
    style SENT fill:#C0392B,color:#fff
    style QA fill:#C0392B,color:#fff
    style SUM fill:#C0392B,color:#fff
    style TRANS fill:#C0392B,color:#fff
```

## 2. Text Representation Evolution

```mermaid
flowchart LR
    subgraph Era1["📜 Era 1: Sparse (Pre-2013)"]
        BOW2["📊 Bag of Words<br/>One-hot encoding<br/>High-dimensional"]
        TFIDF2["📈 TF-IDF<br/>Term importance<br/>Still sparse"]
    end

    subgraph Era2["🧠 Era 2: Dense Static (2013)"]
        W2V2["🔵 Word2Vec<br/>Dense 300-dim<br/>Fixed per word"]
        GLOVE["🟢 GloVe<br/>Co-occurrence<br/>Global statistics"]
    end

    subgraph Era3["⚡ Era 3: Contextual (2018)"]
        ELMO["🟣 ELMo<br/>BiLSTM<br/>Context-dependent"]
        BERT2["🔴 BERT<br/>Transformer encoder<br/>Bidirectional"]
    end

    subgraph Era4["🚀 Era 4: Foundation (2020+)"]
        GPT["🌟 GPT-3/4<br/>Decoder-only<br/>In-context learning"]
        LLM["🧬 Claude / Gemini<br/>Multimodal<br/>Reasoning"]
    end

    BOW2 --> TFIDF2 --> W2V2 --> GLOVE --> ELMO --> BERT2 --> GPT --> LLM

    style Era1 fill:#7F8C8D,color:#fff,stroke:#95A5A6
    style Era2 fill:#3498DB,color:#fff,stroke:#2980B9
    style Era3 fill:#9B59B6,color:#fff,stroke:#8E44AD
    style Era4 fill:#E74C3C,color:#fff,stroke:#C0392B
    style BOW2 fill:#95A5A6,color:#fff
    style TFIDF2 fill:#95A5A6,color:#fff
    style W2V2 fill:#2980B9,color:#fff
    style GLOVE fill:#2ECC71,color:#fff
    style ELMO fill:#8E44AD,color:#fff
    style BERT2 fill:#E74C3C,color:#fff
    style GPT fill:#F39C12,color:#fff
    style LLM fill:#E67E22,color:#fff
```

## 3. NER Flow

```mermaid
sequenceDiagram
    participant Text as 📄 Input Text
    participant Tok as ✂️ Tokenizer
    participant Model as 🧠 NER Model
    participant Post as ⚙️ Post-Processing
    participant Out as 🏷️ Entities

    Text->>Tok: "SEBI fined RELIANCE ₹25 crore"
    Tok->>Model: [SEBI, fined, RELIANCE, ₹25, crore]
    Model->>Model: BIO Tagging
    Note over Model: SEBI → B-ORG<br/>fined → O<br/>RELIANCE → B-ORG<br/>₹25 → B-MONEY<br/>crore → I-MONEY
    Model->>Post: BIO labels
    Post->>Post: Merge consecutive spans
    Post->>Out: {ORG: [SEBI, RELIANCE], MONEY: [₹25 crore]}
```

## 4. Sentiment Analysis Pipeline

```mermaid
flowchart TD
    subgraph Input2["📥 Data Sources"]
        NEWS["📰 Financial Headlines"]
        TWEETS["🐦 Social Media"]
        REPORTS["📊 Analyst Reports"]
    end

    subgraph Models["🧠 Models"]
        FINBERT["💰 FinBERT<br/>Financial domain<br/>3-class"]
        VADER["⚡ VADER<br/>Rule-based<br/>Fast, social media"]
        CUSTOM["🎯 Custom Model<br/>Domain fine-tuned<br/>Indian market"]
    end

    subgraph Output["📤 Output"]
        POS["🟢 Positive<br/>Bullish signal"]
        NEU["⚪ Neutral<br/>No signal"]
        NEG["🔴 Negative<br/>Bearish signal"]
        SCORE["📊 Confidence<br/>0.0 - 1.0"]
    end

    NEWS --> FINBERT
    TWEETS --> VADER
    REPORTS --> CUSTOM
    FINBERT --> POS & NEU & NEG
    VADER --> POS & NEU & NEG
    CUSTOM --> POS & NEU & NEG
    POS & NEG --> SCORE

    style Input2 fill:#3498DB,color:#fff,stroke:#2980B9
    style Models fill:#9B59B6,color:#fff,stroke:#8E44AD
    style Output fill:#2ECC71,color:#fff,stroke:#27AE60
    style NEWS fill:#2980B9,color:#fff
    style TWEETS fill:#00B4D8,color:#fff
    style REPORTS fill:#1ABC9C,color:#fff
    style FINBERT fill:#E74C3C,color:#fff
    style VADER fill:#F39C12,color:#fff
    style CUSTOM fill:#E67E22,color:#fff
    style POS fill:#27AE60,color:#fff
    style NEU fill:#7F8C8D,color:#fff
    style NEG fill:#C0392B,color:#fff
    style SCORE fill:#2ECC71,color:#fff
```

## 5. Transformer vs RNN Comparison

```mermaid
flowchart LR
    subgraph RNN["🔄 RNN (Sequential Processing)"]
        direction LR
        R1["Token 1"] --> R2["Token 2"] --> R3["Token 3"] --> R4["Token N"]
        R4 --> H["Hidden State"]
    end

    subgraph TRANS["⚡ Transformer (Parallel)"]
        T1["Token 1"]
        T2["Token 2"]
        T3["Token 3"]
        TN["Token N"]
        ATT["👁️ Self-Attention<br/>All pairs simultaneously"]
        T1 & T2 & T3 & TN --> ATT
    end

    style RNN fill:#E74C3C,color:#fff,stroke:#C0392B
    style TRANS fill:#2ECC71,color:#fff,stroke:#27AE60
    style R1 fill:#C0392B,color:#fff
    style R2 fill:#C0392B,color:#fff
    style R3 fill:#C0392B,color:#fff
    style R4 fill:#C0392B,color:#fff
    style H fill:#E74C3C,color:#fff
    style T1 fill:#27AE60,color:#fff
    style T2 fill:#27AE60,color:#fff
    style T3 fill:#27AE60,color:#fff
    style TN fill:#27AE60,color:#fff
    style ATT fill:#F39C12,color:#fff
```

## 6. spaCy Processing Pipeline

```mermaid
flowchart LR
    TEXT["📄 Input Text"] --> TOK2["✂️ Tokenizer"]
    TOK2 --> TAGGER["🏷️ POS Tagger<br/>noun, verb, adj"]
    TAGGER --> PARSER["🔗 Dependency Parser<br/>Subject, object"]
    PARSER --> NER2["🏷️ NER<br/>PERSON, ORG, GPE"]
    NER2 --> LEMMA["📝 Lemmatizer<br/>running → run"]
    LEMMA --> DOC["📦 Processed Doc"]

    DOC --> ENT["🏷️ doc.ents<br/>Named entities"]
    DOC --> SENTS["📋 doc.sents<br/>Sentences"]
    DOC --> TOKENS["✂️ doc[i]<br/>Token attributes"]
    DOC --> VECS["🔢 doc.vector<br/>Document embedding"]

    style TEXT fill:#3498DB,color:#fff
    style TOK2 fill:#2ECC71,color:#fff
    style TAGGER fill:#9B59B6,color:#fff
    style PARSER fill:#E67E22,color:#fff
    style NER2 fill:#E74C3C,color:#fff
    style LEMMA fill:#F39C12,color:#fff
    style DOC fill:#1ABC9C,color:#fff
    style ENT fill:#E74C3C,color:#fff
    style SENTS fill:#3498DB,color:#fff
    style TOKENS fill:#9B59B6,color:#fff
    style VECS fill:#2ECC71,color:#fff
```

## 7. Model Selection Guide

```mermaid
flowchart TD
    START["🤔 What NLP task?"] --> CLS{"📋 Classification?"}
    START --> EXT{"🏷️ Entity Extraction?"}
    START --> GEN{"✍️ Text Generation?"}
    START --> SIM{"🔍 Similarity?"}

    CLS -->|"Simple, fast"| TFIDF_LR["⚡ TF-IDF + LogReg<br/>Fast, interpretable"]
    CLS -->|"High accuracy"| BERT_CLS["🧠 BERT fine-tuned<br/>Best quality"]
    CLS -->|"Financial"| FB["💰 FinBERT<br/>Domain-specific"]

    EXT -->|"General"| SPACY["🚀 spaCy NER<br/>Fast, production-ready"]
    EXT -->|"Custom domain"| BERT_NER["🎯 BERT NER fine-tuned<br/>Custom entities"]
    EXT -->|"Zero-shot"| LLM_NER["🤖 LLM prompting<br/>No training data"]

    GEN -->|"Summarize"| BART["📝 BART / T5<br/>Seq2seq"]
    GEN -->|"Chat/Write"| GPT_GEN["💬 GPT / Claude<br/>Best generation"]

    SIM -->|"Embeddings"| SBERT["🔢 Sentence-BERT<br/>Fast cosine sim"]
    SIM -->|"Search"| DENSE_S["🔍 Dense Retrieval<br/>Semantic search"]

    style START fill:#3498DB,color:#fff
    style CLS fill:#E74C3C,color:#fff
    style EXT fill:#2ECC71,color:#fff
    style GEN fill:#9B59B6,color:#fff
    style SIM fill:#F39C12,color:#fff
    style TFIDF_LR fill:#E67E22,color:#fff
    style BERT_CLS fill:#C0392B,color:#fff
    style FB fill:#D35400,color:#fff
    style SPACY fill:#27AE60,color:#fff
    style BERT_NER fill:#1ABC9C,color:#fff
    style LLM_NER fill:#16A085,color:#fff
    style BART fill:#8E44AD,color:#fff
    style GPT_GEN fill:#7D3C98,color:#fff
    style SBERT fill:#D68910,color:#fff
    style DENSE_S fill:#D4AC0D,color:#fff
```

## 8. Financial NLP Architecture

```mermaid
flowchart TD
    subgraph Sources["📡 Data Sources"]
        NEWS_API["📰 News API<br/>Headlines"]
        NSE_ANN["🏛️ NSE Announcements<br/>Corporate actions"]
        SOCIAL["🐦 Social Media<br/>Twitter/Reddit"]
        FILINGS["📜 SEBI Filings<br/>Regulatory"]
    end

    subgraph NLP_Pipeline["🧠 NLP Pipeline"]
        PREPROC["⚙️ Preprocessing<br/>Clean, normalize"]
        NER_PIPE["🏷️ NER<br/>Extract entities"]
        SENT_PIPE["😊 Sentiment<br/>FinBERT scoring"]
        TOPIC["📋 Topic Detection<br/>Classify category"]
        REL["🎯 Relevance<br/>Filter noise"]
    end

    subgraph Signals["📊 Trading Signals"]
        SYMBOL_MAP["🔗 Symbol Mapping<br/>Entity → NSE ticker"]
        AGGREGATE["📈 Aggregate Sentiment<br/>Per symbol, per day"]
        COMBINE["🔀 Combine with<br/>Technical signals"]
        FINAL["🚀 Final Signal<br/>Direction + confidence"]
    end

    NEWS_API & NSE_ANN & SOCIAL & FILINGS --> PREPROC
    PREPROC --> NER_PIPE --> SYMBOL_MAP
    PREPROC --> SENT_PIPE --> AGGREGATE
    PREPROC --> TOPIC --> REL
    SYMBOL_MAP & AGGREGATE & REL --> COMBINE --> FINAL

    style Sources fill:#0f3460,color:#fff,stroke:#533483
    style NLP_Pipeline fill:#1a1a2e,color:#fff,stroke:#e94560
    style Signals fill:#1a1a2e,color:#fff,stroke:#2ECC71
    style NEWS_API fill:#E74C3C,color:#fff
    style NSE_ANN fill:#3498DB,color:#fff
    style SOCIAL fill:#00B4D8,color:#fff
    style FILINGS fill:#9B59B6,color:#fff
    style PREPROC fill:#2ECC71,color:#fff
    style NER_PIPE fill:#E67E22,color:#fff
    style SENT_PIPE fill:#F39C12,color:#fff
    style TOPIC fill:#D35400,color:#fff
    style REL fill:#E74C3C,color:#fff
    style SYMBOL_MAP fill:#1ABC9C,color:#fff
    style AGGREGATE fill:#2ECC71,color:#fff
    style COMBINE fill:#3498DB,color:#fff
    style FINAL fill:#27AE60,color:#fff
```

## 9. Attention Mechanism Deep Dive

```mermaid
flowchart TD
    subgraph Self_Att["👁️ Self-Attention (Transformer Core)"]
        INPUT_T["📥 Input Tokens<br/>x₁, x₂, ..., xₙ"]
        Q["🔵 Query (Q)<br/>What am I looking for?"]
        K["🟢 Key (K)<br/>What do I contain?"]
        V["🔴 Value (V)<br/>What information do I carry?"]
        SCORES["📊 Attention Scores<br/>softmax(QKᵀ/√dₖ)"]
        OUTPUT_T["📤 Weighted Sum<br/>Context-aware embeddings"]
    end

    INPUT_T --> Q & K & V
    Q --> SCORES
    K --> SCORES
    SCORES --> OUTPUT_T
    V --> OUTPUT_T

    subgraph Multi_Head["🧠 Multi-Head Attention"]
        H1["🔵 Head 1<br/>Syntax"]
        H2["🟢 Head 2<br/>Semantics"]
        H3["🔴 Head 3<br/>Position"]
        H4["🟣 Head 4<br/>Coreference"]
        CONCAT2["🔗 Concat + Linear"]
    end

    H1 & H2 & H3 & H4 --> CONCAT2

    style Self_Att fill:#0f3460,color:#fff,stroke:#533483
    style Multi_Head fill:#1a1a2e,color:#fff,stroke:#e94560
    style INPUT_T fill:#3498DB,color:#fff
    style Q fill:#2980B9,color:#fff
    style K fill:#2ECC71,color:#fff
    style V fill:#E74C3C,color:#fff
    style SCORES fill:#F39C12,color:#fff
    style OUTPUT_T fill:#9B59B6,color:#fff
    style H1 fill:#2980B9,color:#fff
    style H2 fill:#2ECC71,color:#fff
    style H3 fill:#E74C3C,color:#fff
    style H4 fill:#8E44AD,color:#fff
    style CONCAT2 fill:#E67E22,color:#fff
```

## 10. Learning Path

```mermaid
graph TD
    subgraph Week1["📗 Week 1-2: Foundations"]
        W1A["✂️ Text preprocessing<br/>Tokenization, cleaning"]
        W1B["📏 Regex for NLP<br/>Pattern matching"]
        W1C["📈 TF-IDF + BoW<br/>Feature extraction"]
    end

    subgraph Week2["📘 Week 3-4: Classical NLP"]
        W2A["🚀 spaCy pipeline<br/>NER, POS, dependency"]
        W2B["📋 Text classification<br/>TF-IDF + sklearn"]
        W2C["📊 Topic modeling<br/>LDA, BERTopic"]
    end

    subgraph Week3["📙 Week 5-6: Transformers"]
        W3A["🧠 BERT fine-tuning<br/>Classification, NER"]
        W3B["💰 FinBERT<br/>Financial sentiment"]
        W3C["🔢 Sentence-BERT<br/>Embeddings, similarity"]
    end

    subgraph Week4["📕 Week 7-8: Production"]
        W4A["⚙️ NLP pipelines<br/>Batch + real-time"]
        W4B["🎯 Custom NER<br/>Indian finance entities"]
        W4C["📡 Trading integration<br/>NLP → signals → exec"]
    end

    Week1 --> Week2 --> Week3 --> Week4

    style Week1 fill:#2ECC71,color:#fff,stroke:#27AE60
    style Week2 fill:#3498DB,color:#fff,stroke:#2980B9
    style Week3 fill:#E67E22,color:#fff,stroke:#D35400
    style Week4 fill:#E74C3C,color:#fff,stroke:#C0392B
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
