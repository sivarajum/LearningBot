# Advanced RAG: Complete Guide

## 1. What is Advanced RAG?

Advanced RAG (Retrieval-Augmented Generation) extends basic RAG with sophisticated techniques to improve retrieval quality, reduce hallucinations, and handle complex queries. While basic RAG does simple embed→retrieve→generate, advanced RAG adds **query transformation, re-ranking, multi-step retrieval, hybrid search, and self-correction**.

**Why basic RAG fails:**
- Queries don't always match document embeddings well
- Top-k retrieval misses relevant context buried in document chunks
- No verification that retrieved documents actually answer the query
- Single-step retrieval can't handle multi-hop questions

---

## 2. Core Techniques

### Query Transformation
Transform the user query before retrieval to improve recall:

| Technique | How It Works |
|-----------|-------------|
| **HyDE** (Hypothetical Document Embeddings) | Generate a hypothetical answer, embed it, search for similar real documents |
| **Query Decomposition** | Break complex query into sub-queries, retrieve for each |
| **Query Expansion** | Add synonyms, related terms to broaden retrieval |
| **Step-Back Prompting** | Abstract the query to a higher-level question first |

```python
# HyDE: Generate hypothetical answer, then search
def hyde_retrieve(query: str, retriever, llm):
    # Step 1: Generate hypothetical document
    hypothetical = llm.invoke(
        f"Write a passage that would answer: {query}"
    )
    # Step 2: Embed hypothetical doc and find similar real docs
    results = retriever.similarity_search(hypothetical.content)
    return results

# Query Decomposition
def decompose_query(query: str, llm):
    sub_queries = llm.invoke(
        f"Break this question into 2-3 simpler sub-questions:\n{query}"
    )
    return sub_queries.content.split("\n")
```

### Re-Ranking
After initial retrieval, re-rank results for relevance:

```python
from sentence_transformers import CrossEncoder

# Cross-encoder re-ranking (much more accurate than bi-encoder)
reranker = CrossEncoder("cross-encoder/ms-marco-MiniLM-L-6-v2")

def rerank(query: str, documents: list, top_k: int = 5):
    pairs = [(query, doc.page_content) for doc in documents]
    scores = reranker.predict(pairs)
    ranked = sorted(zip(documents, scores), key=lambda x: x[1], reverse=True)
    return [doc for doc, score in ranked[:top_k]]

# Usage: retrieve 20, rerank to top 5
initial_results = retriever.similarity_search(query, k=20)
final_results = rerank(query, initial_results, top_k=5)
```

### Hybrid Search
Combine dense (semantic) and sparse (keyword) retrieval:

```python
from langchain.retrievers import EnsembleRetriever
from langchain_community.retrievers import BM25Retriever

# Sparse: BM25 (keyword matching)
bm25_retriever = BM25Retriever.from_documents(documents, k=10)

# Dense: Vector similarity
vector_retriever = vectorstore.as_retriever(search_kwargs={"k": 10})

# Hybrid: Combine with Reciprocal Rank Fusion
hybrid_retriever = EnsembleRetriever(
    retrievers=[bm25_retriever, vector_retriever],
    weights=[0.3, 0.7],  # Weight semantic higher
)
results = hybrid_retriever.invoke(query)
```

### Multi-Vector Retrieval
Store multiple representations per document:

```python
from langchain.storage import InMemoryByteStore
from langchain.retrievers.multi_vector import MultiVectorRetriever

# For each document, create:
# 1. Summary embedding (for broad queries)
# 2. Full-text embedding (for detailed queries)
# 3. Question embeddings (questions the doc answers)

summaries = [llm.invoke(f"Summarize: {doc}") for doc in documents]
questions = [llm.invoke(f"What questions does this answer: {doc}") for doc in documents]

# Add all representations to vectorstore
# Link back to original full document
retriever = MultiVectorRetriever(
    vectorstore=vectorstore,
    byte_store=InMemoryByteStore(),
    id_key="doc_id",
)
```

### Self-Querying
LLM constructs structured queries with metadata filters:

```python
from langchain.retrievers.self_query.base import SelfQueryRetriever

metadata_field_info = [
    {"name": "sector", "type": "string", "description": "Stock sector"},
    {"name": "market_cap", "type": "float", "description": "Market cap in crores"},
    {"name": "date", "type": "date", "description": "Report date"},
]

retriever = SelfQueryRetriever.from_llm(
    llm=llm,
    vectorstore=vectorstore,
    document_contents="Financial analysis reports",
    metadata_field_info=metadata_field_info,
)

# Query: "Large-cap IT stocks analysis from 2024"
# Auto-generates filter: sector="IT" AND market_cap > 50000 AND date >= "2024-01-01"
```

---

## 3. Advanced Chunking Strategies

