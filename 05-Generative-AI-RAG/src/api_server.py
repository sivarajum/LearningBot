"""
FastAPI Server for RAG System
"""
import logging
from typing import List, Dict, Any
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, Field
import uvicorn
from rag_pipeline import RAGPipeline

logger = logging.getLogger(__name__)

app = FastAPI(
    title="RAG API",
    description="Retrieval-Augmented Generation API for data documentation",
    version="1.0.0"
)

# Global RAG pipeline
rag_pipeline = None


class QueryRequest(BaseModel):
    """Request model for queries"""
    question: str = Field(..., description="User question")
    k: int = Field(default=4, ge=1, le=10, description="Number of documents to retrieve")


class QueryResponse(BaseModel):
    """Response model for queries"""
    answer: str
    sources: List[Dict[str, Any]]


@app.on_event("startup")
async def startup_event():
    """Initialize RAG pipeline on startup"""
    global rag_pipeline
    
    try:
        rag_pipeline = RAGPipeline(
            vector_store_type="chroma",
            embedding_model="huggingface",
            llm_provider="openai"
        )
        
        # Build pipeline if data exists
        import os
        data_dir = "data/documents"
        if os.path.exists(data_dir):
            rag_pipeline.build_pipeline(data_dir)
            logger.info("RAG pipeline initialized successfully")
        else:
            logger.warning("Data directory not found. Pipeline not built.")
    except Exception as e:
        logger.error(f"Error initializing RAG pipeline: {e}")


@app.get("/")
async def root():
    """Root endpoint"""
    return {
        "message": "RAG API",
        "version": "1.0.0",
        "status": "healthy"
    }


@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {
        "status": "healthy",
        "pipeline_ready": rag_pipeline is not None and rag_pipeline.qa_chain is not None
    }


@app.post("/query", response_model=QueryResponse)
async def query(request: QueryRequest):
    """
    Query the RAG system
    
    Args:
        request: Query request
        
    Returns:
        Query response with answer and sources
    """
    if rag_pipeline is None or rag_pipeline.qa_chain is None:
        raise HTTPException(
            status_code=503,
            detail="RAG pipeline not initialized. Please build the pipeline first."
        )
    
    try:
        # Update retriever k if different
        if request.k != 4:
            rag_pipeline.create_qa_chain(k=request.k)
        
        # Query pipeline
        result = rag_pipeline.query(request.question)
        
        return QueryResponse(
            answer=result["answer"],
            sources=result["source_documents"]
        )
    except Exception as e:
        logger.error(f"Query error: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/build")
async def build_pipeline(data_dir: str = "data/documents"):
    """
    Build RAG pipeline from documents
    
    Args:
        data_dir: Directory containing documents
        
    Returns:
        Success message
    """
    global rag_pipeline
    
    if rag_pipeline is None:
        raise HTTPException(status_code=503, detail="RAG pipeline not initialized")
    
    try:
        rag_pipeline.build_pipeline(data_dir)
        return {"message": "Pipeline built successfully"}
    except Exception as e:
        logger.error(f"Build error: {e}")
        raise HTTPException(status_code=500, detail=str(e))


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    
    uvicorn.run(
        "api_server:app",
        host="0.0.0.0",
        port=8000,
        reload=True
    )

