# LlamaIndex — Interview Questions & Answers

## Table of Contents

1. [Beginner Level (Q1–Q6)](#beginner-level)
2. [Intermediate Level (Q7–Q12)](#intermediate-level)
3. [Advanced Level (Q13–Q18)](#advanced-level)

---

## Beginner Level

### Q1: What is LlamaIndex and how does it differ from using an LLM directly?

**Answer:**

LlamaIndex is a **data framework for LLM applications** that specializes in Retrieval-Augmented Generation (RAG). It bridges the gap between your private data and LLMs.

**Without LlamaIndex (raw LLM):**
```python
import openai

# Problem: LLM has no knowledge of your data
response = openai.chat.completions.create(
    model="gpt-4o",
    messages=[{"role": "user", "content": "What was our Q3 revenue?"}]
)
# Answer: "I don't have access to your company's data."
```

**With LlamaIndex:**
```python
from llama_index.core import VectorStoreIndex, SimpleDirectoryReader

# Load your private financial documents
documents = SimpleDirectoryReader("./financials").load_data()

# Create a searchable index
index = VectorStoreIndex.from_documents(documents)

# Now the LLM can answer using YOUR data
query_engine = index.as_query_engine()
response = query_engine.query("What was our Q3 revenue?")
# Answer: "Q3 revenue was $2.1B, up 15% YoY based on the quarterly report."
```

**Key differences:**
| Aspect | Raw LLM | LLM + LlamaIndex |
|--------|---------|-------------------|
| Private data access | No | Yes |
| Grounded answers | No (hallucinates) | Yes (cites sources) |
| Updated information | No (training cutoff) | Yes (index updates) |
| Token limit handling | Manual chunking | Automatic |

---

### Q2: Explain the core RAG pipeline in LlamaIndex. What are the main steps?

**Answer:**

RAG (Retrieval-Augmented Generation) in LlamaIndex follows 5 stages:

```
Loading → Indexing → Storing → Querying → Evaluating
```

**Stage 1 — Loading:**
```python
from llama_index.core import SimpleDirectoryReader

# Load raw data into Document objects
documents = SimpleDirectoryReader("./data").load_data()
# Each file → one Document with text + metadata
```

**Stage 2 — Indexing (Chunking + Embedding):**
```python
from llama_index.core import VectorStoreIndex

# Under the hood:
# 1. Documents split into Nodes (chunks of ~1024 tokens)
# 2. Each Node is embedded (converted to a vector)
# 3. Nodes stored in an index data structure
index = VectorStoreIndex.from_documents(documents)
```

**Stage 3 — Storing (Persistence):**
```python
# Save the index to disk so you don't re-embed every time
index.storage_context.persist(persist_dir="./storage")

# Load later
from llama_index.core import StorageContext, load_index_from_storage
storage_context = StorageContext.from_defaults(persist_dir="./storage")
index = load_index_from_storage(storage_context)
```

**Stage 4 — Querying (Retrieval + Synthesis):**
```python
query_engine = index.as_query_engine(similarity_top_k=5)
response = query_engine.query("What is the refund policy?")

# Under the hood:
# 1. Query embedded into same vector space
# 2. Top-k most similar nodes retrieved
# 3. Retrieved nodes + query sent to LLM
# 4. LLM generates grounded response
```

**Stage 5 — Evaluating:**
```python
from llama_index.core.evaluation import FaithfulnessEvaluator
evaluator = FaithfulnessEvaluator()
result = evaluator.evaluate_response(response=response)
print(f"Answer is faithful to sources: {result.passing}")
```

---

### Q3: What is the difference between a Document and a Node in LlamaIndex?

**Answer:**

| Aspect | Document | Node |
|--------|----------|------|
| What | Entire file/source | Chunk of a document |
| Size | Can be any size (1 page to 1000 pages) | Fixed chunk size (typically 1024 tokens) |
| Created by | Data connectors/readers | Node parsers (splitters) |
| Has embedding? | No | Yes (after indexing) |
| Relationships | None by default | Parent doc, prev/next nodes |
| Queried directly? | No (too large for LLM context) | Yes (right-sized for retrieval) |

```python
from llama_index.core import Document, SimpleDirectoryReader
from llama_index.core.node_parser import SentenceSplitter

# Document: raw data container
doc = Document(
    text="This is a 50-page annual report...",
    metadata={"source": "annual_report_2024.pdf", "year": 2024}
)

# Or load automatically
documents = SimpleDirectoryReader("./data").load_data()
print(f"Loaded {len(documents)} documents")

# Nodes: chunks of documents
parser = SentenceSplitter(chunk_size=1024, chunk_overlap=200)
nodes = parser.get_nodes_from_documents(documents)
print(f"Created {len(nodes)} nodes from {len(documents)} documents")

# Each node knows its parent
for node in nodes[:3]:
    print(f"Node text: {node.text[:100]}...")
    print(f"Node source: {node.metadata.get('file_name')}")
    print(f"Relationships: {node.relationships}")
```

**Why this matters:** A 100-page PDF is useless in a single LLM prompt (too big). But 100 well-chunked Nodes? Now the retriever can find the 3-5 most relevant chunks and pass only those to the LLM.

---

### Q4: What are the different index types in LlamaIndex and when would you use each?

**Answer:**

LlamaIndex offers 5 primary index types:

```python
from llama_index.core import (
    VectorStoreIndex,      # Semantic similarity search
    SummaryIndex,          # Summarization over all nodes
    TreeIndex,             # Hierarchical summarization
    KeywordTableIndex,     # Keyword-based retrieval
    KnowledgeGraphIndex,   # Entity-relationship graph
)
```

**1. VectorStoreIndex (use 90% of the time):**
```python
# Best for: "Find information relevant to my question"
index = VectorStoreIndex.from_documents(documents)
response = index.as_query_engine().query("What is the pricing model?")
# How: Embeds chunks → cosine similarity search → top-k retrieval
```

**2. SummaryIndex (formerly ListIndex):**
```python
# Best for: "Summarize everything"
index = SummaryIndex.from_documents(documents)
response = index.as_query_engine(response_mode="tree_summarize").query(
    "What are the key themes across all documents?"
)
# How: Passes ALL nodes to LLM (expensive for large datasets)
```

**3. TreeIndex:**
```python
# Best for: "Hierarchical summarization of long documents"
index = TreeIndex.from_documents(documents)
response = index.as_query_engine().query("What are the main topics?")
# How: Bottom-up tree → leaves are chunks, parents are summaries
```

**4. KeywordTableIndex:**
```python
# Best for: "Find documents with specific terms/codes/IDs"
index = KeywordTableIndex.from_documents(documents)
response = index.as_query_engine().query("Error code E-4501")
# How: Extracts keywords per chunk → keyword matching retrieval
```

**5. KnowledgeGraphIndex:**
```python
# Best for: "How is entity X related to entity Y?"
index = KnowledgeGraphIndex.from_documents(documents, max_triplets_per_chunk=10)
response = index.as_query_engine().query("How is CEO related to Product Z?")
# How: Extracts (subject, predicate, object) triples → graph query
```

**Decision matrix:**

| Need | Index Type |
|------|-----------|
| General Q&A | VectorStoreIndex |
| Summarization | SummaryIndex |
| Long document overview | TreeIndex |
| Exact keyword/code lookup | KeywordTableIndex |
| Relationship queries | KnowledgeGraphIndex |
| Best of vector + keyword | Hybrid (Vector + BM25) |

---

### Q5: How do you persist and reload an index so you don't re-embed documents every time?

**Answer:**

```python
# === SAVE ===
from llama_index.core import VectorStoreIndex, SimpleDirectoryReader

documents = SimpleDirectoryReader("./data").load_data()
index = VectorStoreIndex.from_documents(documents)  # Embeds all chunks (expensive!)

# Persist to disk
index.storage_context.persist(persist_dir="./my_index_storage")
# Creates: docstore.json, index_store.json, vector_store.json

# === LOAD (fast, no re-embedding!) ===
from llama_index.core import StorageContext, load_index_from_storage

storage_context = StorageContext.from_defaults(persist_dir="./my_index_storage")
index = load_index_from_storage(storage_context)

# Use it
query_engine = index.as_query_engine()
response = query_engine.query("What is the key finding?")
```

**For production, use a proper vector store:**
```python
import chromadb
from llama_index.vector_stores.chroma import ChromaVectorStore
from llama_index.core import VectorStoreIndex, StorageContext

# ChromaDB persists automatically
client = chromadb.PersistentClient(path="./chroma_db")
collection = client.get_or_create_collection("my_rag")
vector_store = ChromaVectorStore(chroma_collection=collection)

# First time: build and store
storage_context = StorageContext.from_defaults(vector_store=vector_store)
index = VectorStoreIndex.from_documents(documents, storage_context=storage_context)

# Later: just load from the vector store (instant)
index = VectorStoreIndex.from_vector_store(vector_store)
```

**Key point:** In-memory storage (`VectorStoreIndex.from_documents()`) is lost when the process exits. Always persist for production.

---

### Q6: How do you configure the LLM and embedding model in LlamaIndex?

**Answer:**

LlamaIndex uses a global `Settings` object for configuration:

```python
from llama_index.core import Settings

# ─── Option 1: OpenAI (default, requires API key) ───
from llama_index.llms.openai import OpenAI
from llama_index.embeddings.openai import OpenAIEmbedding

Settings.llm = OpenAI(model="gpt-4o-mini", temperature=0.1, max_tokens=1024)
Settings.embed_model = OpenAIEmbedding(model="text-embedding-3-small")

# ─── Option 2: Anthropic Claude ───
from llama_index.llms.anthropic import Anthropic
Settings.llm = Anthropic(model="claude-sonnet-4-20250514", temperature=0.1)
# Still use OpenAI or HuggingFace for embeddings (Anthropic doesn't have embedding API)

# ─── Option 3: 100% Local (free, private) ───
from llama_index.llms.ollama import Ollama
from llama_index.embeddings.huggingface import HuggingFaceEmbedding

Settings.llm = Ollama(model="llama3.1", request_timeout=120.0)
Settings.embed_model = HuggingFaceEmbedding(model_name="BAAI/bge-small-en-v1.5")

# ─── Other global settings ───
Settings.chunk_size = 1024        # Node chunk size
Settings.chunk_overlap = 200      # Overlap between chunks
Settings.num_output = 512         # Max LLM output tokens
Settings.embed_batch_size = 100   # Batch size for embedding API calls
```

**Per-index override (doesn't change global):**
```python
from llama_index.core import VectorStoreIndex

# This index uses a specific LLM, not the global one
index = VectorStoreIndex.from_documents(
    documents,
    embed_model=OpenAIEmbedding(model="text-embedding-3-large")
)

query_engine = index.as_query_engine(llm=OpenAI(model="gpt-4o"))
```

---

## Intermediate Level

### Q7: Explain hybrid search in LlamaIndex. Why is pure vector search sometimes insufficient?

**Answer:**

**The problem with pure vector search:**
Vector search matches by *meaning* but can miss exact terms. If a user searches for "error code E-4501", vector search might return documents about "error handling" instead of the specific code.

**Hybrid search = Vector (semantic) + BM25 (keyword)**

```python
from llama_index.core import VectorStoreIndex, SimpleDirectoryReader
from llama_index.core.retrievers import QueryFusionRetriever
from llama_index.retrievers.bm25 import BM25Retriever

# Load and index
documents = SimpleDirectoryReader("./data").load_data()
index = VectorStoreIndex.from_documents(documents)
nodes = list(index.docstore.docs.values())

# Two retrievers
vector_retriever = index.as_retriever(similarity_top_k=10)
bm25_retriever = BM25Retriever.from_defaults(nodes=nodes, similarity_top_k=10)

# Fuse results using Reciprocal Rank Fusion (RRF)
hybrid_retriever = QueryFusionRetriever(
    retrievers=[vector_retriever, bm25_retriever],
    retriever_weights=[0.6, 0.4],   # 60% semantic, 40% keyword
    similarity_top_k=5,
    num_queries=1,
    mode="reciprocal_rerank"
)

from llama_index.core.query_engine import RetrieverQueryEngine
query_engine = RetrieverQueryEngine.from_args(retriever=hybrid_retriever)

# Now handles both semantic AND keyword queries well
response = query_engine.query("What does error code E-4501 mean?")
```

**When to use hybrid search:**
| Scenario | Pure Vector | Hybrid |
|----------|------------|--------|
| "Explain the pricing strategy" | ✅ Good | ✅ Good |
| "Error code E-4501" | ❌ Misses | ✅ Finds exactly |
| "Policy ID P-2024-0893" | ❌ Misses | ✅ Finds exactly |
| "Tell me about machine learning" | ✅ Good | ✅ Good |
| Proper nouns, acronyms, codes | ❌ Poor | ✅ Strong |

---

### Q8: How do you implement re-ranking in LlamaIndex and why does it improve results?

**Answer:**

**The problem:** Vector search (ANN) is fast but approximate. The top-k results often include irrelevant nodes because cosine similarity on embeddings has limited precision.

**The fix:** Retrieve more candidates, then re-rank with a cross-encoder for precision.

```
Step 1: Vector search → retrieve top-20 (fast, approximate)
Step 2: Cross-encoder re-rank → keep top-5 (slow, precise)
```

```python
from llama_index.core import VectorStoreIndex, SimpleDirectoryReader
from llama_index.core.postprocessor import SentenceTransformerRerank

documents = SimpleDirectoryReader("./data").load_data()
index = VectorStoreIndex.from_documents(documents)

# Cross-encoder re-ranker
reranker = SentenceTransformerRerank(
    model="cross-encoder/ms-marco-MiniLM-L-2-v2",  # Fast, good quality
    top_n=3  # Keep top 3 after re-ranking
)

query_engine = index.as_query_engine(
    similarity_top_k=20,                  # Retrieve 20 candidates
    node_postprocessors=[reranker]        # Re-rank to top 3
)

response = query_engine.query("What are the security requirements?")

# You can also chain multiple postprocessors
from llama_index.core.postprocessor import MetadataReplacementPostProcessor

query_engine = index.as_query_engine(
    similarity_top_k=20,
    node_postprocessors=[
        # Step 1: Replace sentence window with full surrounding context
        MetadataReplacementPostProcessor(target_metadata_key="window"),
        # Step 2: Re-rank expanded context
        reranker
    ]
)
```

**Impact:** Re-ranking typically improves retrieval precision by 15-25% with minimal latency increase (~50-100ms for cross-encoder inference).

---

### Q9: How does the SubQuestionQueryEngine work? When should you use it?

**Answer:**

The **SubQuestionQueryEngine** breaks a complex question into simpler sub-questions, routes each to the appropriate data source, and combines the answers.

**When to use:** Questions that span multiple documents/domains and can't be answered by a single retrieval.

```python
from llama_index.core import VectorStoreIndex, SimpleDirectoryReader
from llama_index.core.tools import QueryEngineTool, ToolMetadata
from llama_index.core.query_engine import SubQuestionQueryEngine

# Separate indexes for different domains
hr_docs = SimpleDirectoryReader("./data/hr").load_data()
finance_docs = SimpleDirectoryReader("./data/finance").load_data()
engineering_docs = SimpleDirectoryReader("./data/engineering").load_data()

hr_index = VectorStoreIndex.from_documents(hr_docs)
finance_index = VectorStoreIndex.from_documents(finance_docs)
eng_index = VectorStoreIndex.from_documents(engineering_docs)

# Define tools with clear descriptions
tools = [
    QueryEngineTool(
        query_engine=hr_index.as_query_engine(),
        metadata=ToolMetadata(
            name="hr_policies",
            description="Contains HR policies, benefits, leave policies, hiring processes"
        )
    ),
    QueryEngineTool(
        query_engine=finance_index.as_query_engine(),
        metadata=ToolMetadata(
            name="financial_reports",
            description="Contains revenue data, budgets, quarterly reports, financial forecasts"
        )
    ),
    QueryEngineTool(
        query_engine=eng_index.as_query_engine(),
        metadata=ToolMetadata(
            name="engineering_docs",
            description="Contains architecture docs, API specs, deployment guides, tech stack"
        )
    ),
]

# SubQuestion engine
engine = SubQuestionQueryEngine.from_defaults(query_engine_tools=tools)

# Complex question → decomposed into sub-questions
response = engine.query(
    "How much budget is allocated to engineering hiring, "
    "and what are the technical requirements for senior roles?"
)

# Internally generates:
# Sub-Q1: "What is the budget allocated to engineering hiring?" → finance_reports
# Sub-Q2: "What are the technical requirements for senior engineering roles?" → hr_policies + engineering_docs
# Then combines answers into a coherent response
```

---

### Q10: How do you build a chat engine with conversation memory in LlamaIndex?

**Answer:**

```python
from llama_index.core import VectorStoreIndex, SimpleDirectoryReader

documents = SimpleDirectoryReader("./data").load_data()
index = VectorStoreIndex.from_documents(documents)

# Chat engine with memory
chat_engine = index.as_chat_engine(
    chat_mode="condense_plus_context",  # Best mode for most cases
    similarity_top_k=5,
    verbose=True  # See the condensed query
)

# Conversation with context
r1 = chat_engine.chat("What products does the company offer?")
print(r1)

# Follow-up — the engine condenses this + chat history into a standalone query
r2 = chat_engine.chat("Which one launched most recently?")
print(r2)
# Internally: "Which product launched most recently?" (condensed from context)

r3 = chat_engine.chat("What are its key features?")
print(r3)
# Internally: "What are the key features of [most recently launched product]?"

# Reset conversation
chat_engine.reset()
```

**Chat modes explained:**

| Mode | How It Works | Best For |
|------|-------------|----------|
| `condense_question` | Condenses follow-up into standalone query, then retrieves | Simple follow-ups |
| `context` | Retrieves context for every message (no condensing) | Independent questions |
| `condense_plus_context` | Condenses + retrieves (combines both) | **Most use cases** |
| `react` | Full ReAct agent with tool use | Complex reasoning |

**Custom memory:**
```python
from llama_index.core.memory import ChatMemoryBuffer

memory = ChatMemoryBuffer.from_defaults(token_limit=3000)

chat_engine = index.as_chat_engine(
    chat_mode="condense_plus_context",
    memory=memory
)
```

---

### Q11: How do you use metadata filtering to improve retrieval precision?

**Answer:**

Metadata filtering narrows the search space BEFORE semantic search happens. Critical for multi-tenant systems, time-based data, or categorized documents.

```python
from llama_index.core import VectorStoreIndex, Document
from llama_index.core.vector_stores import (
    MetadataFilters,
    MetadataFilter,
    FilterOperator,
    FilterCondition
)

# Documents with rich metadata
documents = [
    Document(text="Q1 2024 revenue: $50B", metadata={"quarter": "Q1", "year": 2024, "dept": "finance"}),
    Document(text="Q2 2024 revenue: $55B", metadata={"quarter": "Q2", "year": 2024, "dept": "finance"}),
    Document(text="Q1 2023 revenue: $42B", metadata={"quarter": "Q1", "year": 2023, "dept": "finance"}),
    Document(text="New AI features spec", metadata={"quarter": "Q1", "year": 2024, "dept": "engineering"}),
    Document(text="Hiring plan for 2024", metadata={"quarter": "Q1", "year": 2024, "dept": "hr"}),
]

index = VectorStoreIndex.from_documents(documents)

# Filter: only 2024 financial documents
filters = MetadataFilters(
    filters=[
        MetadataFilter(key="year", value=2024, operator=FilterOperator.EQ),
        MetadataFilter(key="dept", value="finance", operator=FilterOperator.EQ),
    ],
    condition=FilterCondition.AND  # Both must match
)

query_engine = index.as_query_engine(filters=filters, similarity_top_k=5)
response = query_engine.query("What was the revenue?")
# Only searches Q1 2024 and Q2 2024 finance docs

# OR condition: engineering OR finance docs
or_filters = MetadataFilters(
    filters=[
        MetadataFilter(key="dept", value="finance"),
        MetadataFilter(key="dept", value="engineering"),
    ],
    condition=FilterCondition.OR
)

# Range filters
range_filters = MetadataFilters(
    filters=[
        MetadataFilter(key="year", value=2023, operator=FilterOperator.GTE),
        MetadataFilter(key="year", value=2024, operator=FilterOperator.LTE),
    ]
)
```

**Production pattern — multi-tenant RAG:**
```python
def query_for_user(user_id: str, question: str):
    """Each user only sees their own data."""
    filters = MetadataFilters(
        filters=[MetadataFilter(key="user_id", value=user_id)]
    )
    return index.as_query_engine(filters=filters).query(question)
```

---

### Q12: Explain the Ingestion Pipeline in LlamaIndex. How does it differ from basic `from_documents()`?

**Answer:**

`from_documents()` is a convenience method that does everything in one shot. `IngestionPipeline` gives you fine-grained control with caching, custom transformations, and incremental processing.

```python
from llama_index.core.ingestion import IngestionPipeline, IngestionCache
from llama_index.core.node_parser import SentenceSplitter
from llama_index.core.extractors import TitleExtractor, SummaryExtractor, QuestionsAnsweredExtractor
from llama_index.embeddings.openai import OpenAIEmbedding

# Define transformation pipeline
pipeline = IngestionPipeline(
    transformations=[
        # Step 1: Split into chunks
        SentenceSplitter(chunk_size=1024, chunk_overlap=200),

        # Step 2: Extract title metadata (LLM call)
        TitleExtractor(nodes=5),

        # Step 3: Generate summary metadata (LLM call)
        SummaryExtractor(summaries=["self"]),

        # Step 4: Generate hypothetical questions (for HyDE-like retrieval)
        QuestionsAnsweredExtractor(questions=3),

        # Step 5: Embed
        OpenAIEmbedding(model="text-embedding-3-small"),
    ],
    # Cache: skip re-processing unchanged documents
    cache=IngestionCache()
)

# Run pipeline
from llama_index.core import SimpleDirectoryReader
documents = SimpleDirectoryReader("./data").load_data()
nodes = pipeline.run(documents=documents, show_progress=True)

# Build index from processed nodes
from llama_index.core import VectorStoreIndex
index = VectorStoreIndex(nodes)

# Later: add new documents (only new ones are processed, thanks to cache)
new_docs = SimpleDirectoryReader("./data/new").load_data()
new_nodes = pipeline.run(documents=new_docs)
index.insert_nodes(new_nodes)
```

**Comparison:**

| Feature | `from_documents()` | `IngestionPipeline` |
|---------|-------------------|---------------------|
| Setup complexity | 1 line | 10+ lines |
| Custom transformations | No | Yes (any order) |
| Metadata extraction | No | Title, summary, questions |
| Caching | No (re-embeds everything) | Yes (skip unchanged docs) |
| Incremental updates | Limited | First-class support |
| Production use | Prototyping | Recommended |

---

## Advanced Level

### Q13: Design an agentic RAG system that can reason about which tools to use, when to retrieve, and when to compute.

**Answer:**

Agentic RAG goes beyond "retrieve then answer." The agent decides *if*, *when*, and *how* to retrieve.

```python
from llama_index.core import VectorStoreIndex, SimpleDirectoryReader, Settings
from llama_index.core.tools import QueryEngineTool, ToolMetadata, FunctionTool
from llama_index.core.agent import ReActAgent
from llama_index.llms.openai import OpenAI
import yfinance as yf
from datetime import datetime

Settings.llm = OpenAI(model="gpt-4o", temperature=0)

# ─── Tool 1: RAG over internal documents ───
docs = SimpleDirectoryReader("./data/company").load_data()
index = VectorStoreIndex.from_documents(docs)

rag_tool = QueryEngineTool(
    query_engine=index.as_query_engine(similarity_top_k=5),
    metadata=ToolMetadata(
        name="company_docs",
        description="Search internal company documents for policies, reports, and procedures. "
                    "Use this when the question is about company-specific information."
    )
)

# ─── Tool 2: Live stock data ───
def get_stock_price(ticker: str) -> str:
    """Get current stock price for a given ticker symbol."""
    stock = yf.Ticker(ticker)
    price = stock.info.get("currentPrice", "N/A")
    return f"{ticker} current price: ${price}"

stock_tool = FunctionTool.from_defaults(fn=get_stock_price)

# ─── Tool 3: Calculator ───
def calculate(expression: str) -> str:
    """Evaluate a mathematical expression. Input should be a valid Python math expression."""
    try:
        result = eval(expression)  # In production, use a safe math parser
        return str(result)
    except Exception as e:
        return f"Error: {e}"

calc_tool = FunctionTool.from_defaults(fn=calculate)

# ─── Tool 4: Date/time ───
def get_current_datetime() -> str:
    """Get the current date and time."""
    return datetime.now().strftime("%Y-%m-%d %H:%M:%S")

date_tool = FunctionTool.from_defaults(fn=get_current_datetime)

# ─── Agentic RAG ───
agent = ReActAgent.from_tools(
    tools=[rag_tool, stock_tool, calc_tool, date_tool],
    verbose=True,
    max_iterations=10
)

# The agent reasons about which tools to use:
# Q: "What is our stock buyback policy and how much would it cost at current prices?"
# Agent thinks: search docs for buyback policy → get stock price → calculate cost
response = agent.chat(
    "What is our stock buyback policy and how much would 1M shares cost at current price?"
)

# Agent trace:
# Thought: I need to find the buyback policy first
# Action: company_docs("stock buyback policy")
# Observation: "The company's buyback policy allows up to 5M shares per quarter..."
# Thought: Now I need the current stock price
# Action: get_stock_price("AAPL")
# Observation: "AAPL current price: $185.50"
# Thought: Now I can calculate
# Action: calculate("1000000 * 185.50")
# Observation: "185500000.0"
# Answer: "The buyback policy allows up to 5M shares/quarter. 1M shares at $185.50 = $185.5M"
```

**Key design principles:**
1. Tool descriptions must be precise — the agent selects tools based on descriptions
2. Give the agent enough tools but not too many (5-10 is ideal)
3. Include a "fallback" tool for general knowledge
4. Set `max_iterations` to prevent runaway loops
5. Use `verbose=True` during development to inspect agent reasoning

---

### Q14: How would you design a multi-document agent system for comparing information across many documents?

**Answer:**

The multi-document agent pattern creates per-document tools (vector search + summary) and wraps them in an agent that can reason about which documents to consult.

```python
from llama_index.core import VectorStoreIndex, SummaryIndex, SimpleDirectoryReader, Settings
from llama_index.core.tools import QueryEngineTool, ToolMetadata
from llama_index.core.agent import ReActAgent
from llama_index.core.objects import ObjectIndex
from pathlib import Path

Settings.llm = OpenAI(model="gpt-4o", temperature=0)

def build_document_agent_tools(doc_dir: str) -> list:
    """Build vector + summary tools for each document in a directory."""
    tools = []
    for file_path in Path(doc_dir).glob("*.pdf"):
        doc_name = file_path.stem

        # Load single document
        docs = SimpleDirectoryReader(input_files=[str(file_path)]).load_data()

        # Two indexes per document
        vector_index = VectorStoreIndex.from_documents(docs)
        summary_index = SummaryIndex.from_documents(docs)

        # Two tools per document
        tools.append(QueryEngineTool(
            query_engine=vector_index.as_query_engine(similarity_top_k=3),
            metadata=ToolMetadata(
                name=f"{doc_name}_search",
                description=f"Search the {doc_name} document for specific facts and details"
            )
        ))
        tools.append(QueryEngineTool(
            query_engine=summary_index.as_query_engine(response_mode="tree_summarize"),
            metadata=ToolMetadata(
                name=f"{doc_name}_summary",
                description=f"Get a comprehensive summary of the {doc_name} document"
            )
        ))

    return tools

# Build tools for all company 10-K filings
tools = build_document_agent_tools("./data/10k_filings")
# E.g., apple_2024_search, apple_2024_summary, google_2024_search, google_2024_summary, ...

# For many documents (20+), use ObjectIndex so the agent can handle the tool list
obj_index = ObjectIndex.from_objects(tools, index_cls=VectorStoreIndex)
obj_retriever = obj_index.as_retriever(similarity_top_k=4)

# Agent with dynamic tool retrieval
agent = ReActAgent.from_tools(
    tool_retriever=obj_retriever,  # Dynamically selects relevant tools per query
    verbose=True,
    max_iterations=15
)

# Cross-document comparison
response = agent.chat(
    "Compare Apple and Google's AI strategy and R&D spending for 2024. "
    "Which company is investing more aggressively?"
)
```

**Scaling considerations:**
- Up to 10 documents: Use flat tool list (`from_tools(tools)`)
- 10-100 documents: Use `ObjectIndex` for dynamic tool retrieval
- 100+ documents: Use a two-level hierarchy (category → document → tools)

---

### Q15: How would you build a production RAG system with evaluation, monitoring, and continuous improvement?

**Answer:**

A production RAG system needs: **evaluation pipeline**, **observability**, **feedback loop**, and **automated testing**.

```python
# ── 1. Build the RAG pipeline ──
from llama_index.core import VectorStoreIndex, StorageContext
from llama_index.vector_stores.chroma import ChromaVectorStore
from llama_index.core.node_parser import SentenceSplitter
from llama_index.core.postprocessor import SentenceTransformerRerank
from llama_index.core.ingestion import IngestionPipeline
import chromadb

# Persistent vector store
client = chromadb.PersistentClient(path="./production_db")
collection = client.get_or_create_collection("production_rag")
vector_store = ChromaVectorStore(chroma_collection=collection)

# Ingestion with metadata extraction
pipeline = IngestionPipeline(
    transformations=[
        SentenceSplitter(chunk_size=1024, chunk_overlap=200),
    ]
)

# ── 2. Evaluation Framework ──
from llama_index.core.evaluation import (
    FaithfulnessEvaluator, RelevancyEvaluator,
    CorrectnessEvaluator, BatchEvalRunner
)

# Golden test set (maintain 50+ question-answer pairs)
golden_qa_pairs = [
    {"query": "What is the refund policy?", "expected": "30-day money-back guarantee"},
    {"query": "What are the pricing tiers?", "expected": "Free, Pro ($29/mo), Enterprise (custom)"},
    # ... 50+ more
]

async def run_evaluation(query_engine, golden_set):
    """Run full evaluation suite."""
    faithfulness = FaithfulnessEvaluator()
    relevancy = RelevancyEvaluator()

    runner = BatchEvalRunner(
        evaluators={"faithfulness": faithfulness, "relevancy": relevancy},
        workers=4
    )

    queries = [qa["query"] for qa in golden_set]
    results = await runner.aevaluate_queries(query_engine, queries=queries)

    # Aggregate metrics
    faith_scores = [r.score for r in results["faithfulness"]]
    rel_scores = [r.score for r in results["relevancy"]]

    return {
        "faithfulness_avg": sum(faith_scores) / len(faith_scores),
        "relevancy_avg": sum(rel_scores) / len(rel_scores),
        "total_queries": len(queries),
        "faith_pass_rate": sum(1 for s in faith_scores if s >= 0.5) / len(faith_scores),
    }

# ── 3. Observability (log every query) ──
import logging
import json
from datetime import datetime

logger = logging.getLogger("rag_production")

def query_with_logging(query_engine, query: str, user_id: str = "anonymous"):
    """Query with full observability."""
    start = datetime.now()
    response = query_engine.query(query)
    latency = (datetime.now() - start).total_seconds()

    log_entry = {
        "timestamp": start.isoformat(),
        "user_id": user_id,
        "query": query,
        "response": str(response)[:500],
        "latency_seconds": latency,
        "num_sources": len(response.source_nodes),
        "source_scores": [n.score for n in response.source_nodes],
    }
    logger.info(json.dumps(log_entry))
    return response

# ── 4. A/B Testing Different Configurations ──
def create_query_engine_v1(index):
    """Baseline: simple vector search."""
    return index.as_query_engine(similarity_top_k=5)

def create_query_engine_v2(index):
    """Improved: hybrid + re-ranking."""
    reranker = SentenceTransformerRerank(
        model="cross-encoder/ms-marco-MiniLM-L-2-v2", top_n=3
    )
    return index.as_query_engine(
        similarity_top_k=10,
        node_postprocessors=[reranker]
    )

# Compare
# v1_metrics = await run_evaluation(v1_engine, golden_set)
# v2_metrics = await run_evaluation(v2_engine, golden_set)
# Deploy the winner
```

**Production checklist:**
```
□ Persistent vector store (ChromaDB/Pinecone/Qdrant)
□ Evaluation pipeline with golden test set (50+ QA pairs)
□ Query logging (latency, sources, scores)
□ Error handling and fallbacks
□ Rate limiting for LLM API calls
□ Incremental indexing (add/update/delete docs)
□ Health check endpoint
□ A/B testing framework for config changes
□ User feedback collection (thumbs up/down)
□ Automated regression testing in CI/CD
```

---

### Q16: How do you handle multi-modal data (text + images + tables) in LlamaIndex?

**Answer:**

LlamaIndex supports multi-modal RAG through specialized parsers and multi-modal LLMs.

```python
# ── 1. Parse documents with tables and images ──
from llama_index.core import SimpleDirectoryReader
from llama_index.readers.file import PDFReader

# Use unstructured.io for complex PDFs with images + tables
from llama_index.readers.file import UnstructuredReader
reader = UnstructuredReader()
documents = reader.load_data(file="./data/report_with_images.pdf")

# ── 2. Multi-modal index ──
from llama_index.core import VectorStoreIndex, Settings
from llama_index.multi_modal_llms.openai import OpenAIMultiModal
from llama_index.core.schema import ImageDocument, TextNode

# Configure multi-modal LLM
mm_llm = OpenAIMultiModal(model="gpt-4o", max_new_tokens=1024)

# Create image documents
image_docs = [
    ImageDocument(image_path="./data/chart1.png", metadata={"type": "revenue_chart"}),
    ImageDocument(image_path="./data/diagram1.png", metadata={"type": "architecture"}),
]

# Build multi-modal index
from llama_index.core.indices.multi_modal import MultiModalVectorStoreIndex

mm_index = MultiModalVectorStoreIndex.from_documents(
    documents + image_docs,
    # image_embed_model=clip_embed_model  # Optional: CLIP for image embeddings
)

# Query across text AND images
query_engine = mm_index.as_query_engine(multi_modal_llm=mm_llm)
response = query_engine.query("What does the revenue chart show?")
```

**Table handling:**
```python
from llama_index.core.node_parser import MarkdownNodeParser

# Parse markdown tables from PDFs
parser = MarkdownNodeParser()
nodes = parser.get_nodes_from_documents(documents)

# Tables are preserved as markdown in nodes
# The LLM can reason over tabular data in markdown format
```

---

### Q17: How would you implement a custom retriever that combines vector search with a SQL database for structured + unstructured data?

**Answer:**

This is a common enterprise pattern: unstructured documents (PDFs, wikis) + structured data (SQL database) together.

```python
from llama_index.core import VectorStoreIndex, SQLDatabase, SimpleDirectoryReader
from llama_index.core.retrievers import BaseRetriever
from llama_index.core.schema import NodeWithScore, TextNode, QueryBundle
from llama_index.core.query_engine import RetrieverQueryEngine
from sqlalchemy import create_engine, text
from typing import List

class HybridSQLVectorRetriever(BaseRetriever):
    """Retrieves from both SQL database AND vector index."""

    def __init__(self, vector_index, sql_engine, sql_table: str, top_k: int = 5):
        self.vector_retriever = vector_index.as_retriever(similarity_top_k=top_k)
        self.sql_engine = sql_engine
        self.sql_table = sql_table
        self.top_k = top_k
        super().__init__()

    def _retrieve(self, query_bundle: QueryBundle) -> List[NodeWithScore]:
        # 1. Vector search over unstructured docs
        vector_nodes = self.vector_retriever.retrieve(query_bundle)

        # 2. SQL search over structured data
        sql_nodes = self._sql_search(query_bundle.query_str)

        # 3. Combine and interleave results
        combined = []
        for i, (v_node, s_node) in enumerate(
            zip(vector_nodes[:self.top_k], sql_nodes[:self.top_k])
        ):
            combined.append(v_node)
            combined.append(s_node)

        # Add remaining nodes
        combined.extend(vector_nodes[self.top_k:])
        combined.extend(sql_nodes[self.top_k:])

        return combined[:self.top_k * 2]

    def _sql_search(self, query: str) -> List[NodeWithScore]:
        """Simple keyword search in SQL. In production, use NL-to-SQL."""
        keywords = query.lower().split()[:5]
        conditions = " OR ".join([f"description LIKE '%{kw}%'" for kw in keywords])

        with self.sql_engine.connect() as conn:
            result = conn.execute(text(
                f"SELECT id, name, description, category FROM {self.sql_table} "
                f"WHERE {conditions} LIMIT {self.top_k}"
            ))
            rows = result.fetchall()

        nodes = []
        for row in rows:
            node = TextNode(
                text=f"Product: {row.name}\nCategory: {row.category}\nDescription: {row.description}",
                metadata={"source": "sql_database", "id": str(row.id)}
            )
            nodes.append(NodeWithScore(node=node, score=0.8))
        return nodes


# Usage
documents = SimpleDirectoryReader("./data/docs").load_data()
vector_index = VectorStoreIndex.from_documents(documents)
sql_engine = create_engine("sqlite:///./data/products.db")

retriever = HybridSQLVectorRetriever(
    vector_index=vector_index,
    sql_engine=sql_engine,
    sql_table="products",
    top_k=5
)

query_engine = RetrieverQueryEngine.from_args(retriever=retriever)
response = query_engine.query("What premium products do we offer and what's the policy on returns?")
# Combines SQL product data + document return policy
```

---

### Q18: Explain the Sentence Window Retrieval pattern and how Auto-Merging Retriever works. When do each shine?

**Answer:**

Both solve the same problem: **small chunks are good for precise retrieval, but the LLM needs more context for good answers.**

### Sentence Window Retrieval

Embed small windows (1-3 sentences), but at synthesis time, expand to the surrounding window.

```python
from llama_index.core import VectorStoreIndex, SimpleDirectoryReader
from llama_index.core.node_parser import SentenceWindowNodeParser
from llama_index.core.postprocessor import MetadataReplacementPostProcessor

documents = SimpleDirectoryReader("./data").load_data()

# Parse: each node = 1 sentence, but stores surrounding window in metadata
node_parser = SentenceWindowNodeParser.from_defaults(
    window_size=3,  # 3 sentences on each side
    window_metadata_key="window",
    original_text_metadata_key="original_text"
)

nodes = node_parser.get_nodes_from_documents(documents)
index = VectorStoreIndex(nodes)

# At query time: retrieve by sentence embedding, replace with full window
query_engine = index.as_query_engine(
    similarity_top_k=5,
    node_postprocessors=[
        MetadataReplacementPostProcessor(target_metadata_key="window")
    ]
)

response = query_engine.query("What is the key finding?")
# Retrieved: precise 1-sentence match
# Sent to LLM: 7-sentence window around the match (3 before + 1 match + 3 after)
```

### Auto-Merging Retriever

Create hierarchical chunks (large → medium → small). Search at the leaf level. If enough leaves from one parent match, merge up to the parent.

```python
from llama_index.core import VectorStoreIndex, SimpleDirectoryReader, StorageContext
from llama_index.core.node_parser import HierarchicalNodeParser, get_leaf_nodes
from llama_index.core.retrievers import AutoMergingRetriever
from llama_index.core.query_engine import RetrieverQueryEngine

documents = SimpleDirectoryReader("./data").load_data()

# 3-level hierarchy: 2048 → 512 → 128 tokens
node_parser = HierarchicalNodeParser.from_defaults(chunk_sizes=[2048, 512, 128])
nodes = node_parser.get_nodes_from_documents(documents)
leaf_nodes = get_leaf_nodes(nodes)

# Store all levels in docstore, index only leaves
storage_context = StorageContext.from_defaults()
storage_context.docstore.add_documents(nodes)
index = VectorStoreIndex(leaf_nodes, storage_context=storage_context)

# Auto-merge: if >30% of a parent's children match, return the parent instead
retriever = AutoMergingRetriever(
    index.as_retriever(similarity_top_k=12),
    storage_context=storage_context,
    simple_ratio_thresh=0.3
)

query_engine = RetrieverQueryEngine.from_args(retriever=retriever)
response = query_engine.query("Explain the architecture in detail")
```

### Comparison

| Aspect | Sentence Window | Auto-Merging |
|--------|----------------|--------------|
| Retrieval granularity | Sentence-level | Leaf chunk level |
| Context expansion | Fixed window (N sentences) | Dynamic (parent merge) |
| Best for | Dense, information-rich text | Structured documents with sections |
| Storage overhead | Low (metadata) | Medium (3 levels of nodes) |
| Implementation complexity | Simple | Moderate |
| When it shines | Legal docs, research papers | Technical docs, manuals, reports |

---

## Bonus: Quick Reference Cheat Sheet

```python
# ── Setup ──
pip install llama-index
from llama_index.core import Settings
Settings.llm = OpenAI(model="gpt-4o-mini")

# ── Load ──
docs = SimpleDirectoryReader("./data").load_data()

# ── Index ──
index = VectorStoreIndex.from_documents(docs)

# ── Query ──
engine = index.as_query_engine(similarity_top_k=5)
response = engine.query("Your question here")

# ── Chat ──
chat = index.as_chat_engine(chat_mode="condense_plus_context")
response = chat.chat("Your question")

# ── Persist ──
index.storage_context.persist("./storage")
index = load_index_from_storage(StorageContext.from_defaults(persist_dir="./storage"))

# ── Evaluate ──
evaluator = FaithfulnessEvaluator()
result = evaluator.evaluate_response(response=response)
```