| Strategy | Description | Best For |
|----------|-------------|----------|
| **Semantic Chunking** | Split at topic boundaries using embeddings | Long documents with diverse topics |
| **Parent-Child** | Small chunks for retrieval, return parent chunk for context | Maintaining context while precise matching |
| **Sliding Window** | Overlapping chunks with configurable stride | Continuous text without clear boundaries |
| **Recursive** | Split by hierarchy (headings → paragraphs → sentences) | Structured documents (markdown, HTML) |
| **Agentic Chunking** | LLM decides chunk boundaries | Complex, unstructured documents |

```python
# Semantic Chunking — split at topic shifts
from langchain_experimental.text_splitter import SemanticChunker

splitter = SemanticChunker(
    embeddings=OpenAIEmbeddings(),
    breakpoint_threshold_type="percentile",
    breakpoint_threshold_amount=90,  # Split at high dissimilarity
)
chunks = splitter.split_text(long_document)

# Parent-Child — small chunks map to larger parents
from langchain.text_splitter import RecursiveCharacterTextSplitter

parent_splitter = RecursiveCharacterTextSplitter(chunk_size=2000)
child_splitter = RecursiveCharacterTextSplitter(chunk_size=400)

parents = parent_splitter.split_documents(docs)
for parent in parents:
    children = child_splitter.split_documents([parent])
    # Index children, but return parent when matched
```

---

## 4. RAG Evaluation

### Metrics

| Metric | Measures | Range |
|--------|----------|-------|
| **Faithfulness** | Is the answer grounded in retrieved docs? | 0-1 |
| **Answer Relevancy** | Does the answer address the question? | 0-1 |
| **Context Precision** | Are retrieved docs relevant (top-k accuracy)? | 0-1 |
| **Context Recall** | Are all relevant docs retrieved? | 0-1 |

```python
# Using RAGAS for evaluation
from ragas import evaluate
from ragas.metrics import (
    faithfulness,
    answer_relevancy,
    context_precision,
    context_recall,
)

dataset = {
    "question": ["What is RELIANCE P/E ratio?"],
    "answer": ["RELIANCE P/E ratio is 28.5"],
    "contexts": [["RELIANCE financial data: P/E=28.5, EPS=95.2"]],
    "ground_truth": ["RELIANCE has a P/E ratio of 28.5"],
}

result = evaluate(
    dataset,
    metrics=[faithfulness, answer_relevancy, context_precision, context_recall],
)
print(result)  # {'faithfulness': 1.0, 'answer_relevancy': 0.95, ...}
```

---

## 5. Corrective RAG (CRAG)

Self-correcting RAG that evaluates and refines retrieval:

```python
def corrective_rag(query: str, retriever, llm):
    # Step 1: Retrieve
    docs = retriever.invoke(query)

    # Step 2: Grade relevance
    graded_docs = []
    for doc in docs:
        grade = llm.invoke(
            f"Is this document relevant to '{query}'?\n"
            f"Document: {doc.page_content}\n"
            f"Answer RELEVANT or NOT_RELEVANT."
        )
        if "RELEVANT" in grade.content:
            graded_docs.append(doc)

    # Step 3: If no relevant docs, fall back to web search
    if not graded_docs:
        web_results = web_search(query)
        graded_docs = web_results

    # Step 4: Generate with verified context
    response = llm.invoke(
        f"Answer based ONLY on these documents:\n"
        f"{format_docs(graded_docs)}\n\n"
        f"Question: {query}"
    )

    # Step 5: Check for hallucination
    hallucination_check = llm.invoke(
        f"Does this answer contain claims not in the documents?\n"
        f"Answer: {response.content}\n"
        f"Documents: {format_docs(graded_docs)}\n"
        f"Reply YES or NO."
    )
    if "YES" in hallucination_check.content:
        return corrective_rag(query, retriever, llm)  # Retry

    return response.content
```

---

## 6. Graph RAG

Combine knowledge graphs with vector retrieval:

```python
# Build knowledge graph from documents
from langchain_community.graphs import Neo4jGraph

graph = Neo4jGraph(url="bolt://localhost:7687")

# Extract entities and relationships
entities = llm.invoke(
    "Extract entities and relationships from this text as triples: "
    f"{document}"
)
# Output: (RELIANCE, has_sector, Oil_And_Gas), (RELIANCE, pe_ratio, 28.5)

# Query combines graph traversal + vector search
def graph_rag(query):
    # 1. Extract entities from query
    query_entities = extract_entities(query)

    # 2. Graph traversal (structured relationships)
    graph_context = graph.query(
        f"MATCH (n)-[r]->(m) WHERE n.name IN {query_entities} RETURN n, r, m"
    )

    # 3. Vector search (semantic similarity)
    vector_context = retriever.invoke(query)

    # 4. Combine both contexts
    combined = f"Graph facts: {graph_context}\nDocuments: {vector_context}"
    return llm.invoke(f"Answer using this context:\n{combined}\n\nQ: {query}")
```

---

## 7. Best Practices

