"""
Gen-AI Tool: RAG (Retrieval-Augmented Generation)
===================================================
Demonstrates: Basic RAG pipeline — retrieve relevant context from
vector store, inject into LLM prompt, generate grounded answer.
Covers: chunking, retrieval, context injection, citation tracking.

Role in GenAI Nexus: Ground startup analysis in real data (competitor
reports, market research) rather than LLM hallucinations.
"""

from __future__ import annotations

from dataclasses import dataclass, field

from src.llm.openai_client import OpenAIClient
from src.vectorstore.chroma_store import ChromaVectorStore, Document


def _get_local_llm():
    """Try to create an Ollama client for local RAG generation."""
    try:
        from config.settings import settings

        if settings.has_local_llm:
            from src.llm.ollama_client import OllamaClient

            return OllamaClient()
    except Exception:
        pass
    return None


@dataclass
class RAGResponse:
    """RAG pipeline output with sources."""

    answer: str
    sources: list[str] = field(default_factory=list)
    retrieved_chunks: int = 0
    query: str = ""
    grounded: bool = True


class TextChunker:
    """
    Splits long documents into overlapping chunks for better retrieval.
    Demonstrates: fixed-size chunking, sentence-aware splitting, overlap.
    """

    def __init__(self, chunk_size: int = 500, overlap: int = 50):
        self.chunk_size = chunk_size
        self.overlap = overlap

    def chunk_text(self, text: str, metadata: dict | None = None) -> list[Document]:
        """Split text into overlapping chunks."""
        metadata = metadata or {}

        if len(text) <= self.chunk_size:
            return [Document(content=text, metadata={**metadata, "chunk_index": 0})]

        chunks = []
        start = 0
        chunk_index = 0

        while start < len(text):
            end = start + self.chunk_size

            # Try to break at sentence boundary
            if end < len(text):
                period = text.rfind(".", start, end)
                if period > start + self.chunk_size // 2:
                    end = period + 1

            chunk_text = text[start:end].strip()
            if chunk_text:
                chunks.append(
                    Document(
                        content=chunk_text,
                        metadata={**metadata, "chunk_index": chunk_index},
                    )
                )
                chunk_index += 1

            start = end - self.overlap  # overlap

        return chunks

    def chunk_documents(self, documents: list[tuple[str, dict]]) -> list[Document]:
        """Chunk multiple documents."""
        all_chunks = []
        for text, metadata in documents:
            all_chunks.extend(self.chunk_text(text, metadata))
        return all_chunks


