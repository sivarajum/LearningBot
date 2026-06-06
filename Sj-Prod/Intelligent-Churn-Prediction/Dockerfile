FROM python:3.11-slim

WORKDIR /app

# Install dependencies first (layer caching)
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy source code
COPY src/ src/
COPY data/ data/

# Pre-train model during build so containers start instantly
RUN python -m src.pipeline

EXPOSE 8000 8501
