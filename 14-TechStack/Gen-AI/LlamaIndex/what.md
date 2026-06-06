# LlamaIndex — Complete Learning Guide

## Table of Contents

1. [What is LlamaIndex?](#what-is-llamaindex)
2. [Problem It Solves](#problem-it-solves)
3. [LlamaIndex vs LangChain](#llamaindex-vs-langchain)
4. [Core Concepts](#core-concepts)
5. [Architecture Overview](#architecture-overview)
6. [Installation & Setup](#installation--setup)
7. [Beginner: Your First RAG Pipeline](#beginner-your-first-rag-pipeline)
8. [Intermediate Patterns](#intermediate-patterns)
9. [Advanced Architectures](#advanced-architectures)
10. [Data Connectors (LlamaHub)](#data-connectors-llamahub)
11. [Production Deployment](#production-deployment)
12. [Best Practices](#best-practices)
13. [Common Pitfalls](#common-pitfalls)
14. [Real-World Use Cases](#real-world-use-cases)
15. [Performance Optimization](#performance-optimization)
16. [Ecosystem & Community](#ecosystem--community)

---

## What is LlamaIndex?

LlamaIndex (formerly GPT Index) is a **data framework for LLM applications**. It specializes in connecting your private data to large language models through a technique called **Retrieval-Augmented Generation (RAG)**.

Think of it this way:
- **LLMs** (GPT-4, Claude, Llama) know a lot about the world — but they know nothing about YOUR data
- **LlamaIndex** bridges that gap — it ingests, structures, indexes, and retrieves your data so LLMs can answer questions about it accurately

### Key Identity

```
LlamaIndex = Data Framework for LLM Apps
           = Ingestion + Indexing + Querying + Retrieval
           = The "data plumbing" layer between your data and LLMs
```

LlamaIndex is NOT a general-purpose AI orchestration framework (that's LangChain). It is laser-focused on one thing: **making your data accessible to LLMs**.

### Core Philosophy

1. **Data-first**: Your data is the moat, not the model
2. **Modular**: Swap any component (LLM, embeddings, vector store, retriever)
3. **Production-ready**: Not just prototyping — scales to enterprise RAG
4. **Opinionated defaults, flexible overrides**: Works out of the box, customizable when needed

---

## Problem It Solves

### The Fundamental LLM Problem

```
User: "What was our Q3 revenue?"
GPT-4: "I don't have access to your company's financial data."

User: "Summarize the last board meeting notes."
GPT-4: "I don't have access to your internal documents."
```

### Naive Solutions (and why they fail)

| Approach | Problem |
|----------|---------|
| Paste everything into the prompt | Context window limits (even 128K tokens isn't enough for large datasets) |
| Fine-tune the LLM | Expensive, doesn't update with new data, hallucinates facts |
| Just use embeddings + vector search | Works for simple cases, fails for complex multi-step reasoning |

### LlamaIndex Solution: Structured RAG

```
1. INGEST   → Load your data (PDFs, databases, APIs, Slack, etc.)
2. INDEX    → Create searchable indexes (vector, keyword, tree, graph)
3. QUERY    → User asks a question
4. RETRIEVE → Find the most relevant chunks
5. SYNTHESIZE → LLM generates answer using retrieved context
6. RESPOND  → Return accurate, grounded answer
```

This gives you:
- **Accuracy** — answers grounded in your actual data
- **Freshness** — indexes update as data changes
- **Scalability** — handles millions of documents
- **Transparency** — you can see what sources were used

---

## LlamaIndex vs LangChain

This is the #1 question people ask. They are **complementary, not competitors**.

| Dimension | LlamaIndex | LangChain |
|-----------|-----------|-----------|
| **Primary Focus** | Data indexing & retrieval (RAG) | LLM orchestration & chaining |
| **Metaphor** | "The librarian" — organizes & finds your data | "The conductor" — orchestrates LLM workflows |
| **Strength** | Deep RAG, index types, retrieval strategies | Chains, agents, tool use, memory |
| **Data Connectors** | 150+ via LlamaHub | Fewer built-in, relies on custom loaders |
| **Index Types** | Vector, Summary, Tree, Keyword, Knowledge Graph | Primarily vector-based |
| **Query Complexity** | Sub-question, routing, multi-doc, agentic RAG | Chain-of-thought, ReAct agents |
| **Learning Curve** | Easier for RAG-specific use cases | Steeper, more general-purpose |
| **When to Use** | "I need to query my data" | "I need to build complex AI workflows" |
| **Production RAG** | First-class citizen, deeply optimized | Possible but requires more manual work |

### Can You Use Both?

Yes! Common pattern:

```python
# LlamaIndex for RAG
from llama_index.core import VectorStoreIndex
index = VectorStoreIndex.from_documents(documents)
query_engine = index.as_query_engine()

# LangChain for orchestration
from langchain.agents import Tool
tools = [
    Tool(name="RAG Search", func=query_engine.query, description="Search company docs")
]
# Use LangChain agent with LlamaIndex as a tool
```

### Decision Matrix

```
Need simple RAG?                    → LlamaIndex alone
Need complex multi-step agents?     → LangChain alone
Need RAG + agents + tools?          → LlamaIndex (RAG) + LangChain (orchestration)
Need production RAG pipeline?       → LlamaIndex
Need prompt chaining?               → LangChain
Building a chatbot over your docs?  → LlamaIndex
Building a general AI assistant?    → LangChain
```

---

## Core Concepts

### 1. Documents

A `Document` is the top-level container for your data. It wraps raw text with metadata.

```python
from llama_index.core import Document

# Create a document manually
doc = Document(
    text="LlamaIndex is a data framework for LLM applications.",
    metadata={"source": "website", "author": "Jerry Liu", "date": "2024-01-15"},
    doc_id="doc_001"
)

# Documents are typically loaded via data connectors
from llama_index.core import SimpleDirectoryReader
documents = SimpleDirectoryReader("./data").load_data()
# Each file becomes a Document object
```

**Key properties:**
- `text` — the raw content
- `metadata` — key-value pairs (source, date, author, etc.)
- `doc_id` — unique identifier
- `relationships` — links to other documents

### 2. Nodes

A `Node` is a chunk of a Document. LlamaIndex splits Documents into Nodes for indexing.

```python
from llama_index.core.node_parser import SentenceSplitter

# Split documents into nodes (chunks)
parser = SentenceSplitter(chunk_size=1024, chunk_overlap=200)
nodes = parser.get_nodes_from_documents(documents)

# Each node has:
# - text (the chunk content)
# - metadata (inherited from parent document + chunk-specific)
# - relationships (prev/next node, parent document)
# - embedding (computed during indexing)
```

**Why Nodes matter:**
- Documents can be huge (100-page PDFs) — too big for LLM context
- Nodes are right-sized chunks that can be individually embedded and retrieved
- Relationships between nodes preserve document structure

**Node parsers available:**
- `SentenceSplitter` — splits by sentences, respects chunk_size
- `TokenTextSplitter` — splits by token count
- `HierarchicalNodeParser` — creates parent/child node hierarchy
- `SemanticSplitterNodeParser` — splits by semantic similarity (uses embeddings)
- `MarkdownNodeParser` — respects markdown structure (headers, sections)
- `HTMLNodeParser` — parses HTML structure
- `CodeSplitter` — splits code by functions/classes

### 3. Indexes

Indexes are the heart of LlamaIndex. They organize nodes for efficient retrieval.

#### VectorStoreIndex (Most Common)

Stores node embeddings in a vector store. Retrieves by semantic similarity.

```python
from llama_index.core import VectorStoreIndex

# Build index (embeds all nodes using the configured embedding model)
index = VectorStoreIndex.from_documents(documents)

# Query — finds top-k most similar nodes
query_engine = index.as_query_engine(similarity_top_k=5)
response = query_engine.query("What is our refund policy?")
```

**When to use:** Default choice. Works for 90% of RAG use cases.

#### SummaryIndex (formerly ListIndex)

Stores all nodes and passes them ALL to the LLM. No retrieval step — synthesizes over everything.

```python
from llama_index.core import SummaryIndex

index = SummaryIndex.from_documents(documents)
query_engine = index.as_query_engine(response_mode="tree_summarize")
response = query_engine.query("Summarize the key themes across all documents")
```

**When to use:** When you need a summary across ALL documents. Small datasets only (everything goes to LLM).

#### TreeIndex

Builds a tree structure bottom-up. Leaf nodes are chunks, parent nodes are summaries.

```python
from llama_index.core import TreeIndex

index = TreeIndex.from_documents(documents)
query_engine = index.as_query_engine(child_branch_factor=2)
response = query_engine.query("What are the main topics?")
```

**When to use:** Hierarchical summarization. Good for long documents where you want multi-level abstraction.

#### KeywordTableIndex

Extracts keywords from each node. Retrieves nodes matching query keywords.

```python
from llama_index.core import KeywordTableIndex

index = KeywordTableIndex.from_documents(documents)
query_engine = index.as_query_engine()
response = query_engine.query("Tell me about machine learning")
# Retrieves nodes containing "machine", "learning" keywords
```

**When to use:** When semantic similarity isn't enough — keyword matching for specific terms, codes, IDs.

#### KnowledgeGraphIndex

Builds a knowledge graph from text (entity-relationship triples).

```python
from llama_index.core import KnowledgeGraphIndex

index = KnowledgeGraphIndex.from_documents(
    documents,
    max_triplets_per_chunk=10,
    include_embeddings=True
)
query_engine = index.as_query_engine(include_text=True)
response = query_engine.query("How is Company X related to Product Y?")
```

**When to use:** Relationship-heavy data. When you need to traverse connections between entities.

### Index Comparison Table

| Index Type | Retrieval Method | Build Cost | Query Cost | Best For |
|-----------|-----------------|-----------|-----------|---------|
| VectorStoreIndex | Semantic similarity | Medium (embedding) | Low (ANN search) | General RAG, most use cases |
| SummaryIndex | Scan all nodes | Low (no embedding) | High (all to LLM) | Full-document summarization |
| TreeIndex | Tree traversal | High (LLM summaries) | Medium (traverse) | Hierarchical summarization |
| KeywordTableIndex | Keyword matching | Medium (LLM extraction) | Low (keyword lookup) | Exact term matching |
| KnowledgeGraphIndex | Graph traversal | High (triple extraction) | Medium (graph query) | Relationship queries |

### 4. Query Engines

A Query Engine takes a natural language query and returns a response. It orchestrates retrieval + synthesis.

```python
# Basic query engine
query_engine = index.as_query_engine(
    similarity_top_k=5,          # Number of nodes to retrieve
    response_mode="compact",      # How to synthesize the response
    streaming=True                # Stream response tokens
)

response = query_engine.query("What is the company's AI strategy?")
print(response)                   # The synthesized answer
print(response.source_nodes)      # The retrieved source nodes
print(response.metadata)          # Response metadata
```

**Response modes:**
- `refine` — iterate through each node, refining the answer
- `compact` — stuff as many nodes as possible into one LLM call
- `tree_summarize` — bottom-up summarization tree
- `simple_summarize` — truncate to fit context, one LLM call
- `accumulate` — separate answer per node, then combine
- `compact_accumulate` — compact + accumulate

### 5. Chat Engines

Like Query Engines but with conversation memory. Maintains chat history.

```python
chat_engine = index.as_chat_engine(
    chat_mode="condense_plus_context",   # Condense follow-ups into standalone queries
    similarity_top_k=5
)

response = chat_engine.chat("What products does the company sell?")
print(response)

# Follow-up (uses chat history for context)
response = chat_engine.chat("Which one is the most popular?")
print(response)

# Reset conversation
chat_engine.reset()
```

**Chat modes:**
- `condense_question` — condense follow-up + chat history into standalone query
- `context` — retrieve context for every message
- `condense_plus_context` — condense + retrieve (best for most cases)
- `simple` — no retrieval, pass everything to LLM
- `react` — ReAct agent mode with tools
- `best` — auto-selects best mode

### 6. Retrievers

Retrievers find relevant nodes for a query WITHOUT synthesizing a response. Building block for custom pipelines.

```python
from llama_index.core.retrievers import VectorIndexRetriever

retriever = VectorIndexRetriever(index=index, similarity_top_k=10)
nodes = retriever.retrieve("What is our pricing model?")

for node in nodes:
    print(f"Score: {node.score:.4f}")
    print(f"Text: {node.text[:200]}")
    print(f"Source: {node.metadata.get('source', 'unknown')}")
    print("---")
```

**Retriever types:**
- `VectorIndexRetriever` — cosine similarity on embeddings
- `KeywordTableRetriever` — keyword matching
- `KnowledgeGraphRetriever` — graph traversal
- `RouterRetriever` — routes to different retrievers based on query
- `AutoMergingRetriever` — merges child nodes into parent
- `RecursiveRetriever` — retrieves from hierarchical index
- `BM25Retriever` — classic BM25 text search
- `QueryFusionRetriever` — generates multiple queries, fuses results

### 7. Response Synthesizers

Take retrieved nodes and a query → produce a final response.

```python
from llama_index.core.response_synthesizers import get_response_synthesizer

synthesizer = get_response_synthesizer(
    response_mode="tree_summarize",
    use_async=True
)

response = synthesizer.synthesize(
    query="What are the key findings?",
    nodes=retrieved_nodes
)
```

### 8. Embeddings

Models that convert text to numerical vectors. Used by VectorStoreIndex.

```python
from llama_index.core import Settings
from llama_index.embeddings.openai import OpenAIEmbedding
from llama_index.embeddings.huggingface import HuggingFaceEmbedding

# OpenAI embeddings (default)
Settings.embed_model = OpenAIEmbedding(model="text-embedding-3-small")

# Local embeddings (free, private)
Settings.embed_model = HuggingFaceEmbedding(model_name="BAAI/bge-small-en-v1.5")

# Google embeddings
from llama_index.embeddings.gemini import GeminiEmbedding
Settings.embed_model = GeminiEmbedding(model_name="models/text-embedding-004")
```

### 9. LLMs

The language model used for synthesis, summarization, and extraction.

```python
from llama_index.core import Settings
from llama_index.llms.openai import OpenAI
from llama_index.llms.anthropic import Anthropic

# OpenAI (default)
Settings.llm = OpenAI(model="gpt-4o", temperature=0.1)

# Anthropic Claude
Settings.llm = Anthropic(model="claude-sonnet-4-20250514", temperature=0.1)

# Local LLM via Ollama
from llama_index.llms.ollama import Ollama
Settings.llm = Ollama(model="llama3.1", request_timeout=120.0)

# Google Gemini
from llama_index.llms.gemini import Gemini
Settings.llm = Gemini(model="models/gemini-2.0-flash")
```

---

## Architecture Overview

### The RAG Pipeline (Simplified)

```
┌─────────────┐     ┌──────────────┐     ┌─────────────┐
│  Your Data   │────▶│  LlamaIndex  │────▶│  LLM (GPT)  │
│  (PDF, SQL)  │     │  Index/Store │     │  Synthesis   │
└─────────────┘     └──────────────┘     └─────────────┘
                          │                      │
                    ┌─────▼──────┐          ┌────▼─────┐
                    │ Retriever  │          │ Response │
                    │ (top-k)    │          │          │
                    └────────────┘          └──────────┘
```

### Detailed Architecture

```
Data Sources → Data Connectors → Documents → Node Parsers → Nodes
                                                              │
                                                    ┌─────────▼──────────┐
                                                    │    Index Building   │
                                                    │  (Embed + Store)    │
                                                    └─────────┬──────────┘
                                                              │
User Query → Query Engine → Retriever → Retrieved Nodes → Response Synthesizer → Response
                                │                              │
                          (vector search,                (LLM call with
                           keyword match,                 context + query)
                           graph traversal)
```

---

## Installation & Setup

### Basic Installation

```bash
# Core package
pip install llama-index

# This installs:
# - llama-index-core (core framework)
# - llama-index-llms-openai (OpenAI LLM)
# - llama-index-embeddings-openai (OpenAI embeddings)
# - llama-index-readers-file (file readers)
```

### Modular Installation (Recommended for Production)

```bash
# Core only (minimal)
pip install llama-index-core

# Add specific components
pip install llama-index-llms-openai          # OpenAI LLMs
pip install llama-index-llms-anthropic       # Claude
pip install llama-index-llms-ollama          # Local LLMs
pip install llama-index-embeddings-openai    # OpenAI embeddings
pip install llama-index-embeddings-huggingface  # Local embeddings

# Vector stores
pip install llama-index-vector-stores-chroma
pip install llama-index-vector-stores-pinecone
pip install llama-index-vector-stores-qdrant
pip install llama-index-vector-stores-weaviate
pip install llama-index-vector-stores-pgvector

# Data connectors
pip install llama-index-readers-file         # PDF, DOCX, etc.
pip install llama-index-readers-database     # SQL databases
pip install llama-index-readers-web          # Web scraping
pip install llama-index-readers-notion       # Notion
pip install llama-index-readers-slack        # Slack
pip install llama-index-readers-google       # Google Drive, Docs
```

### Environment Setup

```bash
# Set API keys
export OPENAI_API_KEY="sk-..."
export ANTHROPIC_API_KEY="sk-ant-..."

# Or use .env file
pip install python-dotenv
```

```python
# .env
OPENAI_API_KEY=sk-...

# In code
from dotenv import load_dotenv
load_dotenv()
```

### Global Settings

```python
from llama_index.core import Settings
from llama_index.llms.openai import OpenAI
from llama_index.embeddings.openai import OpenAIEmbedding

# Configure globally (applies to all indexes/queries)
Settings.llm = OpenAI(model="gpt-4o-mini", temperature=0.1)
Settings.embed_model = OpenAIEmbedding(model="text-embedding-3-small")
Settings.chunk_size = 1024
Settings.chunk_overlap = 200
Settings.num_output = 512
```

---

## Beginner: Your First RAG Pipeline

### Example 1: Simple Document Q&A

```python
from llama_index.core import VectorStoreIndex, SimpleDirectoryReader

# Step 1: Load documents from a directory
documents = SimpleDirectoryReader("./data").load_data()
print(f"Loaded {len(documents)} documents")

# Step 2: Build index (embeds all document chunks)
index = VectorStoreIndex.from_documents(documents)

# Step 3: Query
query_engine = index.as_query_engine()
response = query_engine.query("What are the main topics discussed?")
print(response)
```

That's it. 5 lines of code for a complete RAG pipeline.

### Example 2: PDF Q&A System

```python
from llama_index.core import VectorStoreIndex, SimpleDirectoryReader, Settings
from llama_index.llms.openai import OpenAI

# Configure
Settings.llm = OpenAI(model="gpt-4o-mini", temperature=0.1)

# Load PDFs
documents = SimpleDirectoryReader(
    input_dir="./pdfs",
    required_exts=[".pdf"],
    recursive=True
).load_data()

# Build searchable index
index = VectorStoreIndex.from_documents(documents, show_progress=True)

# Interactive Q&A
query_engine = index.as_query_engine(
    similarity_top_k=5,
    response_mode="compact"
)

while True:
    question = input("\nAsk a question (or 'quit'): ")
    if question.lower() == 'quit':
        break
    response = query_engine.query(question)
    print(f"\nAnswer: {response}")
    print(f"\nSources: {[n.metadata.get('file_name', '?') for n in response.source_nodes]}")
```

### Example 3: Chat Over Your Documents

```python
from llama_index.core import VectorStoreIndex, SimpleDirectoryReader

documents = SimpleDirectoryReader("./docs").load_data()
index = VectorStoreIndex.from_documents(documents)

# Chat engine maintains conversation history
chat_engine = index.as_chat_engine(
    chat_mode="condense_plus_context",
    verbose=True
)

response = chat_engine.chat("What is this document about?")
print(response)

response = chat_engine.chat("Can you give me more details about the first point?")
print(response)

response = chat_engine.chat("How does that compare to the conclusion?")
print(response)
```

### Example 4: Persisting Your Index

```python
from llama_index.core import VectorStoreIndex, SimpleDirectoryReader, StorageContext, load_index_from_storage

PERSIST_DIR = "./storage"

# Build and persist
documents = SimpleDirectoryReader("./data").load_data()
index = VectorStoreIndex.from_documents(documents)
index.storage_context.persist(persist_dir=PERSIST_DIR)
print("Index saved!")

# Load later (no re-embedding needed)
storage_context = StorageContext.from_defaults(persist_dir=PERSIST_DIR)
index = load_index_from_storage(storage_context)
print("Index loaded!")

query_engine = index.as_query_engine()
response = query_engine.query("What is the summary?")
```

### Example 5: Using a Local LLM (No API Keys!)

```python
from llama_index.core import VectorStoreIndex, SimpleDirectoryReader, Settings
from llama_index.llms.ollama import Ollama
from llama_index.embeddings.huggingface import HuggingFaceEmbedding

# 100% local — no data leaves your machine
Settings.llm = Ollama(model="llama3.1", request_timeout=120.0)
Settings.embed_model = HuggingFaceEmbedding(model_name="BAAI/bge-small-en-v1.5")

documents = SimpleDirectoryReader("./data").load_data()
index = VectorStoreIndex.from_documents(documents)
query_engine = index.as_query_engine()
response = query_engine.query("Summarize the key points")
print(response)
```

---

## Intermediate Patterns

### 1. Hybrid Search (Vector + BM25)

Combines semantic similarity (vector) with keyword matching (BM25). Best of both worlds.

```python
from llama_index.core import VectorStoreIndex, SimpleDirectoryReader
from llama_index.core.retrievers import QueryFusionRetriever
from llama_index.retrievers.bm25 import BM25Retriever

documents = SimpleDirectoryReader("./data").load_data()
index = VectorStoreIndex.from_documents(documents)
nodes = index.docstore.docs.values()

# Vector retriever (semantic)
vector_retriever = index.as_retriever(similarity_top_k=5)

# BM25 retriever (keyword)
bm25_retriever = BM25Retriever.from_defaults(nodes=list(nodes), similarity_top_k=5)

# Fusion retriever (combines both with reciprocal rank fusion)
hybrid_retriever = QueryFusionRetriever(
    retrievers=[vector_retriever, bm25_retriever],
    retriever_weights=[0.6, 0.4],
    similarity_top_k=5,
    num_queries=1,   # dont generate sub-queries
    mode="reciprocal_rerank"
)

from llama_index.core.query_engine import RetrieverQueryEngine
query_engine = RetrieverQueryEngine.from_args(retriever=hybrid_retriever)
response = query_engine.query("What is the refund policy for enterprise customers?")
```

### 2. Re-Ranking Retrieved Results

Use a cross-encoder to re-rank retrieved nodes for better precision.

```python
from llama_index.core import VectorStoreIndex, SimpleDirectoryReader
from llama_index.core.postprocessor import SentenceTransformerRerank

documents = SimpleDirectoryReader("./data").load_data()
index = VectorStoreIndex.from_documents(documents)

# Re-ranker: retrieves 10, re-ranks, keeps top 3
reranker = SentenceTransformerRerank(
    model="cross-encoder/ms-marco-MiniLM-L-2-v2",
    top_n=3
)

query_engine = index.as_query_engine(
    similarity_top_k=10,             # Retrieve more candidates
    node_postprocessors=[reranker]    # Re-rank them
)

response = query_engine.query("What are the security best practices?")
```

### 3. Sub-Question Query Engine

Breaks complex questions into sub-questions, each routed to the right index.

```python
from llama_index.core import VectorStoreIndex, SimpleDirectoryReader
from llama_index.core.tools import QueryEngineTool, ToolMetadata
from llama_index.core.query_engine import SubQuestionQueryEngine

# Create separate indexes for different document types
financial_docs = SimpleDirectoryReader("./data/financial").load_data()
technical_docs = SimpleDirectoryReader("./data/technical").load_data()

financial_index = VectorStoreIndex.from_documents(financial_docs)
technical_index = VectorStoreIndex.from_documents(technical_docs)

# Wrap as tools with descriptions
query_engine_tools = [
    QueryEngineTool(
        query_engine=financial_index.as_query_engine(),
        metadata=ToolMetadata(
            name="financial_reports",
            description="Contains quarterly financial reports, revenue data, and forecasts"
        )
    ),
    QueryEngineTool(
        query_engine=technical_index.as_query_engine(),
        metadata=ToolMetadata(
            name="technical_docs",
            description="Contains API documentation, architecture guides, and technical specs"
        )
    ),
]

# Sub-question engine decomposes complex queries
sub_question_engine = SubQuestionQueryEngine.from_defaults(
    query_engine_tools=query_engine_tools
)

# This will generate sub-questions for each relevant index
response = sub_question_engine.query(
    "How does the company's technical architecture support its revenue growth targets?"
)
```

### 4. Multi-Document Agent

An agent that can reason across multiple documents with tool use.

```python
from llama_index.core import VectorStoreIndex, SimpleDirectoryReader, SummaryIndex
from llama_index.core.tools import QueryEngineTool, ToolMetadata
from llama_index.core.agent import ReActAgent

# Load docs per company
apple_docs = SimpleDirectoryReader("./data/apple").load_data()
google_docs = SimpleDirectoryReader("./data/google").load_data()

# Create both vector and summary indexes for each
apple_vector = VectorStoreIndex.from_documents(apple_docs)
apple_summary = SummaryIndex.from_documents(apple_docs)

google_vector = VectorStoreIndex.from_documents(google_docs)
google_summary = SummaryIndex.from_documents(google_docs)

# Tools for the agent
tools = [
    QueryEngineTool(
        query_engine=apple_vector.as_query_engine(),
        metadata=ToolMetadata(name="apple_search", description="Search Apple 10-K filing for specific information")
    ),
    QueryEngineTool(
        query_engine=apple_summary.as_query_engine(response_mode="tree_summarize"),
        metadata=ToolMetadata(name="apple_summary", description="Get a summary of Apple's 10-K filing")
    ),
    QueryEngineTool(
        query_engine=google_vector.as_query_engine(),
        metadata=ToolMetadata(name="google_search", description="Search Google 10-K filing for specific information")
    ),
    QueryEngineTool(
        query_engine=google_summary.as_query_engine(response_mode="tree_summarize"),
        metadata=ToolMetadata(name="google_summary", description="Get a summary of Google's 10-K filing")
    ),
]

# ReAct agent reasons about which tools to use
agent = ReActAgent.from_tools(tools, verbose=True)
response = agent.chat("Compare Apple and Google's revenue growth and AI strategies")
```

### 5. Metadata Filtering

Filter retrieved nodes by metadata before semantic search.

```python
from llama_index.core import VectorStoreIndex, Document
from llama_index.core.vector_stores import MetadataFilters, MetadataFilter, FilterOperator

# Documents with rich metadata
documents = [
    Document(text="Q1 2024 revenue was $50B", metadata={"quarter": "Q1", "year": 2024, "type": "financial"}),
    Document(text="Q2 2024 revenue was $55B", metadata={"quarter": "Q2", "year": 2024, "type": "financial"}),
    Document(text="New AI features launched", metadata={"quarter": "Q1", "year": 2024, "type": "product"}),
]

index = VectorStoreIndex.from_documents(documents)

# Query with metadata filter
filters = MetadataFilters(
    filters=[
        MetadataFilter(key="year", value=2024, operator=FilterOperator.EQ),
        MetadataFilter(key="type", value="financial", operator=FilterOperator.EQ),
    ]
)

query_engine = index.as_query_engine(
    similarity_top_k=5,
    filters=filters
)

response = query_engine.query("What was the revenue?")
# Only searches within 2024 financial documents
```

### 6. Streaming Responses

```python
from llama_index.core import VectorStoreIndex, SimpleDirectoryReader

documents = SimpleDirectoryReader("./data").load_data()
index = VectorStoreIndex.from_documents(documents)

query_engine = index.as_query_engine(streaming=True)
streaming_response = query_engine.query("Explain the main concepts")

# Stream tokens as they arrive
for text in streaming_response.response_gen:
    print(text, end="", flush=True)
```

### 7. Custom Prompts

```python
from llama_index.core import VectorStoreIndex, SimpleDirectoryReader, PromptTemplate

documents = SimpleDirectoryReader("./data").load_data()
index = VectorStoreIndex.from_documents(documents)

# Custom QA prompt
qa_prompt_tmpl = PromptTemplate(
    "Context information is below.\n"
    "---------------------\n"
    "{context_str}\n"
    "---------------------\n"
    "You are a helpful financial analyst. Given the context above, "
    "answer the following question in a professional tone with specific numbers.\n"
    "If the answer cannot be determined from the context, say 'Insufficient data'.\n"
    "Question: {query_str}\n"
    "Answer: "
)

query_engine = index.as_query_engine()
query_engine.update_prompts({"response_synthesizer:text_qa_template": qa_prompt_tmpl})

response = query_engine.query("What was the year-over-year revenue growth?")
```

---

## Advanced Architectures

### 1. Agentic RAG

The LLM decides what to retrieve, when, and how — not just "retrieve then answer."

```python
from llama_index.core import VectorStoreIndex, SimpleDirectoryReader, Settings
from llama_index.core.tools import QueryEngineTool, ToolMetadata, FunctionTool
from llama_index.core.agent import ReActAgent
from llama_index.llms.openai import OpenAI

Settings.llm = OpenAI(model="gpt-4o", temperature=0)

# RAG tool
documents = SimpleDirectoryReader("./data").load_data()
index = VectorStoreIndex.from_documents(documents)

# Custom Python tools
def calculate_growth(current: float, previous: float) -> str:
    """Calculate percentage growth between two values."""
    growth = ((current - previous) / previous) * 100
    return f"Growth: {growth:.1f}%"

def get_current_date() -> str:
    """Get today's date."""
    from datetime import date
    return str(date.today())

tools = [
    QueryEngineTool(
        query_engine=index.as_query_engine(),
        metadata=ToolMetadata(name="document_search", description="Search internal documents for information")
    ),
    FunctionTool.from_defaults(fn=calculate_growth),
    FunctionTool.from_defaults(fn=get_current_date),
]

agent = ReActAgent.from_tools(
    tools,
    verbose=True,
    max_iterations=10
)

# Agent decides: search docs → extract numbers → calculate growth
response = agent.chat("What was the revenue growth from last quarter to this quarter?")
```

### 2. Router Query Engine

Routes queries to the most appropriate index/engine based on the query content.

```python
from llama_index.core import VectorStoreIndex, SummaryIndex, SimpleDirectoryReader
from llama_index.core.tools import QueryEngineTool, ToolMetadata
from llama_index.core.query_engine import RouterQueryEngine
from llama_index.core.selectors import LLMSingleSelector

documents = SimpleDirectoryReader("./data").load_data()

# Two different indexes for different query types
vector_index = VectorStoreIndex.from_documents(documents)
summary_index = SummaryIndex.from_documents(documents)

# Router decides which engine to use
router_engine = RouterQueryEngine(
    selector=LLMSingleSelector.from_defaults(),
    query_engine_tools=[
        QueryEngineTool(
            query_engine=vector_index.as_query_engine(),
            metadata=ToolMetadata(
                name="vector_search",
                description="Useful for specific factual questions about the documents"
            )
        ),
        QueryEngineTool(
            query_engine=summary_index.as_query_engine(response_mode="tree_summarize"),
            metadata=ToolMetadata(
                name="summarization",
                description="Useful for summarizing the entire document or getting broad themes"
            )
        ),
    ]
)

# Specific question → routes to vector search
response = router_engine.query("What was Q3 revenue?")

# Broad question → routes to summarization
response = router_engine.query("Give me an overview of the annual report")
```

### 3. Knowledge Graph RAG

Build and query a knowledge graph for relationship-heavy data.

```python
from llama_index.core import KnowledgeGraphIndex, SimpleDirectoryReader, Settings
from llama_index.core.graph_stores import SimpleGraphStore
from llama_index.core import StorageContext

# Setup graph store
graph_store = SimpleGraphStore()
storage_context = StorageContext.from_defaults(graph_store=graph_store)

documents = SimpleDirectoryReader("./data").load_data()

# Build knowledge graph (extracts entity-relationship triples)
kg_index = KnowledgeGraphIndex.from_documents(
    documents,
    storage_context=storage_context,
    max_triplets_per_chunk=10,
    include_embeddings=True,
    show_progress=True
)

# Query with graph retrieval
query_engine = kg_index.as_query_engine(
    include_text=True,
    response_mode="tree_summarize",
    retriever_mode="keyword",  # or "embedding" or "hybrid"
)

response = query_engine.query("What relationships exist between the CEO and the board members?")

# Visualize the graph
from pyvis.network import Network
g = kg_index.get_networkx_graph()
net = Network(notebook=True, directed=True)
net.from_nx(g)
net.show("knowledge_graph.html")
```

### 4. Custom Retriever Pipeline

Build a fully custom retrieval pipeline.

```python
from llama_index.core import VectorStoreIndex, SimpleDirectoryReader
from llama_index.core.retrievers import BaseRetriever
from llama_index.core.schema import NodeWithScore, QueryBundle
from typing import List

class HybridCustomRetriever(BaseRetriever):
    """Custom retriever that combines vector + keyword with custom logic."""

    def __init__(self, vector_retriever, keyword_retriever, alpha=0.5):
        self.vector_retriever = vector_retriever
        self.keyword_retriever = keyword_retriever
        self.alpha = alpha
        super().__init__()

    def _retrieve(self, query_bundle: QueryBundle) -> List[NodeWithScore]:
        # Get results from both retrievers
        vector_nodes = self.vector_retriever.retrieve(query_bundle)
        keyword_nodes = self.keyword_retriever.retrieve(query_bundle)

        # Combine and re-score
        node_dict = {}
        for node in vector_nodes:
            node_dict[node.node_id] = {
                "node": node,
                "vector_score": node.score or 0.0,
                "keyword_score": 0.0
            }

        for node in keyword_nodes:
            if node.node_id in node_dict:
                node_dict[node.node_id]["keyword_score"] = node.score or 0.0
            else:
                node_dict[node.node_id] = {
                    "node": node,
                    "vector_score": 0.0,
                    "keyword_score": node.score or 0.0
                }

        # Weighted combination
        results = []
        for info in node_dict.values():
            combined_score = (
                self.alpha * info["vector_score"] +
                (1 - self.alpha) * info["keyword_score"]
            )
            node = info["node"]
            node.score = combined_score
            results.append(node)

        # Sort by combined score
        results.sort(key=lambda x: x.score, reverse=True)
        return results[:5]

# Usage
documents = SimpleDirectoryReader("./data").load_data()
index = VectorStoreIndex.from_documents(documents)

vector_retriever = index.as_retriever(similarity_top_k=10)
# Could also use BM25 or keyword retriever here
custom_retriever = HybridCustomRetriever(vector_retriever, vector_retriever, alpha=0.7)
```

### 5. Hierarchical Node Parsing (Auto-Merging Retriever)

Retrieve small chunks but return larger parent context when multiple children match.

```python
from llama_index.core import VectorStoreIndex, SimpleDirectoryReader, StorageContext
from llama_index.core.node_parser import HierarchicalNodeParser, get_leaf_nodes
from llama_index.core.retrievers import AutoMergingRetriever
from llama_index.core.query_engine import RetrieverQueryEngine

documents = SimpleDirectoryReader("./data").load_data()

# Create hierarchical nodes (3 levels: 2048 → 512 → 128 tokens)
node_parser = HierarchicalNodeParser.from_defaults(chunk_sizes=[2048, 512, 128])
nodes = node_parser.get_nodes_from_documents(documents)
leaf_nodes = get_leaf_nodes(nodes)

# Build index from leaf nodes only
storage_context = StorageContext.from_defaults()
storage_context.docstore.add_documents(nodes)  # Store ALL levels

index = VectorStoreIndex(leaf_nodes, storage_context=storage_context)

# Auto-merging retriever: if enough children match, return parent
retriever = AutoMergingRetriever(
    index.as_retriever(similarity_top_k=12),
    storage_context=index.storage_context,
    simple_ratio_thresh=0.3  # merge if >30% of children match
)

query_engine = RetrieverQueryEngine.from_args(retriever=retriever)
response = query_engine.query("Explain the architecture in detail")
```

### 6. SQL + Natural Language (Text-to-SQL)

Query structured databases with natural language.

```python
from llama_index.core import SQLDatabase
from llama_index.core.query_engine import NLSQLTableQueryEngine
from sqlalchemy import create_engine

# Connect to database
engine = create_engine("sqlite:///./data/company.db")
sql_database = SQLDatabase(engine, include_tables=["employees", "departments", "sales"])

# Natural language to SQL
query_engine = NLSQLTableQueryEngine(
    sql_database=sql_database,
    tables=["employees", "departments", "sales"],
)

response = query_engine.query("How many employees are in the engineering department?")
print(response)
# Generated SQL: SELECT COUNT(*) FROM employees WHERE department = 'Engineering'
# Answer: There are 42 employees in the engineering department.

response = query_engine.query("What were the total sales by department last quarter?")
print(response)
```

### 7. Evaluation & Observability

Measure RAG quality systematically.

```python
from llama_index.core.evaluation import (
    FaithfulnessEvaluator,
    RelevancyEvaluator,
    CorrectnessEvaluator,
    BatchEvalRunner
)
from llama_index.core import VectorStoreIndex, SimpleDirectoryReader

documents = SimpleDirectoryReader("./data").load_data()
index = VectorStoreIndex.from_documents(documents)
query_engine = index.as_query_engine()

# Evaluators
faithfulness_evaluator = FaithfulnessEvaluator()  # Is the response grounded in context?
relevancy_evaluator = RelevancyEvaluator()          # Is the response relevant to the query?

# Evaluate a single query
response = query_engine.query("What is the company's revenue?")

# Faithfulness: is the answer supported by retrieved sources?
faith_result = faithfulness_evaluator.evaluate_response(response=response)
print(f"Faithful: {faith_result.passing} (score: {faith_result.score})")

# Relevancy: is the retrieved context relevant to the query?
rel_result = relevancy_evaluator.evaluate_response(
    query="What is the company's revenue?", response=response
)
print(f"Relevant: {rel_result.passing} (score: {rel_result.score})")

# Batch evaluation
eval_questions = [
    "What is the revenue?",
    "Who is the CEO?",
    "What products does the company sell?",
]

runner = BatchEvalRunner(
    evaluators={"faithfulness": faithfulness_evaluator, "relevancy": relevancy_evaluator},
    workers=4
)

eval_results = await runner.aevaluate_queries(
    query_engine, queries=eval_questions
)
```

---

## Data Connectors (LlamaHub)

LlamaHub provides 150+ data connectors. Here are the most popular:

### File-Based

```python
from llama_index.core import SimpleDirectoryReader

# Supports: .pdf, .docx, .pptx, .xlsx, .csv, .txt, .md, .html, .epub, .ipynb
documents = SimpleDirectoryReader(
    input_dir="./data",
    required_exts=[".pdf", ".docx"],
    recursive=True,
    filename_as_id=True
).load_data()
```

### Databases

```python
# SQL Databases
from llama_index.readers.database import DatabaseReader
reader = DatabaseReader(uri="postgresql://user:pass@localhost:5432/mydb")
documents = reader.load_data(query="SELECT * FROM articles")

# MongoDB
from llama_index.readers.mongodb import SimpleMongoReader
reader = SimpleMongoReader(uri="mongodb://localhost:27017")
documents = reader.load_data(db_name="mydb", collection_name="articles")
```

### Cloud & SaaS

```python
# Google Drive
from llama_index.readers.google import GoogleDriveReader
reader = GoogleDriveReader()
documents = reader.load_data(folder_id="your_folder_id")

# Notion
from llama_index.readers.notion import NotionPageReader
reader = NotionPageReader(integration_token="secret_xxx")
documents = reader.load_data(page_ids=["page_id_1", "page_id_2"])

# Slack
from llama_index.readers.slack import SlackReader
reader = SlackReader(slack_token="xoxb-xxx")
documents = reader.load_data(channel_ids=["C01234567"])

# Confluence
from llama_index.readers.confluence import ConfluenceReader
reader = ConfluenceReader(base_url="https://company.atlassian.net/wiki")
documents = reader.load_data(space_key="ENG")

# GitHub
from llama_index.readers.github import GithubRepositoryReader
reader = GithubRepositoryReader(owner="org", repo="repo", github_token="ghp_xxx")
documents = reader.load_data(branch="main")
```

### Web

```python
# Web pages
from llama_index.readers.web import SimpleWebPageReader
reader = SimpleWebPageReader()
documents = reader.load_data(urls=["https://example.com/page1", "https://example.com/page2"])

# Entire websites (crawl)
from llama_index.readers.web import WholeSiteReader
reader = WholeSiteReader(prefix="https://docs.example.com", max_depth=3)
documents = reader.load_data(base_url="https://docs.example.com")
```

---

## Production Deployment

### With ChromaDB (Persistent Vector Store)

```python
import chromadb
from llama_index.core import VectorStoreIndex, SimpleDirectoryReader, StorageContext
from llama_index.vector_stores.chroma import ChromaVectorStore

# Persistent ChromaDB
chroma_client = chromadb.PersistentClient(path="./chroma_db")
chroma_collection = chroma_client.get_or_create_collection("my_collection")
vector_store = ChromaVectorStore(chroma_collection=chroma_collection)

# First time: build index
storage_context = StorageContext.from_defaults(vector_store=vector_store)
documents = SimpleDirectoryReader("./data").load_data()
index = VectorStoreIndex.from_documents(documents, storage_context=storage_context)

# Later: load existing index (no re-embedding!)
vector_store = ChromaVectorStore(chroma_collection=chroma_collection)
index = VectorStoreIndex.from_vector_store(vector_store)
```

### With Pinecone (Cloud Vector Store)

```python
from pinecone import Pinecone, ServerlessSpec
from llama_index.vector_stores.pinecone import PineconeVectorStore
from llama_index.core import VectorStoreIndex, StorageContext

# Initialize Pinecone
pc = Pinecone(api_key="your-api-key")
pc.create_index(
    name="my-index",
    dimension=1536,  # text-embedding-3-small dimension
    metric="cosine",
    spec=ServerlessSpec(cloud="aws", region="us-east-1")
)

pinecone_index = pc.Index("my-index")
vector_store = PineconeVectorStore(pinecone_index=pinecone_index)
storage_context = StorageContext.from_defaults(vector_store=vector_store)

# Build
index = VectorStoreIndex.from_documents(documents, storage_context=storage_context)

# Query
query_engine = index.as_query_engine()
```

### FastAPI Integration

```python
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from llama_index.core import VectorStoreIndex, StorageContext, load_index_from_storage

app = FastAPI()

# Load index at startup
storage_context = StorageContext.from_defaults(persist_dir="./storage")
index = load_index_from_storage(storage_context)
query_engine = index.as_query_engine(similarity_top_k=5, streaming=False)

class QueryRequest(BaseModel):
    question: str
    top_k: int = 5

class QueryResponse(BaseModel):
    answer: str
    sources: list[dict]

@app.post("/query", response_model=QueryResponse)
async def query_documents(request: QueryRequest):
    try:
        response = query_engine.query(request.question)
        sources = [
            {
                "text": node.text[:200],
                "score": node.score,
                "file": node.metadata.get("file_name", "unknown")
            }
            for node in response.source_nodes
        ]
        return QueryResponse(answer=str(response), sources=sources)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/health")
async def health():
    return {"status": "ok", "index_loaded": index is not None}
```

### Incremental Indexing (Add/Update/Delete Documents)

```python
from llama_index.core import VectorStoreIndex, SimpleDirectoryReader
from llama_index.core.ingestion import IngestionPipeline
from llama_index.core.node_parser import SentenceSplitter
from llama_index.core.extractors import TitleExtractor, SummaryExtractor

# Pipeline for incremental indexing
pipeline = IngestionPipeline(
    transformations=[
        SentenceSplitter(chunk_size=1024, chunk_overlap=200),
        TitleExtractor(),
        SummaryExtractor(summaries=["self"]),
    ]
)

# Initial load
documents = SimpleDirectoryReader("./data").load_data()
nodes = pipeline.run(documents=documents)
index = VectorStoreIndex(nodes)

# Add new documents later
new_docs = SimpleDirectoryReader("./data/new").load_data()
new_nodes = pipeline.run(documents=new_docs)
index.insert_nodes(new_nodes)

# Delete a document
index.delete_ref_doc("doc_id_to_delete", delete_from_docstore=True)

# Refresh (add new, update changed, keep unchanged)
refreshed_docs = SimpleDirectoryReader("./data").load_data()
index.refresh_ref_docs(refreshed_docs)
```

---

## Best Practices

### 1. Chunking Strategy

```
WRONG: One-size-fits-all chunk_size=1024
RIGHT: Tune chunk_size based on your data type

- Legal documents: 2048+ (long, structured sections)
- Chat logs: 256-512 (short, conversational)
- Technical docs: 1024 (balanced)
- Code: Use CodeSplitter (respects function boundaries)
```

### 2. Embedding Model Selection

```
Cost-sensitive:    BAAI/bge-small-en-v1.5 (local, free)
Balanced:          text-embedding-3-small (OpenAI, cheap, good)
Best quality:      text-embedding-3-large (OpenAI, expensive, best)
Privacy-required:  BAAI/bge-large-en-v1.5 or nomic-embed-text (local)
Multilingual:      multilingual-e5-large (local, 100+ languages)
```

### 3. Retrieval Configuration

```python
# Don't just use defaults — tune these:
query_engine = index.as_query_engine(
    similarity_top_k=5,          # Start with 5, increase if answers lack context
    response_mode="compact",     # Best balance of speed and quality
    node_postprocessors=[        # Add re-ranking for precision
        SentenceTransformerRerank(top_n=3)
    ]
)
```

### 4. Metadata Enrichment

```python
# Always add metadata — it dramatically improves retrieval
documents = SimpleDirectoryReader("./data").load_data()
for doc in documents:
    doc.metadata["source"] = "internal_wiki"
    doc.metadata["department"] = "engineering"
    doc.metadata["last_updated"] = "2024-01-15"
    doc.metadata["confidentiality"] = "internal"
```

### 5. Evaluation is Non-Negotiable

```
Never ship a RAG pipeline without measuring:
1. Faithfulness — is the answer grounded in context?
2. Relevancy   — are the right documents retrieved?
3. Correctness — is the answer actually correct?

Build a golden test set (50+ question-answer pairs) and evaluate every change.
```

---

## Common Pitfalls

### 1. "My RAG gives wrong answers"

**Root cause:** Bad chunking. Relevant information is split across chunks.

```python
# FIX: Increase chunk_overlap
parser = SentenceSplitter(chunk_size=1024, chunk_overlap=200)  # was 20

# FIX: Use semantic chunking
from llama_index.core.node_parser import SemanticSplitterNodeParser
parser = SemanticSplitterNodeParser(
    embed_model=embed_model,
    breakpoint_percentile_threshold=95
)
```

### 2. "Retrieval misses relevant documents"

**Root cause:** Semantic search alone isn't enough.

```python
# FIX: Use hybrid search (vector + BM25)
# FIX: Increase similarity_top_k
# FIX: Add re-ranking
# FIX: Use metadata filtering to narrow search space
```

### 3. "Token limit exceeded"

**Root cause:** Too many chunks stuffed into the prompt.

```python
# FIX: Use tree_summarize response mode (summarizes incrementally)
query_engine = index.as_query_engine(response_mode="tree_summarize")

# FIX: Reduce similarity_top_k
query_engine = index.as_query_engine(similarity_top_k=3)

# FIX: Use a model with larger context
Settings.llm = OpenAI(model="gpt-4o")  # 128K context
```

### 4. "Index building is too slow"

```python
# FIX: Use batch embedding
Settings.embed_batch_size = 100  # default is 10

# FIX: Use async embedding
index = VectorStoreIndex.from_documents(documents, use_async=True, show_progress=True)

# FIX: Use local embeddings for large datasets
Settings.embed_model = HuggingFaceEmbedding(model_name="BAAI/bge-small-en-v1.5")
```

### 5. "Response is not in the right format"

```python
# FIX: Use output parsers
from llama_index.core.output_parsers import PydanticOutputParser
from pydantic import BaseModel

class AnswerFormat(BaseModel):
    answer: str
    confidence: float
    sources: list[str]

output_parser = PydanticOutputParser(output_cls=AnswerFormat)
# Use in prompt template
```

### 6. "RAG works locally but fails in production"

```
Checklist:
□ API keys set in environment?
□ Vector store persistent (not in-memory)?
□ Enough memory for embeddings model?
□ Rate limits handled (retry with backoff)?
□ Timeouts configured for LLM calls?
□ Error handling for missing documents?
□ Logging/observability set up?
```

---

## Real-World Use Cases

### 1. Enterprise Knowledge Base

```
Input: Company wiki, Confluence, Slack, Google Drive (10K+ documents)
Pipeline: Multi-source ingestion → Hybrid index → Chat engine
Value: Employees get instant answers instead of searching 5 different tools
Stack: LlamaIndex + ChromaDB + GPT-4o-mini + FastAPI
```

### 2. Legal Document Analysis

```
Input: Contracts, legal briefs, regulatory filings (PDFs)
Pipeline: PDF loader → HierarchicalNodeParser → VectorStore + MetadataFilter
Value: Lawyers find relevant clauses in seconds vs hours
Stack: LlamaIndex + Pinecone + Claude + Custom prompts
```

### 3. Customer Support Bot

```
Input: Help docs, FAQ, ticket history, product docs
Pipeline: Multi-index (FAQ=keyword, docs=vector) → Router → Chat engine
Value: 60% ticket deflection, instant 24/7 support
Stack: LlamaIndex + Qdrant + GPT-4o-mini + Slack integration
```

### 4. Financial Research Assistant

```
Input: 10-K filings, earnings calls, market data, news
Pipeline: Multi-document agent with sub-question decomposition
Value: Analysts get cross-document insights in seconds
Stack: LlamaIndex + Weaviate + GPT-4o + Custom evaluation
```

### 5. Code Documentation Q&A

```
Input: GitHub repos, API docs, README files, docstrings
Pipeline: CodeSplitter → VectorIndex → Query engine with code-aware prompts
Value: Developers onboard 3x faster
Stack: LlamaIndex + ChromaDB + Claude + GitHub reader
```

### 6. Medical/Clinical Research

```
Input: Research papers, clinical guidelines, drug databases
Pipeline: Metadata-filtered retrieval → Re-ranking → Faithfulness evaluation
Value: Researchers find relevant studies 10x faster
Stack: LlamaIndex + PGVector + GPT-4o + Strict evaluation
```

---

## Performance Optimization

### Embedding Optimization

| Technique | Impact | Implementation |
|-----------|--------|----------------|
| Batch embedding | 5-10x faster indexing | `Settings.embed_batch_size = 100` |
| Local embeddings | No API costs, no latency | `HuggingFaceEmbedding("BAAI/bge-small-en-v1.5")` |
| Dimensionality reduction | 30% less storage | `text-embedding-3-small` with `dimensions=512` |
| Async embedding | 3-5x faster | `use_async=True` in index construction |

### Retrieval Optimization

| Technique | Impact | When to Use |
|-----------|--------|-------------|
| Re-ranking | +15-25% precision | Always, unless latency-critical |
| Hybrid search | +10-20% recall | When keyword terms are important |
| Metadata filtering | 2-5x faster search | When data has clear categories |
| Auto-merging retriever | Better context | Long documents with hierarchical structure |

### LLM Optimization

| Technique | Impact | Implementation |
|-----------|--------|----------------|
| Streaming | Better UX | `streaming=True` |
| Smaller model for routing | 50% cost reduction | GPT-4o-mini for router, GPT-4o for synthesis |
| Caching | Eliminate duplicate calls | `llama_index.core.global_handler` |
| Response mode tuning | Balance cost/quality | `compact` for most, `tree_summarize` for large context |

### Memory & Storage

```python
# Use persistent vector store in production (not in-memory)
# ChromaDB for simple deployments
# Pinecone/Qdrant/Weaviate for scale

# Cache embeddings to avoid re-computation
from llama_index.core.ingestion import IngestionCache, IngestionPipeline
from llama_index.core.storage.kvstore import SimpleKVStore

cache = IngestionCache(cache=SimpleKVStore())
pipeline = IngestionPipeline(
    transformations=[...],
    cache=cache
)
```

---

## Ecosystem & Community

### Key Resources

| Resource | URL | Purpose |
|----------|-----|---------|
| Official Docs | docs.llamaindex.ai | Comprehensive documentation |
| LlamaHub | llamahub.ai | 150+ data connectors |
| GitHub | github.com/run-llama/llama_index | Source code, issues |
| Discord | discord.gg/llamaindex | Community support |
| Blog | blog.llamaindex.ai | Tutorials, announcements |

### Version History

| Version | Key Changes |
|---------|-------------|
| 0.10.x+ | Modular architecture (separate packages) |
| 0.9.x | Ingestion pipeline, evaluation framework |
| 0.8.x | Agent framework, tool abstraction |
| 0.7.x | Response synthesizers, chat engine |
| 0.6.x | Knowledge graph index |

### LlamaIndex vs Other Frameworks

| Framework | Focus | Use With LlamaIndex? |
|-----------|-------|---------------------|
| LangChain | LLM orchestration, chains, agents | Yes — LlamaIndex for RAG, LangChain for agents |
| Haystack | End-to-end NLP pipelines | Competing — choose one |
| Semantic Kernel | Microsoft's AI orchestration | Complementary for .NET shops |
| ChromaDB/Pinecone/Qdrant | Vector storage only | Yes — use as LlamaIndex's vector store backend |
| Unstructured.io | Document parsing | Yes — use as LlamaIndex's document loader |

---

## Summary: When to Use LlamaIndex

```
✅ USE LlamaIndex when:
   - Building RAG over your private data
   - Need multiple index types (vector, keyword, graph)
   - Want production-ready retrieval with minimal code
   - Working with 150+ data sources
   - Need evaluation/observability for RAG

❌ DON'T USE LlamaIndex when:
   - Building general AI agents (use LangChain)
   - Simple prompt chaining (use LangChain or raw API)
   - No retrieval needed (just use the LLM directly)
   - Need real-time streaming data (use custom pipeline)
```

### The 5-Minute Decision

```
"I need to build Q&A over my documents" → LlamaIndex ✓
"I need a chatbot that uses tools"      → LangChain ✓
"I need both"                           → LlamaIndex (RAG) + LangChain (agent)
```

---

*LlamaIndex is the data framework that makes RAG practical. Start simple (5 lines), scale to production (custom retrievers, evaluation, vector stores). The framework handles the complexity so you can focus on your data.*