| Practice | Why |
|----------|-----|
| Always re-rank after initial retrieval | Top-k by cosine similarity misses relevant docs |
| Use hybrid search (dense + sparse) | Keywords matter for specific entities/numbers |
| Chunk with overlap (10-20%) | Prevent splitting important context across chunks |
| Evaluate with RAGAS metrics | Quantify retrieval and generation quality |
| Cache embeddings | Re-embedding unchanged docs wastes compute |
| Use metadata filters | Pre-filter before vector search for efficiency |
| Test with adversarial queries | Queries that look similar to wrong docs |

---

## 8. Common Pitfalls

| Pitfall | Solution |
|---------|----------|
| Chunks too large | Important info diluted. Use 200-500 tokens. |
| Chunks too small | No context. Use parent-child retrieval. |
| Ignoring metadata | Filter by date, sector, type before vector search |
| No re-ranking | Cross-encoder re-ranking improves precision 20-40% |
| Single retrieval step | Multi-step retrieval for complex, multi-hop queries |
| Not evaluating | Use RAGAS to measure faithfulness and relevancy |
| Embedding model mismatch | Use same model for indexing and querying |

---

## 9. RAG Evaluation with RAGAS

```python
from ragas import evaluate
from ragas.metrics import faithfulness, answer_relevancy, context_precision, context_recall

# Prepare evaluation dataset
eval_data = {
    "question": ["What is RELIANCE PE ratio?", "Who is the CFO of TCS?"],
    "answer": ["RELIANCE PE is 28.5", "TCS CFO is K Krithivasan"],
    "contexts": [["RELIANCE trades at PE 28.5..."], ["TCS CEO: K Krithivasan..."]],
    "ground_truth": ["RELIANCE PE is 28.5", "TCS CFO information..."],
}

results = evaluate(
    dataset=eval_data,
    metrics=[faithfulness, answer_relevancy, context_precision, context_recall],
)
print(results)
# faithfulness: 0.92, relevancy: 0.88, precision: 0.85, recall: 0.78
```

### Key Metrics Explained

| Metric | Measures | Target |
|--------|----------|--------|
| **Faithfulness** | Is answer grounded in retrieved context? (no hallucination) | > 0.90 |
| **Answer Relevancy** | Does answer address the question? | > 0.85 |
| **Context Precision** | Are retrieved chunks actually relevant? | > 0.80 |
| **Context Recall** | Did we retrieve all needed information? | > 0.75 |

---

## 10. Chunking Strategies Compared

```python
# Strategy 1: Fixed-size chunks (simple but naive)
from langchain.text_splitter import CharacterTextSplitter
splitter = CharacterTextSplitter(chunk_size=500, chunk_overlap=50)

# Strategy 2: Recursive splitting (respects document structure)
from langchain.text_splitter import RecursiveCharacterTextSplitter
splitter = RecursiveCharacterTextSplitter(
    chunk_size=500, chunk_overlap=100,
    separators=["\n\n", "\n", ". ", " ", ""],  # Try largest first
)

# Strategy 3: Semantic chunking (split by meaning change)
from langchain_experimental.text_splitter import SemanticChunker
from langchain_openai import OpenAIEmbeddings
splitter = SemanticChunker(
    OpenAIEmbeddings(),
    breakpoint_threshold_type="percentile",  # Split when embedding similarity drops
)

# Strategy 4: Document-specific (best for structured docs)
# Tables → keep as single chunk with metadata
# Headers → include parent headers in each chunk
# Code blocks → never split mid-function
```

| Strategy | Best For | Chunk Quality |
|----------|----------|---------------|
| Fixed-size | Quick prototyping | ⭐⭐ |
| Recursive | General documents | ⭐⭐⭐ |
| Semantic | Dense technical text | ⭐⭐⭐⭐ |
| Document-specific | Structured docs (filings, reports) | ⭐⭐⭐⭐⭐ |

---

## 11. Production RAG Architecture

```
┌─────────────────────────────────────────────────────┐
│  Ingestion Pipeline (offline, batch)                │
│  Documents → Parse → Chunk → Embed → Vector Store   │
│  + Metadata extraction → Graph DB (optional)         │
├─────────────────────────────────────────────────────┤
│  Query Pipeline (online, real-time)                 │
│  Query → Rewrite → Hybrid Search → Re-rank          │
│  → Context Assembly → LLM Generation → Validate     │
├─────────────────────────────────────────────────────┤
│  Evaluation Pipeline (continuous)                   │
│  RAGAS metrics → Drift detection → Auto-reindex     │
│  → A/B testing → Feedback loop                      │
└─────────────────────────────────────────────────────┘
```

### Financial RAG: Analyst Report Q&A

```python
# End-to-end financial RAG system
from langchain_community.vectorstores import Chroma
from langchain_openai import OpenAIEmbeddings

# Index annual reports with financial metadata
vectorstore = Chroma.from_documents(
    documents=annual_report_chunks,
    embedding=OpenAIEmbeddings(),
    collection_metadata={"hnsw:space": "cosine"},
)

# Query with metadata filter
results = vectorstore.similarity_search(
    "What was EBITDA margin trend?",
    filter={"company": "RELIANCE", "year": {"$gte": 2022}},
    k=5,
)
```
