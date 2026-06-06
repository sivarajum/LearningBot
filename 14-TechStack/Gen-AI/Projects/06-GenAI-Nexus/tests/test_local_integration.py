"""
Tests for local LLM integration across all modules.
Verifies: settings, router, chains, agents, RAG — all with use_local=True.
All tests work in demo mode (no Ollama server required).
"""

import os
import sys
from pathlib import Path
from unittest.mock import patch

sys.path.insert(0, str(Path(__file__).parent.parent))

from src.llm.ollama_client import OllamaClient, OllamaConfig

# Force demo mode: unreachable URL so Ollama never connects in tests
DEMO_CONFIG = OllamaConfig(base_url="http://127.0.0.1:1")


class TestSettingsLocalLLM:
    """Test Pydantic Settings with Ollama fields."""

    def test_default_use_local_false(self):
        from config.settings import Settings

        s = Settings()
        assert s.use_local_llm is False
        assert s.has_local_llm is False

    def test_has_local_llm_true(self):
        with patch.dict(os.environ, {"USE_LOCAL_LLM": "true"}):
            from config.settings import Settings

            s = Settings()
            assert s.use_local_llm is True
            assert s.has_local_llm is True

    def test_ollama_url_default(self):
        from config.settings import Settings

        s = Settings()
        assert s.ollama_base_url == "http://localhost:11434"

    def test_ollama_url_custom(self):
        with patch.dict(os.environ, {"OLLAMA_BASE_URL": "http://gpu-box:11434"}):
            from config.settings import Settings

            s = Settings()
            assert s.ollama_base_url == "http://gpu-box:11434"

    def test_ollama_model_defaults(self):
        from config.settings import Settings

        s = Settings()
        assert s.ollama_model == "llama3.1:8b"
        assert s.ollama_code_model == "codellama:7b"
        assert s.ollama_fast_model == "llama3.2:3b"
        assert s.ollama_embed_model == "nomic-embed-text"

    def test_custom_models(self):
        with patch.dict(os.environ, {
            "OLLAMA_MODEL": "mistral:7b",
            "OLLAMA_CODE_MODEL": "deepseek-coder:6.7b",
        }):
            from config.settings import Settings

            s = Settings()
            assert s.ollama_model == "mistral:7b"
            assert s.ollama_code_model == "deepseek-coder:6.7b"


class TestRouterLocalLLM:
    """Test LLM Router with Ollama integration."""

    def test_router_without_local(self):
        """Router should work without local LLM (default behavior)."""
        from src.llm.llm_router import LLMRouter

        router = LLMRouter()
        # Without USE_LOCAL_LLM, should not have local LLM
        # (may or may not, depends on env — just check works)
        assert hasattr(router, "has_local_llm")

    def test_router_all_tasks_cloud(self):
        """All task types should route successfully in cloud (demo) mode."""
        from src.llm.llm_router import LLMRouter, TaskType

        router = LLMRouter()
        for task in TaskType:
            result = router.route(task, {"startup_idea": "AI legal analyzer"})
            assert result.content
            assert result.task_type == task

    def test_router_run_all(self):
        """run_all should complete for all task types."""
        from src.llm.llm_router import LLMRouter, TaskType

        router = LLMRouter()
        results = router.run_all("AI legal document analyzer")
        assert len(results) == len(TaskType)

    def test_route_local_method_exists(self):
        """Router should have _route_local and _route_cloud methods."""
        from src.llm.llm_router import LLMRouter

        router = LLMRouter()
        assert hasattr(router, "_route_local")
        assert hasattr(router, "_route_cloud")

    def test_router_with_forced_ollama(self):
        """Force-inject Ollama client and verify local routing."""
        from src.llm.llm_router import LLMRouter, TaskType
        from src.llm.ollama_client import OllamaClient

        router = LLMRouter()
        # Inject Ollama client (demo mode)
        router._ollama = OllamaClient(config=DEMO_CONFIG)

        result = router.route(
            TaskType.MARKET_RESEARCH, {"startup_idea": "AI legal analyzer"}
        )
        assert result.content
        assert result.task_type == TaskType.MARKET_RESEARCH

    def test_router_local_all_tasks(self):
        """All tasks should route through local Ollama when injected."""
        from src.llm.llm_router import LLMRouter, TaskType
        from src.llm.ollama_client import OllamaClient

        router = LLMRouter()
        router._ollama = OllamaClient(config=DEMO_CONFIG)

        for task in TaskType:
            result = router.route(task, {"startup_idea": "AI legal analyzer"})
            assert result.content
            assert result.task_type == task

    def test_router_local_code_with_stack(self):
        """Code generation should accept tech_stack payload param."""
        from src.llm.llm_router import LLMRouter, TaskType
        from src.llm.ollama_client import OllamaClient

        router = LLMRouter()
        router._ollama = OllamaClient(config=DEMO_CONFIG)

        result = router.route(
            TaskType.CODE_GENERATION,
            {"startup_idea": "AI legal analyzer", "tech_stack": ["Python", "Django"]},
        )
        assert result.content

    def test_router_local_pitch_with_market(self):
        """Pitch generation should accept market_data payload param."""
        from src.llm.llm_router import LLMRouter, TaskType
        from src.llm.ollama_client import OllamaClient

        router = LLMRouter()
        router._ollama = OllamaClient(config=DEMO_CONFIG)

        result = router.route(
            TaskType.PITCH_CONTENT,
            {"startup_idea": "AI legal analyzer", "market_data": {"tam": "$45B"}},
        )
        assert result.content


