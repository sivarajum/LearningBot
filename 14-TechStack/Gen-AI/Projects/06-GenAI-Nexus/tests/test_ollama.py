"""Tests for OllamaClient — local LLM via Ollama (demo mode, no server required)."""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

from src.llm.ollama_client import (
    DEMO_CODE,
    DEMO_COMPETITOR,
    DEMO_MARKET,
    DEMO_PITCH,
    OllamaClient,
    OllamaConfig,
    OllamaResponse,
)

# Force demo mode: point to an unreachable URL so Ollama never connects
DEMO_CONFIG = OllamaConfig(base_url="http://127.0.0.1:1")  # port 1 = guaranteed closed


class TestOllamaConfig:
    def test_default_values(self):
        config = OllamaConfig()
        assert config.base_url == "http://localhost:11434"
        assert config.default_model == "llama3.1:8b"
        assert config.code_model == "codellama:7b"
        assert config.fast_model == "llama3.2:3b"
        assert config.embedding_model == "nomic-embed-text"
        assert config.temperature == 0.3
        assert config.max_tokens == 2048
        assert config.timeout == 120

    def test_custom_config(self):
        config = OllamaConfig(
            base_url="http://192.168.1.100:11434",
            default_model="mistral:7b",
            temperature=0.7,
            max_tokens=4096,
        )
        assert config.base_url == "http://192.168.1.100:11434"
        assert config.default_model == "mistral:7b"
        assert config.temperature == 0.7
        assert config.max_tokens == 4096
        # Unchanged defaults
        assert config.code_model == "codellama:7b"


class TestOllamaResponse:
    def test_basic_response(self):
        resp = OllamaResponse(content="Hello", model="llama3.1:8b")
        assert resp.content == "Hello"
        assert resp.model == "llama3.1:8b"
        assert resp.tokens_used == 0
        assert resp.metadata == {}

    def test_response_with_metadata(self):
        resp = OllamaResponse(
            content="Analysis",
            model="codellama:7b",
            tokens_used=150,
            metadata={"task": "code_gen"},
        )
        assert resp.tokens_used == 150
        assert resp.metadata["task"] == "code_gen"


class TestOllamaClientDemoMode:
    """All tests run in demo mode — no Ollama server needed."""

    def test_init_demo_mode(self):
        """Client should initialize in demo mode when Ollama is not running."""
        client = OllamaClient(config=DEMO_CONFIG)
        # In CI/test env, Ollama is likely not running → demo mode
        assert client._demo is True or client._available is True
        # Either way, client should be usable
        assert client.config.default_model == "llama3.1:8b"

    def test_is_available_property(self):
        client = OllamaClient(config=DEMO_CONFIG)
        assert isinstance(client.is_available, bool)

    def test_available_models_property(self):
        client = OllamaClient(config=DEMO_CONFIG)
        assert isinstance(client.available_models, list)

    def test_analyze_market(self):
        client = OllamaClient(config=DEMO_CONFIG)
        result = client.analyze_market("AI legal document analyzer")
        assert isinstance(result, OllamaResponse)
        assert len(result.content) > 50
        # In demo mode, should return DEMO_MARKET
        if client._demo:
            assert result.model == "demo-local"
            assert "TAM" in result.content or "Market" in result.content.upper()

    def test_analyze_competitors(self):
        client = OllamaClient(config=DEMO_CONFIG)
        result = client.analyze_competitors("AI legal document analyzer")
        assert isinstance(result, OllamaResponse)
        assert len(result.content) > 50
        if client._demo:
            assert "Harvey" in result.content or "competitor" in result.content.lower()

    def test_generate_code(self):
        client = OllamaClient(config=DEMO_CONFIG)
        result = client.generate_code("AI legal analyzer", ["Python", "FastAPI"])
        assert isinstance(result, OllamaResponse)
        assert len(result.content) > 50
        if client._demo:
            assert "def " in result.content or "class" in result.content or "FastAPI" in result.content

    def test_generate_code_default_stack(self):
        client = OllamaClient(config=DEMO_CONFIG)
        result = client.generate_code("AI legal analyzer")
        assert isinstance(result, OllamaResponse)
        assert len(result.content) > 50

    def test_generate_pitch(self):
        client = OllamaClient(config=DEMO_CONFIG)
        result = client.generate_pitch("AI legal analyzer")
        assert isinstance(result, OllamaResponse)
        assert len(result.content) > 50
        if client._demo:
            assert "pitch" in result.content.lower() or "SLIDE" in result.content

    def test_generate_pitch_with_market_data(self):
        client = OllamaClient(config=DEMO_CONFIG)
        result = client.generate_pitch("AI legal analyzer", {"tam": "$45.2B"})
        assert isinstance(result, OllamaResponse)
        assert len(result.content) > 50

    def test_fast_summary(self):
        client = OllamaClient(config=DEMO_CONFIG)
        result = client.fast_summary("The legal tech market is growing rapidly at 18.9% CAGR")
        assert isinstance(result, OllamaResponse)
        assert len(result.content) > 10
        if client._demo:
            assert "summar" in result.content.lower() or "Demo" in result.content

    def test_stream(self):
        client = OllamaClient(config=DEMO_CONFIG)
        chunks = list(client.stream("Explain RAG in one sentence"))
        assert len(chunks) > 0
        full_text = "".join(chunks)
        assert len(full_text) > 10
        if client._demo:
            assert "Demo" in full_text or "demo" in full_text

    def test_embed_single_text(self):
        client = OllamaClient(config=DEMO_CONFIG)
        embeddings = client.embed(["AI legal document analyzer"])
        assert len(embeddings) == 1
        assert len(embeddings[0]) == 768  # nomic-embed-text dimension
        # Should be unit-normalized
        import math
        norm = math.sqrt(sum(x * x for x in embeddings[0]))
        assert abs(norm - 1.0) < 0.01

    def test_embed_batch(self):
        client = OllamaClient(config=DEMO_CONFIG)
        texts = ["AI legal tools", "contract analysis", "market research"]
        embeddings = client.embed(texts)
        assert len(embeddings) == 3
        for emb in embeddings:
            assert len(emb) == 768

    def test_embed_deterministic(self):
        """Same text should produce same embedding (demo mode is seeded)."""
        client = OllamaClient(config=DEMO_CONFIG)
        e1 = client.embed(["test text"])
        e2 = client.embed(["test text"])
        if client._demo:
            assert e1[0][:10] == e2[0][:10]

    def test_embed_different_texts_differ(self):
        """Different texts should produce different embeddings."""
        client = OllamaClient(config=DEMO_CONFIG)
        embeddings = client.embed(["legal tech", "quantum computing"])
        assert embeddings[0][:10] != embeddings[1][:10]

    def test_health_check(self):
        client = OllamaClient(config=DEMO_CONFIG)
        health = client.health_check()
        assert isinstance(health, dict)
        assert "available" in health
        assert "base_url" in health
        assert "models" in health
        assert "default_model" in health
        assert "code_model" in health
        assert "fast_model" in health
        assert health["default_model"] == "llama3.1:8b"
        assert health["code_model"] == "codellama:7b"
        assert health["fast_model"] == "llama3.2:3b"


