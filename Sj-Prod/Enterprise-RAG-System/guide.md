# POC-02: Enterprise RAG System -- Comprehensive Guide

A baby-step, beginner-friendly walkthrough of the Enterprise RAG (Retrieval-Augmented
Generation) system. This guide explains every component, every design decision, and the
full data flow from raw documents to generated answers.

---

## Table of Contents

1.  [What Is This Project?](#1-what-is-this-project)
2.  [What Is RAG and Why Does It Matter?](#2-what-is-rag-and-why-does-it-matter)
3.  [Project Structure](#3-project-structure)
4.  [Prerequisites](#4-prerequisites)
5.  [Step 1 -- Document Loading and Chunking](#5-step-1----document-loading-and-chunking)
6.  [Step 2 -- Embeddings and the Vector Store](#6-step-2----embeddings-and-the-vector-store)
7.  [Step 3 -- The RAG Pipeline (Retrieve + Generate)](#7-step-3----the-rag-pipeline-retrieve--generate)
8.  [Step 4 -- The FastAPI Server](#8-step-4----the-fastapi-server)
9.  [Step 5 -- The Streamlit Dashboard](#9-step-5----the-streamlit-dashboard)
10. [Step 6 -- The Entry Point (main.py)](#10-step-6----the-entry-point-mainpy)
11. [End-to-End Data Flow](#11-end-to-end-data-flow)
12. [Running the Project Locally](#12-running-the-project-locally)
13. [Running with Docker](#13-running-with-docker)
14. [Testing the API with curl](#14-testing-the-api-with-curl)
15. [Key Concepts Explained in Depth](#15-key-concepts-explained-in-depth)
16. [Configuration Reference](#16-configuration-reference)
17. [Troubleshooting](#17-troubleshooting)
18. [What to Try Next](#18-what-to-try-next)

---

## 1. What Is This Project?

This is a fully working Enterprise RAG System. You feed it documents (Markdown, text,
or PDF files), and it lets you ask natural-language questions about those documents. The
system retrieves the most relevant passages from your documents, then uses a large
language model (LLM) to generate an answer grounded in those passages.

The key features are:

- **No API key required to start.** The system ships with a free, local embedding model
  and an extractive fallback mode that works without OpenAI or Anthropic keys.
- **Five sample documents** are included so you can try it immediately.
- **Full-stack architecture**: a FastAPI backend, a Streamlit frontend, and a ChromaDB
  vector database -- all launched with a single command.
- **Source citations**: every answer tells you which document chunks it came from and
  how similar they were to your question.

Think of it as building your own mini version of ChatGPT that only knows about
the documents you give it.

---

## 2. What Is RAG and Why Does It Matter?

### The Problem

Large language models (like GPT-4 or Claude) are trained on massive public datasets.
They know a lot, but they do not know about YOUR documents -- your company wiki, your
internal runbooks, your private research papers. If you ask an LLM about something it
was not trained on, it will either say it does not know or, worse, make something up
(this is called "hallucination").

### The Solution: Retrieval-Augmented Generation

RAG solves this by adding a retrieval step before generation:

```
Traditional LLM:
    Question --> LLM --> Answer (may hallucinate)

RAG:
    Question --> Search your documents --> Found relevant passages
             --> Stuff passages into the prompt --> LLM --> Answer (grounded in YOUR data)
```

The name breaks down as follows:

- **Retrieval**: search a knowledge base for passages related to the question.
- **Augmented**: add those passages to the LLM's prompt as context.
- **Generation**: the LLM generates an answer using that context.

### Why RAG Matters for Enterprises

1. **Privacy**: your documents never leave your infrastructure. The LLM only sees the
   chunks you retrieve, not your entire corpus.
2. **Accuracy**: answers are grounded in real documents, not the model's training data.
3. **Traceability**: every answer comes with source citations so you can verify it.
4. **Freshness**: when your documents change, re-index them and the answers update
   immediately -- no model retraining needed.

---

## 3. Project Structure

```
POC-02-Enterprise-RAG-System/
|
|-- main.py                  # Entry point -- launches API, UI, or both
|-- requirements.txt         # Python package dependencies
|-- .env                     # Environment variables (API keys, paths)
|-- Dockerfile               # Container image definition
|-- docker-compose.yml       # Multi-container orchestration
|
|-- sample_docs/             # 5 sample Markdown documents
|   |-- bigquery.md
|   |-- docker.md
|   |-- kubernetes.md
|   |-- langchain.md
|   |-- rag_patterns.md
|
|-- data/                    # ChromaDB persistent storage (created at runtime)
|   |-- chroma_db/
|
|-- src/                     # Application source code
    |-- __init__.py          # Makes src a Python package
    |-- document_loader.py   # Step 1: Load files, split into chunks
    |-- embeddings.py        # Step 2: Embed chunks, store in ChromaDB
    |-- rag_pipeline.py      # Step 3: Retrieve + generate answers
    |-- api.py               # Step 4: FastAPI HTTP endpoints
    |-- ui.py                # Step 5: Streamlit chat interface
```

The code is organized as a pipeline. Each file handles one stage, and they
connect together in a clear chain: load --> embed --> store --> retrieve --> generate.

---

## 4. Prerequisites

### Required (works out of the box)

- **Python 3.10 or higher** -- the code uses modern type hints (e.g., `list[str]`).
- **pip** -- Python package manager.
- About **2 GB of disk space** -- the sentence-transformers model downloads on first run.

### Optional (for enhanced answers)

- **OpenAI API key** -- set `OPENAI_API_KEY` in `.env` for GPT-powered answers.
- **Anthropic API key** -- set `ANTHROPIC_API_KEY` in `.env` for Claude-powered answers.
- **Docker and Docker Compose** -- for containerized deployment.

If you provide neither API key, the system still works. It uses "extractive fallback"
mode, which returns the most relevant chunk directly instead of generating a
synthesized answer.

---

## 5. Step 1 -- Document Loading and Chunking

**File**: `src/document_loader.py`

This module is responsible for reading files from disk and breaking them into small,
searchable pieces called "chunks."

### 5.1 Why We Chunk Documents

Imagine you have a 50-page PDF about Kubernetes. If you searched for "how do pods
communicate?" and the system returned the entire 50-page document, that would not be
very helpful. Instead, we split the document into small chunks (roughly paragraph-sized),
so the system can return just the one or two paragraphs that actually answer your
question.

Chunking also matters because:

- **Embedding models have size limits.** The all-MiniLM-L6-v2 model works best on texts
  under ~500 tokens. Smaller chunks produce more accurate embeddings.
- **LLM context windows are finite.** We retrieve the top 5 chunks. If each chunk is
  1000 characters, that is about 5000 characters of context -- manageable for any LLM.
- **Precision improves.** Smaller chunks mean each chunk is about one topic, so
  similarity search is more precise.

### 5.2 How the Code Works

**Supported file types**: `.md` (Markdown), `.txt` (plain text), `.pdf` (requires
the optional `pypdf` package).

The `load_documents()` function does the following:

1. **Scan the directory.** It uses `Path.rglob("*")` to recursively find all files,
   then filters for supported extensions.

2. **Read each file.** Markdown and text files are read as UTF-8 strings. PDF files
   are loaded using LangChain's `PyPDFLoader`, which extracts text page by page.

3. **Create LangChain Document objects.** Each file becomes a `Document` with its text
   in `page_content` and the filename in `metadata["source"]`.

4. **Split into chunks.** The `RecursiveCharacterTextSplitter` from LangChain does
   the heavy lifting.

### 5.3 The RecursiveCharacterTextSplitter

This is one of the most important components. It splits text intelligently by trying
a sequence of separators, from most preferred to least preferred:

```
Separators (in order of preference):
  1. "\n\n"  -- paragraph breaks (best: keeps paragraphs intact)
  2. "\n"    -- line breaks (keeps lines intact)
  3. ". "    -- sentence endings (keeps sentences intact)
  4. " "     -- word boundaries (keeps words intact)
  5. ""      -- individual characters (last resort)
```

The algorithm works like this:

```
Given chunk_size = 1000 and chunk_overlap = 200:

1. Try to split on "\n\n" (paragraph breaks).
2. If a resulting piece is still > 1000 chars, split that piece on "\n".
3. If still > 1000 chars, split on ". " (sentences).
4. Keep going down the separator list until every piece is <= 1000 chars.
5. Add 200 chars of overlap between consecutive chunks.
```

### 5.4 Chunk Overlap -- Why 200 Characters?

Overlap ensures that information at chunk boundaries is not lost. Consider this text:

```
...Kubernetes uses etcd as its backing store. Etcd is a distributed
key-value store that holds all cluster state, including pod
definitions and service configurations...
```

If a chunk boundary falls right between "backing store." and "Etcd is a distributed",
then without overlap, one chunk knows about etcd as a backing store, and the next
chunk knows about etcd being a key-value store, but neither chunk has the full
picture. With 200 characters of overlap, both chunks contain the connecting text.

The tradeoff:

| Setting         | Value | Effect                                        |
|-----------------|-------|-----------------------------------------------|
| chunk_size      | 1000  | Each chunk is at most ~1000 characters         |
| chunk_overlap   | 200   | Consecutive chunks share ~200 characters       |
| Overlap ratio   | 20%   | Good balance between coverage and redundancy   |

### 5.5 Metadata Tracking

Each chunk gets metadata so we can trace it back to its source:

```python
chunk.metadata = {
    "source": "kubernetes.md",     # which file it came from
    "chunk_index": 3,              # this is the 4th chunk (0-indexed)
    "total_chunks": 12             # the file was split into 12 chunks total
}
```

This metadata is stored alongside the chunk in ChromaDB and appears in the final
answer as source citations.

### 5.6 The Helper Function

`get_supported_files(directory)` returns a list of filenames that can be loaded from
a directory. The API uses this to show the user which files were found before indexing.

---

## 6. Step 2 -- Embeddings and the Vector Store

**File**: `src/embeddings.py`

This module converts text chunks into numerical vectors (embeddings) and stores them
in ChromaDB for fast similarity search.

### 6.1 What Are Embeddings?

An embedding is a list of numbers (a vector) that represents the meaning of a piece
of text. Texts with similar meanings produce vectors that are close together in
vector space.

```
"How do Kubernetes pods communicate?"
    --> [0.12, -0.45, 0.78, 0.33, ..., -0.21]   (384 numbers)

"Pod-to-pod networking in K8s"
    --> [0.11, -0.43, 0.80, 0.31, ..., -0.19]   (384 numbers, very similar!)

"Best chocolate cake recipe"
    --> [-0.67, 0.22, -0.15, 0.89, ..., 0.44]   (384 numbers, very different)
```

Even though the first two sentences use completely different words, their embeddings
are nearly identical because they mean the same thing. This is what makes semantic
search possible.

### 6.2 The all-MiniLM-L6-v2 Model

This project uses the `all-MiniLM-L6-v2` model from the `sentence-transformers`
library. Here is why:

| Property          | Value                           |
|-------------------|---------------------------------|
| Embedding size    | 384 dimensions                  |
| Model size        | ~80 MB                          |
| Speed             | Very fast (runs on CPU)         |
| Quality           | Excellent for general English   |
| Cost              | Completely free, runs locally   |
| API key needed    | No                              |

This model is a distilled version of Microsoft's MiniLM, fine-tuned on over 1 billion
sentence pairs. It captures semantic meaning well enough for most RAG applications.

The model is loaded once when the `VectorStore` is initialized:

```python
from sentence_transformers import SentenceTransformer
model = SentenceTransformer("all-MiniLM-L6-v2")
```

On first run, the model is downloaded from Hugging Face Hub (~80 MB). After that,
it is cached locally.

### 6.3 ChromaDB -- The Vector Database

ChromaDB is an open-source, lightweight vector database. This project uses it in
**persistent mode**, meaning vectors are saved to disk and survive restarts.

```python
client = chromadb.PersistentClient(path="./data/chroma_db")
collection = client.get_or_create_collection(
    name="rag_documents",
    metadata={"hnsw:space": "cosine"},  # use cosine similarity
)
```

Key concepts:

- **Collection**: like a table in a relational database. All chunks go into one
  collection called `rag_documents`.
- **HNSW index**: ChromaDB uses the HNSW (Hierarchical Navigable Small World)
  algorithm for approximate nearest neighbor search. This is much faster than
  comparing every vector (brute force) and is accurate enough for RAG.
- **Cosine space**: we configure the collection to use cosine similarity, which
  measures the angle between two vectors rather than the distance.

### 6.4 Content-Based Deduplication

When you index documents multiple times (for example, clicking "Index Documents"
twice in the UI), you do not want duplicate chunks. The system handles this with
SHA256 hashing:

```python
ids = [
    hashlib.sha256(doc.page_content.encode()).hexdigest()[:16]
    for doc in docs
]
collection.upsert(ids=ids, ...)  # upsert = update if exists, insert if new
```

Each chunk's content is hashed to produce a unique ID. If you re-index the same
document, the chunks produce the same hashes, and `upsert` updates them in place
rather than creating duplicates.

### 6.5 Similarity Search

When you ask a question, it goes through the same embedding model to produce a
query vector:

```python
query_embedding = model.encode(["How do pods communicate?"])
results = collection.query(
    query_embeddings=[query_embedding],
    n_results=5,  # return top 5 most similar chunks
)
```

ChromaDB returns results sorted by distance (lower = more similar). The code converts
ChromaDB's cosine distance to a similarity score:

```python
# ChromaDB cosine distance is in [0, 2]
# 0 = identical, 2 = opposite meaning
similarity = 1.0 - (distance / 2.0)
# Now: 1.0 = identical, 0.0 = opposite
```

### 6.6 The VectorStore Class API

| Method              | What it does                                          |
|---------------------|-------------------------------------------------------|
| `__init__()`        | Opens ChromaDB, loads the embedding model             |
| `add_documents()`   | Embeds chunks and upserts them into the collection    |
| `similarity_search()`| Finds the k most similar chunks to a query           |
| `get_stats()`       | Returns collection name, chunk count, model info      |
| `reset()`           | Deletes all chunks from the collection                |

---

## 7. Step 3 -- The RAG Pipeline (Retrieve + Generate)

**File**: `src/rag_pipeline.py`

This is the core of the system. It connects retrieval (Step 2) with answer generation.

### 7.1 The RAGResponse Data Class

Every query returns a structured response:

```python
@dataclass
class RAGResponse:
    answer: str                           # the generated answer text
    sources: list[dict]                   # which chunks were used
    model_used: str = "extractive-fallback"  # which LLM generated the answer
```

### 7.2 The Prompt Template

The `_build_prompt()` function constructs the prompt that gets sent to the LLM.
This is one of the most critical pieces of the system. Here is what it looks like:

```
You are a helpful technical assistant. Answer the question using
ONLY the context provided below. If the answer is not in the
context, say "I don't have enough information to answer that."
Cite which source(s) you used.

Context:
[Source 1: kubernetes.md]
Kubernetes uses a flat networking model where every pod can
communicate with every other pod without NAT...

---

[Source 2: docker.md]
Docker containers within the same network can communicate
using container names as hostnames...

---

[Source 3: kubernetes.md]
Services provide stable endpoints for a set of pods...

Question: How do pods communicate in Kubernetes?

Answer:
```

The key design decisions in this prompt:

1. **"ONLY the context provided below"** -- this prevents the LLM from making things
   up. If the answer is not in the retrieved chunks, we want it to say so.
2. **Source labels** -- each chunk is labeled (e.g., `[Source 1: kubernetes.md]`) so
   the LLM can cite which document it used.
3. **Separator lines** (`---`) -- these visually separate chunks so the LLM can
   distinguish between different sources.

### 7.3 The LLM Cascade

The system tries three approaches in order:

```
1. OpenAI (gpt-3.5-turbo)    -- if OPENAI_API_KEY is set
       |
       | (failed or not configured)
       v
2. Anthropic (claude-3-haiku) -- if ANTHROPIC_API_KEY is set
       |
       | (failed or not configured)
       v
3. Extractive fallback        -- always works, no API key needed
```

This cascade design means:

- If you have an OpenAI key, you get GPT-powered answers.
- If you only have an Anthropic key, you get Claude-powered answers.
- If you have neither, you still get useful results via extractive fallback.
- If an API call fails (network error, rate limit), it falls back gracefully.

The code checks for placeholder values too:

```python
has_openai = openai_key and openai_key != "your_key_here"
```

So even if the `.env` file has the default placeholder, it will not try to call
the API and waste time on an authentication error.

### 7.4 Extractive Fallback

When no LLM is available, the system returns the single best-matching chunk
directly as the answer:

```
**[Extractive answer -- no LLM configured]**

Best matching passage (similarity: 89%) from *kubernetes.md*:

> Kubernetes uses a flat networking model where every pod can
> communicate with every other pod without NAT. This is achieved
> through the Container Network Interface (CNI) plugin system...

*Tip: Set OPENAI_API_KEY or ANTHROPIC_API_KEY for generated answers.*
```

This is less polished than an LLM-generated answer, but it is still useful because
the retrieval step found the right passage. The user can read the passage and get
their answer.

### 7.5 Source Tracking

Every response includes source metadata:

```python
sources = [
    {
        "source": "kubernetes.md",
        "chunk_index": 3,
        "score": 0.8921,
        "preview": "Kubernetes uses a flat networking model where..."
    },
    ...
]
```

The preview is truncated to 200 characters to keep API responses lightweight.
The full chunk content is used in the prompt but not returned in the response.

---

## 8. Step 4 -- The FastAPI Server

**File**: `src/api.py`

The FastAPI server wraps the RAG pipeline in a clean HTTP API.

### 8.1 Application Startup (Lifespan)

The vector store is initialized once when the server starts:

```python
@asynccontextmanager
async def lifespan(app: FastAPI):
    app.state.vector_store = VectorStore()
    yield
```

This means:

- The sentence-transformers model is loaded once into memory (not per request).
- ChromaDB is opened once and kept open for the server's lifetime.
- All endpoints access the same `VectorStore` instance via `request.app.state`.

### 8.2 Endpoints

#### GET /health

A simple liveness probe. Returns `{"status": "healthy", "service": "rag-api"}`.
Used by Docker health checks and load balancers.

#### GET /stats

Returns vector store statistics:

```json
{
    "collection": "rag_documents",
    "total_chunks": 47,
    "embedding_model": "all-MiniLM-L6-v2",
    "persist_dir": "./data/chroma_db"
}
```

#### POST /ingest

Loads documents from a directory and indexes them in the vector store.

Request:
```json
{
    "directory": "./sample_docs",
    "chunk_size": 1000,
    "chunk_overlap": 200
}
```

Response:
```json
{
    "files_found": ["bigquery.md", "docker.md", "kubernetes.md", "langchain.md", "rag_patterns.md"],
    "chunks_indexed": 47,
    "elapsed_seconds": 3.21
}
```

**Security**: the endpoint includes path traversal protection. The resolved path must
be under `ALLOWED_BASE` (defaults to the project root). This prevents a malicious
request from indexing `/etc/passwd` or other sensitive files.

#### POST /query

The main RAG endpoint. Retrieves relevant chunks and generates an answer.

Request:
```json
{
    "question": "What is RAG?",
    "k": 5
}
```

Response:
```json
{
    "answer": "RAG (Retrieval-Augmented Generation) is a technique that...",
    "model_used": "extractive-fallback",
    "sources": [
        {
            "source": "rag_patterns.md",
            "chunk_index": 0,
            "score": 0.8934,
            "preview": "Retrieval-Augmented Generation (RAG) is a technique..."
        }
    ],
    "elapsed_seconds": 0.45
}
```

### 8.3 CORS Configuration

The server allows requests from any origin:

```python
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)
```

This is permissive and suitable for local development. In production, you would
restrict `allow_origins` to your frontend's domain.

### 8.4 Request/Response Models

All requests and responses are defined as Pydantic models. This gives you:

- **Automatic validation**: if someone sends `"k": "not a number"`, FastAPI returns
  a 422 error with a clear message.
- **Auto-generated documentation**: visit `/docs` for interactive Swagger UI.
- **Type safety**: your IDE can autocomplete response fields.

---

## 9. Step 5 -- The Streamlit Dashboard

**File**: `src/ui.py`

The Streamlit dashboard provides a visual interface for interacting with the RAG system.

### 9.1 Layout

The UI has two main areas:

```
+-------------------+----------------------------------------+
|    SIDEBAR        |          MAIN AREA                     |
|                   |                                        |
| [Document Dir]    |  Enterprise RAG System                 |
| [Index Documents] |                                        |
|                   |  User: What is RAG?                    |
| --- Stats ---     |                                        |
| Total Chunks: 47  |  Assistant: RAG is a technique...      |
| Model: all-Mini.. |    [v Sources (5 chunks retrieved)]    |
| Collection: rag.. |    Model: extractive-fallback | 0.45s  |
|                   |                                        |
|                   |  [Ask a question about your docs...]   |
+-------------------+----------------------------------------+
```

### 9.2 Sidebar -- Document Indexing

- **Document directory**: a text input defaulting to `./sample_docs`.
- **Index Documents button**: sends a POST to `/ingest` with the directory path.
- **Collection Stats**: fetches from GET `/stats` and displays the total chunk count,
  embedding model name, and collection name.

### 9.3 Main Area -- Chat Interface

- Uses Streamlit's `st.chat_message` and `st.chat_input` for a ChatGPT-like
  experience.
- **Session history**: messages are stored in `st.session_state.messages` so they
  persist across Streamlit reruns (but not across browser refreshes).
- **Source expander**: after each answer, an expandable section shows all retrieved
  chunks with their source filenames, chunk indices, and similarity scores.
- **Model and timing info**: displayed as a caption below each answer.

### 9.4 API Connection

The UI communicates with the API server via HTTP. The API URL defaults to
`http://localhost:8000` and can be overridden with the `API_URL` environment
variable (used in Docker Compose to point to the `api` service).

---

## 10. Step 6 -- The Entry Point (main.py)

**File**: `main.py`

A simple dispatcher that launches the API server, the UI, or both:

```
python main.py api    # Start FastAPI on port 8000
python main.py ui     # Start Streamlit on port 8501
python main.py all    # Start both (API as background process, UI as foreground)
```

When you run `python main.py all`:

1. The FastAPI server starts as a background subprocess (`subprocess.Popen`).
2. The Streamlit dashboard starts in the foreground (`subprocess.run`).
3. When you press Ctrl+C, the `finally` block terminates the API process.

If no argument is given, it defaults to `api` mode.

---

## 11. End-to-End Data Flow

### Indexing Flow (loading documents)

```
sample_docs/            document_loader.py         embeddings.py          ChromaDB
+-----------+          +------------------+       +----------------+     +----------+
| .md files |  ---->   | Read files       |       | Encode chunks  |     | Store    |
| .txt files|          | Split into chunks|  ---->| all-MiniLM-L6  |---->| vectors  |
| .pdf files|          | Add metadata     |       | SHA256 hash IDs|     | + text   |
+-----------+          +------------------+       +----------------+     | + meta   |
                                                                        +----------+
                       chunk_size: 1000
                       chunk_overlap: 200
                       separators: para, line,
                         sentence, word
```

Step by step:

```
1. User clicks "Index Documents" in the UI (or sends POST /ingest)
2. api.py receives the request, calls document_loader.load_documents()
3. document_loader scans the directory for .md, .txt, .pdf files
4. Each file is read into memory as a string
5. RecursiveCharacterTextSplitter splits each file into ~1000-char chunks
6. Each chunk becomes a Document with metadata (source, chunk_index, total_chunks)
7. api.py passes the chunks to vector_store.add_documents()
8. embeddings.py encodes each chunk into a 384-dimensional vector
9. Each chunk gets a SHA256-based ID for deduplication
10. ChromaDB upserts: vectors + text + metadata saved to disk
```

### Query Flow (asking a question)

```
User Question         embeddings.py         ChromaDB            rag_pipeline.py
+------------+       +---------------+     +----------+        +----------------+
| "What is   | ----> | Encode query  |---->| Find top |------->| Build prompt   |
|  RAG?"     |       | all-MiniLM-L6 |     | 5 similar|        | with context   |
+------------+       +---------------+     | chunks   |        |                |
                                           +----------+        | Try OpenAI     |
                                                               | Try Anthropic  |
                                                               | Try extractive |
                                                               +-------+--------+
                                                                       |
                                                                       v
                                                               +----------------+
                                                               | RAGResponse    |
                                                               | - answer       |
                                                               | - sources      |
                                                               | - model_used   |
                                                               +----------------+
```

Step by step:

```
1. User types a question in the chat input (or sends POST /query)
2. api.py receives the request, calls rag_pipeline.query()
3. rag_pipeline calls vector_store.similarity_search(question, k=5)
4. embeddings.py encodes the question into a 384-dimensional vector
5. ChromaDB compares this vector against all stored vectors using cosine similarity
6. The top 5 most similar chunks are returned with their scores
7. rag_pipeline builds a prompt: system instructions + retrieved chunks + question
8. The prompt is sent to OpenAI, Anthropic, or extractive fallback
9. The LLM generates an answer grounded in the retrieved context
10. A RAGResponse is returned with the answer, sources, and model info
11. api.py wraps this in a QueryResponse and returns it as JSON
12. The UI displays the answer, sources, and timing information
```

---

## 12. Running the Project Locally

### Step 1: Navigate to the project directory

```bash
cd POC-02-Enterprise-RAG-System
```

### Step 2: Install dependencies

```bash
pip install langchain langchain-community langchain-openai langchain-text-splitters \
    chromadb sentence-transformers fastapi uvicorn streamlit python-dotenv \
    requests python-multipart
```

Note: The first time you run the system, it will download the all-MiniLM-L6-v2 model
(~80 MB). This only happens once.

### Step 3: (Optional) Configure API keys

Edit the `.env` file if you want LLM-generated answers:

```
OPENAI_API_KEY=sk-your-actual-key-here
ANTHROPIC_API_KEY=sk-ant-your-actual-key-here
```

If you skip this step, the system still works using extractive fallback.

### Step 4: Start the system

```bash
python main.py all
```

This starts:
- The FastAPI server on http://localhost:8000
- The Streamlit dashboard on http://localhost:8501

### Step 5: Index the sample documents

1. Open http://localhost:8501 in your browser.
2. In the left sidebar, you will see a "Document directory" field pre-filled with
   `./sample_docs`.
3. Click the "Index Documents" button.
4. Wait a few seconds. You should see a success message like:
   "Indexed 47 chunks from 5 files in 3.21s"

### Step 6: Ask questions

Type a question in the chat input at the bottom:

- "What is RAG?"
- "How does Kubernetes networking work?"
- "Explain Docker containers vs images"
- "What are the best practices for chunking documents?"
- "How does LangChain work?"

Each answer will show the retrieved sources and similarity scores.

### Step 7: Stop the system

Press Ctrl+C in the terminal. This stops both the API server and the Streamlit
dashboard.

---

## 13. Running with Docker

### Build and start

```bash
docker-compose up --build
```

This builds a Docker image with:
- Python 3.11 (slim base image)
- All Python dependencies pre-installed
- The all-MiniLM-L6-v2 model pre-downloaded (so startup is fast)
- Sample documents copied into the image

Two containers start:
- **api** on port 8000 -- the FastAPI server
- **ui** on port 8501 -- the Streamlit dashboard

### Access the services

- API: http://localhost:8000
- API docs (Swagger): http://localhost:8000/docs
- Dashboard: http://localhost:8501

### Data persistence

The `docker-compose.yml` mounts `./data` as a volume:

```yaml
volumes:
  - ./data:/app/data
```

This means ChromaDB data persists on your host machine even if the container is
destroyed. To start fresh, delete the `data/` directory.

### Stop the containers

```bash
docker-compose down
```

### Docker architecture

```
+---------------------------+     +---------------------------+
| Container: api            |     | Container: ui             |
|                           |     |                           |
| FastAPI (port 8000)       |<----| Streamlit (port 8501)     |
| ChromaDB (persistent)     |     | API_URL=http://api:8000   |
| sentence-transformers     |     |                           |
+---------------------------+     +---------------------------+
        |                                     |
        v                                     v
   host:8000                             host:8501
```

The UI container connects to the API container using Docker's internal DNS
(`http://api:8000`), not `localhost`.

---

## 14. Testing the API with curl

You can test the API directly from the command line without the UI.

### Health check

```bash
curl http://localhost:8000/health
```

Expected response:
```json
{"status": "healthy", "service": "rag-api"}
```

### Check collection stats

```bash
curl http://localhost:8000/stats
```

Expected response (before indexing):
```json
{"collection": "rag_documents", "total_chunks": 0, "embedding_model": "all-MiniLM-L6-v2", "persist_dir": "./data/chroma_db"}
```

### Index the sample documents

```bash
curl -X POST http://localhost:8000/ingest \
  -H "Content-Type: application/json" \
  -d '{"directory": "./sample_docs"}'
```

Expected response:
```json
{
  "files_found": ["bigquery.md", "docker.md", "kubernetes.md", "langchain.md", "rag_patterns.md"],
  "chunks_indexed": 47,
  "elapsed_seconds": 3.21
}
```

### Ask a question

```bash
curl -X POST http://localhost:8000/query \
  -H "Content-Type: application/json" \
  -d '{"question": "What is RAG and how does it work?", "k": 5}'
```

Expected response:
```json
{
  "answer": "**[Extractive answer -- no LLM configured]** ...",
  "model_used": "extractive-fallback",
  "sources": [
    {
      "source": "rag_patterns.md",
      "chunk_index": 0,
      "score": 0.8934,
      "preview": "Retrieval-Augmented Generation (RAG) is a technique..."
    }
  ],
  "elapsed_seconds": 0.45
}
```

### Ask with a different number of results

```bash
curl -X POST http://localhost:8000/query \
  -H "Content-Type: application/json" \
  -d '{"question": "Explain Docker networking", "k": 3}'
```

### Index with custom chunk settings

```bash
curl -X POST http://localhost:8000/ingest \
  -H "Content-Type: application/json" \
  -d '{"directory": "./sample_docs", "chunk_size": 500, "chunk_overlap": 100}'
```

### View auto-generated API docs

Open http://localhost:8000/docs in your browser for interactive Swagger documentation.
You can try all endpoints directly from the browser.

---

## 15. Key Concepts Explained in Depth

### 15.1 Cosine Similarity

Cosine similarity measures the angle between two vectors, ignoring their magnitude.
It is the standard metric for comparing text embeddings.

```
           B (0.6, 0.8)
          /
         /  angle = 15 degrees --> cosine similarity = 0.97 (very similar)
        /
       /----------> A (0.9, 0.4)

Cosine similarity = cos(angle between A and B)
  = (A . B) / (|A| * |B|)
  = 1.0 means identical direction
  = 0.0 means perpendicular (unrelated)
  = -1.0 means opposite direction
```

Why cosine instead of Euclidean distance? Because cosine similarity is invariant
to the length of the vectors. Two sentences that say the same thing in different
numbers of words will have similar directions but different magnitudes. Cosine
similarity catches the meaning; Euclidean distance might miss it.

ChromaDB internally uses cosine distance (1 - cosine_similarity), which ranges
from 0 (identical) to 2 (opposite). The code converts this back to similarity:

```python
similarity = 1.0 - (distance / 2.0)
```

### 15.2 How HNSW Works (Simplified)

HNSW (Hierarchical Navigable Small World) is the algorithm ChromaDB uses to find
similar vectors quickly without comparing against every stored vector.

Think of it like a skip list for vectors:

```
Layer 3 (few nodes):     A ---------> F
                         |             |
Layer 2 (more nodes):    A ---> C ---> F ---> H
                         |      |      |      |
Layer 1 (even more):     A -> B -> C -> E -> F -> G -> H
                         |    |    |    |    |    |    |
Layer 0 (all nodes):     A  B  C  D  E  F  G  H  I  J
```

To find vectors similar to a query:
1. Start at the top layer (few nodes, big jumps).
2. Find the nearest node at each layer.
3. Drop down to the next layer and refine.
4. At the bottom layer, do a local search.

This gives O(log N) search time instead of O(N), making it practical for millions
of documents.

### 15.3 Sentence Transformers Architecture

The all-MiniLM-L6-v2 model is a transformer neural network that:

1. **Tokenizes** the input text into subword tokens.
2. **Passes tokens** through 6 transformer layers (the "L6" in the name).
3. **Pools** the output into a single 384-dimensional vector (mean pooling).

```
Input: "How do pods communicate?"

Tokenizer:   ["how", "do", "pods", "communicate", "?"]
                    |
Transformer:  6 layers of self-attention
                    |
Pooling:      Mean of all token embeddings
                    |
Output:       [0.12, -0.45, 0.78, ..., -0.21]  (384 numbers)
```

The "MiniLM" part means it is a smaller, distilled version of a larger model.
Distillation trains a small model to mimic a large model, keeping most of the
quality at a fraction of the size and speed.

### 15.4 Why ChromaDB?

There are many vector databases (Pinecone, Weaviate, Milvus, Qdrant, FAISS). This
project uses ChromaDB because:

| Feature            | ChromaDB advantage                                  |
|--------------------|-----------------------------------------------------|
| Installation       | `pip install chromadb` -- no external service needed |
| Persistence        | Built-in file-based storage                         |
| Embedded mode      | Runs in-process, no separate server needed           |
| Python-native      | First-class Python API                               |
| Metadata filtering | Can filter by source, chunk_index, etc.              |
| Good for POCs      | Zero configuration needed                            |

For production at scale (millions of documents), you might switch to a managed
service like Pinecone or a distributed database like Milvus. But for learning and
prototyping, ChromaDB is ideal.

### 15.5 The Extractive vs. Generative Spectrum

This system supports two modes, which sit at opposite ends of a spectrum:

```
Extractive                                              Generative
|-------|-------|-------|-------|-------|-------|---------|
Return the     Return multiple    Summarize the      Generate a
best chunk     chunks ranked      chunks into a      conversational
as-is          by relevance       concise answer     answer with
                                                     citations

<-- This project's fallback mode      This project's LLM mode -->
```

**Extractive mode** (no API key):
- Returns the highest-scoring chunk verbatim.
- Pros: fast, deterministic, no API cost, no hallucination risk.
- Cons: may include irrelevant text within the chunk, no synthesis.

**Generative mode** (with API key):
- Sends retrieved chunks + question to an LLM.
- Pros: synthesizes a natural-language answer, can combine information from
  multiple chunks, cites sources.
- Cons: slower, costs money, small hallucination risk (mitigated by the "ONLY
  use the context" instruction in the prompt).

---

## 16. Configuration Reference

### Environment Variables

| Variable            | Default              | Description                               |
|---------------------|----------------------|-------------------------------------------|
| `OPENAI_API_KEY`    | `your_key_here`      | OpenAI API key for GPT-powered answers    |
| `ANTHROPIC_API_KEY` | `your_key_here`      | Anthropic API key for Claude-powered answers |
| `CHROMA_DB_PATH`    | `./data/chroma_db`   | Where ChromaDB stores its data on disk    |
| `ALLOWED_BASE`      | Project root         | Base directory for path traversal protection |
| `API_URL`           | `http://localhost:8000` | API URL used by the Streamlit UI       |

### Chunking Parameters

| Parameter       | Default | Recommended Range | Notes                          |
|-----------------|---------|-------------------|--------------------------------|
| `chunk_size`    | 1000    | 500 -- 2000       | Characters per chunk           |
| `chunk_overlap` | 200     | 50 -- 400         | Overlap between chunks         |
| `k`             | 5       | 3 -- 10           | Number of chunks to retrieve   |

### Ports

| Service    | Port | Protocol |
|------------|------|----------|
| FastAPI    | 8000 | HTTP     |
| Streamlit  | 8501 | HTTP     |

---

## 17. Troubleshooting

### "Cannot connect to API. Is the server running?"

**Cause**: The Streamlit UI cannot reach the FastAPI server on localhost:8000.

**Fix**:
- Make sure you ran `python main.py all` (not just `python main.py ui`).
- If running services separately, start the API first: `python main.py api`, then
  in another terminal: `python main.py ui`.
- If using Docker, check that both containers are running: `docker-compose ps`.

### "No documents indexed yet. Call POST /ingest first."

**Cause**: You asked a question before indexing any documents.

**Fix**: Click "Index Documents" in the sidebar, or run:
```bash
curl -X POST http://localhost:8000/ingest \
  -H "Content-Type: application/json" \
  -d '{"directory": "./sample_docs"}'
```

### "No supported files found in './sample_docs'"

**Cause**: The server cannot find the `sample_docs` directory relative to its
working directory.

**Fix**:
- Make sure you are running `main.py` from the project root directory.
- In Docker, the sample_docs are at `/app/sample_docs`.
- Try using an absolute path in the API call.

### Model download is slow or fails

**Cause**: The all-MiniLM-L6-v2 model (~80 MB) is downloaded from Hugging Face Hub
on first run.

**Fix**:
- Check your internet connection.
- If behind a corporate proxy, set `HTTP_PROXY` and `HTTPS_PROXY`.
- The model is cached in `~/.cache/huggingface/` after first download.
- In Docker, the model is pre-downloaded during image build.

### "LLM generation failed: ..."

**Cause**: The configured API key is invalid or the API is unreachable.

**Fix**:
- Check that your API key is correct in `.env`.
- Make sure the key is not the placeholder `your_key_here`.
- Check your API account for billing issues or rate limits.
- The system will automatically fall back to extractive mode, so you will still
  get an answer.

### ChromaDB errors on startup

**Cause**: Corrupted database files in `data/chroma_db/`.

**Fix**: Delete the data directory and re-index:
```bash
rm -rf data/chroma_db
python main.py api
# Then re-index via the UI or curl
```

### Port already in use

**Cause**: Another process is using port 8000 or 8501.

**Fix**:
```bash
# Find what is using the port
lsof -i :8000
# Kill the process
kill -9 <PID>
```

Or modify the ports in `main.py` (search for `8000` and `8501`).

### ImportError: langchain or sentence-transformers not found

**Cause**: Dependencies are not installed.

**Fix**:
```bash
pip install langchain langchain-community langchain-openai langchain-text-splitters \
    chromadb sentence-transformers fastapi uvicorn streamlit python-dotenv \
    requests python-multipart
```

### Answers seem irrelevant or low quality

**Possible causes and fixes**:

1. **Chunk size too large**: Try re-indexing with `chunk_size=500`. Smaller chunks
   are more focused and match better.
2. **Not enough chunks retrieved**: Increase `k` from 5 to 10 in the query.
3. **Documents are too short**: Very short documents may not have enough content
   for meaningful embeddings.
4. **Question is too vague**: Be specific. "Tell me about Kubernetes" is vague;
   "How do Kubernetes pods communicate across nodes?" is specific.

### Re-indexing does not seem to update

**Cause**: Content-based deduplication means identical chunks are not duplicated.

**Fix**: If you changed the content of a file and want to re-index, the chunks with
new content will be added, and unchanged chunks will be updated in place. If you want
a completely fresh index, call the `reset()` method on the vector store or delete the
`data/chroma_db/` directory.

---

## 18. What to Try Next

Once you have the system running, here are some experiments to deepen your understanding:

### Experiment 1: Add your own documents

Create a new directory with your own `.md` or `.txt` files and index them:

```bash
curl -X POST http://localhost:8000/ingest \
  -H "Content-Type: application/json" \
  -d '{"directory": "./my_docs"}'
```

### Experiment 2: Tune chunk sizes

Re-index with different chunk sizes and see how it affects answer quality:

```bash
# Small chunks (more precise, less context)
curl -X POST http://localhost:8000/ingest \
  -H "Content-Type: application/json" \
  -d '{"directory": "./sample_docs", "chunk_size": 300, "chunk_overlap": 50}'

# Large chunks (more context, less precise)
curl -X POST http://localhost:8000/ingest \
  -H "Content-Type: application/json" \
  -d '{"directory": "./sample_docs", "chunk_size": 2000, "chunk_overlap": 400}'
```

### Experiment 3: Add an LLM

Set an OpenAI or Anthropic API key in `.env` and restart the server. Compare the
extractive fallback answers with the LLM-generated answers for the same questions.

### Experiment 4: Inspect the vector store

Use the `/stats` endpoint to monitor how many chunks are stored. Try indexing the
same documents twice and verify the count does not double (deduplication working).

### Experiment 5: Explore the API docs

Visit http://localhost:8000/docs for the auto-generated Swagger UI. You can try
all endpoints interactively, see the request/response schemas, and understand the
API contract.

---

## Summary

This project implements a complete RAG pipeline in about 400 lines of Python:

| Component           | File                 | Lines | What it does                      |
|---------------------|----------------------|-------|-----------------------------------|
| Document loader     | document_loader.py   | ~100  | Read files, split into chunks     |
| Vector store        | embeddings.py        | ~110  | Embed, store, search with ChromaDB|
| RAG pipeline        | rag_pipeline.py      | ~135  | Retrieve context, generate answers|
| API server          | api.py               | ~145  | HTTP endpoints for the pipeline   |
| Dashboard           | ui.py                | ~120  | Chat-style visual interface       |
| Entry point         | main.py              | ~45   | Launch API, UI, or both           |

The key takeaway: RAG is not magic. It is a simple pipeline -- load, chunk, embed,
store, retrieve, generate. Each step is straightforward on its own. The power comes
from combining them into a system that can answer questions about any set of documents,
with source citations and graceful fallback when no LLM is available.

---

## 19. Interview Questions

*Situation-based and technical questions from AI Engineer, ML Platform, and Data Engineer interviews. Sourced from LinkedIn posts, Glassdoor interview reports, and community discussions on Hacker News and r/MachineLearning.*

---

### Situational / Behavioral Questions

**Q: "Your RAG system confidently answered a compliance question incorrectly and the legal team is upset. Walk through your incident response and the technical changes you'd make."**

A: Immediate: add a disclaimer banner to the UI ("AI-generated answers may not reflect current policy — always verify with official documentation") while investigating. Root cause analysis: (1) Log the exact query, the top-5 retrieved chunks and their similarity scores, and the LLM's generated response. Was the correct answer in any retrieved chunk? If no — retrieval failed, the LLM hallucinated from training data. If yes — the LLM ignored the retrieved context. Technical fixes: add a minimum similarity threshold (`if best_match_score < 0.6: return "I couldn't find authoritative information on this topic. Please consult the official documentation."` instead of sending low-quality context to the LLM). Strengthen the system prompt: "If you are not certain the answer is supported by the provided context, say 'I don't have authoritative information on this — please consult the official source document directly.'" Add a post-retrieval citation validator: the LLM must cite the source filename and chunk index for every factual claim it makes.

**Q: "Legal told you a policy document was superseded 6 months ago but the RAG system is still citing it. How do you fix the document lifecycle problem?"**

A: Three-layer fix: (1) **Metadata-based filtering** — at indexing time, add `effective_date` and `expiry_date` to each document's metadata. ChromaDB supports metadata filtering: `collection.query(where={"expiry_date": {"$gt": today_iso}})`. Superseded documents are automatically excluded without deleting them. (2) **Explicit deletion** — when a policy is replaced, the old document is removed from the vector store using its content-hash ID before the new version is indexed. Don't rely on upsert alone — upsert updates matched IDs but doesn't remove chunks from deleted sections of a revised document. (3) **Document ownership workflow** — integrate with the document management system. When a document's status changes to "superseded" in the CMS, a webhook triggers an Airflow task that calls `vector_store.remove_document(source=filename)` and indexes the replacement. This closes the human-process gap that caused this incident.

**Q: "You need to scale the RAG system from 5 documents to 50,000 technical documents. The current architecture handles it in 20 seconds per document. How do you redesign the ingestion pipeline?"**

A: The bottleneck is embedding computation (CPU-bound). Four optimizations: (1) **Batch encoding** — sentence-transformers' `model.encode()` accepts batches. Instead of encoding one chunk at a time, encode 64 chunks per call. This achieves 10–20x throughput improvement on CPU alone. (2) **GPU acceleration** — move the embedding model to a GPU instance: `SentenceTransformer("all-MiniLM-L6-v2", device="cuda")`. Batch encoding on GPU achieves 50–100x the throughput of single-chunk CPU encoding. (3) **Parallel ingestion workers** — run 8 workers in parallel using Celery + Redis, each handling a subset of documents. Combined with GPU batching, 50,000 documents become a 2–4 hour initial load (done once). (4) **Content-hash deduplication** — already in this POC via SHA256 chunk IDs. On subsequent runs (documents updated daily), only changed chunks are re-embedded and upserted. At steady state, the incremental ingestion handles < 100 changed chunks per day.

---

### Technical Deep-Dive Questions

**Q: "Explain the trade-off between chunk size, chunk overlap, and answer quality. How do you tune them empirically?"**

A: Chunk size controls the precision vs. context trade-off. Small chunks (300 chars): high precision retrieval (the matching passage is tightly relevant) but the answer may lack surrounding context needed for a complete response. Large chunks (2000 chars): broad context but diluted similarity signal — the retrieved chunk may contain the answer buried in irrelevant text. Overlap ensures continuity: information at a chunk boundary appears in both adjacent chunks. The 20% overlap heuristic (200 chars for 1000-char chunks) prevents boundary information loss. Empirical tuning process: create a test set of 30 question/expected-answer pairs from your documents. Score retrieval (does the correct passage appear in the top-5?) and answer quality (does the LLM's response correctly answer the question?) at chunk sizes of 500, 1000, 1500. Plot the precision-recall curve. For most enterprise technical documents, 800–1200 chars with 20% overlap is the sweet spot. Special case: if your documents have clear semantic sections (Markdown headers, numbered steps), split on those boundaries first before falling back to character count.

**Q: "What's the difference between sparse (BM25) and dense (embedding) retrieval? When would you add hybrid search?"**

A: BM25 is term-frequency-based: scores documents by exact keyword matches weighted by their rarity in the corpus (TF-IDF logic). Excels when queries contain specific jargon, model numbers, or error codes. Dense retrieval uses embedding similarity: captures semantic meaning even when query and document use different words. "How do I avoid overfitting?" and "regularization techniques for gradient boosting" are semantically close despite sharing no keywords. Add hybrid search when: (1) Users query with exact product names or error codes that the embedding model may not encode distinctly (e.g., "error 0x8024002E" — the model may not differentiate this from other error codes). (2) Retrieval quality on keyword-heavy queries is poor despite good semantic coverage. Implementation: run BM25 (via `rank_bm25` or Elasticsearch) and dense retrieval in parallel, then merge rankings using Reciprocal Rank Fusion (RRF): `score = sum(1 / (k + rank_i) for each retriever)`. RRF is robust and requires no weight tuning.

**Q: "How would you evaluate the quality of your RAG system at scale? What metrics and tooling would you use?"**

A: Three metric categories: (1) **Retrieval quality** — Precision@5 (are the top-5 retrieved chunks relevant?) and Recall (did we retrieve all relevant chunks for this query?). Requires a human-labeled evaluation set of 100+ query/relevant-chunk pairs. Use LLM-as-judge (Claude or GPT-4 scoring chunk relevance 1–5) to scale labeling cheaply. (2) **Answer quality** — Faithfulness (does the answer stay within the retrieved context?), Answer Relevance (does it actually answer the question asked?), Hallucination rate (claims in the answer not supported by any retrieved chunk). Tool: RAGAS framework automates all three against a labeled dataset. (3) **Business metrics** — resolution rate (did the user get what they needed without follow-up?), negative feedback rate (thumbs-down clicks in the UI), escalation rate (how often users abandon the bot and contact a human). Run weekly regression tests against a 50-query golden dataset to catch regressions when chunking parameters, embedding models, or LLM prompts change.

---

### System Design Questions

**Q: "Design a multi-tenant RAG system where each department has isolated document collections and cannot see each other's data."**

A: Four isolation layers: (1) **Collection-per-tenant** — each department gets its own ChromaDB collection (`rag_hr`, `rag_finance`, `rag_legal`). The API extracts the tenant ID from the authenticated JWT token and only queries that tenant's collection. Zero cross-collection data leakage is possible. (2) **Tenant-aware ingestion** — document upload endpoints require authentication. Documents are tagged with `tenant_id` in metadata and stored in the tenant's collection. An admin endpoint can audit what's indexed per tenant. (3) **Rate limiting per tenant** — each tenant gets a query budget (e.g., 1,000 queries/day) to prevent one department monopolizing the embedding model or LLM API budget. Enforce via Redis with a sliding window counter keyed on `tenant_id`. (4) **Audit logging** — every query, retrieved chunk, and response is logged with `tenant_id`, `user_id`, `timestamp`, and `query_hash` for compliance (GDPR Article 30, SOC 2). For maximum isolation in regulated environments: a dedicated ChromaDB instance per tenant, deployed in the tenant's own cloud account.

**Q: "A startup asks you: should we build a RAG system or fine-tune an LLM on our proprietary data? How do you advise them?"**

A: RAG first, fine-tuning rarely. RAG wins in most enterprise scenarios because: (1) **Data freshness** — RAG retrieves from a live document store that can be updated in minutes. Fine-tuning bakes knowledge into model weights; updating requires a full retraining cycle (hours to days, thousands of dollars). (2) **Citation and auditability** — RAG returns source documents with every answer. Fine-tuned models generate from internalized knowledge with no traceable source. For legal and compliance use cases, citations are mandatory. (3) **Cost** — embedding 50,000 documents costs cents. Fine-tuning a 7B parameter model costs hundreds to thousands of dollars and requires ML expertise. (4) **Hallucination control** — the "ONLY use provided context" instruction in this POC's prompt directly constrains the answer to indexed content. Fine-tuned models hallucinate with equal confidence to base models. When fine-tuning makes sense: when the style of generation matters (e.g., the model needs to write in your company's specific voice), when latency is critical (no retrieval step), or when domain terminology is so specialized that embeddings don't cluster correctly.
