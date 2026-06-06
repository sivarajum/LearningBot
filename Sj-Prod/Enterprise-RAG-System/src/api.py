"""FastAPI server exposing the RAG pipeline over HTTP."""

import logging
import time
from contextlib import asynccontextmanager
from collections.abc import AsyncGenerator
from pathlib import Path

from dotenv import load_dotenv
from fastapi import FastAPI, HTTPException, Request
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field, model_validator

from src.document_loader import get_supported_files, load_documents
from src.embeddings import VectorStore
from src.rag_pipeline import query as rag_query
from src.settings import CORS_ORIGINS

load_dotenv()

logger = logging.getLogger(__name__)

ALLOWED_BASE = Path(__file__).parent.parent.resolve()


@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncGenerator[None, None]:
    """Initialize shared resources on startup."""
    logger.info("Starting Enterprise RAG System API")
    app.state.vector_store = VectorStore()
    logger.info("VectorStore initialized successfully")
    yield
    logger.info("Shutting down Enterprise RAG System API")


app = FastAPI(
    title="Enterprise RAG System",
    description="Retrieval-Augmented Generation API for document Q&A",
    version="1.0.0",
    lifespan=lifespan,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=CORS_ORIGINS,
    allow_methods=["*"],
    allow_headers=["*"],
)


# -- Request / Response models ------------------------------------------------


class IngestRequest(BaseModel):
    directory: str = "./sample_docs"
    chunk_size: int = Field(default=1000, ge=100, le=5000, description="Maximum characters per chunk")
    chunk_overlap: int = Field(default=200, ge=0, le=500, description="Overlap between consecutive chunks")

    @model_validator(mode="after")
    def validate_overlap_less_than_size(self) -> "IngestRequest":
        if self.chunk_overlap >= self.chunk_size:
            raise ValueError(
                f"chunk_overlap ({self.chunk_overlap}) must be less than chunk_size ({self.chunk_size})"
            )
        return self


class IngestResponse(BaseModel):
    files_found: list[str]
    chunks_indexed: int
    elapsed_seconds: float


class QueryRequest(BaseModel):
    question: str = Field(..., min_length=1, max_length=2000, description="The question to ask")
    k: int = Field(default=5, ge=1, le=50, description="Number of chunks to retrieve")


class QueryResponse(BaseModel):
    model_config = {"protected_namespaces": ()}
    answer: str
    model_used: str
    sources: list[dict]
    elapsed_seconds: float


# -- Endpoints -----------------------------------------------------------------


@app.get("/health")
def health_check() -> dict:
    """Basic liveness check."""
    return {"status": "healthy", "service": "rag-api"}


@app.get("/stats")
def get_stats(request: Request) -> dict:
    """Return vector store statistics."""
    store: VectorStore = request.app.state.vector_store
    stats = store.get_stats()
    return stats


@app.post("/ingest", response_model=IngestResponse)
def ingest_documents(req: IngestRequest, request: Request) -> IngestResponse:
    """Load documents from a directory and index them in the vector store."""
    start = time.time()
    logger.info("Ingest request: directory=%s, chunk_size=%d, chunk_overlap=%d", req.directory, req.chunk_size, req.chunk_overlap)

    # Path traversal protection
    resolved = Path(req.directory).resolve()
    if not resolved.is_relative_to(ALLOWED_BASE):
        logger.warning("Path traversal attempt blocked: %s", req.directory)
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
    store: VectorStore = request.app.state.vector_store
    count = store.add_documents(chunks)

    elapsed = round(time.time() - start, 2)
    logger.info("Ingested %d chunks from %d files in %.2fs", count, len(files), elapsed)

    return IngestResponse(
        files_found=files,
        chunks_indexed=count,
        elapsed_seconds=elapsed,
    )


@app.post("/query", response_model=QueryResponse)
def query_documents(req: QueryRequest, request: Request) -> QueryResponse:
    """Ask a question and get a RAG-powered answer."""
    start = time.time()
    logger.info("Query request: question=%r, k=%d", req.question[:80], req.k)

    store: VectorStore = request.app.state.vector_store

    if store.collection.count() == 0:
        raise HTTPException(
            status_code=400,
            detail="No documents indexed yet. Call POST /ingest first.",
        )

    response = rag_query(req.question, store, k=req.k)

    elapsed = round(time.time() - start, 2)
    logger.info("Query answered in %.2fs using model=%s", elapsed, response.model_used)

    return QueryResponse(
        answer=response.answer,
        model_used=response.model_used,
        sources=response.sources,
        elapsed_seconds=elapsed,
    )
