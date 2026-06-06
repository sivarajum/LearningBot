# Dockerfile for POC-07: Enterprise Airflow Orchestration Platform
# ================================================================
# This builds the lightweight Python-only layer (FastAPI + Streamlit).
# For the full Airflow stack, use docker-compose.yml instead.

FROM python:3.11-slim

LABEL maintainer="data-engineering"
LABEL description="POC-07 Airflow Orchestration POC — simulator + API + UI"

# System dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Working directory
WORKDIR /app

# Copy requirements first for layer caching
COPY requirements.txt .

# Install Python dependencies (no Airflow — this is the lightweight image)
RUN pip install --no-cache-dir --upgrade pip \
    && pip install --no-cache-dir -r requirements.txt

# Copy project files
COPY . .

# Expose ports
EXPOSE 8000 8501

# Environment
ENV PYTHONUNBUFFERED=1
ENV PYTHONPATH=/app

# Default: start API
CMD ["python", "main.py", "api", "--api-port", "8000"]

# ───────────────────────────────────────────────────────────────────────────
# Build examples:
#   docker build -t poc-07-airflow .
#   docker run -p 8000:8000 poc-07-airflow                    # API only
#   docker run -p 8501:8501 poc-07-airflow python main.py ui  # UI only
# ───────────────────────────────────────────────────────────────────────────
