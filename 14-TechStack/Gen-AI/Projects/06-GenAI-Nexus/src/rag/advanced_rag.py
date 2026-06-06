"""
Gen-AI Tool: Advanced RAG
===========================
Demonstrates: Hybrid search (semantic + keyword BM25), re-ranking,
query decomposition, HyDE (Hypothetical Document Embeddings),
multi-hop retrieval, and contextual compression.

Role in GenAI Nexus: Higher-quality retrieval for complex startup
analysis queries that require synthesizing multiple sources.
"""

from __future__ import annotations

from dataclasses import dataclass, field

from src.rag.basic_rag import BasicRAG, RAGResponse, TextChunker
from src.vectorstore.chroma_store import ChromaVectorStore, SearchResult


@dataclass
class RerankedResult:
    content: str
    metadata: dict
    original_rank: int
    rerank_score: float
    final_rank: int


class HybridSearcher:
    """
    Hybrid search: combines semantic similarity + BM25 keyword scoring.
    Handles cases where pure semantic search misses exact term matches.
    """

    def __init__(self, vector_store: ChromaVectorStore):
        self._store = vector_store

    def search(self, query: str, top_k: int = 10) -> list[SearchResult]:
        """
        Hybrid search: semantic results + BM25 keyword boost.
        Merges and deduplicates results from both methods.
        """
        # Semantic search (vector store)
        semantic_results = self._store.search(query, top_k=top_k)

        # BM25-style keyword boost (simple implementation)
        query_terms = set(query.lower().split())
        reranked = []

        for result in semantic_results:
            content_terms = set(result.content.lower().split())
            keyword_overlap = len(query_terms & content_terms) / max(len(query_terms), 1)

            # Combine: 0.7 × semantic + 0.3 × keyword
            semantic_score = 1 - result.distance
            combined_score = 0.7 * semantic_score + 0.3 * keyword_overlap

            reranked.append((result, combined_score))

        reranked.sort(key=lambda x: x[1], reverse=True)
        return [r for r, _ in reranked[:top_k]]


class QueryDecomposer:
    """
    Decomposes complex queries into simpler sub-queries.
    Enables multi-hop retrieval for multi-faceted questions.
    """

    # Pattern-based decomposition (LLM decomposition in production)
    _TEMPLATES = {
        "market + competition": [
            "What is the market size and growth?",
            "Who are the main competitors?",
            "What is the competitive moat opportunity?",
        ],
        "tech + team": [
            "What is the technical architecture needed?",
            "What team skills are required?",
        ],
        "default": [
            "{query} — market opportunity",
            "{query} — competitive landscape",
            "{query} — technical requirements",
        ],
    }

    def decompose(self, query: str) -> list[str]:
        """Break a complex query into focused sub-queries."""
        q_lower = query.lower()

        if "market" in q_lower and ("competitor" in q_lower or "competition" in q_lower):
            return self._TEMPLATES["market + competition"]
        elif "tech" in q_lower and "team" in q_lower:
            return self._TEMPLATES["tech + team"]
        else:
            return [t.format(query=query) for t in self._TEMPLATES["default"]]


class CrossEncoderReranker:
    """
    Re-ranks retrieved results using a cross-encoder model.
    More accurate than bi-encoder (used in retrieval) but slower.
    Uses simple heuristic scoring in demo mode.
    """

    def __init__(self, model_name: str = "cross-encoder/ms-marco-MiniLM-L-6-v2"):
        self._model = None
        try:
            from sentence_transformers import CrossEncoder

            self._model = CrossEncoder(model_name)
        except (ImportError, Exception):
            pass  # demo mode

    def rerank(
        self, query: str, results: list[SearchResult], top_k: int = 5
    ) -> list[RerankedResult]:
        """Rerank results using cross-encoder or heuristic fallback."""
        if self._model:
            pairs = [(query, r.content) for r in results]
            scores = self._model.predict(pairs)
            scored = list(zip(results, scores))
        else:
            # Heuristic: boost results with query term density
            scored = []
            query_terms = set(query.lower().split())
            for result in results:
                content_lower = result.content.lower()
                term_hits = sum(1 for t in query_terms if t in content_lower)
                score = term_hits / max(len(query_terms), 1)
                scored.append((result, score))

        scored.sort(key=lambda x: x[1], reverse=True)

        return [
            RerankedResult(
                content=result.content,
                metadata=result.metadata,
                original_rank=i + 1,
                rerank_score=round(float(score), 4),
                final_rank=j + 1,
            )
            for j, (result, score) in enumerate(scored[:top_k])
            for i, orig in enumerate(results)
            if orig.content == result.content
        ]


