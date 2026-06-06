# RAG - Visual Architecture & Patterns Guide

## 1. Complete RAG Pipeline Flow

```mermaid
graph LR
    Query["👤 User Query<br/>'What is AI?'"]
    
    Query -->|1. Embed| QueryEmbed["🔢 Embed Query<br/>Convert to vector"]
    
    KB["📚 Knowledge Base<br/>Documents + Embeddings"]
    
    QueryEmbed -->|2. Search| Search["🔍 Vector Search<br/>Find similar docs<br/>Top-K matching"]
    
    KB -.->|Pre-computed| Search
    
    Search -->|3. Retrieve| Retrieved["📋 Retrieved Docs<br/>3-5 most relevant<br/>with scores"]
    
    Retrieved -->|4. Augment| Augment["📝 Augmented Prompt<br/>System + Context<br/>+ User Query"]
    
    Augment -->|5. Generate| LLM["🧠 LLM Generation<br/>Generate answer<br/>based on context"]
    
    LLM -->|6. Format| Response["✅ Final Response<br/>Grounded answer<br/>+ Sources"]
    
    Response --> Query
    
    style Query fill:#95E1D3
    style QueryEmbed fill:#4ECDC4
    style Search fill:#FFE66D
    style Retrieved fill:#FFE66D
    style Augment fill:#4ECDC4
    style LLM fill:#19C937
    style Response fill:#19C937
```

---

## 2. RAG Architecture Components

```mermaid
graph TB
    subgraph Documents["📚 Documents Layer"]
        Doc1["Raw Documents"]
        Chunk["Split into Chunks"]
    end
    
    subgraph Embeddings["🔢 Embeddings Layer"]
        Embed["Convert to Vectors<br/>1536 dimensions"]
        Store["Store in Vector DB<br/>Pinecone/Weaviate/Milvus"]
    end
    
    subgraph Retrieval["🔍 Retrieval Layer"]
        Index["Vector Index<br/>HNSW/IVF"]
        Search["Similarity Search<br/>Cosine/Euclidean"]
    end
    
    subgraph Generation["🧠 Generation Layer"]
        Context["Add Context<br/>to Prompt"]
        LLM["LLM Generation<br/>gpt-4"]
        Format["Format Output<br/>Add Citations"]
    end
    
    Doc1 --> Chunk
    Chunk --> Embed
    Embed --> Store
    
    User["User Query"]
    User --> Index
    Store --> Index
    Index --> Search
    Search --> Retrieval
    
    Retrieval -->|Retrieved Docs| Context
    User -->|User Query| Context
    Context --> LLM
    LLM --> Format
    Format --> User
    
    style Documents fill:#4ECDC4
    style Embeddings fill:#FFE66D
    style Retrieval fill:#FF6B6B
    style Generation fill:#19C937
```

---

## 3. Chunking Strategy Comparison

```mermaid
graph LR
    Doc["📄 Long Document"]
    
    Doc -->|Small Chunks<br/>100 words| Small["⚠️ Loses Context<br/>Precise retrieval<br/>High recall<br/>More API calls"]
    
    Doc -->|Optimal Chunks<br/>300-500 words| Optimal["✅ Best Balance<br/>Context preserved<br/>Faster retrieval<br/>Reasonable costs"]
    
    Doc -->|Large Chunks<br/>1000 words| Large["⚠️ Too Much Context<br/>May miss relevant<br/>Fewer chunks<br/>Imprecise"]
    
    style Doc fill:#FFE66D
    style Small fill:#FF6B6B
    style Optimal fill:#19C937
    style Large fill:#FF6B6B
```

---

## 4. Retrieval Quality Trade-off

```mermaid
graph TB
    Speed["⚡ Speed"]
    Quality["🎯 Quality"]
    Cost["💰 Cost"]
    
    Keyword["Keyword Search<br/>Fast ✓<br/>Cheap ✓<br/>Limited ✗"]
    
    Semantic["Semantic Search<br/>Better quality ✓<br/>More compute ✗<br/>Higher cost ✗"]
    
    Hybrid["Hybrid Search<br/>Good quality ✓<br/>Balanced speed ✓<br/>Moderate cost ✓"]
    
    Reranked["+ Reranking<br/>Best quality ✓<br/>Slower ✗<br/>Higher cost ✗"]
    
    Keyword -.-> Semantic
    Semantic -.-> Hybrid
    Hybrid -.-> Reranked
    
    style Keyword fill:#FF6B6B
    style Semantic fill:#FFE66D
    style Hybrid fill:#19C937
    style Reranked fill:#4ECDC4
```

