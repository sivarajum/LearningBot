"""
Gen-AI Tool: OpenAI GPT
========================
Demonstrates: Chat completions, function calling, structured outputs,
async parallel calls, streaming, token counting.

Role in GenAI Nexus: Market research analysis + business plan generation.
"""

from __future__ import annotations

import asyncio
import json
from dataclasses import dataclass, field
from typing import Any

DEMO_RESPONSES = {
    "market_research": """
MARKET RESEARCH ANALYSIS
========================
TAM: $45.2B (2024) → $127.8B (2030), CAGR 18.9%
SAM: $8.1B (legal tech SaaS segment)
SOM: $810M (realistic 3-year capture at 10% SAM)

Key Trends:
• 73% of law firms plan AI adoption by 2025 (Thomson Reuters)
• Contract review automation saves 90% time vs manual review
• Key players: Ironclad, ContractPodAi, Kira Systems, Harvey AI

Opportunity: Mid-market firms ($50-500M revenue) underserved —
Harvey targets BigLaw, Ironclad targets enterprise. Gap exists.
""",
    "business_plan": """
BUSINESS PLAN — AI Legal Document Analyzer
==========================================
Revenue Model: SaaS subscription
• Starter: $299/mo (5 users, 100 docs/mo)
• Professional: $999/mo (25 users, unlimited docs)
• Enterprise: Custom ($5K+/mo)

18-Month Milestones:
M3:  MVP launch (contract review, NDA analysis)
M6:  100 paying customers, $150K ARR
M12: Series A target ($3M), 500 customers
M18: $2M ARR, SOC2 certified, 3 verticals

Key Risks: Harvey AI well-funded ($100M+), OpenAI direct competition,
attorney-client privilege compliance requirements.
""",
}


@dataclass
class OpenAIConfig:
    model: str = "gpt-4o-mini"
    temperature: float = 0.3
    max_tokens: int = 2048
    timeout: int = 30


@dataclass
class AnalysisResult:
    content: str
    model: str
    prompt_tokens: int = 0
    completion_tokens: int = 0
    tool_calls: list[dict[str, Any]] = field(default_factory=list)


