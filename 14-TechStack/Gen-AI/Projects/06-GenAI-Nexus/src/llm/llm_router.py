"""
LLM Router — Intelligent task-to-model routing.
Routes each analysis task to the best LLM based on:
- Task type (code, long-context, multimodal, fast)
- API key availability
- Cost optimization
"""

from __future__ import annotations

from dataclasses import dataclass
from enum import Enum

from config.settings import settings
from src.llm.claude_client import ClaudeClient, ClaudeResponse
from src.llm.gemini_client import GeminiClient, GeminiResponse
from src.llm.ollama_client import OllamaClient, OllamaConfig
from src.llm.openai_client import AnalysisResult, OpenAIClient


class TaskType(str, Enum):
    MARKET_RESEARCH = "market_research"
    COMPETITOR_ANALYSIS = "competitor_analysis"
    CODE_GENERATION = "code_generation"
    PITCH_CONTENT = "pitch_content"
    MULTIMODAL = "multimodal"
    FAST_SUMMARY = "fast_summary"


@dataclass
class RouterResult:
    content: str
    model_used: str
    task_type: TaskType


# Task → preferred LLM mapping
_ROUTING_TABLE: dict[TaskType, str] = {
    TaskType.MARKET_RESEARCH: "openai",        # GPT-4o structured analysis
    TaskType.COMPETITOR_ANALYSIS: "claude",    # Long-context, thorough
    TaskType.CODE_GENERATION: "claude",        # Claude excels at code
    TaskType.PITCH_CONTENT: "gemini",          # Fast, creative
    TaskType.MULTIMODAL: "gemini",             # Only Gemini handles images
    TaskType.FAST_SUMMARY: "gemini",           # Gemini Flash = cheapest
}


class LLMRouter:
    """
    Routes tasks to the optimal LLM.
    Falls back gracefully if a key is missing.
    Supports local LLM (Ollama) when USE_LOCAL_LLM=true.
    """

    def __init__(self):
        openai_key = settings.openai_api_key if settings.has_openai else ""
        claude_key = settings.anthropic_api_key if settings.has_anthropic else ""
        gemini_key = settings.google_api_key if settings.has_google else ""

        self._openai = OpenAIClient(api_key=openai_key)
        self._claude = ClaudeClient(api_key=claude_key)
        self._gemini = GeminiClient(api_key=gemini_key)

        # Local LLM via Ollama
        self._ollama = None
        if settings.has_local_llm:
            ollama_config = OllamaConfig(
                base_url=settings.ollama_base_url,
                default_model=settings.ollama_model,
                code_model=settings.ollama_code_model,
                fast_model=settings.ollama_fast_model,
                embedding_model=settings.ollama_embed_model,
            )
            self._ollama = OllamaClient(config=ollama_config)

    @property
    def has_local_llm(self) -> bool:
        """Check if local Ollama LLM is available."""
        return self._ollama is not None

    def route(self, task: TaskType, payload: dict) -> RouterResult:
        """Route task to best available LLM. Prefers local if configured."""
        idea = payload.get("startup_idea", "AI startup")

        # Local LLM override — route everything through Ollama
        if self._ollama is not None:
            return self._route_local(task, payload, idea)

        # Original cloud routing
        return self._route_cloud(task, payload, idea)

    def _route_local(self, task: TaskType, payload: dict, idea: str) -> RouterResult:
        """Route all tasks through local Ollama LLM."""
        if task == TaskType.MARKET_RESEARCH:
            r = self._ollama.analyze_market(idea)
        elif task == TaskType.COMPETITOR_ANALYSIS:
            r = self._ollama.analyze_competitors(idea)
        elif task == TaskType.CODE_GENERATION:
            stack = payload.get("tech_stack", ["Python", "FastAPI"])
            r = self._ollama.generate_code(idea, stack)
        elif task == TaskType.PITCH_CONTENT:
            market = payload.get("market_data", {})
            r = self._ollama.generate_pitch(idea, market)
        elif task == TaskType.FAST_SUMMARY:
            r = self._ollama.fast_summary(idea)
        elif task == TaskType.MULTIMODAL:
            # Multimodal not supported locally — fall back to market analysis
            r = self._ollama.analyze_market(idea)
        else:
            r = self._ollama.analyze_market(idea)

        return RouterResult(content=r.content, model_used=r.model, task_type=task)

    def _route_cloud(self, task: TaskType, payload: dict, idea: str) -> RouterResult:
        """Route tasks to cloud LLM providers (original behavior)."""
        if task == TaskType.MARKET_RESEARCH:
            result = self._openai.analyze_market(idea)
            return RouterResult(result.content, result.model, task)

        elif task == TaskType.COMPETITOR_ANALYSIS:
            result = self._claude.analyze_competitors(idea)
            return RouterResult(result.content, result.model, task)

        elif task == TaskType.CODE_GENERATION:
            stack = payload.get("tech_stack", ["Python", "FastAPI"])
            result = self._claude.generate_code_skeleton(idea, stack)
            return RouterResult(result.content, result.model, task)

        elif task == TaskType.PITCH_CONTENT:
            market = payload.get("market_data", {})
            result = self._gemini.pitch_deck_content(idea, market)
            return RouterResult(result.content, result.model, task)

        elif task == TaskType.MULTIMODAL:
            prompt = payload.get("prompt", f"Analyze market for {idea}")
            image = payload.get("image_path")
            result = self._gemini.analyze_image_and_text(prompt, image)
            return RouterResult(result.content, result.model, task)

        elif task == TaskType.FAST_SUMMARY:
            result = self._gemini.analyze_market_text(idea)
            return RouterResult(result.content, result.model, task)

        else:
            result = self._openai.analyze_market(idea)
            return RouterResult(result.content, result.model, task)

    def run_all(self, startup_idea: str) -> dict[str, RouterResult]:
        """Run all task types for a complete analysis."""
        payload = {"startup_idea": startup_idea}
        results = {}
        for task in TaskType:
            results[task.value] = self.route(task, payload)
        return results


def demo():
    print("=" * 60)
    print("DEMO: LLM Router")
    print("=" * 60)
    router = LLMRouter()

    print("\n[1] Route: Market Research → OpenAI")
    result = router.route(
        TaskType.MARKET_RESEARCH, {"startup_idea": "AI legal document analyzer"}
    )
    print(f"Model: {result.model_used}\n{result.content[:300]}...")

    print("\n[2] Route: Code Generation → Claude")
    result = router.route(
        TaskType.CODE_GENERATION,
        {"startup_idea": "AI legal document analyzer", "tech_stack": ["Python", "FastAPI"]},
    )
    print(f"Model: {result.model_used}\n{result.content[:300]}...")

    print("\n[3] Run All Tasks")
    all_results = router.run_all("AI legal document analyzer")
    for task, res in all_results.items():
        print(f"  {task}: {res.model_used} ✓")


if __name__ == "__main__":
    demo()
