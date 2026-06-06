# RAG - Interview Q&A Guide

## Beginner Level (8 Questions)

### Q1: What is RAG and why is it needed?

**Answer:**
RAG (Retrieval Augmented Generation) combines document retrieval with LLM generation. Instead of relying on the LLM's training data, RAG retrieves relevant documents first, then uses them to answer questions.

**Code Example:**
```python
# Without RAG: LLM answers from training data
response = client.chat.completions.create(
    model="gpt-4",
    messages=[{"role": "user", "content": "What's in my company's handbook?"}]
)
# Result: Hallucinated or generic answer

# With RAG: LLM answers from retrieved documents
context = retrieve_from_handbook(query)
response = client.chat.completions.create(
    model="gpt-4",
    messages=[{
        "role": "user",
        "content": f"Context: {context}\n\nQuestion: What's in my company's handbook?"
    }]
)
# Result: Accurate answer based on actual handbook
```

---

### Q2: What are the main components of a RAG system?

**Answer:**
1. **Documents:** Knowledge base to retrieve from
2. **Embeddings:** Convert text to vectors
3. **Vector Store:** Store & retrieve embeddings
4. **Retriever:** Find relevant documents
5. **Augmenter:** Add context to prompt
6. **Generator:** LLM generates answer

**Code Example:**
```python
class RAGPipeline:
    def __init__(self, documents):
        # Component 1: Documents
        self.documents = documents

        # Component 2: Create embeddings
        response = client.embeddings.create(
            model="text-embedding-3-small",
            input=documents
        )
        self.embeddings = [item.embedding for item in response.data]

    def answer(self, query):
        # Component 3: Vector store (in-memory for this example)
        # Component 4: Retrieve
        retrieved = self.retrieve(query, top_k=3)

        # Component 5: Augment
        context = "\n\n".join(retrieved)
        prompt = f"Context: {context}\n\nQuestion: {query}"

        # Component 6: Generate
        response = client.chat.completions.create(
            model="gpt-4",
            messages=[{"role": "user", "content": prompt}]
        )
        return response.choices[0].message.content

    def retrieve(self, query, top_k=3):
        # Simplified retrieval
        return self.documents[:top_k]
```

---

### Q3: How do embeddings work in RAG?

**Answer:**
Embeddings convert text into numerical vectors that capture semantic meaning. Documents and queries with similar meaning have vectors close together in vector space.

**Code Example:**
```python
import numpy as np

# Create embeddings
docs = ["Python is a language", "Machine learning uses algorithms"]
response = client.embeddings.create(
    model="text-embedding-3-small",
    input=docs
)

# Get vectors
emb1 = np.array(response.data[0].embedding)
emb2 = np.array(response.data[1].embedding)

# Measure similarity
similarity = np.dot(emb1, emb2) / (np.linalg.norm(emb1) * np.linalg.norm(emb2))
print(f"Similarity: {similarity:.3f}")  # Higher = more similar
```

---

### Q4: What is chunking and why is it important?

**Answer:**
Chunking splits large documents into smaller pieces for better retrieval. Good chunks have enough context but are small enough for precise retrieval.

**Code Example:**
```python
def chunk_document(text, chunk_size=300):
    """Split text into chunks"""
    words = text.split()
    chunks = []
    for i in range(0, len(words), chunk_size):
        chunk = " ".join(words[i:i + chunk_size])
        chunks.append(chunk)
    return chunks

document = "Long text here..."
chunks = chunk_document(document, chunk_size=300)
print(f"Created {len(chunks)} chunks")
```

---

### Q5: How do you measure retrieval quality?

**Answer:**
Key metrics:
- **Precision:** % of retrieved documents that are relevant
- **Recall:** % of relevant documents that are retrieved
- **F1:** Balance between precision & recall

