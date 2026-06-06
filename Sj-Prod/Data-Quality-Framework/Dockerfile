FROM python:3.11-slim

LABEL maintainer="Lead Data Engineer"
LABEL description="POC-09: Enterprise Data Quality Framework"

# Set working directory
WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements first (layer caching)
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy project files
COPY . .

# Create data and reports directories
RUN mkdir -p data reports

# Expose ports: 8000 (FastAPI), 8501 (Streamlit)
EXPOSE 8000 8501

# Default: run validation + start API
CMD ["python", "main.py", "validate"]