---

## 5. Embedding & Similarity Computation

```mermaid
graph LR
    Query["🔍 Query<br/>'Machine learning'"]
    Doc1["📄 Doc1<br/>'ML uses algorithms'"]
    Doc2["📄 Doc2<br/>'Data science analysis'"]
    Doc3["📄 Doc3<br/>'Math fundamentals'"]
    
    Query -->|Vectorize| QV["V=[0.2, 0.8...]<br/>1536 dims"]
    Doc1 -->|Vectorize| D1V["V=[0.25, 0.79...]"]
    Doc2 -->|Vectorize| D2V["V=[0.15, 0.3...]"]
    Doc3 -->|Vectorize| D3V["V=[0.01, 0.2...]"]
    
    QV -->|Compare| Sim["Cosine Similarity"]
    D1V -->|with| Sim
    D2V -->|each| Sim
    D3V -->|vector| Sim
    
    Sim -->|Score| S1["Doc1: 0.95 ⭐⭐⭐"]
    Sim -->|Score| S2["Doc2: 0.72 ⭐⭐"]
    Sim -->|Score| S3["Doc3: 0.24 ⭐"]
    
    S1 -->|Rank| Results["✅ Results<br/>1. Doc1<br/>2. Doc2"]
    S2 -->|by| Results
    
    style Query fill:#4ECDC4
    style QV fill:#FFE66D
    style Sim fill:#FFE66D
    style S1 fill:#19C937
    style S2 fill:#FFE66D
    style S3 fill:#FF6B6B
    style Results fill:#19C937
```

---

## 6. Multi-Document RAG

```mermaid
graph TB
    Query["🔍 User Query"]
    
    Query -->|Search| Doc1Index["📚 Document 1<br/>Index"]
    Query -->|Search| Doc2Index["📚 Document 2<br/>Index"]
    Query -->|Search| Doc3Index["📚 Document 3<br/>Index"]
    
    Doc1Index -->|Retrieve| R1["Results from Doc 1<br/>Top 2 chunks"]
    Doc2Index -->|Retrieve| R2["Results from Doc 2<br/>Top 2 chunks"]
    Doc3Index -->|Retrieve| R3["Results from Doc 3<br/>Top 2 chunks"]
    
    R1 -->|Merge| Merged["📋 All Results<br/>From all documents<br/>Ranked by relevance"]
    R2 -->|&| Merged
    R3 -->|Combine| Merged
    
    Merged -->|Top-3| Selected["✅ Selected<br/>Best 3 results<br/>Mixed sources"]
    
    Selected -->|Context| LLM["🧠 LLM<br/>Synthesize answer<br/>from multiple sources"]
    
    LLM --> Response["✅ Answer<br/>Cites all sources"]
    
    style Query fill:#95E1D3
    style Doc1Index fill:#4ECDC4
    style Doc2Index fill:#4ECDC4
    style Doc3Index fill:#4ECDC4
    style Merged fill:#FFE66D
    style Selected fill:#FFE66D
    style LLM fill:#19C937
    style Response fill:#19C937
```

---

## 7. RAG vs Fine-tuning Comparison

```mermaid
graph TB
    Task["🎯 Need Domain Knowledge"]
    
    Task -->|Dynamic, Frequently Updated| RAG["✅ RAG<br/>Add docs anytime<br/>No retraining<br/>Current knowledge<br/>Higher latency"]
    
    Task -->|Static, Fixed Style| FT["✅ Fine-tuning<br/>Train once<br/>Permanent knowledge<br/>Fast inference<br/>Expensive update"]
    
    Task -->|Both Dynamic & Style| Hybrid["✅ Hybrid<br/>RAG + Fine-tuned<br/>Best of both<br/>Most complex"]
    
    style Task fill:#FFE66D
    style RAG fill:#19C937
    style FT fill:#FF6B6B
    style Hybrid fill:#4ECDC4
```

---

## 8. Reranking Strategy

