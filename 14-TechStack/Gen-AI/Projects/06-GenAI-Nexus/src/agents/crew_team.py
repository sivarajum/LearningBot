"""
Gen-AI Tool: CrewAI
====================
Demonstrates: Multi-agent teams with specialized roles, task delegation,
agent collaboration, backstory-driven personas, hierarchical process,
and sequential task execution with context passing.

Role in GenAI Nexus: 4-agent executive team — CEO, CTO, CMO, CFO —
each producing their domain plan for the startup.
"""

from __future__ import annotations

from dataclasses import dataclass, field

DEMO_CEO_OUTPUT = """
CEO STRATEGY PLAN
=================
Vision: Become the #1 AI legal tools platform for small-to-mid law firms.

18-Month Roadmap:
M1-3:  Close 10 design partners. Build with them, not for them.
M4-6:  Launch public beta. Target 100 customers, $15K MRR.
M6:    Raise $1.5M seed from legal tech-focused angels + 1 VC.
M9-12: Scale to 300 customers, $50K MRR. Hire 5 engineers.
M15-18: Series A readiness ($150K MRR, 40% YoY growth, 85% NRR).

Key Decisions:
1. US-only launch (legal rules differ per jurisdiction)
2. Flat-rate pricing (lawyers hate surprises)
3. No-code onboarding (lawyers are not technical)

First 10 customers strategy: Offer 6 months free + dedicated support
in exchange for product feedback + case studies.
"""

DEMO_CTO_OUTPUT = """
CTO TECHNICAL ARCHITECTURE
============================
MVP Stack (Ship in 3 months):
• Backend: Python 3.12 + FastAPI (async)
• AI: Claude API (100K context, best for contracts) + GPT-4 fallback
• Database: PostgreSQL + pgvector (embeddings co-located)
• File Storage: AWS S3 (SOC2-friendly)
• Auth: Auth0 (saves 2 weeks of dev time)
• Frontend: React + Tailwind (fast, familiar)
• Deploy: AWS ECS on Fargate (SOC2 audit trail)

AI Pipeline:
Upload PDF → Extract text (PyMuPDF) → Chunk (512 tokens, 50 overlap)
→ Embed (text-embedding-3-small) → Store (pgvector)
→ Analyze (Claude claude-3-5-sonnet-20241022) → Risk Score → UI

Month 1 Focus: PDF text extraction + Claude analysis = core value.
Everything else is polish.

Critical: SOC2 Type I by Month 9 (required for enterprise sales).
AWS + Cloudflare WAF covers 80% of requirements out-of-box.
"""

DEMO_CMO_OUTPUT = """
CMO GO-TO-MARKET PLAN
======================
ICP (Ideal Customer Profile):
- Solo or 2-10 attorney firms
- US-based, common law jurisdictions
- Revenue: $500K - $5M/year
- Pain: NDA review, contractor agreements, client intake contracts

Acquisition Channels (priority order):
1. Legal Tech Forums (Clio Community, MyCase Community) — FREE
   → Post helpful content about AI legal tools
   → Answer contract review questions (no pitch)
   → Cost: 0, Expected: 2-3 leads/week

2. Bar Association Partnerships (target: 5 local bars in M1-3)
   → Offer free AI webinar + demo
   → Cost: $0 (speaking fee), Expected: 10-20 leads/event

3. Clio/PracticePanther App Marketplace (Month 4)
   → List as integration partner
   → 150K potential customers browsing marketplace

4. LinkedIn Organic (founder-led content)
   → Share "AI vs Manual contract review" content
   → Real case studies with time savings

Month 1-3 Goal: 100 trial signups, 15 qualified demos, 5 paid pilots.
"""

