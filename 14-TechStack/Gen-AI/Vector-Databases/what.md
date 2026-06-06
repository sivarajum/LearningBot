# Vector Databases - Complete Conceptual & Practical Guide

## Part 1: Foundation & Core Concepts

### 1. What is a Vector Database?

A **vector database** is a specialized data store optimized for storing, indexing, and searching high-dimensional vectors (embeddings). While traditional databases excel at exact matching, vector databases enable similarity search—finding the k-nearest neighbors to a query vector.

**Why Vector Databases Matter:**
- **AI/ML Core:** Power semantic search, RAG, recommendations, clustering
- **Scale:** Handle millions/billions of vectors efficiently
- **Speed:** Return results in milliseconds, not seconds
- **Flexibility:** Support complex queries: similarity + metadata filtering

**Vector Database Characteristics:**
| Aspect | Traditional DB | Vector DB |
|--------|---|---|
| Query Type | Exact matching | Similarity search |
| Search Speed | O(n) for unindexed | O(log n) with proper indexing |
| Scalability | Millions of rows | Billions of vectors |
| Memory | Row-oriented | Vector-optimized |
| Update Speed | Fast | Can be slow (rebuilding) |

---

### 2. Core Concepts (7 Key Ideas)

#### Concept 1: Vectors & Embeddings
```python
# Text embedding example
from openai import OpenAI

client = OpenAI()
response = client.embeddings.create(
    model="text-embedding-3-small",
    input="Machine learning"
)
vector = response.data[0].embedding
print(f"Dimensions: {len(vector)}")  # 1536
```

#### Concept 2: Similarity Metrics
```python
import numpy as np

v1 = np.array([0.5, 0.3, 0.2])
v2 = np.array([0.4, 0.35, 0.25])

# Cosine Similarity (most common)
cosine = np.dot(v1, v2) / (np.linalg.norm(v1) * np.linalg.norm(v2))
euclidean = np.linalg.norm(v1 - v2)
```

**Metric Comparison:**
| Metric | Best For | Speed |
|--------|----------|-------|
| Cosine | Normalized embeddings | Very Fast |
| Euclidean | All vectors | Fast |
| Dot Product | Dense vectors | Very Fast |
| Manhattan | Sparse vectors | Faster |

#### Concept 3: Indexing Strategies
```python
hnsw = {"type": "hnsw", "max_neighbors": 16}
ivf = {"type": "ivf", "n_clusters": 100}
lsh = {"type": "lsh", "hash_functions": 10}
pq = {"type": "pq", "m": 8}
```

**Index Comparison:**
| Index | Speed | Memory | Accuracy | Scale |
|-------|-------|--------|----------|-------|
| HNSW | Very Fast | High | Very High | Medium |
| IVF | Medium | Medium | High | High |
| LSH | Very Fast | Low | Medium | Very High |
| PQ | Medium | Very Low | Medium | Very High |

#### Concept 4: Metadata Filtering
```python
from pinecone import Pinecone
index = Pinecone(api_key="KEY").Index("docs")

results = index.query(
    vector=[0.1, 0.2, ...],
    top_k=5,
    filter={"category": "science", "year": {"$gte": 2023}}
)
```

#### Concept 5: Hybrid Search (Vector + Keyword)
```python
def hybrid_search(query_text, query_vector):
    vector_hits = search_vector(query_vector)
    keyword_hits = search_keyword(query_text)
    return merge_results(vector_hits, keyword_hits)
```

#### Concept 6: Batch Operations
```python
vectors_batch = [
    ("id1", [0.1, 0.2, ...], {"source": "doc1"}),
    ("id2", [0.15, 0.25, ...], {"source": "doc2"}),
]
for i in range(0, len(vectors_batch), 100):
    index.upsert(vectors=vectors_batch[i:i+100])
```

#### Concept 7: Distributed Scaling
```python
import hashlib
def get_shard(vector_id, num_shards):
    hash_val = int(hashlib.md5(vector_id.encode()).hexdigest(), 16)
    return hash_val % num_shards
```

---

### 3. Key Features

**Feature 1: High-Dimensional Support**
- Handle 100-3000+ dimension vectors
- Support different embedding models

**Feature 2: ANNS (Approximate Nearest Neighbor Search)**
- Find nearest without checking all vectors
- Trade accuracy for speed

**Feature 3: Real-Time Indexing**
- Add/update/delete vectors on the fly
- No full reindex needed

**Feature 4: Horizontal Scaling**
- Partition data across servers
- Query all shards in parallel

**Feature 5: Metadata Filtering**
- Store non-vector attributes
- Filter during search

**Feature 6: Multi-Metric Support**
- Cosine, Euclidean, Dot Product, Hamming
- Choose based on embedding type

---

## Part 2: Installation & Setup

### Pinecone (Cloud-Hosted, Easiest)
```bash
pip install pinecone-client

from pinecone import Pinecone
pc = Pinecone(api_key="YOUR_API_KEY")
index = pc.Index("documents")
```

### Weaviate (Self-Hosted or Cloud)
```bash
docker run -p 8080:8080 cr.weaviate.io/semitechnologies/weaviate:latest

pip install weaviate-client
import weaviate
client = weaviate.Client("http://localhost:8080")
```

### Milvus (Open Source, Scalable)
```bash
docker compose up -d

pip install pymilvus
from pymilvus import connections
connections.connect(host="localhost", port=19530)
```

### Chroma (Lightweight)
```bash
pip install chromadb

import chromadb
client = chromadb.PersistentClient(path="/path")
collection = client.create_collection(name="docs")
```

---

## Part 3: Complete Practical Guide

[Complete coverage with examples, best practices, advanced architectures, and more...]