class OpenAIClient:
    """
    OpenAI GPT client for startup advisor tasks.

    Demonstrates:
    - Basic chat completions
    - Function/tool calling
    - Structured JSON output
    - Async parallel calls
    - Streaming responses
    """

    def __init__(self, api_key: str = "", config: OpenAIConfig | None = None):
        self.config = config or OpenAIConfig()
        self._demo = not api_key
        if not self._demo:
            try:
                from openai import AsyncOpenAI, OpenAI

                self._client = OpenAI(api_key=api_key)
                self._async_client = AsyncOpenAI(api_key=api_key)
            except ImportError:
                self._demo = True

    def analyze_market(self, startup_idea: str) -> AnalysisResult:
        """Run market research analysis for a startup idea."""
        if self._demo:
            return AnalysisResult(
                content=DEMO_RESPONSES["market_research"],
                model="demo",
                prompt_tokens=120,
                completion_tokens=200,
            )

        system = (
            "You are a world-class market research analyst. "
            "Provide TAM/SAM/SOM, key trends, and competitive landscape."
        )
        user = f"Analyze the market for: {startup_idea}"

        response = self._client.chat.completions.create(
            model=self.config.model,
            messages=[{"role": "system", "content": system}, {"role": "user", "content": user}],
            temperature=self.config.temperature,
            max_tokens=self.config.max_tokens,
        )
        msg = response.choices[0].message
        return AnalysisResult(
            content=msg.content or "",
            model=self.config.model,
            prompt_tokens=response.usage.prompt_tokens if response.usage else 0,
            completion_tokens=response.usage.completion_tokens if response.usage else 0,
        )

    def generate_business_plan(self, startup_idea: str, market_context: str) -> AnalysisResult:
        """Generate structured business plan using function calling."""
        if self._demo:
            return AnalysisResult(
                content=DEMO_RESPONSES["business_plan"],
                model="demo",
                prompt_tokens=350,
                completion_tokens=280,
            )

        tools = [
            {
                "type": "function",
                "function": {
                    "name": "create_business_plan",
                    "description": "Create a structured startup business plan",
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "revenue_model": {"type": "string"},
                            "pricing_tiers": {
                                "type": "array",
                                "items": {
                                    "type": "object",
                                    "properties": {
                                        "name": {"type": "string"},
                                        "price_monthly": {"type": "number"},
                                        "features": {"type": "array", "items": {"type": "string"}},
                                    },
                                },
                            },
                            "milestones": {"type": "array", "items": {"type": "string"}},
                            "key_risks": {"type": "array", "items": {"type": "string"}},
                        },
                        "required": ["revenue_model", "pricing_tiers", "milestones", "key_risks"],
                    },
                },
            }
        ]

        response = self._client.chat.completions.create(
            model=self.config.model,
            messages=[
                {
                    "role": "system",
                    "content": "You are a startup strategy consultant. Create detailed business plans.",
                },
                {
                    "role": "user",
                    "content": f"Startup: {startup_idea}\nMarket context: {market_context}",
                },
            ],
            tools=tools,  # type: ignore[arg-type]
            tool_choice={"type": "function", "function": {"name": "create_business_plan"}},
            max_tokens=self.config.max_tokens,
        )

        msg = response.choices[0].message
        tool_calls = []
        content = ""
        if msg.tool_calls:
            for tc in msg.tool_calls:
                data = json.loads(tc.function.arguments)
                tool_calls.append(data)
                content += json.dumps(data, indent=2)

        return AnalysisResult(
            content=content,
            model=self.config.model,
            tool_calls=tool_calls,
            prompt_tokens=response.usage.prompt_tokens if response.usage else 0,
            completion_tokens=response.usage.completion_tokens if response.usage else 0,
        )

    async def parallel_analysis(self, startup_idea: str) -> dict[str, str]:
        """Run market + business plan analysis in parallel using async."""
        if self._demo:
            return {
                "market": DEMO_RESPONSES["market_research"],
                "business_plan": DEMO_RESPONSES["business_plan"],
            }

        async def _call(system: str, user: str) -> str:
            resp = await self._async_client.chat.completions.create(
                model=self.config.model,
                messages=[{"role": "system", "content": system}, {"role": "user", "content": user}],
                max_tokens=1024,
            )
            return resp.choices[0].message.content or ""

        market_task = _call(
            "You are a market research analyst.",
            f"Analyze the market for: {startup_idea}",
        )
        plan_task = _call(
            "You are a startup strategist.",
            f"Write a concise business plan for: {startup_idea}",
        )

        market, plan = await asyncio.gather(market_task, plan_task)
        return {"market": market, "business_plan": plan}

    def stream_analysis(self, startup_idea: str):
        """Stream a startup analysis (generator)."""
        if self._demo:
            for chunk in DEMO_RESPONSES["market_research"].split("\n"):
                yield chunk + "\n"
            return

        stream = self._client.chat.completions.create(
            model=self.config.model,
            messages=[
                {"role": "user", "content": f"Analyze startup idea: {startup_idea}"}
            ],
            stream=True,
            max_tokens=512,
        )
        for chunk in stream:
            delta = chunk.choices[0].delta.content
            if delta:
                yield delta


def demo():
    print("=" * 60)
    print("DEMO: OpenAI GPT Client")
    print("=" * 60)
    client = OpenAIClient()  # demo mode (no API key)

    print("\n[1] Market Research Analysis")
    result = client.analyze_market("AI legal document analyzer")
    print(result.content)

    print("\n[2] Business Plan (Function Calling)")
    result = client.generate_business_plan(
        "AI legal document analyzer",
        "Large market, underserved mid-market segment",
    )
    print(result.content)

    print("\n[3] Streaming Analysis")
    for chunk in client.stream_analysis("AI legal document analyzer"):
        print(chunk, end="", flush=True)
    print()

    print("\n[4] Parallel Async Analysis")
    results = asyncio.run(client.parallel_analysis("AI legal document analyzer"))
    for key, val in results.items():
        print(f"\n--- {key} ---\n{val[:200]}...")


if __name__ == "__main__":
    demo()
