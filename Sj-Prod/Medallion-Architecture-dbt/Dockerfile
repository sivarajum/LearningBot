FROM python:3.11-slim

# System deps
RUN apt-get update && apt-get install -y --no-install-recommends \
    gcc \
    g++ \
    curl \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app

# Install Python dependencies first (layer caching)
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy project files
COPY . .

# Create data directories
RUN mkdir -p data/raw

# Environment defaults (overridable via docker-compose or -e flags)
ENV RAW_DATA_PATH=/app/data/raw
ENV DUCKDB_PATH=/app/data/warehouse.duckdb
ENV PYTHONUNBUFFERED=1
ENV PYTHONPATH=/app

# Expose ports for API and Streamlit
EXPOSE 8000 8501

# Default: run full pipeline then start API
CMD ["python", "main.py", "all"]
