# GCP Production Variant: Vertex AI Embeddings + Vector Search

This document shows the exact code changes needed to move the POC from its local
ChromaDB + sentence-transformers setup to a production-grade GCP stack.

---

## SDK swap summary

| Local (POC) | GCP Production |
|-------------|---------------|
| `sentence_transformers.SentenceTransformer` | `langchain_google_vertexai.VertexAIEmbeddings` |
| `chromadb.PersistentClient` | `langchain_google_vertexai.VectorSearchVectorStore` (Vertex AI Vector Search) |
| Local SQLite persistence | Managed index on Google Cloud |
| Free (CPU only) | ~$0.000025/1K chars + ~$0.65/hour per Vector Search node |

---

## 1. Embedding: SentenceTransformer → VertexAIEmbeddings

### Local (current)

```python
# src/embeddings.py
from sentence_transformers import SentenceTransformer

EMBEDDING_MODEL = "all-MiniLM-L6-v2"

class VectorStore:
    def _build_embedding_fn(self):
        return SentenceTransformer(EMBEDDING_MODEL)

    def _embed(self, texts: list[str]) -> list[list[float]]:
        embeddings = self._embedding_fn.encode(texts, show_progress_bar=False)
        return embeddings.tolist()
```

### GCP Production

```python
# src/embeddings_gcp.py
from langchain_google_vertexai import VertexAIEmbeddings

# text-embedding-004 produces 768-dimensional vectors.
# Requires: pip install langchain-google-vertexai
# Auth: GOOGLE_APPLICATION_CREDENTIALS or Workload Identity on GKE/Cloud Run.
EMBEDDING_MODEL = "text-embedding-004"

embedding_fn = VertexAIEmbeddings(model_name=EMBEDDING_MODEL)

# Usage — same interface as sentence-transformers:
vectors: list[list[float]] = embedding_fn.embed_documents(texts)
query_vector: list[float] = embedding_fn.embed_query(query_text)
```

The `VertexAIEmbeddings` class handles batching, retries, and quota management
automatically. Dimension is 768 (vs 384 for `all-MiniLM-L6-v2`) — you will need
to recreate the Vector Search index if migrating an existing index.

---

## 2. Vector store: ChromaDB → Vertex AI Vector Search

### Local (current)

```python
# src/embeddings.py
import chromadb

class VectorStore:
    def __init__(self, persist_dir: str = "./data/chroma_db"):
        self.client = chromadb.PersistentClient(path=persist_dir)
        self.collection = self.client.get_or_create_collection(
            name="rag_documents",
            metadata={"hnsw:space": "cosine"},
        )
```

### GCP Production

```python
# src/embeddings_gcp.py
from google.cloud import aiplatform
from langchain_google_vertexai import VectorSearchVectorStore, VertexAIEmbeddings

# Prerequisites (one-time setup via gcloud or Terraform):
#   1. Create a Vector Search Index with dimensions=768, distanceMeasureType=COSINE
#   2. Deploy the index to an IndexEndpoint
#   3. Note the INDEX_ID and INDEX_ENDPOINT_ID from the Cloud Console

GCP_PROJECT = "your-gcp-project-id"
GCP_REGION = "us-central1"
GCS_BUCKET = "your-bucket-for-vector-search"   # used for batch index updates
INDEX_ID = "projects/.../indexes/YOUR_INDEX_ID"
INDEX_ENDPOINT_ID = "projects/.../indexEndpoints/YOUR_ENDPOINT_ID"

aiplatform.init(project=GCP_PROJECT, location=GCP_REGION)

embedding_fn = VertexAIEmbeddings(model_name="text-embedding-004")

vector_store = VectorSearchVectorStore.from_components(
    project_id=GCP_PROJECT,
    region=GCP_REGION,
    gcs_bucket_name=GCS_BUCKET,
    index_id=INDEX_ID,
    endpoint_id=INDEX_ENDPOINT_ID,
    embedding=embedding_fn,
    stream_update=True,   # True = streaming updates; False = batch (cheaper for bulk)
)

# Adding documents — same interface as the local VectorStore:
vector_store.add_documents(docs)

# Similarity search — returns LangChain Document objects:
results = vector_store.similarity_search_with_score(query_text, k=5)
```

---

## 3. rag_pipeline.py changes

The `query()` function in `src/rag_pipeline.py` calls `vector_store.similarity_search()`.
Replace the `VectorStore` import with `VectorSearchVectorStore` and the return format
changes slightly — LangChain's `similarity_search_with_score` returns
`list[tuple[Document, float]]` instead of `list[dict]`.

```python
# Adapter to keep rag_pipeline.py interface unchanged:
chunks = [
    {
        "content": doc.page_content,
        "metadata": doc.metadata,
        "score": score,
    }
    for doc, score in vector_store.similarity_search_with_score(question, k=k)
]
```

---

## 4. Authentication

On Cloud Run or GKE, use Workload Identity — no key files needed:

```bash
gcloud iam service-accounts create rag-sa
gcloud projects add-iam-policy-binding YOUR_PROJECT \
  --member="serviceAccount:rag-sa@YOUR_PROJECT.iam.gserviceaccount.com" \
  --role="roles/aiplatform.user"
# Bind to Cloud Run service or GKE service account via Workload Identity
```

Locally during development:

```bash
gcloud auth application-default login
```

---

## 5. Cost note

| Resource | Cost (approximate) |
|----------|-------------------|
| Vertex AI Embeddings (`text-embedding-004`) | ~$0.000025 / 1K characters |
| Vector Search node (e2-standard-2) | ~$0.65 / hour (always-on) |
| Vector Search — queries | Included in node cost |
| Vector Search — batch index updates | $0.20 / GB processed |

For a POC with infrequent queries, consider deploying the index endpoint only
during business hours using Cloud Scheduler to start/stop the node, which can
reduce node costs by ~65%.

For read-heavy production workloads, a 2-node deployment behind a load balancer
provides HA and handles ~1,000 QPS per node.

---

## 6. Local → GCP migration checklist

- [ ] Create GCP project and enable `aiplatform.googleapis.com` API
- [ ] Create a GCS bucket in the same region as Vector Search
- [ ] Create Vector Search Index (768 dims, COSINE distance, streaming updates enabled)
- [ ] Deploy index to an IndexEndpoint
- [ ] Update `src/embeddings_gcp.py` with project/region/index IDs
- [ ] Re-embed existing documents with `text-embedding-004` (vectors are not compatible)
- [ ] Update `rag_pipeline.py` with the chunk adapter (section 3 above)
- [ ] Set up Workload Identity or service account key for auth
- [ ] Add `langchain-google-vertexai` to `requirements.txt`