class TestOllamaDemoResponseRouting:
    """Test that _demo_response routes to correct demo content."""

    def test_competitor_keywords_route(self):
        client = OllamaClient(config=DEMO_CONFIG)
        # Force demo mode
        client._demo = True
        resp = client._demo_response("llama3.1:8b", "Map the competitive landscape")
        assert "Harvey" in resp.content or "Competitive" in resp.content.upper()

    def test_code_keywords_route(self):
        client = OllamaClient(config=DEMO_CONFIG)
        client._demo = True
        resp = client._demo_response("codellama:7b", "Generate a code skeleton for MVP")
        assert "def " in resp.content or "class" in resp.content

    def test_pitch_keywords_route(self):
        client = OllamaClient(config=DEMO_CONFIG)
        client._demo = True
        resp = client._demo_response("llama3.2:3b", "Create a pitch deck")
        assert "PITCH" in resp.content or "SLIDE" in resp.content

    def test_summary_keywords_route(self):
        client = OllamaClient(config=DEMO_CONFIG)
        client._demo = True
        resp = client._demo_response("llama3.2:3b", "Summarize this market data")
        assert "Summary" in resp.content or "summar" in resp.content.lower()

    def test_default_routes_to_market(self):
        client = OllamaClient(config=DEMO_CONFIG)
        client._demo = True
        resp = client._demo_response("llama3.1:8b", "Analyze the opportunity for this startup")
        assert "MARKET" in resp.content or "TAM" in resp.content

    def test_demo_response_model_is_demo(self):
        client = OllamaClient(config=DEMO_CONFIG)
        client._demo = True
        resp = client._demo_response("llama3.1:8b", "Anything")
        assert resp.model == "demo-local"
        assert resp.tokens_used == 0


class TestDemoConstants:
    """Verify demo content constants are well-formed."""

    def test_demo_market_content(self):
        assert len(DEMO_MARKET) > 100
        assert "TAM" in DEMO_MARKET
        assert "SAM" in DEMO_MARKET

    def test_demo_competitor_content(self):
        assert len(DEMO_COMPETITOR) > 100
        assert "Harvey" in DEMO_COMPETITOR

    def test_demo_code_content(self):
        assert len(DEMO_CODE) > 100
        assert "FastAPI" in DEMO_CODE or "def " in DEMO_CODE

    def test_demo_pitch_content(self):
        assert len(DEMO_PITCH) > 100
        assert "PITCH" in DEMO_PITCH or "SLIDE" in DEMO_PITCH