**Code Example:**
```python
def evaluate_retrieval(retrieved_docs, relevant_docs):
    """Calculate retrieval metrics"""
    retrieved_set = set(retrieved_docs)
    relevant_set = set(relevant_docs)

    # Precision
    precision = len(retrieved_set & relevant_set) / len(retrieved_set)

    # Recall
    recall = len(retrieved_set & relevant_set) / len(relevant_set)

    # F1
    f1 = 2 * (precision * recall) / (precision + recall)

    return {
        "precision": precision,
        "recall": recall,
        "f1": f1
    }
```

---

### Q6: What is the difference between semantic and keyword search?

**Answer:**
- **Keyword:** Exact word matches (fast, literal)
- **Semantic:** Meaning-based matching (slower, contextual)
- **Hybrid:** Combines both

**Code Example:**
```python
# Keyword search
def keyword_search(query, documents):
    query_words = set(query.lower().split())
    scores = []
    for doc in documents:
        doc_words = set(doc.lower().split())
        match_count = len(query_words & doc_words)
        scores.append(match_count / len(query_words))
    return scores

# Semantic search
def semantic_search(query, documents, embeddings):
    response = client.embeddings.create(
        model="text-embedding-3-small",
        input=[query]
    )
    query_emb = np.array(response.data[0].embedding)

    scores = []
    for emb in embeddings:
        emb = np.array(emb)
        sim = np.dot(query_emb, emb) / (np.linalg.norm(query_emb) * np.linalg.norm(emb))
        scores.append(sim)
    return scores

# Hybrid
def hybrid_search(query, documents, embeddings, weight=0.5):
    keyword_scores = keyword_search(query, documents)
    semantic_scores = semantic_search(query, documents, embeddings)

    combined = np.array(keyword_scores) * (1 - weight) + \
              np.array(semantic_scores) * weight
    return combined
```

---

### Q7: How do you handle documents longer than context window?

**Answer:**
Split into chunks, embed each chunk, retrieve relevant chunks, and use them as context.

**Code Example:**
```python
def handle_long_document(large_doc, query, chunk_size=500):
    """Process document longer than context window"""
    # Step 1: Chunk the document
    chunks = chunk_document(large_doc, chunk_size)

    # Step 2: Embed all chunks
    response = client.embeddings.create(
        model="text-embedding-3-small",
        input=chunks
    )
    embeddings = [item.embedding for item in response.data]

    # Step 3: Find relevant chunks
    query_response = client.embeddings.create(
        model="text-embedding-3-small",
        input=[query]
    )
    query_emb = np.array(query_response.data[0].embedding)

    similarities = []
    for emb in embeddings:
        sim = np.dot(query_emb, np.array(emb)) / (
            np.linalg.norm(query_emb) * np.linalg.norm(np.array(emb))
        )
        similarities.append(sim)

    # Step 4: Get top chunks
    top_indices = np.argsort(similarities)[-3:][::-1]
    context = "\n\n".join([chunks[i] for i in top_indices])

    # Step 5: Generate answer
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

### Q8: What are common RAG challenges?

**Answer:**
1. **Relevance:** Wrong documents retrieved
2. **Context:** Not enough context
3. **Recency:** Outdated documents
4. **Scale:** Slow for large corpora
5. **Cost:** Embedding & LLM costs

**Solutions:**
```python
# Challenge 1: Improve relevance with reranking
def rerank(query, candidates, top_k=3):
    """Use LLM to rerank candidates"""
    # Simplified: just return top semantic matches
    return candidates[:top_k]

# Challenge 2: Add overlapping chunks
def overlapping_chunks(text, chunk_size=300, overlap=50):
    """Create overlapping chunks for context"""
    chunks = []
    for i in range(0, len(text), chunk_size - overlap):
        chunk = text[i:i + chunk_size]
        chunks.append(chunk)
    return chunks

# Challenge 3: Version documents
def version_document(doc, version_id):
    """Track document versions"""
    return {
        "content": doc,
        "version": version_id,
        "updated": datetime.now()
    }

