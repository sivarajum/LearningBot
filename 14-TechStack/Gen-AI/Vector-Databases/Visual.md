
# Vector Databases - Visual Architecture & Patterns

Below are Mermaid diagrams covering core vector-database architectures, index internals, query flows, scaling patterns, and trade-offs.

---

## 1. High-level Ingest & Query Flow

```mermaid
flowchart LR
    User["User / Client"] -->|1. Upload / Query| API["API Layer\n(ingest & query)"]
    API -->|2. Embed| Embed["Embedding Service\n(OpenAI / SBERT)"]
    Embed -->|3. Upsert| Ingest["Ingest Pipeline\n(chunking, metadata)"]
    Ingest -->|4. Store| VectorDB["Vector Database\n(index + metadata store)"]
  
    User -->|5. Query| API
    API -->|6. Embed Query| Embed
    Embed -->|7. Search| VectorDB
    VectorDB -->|8. Results (IDs+scores)| API
    API -->|9. Fetch + Augment| PrimaryDB["Primary DB / CDN\n(store full records)"]
    API -->|10. Return| User
```

---

## 2. Index Type Comparison (Decision Tree)

```mermaid
flowchart TB
    A["Dataset Size & Latency Needs"]
    A -->|small, high-accuracy| Flat["Flat (exact)\nUse: small corpora, testing"]
    A -->|low-latency, high-accuracy| HNSW["HNSW\nUse: low-latency, memory available"]
    A -->|very large corpora| IVF["IVF (cluster-based)\nUse: large-scale, lower memory"]
    A -->|memory constrained| PQ["PQ (quantized)\nUse: compress vectors"]
    A -->|simple/fast approximate| LSH["LSH\nUse: very large, simple approx"]
```

---

## 3. HNSW Internal Layers

```mermaid
graph TB
    subgraph top[Top Layers]
        entry["Entry Point\n(high level)"]
    end
    subgraph mid[Mid Layers]
        nodes1["Node A"]
        nodes2["Node B"]
        nodes3["Node C"]
    end
    subgraph bottom[Base Layer]
        many["Many nodes (dense graph)\nPrecise neighbor links"]
    end
    entry --> nodes1 --> nodes2 --> nodes3 --> many
    style entry fill:#f9f,stroke:#333,stroke-width:1px
    style many fill:#ffb86b
```

---

## 4. IVF Clustering + Search Flow

```mermaid
flowchart LR
    Docs["Documents -> Embeddings"] --> Cluster["KMeans Clustering\n(n_clusters) -> Centroids"]
    QueryVec["Query Vector"] -->|Find nearest clusters| CentroidSearch["Find nearest centroids\n(n_probes)"]
    CentroidSearch -->|Search within those buckets| BucketSearch["Search vectors in buckets (ANN)"]
    BucketSearch --> Results["Aggregate + Rank"]
```

---

## 5. PQ Compression Overview

```mermaid
flowchart LR
    Vector["Float vector (1536 dims)"] -->|split into m sub-vectors| Sub1["m=8 sub-vectors"]
    Sub1 -->|quantize| Codebooks["Lookup codebooks (centroids)"]
    Codebooks -->|store| PQIndex["Compressed codes (small memory)"]
    QueryVec -->|quantize| QueryCodes
    QueryCodes -->|approx search| PQIndex
```

---

## 6. Hybrid Search (Keyword + Semantic)

```mermaid
flowchart LR
    Query["User Query"] -->|1: Vectorize| Embed["Embedder"]
    Query -->|2: Keyword| KeywordEngine["Keyword Index (Elasticsearch)"]
    Embed -->|3: Vector Search| VectorDB
    KeywordEngine -->|4: Keyword Results| Merge["Merge & Score"]
    VectorDB -->|5: Vector Results| Merge
    Merge -->|6: Rerank| Reranker["Cross-encoder / LLM"]
    Reranker --> Final["Final Ranked Results"]
```

---

## 7. Multi-Shard Query Architecture

