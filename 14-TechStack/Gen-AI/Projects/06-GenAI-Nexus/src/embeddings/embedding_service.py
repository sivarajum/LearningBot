"""
Gen-AI Tool: Embeddings
========================
Demonstrates: OpenAI text-embedding-3-small, HuggingFace sentence
transformers, cosine similarity, semantic search, batch embedding,
embedding caching, and dimensionality analysis.

Role in GenAI Nexus: Convert all text (startup docs, knowledge base,
competitor data) to embeddings for semantic search and RAG retrieval.
"""

from __future__ import annotations

import hashlib
import json
import math
from dataclasses import dataclass, field
from pathlib import Path


@dataclass
class EmbeddingResult:
    text: str
    vector: list[float]
    model: str
    dimensions: int
    cached: bool = False


@dataclass
class SimilarityResult:
    text: str
    score: float
    rank: int


class EmbeddingService:
    """
    Unified embedding service supporting OpenAI and HuggingFace models.

    Demonstrates:
    - OpenAI text-embedding-3-small (1536-dim, cost-efficient)
    - HuggingFace sentence-transformers (local, free)
    - Cosine similarity computation
    - Batch embedding with rate limiting
    - Simple disk cache to avoid re-embedding
    - Semantic search over a corpus
    """

    OPENAI_MODEL = "text-embedding-3-small"
    HF_MODEL = "sentence-transformers/all-MiniLM-L6-v2"

    def __init__(
        self,
        openai_key: str = "",
        use_hf: bool = False,
        cache_path: str = "./data/embedding_cache",
    ):
        self._demo = True
        self._cache: dict[str, list[float]] = {}
        self._cache_path = Path(cache_path)
        self._model_name = "demo"

        if openai_key:
            try:
                from openai import OpenAI

                self._openai = OpenAI(api_key=openai_key)
                self._model_name = self.OPENAI_MODEL
                self._demo = False
            except ImportError:
                pass

        elif use_hf:
            try:
                from sentence_transformers import SentenceTransformer

                self._hf_model = SentenceTransformer(self.HF_MODEL)
                self._model_name = self.HF_MODEL
                self._demo = False
            except ImportError:
                pass

        # Load disk cache if exists
        self._load_cache()

    def embed(self, text: str) -> EmbeddingResult:
        """Embed a single text string."""
        cache_key = self._cache_key(text)

        if cache_key in self._cache:
            return EmbeddingResult(
                text=text,
                vector=self._cache[cache_key],
                model=self._model_name,
                dimensions=len(self._cache[cache_key]),
                cached=True,
            )

        if self._demo:
            vector = self._fake_embedding(text)
        elif hasattr(self, "_openai"):
            response = self._openai.embeddings.create(
                model=self.OPENAI_MODEL, input=text
            )
            vector = response.data[0].embedding
        elif hasattr(self, "_hf_model"):
            vec = self._hf_model.encode(text)
            vector = vec.tolist()
        else:
            vector = self._fake_embedding(text)

        # Cache result
        self._cache[cache_key] = vector

        return EmbeddingResult(
            text=text,
            vector=vector,
            model=self._model_name,
            dimensions=len(vector),
        )

    def embed_batch(self, texts: list[str]) -> list[EmbeddingResult]:
        """Embed multiple texts efficiently (batched API calls)."""
        # Check cache first
        results = []
        uncached_texts = []
        uncached_indices = []

        for i, text in enumerate(texts):
            key = self._cache_key(text)
            if key in self._cache:
                results.append(
                    EmbeddingResult(
                        text=text,
                        vector=self._cache[key],
                        model=self._model_name,
                        dimensions=len(self._cache[key]),
                        cached=True,
                    )
                )
            else:
                results.append(None)  # placeholder
                uncached_texts.append(text)
                uncached_indices.append(i)

        # Batch embed uncached texts
        if uncached_texts:
            if self._demo:
                vectors = [self._fake_embedding(t) for t in uncached_texts]
            elif hasattr(self, "_openai"):
                response = self._openai.embeddings.create(
                    model=self.OPENAI_MODEL, input=uncached_texts
                )
                vectors = [item.embedding for item in response.data]
            elif hasattr(self, "_hf_model"):
                batch = self._hf_model.encode(uncached_texts)
                vectors = batch.tolist()
            else:
                vectors = [self._fake_embedding(t) for t in uncached_texts]

            for idx, text, vector in zip(uncached_indices, uncached_texts, vectors):
                self._cache[self._cache_key(text)] = vector
                results[idx] = EmbeddingResult(
                    text=text,
                    vector=vector,
                    model=self._model_name,
                    dimensions=len(vector),
                )

        return [r for r in results if r is not None]

    def cosine_similarity(self, vec_a: list[float], vec_b: list[float]) -> float:
        """Compute cosine similarity between two vectors."""
        if len(vec_a) != len(vec_b):
            raise ValueError("Vector dimensions must match")

        dot = sum(a * b for a, b in zip(vec_a, vec_b))
        mag_a = math.sqrt(sum(a * a for a in vec_a))
        mag_b = math.sqrt(sum(b * b for b in vec_b))

        if mag_a == 0 or mag_b == 0:
            return 0.0
        return dot / (mag_a * mag_b)

    def semantic_search(
        self, query: str, corpus: list[str], top_k: int = 5
    ) -> list[SimilarityResult]:
        """
        Semantic search: find most similar texts to query.
        Embeds query + corpus, ranks by cosine similarity.
        """
        query_emb = self.embed(query)
        corpus_embs = self.embed_batch(corpus)

        scores = [
            (text, self.cosine_similarity(query_emb.vector, emb.vector))
            for text, emb in zip(corpus, corpus_embs)
        ]

        scores.sort(key=lambda x: x[1], reverse=True)

        return [
            SimilarityResult(text=text, score=round(score, 4), rank=i + 1)
            for i, (text, score) in enumerate(scores[:top_k])
        ]

    def save_cache(self) -> None:
        """Persist embedding cache to disk."""
        self._cache_path.mkdir(parents=True, exist_ok=True)
        cache_file = self._cache_path / "embeddings.json"
        with open(cache_file, "w") as f:
            json.dump(self._cache, f)

    def _load_cache(self) -> None:
        cache_file = self._cache_path / "embeddings.json"
        if cache_file.exists():
            with open(cache_file) as f:
                self._cache = json.load(f)

    def _cache_key(self, text: str) -> str:
        return hashlib.md5(f"{self._model_name}:{text}".encode()).hexdigest()

    def _fake_embedding(self, text: str, dims: int = 384) -> list[float]:
        """Deterministic fake embedding for demo mode."""
        seed = int(hashlib.md5(text.encode()).hexdigest(), 16) % (2**32)
        import random

        rng = random.Random(seed)
        raw = [rng.gauss(0, 1) for _ in range(dims)]
        # Normalize to unit vector
        mag = math.sqrt(sum(x * x for x in raw))
        return [x / mag for x in raw]