DEMO_CFO_OUTPUT = """
CFO FINANCIAL MODEL
====================
Revenue Projections:
M3:   $0 ARR (design partners, free)
M6:   $15K MRR ($180K ARR) — 50 customers at avg $299/mo
M9:   $35K MRR ($420K ARR) — growth + upsell
M12:  $65K MRR ($780K ARR) — 200 customers, mix of tiers
M18:  $150K MRR ($1.8M ARR) — 400 customers, NRR 115%

Unit Economics (targets):
• LTV: $3,600 (avg $300/mo × 12 months avg tenure)
• CAC: $800 (blended: bar assoc + content + outbound)
• LTV/CAC: 4.5x (healthy: above 3x)
• Payback period: 2.7 months (excellent for SaaS)
• Gross Margin: 78% (LLM API costs ~$0.50/doc, charge $299+/mo)

Burn Rate:
• Seed: $1.5M raised
• Monthly burn: $65K (2 founders + 2 engineers + infra)
• Runway: 23 months
• Default alive at M18 if plan executed

Fundraising Timeline:
Seed ($1.5M pre-money $7M): Month 6
Series A ($5M pre-money $25M): Month 18 if $150K MRR hit
"""


@dataclass
class CrewConfig:
    openai_key: str = ""
    verbose: bool = False


@dataclass
class TeamOutput:
    """Output from the 4-agent executive team."""

    ceo: str = ""
    cto: str = ""
    cmo: str = ""
    cfo: str = ""
    startup_idea: str = ""


