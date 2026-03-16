FROM python:3.11-slim

WORKDIR /app

# Install system dependencies for sentence-transformers
RUN apt-get update && \
    apt-get install -y --no-install-recommends build-essential && \
    rm -rf /var/lib/apt/lists/*

# Install Python dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Pre-download the sentence-transformers model so it's cached in the image
RUN python -c "from sentence_transformers import SentenceTransformer; SentenceTransformer('all-MiniLM-L6-v2')"

# Copy application code and sample documents
COPY src/ ./src/
COPY sample_docs/ ./sample_docs/

# Create data directory for ChromaDB persistence
RUN mkdir -p /app/data/chroma_db

# Expose API and Streamlit ports
EXPOSE 8000 8501