# Challenge 4: Index subsets
def partition_documents(docs, partition_size=1000):
    """Split large corpus into manageable partitions"""
    return [docs[i:i+partition_size] for i in range(0, len(docs), partition_size)]

# Challenge 5: Cache results
@lru_cache(maxsize=100)
def cached_rag_answer(query):
    """Cache frequently asked questions"""
    return rag_pipeline.answer(query)
```

---

## Intermediate Level (8 Questions)

### Q9: How do you implement a multi-document RAG system?

**Answer:**
Store multiple documents separately, retrieve from all, and synthesize answers from multiple sources.

**Code Example:**
```python
class MultiDocumentRAG:
    def __init__(self):
        self.documents = {}  # doc_name -> content
        self.embeddings = {} # doc_name -> embeddings

    def add_document(self, name, content, chunk_size=300):
        """Add a new document"""
        chunks = chunk_document(content, chunk_size)

        response = client.embeddings.create(
            model="text-embedding-3-small",
            input=chunks
        )

        self.documents[name] = chunks
        self.embeddings[name] = [item.embedding for item in response.data]

    def search_all(self, query, top_k_per_doc=2):
        """Search across all documents"""
        results = {}

        query_response = client.embeddings.create(
            model="text-embedding-3-small",
            input=[query]
        )
        query_emb = query_response.data[0].embedding

        for doc_name, embeddings in self.embeddings.items():
            similarities = []
            for emb in embeddings:
                sim = np.dot(np.array(query_emb), np.array(emb)) / (
                    np.linalg.norm(np.array(query_emb)) * np.linalg.norm(np.array(emb))
                )
                similarities.append(sim)

            top_indices = np.argsort(similarities)[-top_k_per_doc:][::-1]
            results[doc_name] = [self.documents[doc_name][i] for i in top_indices]

        return results

    def answer(self, query):
        """Answer using all documents"""
        results = self.search_all(query)

        context_parts = []
        for doc_name, chunks in results.items():
            context_parts.append(f"From {doc_name}:\n" + "\n".join(chunks))

        context = "\n\n".join(context_parts)

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

### Q10: What is the relationship between RAG and prompt engineering?

**Answer:**
RAG provides the content (documents), prompt engineering structures how the LLM uses it. Both are essential for quality answers.

**Code Example:**
```python
# Poor prompt: Vague
poor_prompt = f"Context: {context}\n\nAnswer this: {query}"

# Good prompt: Structured with instructions
good_prompt = f"""Use ONLY the provided context to answer the question.

Context:
{context}

Question: {query}

Instructions:
1. Base your answer only on the context
2. If information is not in context, say "Not found in documents"
3. Cite the relevant section of context
4. Format your answer clearly with numbered points if applicable

Answer:"""

response = client.chat.completions.create(
    model="gpt-4",
    messages=[{"role": "user", "content": good_prompt}]
)
```

---

### Q11: How do you optimize RAG performance?

**Answer:**
Key optimizations:
1. **Caching:** Cache frequent queries
2. **Indexing:** Use vector databases
3. **Batching:** Embed in batches
4. **Filtering:** Filter documents by metadata
5. **Async:** Parallel operations

**Code Example:**
```python
class OptimizedRAG:
    def __init__(self, documents):
        self.documents = documents
        self.cache = {}
        self.retrieval_metrics = []

    # 1. Caching
    def answer_cached(self, query):
        if query in self.cache:
            return self.cache[query]

        answer = self._generate_answer(query)
        self.cache[query] = answer
        return answer

    # 2. Batch embedding
    def batch_embed(self, texts, batch_size=50):
        embeddings = []
        for i in range(0, len(texts), batch_size):
            batch = texts[i:i+batch_size]
            response = client.embeddings.create(
                model="text-embedding-3-small",
                input=batch
            )
            embeddings.extend([item.embedding for item in response.data])
        return embeddings

    # 3. Metadata filtering
    def retrieve_with_filter(self, query, metadata_filter=None):
        # Filter documents by metadata first
        filtered_docs = self.documents
        if metadata_filter:
            filtered_docs = [d for d in self.documents if d.get("type") == metadata_filter]

        # Then retrieve
        return filtered_docs[:3]

    # 4. Track metrics
    def answer_with_metrics(self, query):
        start = time.time()
        answer = self.answer_cached(query)
        duration = time.time() - start

        self.retrieval_metrics.append({
            "query": query,
            "duration": duration,
            "cached": query in self.cache
        })

        return answer
```