class StartupCrew:
    """
    CrewAI multi-agent executive team.

    Demonstrates:
    - Agent definition with role + backstory + goal
    - Task creation with context dependencies
    - Sequential process (each agent builds on previous)
    - Hierarchical process (optional)
    - Inter-agent communication via task context
    """

    def __init__(self, config: CrewConfig | None = None, use_local: bool = False):
        self._config = config or CrewConfig()
        self._use_local = use_local
        self._demo = not self._config.openai_key and not use_local
        self._crew = None

        if not self._demo:
            self._build_crew()

    def _build_crew(self):
        """Build the CrewAI agents and tasks."""
        try:
            from crewai import Agent, Crew, Process, Task

            if self._use_local:
                # Use Ollama as LLM backend for CrewAI
                import os

                from config.settings import settings

                os.environ["OPENAI_API_BASE"] = f"{settings.ollama_base_url}/v1"
                os.environ["OPENAI_API_KEY"] = "ollama"
                os.environ["OPENAI_MODEL_NAME"] = settings.ollama_model

                from langchain_openai import ChatOpenAI

                llm = ChatOpenAI(
                    base_url=f"{settings.ollama_base_url}/v1",
                    api_key="ollama",
                    model=settings.ollama_model,
                    temperature=0.3,
                )
            else:
                from langchain_openai import ChatOpenAI

                llm = ChatOpenAI(
                    api_key=self._config.openai_key,
                    model="gpt-4o-mini",
                    temperature=0.3,
                )

            # Define 4 executive agents
            ceo = Agent(
                role="CEO and Startup Strategist",
                goal="Define the vision, roadmap, and fundraising strategy for the startup",
                backstory=(
                    "You are a 3x founder with exits in B2B SaaS. You raised $50M total "
                    "across your startups and have deep expertise in legal tech. "
                    "You are direct, numbers-driven, and allergic to fluff."
                ),
                llm=llm,
                verbose=self._config.verbose,
            )

            cto = Agent(
                role="CTO and Principal Engineer",
                goal="Design the technical architecture and define the MVP build plan",
                backstory=(
                    "You are a Stanford CS graduate with 10+ years at Google and Stripe. "
                    "You built 2 production ML systems serving 10M+ users. "
                    "You believe in shipping fast with clean architecture."
                ),
                llm=llm,
                verbose=self._config.verbose,
            )

            cmo = Agent(
                role="CMO and Growth Strategist",
                goal="Define go-to-market strategy, ICP, and first 100 customer acquisition plan",
                backstory=(
                    "You led growth at Clio from $10M to $100M ARR. "
                    "You know legal tech distribution cold — bar associations, "
                    "practice management integrations, community building. "
                    "You focus on metrics: CAC, LTV, payback period."
                ),
                llm=llm,
                verbose=self._config.verbose,
            )

            cfo = Agent(
                role="CFO and Financial Strategist",
                goal="Build the financial model, unit economics, and fundraising strategy",
                backstory=(
                    "You are a former VC analyst at Bessemer turned startup CFO. "
                    "You've seen 500+ SaaS businesses and know what good looks like. "
                    "You are obsessed with unit economics and burn rate."
                ),
                llm=llm,
                verbose=self._config.verbose,
            )

            self._agents = {"ceo": ceo, "cto": cto, "cmo": cmo, "cfo": cfo}

        except ImportError:
            self._demo = True

    def run(self, startup_idea: str, context: dict | None = None) -> dict[str, str]:
        """
        Run the 4-agent team on the startup idea.

        Args:
            startup_idea: The startup to analyze
            context: Prior research (market, competitive, technical)

        Returns:
            Dict with ceo, cto, cmo, cfo outputs
        """
        if self._demo:
            return {
                "ceo": DEMO_CEO_OUTPUT,
                "cto": DEMO_CTO_OUTPUT,
                "cmo": DEMO_CMO_OUTPUT,
                "cfo": DEMO_CFO_OUTPUT,
            }

        try:
            from crewai import Crew, Process, Task

            ctx = context or {}
            market = ctx.get("market", "")
            competition = ctx.get("competition", "")

            # Define tasks with context dependencies
            ceo_task = Task(
                description=f"Create vision, roadmap, and fundraising strategy for: {startup_idea}\nMarket: {market[:500]}",
                agent=self._agents["ceo"],
                expected_output="CEO strategy with 18-month roadmap and fundraising plan",
            )

            cto_task = Task(
                description=f"Design technical architecture for: {startup_idea}\nCompetition: {competition[:500]}",
                agent=self._agents["cto"],
                expected_output="Tech stack, MVP architecture, data pipeline, SOC2 plan",
            )

            cmo_task = Task(
                description=f"Create go-to-market strategy for: {startup_idea}\nMarket: {market[:300]}",
                agent=self._agents["cmo"],
                expected_output="ICP, top 3 acquisition channels, Month 1-3 targets",
            )

            cfo_task = Task(
                description=f"Build financial model for: {startup_idea}",
                agent=self._agents["cfo"],
                expected_output="Revenue projections M3-M18, unit economics, fundraising timeline",
            )

            crew = Crew(
                agents=list(self._agents.values()),
                tasks=[ceo_task, cto_task, cmo_task, cfo_task],
                process=Process.sequential,
                verbose=self._config.verbose,
            )

            results = crew.kickoff()
            return {
                "ceo": str(ceo_task.output) if hasattr(ceo_task, "output") else str(results),
                "cto": str(cto_task.output) if hasattr(cto_task, "output") else "",
                "cmo": str(cmo_task.output) if hasattr(cmo_task, "output") else "",
                "cfo": str(cfo_task.output) if hasattr(cfo_task, "output") else "",
            }

        except Exception as e:
            # Fallback to demo on any error
            return {
                "ceo": DEMO_CEO_OUTPUT + f"\n[Error: {e}]",
                "cto": DEMO_CTO_OUTPUT,
                "cmo": DEMO_CMO_OUTPUT,
                "cfo": DEMO_CFO_OUTPUT,
            }


def demo():
    print("=" * 60)
    print("DEMO: CrewAI — 4-Agent Executive Team")
    print("=" * 60)
    crew = StartupCrew()

    print("\n[1] Run 4-Agent Executive Team")
    results = crew.run("AI legal document analyzer")

    for role, output in results.items():
        print(f"\n{'=' * 40}")
        print(f"[{role.upper()}]")
        print(output[:400] + "..." if len(output) > 400 else output)


if __name__ == "__main__":
    demo()