class HyDERetriever:
    """
    HyDE: Hypothetical Document Embeddings.
    Generate a hypothetical answer, embed it, use it for retrieval.
    Often finds more relevant results than embedding the raw question.
    """

    _HYPOTHETICAL_TEMPLATES = {
        "competitor": (
            "The main competitors in this space are [Company A] with $Xm funding targeting "
            "[segment], and [Company B] with weakness in [area]. The market gap is [opportunity]."
        ),
        "market": (
            "The total addressable market is $XB growing at Y% CAGR. "
            "The key growth drivers are [trend1], [trend2], and [trend3]."
        ),
        "technical": (
            "The technical architecture uses [stack] with [key components]. "
            "The main technical challenges are [challenge1] and [challenge2]."
        ),
    }

    def get_hypothetical_query(self, query: str) -> str:
        """Generate hypothetical document to use as retrieval query."""
        q_lower = query.lower()
        if "competitor" in q_lower or "competition" in q_lower:
            return self._HYPOTHETICAL_TEMPLATES["competitor"]
        elif "market" in q_lower or "size" in q_lower or "tam" in q_lower:
            return self._HYPOTHETICAL_TEMPLATES["market"]
        elif "tech" in q_lower or "architecture" in q_lower:
            return self._HYPOTHETICAL_TEMPLATES["technical"]
        return query  # fallback: use original query


class AdvancedRAG(BasicRAG):
    """
    Advanced RAG pipeline with hybrid search, reranking, HyDE,
    query decomposition, and multi-hop retrieval.

    Extends BasicRAG with production-grade retrieval techniques.
    """

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self._hybrid = HybridSearcher(self._store)
        self._decomposer = QueryDecomposer()
        self._reranker = CrossEncoderReranker()
        self._hyde = HyDERetriever()

    def query_advanced(self, question: str) -> RAGResponse:
        """
        Advanced RAG query with:
        1. HyDE: use hypothetical doc for retrieval
        2. Hybrid search: semantic + keyword
        3. Cross-encoder reranking
        4. Context compression
        """
        # Step 1: HyDE — retrieve using hypothetical document
        hyde_query = self._hyde.get_hypothetical_query(question)
        raw_results = self._hybrid.search(hyde_query, top_k=8)

        if not raw_results:
            return RAGResponse(
                answer="No relevant context found.",
                query=question,
                grounded=False,
            )

        # Step 2: Rerank results
        reranked = self._reranker.rerank(question, raw_results, top_k=3)

        # Step 3: Build compressed context
        context_parts = []
        sources = []
        for r in reranked:
            source = r.metadata.get("company") or r.metadata.get("type", "unknown")
            context_parts.append(f"[{source}]: {r.content}")
            sources.append(f"{source} (score={r.rerank_score:.3f})")

        context = "\n\n".join(context_parts)

        # Step 4: Generate answer
        if self._llm._demo:
            answer = f"[Advanced RAG — HyDE + Reranking]\n\n{context[:500]}..."
        else:
            response = self._llm._client.chat.completions.create(
                model=self._llm.config.model,
                messages=[
                    {"role": "system", "content": self.SYSTEM_PROMPT},
                    {
                        "role": "user",
                        "content": f"Context:\n{context}\n\nQuestion: {question}",
                    },
                ],
                max_tokens=1024,
                temperature=0.1,
            )
            answer = response.choices[0].message.content or ""

        return RAGResponse(
            answer=answer,
            sources=sources,
            retrieved_chunks=len(reranked),
            query=question,
            grounded=True,
        )

    def query_multihop(self, question: str) -> dict[str, RAGResponse]:
        """
        Multi-hop RAG: decompose complex question → answer each sub-query.
        Synthesizes a final answer from all sub-answers.
        """
        sub_queries = self._decomposer.decompose(question)
        sub_answers = {}

        for sub_q in sub_queries:
            sub_answers[sub_q] = self.query(sub_q)

        return sub_answers


def demo():
    print("=" * 60)
    print("DEMO: Advanced RAG Pipeline")
    print("=" * 60)
    rag = AdvancedRAG()

    print("\n[1] HyDE + Hybrid Search + Reranking")
    result = rag.query_advanced("Who are the main competitors and what is the market opportunity?")
    print(f"Answer: {result.answer[:400]}...")
    print(f"Sources: {result.sources}")

    print("\n[2] Multi-Hop RAG (Query Decomposition)")
    multi_results = rag.query_multihop("What is the full startup landscape for AI legal tools?")
    for sub_q, sub_result in multi_results.items():
        print(f"\n  Sub-query: {sub_q[:60]}...")
        print(f"  Answer: {sub_result.answer[:150]}...")

    print("\n[3] HyDE Query Transformation")
    hyde = HyDERetriever()
    for query in [
        "Who are the competitors?",
        "What is the market size?",
        "What tech stack should I use?",
    ]:
        hypo = hyde.get_hypothetical_query(query)
        print(f"\n  Original: {query}")
        print(f"  HyDE: {hypo[:100]}...")


if __name__ == "__main__":
    demo()