---

### Q12: How do you handle context length limits with RAG?

**Answer:**
Strategically select most relevant chunks and compress context while maintaining key information.

**Code Example:**
```python
def smart_context_selection(query, documents, embeddings, max_tokens=2000):
    """Select documents that fit within token limit"""
    import tiktoken
    encoding = tiktoken.encoding_for_model("gpt-4")

    # Retrieve candidates
    query_response = client.embeddings.create(
        model="text-embedding-3-small",
        input=[query]
    )
    query_emb = query_response.data[0].embedding

    similarities = []
    for emb in embeddings:
        sim = np.dot(np.array(query_emb), np.array(emb)) / (
            np.linalg.norm(np.array(query_emb)) * np.linalg.norm(np.array(emb))
        )
        similarities.append(sim)

    # Sort by relevance
    sorted_indices = np.argsort(similarities)[::-1]

    # Add documents until token limit
    selected = []
    token_count = 0
    for idx in sorted_indices:
        doc = documents[idx]
        doc_tokens = len(encoding.encode(doc))

        if token_count + doc_tokens < max_tokens:
            selected.append(doc)
            token_count += doc_tokens
        else:
            break

    return selected
```

---

### Q13: What are vector databases and when should you use them?

**Answer:**
Vector databases (Pinecone, Weaviate, Milvus) store embeddings efficiently for fast retrieval at scale.

**Use cases:**
- 1000+ documents
- Real-time retrieval
- High frequency queries
- Need for metadata filtering
- Distributed systems

**Code Example:**
```python
# Without vector DB: O(n) search
def naive_search(query, embeddings, top_k=3):
    # Must compare against all embeddings
    similarities = [compute_similarity(query_emb, emb) for emb in embeddings]
    return sorted(range(len(similarities)), key=lambda i: similarities[i])[-top_k:]

# With vector DB: O(log n) search with indexing
def vector_db_search(query, vector_db_client, top_k=3):
    query_emb = client.embeddings.create(
        model="text-embedding-3-small",
        input=[query]
    ).data[0].embedding

    # Fast search using indices (HNSW, IVF, etc.)
    results = vector_db_client.search(query_emb, top_k=top_k)
    return results
```

---

### Q14: How do you evaluate RAG quality?

**Answer:**
Multiple metrics:
- **Retrieval Quality:** Precision, recall, NDCG
- **Generation Quality:** BLEU, ROUGE, semantic similarity
- **End-to-End:** Human evaluation

**Code Example:**
```python
def evaluate_rag(questions, ground_truth_answers, retrieved_docs):
    """Comprehensive RAG evaluation"""
    metrics = {
        "retrieval_precision": 0,
        "retrieval_recall": 0,
        "answer_similarity": 0,
        "latency": 0
    }

    for q, true_answer, retrieved in zip(questions, ground_truth_answers, retrieved_docs):
        # 1. Retrieval quality
        relevant = find_relevant_docs(q, true_answer)
        precision = len(set(retrieved) & set(relevant)) / len(retrieved)
        recall = len(set(retrieved) & set(relevant)) / len(relevant)

        # 2. Answer quality (simplified)
        generated_answer = rag.answer(q)
        similarity = calculate_similarity(generated_answer, true_answer)

        metrics["retrieval_precision"] += precision
        metrics["retrieval_recall"] += recall
        metrics["answer_similarity"] += similarity

    # Average
    n = len(questions)
    return {k: v/n for k, v in metrics.items()}
```

