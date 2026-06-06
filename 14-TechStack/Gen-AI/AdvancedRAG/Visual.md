# Advanced RAG: Visual Guide & Architecture Diagrams

## 1. Basic vs Advanced RAG Pipeline

```mermaid
graph TD
    subgraph BASIC["📦 Basic RAG"]
        BQ["❓ Query"] --> BE["🔢 Embed"] --> BS["🔍 Vector Search"] --> BG["🧠 Generate"]
    end

    subgraph ADVANCED["🚀 Advanced RAG"]
        AQ["❓ Query"] --> QT["🔄 Query Transform<br/>(HyDE, Decompose)"]
        QT --> HS["🔍 Hybrid Search<br/>(Dense + Sparse)"]
        HS --> RR["📊 Re-Rank<br/>(Cross-Encoder)"]
        RR --> GRADE["✅ Grade Relevance<br/>(CRAG)"]
        GRADE --> GEN["🧠 Generate"]
        GEN --> VERIFY["🔍 Verify Faithfulness"]
        VERIFY -->|"❌ Hallucination"| QT
        VERIFY -->|"✅ Grounded"| OUT["📎 Output + Citations"]
    end

    style BASIC fill:#0f3460,color:#fff,stroke:#533483
    style ADVANCED fill:#1a1a2e,color:#fff,stroke:#e94560
    style BQ fill:#95A5A6,color:#fff
    style BE fill:#95A5A6,color:#fff
    style BS fill:#95A5A6,color:#fff
    style BG fill:#95A5A6,color:#fff
    style AQ fill:#3498DB,color:#fff
    style QT fill:#9B59B6,color:#fff
    style HS fill:#E74C3C,color:#fff
    style RR fill:#F39C12,color:#fff
    style GRADE fill:#E67E22,color:#fff
    style GEN fill:#8E44AD,color:#fff
    style VERIFY fill:#2ECC71,color:#fff
    style OUT fill:#27AE60,color:#fff,stroke:#1E8449
```

## 2. Query Transformation Techniques

```mermaid
flowchart TD
    Q["❓ User Query<br/>'Best performing oil stocks?'"]

    Q --> HYDE["🔮 HyDE<br/>Generate hypothetical answer,<br/>embed that instead"]
    Q --> DECOMP["🔀 Decomposition<br/>1. 'Oil sector stocks'<br/>2. 'Performance metrics'<br/>3. 'Top performers ranking'"]
    Q --> EXPAND["📝 Expansion<br/>'oil stocks petroleum<br/>energy crude oil sector'"]
    Q --> STEPBACK["🔙 Step-Back<br/>'How to evaluate sector<br/>stock performance?'"]

    HYDE --> SEARCH["🔍 Vector Search"]
    DECOMP --> SEARCH
    EXPAND --> SEARCH
    STEPBACK --> SEARCH

    style Q fill:#3498DB,color:#fff,stroke:#2980B9
    style HYDE fill:#2ECC71,color:#fff,stroke:#27AE60
    style DECOMP fill:#E74C3C,color:#fff,stroke:#C0392B
    style EXPAND fill:#F39C12,color:#fff,stroke:#E67E22
    style STEPBACK fill:#9B59B6,color:#fff,stroke:#8E44AD
    style SEARCH fill:#1ABC9C,color:#fff
```

## 3. Hybrid Search Architecture

```mermaid
flowchart LR
    Q["❓ Query"] --> BM25["📝 BM25<br/>(Keyword / Sparse)"]
    Q --> DENSE["🔢 Dense Retriever<br/>(Embedding)"]

    BM25 --> K1["📋 Top 15<br/>(exact matches)"]
    DENSE --> K2["📋 Top 15<br/>(semantic)"]

    K1 --> RRF["🔄 Reciprocal Rank<br/>Fusion (RRF)"]
    K2 --> RRF

    RRF --> RERANK["🏆 Cross-Encoder<br/>Re-Ranker"]
    RERANK --> TOP["✅ Top 5<br/>Final Results"]

    style Q fill:#3498DB,color:#fff
    style BM25 fill:#E74C3C,color:#fff,stroke:#C0392B
    style DENSE fill:#2ECC71,color:#fff,stroke:#27AE60
    style K1 fill:#C0392B,color:#fff
    style K2 fill:#27AE60,color:#fff
    style RRF fill:#F39C12,color:#fff,stroke:#E67E22
    style RERANK fill:#9B59B6,color:#fff,stroke:#8E44AD
    style TOP fill:#1ABC9C,color:#fff,stroke:#16A085
```

## 4. Corrective RAG (CRAG) Flow

