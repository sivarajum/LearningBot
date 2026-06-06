# Module 05: Generative AI RAG System

## Overview
Intelligent data documentation system using Retrieval-Augmented Generation (RAG). Combines vector search with LLMs to provide natural language access to enterprise data schemas, pipelines, and metadata.

## Architecture
- **Document Ingestion**: PDF, Markdown, Code files
- **Vector Database**: Pinecone or Chroma
- **Embeddings**: OpenAI or HuggingFace
- **LLM**: GPT-3.5/GPT-4 via LangChain
- **UI**: Streamlit web interface

## Features
- ✅ Multi-format document ingestion
- ✅ Vector database integration
- ✅ Semantic search
- ✅ RAG pipeline with LangChain
- ✅ FastAPI backend
- ✅ Streamlit UI

## Quick Start

### Prerequisites
- OpenAI API key (or HuggingFace)
- Python 3.9+

### Installation
```bash
pip install -r requirements.txt
```

### Setup
1. Set environment variables:
```bash
export OPENAI_API_KEY="your-api-key"
export PINECONE_API_KEY="your-pinecone-key"  # Optional
```

2. Add documents to `data/documents/`:
```bash
mkdir -p data/documents
# Add PDF, TXT, or Markdown files
```

3. Build RAG pipeline:
```python
from src.rag_pipeline import RAGPipeline

rag = RAGPipeline(
    vector_store_type="chroma",  # or "pinecone"
    embedding_model="huggingface",  # or "openai"
    llm_provider="openai"
)

rag.build_pipeline("data/documents")
```

4. Run Streamlit UI:
```bash
streamlit run src/streamlit_app.py
```

5. Or run FastAPI server:
```bash
python src/api_server.py
```

## Usage

### Query via API
```bash
POST /query
Content-Type: application/json

{
  "question": "What is the data schema for customer table?",
  "k": 4
}
```

### Query via Streamlit
1. Open Streamlit UI
2. Initialize and build pipeline
3. Ask questions in the chat interface

## Project Structure
```
05-Generative-AI-RAG/
├── src/
│   ├── rag_pipeline.py
│   ├── api_server.py
│   └── streamlit_app.py
├── data/
│   └── documents/
├── requirements.txt
└── README.md
```

## Success Metrics
- Retrieval accuracy >90%
- Response time <3s
- Answer correctness
- Source attribution

## Next Steps
- Add more document types
- Implement advanced retrieval strategies
- Add response quality evaluation
- Deploy to cloud