---

### Q15: What's the difference between RAG and fine-tuning?

**Answer:**

| Aspect | RAG | Fine-tuning |
|--------|-----|-------------|
| **Knowledge Update** | Add documents anytime | Requires retraining |
| **Cost** | Retrieval cost | High training cost |
| **Latency** | Higher (retrieval) | Lower |
| **Best For** | Dynamic knowledge | Fixed style/domain |
| **Scalability** | Excellent | Moderate |

**Code Example:**
```python
# RAG: Dynamic, updatable
rag_system = RAG()
rag_system.add_document("new_knowledge.txt")  # Easy update

# Fine-tuning: Static, permanent
fine_tune_job = client.fine_tuning.jobs.create(
    training_file=training_file_id,
    model="gpt-3.5-turbo"
)
# Wait days for training to complete
```

---

## Advanced Level (8 Questions)

### Q16: How do you design a RAG system for production?

**Answer:**
Production RAG requires:
1. **Scalability:** Vector database, batch processing
2. **Reliability:** Error handling, monitoring
3. **Quality:** Evaluation metrics, continuous improvement
4. **Efficiency:** Caching, indexing, async operations

**Code Example:**
```python
class ProductionRAGSystem:
    def __init__(self, vector_db, cache_size=1000):
        self.vector_db = vector_db  # Pinecone, Weaviate, etc.
        self.cache = LRUCache(max_size=cache_size)
        self.metrics = MetricsCollector()

    async def answer(self, query):
        """Async RAG with monitoring"""
        try:
            # Check cache
            if query in self.cache:
                self.metrics.record("cache_hit")
                return self.cache[query]

            # Retrieve from vector DB
            start = time.time()
            retrieved = await self.vector_db.search(query, top_k=3)
            self.metrics.record("retrieval_time", time.time() - start)

            # Generate answer
            context = format_context(retrieved)
            answer = await self.generate_answer(query, context)

            # Cache result
            self.cache[query] = answer

            return answer
        except Exception as e:
            self.metrics.record("error", str(e))
            # Fallback to simple retrieval
            return self.fallback_answer(query)

    def get_metrics(self):
        """Monitor system health"""
        return self.metrics.get_summary()
```

---

### Q17: How do you implement semantic caching in RAG?

**Answer:**
Cache answers for similar queries, not just exact matches.

**Code Example:**
```python
class SemanticCache:
    def __init__(self, similarity_threshold=0.95):
        self.queries = []
        self.answers = []
        self.embeddings = []
        self.threshold = similarity_threshold

    def get(self, query):
        """Get cached answer if similar query exists"""
        query_response = client.embeddings.create(
            model="text-embedding-3-small",
            input=[query]
        )
        query_emb = query_response.data[0].embedding

        for cached_query, cached_answer, cached_emb in zip(
            self.queries, self.answers, self.embeddings
        ):
            similarity = np.dot(np.array(query_emb), np.array(cached_emb)) / (
                np.linalg.norm(np.array(query_emb)) * np.linalg.norm(np.array(cached_emb))
            )

            if similarity > self.threshold:
                return cached_answer  # Found similar

        return None  # No similar query cached

    def set(self, query, answer):
        """Cache new answer"""
        query_response = client.embeddings.create(
            model="text-embedding-3-small",
            input=[query]
        )
        query_emb = query_response.data[0].embedding

        self.queries.append(query)
        self.answers.append(answer)
        self.embeddings.append(query_emb)
```

---

### Q18: How do you handle multimodal RAG (text + images)?

**Answer:**
Use multi-modal embeddings or combine text and image analysis.

