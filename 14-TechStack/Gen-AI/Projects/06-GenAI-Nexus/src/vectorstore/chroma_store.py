"""
Gen-AI Tool: Vector Databases (ChromaDB)
==========================================
Demonstrates: ChromaDB setup, collection management, document ingestion,
metadata filtering, similarity search, hybrid search, persistence.

Role in GenAI Nexus: Store + query all knowledge chunks — startup reports,
competitor data, market research, case studies.
"""

from __future__ import annotations

import hashlib
import uuid
from dataclasses import dataclass, field
from typing import Any


@dataclass
class Document:
    """A document chunk ready for vector storage."""

    content: str
    metadata: dict[str, Any] = field(default_factory=dict)
    doc_id: str = ""

    def __post_init__(self):
        if not self.doc_id:
            self.doc_id = hashlib.md5(self.content.encode()).hexdigest()[:12]


@dataclass
class SearchResult:
    content: str
    metadata: dict[str, Any]
    distance: float
    doc_id: str


# Sample knowledge base for demo
SAMPLE_KNOWLEDGE = [
    Document(
        content="Harvey AI raised $100M Series B for AI legal assistant targeting BigLaw firms. "
        "Focus on large law firms with 500+ attorneys. Pricing starts at $5,000/month.",
        metadata={"type": "competitor", "company": "Harvey AI", "domain": "legal_tech"},
    ),
    Document(
        content="Ironclad raised $333M total for contract lifecycle management. "
        "Strong in Fortune 500 enterprise segment. Weakness: not AI-first, legacy workflow UX.",
        metadata={"type": "competitor", "company": "Ironclad", "domain": "legal_tech"},
    ),
    Document(
        content="Legal technology market TAM is $45.2B in 2024, growing at 18.9% CAGR. "
        "Mid-market segment ($50M-500M revenue firms) is underserved with limited AI tools.",
        metadata={"type": "market_data", "year": 2024, "domain": "legal_tech"},
    ),
    Document(
        content="AI document review reduces manual contract review time by 90%. "
        "Average attorney billable rate: $350-$500/hour. ROI on AI tools: 10-15x in year 1.",
        metadata={"type": "research", "domain": "legal_tech"},
    ),
    Document(
        content="PLG (Product-Led Growth) works well for legal tech. "
        "Firms start with free NDA review, upgrade to full contract suite. "
        "Conversion rate: 15-25% free to paid in legal tech.",
        metadata={"type": "gtm_strategy", "domain": "legal_tech"},
    ),
]