```mermaid
flowchart TD
    Q["❓ Query"] --> RET["🔍 Retrieve K docs"]
    RET --> GRADE{"📊 Grade Each<br/>Document"}
    GRADE -->|"✅ All Relevant"| GEN["🧠 Generate Answer"]
    GRADE -->|"⚠️ Mixed"| FILTER["🔀 Use Relevant +<br/>Web Search Supplement"]
    GRADE -->|"❌ None Relevant"| WEB["🌐 Web Search Fallback"]

    FILTER --> GEN
    WEB --> GEN

    GEN --> HAL{"🔍 Hallucination<br/>Check"}
    HAL -->|"✅ Grounded"| OUT["✅ Final Answer"]
    HAL -->|"❌ Hallucinated"| RETRY["🔄 Retry (max 2)"]
    RETRY --> RET

    style Q fill:#3498DB,color:#fff
    style RET fill:#9B59B6,color:#fff
    style GRADE fill:#F39C12,color:#fff,stroke:#E67E22
    style GEN fill:#8E44AD,color:#fff
    style FILTER fill:#E67E22,color:#fff
    style WEB fill:#E74C3C,color:#fff
    style HAL fill:#E74C3C,color:#fff,stroke:#C0392B
    style OUT fill:#2ECC71,color:#fff,stroke:#27AE60
    style RETRY fill:#F39C12,color:#fff
```

## 5. Chunking Strategies Comparison

```mermaid
graph TB
    subgraph FIX["📏 Fixed Size Chunking"]
        F1["📄 Chunk 1<br/>(500 tok)"]
        F2["📄 Chunk 2<br/>(500 tok)"]
        F3["📄 Chunk 3<br/>(500 tok)"]
    end

    subgraph SEM["🧠 Semantic Chunking"]
        S1["💭 Topic A<br/>(350 tok)"]
        S2["💭 Topic B<br/>(600 tok)"]
        S3["💭 Topic C<br/>(400 tok)"]
    end

    subgraph PC["👪 Parent-Child"]
        P["📚 Parent (1500 tok)"]
        P --> C1["📄 Child (300)"]
        P --> C2["📄 Child (300)"]
        P --> C3["📄 Child (300)"]
    end

    style FIX fill:#2ECC71,color:#fff,stroke:#27AE60
    style SEM fill:#3498DB,color:#fff,stroke:#2980B9
    style PC fill:#E74C3C,color:#fff,stroke:#C0392B
    style F1 fill:#27AE60,color:#fff
    style F2 fill:#27AE60,color:#fff
    style F3 fill:#27AE60,color:#fff
    style S1 fill:#2980B9,color:#fff
    style S2 fill:#2980B9,color:#fff
    style S3 fill:#2980B9,color:#fff
    style P fill:#C0392B,color:#fff
    style C1 fill:#E67E22,color:#fff
    style C2 fill:#E67E22,color:#fff
    style C3 fill:#E67E22,color:#fff
```

## 6. RAGAS Evaluation Framework

```mermaid
graph TD
    subgraph RQ["🔍 Retrieval Quality"]
        CP["📊 Context Precision<br/>(Are top docs relevant?)"]
        CR["📊 Context Recall<br/>(Found all relevant docs?)"]
    end

    subgraph GQ["🧠 Generation Quality"]
        F["✅ Faithfulness<br/>(Grounded in context?)"]
        AR["🎯 Answer Relevancy<br/>(Addresses question?)"]
    end

    CP --> SCORE["📈 RAG Quality Score"]
    CR --> SCORE
    F --> SCORE
    AR --> SCORE

    SCORE --> GOOD{"Score > 0.85?"}
    GOOD -->|"✅ Yes"| PROD["✅ Production Ready"]
    GOOD -->|"❌ No"| IMPROVE["⚙️ Iterate & Improve"]

    style RQ fill:#0f3460,color:#fff,stroke:#533483
    style GQ fill:#1a1a2e,color:#fff,stroke:#e94560
    style CP fill:#3498DB,color:#fff
    style CR fill:#3498DB,color:#fff
    style F fill:#E74C3C,color:#fff
    style AR fill:#E74C3C,color:#fff
    style SCORE fill:#F39C12,color:#fff,stroke:#E67E22
    style GOOD fill:#9B59B6,color:#fff
    style PROD fill:#2ECC71,color:#fff,stroke:#27AE60
    style IMPROVE fill:#E67E22,color:#fff
```

## 7. Graph RAG Architecture

