"""
Gen-AI Tool: AgenticAI (Autonomous Agent)
==========================================
Demonstrates: ReAct agent loop, tool use, autonomous research,
self-reflection, goal-directed execution, action planning.

Role in GenAI Nexus: Autonomous agent that researches the startup idea,
generates code skeletons, and creates the pitch deck autonomously.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Callable

DEMO_AGENT_LOG = [
    ("Thought", "I need to research the legal tech market and find key data points."),
    ("Action", "search_market[legal document analysis AI market 2024]"),
    ("Observation", "Found: $45.2B TAM, 18.9% CAGR, Harvey AI $100M funded"),
    ("Thought", "I have market data. Now I need to identify the key competitors."),
    ("Action", "search_competitors[AI legal document tools mid-market]"),
    ("Observation", "Competitors: Harvey AI (BigLaw), Ironclad (enterprise), gap in mid-market"),
    ("Thought", "Found the market gap. Now generate a code skeleton for the MVP."),
    ("Action", "generate_code[legal document NER contract risk scoring FastAPI]"),
    ("Observation", "Generated: document_processor.py, risk_scorer.py, api/routes.py"),
    ("Thought", "Code skeleton created. Generate pitch deck content."),
    ("Action", "create_pitch[legal AI mid-market $45B market $1.5M seed]"),
    ("Observation", "Created 10-slide pitch deck with financial projections"),
    ("Final Answer", "Research complete. Generated: market analysis, code skeleton, pitch deck."),
]


@dataclass
class Tool:
    """An agent tool with name, description, and function."""

    name: str
    description: str
    fn: Callable[..., str]


@dataclass
class AgentStep:
    """One step in the ReAct agent loop."""

    thought: str
    action: str
    action_input: str
    observation: str
    step_number: int


@dataclass
class AgentResult:
    """Final result from autonomous agent execution."""

    final_answer: str
    steps: list[AgentStep] = field(default_factory=list)
    tools_used: list[str] = field(default_factory=list)
    artifacts: dict[str, Any] = field(default_factory=dict)


# ─────────────────────────────────────────────
# TOOLS (agent capabilities)
# ─────────────────────────────────────────────


def market_search_tool(query: str) -> str:
    """Search for market data and industry reports."""
    # In production: connects to web search, Perplexity API, or internal RAG
    return f"""Market search results for "{query}":
- TAM: $45.2B (legal tech 2024, Grand View Research)
- CAGR: 18.9% through 2030
- Key segments: Contract Management 28%, eDiscovery 22%, Legal Research 18%
- Investment: $2.1B VC invested in legal tech in 2023
- Adoption: 73% of law firms plan AI by 2025 (Thomson Reuters survey)"""


def competitor_search_tool(query: str) -> str:
    """Search for competitive intelligence."""
    return f"""Competitor results for "{query}":
- Harvey AI: $100M Series B, BigLaw focus, GPT-4 powered, $5K+/month
- Ironclad: $333M total, enterprise CLM, 1,000+ customers, not AI-first
- Kira Systems: Acquired by Litera, due diligence focus
- Gap identified: Mid-market (1-50 attorney firms) with no AI-native solution at $299-999/month"""


def code_generator_tool(requirements: str) -> str:
    """Generate production-ready code skeleton."""
    return f'''Code skeleton generated for: {requirements}

# document_processor.py
from dataclasses import dataclass
from anthropic import Anthropic

@dataclass
class ContractRisk:
    score: float  # 0-1
    clauses: list[str]
    red_flags: list[str]

class LegalDocumentProcessor:
    def __init__(self, api_key: str):
        self.client = Anthropic(api_key=api_key)

    def analyze(self, document: str) -> ContractRisk:
        response = self.client.messages.create(
            model="claude-3-5-sonnet-20241022",
            max_tokens=1000,
            messages=[{{"role": "user", "content": f"Analyze risks: {{document[:2000]}}"}}]
        )
        # Parse response into ContractRisk...
        return ContractRisk(score=0.3, clauses=["§3.2 Limitation of Liability"],
                           red_flags=["Unlimited indemnification in §7"])

# api/routes.py
from fastapi import FastAPI, UploadFile
app = FastAPI()

@app.post("/analyze")
async def analyze_document(file: UploadFile) -> dict:
    text = await file.read()
    processor = LegalDocumentProcessor(api_key="...")
    result = processor.analyze(text.decode())
    return {{"risk_score": result.score, "red_flags": result.red_flags}}
'''


def pitch_creator_tool(context: str) -> str:
    """Create pitch deck content."""
    return f"""Pitch deck created for context: {context}

