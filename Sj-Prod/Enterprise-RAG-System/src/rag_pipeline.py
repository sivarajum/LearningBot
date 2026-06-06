"""RAG pipeline: retrieve context and generate answers."""

import logging
import os
from dataclasses import dataclass, field

from src.embeddings import VectorStore

logger = logging.getLogger(__name__)


@dataclass
class RAGResponse:
    """Structured response from the RAG pipeline."""

    answer: str
    sources: list[dict] = field(default_factory=list)
    model_used: str = "extractive-fallback"


def _build_prompt(question: str, context_chunks: list[dict]) -> str:
    """Assemble the RAG prompt from retrieved context and the user question."""
    context_parts: list[str] = []
    for i, chunk in enumerate(context_chunks, 1):
        source = chunk["metadata"].get("source", "unknown")
        context_parts.append(f"[Source {i}: {source}]\n{chunk['content']}")

    context_text = "\n\n---\n\n".join(context_parts)

    return (
        "You are a helpful technical assistant. Answer the question using "
        "ONLY the context provided below. If the answer is not in the "
        'context, say "I don\'t have enough information to answer that."\n'
        "Cite which source(s) you used.\n\n"
        f"Context:\n{context_text}\n\n"
        f"Question: {question}\n\n"
        "Answer:"
    )


def _generate_openai(prompt: str) -> tuple[str, str]:
    """Generate answer using OpenAI."""
    from openai import OpenAI

    logger.info("Generating answer via OpenAI")
    client = OpenAI()
    response = client.chat.completions.create(
        model="gpt-3.5-turbo",
        messages=[{"role": "user", "content": prompt}],
        temperature=0.2,
        max_tokens=500,
    )
    answer = response.choices[0].message.content.strip()
    logger.info("OpenAI response received (%d chars)", len(answer))
    return answer, "openai/gpt-3.5-turbo"


def _generate_anthropic(prompt: str) -> tuple[str, str]:
    """Generate answer using Anthropic Claude."""
    import anthropic

    logger.info("Generating answer via Anthropic")
    client = anthropic.Anthropic()
    response = client.messages.create(
        model="claude-3-haiku-20240307",
        max_tokens=500,
        messages=[{"role": "user", "content": prompt}],
    )
    answer = response.content[0].text.strip()
    logger.info("Anthropic response received (%d chars)", len(answer))
    return answer, "anthropic/claude-3-haiku"


def _extractive_fallback(question: str, chunks: list[dict]) -> str:
    """Return the best matching chunk as the answer when no LLM is available."""
    if not chunks:
        return "No relevant documents found. Please index some documents first."

    best = chunks[0]
    source = best["metadata"].get("source", "unknown")
    score = best["score"]

    return (
        f"**[Extractive answer -- no LLM configured]**\n\n"
        f"Best matching passage (similarity: {score:.0%}) "
        f"from *{source}*:\n\n"
        f"> {best['content']}\n\n"
        f"*Tip: Set OPENAI_API_KEY or ANTHROPIC_API_KEY for generated answers.*"
    )


def query(
    question: str,
    vector_store: VectorStore,
    k: int = 5,
) -> RAGResponse:
    """Run the full RAG pipeline: retrieve, generate, return.

    Args:
        question: The user's natural-language question.
        vector_store: Initialized VectorStore instance.
        k: Number of chunks to retrieve.

    Returns:
        RAGResponse with answer text, source documents, and model info.
    """
    logger.info("RAG query: %r (k=%d)", question[:100], k)

    # 1. Retrieve relevant chunks
    chunks = vector_store.similarity_search(question, k=k)
    logger.info("Retrieved %d chunks", len(chunks))

    sources: list[dict] = [
        {
            "source": c["metadata"].get("source", "unknown"),
            "chunk_index": c["metadata"].get("chunk_index", 0),
            "score": c["score"],
            "preview": c["content"][:200] + "..." if len(c["content"]) > 200 else c["content"],
        }
        for c in chunks
    ]

    # 2. Generate answer (LLM or fallback)
    prompt = _build_prompt(question, chunks)

    openai_key = os.getenv("OPENAI_API_KEY", "").strip()
    anthropic_key = os.getenv("ANTHROPIC_API_KEY", "").strip()

    # Filter out placeholder values
    has_openai = bool(openai_key and openai_key != "your_key_here")
    has_anthropic = bool(anthropic_key and anthropic_key != "your_key_here")

    try:
        if has_openai:
            answer, model = _generate_openai(prompt)
        elif has_anthropic:
            answer, model = _generate_anthropic(prompt)
        else:
            logger.info("No LLM API key configured; using extractive fallback")
            answer = _extractive_fallback(question, chunks)
            model = "extractive-fallback"
    except ImportError as exc:
        logger.error("LLM provider package not installed: %s", exc)
        answer = (
            f"LLM package not installed: {exc}\n\n"
            f"Falling back to extractive mode.\n\n"
            f"{_extractive_fallback(question, chunks)}"
        )
        model = "extractive-fallback"
    except ConnectionError as exc:
        logger.error("Network error contacting LLM provider: %s", exc)
        answer = (
            f"LLM connection failed: {exc}\n\n"
            f"Falling back to extractive mode.\n\n"
            f"{_extractive_fallback(question, chunks)}"
        )
        model = "extractive-fallback"
    except (ValueError, TypeError, KeyError) as exc:
        logger.error("Unexpected error during LLM generation: %s", exc)
        answer = (
            f"LLM generation failed: {exc}\n\n"
            f"Falling back to extractive mode.\n\n"
            f"{_extractive_fallback(question, chunks)}"
        )
        model = "extractive-fallback"
    except Exception as exc:
        # Catch LLM-provider-specific errors (openai.APIError, anthropic.APIError, etc.)
        # These are imported lazily, so we catch broadly but log the type.
        logger.error("LLM API error (%s): %s", type(exc).__name__, exc)
        answer = (
            f"LLM generation failed ({type(exc).__name__}): {exc}\n\n"
            f"Falling back to extractive mode.\n\n"
            f"{_extractive_fallback(question, chunks)}"
        )
        model = "extractive-fallback"

    return RAGResponse(answer=answer, sources=sources, model_used=model)