**Code Example:**
```python
class MultimodalRAG:
    def __init__(self, documents, images, image_descriptions):
        self.text_docs = documents
        self.images = images  # List of image paths
        self.image_descriptions = image_descriptions

        # Embed everything together
        response = client.embeddings.create(
            model="text-embedding-3-small",
            input=documents + image_descriptions
        )
        self.embeddings = [item.embedding for item in response.data]

    def search_multimodal(self, query, top_k=3):
        """Search across text and images"""
        query_response = client.embeddings.create(
            model="text-embedding-3-small",
            input=[query]
        )
        query_emb = query_response.data[0].embedding

        similarities = []
        for emb in self.embeddings:
            sim = np.dot(np.array(query_emb), np.array(emb)) / (
                np.linalg.norm(np.array(query_emb)) * np.linalg.norm(np.array(emb))
            )
            similarities.append(sim)

        top_indices = np.argsort(similarities)[-top_k:][::-1]

        # Mix of text and images in results
        results = []
        for idx in top_indices:
            if idx < len(self.text_docs):
                results.append(("text", self.text_docs[idx]))
            else:
                img_idx = idx - len(self.text_docs)
                results.append(("image", self.images[img_idx]))

        return results
```

---

### Q19: What are reranking strategies and why use them?

**Answer:**
Reranking re-scores retrieved documents using a second model for better quality.

**Methods:**
1. **Cross-encoder:** Model trained to score query-doc pairs
2. **LLM reranking:** Ask LLM to rate relevance
3. **Rule-based:** Custom scoring logic

**Code Example:**
```python
class Reranker:
    def __init__(self, initial_top_k=10, final_top_k=3):
        self.initial_top_k = initial_top_k
        self.final_top_k = final_top_k

    def rerank_with_llm(self, query, documents):
        """Use LLM to rerank"""
        prompt = f"""Rate relevance of each document to the query (0-10):

Query: {query}

Documents:
"""
        for i, doc in enumerate(documents, 1):
            prompt += f"\n{i}. {doc[:100]}..."

        prompt += "\n\nReturn scores as comma-separated numbers"

        response = client.chat.completions.create(
            model="gpt-4",
            messages=[{"role": "user", "content": prompt}]
        )

        # Parse scores
        scores_text = response.choices[0].message.content
        scores = [float(s.strip()) for s in scores_text.split(",")]

        # Rerank
        reranked = sorted(zip(documents, scores), key=lambda x: x[1], reverse=True)
        return [doc for doc, score in reranked[:self.final_top_k]]

    def rerank_with_rules(self, query, documents):
        """Custom scoring rules"""
        scores = []
        for doc in documents:
            score = 0
            if query.lower() in doc.lower():
                score += 5  # Exact match

            query_words = set(query.lower().split())
            doc_words = set(doc.lower().split())
            score += len(query_words & doc_words)  # Word matches

            scores.append(score)

        reranked = sorted(zip(documents, scores), key=lambda x: x[1], reverse=True)
        return [doc for doc, score in reranked[:self.final_top_k]]
```

---

### Q20: How do you implement query expansion in RAG?

**Answer:**
Generate alternative phrasings of queries to retrieve more diverse results.

**Code Example:**
```python
def expand_query(query, num_expansions=3):
    """Generate alternative query phrasings"""
    prompt = f"""Generate {num_expansions} alternative ways to phrase this query:

Original: {query}

Return as newline-separated list."""

    response = client.chat.completions.create(
        model="gpt-4",
        messages=[{"role": "user", "content": prompt}]
    )

    alternatives = response.choices[0].message.content.split("\n")
    all_queries = [query] + [q.strip() for q in alternatives]
    return all_queries

def search_with_expansion(query, documents, embeddings, top_k=3):
    """Search using expanded queries"""
    expanded = expand_query(query)

    all_retrieved = set()
    for q in expanded:
        retrieved = retrieve_documents(q, documents, embeddings, top_k=5)
        all_retrieved.update(retrieved)

    return list(all_retrieved)[:top_k]
```

---

### Q21: How do you implement RAG with knowledge graphs?

