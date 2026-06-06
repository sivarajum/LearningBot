# Advanced RAG: Interview Questions & Answers

## Beginner Level

### Q1: What is RAG and why do we need it?
**A:** RAG (Retrieval-Augmented Generation) grounds LLM responses in external knowledge by retrieving relevant documents before generating answers. We need it because:
- LLMs have a knowledge cutoff date (can't answer about recent events)
- LLMs hallucinate facts not in training data
- Enterprise data is private and not in any LLM's training
- RAG reduces hallucinations by 60-80% compared to pure generation

Basic flow: `Query → Embed → Search vector DB → Retrieve top K docs → Feed to LLM → Generate grounded answer`

### Q2: What's wrong with basic RAG and what does Advanced RAG fix?
**A:**

| Basic RAG Problem | Advanced RAG Solution |
|-------------------|----------------------|
| Query doesn't match document wording | **HyDE**: Generate hypothetical answer, embed that instead |
| Top-K retrieval misses relevant docs | **Re-ranking**: Retrieve 20, cross-encoder re-rank to 5 |
| Keyword-heavy queries fail on semantic search | **Hybrid search**: Combine BM25 (keyword) + dense (semantic) |
| Complex questions need multiple lookups | **Query decomposition**: Break into sub-queries |
| Retrieved docs aren't verified | **CRAG**: Grade relevance, reject bad docs, fallback to web |
| No way to measure quality | **RAGAS evaluation**: Faithfulness, relevancy, precision, recall |

### Q3: Explain the difference between bi-encoder and cross-encoder retrieval.
**A:**

**Bi-encoder** (used for initial retrieval):
- Encodes query and documents independently
- Fast: pre-compute all document embeddings once
- Less accurate: no cross-attention between query and document

**Cross-encoder** (used for re-ranking):
- Encodes query-document pair together
- Slow: must run inference for every (query, doc) pair
- More accurate: full attention between query and document

```python
# Bi-encoder: fast, approximate
query_embedding = model.encode(query)
doc_embeddings = model.encode(documents)  # Pre-computed
scores = cosine_similarity(query_embedding, doc_embeddings)

# Cross-encoder: slow, precise (used for re-ranking top 20-50 results)
reranker = CrossEncoder("cross-encoder/ms-marco-MiniLM-L-6-v2")
scores = reranker.predict([(query, doc) for doc in top_20_docs])
```

**Best practice:** Bi-encoder retrieves top 20-50, cross-encoder re-ranks to top 3-5.

### Q4: What is HyDE and when should you use it?
**A:** HyDE (Hypothetical Document Embeddings) generates a fake answer to the query, then embeds that fake answer to find real documents that are similar.

```
Query: "What is RELIANCE's dividend policy?"
↓ LLM generates hypothetical answer:
"RELIANCE maintains a dividend payout ratio of 10-15% of net profit..."
↓ Embed this hypothetical answer
↓ Search vector DB for similar real documents
↓ Find actual dividend policy documents
```

**When to use:** When user queries are questions but your documents are statements/reports. The query "What is X?" doesn't embed similarly to "X is defined as..." but a hypothetical answer does.

**When NOT to use:** Simple keyword queries, or when query and document language already match well.

### Q5: What chunking strategy should you use for financial documents?
**A:**

| Document Type | Strategy | Chunk Size | Why |
|---------------|----------|-----------|-----|
| Annual reports (structured) | Recursive by headings | 1000-1500 tokens | Preserve section structure |
| Earnings call transcripts | Semantic chunking | 500-800 tokens | Split at topic shifts |
| News articles | Fixed + overlap | 400-600 tokens | Short, dense content |
| Regulatory filings (SEBI) | Parent-child | Child: 300, Parent: 1500 | Need precise matching + full context |
| Time-series commentary | Sliding window | 500 tokens, 100 overlap | Temporal continuity matters |

---

## Intermediate Level

### Q6: Design a hybrid search retriever for a financial knowledge base.
**A:**

```python
from langchain.retrievers import EnsembleRetriever
from langchain_community.retrievers import BM25Retriever

class FinancialHybridRetriever:
    def __init__(self, documents, vectorstore):
        # Sparse: BM25 for exact ticker symbols, numbers, dates
        self.bm25 = BM25Retriever.from_documents(documents, k=15)

        # Dense: Vector similarity for semantic meaning
        self.vector = vectorstore.as_retriever(
            search_type="mmr",  # Maximum Marginal Relevance (diversity)
            search_kwargs={"k": 15, "fetch_k": 50, "lambda_mult": 0.7},
        )

        # Hybrid: Reciprocal Rank Fusion
        self.hybrid = EnsembleRetriever(
            retrievers=[self.bm25, self.vector],
            weights=[0.4, 0.6],  # Slightly favor semantic
        )

        # Re-ranker
        self.reranker = CrossEncoder("cross-encoder/ms-marco-MiniLM-L-6-v2")

    def retrieve(self, query: str, top_k: int = 5) -> list:
        # Step 1: Hybrid retrieval (20 candidates)
        candidates = self.hybrid.invoke(query)

        # Step 2: Cross-encoder re-ranking
        pairs = [(query, doc.page_content) for doc in candidates]
        scores = self.reranker.predict(pairs)
        ranked = sorted(zip(candidates, scores), key=lambda x: x[1], reverse=True)

        return [doc for doc, _ in ranked[:top_k]]
```

BM25 handles queries like "RELIANCE Q3 FY25 results" (exact terms). Vector handles "which oil company is performing best?" (semantic).

### Q7: How does Corrective RAG (CRAG) work?
**A:** CRAG adds a self-correction loop:

1. **Retrieve** documents normally
2. **Grade** each document for relevance (LLM or classifier)
3. **Action based on grading:**
   - All relevant → Generate answer
   - Some relevant → Use only relevant ones + supplement with web search
   - None relevant → Fall back to web search entirely
4. **Hallucination check** on generated answer
5. **Retry** if hallucination detected

```python
def crag_pipeline(query, retriever, llm):
    docs = retriever.invoke(query)

    # Grade each doc
    relevant = []
    for doc in docs:
        score = grade_relevance(query, doc, llm)
        if score > 0.7:
            relevant.append(doc)

    # Decide action
    if len(relevant) == 0:
        context = web_search(query)
    elif len(relevant) < len(docs) / 2:
        context = relevant + web_search(query)[:2]
    else:
        context = relevant

    # Generate
    answer = generate(query, context, llm)

    # Verify
    if not is_grounded(answer, context, llm):
        return crag_pipeline(query, retriever, llm)  # Retry
    return answer
```

### Q8: Explain multi-step retrieval for complex queries.
**A:** Multi-step retrieval handles questions that require information from multiple sources:

```
Query: "Compare RELIANCE and TCS P/E ratios and recommend which to buy based on sector trends"
```

**Step 1:** Decompose query:
- Sub-Q1: "What is RELIANCE P/E ratio?"
- Sub-Q2: "What is TCS P/E ratio?"
- Sub-Q3: "What are current Oil & Gas sector trends?"
- Sub-Q4: "What are current IT sector trends?"

**Step 2:** Retrieve for each sub-query independently

**Step 3:** Aggregate all retrieved documents

**Step 4:** Generate answer using combined context

```python
def multi_step_retrieve(query, retriever, llm):
    # Decompose
    sub_queries = llm.invoke(
        f"Break into 2-4 specific sub-questions: {query}"
    ).content.split("\n")

    # Retrieve for each
    all_docs = []
    for sq in sub_queries:
        docs = retriever.invoke(sq)
        all_docs.extend(docs)

    # Deduplicate
    unique_docs = deduplicate_by_content(all_docs)

    # Re-rank against original query
    top_docs = rerank(query, unique_docs, top_k=7)

    return generate(query, top_docs, llm)
```

### Q9: How do you evaluate RAG quality using RAGAS?
**A:** RAGAS measures 4 dimensions:

| Metric | Formula | What It Catches |
|--------|---------|-----------------|
| **Faithfulness** | Claims in answer supported by context / Total claims | Hallucinations |
| **Answer Relevancy** | Similarity of answer to question | Off-topic responses |
| **Context Precision** | Relevant docs in top positions / Total retrieved | Retrieval quality |
| **Context Recall** | Ground truth info found in context / Total ground truth | Missing information |

```python
from ragas import evaluate
from ragas.metrics import faithfulness, answer_relevancy

# Prepare evaluation dataset
eval_data = {
    "question": questions,
    "answer": rag_answers,
    "contexts": retrieved_contexts,
    "ground_truth": reference_answers,
}

results = evaluate(eval_data, metrics=[
    faithfulness,      # 0.92 = 8% hallucination rate
    answer_relevancy,  # 0.88 = decent relevance
    context_precision, # 0.75 = retrieval needs improvement
    context_recall,    # 0.90 = finding most relevant info
])
```

**Targets:** Faithfulness > 0.9, Context Precision > 0.8 for production.

---

## Advanced Level

### Q10: Design a production RAG pipeline for a financial advisory platform.
**A:**

```python
class FinancialRAGPipeline:
    def __init__(self):
        # Multi-index architecture
        self.indexes = {
            "reports": ChromaDB("annual_reports"),    # Dense index
            "filings": ElasticsearchBM25("sebi_filings"),  # Sparse index
            "news": PineconeIndex("market_news"),          # Time-weighted dense
        }
        self.reranker = CrossEncoder("cross-encoder/ms-marco-MiniLM-L-12-v2")
        self.guardrails = FinancialGuardrails()

    async def query(self, user_query: str) -> RAGResponse:
        # 1. Query understanding
        intent = classify_intent(user_query)  # factual, opinion, comparison
        entities = extract_entities(user_query)  # RELIANCE, TCS, etc.

        # 2. Query transformation
        if intent == "comparison":
            sub_queries = decompose_comparison(user_query)
        else:
            sub_queries = [user_query]
            if should_use_hyde(intent):
                sub_queries = [generate_hyde(user_query)]

        # 3. Multi-index retrieval (parallel)
        all_candidates = await asyncio.gather(*[
            self.retrieve_from_all_indexes(sq) for sq in sub_queries
        ])
        candidates = flatten_and_deduplicate(all_candidates)

        # 4. Re-ranking + metadata filtering
        if entities:
            candidates = [c for c in candidates if any(e in c.metadata.get("entities", []) for e in entities)]
        top_docs = self.rerank(user_query, candidates, top_k=7)

        # 5. Guardrails (pre-generation)
        verified_docs = self.guardrails.verify_sources(top_docs)

        # 6. Generation with citation
        answer = await self.generate_with_citations(user_query, verified_docs)

        # 7. Post-generation guardrails
        if not self.guardrails.check_faithfulness(answer, verified_docs):
            answer = await self.regenerate_conservative(user_query, verified_docs)

        return RAGResponse(answer=answer, sources=verified_docs)
```

### Q11: How do you handle temporal queries in RAG (e.g., "latest quarterly results")?
**A:**

```python
class TemporalRAG:
    def __init__(self, vectorstore):
        self.vs = vectorstore

    def retrieve(self, query: str, reference_date=None):
        # 1. Detect temporal intent
        temporal_info = self.parse_temporal(query)
        # "Q3 FY25 results" → {"quarter": "Q3", "year": "FY25"}
        # "latest" → {"recency": "most_recent"}
        # "last 3 months" → {"range": "90d"}

        # 2. Build metadata filter
        if temporal_info.get("recency"):
            filter_expr = {"date": {"$gte": date.today() - timedelta(days=30)}}
        elif temporal_info.get("quarter"):
            filter_expr = self.quarter_to_date_range(temporal_info)
        else:
            filter_expr = {}

        # 3. Time-weighted similarity
        docs = self.vs.similarity_search(
            query, k=20, filter=filter_expr
        )

        # 4. Boost recent documents
        for doc in docs:
            days_old = (date.today() - doc.metadata["date"]).days
            doc.score *= math.exp(-0.01 * days_old)  # Exponential decay

        return sorted(docs, key=lambda d: d.score, reverse=True)[:5]
```

### Q12: How would you implement Graph RAG for a financial knowledge base?
**A:**

```python
class FinancialGraphRAG:
    """Combines knowledge graph with vector retrieval."""

    def __init__(self):
        self.graph = Neo4jGraph()  # Structured relationships
        self.vectorstore = ChromaDB()  # Unstructured text

    def build_graph(self, documents):
        """Extract entities and relationships from docs."""
        for doc in documents:
            triples = self.extract_triples(doc)
            # (RELIANCE, sector, Oil_Gas)
            # (RELIANCE, pe_ratio, 28.5)
            # (RELIANCE, competitor, ONGC)
            # (TCS, sector, IT)
            for subj, rel, obj in triples:
                self.graph.create_relationship(subj, rel, obj)

    def query(self, user_query: str):
        # 1. Extract entities from query
        entities = extract_entities(user_query)  # ["RELIANCE", "TCS"]

        # 2. Graph traversal (structured facts)
        graph_facts = self.graph.query(
            f"MATCH (n)-[r]->(m) "
            f"WHERE n.name IN {entities} "
            f"RETURN n.name, type(r), m.name "
            f"LIMIT 20"
        )
        # Returns: [(RELIANCE, sector, Oil_Gas), (RELIANCE, pe_ratio, 28.5), ...]

        # 3. Vector retrieval (unstructured context)
        vector_docs = self.vectorstore.similarity_search(user_query, k=5)

        # 4. Combine contexts
        context = f"""
        Structured facts:
        {format_graph_facts(graph_facts)}

        Relevant documents:
        {format_docs(vector_docs)}
        """

        # 5. Generate answer
        return llm.invoke(
            f"Answer using ONLY this context:\n{context}\n\nQ: {user_query}"
        )
```

**Graph RAG excels when:**
- Questions involve relationships (competitors, sector peers, supply chain)
- Multi-hop reasoning needed ("Which suppliers of RELIANCE are also in Nifty 50?")
- Structured facts complement unstructured documents
