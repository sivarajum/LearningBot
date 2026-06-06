"""
Gen-AI Tool: LangChain
========================
Demonstrates: LCEL (LangChain Expression Language) chains, sequential
chains, parallel chains, output parsers, memory, and chain composition.

Role in GenAI Nexus: Chain the analysis steps — Market → Competitive →
Technical → Report, each stage using previous stage's output.
"""

from __future__ import annotations

from dataclasses import dataclass, field

# Demo responses for each chain stage
DEMO_MARKET = """
MARKET ANALYSIS (LangChain Chain Step 1)
=========================================
TAM: $45.2B | SAM: $8.1B | SOM: $810M
Growth: 18.9% CAGR through 2030
Key drivers: AI adoption, remote work, regulatory complexity
"""

DEMO_COMPETITIVE = """
COMPETITIVE ANALYSIS (LangChain Chain Step 2)
==============================================
Based on market context above:
• Harvey AI — BigLaw focus, $100M funded, overpriced for mid-market
• Ironclad — Enterprise CLM, $333M, not AI-first
• Gap: Mid-market firms ($50M-500M) with no AI-native solution
Recommended position: "AI legal tools at mid-market pricing"
"""

DEMO_TECHNICAL = """
TECHNICAL PLAN (LangChain Chain Step 3)
========================================
Based on competitive analysis above:
MVP Stack: Python + FastAPI + PostgreSQL + React
AI Layer: Claude API (long-context) + OpenAI (structured extraction)
Key features: NDA analysis, contract risk scoring, clause suggestions
Infrastructure: AWS (SOC2-friendly) + Pinecone (vector search)
Timeline: 3 months to MVP, 6 months to first paying customer
"""

DEMO_REPORT = """
FINAL STARTUP REPORT (LangChain Chain Step 4 — Synthesis)
===========================================================
EXECUTIVE SUMMARY
=================
Opportunity: $45.2B legal tech market with AI-native gap in mid-market
Product: AI document analyzer for 1-50 attorney firms
Moat: Domain-trained models + workflow integration + data flywheel
Ask: $1.5M seed to reach $150K ARR in 12 months

KEY DECISIONS:
✓ Build: AI document analysis engine (core IP)
✓ Buy: Auth, billing, email (Stripe, Auth0, SendGrid)
✓ Partner: Legal malpractice insurance (reduces customer risk)
✗ Skip: Multi-jurisdiction support until post-seed

RECOMMENDATION: Build. Execute. Focus on 10 design partners first.
"""


@dataclass
class ChainResult:
    """Output from a LangChain pipeline step."""

    stage: str
    content: str
    metadata: dict = field(default_factory=dict)


@dataclass
class FullAnalysisResult:
    """Complete multi-stage chain output."""

    market: ChainResult
    competitive: ChainResult
    technical: ChainResult
    report: ChainResult
    startup_idea: str


