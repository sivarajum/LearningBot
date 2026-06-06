# POC-02: Enterprise RAG Documentation System

A working RAG (Retrieval-Augmented Generation) system that answers natural-language questions about a local document corpus. Built with ChromaDB, sentence-transformers, and LangChain.

---

## What actually runs

| Component | Technology |
|-----------|-----------|
| Embeddings | `sentence-transformers` — model `all-MiniLM-L6-v2`, runs locally, no API key needed |
| Vector store | `chromadb.PersistentClient` — SQLite-backed, persists to `data/chroma_db/` |
| Document loading | `langchain-text-splitters` — chunks `.md`, `.txt`, and `.pdf` files |
| LLM generation | OpenAI `gpt-3.5-turbo` or Anthropic `claude-3-haiku` — optional |
| Fallback mode | Extractive answer from the best-matching chunk — works without any API key |
| API | FastAPI |
| UI | Streamlit |

There is no Redis cache, no Pinecone, and no Kubernetes in this POC. The architecture diagram in the original README was aspirational. What ships here is a self-contained local system.

---

## API key requirement

An LLM API key is **optional**. Without one, the system answers questions by returning the best-matching text chunk directly (extractive fallback). This is useful for demos and development.

To get generated, synthesised answers you need one of:

- `OPENAI_API_KEY` — calls `gpt-3.5-turbo`
- `ANTHROPIC_API_KEY` — calls `claude-3-haiku-20240307`

---

## Quickstart

```bash
# 1. Install dependencies
pip install -r requirements.txt

# 2. (Optional) configure API key
cp .env.example .env
# Edit .env and add OPENAI_API_KEY or ANTHROPIC_API_KEY

# 3. Run
python main.py
```

The app will:
1. Load and chunk all `.md` files from `sample_docs/`
2. Embed them with `all-MiniLM-L6-v2` (downloads ~90 MB on first run)
3. Store vectors in `data/chroma_db/`
4. Start the Streamlit UI on `http://localhost:8501`

---

## Project structure

```
POC-02-Enterprise-RAG-System/
├── main.py                   # Entry point
├── requirements.txt
├── .env.example
├── src/
│   ├── document_loader.py    # Load files, split into chunks (LangChain splitter)
│   ├── embeddings.py         # ChromaDB VectorStore + sentence-transformers
│   ├── rag_pipeline.py       # Retrieve + generate (or extractive fallback)
│   ├── api.py                # FastAPI endpoints
│   └── ui.py                 # Streamlit UI
├── sample_docs/              # Markdown files indexed on startup
│   ├── bigquery.md
│   ├── docker.md
│   ├── kubernetes.md
│   ├── langchain.md
│   └── rag_patterns.md
└── data/
    └── chroma_db/            # Auto-created; persists between runs
```

---

## How RAG works here

```
sample_docs/*.md
     │
     ▼
document_loader.py        — RecursiveCharacterTextSplitter (chunk_size=1000, overlap=200)
     │
     ▼
embeddings.py             — SentenceTransformer("all-MiniLM-L6-v2").encode()
     │                       → stored in chromadb.PersistentClient (cosine similarity)
     ▼
User query
     │
     ▼
embeddings.py             — similarity_search(query, k=5)  →  top-5 chunks
     │
     ▼
rag_pipeline.py           — build prompt (context + question)
     │                       → call OpenAI / Anthropic, or extractive fallback
     ▼
Answer + source citations
```

---

## Running without an API key

The system works entirely offline. `rag_pipeline.py` checks for `OPENAI_API_KEY` and `ANTHROPIC_API_KEY`; if neither is set (or both are placeholder values), it returns the best-matching chunk with its similarity score and source filename. The UI labels these answers clearly as extractive mode.

---

## GCP production variant

See `docs/gcp_production_variant.md` for the exact SDK swap to move from local ChromaDB + sentence-transformers to Vertex AI Embeddings + Vertex AI Vector Search.

---

## What this POC teaches

- How chunking strategy (size, overlap) affects retrieval quality
- ChromaDB cosine similarity search mechanics
- LangChain document loading and text splitting
- LLM prompt construction for grounded answering with source citations
- Graceful fallback when no LLM is available