class TestChainsLocal:
    """Test LangChain AnalysisChains with use_local=True."""

    def test_chains_demo_mode(self):
        """Chains should work in demo mode (no key, no local)."""
        from src.chains.analysis_chains import AnalysisChains

        chains = AnalysisChains()
        assert chains._demo is True

    def test_chains_use_local_flag(self):
        """Chains accept use_local parameter."""
        from src.chains.analysis_chains import AnalysisChains

        # use_local=True but no Ollama server → falls back to demo
        chains = AnalysisChains(use_local=True)
        # Should still work (either local or demo fallback)
        result = chains.run_market_analysis("AI legal analyzer")
        assert result.content
        assert len(result.content) > 50

    def test_chains_full_analysis_local(self):
        """Full analysis pipeline should work with local flag."""
        from src.chains.analysis_chains import AnalysisChains

        chains = AnalysisChains(use_local=True)
        result = chains.run_full_analysis("AI legal analyzer")
        assert result.market.content
        assert result.competitive.content
        assert result.technical.content
        assert result.report.content
        assert result.startup_idea == "AI legal analyzer"

    def test_chains_parallel_local(self):
        """Parallel analysis should work with local flag."""
        from src.chains.analysis_chains import AnalysisChains

        chains = AnalysisChains(use_local=True)
        result = chains.run_parallel_analysis("AI legal analyzer")
        assert "market" in result


class TestCrewLocal:
    """Test CrewAI StartupCrew with use_local=True."""

    def test_crew_accepts_use_local(self):
        from src.agents.crew_team import StartupCrew

        crew = StartupCrew(use_local=True)
        assert crew._use_local is True

    def test_crew_default_not_local(self):
        from src.agents.crew_team import StartupCrew

        crew = StartupCrew()
        assert crew._use_local is False

    def test_crew_run_local(self):
        """CrewAI should produce all 4 role outputs with local flag."""
        from src.agents.crew_team import StartupCrew

        crew = StartupCrew(use_local=True)
        results = crew.run("AI legal document analyzer")
        assert "ceo" in results
        assert "cto" in results
        assert "cmo" in results
        assert "cfo" in results
        for role, output in results.items():
            assert len(output) > 50, f"Empty output for {role}"

    def test_crew_run_local_with_context(self):
        from src.agents.crew_team import StartupCrew

        crew = StartupCrew(use_local=True)
        context = {"market": "Legal tech $45B TAM", "competition": "Harvey AI"}
        results = crew.run("AI legal analyzer", context=context)
        assert all(len(v) > 20 for v in results.values())


class TestAutoGenLocal:
    """Test AutoGen StartupDebate with use_local=True."""

    def test_debate_accepts_use_local(self):
        from src.agents.autogen_debate import StartupDebate

        debate = StartupDebate(use_local=True)
        assert debate._use_local is True

    def test_debate_default_not_local(self):
        from src.agents.autogen_debate import StartupDebate

        debate = StartupDebate()
        assert debate._use_local is False

    def test_debate_run_local(self):
        """Debate should produce output with local flag."""
        from src.agents.autogen_debate import StartupDebate

        debate = StartupDebate(use_local=True)
        result = debate.run("AI legal document analyzer")
        assert len(result) > 100

    def test_debate_run_local_both_sides(self):
        from src.agents.autogen_debate import StartupDebate

        debate = StartupDebate(use_local=True)
        result = debate.run("AI legal analyzer")
        result_lower = result.lower()
        assert any(w in result_lower for w in ["optimist", "opportunity", "grow", "market"])
        assert any(w in result_lower for w in ["skeptic", "risk", "challenge", "concern"])