class AnalysisChains:
    """
    LangChain LCEL chains for startup analysis pipeline.

    Demonstrates:
    - PromptTemplate + LLM + OutputParser chain (LCEL)
    - Sequential chaining: each stage uses previous output
    - Parallel chains: run independent analyses concurrently
    - Memory: maintain context across chain steps
    - RunnablePassthrough for context injection
    - StrOutputParser and PydanticOutputParser
    """

    def __init__(self, openai_key: str = "", use_local: bool = False):
        self._demo = not openai_key and not use_local
        self._chains_built = False

        if not self._demo:
            try:
                if use_local:
                    # Use Ollama local LLM via LangChain
                    try:
                        from langchain_ollama import ChatOllama

                        from config.settings import settings

                        self._llm = ChatOllama(
                            model=settings.ollama_model, temperature=0.3
                        )
                    except ImportError:
                        # Fallback: use OpenAI client pointing at Ollama
                        from langchain_openai import ChatOpenAI

                        from config.settings import settings

                        self._llm = ChatOpenAI(
                            base_url=f"{settings.ollama_base_url}/v1",
                            api_key="ollama",
                            model=settings.ollama_model,
                            temperature=0.3,
                        )
                else:
                    from langchain_openai import ChatOpenAI

                    self._llm = ChatOpenAI(
                        api_key=openai_key, model="gpt-4o-mini", temperature=0.3
                    )
                self._build_chains()
                self._chains_built = True
            except ImportError:
                self._demo = True

    def _build_chains(self):
        """Build LCEL chains for each analysis stage."""
        from langchain_core.output_parsers import StrOutputParser
        from langchain_core.prompts import ChatPromptTemplate
        from langchain_core.runnables import RunnablePassthrough

        parser = StrOutputParser()

        # Chain 1: Market Research
        market_prompt = ChatPromptTemplate.from_messages([
            ("system", "You are a market analyst. Be concise and data-driven."),
            ("human", "Analyze market for: {startup_idea}\nProvide TAM/SAM/SOM and key trends."),
        ])
        self._market_chain = market_prompt | self._llm | parser

        # Chain 2: Competitive (takes market as context)
        competitive_prompt = ChatPromptTemplate.from_messages([
            ("system", "You are a competitive intelligence analyst."),
            ("human", "Startup: {startup_idea}\nMarket context: {market_analysis}\n\nMap competitors and find the whitespace."),
        ])
        self._competitive_chain = (
            RunnablePassthrough.assign(
                market_analysis=self._market_chain
            )
            | competitive_prompt
            | self._llm
            | parser
        )

        # Chain 3: Technical (sequential)
        tech_prompt = ChatPromptTemplate.from_messages([
            ("system", "You are a CTO. Recommend concrete tech stacks."),
            ("human", "Startup: {startup_idea}\nMarket: {market_analysis}\nCompetitors: {competitive_analysis}\n\nDesign the MVP tech architecture."),
        ])
        self._tech_chain = tech_prompt | self._llm | parser

        # Chain 4: Final Report (synthesis)
        report_prompt = ChatPromptTemplate.from_messages([
            ("system", "You are a startup advisor writing an executive brief."),
            ("human", """Synthesize this complete startup analysis:

Startup: {startup_idea}
Market: {market_analysis}
Competition: {competitive_analysis}
Technical Plan: {technical_plan}

Write a 1-page executive summary with clear RECOMMENDATION."""),
        ])
        self._report_chain = report_prompt | self._llm | parser

    def run_market_analysis(self, startup_idea: str) -> ChainResult:
        """Stage 1: Market research chain."""
        if self._demo:
            return ChainResult(stage="market", content=DEMO_MARKET)

        content = self._market_chain.invoke({"startup_idea": startup_idea})
        return ChainResult(stage="market", content=content)

    def run_competitive_analysis(self, startup_idea: str, market: str) -> ChainResult:
        """Stage 2: Competitive analysis (uses market output)."""
        if self._demo:
            return ChainResult(stage="competitive", content=DEMO_COMPETITIVE)

        content = self._competitive_chain.invoke({
            "startup_idea": startup_idea,
            "market_analysis": market,
        })
        return ChainResult(stage="competitive", content=content)

    def run_technical_plan(
        self, startup_idea: str, market: str, competitive: str
    ) -> ChainResult:
        """Stage 3: Technical architecture plan."""
        if self._demo:
            return ChainResult(stage="technical", content=DEMO_TECHNICAL)

        if self._chains_built:
            content = self._tech_chain.invoke({
                "startup_idea": startup_idea,
                "market_analysis": market,
                "competitive_analysis": competitive,
            })
        else:
            content = DEMO_TECHNICAL
        return ChainResult(stage="technical", content=content)

    def run_full_analysis(self, startup_idea: str) -> FullAnalysisResult:
        """
        Run complete sequential chain: Market → Competitive → Technical → Report.
        Each stage feeds into the next.
        """
        print(f"  [Chain 1/4] Market analysis...")
        market = self.run_market_analysis(startup_idea)

        print(f"  [Chain 2/4] Competitive analysis...")
        competitive = self.run_competitive_analysis(startup_idea, market.content)

        print(f"  [Chain 3/4] Technical planning...")
        technical = self.run_technical_plan(
            startup_idea, market.content, competitive.content
        )

        print(f"  [Chain 4/4] Synthesizing report...")
        if self._demo:
            report = ChainResult(stage="report", content=DEMO_REPORT)
        elif self._chains_built:
            content = self._report_chain.invoke({
                "startup_idea": startup_idea,
                "market_analysis": market.content,
                "competitive_analysis": competitive.content,
                "technical_plan": technical.content,
            })
            report = ChainResult(stage="report", content=content)
        else:
            report = ChainResult(stage="report", content=DEMO_REPORT)

        return FullAnalysisResult(
            market=market,
            competitive=competitive,
            technical=technical,
            report=report,
            startup_idea=startup_idea,
        )

    def run_parallel_analysis(self, startup_idea: str) -> dict[str, ChainResult]:
        """
        Run independent analyses in parallel (LangChain RunnableParallel).
        Market + Tech can run simultaneously (both independent).
        """
        if self._demo:
            return {
                "market": ChainResult(stage="market", content=DEMO_MARKET),
                "technical": ChainResult(stage="technical", content=DEMO_TECHNICAL),
            }

        from langchain_core.runnables import RunnableParallel

        parallel_chain = RunnableParallel(
            market=self._market_chain,
            # A separate tech-focused chain could run in parallel here
        )

        results = parallel_chain.invoke({"startup_idea": startup_idea})
        return {
            "market": ChainResult(stage="market", content=results["market"]),
        }


def demo():
    print("=" * 60)
    print("DEMO: LangChain Analysis Chains")
    print("=" * 60)
    chains = AnalysisChains()  # demo mode

    print("\n[1] Sequential Full Analysis")
    result = chains.run_full_analysis("AI legal document analyzer")

    print(f"\n--- MARKET ---\n{result.market.content}")
    print(f"\n--- COMPETITIVE ---\n{result.competitive.content}")
    print(f"\n--- TECHNICAL ---\n{result.technical.content}")
    print(f"\n--- REPORT ---\n{result.report.content}")

    print("\n[2] Parallel Analysis (Independent stages)")
    parallel = chains.run_parallel_analysis("AI legal document analyzer")
    for stage, res in parallel.items():
        print(f"  {stage}: {res.content[:100]}...")


if __name__ == "__main__":
    demo()
