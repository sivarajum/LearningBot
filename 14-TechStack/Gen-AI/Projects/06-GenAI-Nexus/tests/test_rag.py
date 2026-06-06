"""Tests for RAG pipeline (Basic, Advanced, LlamaIndex)."""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

from src.rag.advanced_rag import AdvancedRAG, HyDERetriever, QueryDecomposer
from src.rag.basic_rag import BasicRAG, TextChunker
from src.rag.llama_indexer import LlamaIndexer
from src.vectorstore.chroma_store import ChromaVectorStore, Document


class TestTextChunker:
    def test_short_text_no_split(self):
        chunker = TextChunker(chunk_size=500)
        chunks = chunker.chunk_text("Short text", {"source": "test"})
        assert len(chunks) == 1
        assert chunks[0].content == "Short text"

    def test_long_text_splits(self):
        chunker = TextChunker(chunk_size=100, overlap=10)
        long_text = "word " * 100  # 500 chars
        chunks = chunker.chunk_text(long_text)
        assert len(chunks) > 1

    def test_metadata_preserved(self):
        chunker = TextChunker()
        chunks = chunker.chunk_text("Some text", {"source": "test_doc"})
        assert chunks[0].metadata["source"] == "test_doc"
        assert "chunk_index" in chunks[0].metadata


class TestChromaVectorStore:
    def test_load_knowledge_base(self):
        store = ChromaVectorStore()
        n = store.load_knowledge_base()
        assert n > 0
        assert store.count() > 0

    def test_search_returns_results(self):
        store = ChromaVectorStore()
        store.load_knowledge_base()
        results = store.search("AI legal competitors", top_k=3)
        assert len(results) > 0
        assert all(r.content for r in results)

    def test_filtered_search(self):
        store = ChromaVectorStore()
        store.load_knowledge_base()
        results = store.search_by_type("legal AI", doc_type="competitor", top_k=2)
        for r in results:
            assert r.metadata.get("type") == "competitor"


class TestBasicRAG:
    def test_query_returns_response(self):
        rag = BasicRAG()
        result = rag.query("What is the market for AI legal tools?")
        assert result.answer
        assert result.retrieved_chunks > 0

    def test_competitor_query(self):
        rag = BasicRAG()
        result = rag.query_competitors("AI legal document analyzer")
        assert result.answer
        assert result.query

    def test_ingest_documents(self):
        rag = BasicRAG()
        docs = [("AI startup raises funding for legal tools", {"type": "news"})]
        n = rag.ingest(docs)
        assert n >= 1

    def test_empty_query_handled(self):
        rag = BasicRAG()
        result = rag.query("xyzunknownquery123")
        # Should return gracefully even if no results
        assert isinstance(result.answer, str)


class TestAdvancedRAG:
    def test_hyde_retriever(self):
        hyde = HyDERetriever()
        hypo = hyde.get_hypothetical_query("Who are the competitors?")
        assert len(hypo) > 20

    def test_query_decomposer(self):
        decomposer = QueryDecomposer()
        sub_queries = decomposer.decompose("What is the market size and who are the competitors?")
        assert len(sub_queries) >= 1

    def test_advanced_query(self):
        rag = AdvancedRAG()
        result = rag.query_advanced("Who are the competitors in AI legal tech?")
        assert result.answer
        assert result.sources

    def test_multihop_query(self):
        rag = AdvancedRAG()
        results = rag.query_multihop("What is the full landscape for AI legal tools?")
        assert len(results) >= 1
        for sub_q, result in results.items():
            assert isinstance(result.answer, str)


class TestLlamaIndexer:
    def test_load_knowledge(self):
        indexer = LlamaIndexer()
        indexer.load_startup_knowledge()
        assert len(indexer._documents_loaded) == 2

    def test_query_returns_result(self):
        indexer = LlamaIndexer()
        indexer.load_startup_knowledge()
        result = indexer.query("What are Harvey AI's weaknesses?")
        assert result.response
        assert result.query

    def test_summarize(self):
        indexer = LlamaIndexer()
        indexer.load_startup_knowledge()
        summary = indexer.summarize()
        assert len(summary) > 50

    def test_keyword_search(self):
        indexer = LlamaIndexer()
        indexer.load_startup_knowledge()
        result = indexer.keyword_search(["mid-market", "PLG"])
        assert result.response