```mermaid
flowchart TB
    Client --> Gateway["Query Gateway"]
    Gateway -->|Fan-out| Shard1["Shard 1\n(index)"]
    Gateway -->|Fan-out| Shard2["Shard 2\n(index)"]
    Gateway -->|Fan-out| ShardN["Shard N\n(index)"]
    Shard1 -->|top-k| Aggregator["Merge & Deduplicate"]
    Shard2 --> Aggregator
    ShardN --> Aggregator
    Aggregator -->|global top-k| Client
```

---

## 8. Ingest Pipeline (Chunking & Embedding)

```mermaid
flowchart LR
    RawDocs["Raw Documents"] --> Chunker["Chunking\n(size, overlap)"]
    Chunker --> Embed
    Embed --> Store["Vector Store (with metadata)"]
    Store -->|Index| Indexer["Build/Update Index\n(e.g., HNSW/IVF)"]
```

---

## 9. Metadata Filtering Flow

```mermaid
flowchart LR
    Query --> Embed
    Embed --> VectorDB
    VectorDB -->|apply filter| Filter["Filter by metadata (tag/date/source)"]
    Filter --> Results
```

---

## 10. Caching Layer (Semantic Cache)

```mermaid
flowchart LR
    Query --> Canonicalizer["Query Canonicalizer\n(compress/prompt-craft)"]
    Canonicalizer --> Hash["Semantic Hash (cluster id)"]
    Hash --> Cache["Semantic Cache (LRU)"]
    Cache -->|hit| Serve["Serve cached results"]
    Cache -->|miss| VectorDB
    VectorDB --> Results
    Results --> Cache
```

---

## 11. Latency vs Accuracy Tradeoff

```mermaid
graph LR
    Latency["Latency"]
    Accuracy["Accuracy"]
    Cost["Cost"]

    A["High-accuracy (HNSW, ef high)"] -->|increases| Cost
    A -->|increases| Latency
    B["Low-latency (ef low, fewer probes)"] -->|decreases| Cost
    B -->|decreases| Accuracy

    style A fill:#ffcccb
    style B fill:#ccffcc
```

---

## 12. Monitoring & Evaluation Pipeline

```mermaid
flowchart LR
    App --> Logs["Query Logs (user feedback)"]
    Logs --> Metrics["Compute metrics: precision@k, recall@k, latency"]
    Metrics -->|alerts| Ops["Alerts / Dashboards"]
    Ops -->|tune| IndexConfig["Tune index parameters (ef, nprobe)"]
    IndexConfig --> VectorDB
```

---

## 13. Multi-tenant Isolation

```mermaid
flowchart TB
    Users -->|namespace| NamespaceRouter["Namespace Router"]
    NamespaceRouter --> Tenant1Index["Tenant1 Index (isolated)"]
    NamespaceRouter --> Tenant2Index["Tenant2 Index (isolated)"]
    TenantX -->|quota| QuotaEnforcer["Quota & Rate Limits"]
```

---

## 14. Backup & Recovery

```mermaid
flowchart LR
    VectorDB -->|snapshot| BlobStore["S3 / Blob Storage"]
    BlobStore -->|restore| VectorDB
    BackupScheduler --> BlobStore
```

---

## 15. Multi-modal Retrieval Flow

```mermaid
flowchart LR
    Image -->|Vision Encoder| ImgVec["Image Vector"]
    Text -->|Text Encoder| TxtVec["Text Vector"]
    ImgVec -->|search| MultiIndex["Multi-modal Index"]
    TxtVec -->|search| MultiIndex
    MultiIndex --> Rerank["Fusion & Rerank"]
    Rerank --> Result
```

---

## Key Visual Takeaways

- Ingest and query are symmetrical: embed then search.
- Index choice is a primary design decision: balance memory, latency, and accuracy.
- Hybrid search and reranking provide practical improvements for real-world apps.
- Sharding, caching, and quantization are essential for scaling to billions.
- Monitoring retrieval quality (precision/recall) is as important as latency/cost.