**Answer:**
Use knowledge graphs to structure relationships and improve retrieval precision.

**Code Example:**
```python
class KnowledgeGraphRAG:
    def __init__(self):
        self.graph = nx.DiGraph()  # Graph structure
        self.embeddings = {}

    def add_relationship(self, entity1, relation, entity2, content):
        """Add structured knowledge"""
        self.graph.add_edge(entity1, entity2, relation=relation)

        # Also embed the content
        response = client.embeddings.create(
            model="text-embedding-3-small",
            input=[content]
        )
        self.embeddings[(entity1, relation, entity2)] = response.data[0].embedding

    def retrieve_with_graph(self, query, entity, depth=2):
        """Retrieve using graph traversal"""
        # Find related entities
        related = list(nx.dfs_preorder_nodes(self.graph, entity, depth_limit=depth))

        # Retrieve content for related entities
        retrieved = []
        for e1, e2 in self.graph.edges():
            if e1 in related or e2 in related:
                content = self.graph[e1][e2].get("content", "")
                if content:
                    retrieved.append(content)

        return retrieved
```

---

### Q22: What's the relationship between RAG and prompt compression?

**Answer:**
Compress context while preserving key information to save tokens and improve efficiency.

**Code Example:**
```python
def compress_context(context, target_ratio=0.5):
    """Compress context using LLM"""
    compression_prompt = f"""Compress the following text to {int(target_ratio*100)}% of original length while preserving key information:

{context}

Compressed version:"""

    response = client.chat.completions.create(
        model="gpt-4",
        messages=[{"role": "user", "content": compression_prompt}]
    )

    return response.choices[0].message.content

def compressed_rag_answer(query, documents, embeddings):
    """RAG with context compression"""
    # Retrieve
    retrieved = retrieve_documents(query, documents, embeddings, top_k=5)
    context = "\n\n".join(retrieved)

    # Compress
    compressed = compress_context(context, target_ratio=0.4)

    # Generate
    response = client.chat.completions.create(
        model="gpt-4",
        messages=[{
            "role": "user",
            "content": f"Context:\n{compressed}\n\nQuestion: {query}"
        }]
    )

    return response.choices[0].message.content
```

---

### Q23: How do you scale RAG to millions of documents?

**Answer:**
Use distributed vector databases with proper indexing and partitioning strategies.

**Strategies:**
1. **Vector Database:** Pinecone, Weaviate, Milvus
2. **Partitioning:** Split by date, category, domain
3. **Indexing:** HNSW, IVF, LSH algorithms
4. **Caching:** Cache popular queries
5. **Async:** Parallel processing

**Code Example:**
```python
class ScalableRAG:
    def __init__(self, num_partitions=10):
        self.partitions = [PartitionedIndex() for _ in range(num_partitions)]
        self.num_partitions = num_partitions

    def hash_to_partition(self, doc_id):
        """Determine which partition for a document"""
        return hash(doc_id) % self.num_partitions

    def add_document(self, doc_id, content):
        """Add to appropriate partition"""
        partition_idx = self.hash_to_partition(doc_id)
        self.partitions[partition_idx].add(doc_id, content)

    def search_all_partitions(self, query, top_k=10):
        """Search all partitions in parallel"""
        import concurrent.futures

        results = []
        with concurrent.futures.ThreadPoolExecutor() as executor:
            futures = [
                executor.submit(p.search, query, top_k=top_k)
                for p in self.partitions
            ]

            for future in concurrent.futures.as_completed(futures):
                results.extend(future.result())

        # Merge and rerank
        return sorted(results, key=lambda x: x["score"], reverse=True)[:top_k]
```

---

## Key Takeaways

**Beginner:** Understand RAG pipeline, embeddings, chunking
**Intermediate:** Implement multi-doc systems, optimize performance
**Advanced:** Build production systems, handle scale, design architectures

RAG combines retrieval and generation for accurate, grounded AI applications.
