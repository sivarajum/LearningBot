"""Vector store: embed documents and perform similarity search using ChromaDB."""

import hashlib
import logging

import chromadb
from langchain_core.documents import Document

from src.settings import CHROMA_DB_PATH, EMBEDDING_MODEL

logger = logging.getLogger(__name__)

COLLECTION_NAME: str = "rag_documents"


class VectorStore:
    """ChromaDB-backed vector store with sentence-transformer embeddings."""

    def __init__(self, persist_dir: str | None = None) -> None:
        self.persist_dir = persist_dir or CHROMA_DB_PATH
        logger.info("Initializing VectorStore at %s", self.persist_dir)
        self.client = chromadb.PersistentClient(path=self.persist_dir)
        self._embedding_fn = self._build_embedding_fn()
        self.collection = self.client.get_or_create_collection(
            name=COLLECTION_NAME,
            metadata={"hnsw:space": "cosine"},
        )
        logger.info(
            "VectorStore ready: collection=%s, existing_chunks=%d",
            COLLECTION_NAME,
            self.collection.count(),
        )

    def _build_embedding_fn(self):  # noqa: ANN202 — returns SentenceTransformer
        """Load the sentence-transformers model once."""
        logger.info("Loading embedding model: %s", EMBEDDING_MODEL)
        from sentence_transformers import SentenceTransformer

        return SentenceTransformer(EMBEDDING_MODEL)

    def _embed(self, texts: list[str]) -> list[list[float]]:
        """Generate embeddings for a list of texts."""
        logger.debug("Embedding %d text(s)", len(texts))
        embeddings = self._embedding_fn.encode(texts, show_progress_bar=False)
        return embeddings.tolist()

    def add_documents(self, docs: list[Document]) -> int:
        """Embed and store documents. Returns the number of chunks added."""
        if not docs:
            return 0

        texts = [doc.page_content for doc in docs]
        metadatas = [doc.metadata for doc in docs]

        logger.info("Embedding %d document chunks", len(docs))
        embeddings = self._embed(texts)

        # Content-based hashing for idempotent re-ingest
        ids = [hashlib.sha256(doc.page_content.encode()).hexdigest()[:16] for doc in docs]

        self.collection.upsert(
            ids=ids,
            documents=texts,
            embeddings=embeddings,
            metadatas=metadatas,
        )
        logger.info("Upserted %d chunks into collection '%s'", len(docs), COLLECTION_NAME)
        return len(docs)

    def similarity_search(self, query: str, k: int = 5) -> list[dict]:
        """Find the k most similar chunks to the query.

        Returns:
            List of dicts with keys: content, metadata, score.
        """
        if self.collection.count() == 0:
            logger.warning("Similarity search on empty collection; returning empty results")
            return []

        logger.debug("Similarity search: query=%r, k=%d", query[:80], k)
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
            hits.append(
                {
                    "content": results["documents"][0][i],
                    "metadata": results["metadatas"][0][i],
                    "score": round(similarity, 4),
                }
            )
        logger.debug("Returned %d hits", len(hits))
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
        logger.warning("Resetting collection '%s' -- all documents will be deleted", COLLECTION_NAME)
        self.client.delete_collection(COLLECTION_NAME)
        self.collection = self.client.get_or_create_collection(
            name=COLLECTION_NAME,
            metadata={"hnsw:space": "cosine"},
        )