```mermaid
graph LR
    Query["🔍 Query"]
    
    Query -->|Retrieve Many| Candidates["📋 Initial Retrieval<br/>10 candidates<br/>Ranked by embedding"]
    
    Candidates -->|Method 1| LLMRerank["🧠 LLM Reranking<br/>Ask model to rate<br/>Cost: 1 LLM call"]
    
    Candidates -->|Method 2| CrossEnc["🔗 Cross-Encoder<br/>Specialized model<br/>Faster than LLM"]
    
    Candidates -->|Method 3| Hybrid["⚖️ Rules + Scores<br/>Custom logic<br/>Instant"]
    
    LLMRerank -->|Result| Final["✅ Final Results<br/>3 best candidates<br/>High confidence"]
    CrossEnc -->|Result| Final
    Hybrid -->|Result| Final
    
    style Query fill:#95E1D3
    style Candidates fill:#FFE66D
    style LLMRerank fill:#FF6B6B
    style CrossEnc fill:#4ECDC4
    style Hybrid fill:#FFE66D
    style Final fill:#19C937
```

---

## 9. Vector Database Index Types

```mermaid
graph TB
    VectorDB["🗄️ Vector Database<br/>Store embeddings"]
    
    VectorDB -->|Type 1| HNSW["🔀 HNSW<br/>Hierarchical<br/>Graph-based<br/>Fast ✓<br/>Memory ✗"]
    
    VectorDB -->|Type 2| IVF["📊 IVF<br/>Inverted File<br/>Clustering<br/>Scalable ✓<br/>Less accurate ✗"]
    
    VectorDB -->|Type 3| LSH["🎲 LSH<br/>Locality Sensitive<br/>Hashing<br/>Fast ✓<br/>Approx only ✗"]
    
    VectorDB -->|Type 4| Tree["🌳 Tree-based<br/>KD-Tree, Quadtree<br/>Structured<br/>Good for low-dim"]
    
    style VectorDB fill:#FFE66D
    style HNSW fill:#19C937
    style IVF fill:#4ECDC4
    style LSH fill:#FF6B6B
    style Tree fill:#95E1D3
```

---

## 10. Token Count Impact

```mermaid
graph TB
    Query["Query<br/>100 tokens"]
    
    Retrieved1["1 Document<br/>300 tokens"]
    Retrieved2["3 Documents<br/>900 tokens"]
    Retrieved5["5 Documents<br/>1500 tokens"]
    
    Query -->|+| Retrieved1 -->|Total| Total1["🔹 400 tokens<br/>Cost: Low<br/>Context: Limited"]
    
    Query -->|+| Retrieved2 -->|Total| Total2["🔹 1000 tokens<br/>Cost: Medium<br/>Context: Good"]
    
    Query -->|+| Retrieved5 -->|Total| Total5["🔹 1600 tokens<br/>Cost: High<br/>Context: Rich"]
    
    style Query fill:#FFE66D
    style Retrieved1 fill:#95E1D3
    style Retrieved2 fill:#4ECDC4
    style Retrieved5 fill:#FF6B6B
    style Total1 fill:#95E1D3
    style Total2 fill:#19C937
    style Total5 fill:#FF6B6B
```

---

## 11. RAG Error Sources

```mermaid
graph TB
    Query["🔍 User Query"]
    
    Query -->|Poor Retrieval| Error1["❌ Wrong Docs Retrieved<br/>Cause: Bad embedding<br/>Fix: Rerank, expand query"]
    
    Query -->|Good Retrieval<br/>but Poor Augmentation| Error2["❌ Lost Context in Prompt<br/>Cause: Prompt engineering<br/>Fix: Better prompts"]
    
    Query -->|Both Good<br/>but LLM Fails| Error3["❌ Generation Error<br/>Cause: Hallucination<br/>Fix: Constraints, validation"]
    
    Error1 -->|Track| Metrics["📊 Monitor Metrics<br/>Retrieval precision<br/>Generation quality<br/>End-to-end accuracy"]
    Error2 -->|Track| Metrics
    Error3 -->|Track| Metrics
    
    Metrics -->|Improve| RAG["✅ Better RAG System"]
    
    style Query fill:#95E1D3
    style Error1 fill:#FF6B6B
    style Error2 fill:#FF6B6B
    style Error3 fill:#FF6B6B
    style Metrics fill:#FFE66D
    style RAG fill:#19C937
```

---

## 12. RAG Learning Path

