# Vector Databases - Complete Guide (Basic to Advanced)

## 🎯 What are Vector Databases?

**Vector Databases** store and search high-dimensional vectors (embeddings) for similarity search. Critical for RAG systems, with 82% of AI architect roles requiring this expertise.

### Why Vector Databases?
- **Semantic Search**: Find similar content by meaning
- **RAG Systems**: Retrieve relevant context for LLMs
- **Scalability**: Handle millions of vectors
- **Performance**: Fast similarity search
- **Production-Ready**: Built for scale

---

## 📚 Learning Path: Basic → Intermediate → Advanced

---

## 🟢 LEVEL 1: BASIC (Getting Started)

### Basic Concepts

```python
import pinecone
from sentence_transformers import SentenceTransformer

# Initialize
pinecone.init(api_key="your-key")
index = pinecone.Index("my-index")

# Generate embeddings
model = SentenceTransformer('all-MiniLM-L6-v2')
embeddings = model.encode(["Hello world", "Hi there"])

# Upsert vectors
index.upsert(vectors=[
    ("id1", embeddings[0].tolist(), {"text": "Hello world"}),
    ("id2", embeddings[1].tolist(), {"text": "Hi there"})
])

# Query
results = index.query(
    vector=embeddings[0].tolist(),
    top_k=5
)
```

### Key Concepts

#### 1. **Embeddings**
- Vector representations of text/images
- High-dimensional (384, 768, 1536 dimensions)
- Capture semantic meaning

#### 2. **Similarity Search**
- Find similar vectors
- Cosine similarity, dot product, Euclidean distance
- Fast approximate nearest neighbor (ANN)

#### 3. **Metadata Filtering**
- Filter by metadata alongside vector search
- Example: Filter by date, category

#### 4. **Indexing**
- Organize vectors for fast search
- HNSW, IVF, LSH algorithms

### Basic Example: RAG System

```python
from pinecone import Pinecone
from sentence_transformers import SentenceTransformer

# Initialize
pc = Pinecone(api_key="your-key")
index = pc.Index("rag-index")
model = SentenceTransformer('all-MiniLM-L6-v2')

# Index documents
documents = ["Document 1 text", "Document 2 text"]
embeddings = model.encode(documents)

for i, (doc, emb) in enumerate(zip(documents, embeddings)):
    index.upsert(vectors=[(f"doc_{i}", emb.tolist(), {"text": doc})])

# Query
query = "What is the main topic?"
query_embedding = model.encode([query])[0]
results = index.query(
    vector=query_embedding.tolist(),
    top_k=3,
    include_metadata=True
)

# Retrieve context for LLM
context = [r.metadata['text'] for r in results.matches]
```

---

## 🟡 LEVEL 2: INTERMEDIATE (Production Patterns)

### Pinecone (Managed)

```python
from pinecone import Pinecone, ServerlessSpec

# Create index
pc = Pinecone(api_key="your-key")
pc.create_index(
    name="production-index",
    dimension=384,
    metric="cosine",
    spec=ServerlessSpec(
        cloud="aws",
        region="us-east-1"
    )
)

# Batch upsert
vectors = []
for i in range(1000):
    vectors.append((f"id_{i}", embedding.tolist(), {"text": text}))

index.upsert(vectors=vectors, batch_size=100)

# Query with metadata filter
results = index.query(
    vector=query_embedding.tolist(),
    top_k=10,
    filter={"category": "technical", "date": {"$gte": "2024-01-01"}},
    include_metadata=True
)
```

### Weaviate (Open-Source)

```python
import weaviate

# Connect
client = weaviate.Client("http://localhost:8080")

# Create schema
schema = {
    "class": "Document",
    "properties": [
        {"name": "text", "dataType": ["text"]},
        {"name": "category", "dataType": ["string"]}
    ]
}
client.schema.create_class(schema)

# Add documents
client.data_object.create(
    data_object={"text": "Document text", "category": "tech"},
    class_name="Document",
    vector=embedding.tolist()
)

# Query
result = client.query.get(
    "Document", ["text", "category"]
).with_near_vector({
    "vector": query_embedding.tolist()
}).with_limit(5).do()
```

### FAISS (Local)

```python
import faiss
import numpy as np

# Create index
dimension = 384
index = faiss.IndexFlatL2(dimension)  # L2 distance

# Add vectors
vectors = np.array(embeddings).astype('float32')
index.add(vectors)

# Search
query_vector = np.array([query_embedding]).astype('float32')
k = 5
distances, indices = index.search(query_vector, k)

# Get results
results = [documents[i] for i in indices[0]]
```

---

## 🔴 LEVEL 3: ADVANCED (Production Excellence)

