# RAG (Retrieval Augmented Generation) - Complete Learning Guide

## Table of Contents
1. [Definition & Problem Statement](#definition--problem-statement)
2. [Core Concepts & Principles](#core-concepts--principles)
3. [RAG Architecture Components](#rag-architecture-components)
4. [Installation & Setup](#installation--setup)
5. [Beginner Examples](#beginner-examples)
6. [Intermediate Patterns](#intermediate-patterns)
7. [Advanced Architectures](#advanced-architectures)
8. [Best Practices & Optimization](#best-practices--optimization)
9. [Common Pitfalls & Solutions](#common-pitfalls--solutions)
10. [Comparison with Alternatives](#comparison-with-alternatives)
11. [Real-World Use Cases](#real-world-use-cases)
12. [Performance & Scaling](#performance--scaling)

---

## Definition & Problem Statement

### What is RAG?

**RAG (Retrieval Augmented Generation)** is a technique that combines document retrieval with LLM generation to provide accurate, grounded answers based on specific knowledge sources. Instead of relying on the LLM's training data alone, RAG retrieves relevant documents first, then uses them to augment the LLM's context.

### Problems It Solves

**Without RAG:**
- LLM generates based on training data only (knowledge cutoff)
- Hallucinations and inaccuracies
- Cannot use proprietary/private data
- No source attribution
- Expensive fine-tuning for new knowledge
- Model doesn't learn from new documents

**With RAG:**
- Current information from any date
- Grounded in source documents
- Uses proprietary data safely
- Source attribution possible
- No retraining needed
- Updates just by adding documents

---

## Core Concepts & Principles

### 1. **Document Embeddings**
Convert documents to numerical vectors capturing semantic meaning.

```python
from openai import OpenAI

client = OpenAI()

# Create embeddings for documents
documents = [
    "Python is a programming language",
    "Machine learning uses algorithms",
    "Data science analyzes data patterns"
]

response = client.embeddings.create(
    model="text-embedding-3-small",
    input=documents
)

embeddings = [item.embedding for item in response.data]
print(f"Embedding dimension: {len(embeddings[0])}")  # 1536
```

### 2. **Vector Storage**
Store embeddings in databases for fast retrieval.

```python
import numpy as np

class SimpleVectorStore:
    def __init__(self):
        self.documents = []
        self.embeddings = []

    def add(self, doc, embedding):
        self.documents.append(doc)
        self.embeddings.append(embedding)

    def search(self, query_embedding, top_k=3):
        """Find k most similar documents"""
        similarities = []
        for emb in self.embeddings:
            sim = np.dot(query_embedding, emb) / (
                np.linalg.norm(query_embedding) * np.linalg.norm(emb)
            )
            similarities.append(sim)

        top_indices = np.argsort(similarities)[-top_k:][::-1]
        return [self.documents[i] for i in top_indices]
```

### 3. **Retrieval**
Find most relevant documents for a query.

```python
def retrieve_documents(query, documents, embeddings, top_k=3):
    """Retrieve most relevant documents"""
    # Embed query
    query_response = client.embeddings.create(
        model="text-embedding-3-small",
        input=[query]
    )
    query_embedding = query_response.data[0].embedding

    # Find similar documents
    similarities = []
    for emb in embeddings:
        similarity = np.dot(query_embedding, emb) / (
            np.linalg.norm(query_embedding) * np.linalg.norm(emb)
        )
        similarities.append(similarity)

    top_indices = np.argsort(similarities)[-top_k:][::-1]
    return [documents[i] for i in top_indices]
```

### 4. **Augmentation**
Add retrieved documents to LLM prompt.

```python
def augment_prompt(query, retrieved_docs):
    """Create augmented prompt with context"""
    context = "\n\n".join(retrieved_docs)

    augmented_prompt = f"""Use the following context to answer the question.

Context:
{context}

Question: {query}

Answer based only on the context above."""

    return augmented_prompt
```

### 5. **Generation**
LLM generates answer using augmented context.

```python
def rag_answer(query, documents, embeddings):
    """Complete RAG pipeline"""
    # Step 1: Retrieve
    retrieved = retrieve_documents(query, documents, embeddings)

    # Step 2: Augment
    augmented = augment_prompt(query, retrieved)

    # Step 3: Generate
    response = client.chat.completions.create(
        model="gpt-4",
        messages=[
            {"role": "system", "content": "You are a helpful assistant"},
            {"role": "user", "content": augmented}
        ]
    )

    return response.choices[0].message.content
```

### 6. **Chunking**
Split large documents into manageable pieces.

```python
def chunk_document(text, chunk_size=500, overlap=50):
    """Split document into overlapping chunks"""
    chunks = []
    for i in range(0, len(text), chunk_size - overlap):
        chunk = text[i:i + chunk_size]
        chunks.append(chunk)
    return chunks

# Example
document = "This is a very long document..."
chunks = chunk_document(document, chunk_size=500)
print(f"Created {len(chunks)} chunks")
```

### 7. **Reranking**
Re-score retrieved documents for better quality.

```python
def rerank_documents(query, documents, scores, model="cross-encoder"):
    """Rerank retrieved documents"""
    reranked = sorted(
        zip(documents, scores),
        key=lambda x: x[1],
        reverse=True
    )
    return [doc for doc, score in reranked[:3]]
```

---

## RAG Architecture Components

```
Input Query
    ↓
[Query Embedding] → [Vector Search] → [Retrieve Documents]
    ↓                                           ↓
              [Augment Prompt with Context]
    ↓
[LLM Generation] → [Format Response]
    ↓
Output Answer with Sources
```

---

## Installation & Setup

### Prerequisites
- Python 3.8+
- OpenAI API key
- Vector database (optional but recommended)

### Installation

```bash
# Core dependencies
pip install openai tiktoken numpy

# For advanced vector search
pip install pinecone-client  # Pinecone
pip install weaviate-client  # Weaviate
pip install pymilvus         # Milvus

# For document processing
pip install pypdf python-docx beautifulsoup4

# For embeddings
pip install sentence-transformers

# For development
pip install python-dotenv pytest
```

### Basic Setup

```python
import os
from openai import OpenAI

# Set API key
os.environ["OPENAI_API_KEY"] = "sk-..."

client = OpenAI()

# Test
response = client.embeddings.create(
    model="text-embedding-3-small",
    input=["test"]
)
print("Setup successful!")
```

---

## Beginner Examples

### Example 1: Simple RAG with In-Memory Storage

```python
from openai import OpenAI
import numpy as np

client = OpenAI()

class SimpleRAG:
    def __init__(self):
        self.documents = []
        self.embeddings = []

    def add_documents(self, docs):
        """Add documents to knowledge base"""
        response = client.embeddings.create(
            model="text-embedding-3-small",
            input=docs
        )

        self.documents = docs
        self.embeddings = [item.embedding for item in response.data]

    def search(self, query, top_k=3):
        """Find relevant documents"""
        query_response = client.embeddings.create(
            model="text-embedding-3-small",
            input=[query]
        )
        query_embedding = query_response.data[0].embedding

        similarities = []
        for emb in self.embeddings:
            sim = np.dot(query_embedding, emb) / (
                np.linalg.norm(query_embedding) * np.linalg.norm(emb)
            )
            similarities.append(sim)

        top_indices = np.argsort(similarities)[-top_k:][::-1]
        return [self.documents[i] for i in top_indices]

    def answer(self, query):
        """Answer query using RAG"""
        docs = self.search(query)
        context = "\n\n".join(docs)

        response = client.chat.completions.create(
            model="gpt-4",
            messages=[{
                "role": "user",
                "content": f"Context:\n{context}\n\nQuestion: {query}"
            }]
        )
        return response.choices[0].message.content

# Usage
rag = SimpleRAG()
rag.add_documents([
    "Python is a programming language",
    "Machine learning uses algorithms",
    "Data science analyzes data"
])
answer = rag.answer("What is Python?")
print(answer)
```

### Example 2: RAG with Document Chunks

```python
def chunk_text(text, chunk_size=300):
    """Split text into chunks"""
    words = text.split()
    chunks = []
    for i in range(0, len(words), chunk_size):
        chunk = " ".join(words[i:i + chunk_size])
        chunks.append(chunk)
    return chunks

# Prepare knowledge base
long_document = """
Python is a high-level programming language known for its simplicity.
It supports multiple programming paradigms and has a comprehensive standard library.
Machine learning in Python uses libraries like scikit-learn and TensorFlow.
Data science workflows often use Pandas for data manipulation and Matplotlib for visualization.
"""

chunks = chunk_text(long_document)
rag.add_documents(chunks)

answer = rag.answer("What libraries does Python use for ML?")
print(answer)
```

### Example 3: RAG with Metadata

```python
class RAGWithMetadata:
    def __init__(self):
        self.documents = []
        self.embeddings = []
        self.metadata = []

    def add_document(self, text, source="unknown", date="unknown"):
        """Add document with metadata"""
        response = client.embeddings.create(
            model="text-embedding-3-small",
            input=[text]
        )

        self.documents.append(text)
        self.embeddings.append(response.data[0].embedding)
        self.metadata.append({
            "source": source,
            "date": date
        })

    def search_with_metadata(self, query, top_k=3):
        """Search and return with sources"""
        query_response = client.embeddings.create(
            model="text-embedding-3-small",
            input=[query]
        )
        query_embedding = query_response.data[0].embedding

        similarities = []
        for emb in self.embeddings:
            sim = np.dot(query_embedding, emb) / (
                np.linalg.norm(query_embedding) * np.linalg.norm(emb)
            )
            similarities.append(sim)

        top_indices = np.argsort(similarities)[-top_k:][::-1]
        results = []
        for idx in top_indices:
            results.append({
                "text": self.documents[idx],
                "source": self.metadata[idx]["source"],
                "date": self.metadata[idx]["date"],
                "similarity": similarities[idx]
            })
        return results

# Usage
rag_meta = RAGWithMetadata()
rag_meta.add_document("Python is a programming language", source="wikipedia", date="2024-01-01")
rag_meta.add_document("ML uses algorithms", source="research paper", date="2024-02-01")

results = rag_meta.search_with_metadata("What is Python?")
for result in results:
    print(f"Source: {result['source']} | Similarity: {result['similarity']:.2f}")
    print(f"Text: {result['text']}\n")
```

---

## Intermediate Patterns

### Pattern 1: Hybrid Search (Keyword + Semantic)

```python
from sklearn.feature_extraction.text import TfidfVectorizer
import numpy as np

class HybridSearch:
    def __init__(self):
        self.documents = []
        self.embeddings = []
        self.vectorizer = TfidfVectorizer()

    def add_documents(self, docs):
        """Add documents with both semantic and keyword indexing"""
        # Semantic embeddings
        response = client.embeddings.create(
            model="text-embedding-3-small",
            input=docs
        )
        self.embeddings = [item.embedding for item in response.data]

        # Keyword indexing
        self.vectorizer.fit(docs)
        self.documents = docs

    def search(self, query, top_k=3, semantic_weight=0.7):
        """Search using both semantic and keyword matching"""
        # Semantic search
        query_response = client.embeddings.create(
            model="text-embedding-3-small",
            input=[query]
        )
        query_embedding = query_response.data[0].embedding

        semantic_scores = []
        for emb in self.embeddings:
            sim = np.dot(query_embedding, emb) / (
                np.linalg.norm(query_embedding) * np.linalg.norm(emb)
            )
            semantic_scores.append(sim)

        # Keyword search
        query_vector = self.vectorizer.transform([query])
        doc_vectors = self.vectorizer.transform(self.documents)
        keyword_scores = (doc_vectors * query_vector.T).toarray().flatten()

        # Combine scores
        combined = np.array(semantic_scores) * semantic_weight + \
                  np.array(keyword_scores) * (1 - semantic_weight)

        top_indices = np.argsort(combined)[-top_k:][::-1]
        return [self.documents[i] for i in top_indices]
```

### Pattern 2: Query Expansion

```python
def expand_query(original_query):
    """Expand query with synonyms and related terms"""
    response = client.chat.completions.create(
        model="gpt-4",
        messages=[{
            "role": "user",
            "content": f"""Generate 3 alternative phrasings of this query:

Original: {original_query}

Return as comma-separated list."""
        }]
    )

    alternatives = response.choices[0].message.content.split(",")
    all_queries = [original_query] + alternatives
    return [q.strip() for q in all_queries]

# Usage
queries = expand_query("What is machine learning?")
print(queries)  # Original + 3 alternatives
```

### Pattern 3: Multi-Step RAG with Reranking

```python
class MultiStepRAG:
    def __init__(self, docs, embeddings):
        self.documents = docs
        self.embeddings = embeddings

    def retrieve_candidates(self, query, num_candidates=10):
        """Initial retrieval with more results"""
        response = client.embeddings.create(
            model="text-embedding-3-small",
            input=[query]
        )
        query_embedding = response.data[0].embedding

        similarities = []
        for emb in self.embeddings:
            sim = np.dot(query_embedding, emb) / (
                np.linalg.norm(query_embedding) * np.linalg.norm(emb)
            )
            similarities.append(sim)

        top_indices = np.argsort(similarities)[-num_candidates:][::-1]
        return [(self.documents[i], similarities[i]) for i in top_indices]

    def rerank(self, query, candidates, top_k=3):
        """Rerank using LLM"""
        # Ask LLM to score relevance
        prompt = f"""Rate relevance of each document to the query on scale 0-10.

Query: {query}

Documents to rate:
"""
        for i, (doc, _) in enumerate(candidates):
            prompt += f"\n{i+1}. {doc[:100]}..."

        # For simplicity, just return top semantic matches
        # In production, use cross-encoder model
        return candidates[:top_k]

    def answer(self, query):
        """Complete pipeline"""
        candidates = self.retrieve_candidates(query, num_candidates=5)
        reranked = self.rerank(query, candidates, top_k=3)
        context = "\n\n".join([doc for doc, _ in reranked])

        response = client.chat.completions.create(
            model="gpt-4",
            messages=[{
                "role": "user",
                "content": f"Context:\n{context}\n\nQuestion: {query}"
            }]
        )
        return response.choices[0].message.content
```

---

## Advanced Architectures

### Architecture 1: Production RAG with Caching

```python
import hashlib
from functools import lru_cache

class ProductionRAG:
    def __init__(self, documents, embeddings):
        self.documents = documents
        self.embeddings = embeddings
        self.cache = {}
        self.retrieval_cache = {}

    def _get_query_hash(self, query):
        """Create cache key for query"""
        return hashlib.md5(query.encode()).hexdigest()

    def retrieve_cached(self, query, top_k=3):
        """Retrieve with caching"""
        query_hash = self._get_query_hash(query)

        if query_hash in self.retrieval_cache:
            return self.retrieval_cache[query_hash]

        # Not cached, retrieve
        response = client.embeddings.create(
            model="text-embedding-3-small",
            input=[query]
        )
        query_embedding = response.data[0].embedding

        similarities = []
        for emb in self.embeddings:
            sim = np.dot(query_embedding, emb) / (
                np.linalg.norm(query_embedding) * np.linalg.norm(emb)
            )
            similarities.append(sim)

        top_indices = np.argsort(similarities)[-top_k:][::-1]
        results = [self.documents[i] for i in top_indices]

        # Cache results
        self.retrieval_cache[query_hash] = results
        return results

    def answer_cached(self, query):
        """Answer with end-to-end caching"""
        query_hash = self._get_query_hash(query)

        if query_hash in self.cache:
            return self.cache[query_hash]

        docs = self.retrieve_cached(query)
        context = "\n\n".join(docs)

        response = client.chat.completions.create(
            model="gpt-4",
            messages=[{
                "role": "user",
                "content": f"Context:\n{context}\n\nQuestion: {query}"
            }]
        )

        answer = response.choices[0].message.content
        self.cache[query_hash] = answer
        return answer
```

### Architecture 2: Multi-Index RAG

```python
class MultiIndexRAG:
    """RAG with multiple vector indices for different document types"""

    def __init__(self):
        self.indices = {}  # Different indices for different doc types

    def add_index(self, name, documents):
        """Add new document index"""
        response = client.embeddings.create(
            model="text-embedding-3-small",
            input=documents
        )

        self.indices[name] = {
            "documents": documents,
            "embeddings": [item.embedding for item in response.data]
        }

    def search_all(self, query, top_k=3):
        """Search across all indices"""
        results = {}

        query_response = client.embeddings.create(
            model="text-embedding-3-small",
            input=[query]
        )
        query_embedding = query_response.data[0].embedding

        for index_name, index in self.indices.items():
            similarities = []
            for emb in index["embeddings"]:
                sim = np.dot(query_embedding, emb) / (
                    np.linalg.norm(query_embedding) * np.linalg.norm(emb)
                )
                similarities.append(sim)

            top_indices = np.argsort(similarities)[-top_k:][::-1]
            results[index_name] = [
                index["documents"][i] for i in top_indices
            ]

        return results
```

### Architecture 3: Streaming RAG Response

```python
def stream_rag_answer(query, documents, embeddings):
    """RAG with streaming response"""
    # Retrieve documents
    response = client.embeddings.create(
        model="text-embedding-3-small",
        input=[query]
    )
    query_embedding = response.data[0].embedding

    similarities = []
    for emb in embeddings:
        sim = np.dot(query_embedding, emb) / (
            np.linalg.norm(query_embedding) * np.linalg.norm(emb)
        )
        similarities.append(sim)

    top_indices = np.argsort(similarities)[-3:][::-1]
    context = "\n\n".join([documents[i] for i in top_indices])

    # Stream response
    with client.chat.completions.create(
        model="gpt-4",
        messages=[{
            "role": "user",
            "content": f"Context:\n{context}\n\nQuestion: {query}"
        }],
        stream=True
    ) as stream:
        for text in stream.text_stream:
            print(text, end="", flush=True)
```

---

## Best Practices & Optimization

### 1. **Optimal Chunk Size**

```python
# Too small: Loss of context
chunk_size_small = 100  # Words

# Too large: Inefficient retrieval
chunk_size_large = 1000  # Words

# Sweet spot: Balance context and precision
chunk_size_optimal = 300  # Words

def determine_chunk_size(document_type):
    """Choose chunk size based on content"""
    if document_type == "code":
        return 200  # Keep functions together
    elif document_type == "research":
        return 400  # Need more context
    else:
        return 300  # Default
```

### 2. **Batch Processing**

```python
def batch_embed_documents(documents, batch_size=100):
    """Embed documents in batches to avoid rate limits"""
    embeddings = []
    for i in range(0, len(documents), batch_size):
        batch = documents[i:i + batch_size]
        response = client.embeddings.create(
            model="text-embedding-3-small",
            input=batch
        )
        embeddings.extend([item.embedding for item in response.data])
        print(f"Embedded {i + len(batch)}/{len(documents)}")
    return embeddings
```

### 3. **Efficient Storage**

```python
import json

def save_embeddings(documents, embeddings, filename="embeddings.json"):
    """Save embeddings for reuse"""
    data = {
        "documents": documents,
        "embeddings": embeddings  # Convert to list if numpy
    }
    with open(filename, "w") as f:
        json.dump(data, f)

def load_embeddings(filename="embeddings.json"):
    """Load saved embeddings"""
    with open(filename, "r") as f:
        data = json.load(f)
    return data["documents"], data["embeddings"]
```

---

## Common Pitfalls & Solutions

### Pitfall 1: Poor Chunk Boundaries

```python
# ❌ Bad: Split in middle of sentence
chunks = text.split("\n")[:100]

# ✅ Good: Respect sentence boundaries
def smart_chunk(text, max_length=300):
    sentences = text.split(". ")
    chunks = []
    current = ""

    for sentence in sentences:
        if len(current) + len(sentence) < max_length:
            current += sentence + ". "
        else:
            chunks.append(current)
            current = sentence + ". "

    if current:
        chunks.append(current)

    return chunks
```

### Pitfall 2: Insufficient Context

```python
# ❌ Bad: Too few retrieved documents
top_k = 1

# ✅ Good: Retrieve enough for context
top_k = 3  # Get diverse perspectives

# ✅ Better: Dynamic top-k based on query
def dynamic_top_k(query):
    query_length = len(query.split())
    return max(3, min(10, query_length // 3))
```

### Pitfall 3: Stale Data

```python
# ❌ Bad: Assuming old documents are still relevant
# Static knowledge base never updated

# ✅ Good: Regular updates with versioning
def update_knowledge_base(new_docs, version):
    timestamp = datetime.now().isoformat()
    for doc in new_docs:
        store.add({
            "content": doc,
            "version": version,
            "updated": timestamp
        })
```

---

## Comparison with Alternatives

| Approach | Pros | Cons | Use Case |
|----------|------|------|----------|
| **RAG** | Current data, grounded, no retraining | Extra latency, retrieval errors | General knowledge, proprietary data |
| **Fine-tuning** | Permanent knowledge, fast | Expensive, outdated, retraining needed | Specific style, domain expertise |
| **Prompting** | Simple, no infrastructure | Limited context, hallucinations | Quick prototyping |
| **Vector DB** | Scalable, fast | Complex setup, maintenance | Large-scale production |
| **Hybrid** | Best of both | Complex, expensive | Enterprise systems |

---

## Real-World Use Cases

### 1. **Customer Support**
- Retrieve relevant support articles
- Answer based on knowledge base
- Include source links

### 2. **Research Assistant**
- Query large research corpus
- Cite relevant papers
- Synthesize information

### 3. **Code Documentation**
- Search code examples
- Explain relevant functions
- Provide working samples

### 4. **Legal Document Analysis**
- Retrieve relevant clauses
- Answer questions about contracts
- Highlight important sections

### 5. **Medical Information**
- Query medical databases
- Answer health questions safely
- Cite authoritative sources

---

## Performance & Scaling

### Retrieval Metrics

```python
def evaluate_retrieval(retrieved, relevant):
    """Calculate retrieval quality metrics"""
    # Precision: What % of retrieved are relevant
    precision = len(set(retrieved) & set(relevant)) / len(retrieved)

    # Recall: What % of relevant are retrieved
    recall = len(set(retrieved) & set(relevant)) / len(relevant)

    # F1: Harmonic mean
    f1 = 2 * (precision * recall) / (precision + recall)

    return {"precision": precision, "recall": recall, "f1": f1}
```

### Scaling Strategies

1. **Batch Processing:** Embed documents overnight
2. **Caching:** Cache frequent queries
3. **Vector Indexing:** Use specialized databases
4. **Distributed Search:** Parallel retrieval
5. **Approximate Search:** Trade accuracy for speed

---

## Conclusion

RAG is a powerful pattern combining the strengths of retrieval and generation. Success depends on:
- Proper chunking strategy
- Quality embeddings
- Efficient retrieval
- Contextual LLM prompting
- Continuous monitoring

Master RAG to build grounded, accurate AI applications.
