# Enterprise RAG System -- Running Guide

## Prerequisites

- Python 3.11+
- pip (or a virtualenv manager of your choice)
- Docker and Docker Compose (optional, for containerised deployment)

## Install

```bash
cd Sj-Prod/Enterprise-RAG-System

# Create and activate a virtual environment (recommended)
python -m venv .venv
source .venv/bin/activate   # Linux / macOS
# .venv\Scripts\activate    # Windows

pip install -r requirements.txt
```

The first run will download the `all-MiniLM-L6-v2` sentence-transformer model (~80 MB). This is cached locally for subsequent runs.

## Environment Setup

Copy the example env file and edit it if you have API keys:

```bash
cp .env.example .env
```

The `.env` file contains:

| Variable            | Required | Default             | Description                                       |
|---------------------|----------|---------------------|---------------------------------------------------|
| `OPENAI_API_KEY`    | No       | `your_key_here`     | OpenAI key for GPT-powered answers                |
| `ANTHROPIC_API_KEY` | No       | `your_key_here`     | Anthropic key for Claude-powered answers           |
| `CHROMA_DB_PATH`    | No       | `./data/chroma_db`  | Directory where ChromaDB persists vectors          |

**Both LLM keys are optional.** The system works fully without them using extractive fallback mode (see below).

## Running Tests

```bash
# Run all tests with coverage
pytest

# Run a single test file
pytest tests/test_document_loader.py

# Run a specific test
pytest tests/test_rag_pipeline.py::TestQueryPipeline::test_query_returns_rag_response

# Skip coverage reporting
pytest --no-cov

# Verbose output
pytest -v
```

Tests mock the sentence-transformer model and vector store where needed, so they run quickly without downloading models or requiring API keys.

## Ingesting Documents

Place your `.md`, `.txt`, or `.pdf` files in a directory (the default is `sample_docs/`).

### Via the API (after starting the server)

```bash
curl -X POST http://localhost:8000/ingest \
  -H "Content-Type: application/json" \
  -d '{"directory": "./sample_docs"}'
```

### Via the Streamlit UI

Use the sidebar "Index Documents" button, specifying the directory path.

## Running the System

### API only (FastAPI on port 8000)

```bash
python main.py api
```

### UI only (Streamlit on port 8501)

The UI requires the API to be running separately.

```bash
python main.py ui
```

### Both API and UI

```bash
python main.py all
```

This starts the API server in the background and Streamlit in the foreground.

## Running with Docker

```bash
# Build and start both services
docker compose up --build

# Or run in detached mode
docker compose up --build -d

# Stop
docker compose down
```

The Docker Compose setup runs:
- **api** service on port 8000
- **ui** service on port 8501 (connects to the api service internally)

The `data/` directory is mounted as a volume so ChromaDB data persists across container restarts.

## API Endpoint Reference

| Method | Path      | Description                                    |
|--------|-----------|------------------------------------------------|
| GET    | `/health` | Liveness check. Returns `{"status": "healthy"}`|
| GET    | `/stats`  | Vector store statistics (chunk count, model)   |
| POST   | `/ingest` | Index documents from a directory               |
| POST   | `/query`  | Ask a question and get a RAG-powered answer    |

### POST /ingest

Request body:
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
  "files_found": ["docker.md", "kubernetes.md"],
  "chunks_indexed": 15,
  "elapsed_seconds": 2.34
}
```

### POST /query

Request body:
```json
{
  "question": "What is Docker?",
  "k": 5
}
```

Response:
```json
{
  "answer": "Docker is a platform for building...",
  "model_used": "extractive-fallback",
  "sources": [
    {
      "source": "docker.md",
      "chunk_index": 0,
      "score": 0.92,
      "preview": "Docker is a platform..."
    }
  ],
  "elapsed_seconds": 0.15
}
```

## Fallback Mode

When no `OPENAI_API_KEY` or `ANTHROPIC_API_KEY` is configured (or the keys are set to `your_key_here`), the system operates in **extractive fallback mode**:

1. Documents are still embedded and indexed using the local `all-MiniLM-L6-v2` model (no API key needed).
2. Queries still perform semantic similarity search against the vector store.
3. Instead of generating a synthesized answer via an LLM, the system returns the most relevant chunk verbatim, with its similarity score and source attribution.

This means the core retrieval pipeline works entirely offline and for free. Adding an LLM key upgrades the answer quality from "best matching passage" to "synthesized, cited response."

If an LLM call fails at runtime (network error, quota exceeded, etc.), the system automatically falls back to extractive mode for that request.

## Production Deployment Notes

- **Reverse proxy**: Place Nginx or a cloud load balancer in front of the uvicorn server. Do not expose uvicorn directly to the internet.
- **Workers**: Run with multiple workers for production traffic: `uvicorn src.api:app --workers 4 --host 0.0.0.0 --port 8000`
- **CORS**: The default config allows all origins (`*`). Restrict `allow_origins` in `src/api.py` for production.
- **Path traversal**: The `/ingest` endpoint validates that the requested directory is under `ALLOWED_BASE` (defaults to the project root). Set the `ALLOWED_BASE` environment variable to restrict document ingestion paths.
- **Persistence**: ChromaDB data is stored at `CHROMA_DB_PATH`. Back up this directory to preserve your index.
- **Model caching**: The sentence-transformer model is downloaded once and cached in `~/.cache/huggingface/`. In Docker, it is baked into the image at build time.
- **Secrets**: Never commit `.env` with real API keys. The `.env` file is listed in `.gitignore`.
