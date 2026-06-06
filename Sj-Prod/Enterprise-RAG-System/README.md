# Enterprise RAG System

RAG pipeline with ChromaDB + sentence-transformers — document ingestion, vector search, LLM-generated or extractive answers. FastAPI API + Streamlit dashboard.

## What It Does

- **Document Loading**: Ingest `.md`, `.txt`, `.pdf` files with recursive character splitting (chunk_size=1000, overlap=200)
- **Embeddings**: `all-MiniLM-L6-v2` via sentence-transformers (runs locally, no API key)
- **Vector Store**: ChromaDB with persistent SQLite storage and cosine similarity search
- **RAG Pipeline**: Retrieve top-k chunks, build grounded prompt, generate answer via LLM or extractive fallback
- **Fallback Mode**: Works fully offline — returns best-matching chunk with similarity score when no LLM key configured
- **REST API**: FastAPI endpoints for document ingestion, querying, and store management
- **Dashboard**: Streamlit UI for document upload and Q&A

## Architecture

```
sample_docs/              # Markdown files indexed on startup (BigQuery, Docker, K8s, LangChain, RAG)
src/document_loader.py    # File loading + text splitting (LangChain splitter)
src/embeddings.py         # ChromaDB VectorStore + sentence-transformers
src/rag_pipeline.py       # Retrieve + generate (OpenAI/Anthropic/extractive fallback)
src/api.py                # FastAPI REST API
src/ui.py                 # Streamlit dashboard
```

## Quick Start

```bash
pip install -r requirements.txt

# Optional: configure LLM API key for generated answers
cp .env.example .env      # Add OPENAI_API_KEY or ANTHROPIC_API_KEY

python main.py api         # API on :8008
python main.py ui          # Dashboard on :8501
python main.py all         # Both
```

## Testing

```bash
pytest                     # 79 tests
```

## LLM Configuration

| Key | Model |
|-----|-------|
| `OPENAI_API_KEY` | gpt-3.5-turbo |
| `ANTHROPIC_API_KEY` | claude-3-haiku |
| Neither | Extractive fallback (best chunk + similarity score) |

## Docker

```bash
docker compose up --build
```

See [RUNNING.md](RUNNING.md) for full build, test, and deployment instructions.