class ChromaVectorStore:
    """
    ChromaDB-backed vector store for startup knowledge.

    Demonstrates:
    - Collection creation and management
    - Document ingestion with metadata
    - Similarity search with filters
    - Metadata filtering (by type, domain, year)
    - Persistence (on-disk ChromaDB)
    - Collection stats and management
    """

    def __init__(self, persist_dir: str = "./data/chroma_db", collection_name: str = "startup_knowledge"):
        self._demo = False
        self._collection_name = collection_name
        self._persist_dir = persist_dir

        # In-memory fallback store for demo
        self._memory_store: list[Document] = []

        try:
            import chromadb

            self._client = chromadb.PersistentClient(path=persist_dir)
            self._collection = self._client.get_or_create_collection(
                name=collection_name,
                metadata={"hnsw:space": "cosine"},
            )
        except (ImportError, Exception):
            self._demo = True
            self._memory_store = list(SAMPLE_KNOWLEDGE)

    def add_documents(self, documents: list[Document]) -> int:
        """Add documents to the vector store."""
        if self._demo:
            self._memory_store.extend(documents)
            return len(documents)

        ids = [doc.doc_id for doc in documents]
        documents_text = [doc.content for doc in documents]
        metadatas = [doc.metadata for doc in documents]

        self._collection.add(
            ids=ids,
            documents=documents_text,
            metadatas=metadatas,
        )
        return len(documents)

    def search(
        self,
        query: str,
        top_k: int = 5,
        filter_metadata: dict | None = None,
    ) -> list[SearchResult]:
        """
        Semantic similarity search with optional metadata filtering.

        ChromaDB where clause example:
        filter_metadata = {"type": "competitor"}
        filter_metadata = {"$and": [{"domain": "legal_tech"}, {"type": "market_data"}]}
        """
        if self._demo:
            return self._demo_search(query, top_k, filter_metadata)

        kwargs: dict[str, Any] = {
            "query_texts": [query],
            "n_results": min(top_k, max(1, len(self._memory_store))),
        }
        if filter_metadata:
            kwargs["where"] = filter_metadata

        results = self._collection.query(**kwargs)

        search_results = []
        for i, (doc, meta, dist) in enumerate(
            zip(
                results["documents"][0],
                results["metadatas"][0],
                results["distances"][0],
            )
        ):
            search_results.append(
                SearchResult(
                    content=doc,
                    metadata=meta,
                    distance=round(dist, 4),
                    doc_id=results["ids"][0][i],
                )
            )

        return search_results

    def search_by_type(self, query: str, doc_type: str, top_k: int = 3) -> list[SearchResult]:
        """Convenience: search only documents of a specific type."""
        return self.search(query, top_k, filter_metadata={"type": doc_type})

    def get_all_metadata(self) -> list[dict]:
        """List all documents' metadata (without vectors)."""
        if self._demo:
            return [doc.metadata for doc in self._memory_store]
        results = self._collection.get()
        return results.get("metadatas", [])

    def count(self) -> int:
        """Total document count in collection."""
        if self._demo:
            return len(self._memory_store)
        return self._collection.count()

    def delete_collection(self) -> None:
        """Drop and recreate the collection."""
        if self._demo:
            self._memory_store = []
            return
        self._client.delete_collection(self._collection_name)
        self._collection = self._client.create_collection(
            name=self._collection_name,
            metadata={"hnsw:space": "cosine"},
        )

    def load_knowledge_base(self) -> int:
        """Load sample startup knowledge base."""
        return self.add_documents(SAMPLE_KNOWLEDGE)

    def _demo_search(
        self, query: str, top_k: int, filter_metadata: dict | None
    ) -> list[SearchResult]:
        """Simple keyword-based search for demo mode."""
        query_words = set(query.lower().split())
        scored = []

        for doc in self._memory_store:
            # Apply metadata filter
            if filter_metadata:
                match = all(
                    doc.metadata.get(k) == v
                    for k, v in filter_metadata.items()
                    if not k.startswith("$")
                )
                if not match:
                    continue

            # Score by word overlap
            doc_words = set(doc.content.lower().split())
            overlap = len(query_words & doc_words)
            score = overlap / max(len(query_words), 1)
            scored.append((doc, score))

        scored.sort(key=lambda x: x[1], reverse=True)

        return [
            SearchResult(
                content=doc.content,
                metadata=doc.metadata,
                distance=round(1 - score, 4),  # distance = 1 - similarity
                doc_id=doc.doc_id,
            )
            for doc, score in scored[:top_k]
        ]


def demo():
    print("=" * 60)
    print("DEMO: ChromaDB Vector Store")
    print("=" * 60)
    store = ChromaVectorStore()

    print("\n[1] Load Knowledge Base")
    n = store.load_knowledge_base()
    print(f"Loaded {n} documents. Total: {store.count()}")

    print("\n[2] Semantic Search")
    results = store.search("legal AI competitors funding", top_k=3)
    for r in results:
        print(f"  Distance={r.distance:.3f} [{r.metadata.get('type')}]: {r.content[:100]}...")

    print("\n[3] Filtered Search — competitors only")
    results = store.search_by_type("AI legal tools", doc_type="competitor", top_k=2)
    for r in results:
        print(f"  {r.metadata.get('company')}: {r.content[:80]}...")

    print("\n[4] Filtered Search — market data only")
    results = store.search_by_type("market size TAM", doc_type="market_data")
    for r in results:
        print(f"  {r.content[:120]}...")

    print("\n[5] All Metadata")
    all_meta = store.get_all_metadata()
    for meta in all_meta:
        print(f"  type={meta.get('type')}, domain={meta.get('domain')}, company={meta.get('company', 'N/A')}")


if __name__ == "__main__":
    demo()