```mermaid
graph TD
    Start["🚀 START"]
    
    Start -->|Week 1| B1["📚 Beginner Phase<br/>Understand RAG<br/>Simple retrieval<br/>Basic LLM answer"]
    
    B1 -->|Week 2| B2["🔨 Build Simple RAG<br/>In-memory storage<br/>Basic chunks<br/>Simple prompt"]
    
    B2 -->|Week 3| I1["📈 Intermediate Phase<br/>Chunking strategies<br/>Retrieval quality<br/>Multi-document"]
    
    I1 -->|Week 4| I2["🔧 Advanced Retrieval<br/>Hybrid search<br/>Reranking<br/>Query expansion"]
    
    I2 -->|Week 5| A1["🏗️ Advanced Phase<br/>Vector databases<br/>Production systems<br/>Monitoring"]
    
    A1 -->|Week 6| A2["⚙️ Optimization<br/>Caching strategies<br/>Batch processing<br/>Cost reduction"]
    
    A2 --> End["✅ COMPLETE"]
    
    style Start fill:#95E1D3
    style B1 fill:#FFE66D
    style B2 fill:#FFE66D
    style I1 fill:#4ECDC4
    style I2 fill:#4ECDC4
    style A1 fill:#FF6B6B
    style A2 fill:#FF6B6B
    style End fill:#19C937
```

---

## 13. Chunking Impact on Retrieval

```mermaid
graph LR
    LargeDoc["📄 Large Document<br/>10,000 words"]
    
    LargeDoc -->|Too Small<br/>50 words| SmallChunk["Chunks: 200<br/>Pro: Precise<br/>Con: Lost context<br/>Con: Many API calls"]
    
    LargeDoc -->|Optimal<br/>300-500 words| OptimalChunk["Chunks: 20-30<br/>Pro: Good context<br/>Pro: Balanced<br/>Pro: Reasonable calls"]
    
    LargeDoc -->|Too Large<br/>2000 words| LargeChunk["Chunks: 5<br/>Pro: Few calls<br/>Con: Too much<br/>Con: Lost relevance"]
    
    SmallChunk -.-> Tradeoff["⚖️ Chunk Size<br/>Trade-off Context<br/>vs Precision"]
    OptimalChunk -.-> Tradeoff
    LargeChunk -.-> Tradeoff
    
    Tradeoff -->|Choose| Optimal
    
    style LargeDoc fill:#FFE66D
    style SmallChunk fill:#FF6B6B
    style OptimalChunk fill:#19C937
    style LargeChunk fill:#FF6B6B
    style Tradeoff fill:#4ECDC4
```

---

## 14. Cost vs Latency

```mermaid
graph LR
    A["Keyword Only<br/>Fast ✓<br/>Cheap ✓<br/>Bad results ✗"]
    
    B["+ Semantic<br/>Medium speed<br/>Medium cost<br/>Good results"]
    
    C["+ Reranking<br/>Slow ✗<br/>Expensive ✗<br/>Best results ✓"]
    
    A -->|Add complexity| B -->|Add complexity| C
    
    B --> Sweet["✅ Sweet Spot<br/>Best ROI<br/>Most useful"]
    
    style A fill:#19C937
    style B fill:#FFE66D
    style C fill:#FF6B6B
    style Sweet fill:#4ECDC4
```

---

## 15. RAG Scaling Architecture

```mermaid
graph TB
    Users["👥 Users"]
    
    Users -->|Requests| Cache["⚡ Cache<br/>LRU Cache<br/>Deduplicate"]
    
    Cache -->|Hit| Return["✅ Return"]
    Cache -->|Miss| Router["🔀 Router<br/>Partition<br/>Select index"]
    
    Router -->|Small<br/>corpus| Partition1["Index 1<br/>10K docs<br/>Fast"]
    Router -->|Medium<br/>corpus| Partition2["Index 2<br/>100K docs<br/>Standard"]
    Router -->|Large<br/>corpus| Partition3["Index 3<br/>1M docs<br/>Distributed"]
    
    Partition1 -->|Retrieve| Search["🔍 Search<br/>Vector DB<br/>HNSW Index"]
    Partition2 -->|Retrieve| Search
    Partition3 -->|Retrieve| Search
    
    Search -->|Results| LLM["🧠 LLM<br/>Generate answer"]
    
    LLM -->|Answer| Return
    
    Return --> Users
    
    style Users fill:#95E1D3
    style Cache fill:#19C937
    style Router fill:#FFE66D
    style Partition1 fill:#4ECDC4
    style Partition2 fill:#4ECDC4
    style Partition3 fill:#4ECDC4
    style Search fill:#FF6B6B
    style LLM fill:#19C937
```

---

## Key Insights from Visuals

1. **Pipeline:** Query → Embed → Search → Retrieve → Augment → Generate → Response
2. **Quality:** Chunking, retrieval method, reranking all critical
3. **Trade-offs:** Speed, cost, quality form a triangle
4. **Scaling:** Vector DBs, partitioning, caching essential
5. **Monitoring:** Track retrieval quality and generation quality separately
6. **Learning:** Incremental improvement from simple to advanced