SLIDE 1 — HOOK: "Legal review costs US law firms $180B/year. 40% is pure waste."
SLIDE 2 — PROBLEM: Solo + small firms spend 40% of attorney time on document review
SLIDE 3 — SOLUTION: LegalAI — 90-second NDA review, automated risk scoring, clause suggestions
SLIDE 4 — MARKET: $45.2B TAM | $8.1B SAM | 18.9% CAGR
SLIDE 5 — TRACTION: 50 beta users | NPS=72 | 85% retention | 3 paid pilots
SLIDE 6 — BUSINESS MODEL: $299/mo (starter) | $999/mo (pro) | Enterprise custom
SLIDE 7 — COMPETITION: Harvey (BigLaw) + Ironclad (enterprise) = Gap in mid-market
SLIDE 8 — TEAM: [CEO ex-BigLaw] [CTO ex-Google AI] [CMO ex-Clio]
SLIDE 9 — FINANCIALS: $150K ARR M12 → $2M ARR M24 → Profitability M36
SLIDE 10 — ASK: $1.5M seed | 18-month runway | 500 customers target"""


class ReactAgent:
    """
    ReAct (Reasoning + Acting) autonomous agent.

    Demonstrates:
    - Thought → Action → Observation loop
    - Tool selection and execution
    - Self-reflection and replanning
    - Goal-directed autonomous execution
    - Artifact collection
    """

    def __init__(self, openai_key: str = "", max_iterations: int = 10, use_local: bool = False):
        self._demo = not openai_key and not use_local
        self._max_iter = max_iterations
        self._use_local = use_local

        # Register available tools
        self._tools: dict[str, Tool] = {
            "search_market": Tool(
                "search_market",
                "Search for market size, growth rates, industry reports",
                market_search_tool,
            ),
            "search_competitors": Tool(
                "search_competitors",
                "Find competitor landscape, funding, positioning",
                competitor_search_tool,
            ),
            "generate_code": Tool(
                "generate_code",
                "Generate production-ready Python code skeleton",
                code_generator_tool,
            ),
            "create_pitch": Tool(
                "create_pitch",
                "Create investor pitch deck content",
                pitch_creator_tool,
            ),
        }

        if not self._demo:
            try:
                if use_local:
                    try:
                        from langchain_ollama import ChatOllama

                        from config.settings import settings

                        self._llm = ChatOllama(
                            model=settings.ollama_model, temperature=0.3
                        )
                    except ImportError:
                        from langchain_openai import ChatOpenAI

                        from config.settings import settings

                        self._llm = ChatOpenAI(
                            base_url=f"{settings.ollama_base_url}/v1",
                            api_key="ollama",
                            model=settings.ollama_model,
                        )
                else:
                    from langchain_openai import ChatOpenAI

                    self._llm = ChatOpenAI(api_key=openai_key, model="gpt-4o-mini")
            except ImportError:
                self._demo = True

    def run(self, goal: str) -> AgentResult:
        """
        Execute autonomous agent to achieve a goal.

        Args:
            goal: What the agent should accomplish
        """
        if self._demo:
            return self._demo_run(goal)

        # LangChain ReAct agent execution
        steps = []
        artifacts = {}

        # Convert tools to LangChain format
        from langchain.tools import Tool as LCTool

        lc_tools = [
            LCTool(
                name=t.name,
                description=t.description,
                func=t.fn,
            )
            for t in self._tools.values()
        ]

        from langchain.agents import AgentExecutor, create_react_agent
        from langchain_core.prompts import PromptTemplate

        prompt = PromptTemplate.from_template(
            "You are a startup research agent. Use tools to research and build a comprehensive startup plan.\n\n"
            "Available tools: {tools}\nTool names: {tool_names}\n\n"
            "Goal: {input}\n\n{agent_scratchpad}"
        )

        agent = create_react_agent(self._llm, lc_tools, prompt)
        executor = AgentExecutor(agent=agent, tools=lc_tools, max_iterations=self._max_iter, verbose=True)

        result = executor.invoke({"input": goal})
        return AgentResult(
            final_answer=result.get("output", ""),
            steps=steps,
            tools_used=list(self._tools.keys()),
            artifacts=artifacts,
        )

    def execute_tool(self, tool_name: str, tool_input: str) -> str:
        """Execute a specific tool directly."""
        if tool_name not in self._tools:
            return f"ERROR: Tool '{tool_name}' not found. Available: {list(self._tools)}"
        return self._tools[tool_name].fn(tool_input)

    def _demo_run(self, goal: str) -> AgentResult:
        """Demo: walk through pre-defined ReAct trace."""
        steps = []
        tools_used = []
        artifacts = {}

        for i, (step_type, content) in enumerate(DEMO_AGENT_LOG[:-1], 1):
            if step_type == "Thought":
                current_thought = content
            elif step_type == "Action":
                tool_name = content.split("[")[0]
                tool_input = content.split("[")[1].rstrip("]") if "[" in content else content
                tools_used.append(tool_name)
            elif step_type == "Observation":
                steps.append(
                    AgentStep(
                        thought=current_thought,
                        action=tool_name if "tool_name" in dir() else "unknown",
                        action_input=tool_input if "tool_input" in dir() else "",
                        observation=content,
                        step_number=len(steps) + 1,
                    )
                )
                # Collect artifacts
                if "code" in content.lower():
                    artifacts["code_skeleton"] = content
                elif "pitch" in content.lower():
                    artifacts["pitch_deck"] = content

        final_answer = DEMO_AGENT_LOG[-1][1]
        return AgentResult(
            final_answer=final_answer,
            steps=steps,
            tools_used=list(set(tools_used)),
            artifacts=artifacts,
        )


def demo():
    print("=" * 60)
    print("DEMO: AgenticAI — Autonomous Startup Research Agent")
    print("=" * 60)
    agent = ReactAgent()

    print("\n[1] Available Tools")
    for name, tool in agent._tools.items():
        print(f"  • {name}: {tool.description}")

    print("\n[2] Run Autonomous Research")
    result = agent.run(
        "Research the market for AI legal document analysis, "
        "find competitors, generate MVP code, and create a pitch deck"
    )

    print(f"\nFinal Answer: {result.final_answer}")
    print(f"\nTools Used: {result.tools_used}")
    print(f"\nExecution Steps:")
    for step in result.steps:
        print(f"\n  Step {step.step_number}:")
        print(f"    Thought: {step.thought[:80]}...")
        print(f"    Action: {step.action}[{step.action_input[:50]}]")
        print(f"    Observation: {step.observation[:80]}...")

    print("\n[3] Direct Tool Execution")
    output = agent.execute_tool("search_market", "legal AI SaaS 2024 growth")
    print(output)


if __name__ == "__main__":
    demo()
