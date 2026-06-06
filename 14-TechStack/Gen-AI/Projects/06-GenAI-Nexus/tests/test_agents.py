"""Tests for agent modules (AgenticAI, CrewAI, AutoGen)."""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

from src.agents.agentic_core import ReactAgent
from src.agents.autogen_debate import StartupDebate
from src.agents.crew_team import StartupCrew


class TestReactAgent:
    def test_available_tools(self):
        agent = ReactAgent()
        assert len(agent._tools) >= 4
        assert "search_market" in agent._tools
        assert "generate_code" in agent._tools
        assert "create_pitch" in agent._tools

    def test_execute_tool_directly(self):
        agent = ReactAgent()
        result = agent.execute_tool("search_market", "legal tech AI 2024")
        assert len(result) > 50
        assert "legal" in result.lower() or "market" in result.lower()

    def test_run_returns_result(self):
        agent = ReactAgent()
        result = agent.run("Research market for AI legal tools and generate code")
        assert result.final_answer
        assert len(result.steps) > 0

    def test_tools_used_tracked(self):
        agent = ReactAgent()
        result = agent.run("Research AI legal market")
        assert len(result.tools_used) > 0

    def test_invalid_tool_handled(self):
        agent = ReactAgent()
        result = agent.execute_tool("nonexistent_tool", "input")
        assert "not found" in result.lower() or "ERROR" in result


class TestStartupCrew:
    def test_run_all_roles(self):
        crew = StartupCrew()
        results = crew.run("AI legal document analyzer")
        assert "ceo" in results
        assert "cto" in results
        assert "cmo" in results
        assert "cfo" in results

    def test_all_outputs_non_empty(self):
        crew = StartupCrew()
        results = crew.run("AI legal document analyzer")
        for role, output in results.items():
            assert len(output) > 50, f"Empty output for {role}"

    def test_ceo_output_has_roadmap(self):
        crew = StartupCrew()
        results = crew.run("AI legal")
        ceo = results["ceo"].lower()
        assert any(word in ceo for word in ["month", "strategy", "roadmap", "vision", "milestone"])

    def test_cfo_output_has_numbers(self):
        crew = StartupCrew()
        results = crew.run("AI legal")
        cfo = results["cfo"]
        import re
        # Should contain dollar amounts or percentages
        assert re.search(r"[\$\d]", cfo)

    def test_with_context(self):
        crew = StartupCrew()
        context = {
            "market": "Legal tech $45.2B TAM",
            "competition": "Harvey AI (BigLaw), Ironclad (enterprise)",
        }
        results = crew.run("AI legal document analyzer", context=context)
        assert all(len(v) > 20 for v in results.values())


class TestStartupDebate:
    def test_run_returns_debate(self):
        debate = StartupDebate()
        result = debate.run("AI legal document analyzer")
        assert len(result) > 100

    def test_debate_has_both_sides(self):
        debate = StartupDebate()
        result = debate.run("AI legal")
        result_lower = result.lower()
        # Should have optimistic and skeptical viewpoints
        assert any(word in result_lower for word in ["optimist", "opportunity", "grow", "market"])
        assert any(word in result_lower for word in ["skeptic", "risk", "challenge", "concern"])

    def test_extract_risks(self):
        debate = StartupDebate()
        from src.agents.autogen_debate import DEMO_DEBATE
        risks = debate.extract_risks(DEMO_DEBATE)
        assert len(risks) >= 1

    def test_with_plan_summary(self):
        debate = StartupDebate()
        result = debate.run(
            "AI legal document analyzer",
            "Focus on mid-market, $299/month pricing",
        )
        assert len(result) > 50