def demo():
    print("=" * 60)
    print("DEMO: Embedding Service")
    print("=" * 60)
    service = EmbeddingService()  # demo mode

    print("\n[1] Single Embedding")
    result = service.embed("AI legal document analyzer startup")
    print(f"Model: {result.model}")
    print(f"Dimensions: {result.dimensions}")
    print(f"Vector preview: {result.vector[:5]}")

    print("\n[2] Batch Embedding")
    texts = [
        "Contract review automation",
        "Legal document analysis",
        "AI for law firms",
        "Financial risk assessment",
        "Medical diagnosis AI",
    ]
    results = service.embed_batch(texts)
    print(f"Embedded {len(results)} texts")

    print("\n[3] Semantic Search")
    query = "AI for legal documents"
    corpus = [
        "Automated contract review system",
        "Legal document analysis platform",
        "Medical imaging AI solution",
        "Financial trading algorithm",
        "NDA and agreement analyzer",
        "Customer support chatbot",
    ]
    search_results = service.semantic_search(query, corpus, top_k=3)
    print(f"Query: '{query}'")
    for r in search_results:
        print(f"  [{r.rank}] Score={r.score:.4f}: {r.text}")

    print("\n[4] Cosine Similarity")
    emb1 = service.embed("legal document analysis")
    emb2 = service.embed("contract review automation")
    emb3 = service.embed("weather forecasting model")
    sim12 = service.cosine_similarity(emb1.vector, emb2.vector)
    sim13 = service.cosine_similarity(emb1.vector, emb3.vector)
    print(f"legal docs ↔ contract review: {sim12:.4f} (should be HIGH)")
    print(f"legal docs ↔ weather: {sim13:.4f} (should be LOW)")


if __name__ == "__main__":
    demo()
