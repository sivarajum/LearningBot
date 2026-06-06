"""Tests for LLM clients (OpenAI, Claude, Gemini, Router)."""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

from src.llm.claude_client import ClaudeClient
from src.llm.gemini_client import GeminiClient
from src.llm.llm_router import LLMRouter, TaskType
from src.llm.openai_client import AnalysisResult, OpenAIClient


class TestOpenAIClient:
    def test_demo_mode_market_analysis(self):
        client = OpenAIClient()  # No key = demo mode
        result = client.analyze_market("AI legal document analyzer")
        assert isinstance(result, AnalysisResult)
        assert len(result.content) > 50
        assert result.model == "demo"

    def test_demo_mode_business_plan(self):
        client = OpenAIClient()
        result = client.generate_business_plan("AI legal", "Large market")
        assert isinstance(result, AnalysisResult)
        assert "Revenue" in result.content or "revenue" in result.content.lower()

    def test_streaming_demo(self):
        client = OpenAIClient()
        chunks = list(client.stream_analysis("AI startup"))
        assert len(chunks) > 0
        full_text = "".join(chunks)
        assert len(full_text) > 20


class TestClaudeClient:
    def test_demo_competitor_analysis(self):
        client = ClaudeClient()
        result = client.analyze_competitors("AI legal document analyzer")
        assert len(result.content) > 50
        assert result.model == "demo"

    def test_demo_code_generation(self):
        client = ClaudeClient()
        result = client.generate_code_skeleton(
            "AI legal analyzer", ["Python", "FastAPI"]
        )
        assert "python" in result.content.lower() or "def " in result.content or "class" in result.content

    def test_multi_turn_conversation(self):
        client = ClaudeClient()
        r1 = client.multi_turn_advisor("Should I focus on NDA analysis?")
        r2 = client.multi_turn_advisor("What about pricing?")
        assert len(client._conversation_history) == 4  # 2 user + 2 assistant

    def test_reset_conversation(self):
        client = ClaudeClient()
        client.multi_turn_advisor("Question 1")
        client.reset_conversation()
        assert len(client._conversation_history) == 0


class TestGeminiClient:
    def test_demo_market_analysis(self):
        client = GeminiClient()
        result = client.analyze_market_text("AI legal document analyzer")
        assert len(result.content) > 50

    def test_demo_structured_output(self):
        client = GeminiClient()
        result = client.structured_market_data("AI legal document analyzer")
        assert result.structured is not None
        assert "market_size_usd_billions" in result.structured

    def test_demo_pitch_content(self):
        client = GeminiClient()
        result = client.pitch_deck_content("AI legal", {"market": "$45B"})
        assert len(result.content) > 50


class TestLLMRouter:
    def test_all_task_types(self):
        router = LLMRouter()
        for task in TaskType:
            result = router.route(task, {"startup_idea": "AI legal analyzer"})
            assert result.content
            assert result.task_type == task

    def test_run_all(self):
        router = LLMRouter()
        results = router.run_all("AI legal analyzer")
        assert len(results) == len(TaskType)
        for task_name, result in results.items():
            assert result.content
