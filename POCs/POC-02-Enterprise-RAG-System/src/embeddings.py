"""Vector store: embed documents and perform similarity search using ChromaDB."""

import hashlib
import os
from typing import Optional

import chromadb
from chromadb.config import Settings
from langchain.schema import Document


# Use a lightweight, free model -- no API key required
EMBEDDING_MODEL = "all-MiniLM-L6-v2"
COLLECTION_NAME = "rag_documents"


class VectorStore:
    """ChromaDB-backed vector store with sentence-transformer embeddings."""

    def __init__(self, persist_dir: Optional[str] = None):
        self.persist_dir = persist_dir or os.getenv(
            "CHROMA_DB_PATH", "./data/chroma_db"
        )
        self.client = chromadb.PersistentClient(path=self.persist_dir)
        self._embedding_fn = self._build_embedding_fn()
        self.collection = self.client.get_or_create_collection(
            name=COLLECTION_NAME,
            metadata={"hnsw:space": "cosine"},
        )

    def _build_embedding_fn(self):
        """Load the sentence-transformers model once."""
        from sentence_transformers import SentenceTransformer
        return SentenceTransformer(EMBEDDING_MODEL)

    def _embed(self, texts: list[str]) -> list[list[float]]:
        """Generate embeddings for a list of texts."""
        embeddings = self._embedding_fn.encode(texts, show_progress_bar=False)
        return embeddings.tolist()

    def add_documents(self, docs: list[Document]) -> int:
        """Embed and store documents. Returns the number of chunks added."""
        if not docs:
            return 0

        texts = [doc.page_content for doc in docs]
        metadatas = [doc.metadata for doc in docs]
        embeddings = self._embed(texts)

        # Content-based hashing for idempotent re-ingest
        ids = [
            hashlib.sha256(doc.page_content.encode()).hexdigest()[:16]
            for doc in docs
        ]

        self.collection.upsert(
            ids=ids,
            documents=texts,
            embeddings=embeddings,
            metadatas=metadatas,
        )
        return len(docs)

    def similarity_search(
        self, query: str, k: int = 5
    ) -> list[dict]:
        """Find the k most similar chunks to the query.

        Returns:
            List of dicts with keys: content, metadata, score.
        """
        if self.collection.count() == 0:
            return []

        query_embedding = self._embed([query])[0]
        results = self.collection.query(
            query_embeddings=[query_embedding],
            n_results=min(k, self.collection.count()),
            include=["documents", "metadatas", "distances"],
        )

        hits: list[dict] = []
        for i in range(len(results["ids"][0])):
            # ChromaDB cosine distance is in [0, 2]; convert to similarity
            distance = results["distances"][0][i]
            similarity = 1.0 - (distance / 2.0)
            hits.append({
                "content": results["documents"][0][i],
                "metadata": results["metadatas"][0][i],
                "score": round(similarity, 4),
            })
        return hits

    def get_stats(self) -> dict:
        """Return collection statistics."""
        count = self.collection.count()
        return {
            "collection": COLLECTION_NAME,
            "total_chunks": count,
            "embedding_model": EMBEDDING_MODEL,
            "persist_dir": self.persist_dir,
        }

    def reset(self) -> None:
        """Delete all documents from the collection."""
        self.client.delete_collection(COLLECTION_NAME)
        self.collection = self.client.get_or_create_collection(
            name=COLLECTION_NAME,
            metadata={"hnsw:space": "cosine"},
        )