```mermaid
graph TD
    Q["❓ Query:<br/>'RELIANCE competitors<br/>in oil sector'"]

    Q --> KG["🕸️ Knowledge Graph<br/>Query"]
    Q --> VS["🔢 Vector Store<br/>Search"]

    KG --> FACTS["📊 Structured Facts:<br/>RELIANCE → competitor → ONGC<br/>RELIANCE → sector → Oil_Gas<br/>ONGC → market_cap → ₹3.2T"]

    VS --> DOCS["📄 Relevant Documents:<br/>'RELIANCE market share...'<br/>'ONGC quarterly report...'"]

    FACTS --> COMBINE["🔗 Combine Contexts"]
    DOCS --> COMBINE

    COMBINE --> LLM["🧠 LLM Generate<br/>(Grounded Answer)"]

    style Q fill:#3498DB,color:#fff
    style KG fill:#2ECC71,color:#fff,stroke:#27AE60
    style VS fill:#E74C3C,color:#fff,stroke:#C0392B
    style FACTS fill:#27AE60,color:#fff
    style DOCS fill:#C0392B,color:#fff
    style COMBINE fill:#F39C12,color:#fff,stroke:#E67E22
    style LLM fill:#9B59B6,color:#fff,stroke:#8E44AD
```

## 8. Financial RAG Pipeline (Trading Research)

```mermaid
flowchart TD
    subgraph Sources["📚 Document Sources"]
        AR["📈 Annual Reports<br/>BSE filings"]
        NEWS["📰 News Articles<br/>Google News RSS"]
        SEBI["🏛️ SEBI Circulars<br/>Regulatory updates"]
        EARN["💰 Earnings Calls<br/>Transcripts"]
    end

    subgraph Ingest["⚙️ Ingestion Pipeline"]
        PARSE["📋 Parse & Clean"]
        CHUNK["✂️ Semantic Chunking<br/>(Financial-aware)"]
        EMBED["🔢 Embed<br/>(FinBERT / BGE)"]
        INDEX["💾 Vector Store<br/>(Pinecone / Qdrant)"]
    end

    subgraph Query["❓ Research Query"]
        USER["📊 'What is RELIANCE<br/>debt-to-equity trend?'"]
        HYBRID["🔍 Hybrid Search<br/>BM25 + Dense"]
        RERANK["🏆 FinBERT Reranker"]
        GEN["🧠 LLM + Citations"]
        OUT["✅ Grounded Answer<br/>+ Source Links"]
    end

    Sources --> PARSE --> CHUNK --> EMBED --> INDEX
    USER --> HYBRID --> RERANK --> GEN --> OUT

    style Sources fill:#0f3460,color:#fff,stroke:#533483
    style Ingest fill:#1a1a2e,color:#fff,stroke:#e94560
    style Query fill:#1a1a2e,color:#fff,stroke:#2ECC71
    style AR fill:#3498DB,color:#fff
    style NEWS fill:#E74C3C,color:#fff
    style SEBI fill:#9B59B6,color:#fff
    style EARN fill:#F39C12,color:#fff
    style PARSE fill:#E67E22,color:#fff
    style CHUNK fill:#00B4D8,color:#fff
    style EMBED fill:#2ECC71,color:#fff
    style INDEX fill:#1ABC9C,color:#fff
    style USER fill:#3498DB,color:#fff
    style HYBRID fill:#E74C3C,color:#fff
    style RERANK fill:#9B59B6,color:#fff
    style GEN fill:#8E44AD,color:#fff
    style OUT fill:#27AE60,color:#fff,stroke:#1E8449
```

## 9. Learning Path

```mermaid
graph TD
    subgraph W1["📗 Week 1: Foundations"]
        B1["📦 Basic RAG<br/>Embed → Search → Generate"]
        B2["✂️ Chunking Strategies<br/>Semantic, Parent-Child"]
    end

    subgraph W2["📘 Week 2: Search"]
        I1["🔍 Hybrid Search<br/>BM25 + Dense"]
        I2["🏆 Re-Ranking<br/>Cross-Encoder"]
    end

    subgraph W3["📙 Week 3: Self-Correction"]
        A1["🔄 CRAG<br/>Corrective RAG"]
        A2["🔍 Hallucination Detection<br/>Faithfulness checks"]
    end

    subgraph W4["📕 Week 4: Advanced"]
        P1["🕸️ Graph RAG<br/>KG + Vector"]
        P2["📊 Evaluation<br/>RAGAS metrics"]
    end

    W1 --> W2 --> W3 --> W4

    style W1 fill:#2ECC71,color:#fff,stroke:#27AE60
    style W2 fill:#3498DB,color:#fff,stroke:#2980B9
    style W3 fill:#E67E22,color:#fff,stroke:#D35400
    style W4 fill:#E74C3C,color:#fff,stroke:#C0392B
    style B1 fill:#27AE60,color:#fff
    style B2 fill:#27AE60,color:#fff
    style I1 fill:#2980B9,color:#fff
    style I2 fill:#2980B9,color:#fff
    style A1 fill:#D35400,color:#fff
    style A2 fill:#D35400,color:#fff
    style P1 fill:#C0392B,color:#fff
    style P2 fill:#C0392B,color:#fff
```