class BasicRAG:
    """
    Basic RAG pipeline: retrieve → augment → generate.

    Demonstrates:
    - Document ingestion and chunking
    - Retrieval from vector store
    - Context injection into LLM prompt
    - Grounded response generation
    - Source attribution
    """

    SYSTEM_PROMPT = """You are a startup advisor grounded in real market data.
Answer questions ONLY based on the provided context.
If the context doesn't contain the answer, say "I don't have data on this."
Always cite specific facts from the context.
Never make up statistics or company information."""

    def __init__(
        self,
        vector_store: ChromaVectorStore | None = None,
        llm: OpenAIClient | None = None,
        top_k: int = 3,
    ):
        self._store = vector_store or ChromaVectorStore()
        self._llm = llm or OpenAIClient()
        self._local_llm = _get_local_llm()
        self._chunker = TextChunker()
        self._top_k = top_k

        # Load default knowledge base
        self._store.load_knowledge_base()

    def ingest(self, documents: list[tuple[str, dict]]) -> int:
        """Ingest and chunk documents into vector store."""
        chunks = self._chunker.chunk_documents(documents)
        return self._store.add_documents(chunks)

    def query(self, question: str, filter_by_type: str | None = None) -> RAGResponse:
        """
        Main RAG query: retrieve relevant context, generate grounded answer.

        Args:
            question: User's question about the startup
            filter_by_type: Optional filter (e.g., "competitor", "market_data")
        """
        # Step 1: Retrieve relevant chunks
        if filter_by_type:
            retrieved = self._store.search_by_type(question, filter_by_type, self._top_k)
        else:
            retrieved = self._store.search(question, self._top_k)

        if not retrieved:
            return RAGResponse(
                answer="No relevant information found in the knowledge base.",
                query=question,
                grounded=False,
            )

        # Step 2: Build context from retrieved chunks
        context_parts = []
        sources = []
        for i, result in enumerate(retrieved, 1):
            source_label = result.metadata.get("company") or result.metadata.get("type", "unknown")
            context_parts.append(f"[Source {i} — {source_label}]:\n{result.content}")
            sources.append(f"Source {i}: {source_label} (relevance={1 - result.distance:.2f})")

        context = "\n\n".join(context_parts)

        # Step 3: Generate answer grounded in context
        augmented_prompt = f"""Based on the following context, answer the question.

CONTEXT:
{context}

QUESTION: {question}

Provide a specific, data-backed answer. Reference the sources by number."""

        if self._local_llm and not self._local_llm._demo:
            # Use local Ollama LLM for generation
            response = self._local_llm._chat(
                model=self._local_llm.config.default_model,
                system=self.SYSTEM_PROMPT,
                user=augmented_prompt,
            )
            answer = response.content
        elif self._llm._demo:
            # Demo mode: use context directly
            answer = f"""Based on retrieved data:

{context[:400]}

[Additional sources available — {len(retrieved)} chunks retrieved]"""
        else:
            response = self._llm._client.chat.completions.create(
                model=self._llm.config.model,
                messages=[
                    {"role": "system", "content": self.SYSTEM_PROMPT},
                    {"role": "user", "content": augmented_prompt},
                ],
                max_tokens=1024,
                temperature=0.1,  # Low temperature for factual RAG
            )
            answer = response.choices[0].message.content or ""

        return RAGResponse(
            answer=answer,
            sources=sources,
            retrieved_chunks=len(retrieved),
            query=question,
            grounded=True,
        )

    def query_competitors(self, startup_idea: str) -> RAGResponse:
        """Convenience: query specifically about competitors."""
        return self.query(
            f"Who are the main competitors for a startup doing: {startup_idea}?",
            filter_by_type="competitor",
        )

    def query_market(self, startup_idea: str) -> RAGResponse:
        """Convenience: query market data."""
        return self.query(
            f"What is the market size and growth for: {startup_idea}?",
            filter_by_type="market_data",
        )


def demo():
    print("=" * 60)
    print("DEMO: Basic RAG Pipeline")
    print("=" * 60)
    rag = BasicRAG()

    # Ingest additional documents
    extra_docs = [
        (
            "Kira Systems was acquired by Litera in 2022. It specialized in due diligence automation "
            "for M&A transactions. Post-acquisition, it became part of Thomson Reuters.",
            {"type": "competitor", "company": "Kira Systems", "domain": "legal_tech"},
        ),
        (
            "Legal AI adoption survey 2024: 73% of law firms plan AI adoption by 2025. "
            "Main use cases: contract review (68%), legal research (54%), billing analysis (31%).",
            {"type": "research", "domain": "legal_tech", "year": 2024},
        ),
    ]
    n = rag.ingest(extra_docs)
    print(f"Ingested {n} additional chunks")

    print("\n[1] General Query")
    result = rag.query("What is the market opportunity for AI legal tools?")
    print(f"Answer: {result.answer[:400]}...")
    print(f"Sources: {result.sources}")

    print("\n[2] Competitor Query (Filtered)")
    result = rag.query_competitors("AI legal document analyzer")
    print(f"Answer: {result.answer[:400]}...")
    print(f"Retrieved {result.retrieved_chunks} chunks")

    print("\n[3] Market Data Query (Filtered)")
    result = rag.query_market("AI legal document analyzer")
    print(f"Answer: {result.answer[:300]}...")


if __name__ == "__main__":
    demo()