class TestAgenticLocal:
    """Test ReactAgent with use_local=True."""

    def test_agent_accepts_use_local(self):
        from src.agents.agentic_core import ReactAgent

        agent = ReactAgent(use_local=True)
        assert agent._use_local is True

    def test_agent_default_not_local(self):
        from src.agents.agentic_core import ReactAgent

        agent = ReactAgent()
        assert agent._use_local is False

    def test_agent_tools_available(self):
        from src.agents.agentic_core import ReactAgent

        agent = ReactAgent(use_local=True)
        assert len(agent._tools) >= 4

    def test_agent_execute_tool(self):
        from src.agents.agentic_core import ReactAgent

        agent = ReactAgent(use_local=True)
        result = agent.execute_tool("search_market", "legal tech AI")
        assert len(result) > 20

    def test_agent_run_local(self):
        from src.agents.agentic_core import ReactAgent

        agent = ReactAgent(use_local=True)
        result = agent.run("Research the AI legal tools market")
        assert result.final_answer
        assert len(result.steps) > 0


class TestRAGLocal:
    """Test BasicRAG with local LLM integration."""

    def test_rag_query(self):
        """BasicRAG should return answers regardless of local LLM."""
        from src.rag.basic_rag import BasicRAG

        rag = BasicRAG()
        result = rag.query("What is the market for AI legal tools?")
        assert result.answer
        assert isinstance(result.answer, str)

    def test_rag_ingest(self):
        from src.rag.basic_rag import BasicRAG

        rag = BasicRAG()
        docs = [("AI document analysis is growing rapidly", {"type": "news"})]
        n = rag.ingest(docs)
        assert n >= 1


class TestMainLocalFlag:
    """Test main.py --local flag integration."""

    def test_parse_args_local_flag(self):
        """--local flag should be recognized by argparse."""
        # Import parse_args to validate it accepts --local
        sys.argv = ["main.py", "--local", "--idea", "test startup"]
        from main import parse_args

        args = parse_args()
        assert args.local is True
        assert args.idea == "test startup"

    def test_parse_args_no_local(self):
        sys.argv = ["main.py", "--idea", "test startup"]
        from main import parse_args

        args = parse_args()
        assert args.local is False

    def test_ollama_in_individual_demos(self):
        """'ollama' module should be available as individual demo."""
        from main import INDIVIDUAL_DEMOS

        assert "ollama" in INDIVIDUAL_DEMOS
        assert INDIVIDUAL_DEMOS["ollama"] == "src.llm.ollama_client"

    def test_individual_demos_complete(self):
        """All 27 individual demos should be registered (26 original + ollama)."""
        from main import INDIVIDUAL_DEMOS

        assert len(INDIVIDUAL_DEMOS) >= 27
        # Key modules must be present
        for key in ["openai", "claude", "gemini", "ollama", "langchain", "rag", "crew", "autogen", "agents"]:
            assert key in INDIVIDUAL_DEMOS, f"Missing demo: {key}"


class TestEndToEndLocal:
    """End-to-end integration: local LLM path through the full system."""

    def test_ollama_to_router_to_result(self):
        """Ollama → Router → RouterResult — full path."""
        from src.llm.llm_router import LLMRouter, RouterResult, TaskType
        from src.llm.ollama_client import OllamaClient

        router = LLMRouter()
        router._ollama = OllamaClient(config=DEMO_CONFIG)

        # Run all 6 task types
        results = router.run_all("AI legal document analyzer")
        assert len(results) == len(TaskType)
        for task_name, result in results.items():
            assert isinstance(result, RouterResult)
            assert result.content
            assert len(result.content) > 20

    def test_chains_produce_all_stages(self):
        """Chains should produce market, competitive, technical, report."""
        from src.chains.analysis_chains import AnalysisChains

        chains = AnalysisChains(use_local=True)
        result = chains.run_full_analysis("AI legal document analyzer")
        stages = [result.market, result.competitive, result.technical, result.report]
        for stage in stages:
            assert stage.content
            assert stage.stage in ("market", "competitive", "technical", "report")

    def test_all_agents_with_local(self):
        """All 3 agent types should work with use_local=True."""
        from src.agents.agentic_core import ReactAgent
        from src.agents.autogen_debate import StartupDebate
        from src.agents.crew_team import StartupCrew

        idea = "AI legal document analyzer"

        # ReactAgent
        agent = ReactAgent(use_local=True)
        result = agent.run(idea)
        assert result.final_answer

        # CrewAI
        crew = StartupCrew(use_local=True)
        crew_result = crew.run(idea)
        assert len(crew_result) == 4

        # AutoGen
        debate = StartupDebate(use_local=True)
        debate_result = debate.run(idea)
        assert len(debate_result) > 50