### Hybrid Search (Vector + Keyword)

```python
# Combine vector and keyword search
from pinecone import Pinecone

pc = Pinecone(api_key="your-key")
index = pc.Index("hybrid-index")

# Vector search
vector_results = index.query(
    vector=query_embedding.tolist(),
    top_k=10
)

# Keyword search (BM25)
keyword_results = bm25_search(query, documents)

# Combine and rerank
combined = combine_results(vector_results, keyword_results)
reranked = rerank(combined, query)
```

### RAG Optimization

```python
# Chunking strategy
def chunk_documents(text, chunk_size=500, overlap=50):
    chunks = []
    for i in range(0, len(text), chunk_size - overlap):
        chunk = text[i:i+chunk_size]
        chunks.append(chunk)
    return chunks

# Embedding optimization
from sentence_transformers import SentenceTransformer

# Use domain-specific model
model = SentenceTransformer('sentence-transformers/all-mpnet-base-v2')

# Batch processing
embeddings = model.encode(documents, batch_size=32, show_progress_bar=True)

# Index with metadata
for chunk, emb in zip(chunks, embeddings):
    index.upsert(vectors=[(
        f"chunk_{i}",
        emb.tolist(),
        {
            "text": chunk,
            "document_id": doc_id,
            "chunk_index": i,
            "metadata": metadata
        }
    )])
```

### Production Deployment

```python
# Connection pooling
from pinecone import Pinecone

pc = Pinecone(api_key="your-key")
index = pc.Index("production-index")

# Async operations
import asyncio
from pinecone import AsyncPinecone

async def async_query(query_embedding):
    async_pc = AsyncPinecone(api_key="your-key")
    index = async_pc.Index("production-index")
    results = await index.query(
        vector=query_embedding.tolist(),
        top_k=5
    )
    return results

# Monitoring
def query_with_monitoring(query_embedding):
    start_time = time.time()
    results = index.query(vector=query_embedding.tolist(), top_k=5)
    latency = time.time() - start_time
    
    # Log metrics
    log_metric("query_latency", latency)
    log_metric("results_count", len(results.matches))
    
    return results
```

---

## 🏗️ Architecture Patterns

### Pattern 1: Simple RAG
```
Documents → Embeddings → Vector DB → Query → Retrieve → LLM
```

### Pattern 2: Hybrid Search
```
Query → Vector Search + Keyword Search → Combine → Rerank → LLM
```

### Pattern 3: Multi-Stage Retrieval
```
Query → Coarse Search (100 results) → Fine Search (10 results) → LLM
```

---

## 🔗 Integration with LangChain

```python
from langchain.vectorstores import Pinecone
from langchain.embeddings import OpenAIEmbeddings

# Initialize
embeddings = OpenAIEmbeddings()
vectorstore = Pinecone.from_documents(
    documents=docs,
    embedding=embeddings,
    index_name="langchain-index"
)

# Query
retriever = vectorstore.as_retriever(search_kwargs={"k": 5})
docs = retriever.get_relevant_documents("query")
```

---

## 📊 Best Practices

### 1. **Choose Right Embedding Model**
```python
# General purpose
model = SentenceTransformer('all-MiniLM-L6-v2')  # Fast, 384 dim

# Better quality
model = SentenceTransformer('all-mpnet-base-v2')  # Slower, 768 dim

# Domain-specific
model = SentenceTransformer('sentence-transformers/all-MiniLM-L6-v2')
```

### 2. **Optimize Chunk Size**
```python
# Too small: Loses context
# Too large: Exceeds token limits
# Optimal: 500-1000 tokens with 100-200 overlap
```

### 3. **Use Metadata Filtering**
```python
# Filter by category, date, etc.
results = index.query(
    vector=query_embedding.tolist(),
    filter={"category": "technical", "date": {"$gte": "2024-01-01"}},
    top_k=10
)
```

### 4. **Batch Operations**
```python
# Batch upsert for efficiency
index.upsert(vectors=vectors, batch_size=100)
```

### 5. **Monitor Performance**
```python
# Track query latency, recall, precision
# Optimize based on metrics
```

---

## 🎯 Key Takeaways

1. **Vector DBs = Semantic Search**
2. **Embeddings = Vector Representations**
3. **Similarity = Cosine/Dot Product**
4. **RAG = Retrieve + Generate**
5. **Hybrid = Vector + Keyword**

---

## 📚 Next Steps

1. ✅ Read this guide
2. 📊 Review `Visual.md` for flows
3. 💬 Practice `Interview.md` questions
4. 🏗️ Build RAG systems
5. 🎯 Explain it confidently

