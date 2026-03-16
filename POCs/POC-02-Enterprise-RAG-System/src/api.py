"""FastAPI server exposing the RAG pipeline over HTTP."""

import os
import time
from contextlib import asynccontextmanager
from pathlib import Path
from typing import Optional

from dotenv import load_dotenv
from fastapi import FastAPI, HTTPException, Request
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

from src.document_loader import load_documents, get_supported_files
from src.embeddings import VectorStore
from src.rag_pipeline import query as rag_query

load_dotenv()

ALLOWED_BASE = Path("/app")


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Initialize shared resources on startup."""
    app.state.vector_store = VectorStore()
    yield


app = FastAPI(
    title="Enterprise RAG System",
    description="Retrieval-Augmented Generation API for document Q&A",
    version="1.0.0",
    lifespan=lifespan,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)


# ── Request / Response models ──────────────────────────────────────────


class IngestRequest(BaseModel):
    directory: str = "./sample_docs"
    chunk_size: int = 1000
    chunk_overlap: int = 200


class IngestResponse(BaseModel):
    files_found: list[str]
    chunks_indexed: int
    elapsed_seconds: float


class QueryRequest(BaseModel):
    question: str
    k: int = 5


class QueryResponse(BaseModel):
    answer: str
    model_used: str
    sources: list[dict]
    elapsed_seconds: float


# ── Endpoints ──────────────────────────────────────────────────────────


@app.get("/health")
def health_check():
    """Basic liveness check."""
    return {"status": "healthy", "service": "rag-api"}


@app.get("/stats")
def get_stats(request: Request):
    """Return vector store statistics."""
    store = request.app.state.vector_store
    stats = store.get_stats()
    return stats


@app.post("/ingest", response_model=IngestResponse)
def ingest_documents(req: IngestRequest, request: Request):
    """Load documents from a directory and index them in the vector store."""
    start = time.time()

    # Path traversal protection
    resolved = Path(req.directory).resolve()
    if not resolved.is_relative_to(ALLOWED_BASE):
        raise HTTPException(
            status_code=400,
            detail="Directory must be under /app",
        )

    files = get_supported_files(req.directory)
    if not files:
        raise HTTPException(
            status_code=400,
            detail=f"No supported files found in '{req.directory}'",
        )

    chunks = load_documents(
        req.directory,
        chunk_size=req.chunk_size,
        chunk_overlap=req.chunk_overlap,
    )
    store = request.app.state.vector_store
    count = store.add_documents(chunks)

    return IngestResponse(
        files_found=files,
        chunks_indexed=count,
        elapsed_seconds=round(time.time() - start, 2),
    )


@app.post("/query", response_model=QueryResponse)
def query_documents(req: QueryRequest, request: Request):
    """Ask a question and get a RAG-powered answer."""
    start = time.time()
    store = request.app.state.vector_store

    if store.collection.count() == 0:
        raise HTTPException(
            status_code=400,
            detail="No documents indexed yet. Call POST /ingest first.",
        )

    response = rag_query(req.question, store, k=req.k)

    return QueryResponse(
        answer=response.answer,
        model_used=response.model_used,
        sources=response.sources,
        elapsed_seconds=round(time.time() - start, 2),
    )
