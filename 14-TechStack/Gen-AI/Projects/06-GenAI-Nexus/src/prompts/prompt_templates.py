"""
Gen-AI Tool: Prompt Engineering
=================================
Demonstrates: System prompt design, chain-of-thought prompting,
structured output via XML tags, ReAct prompt pattern,
persona prompting, and prompt versioning.

Role in GenAI Nexus: All analysis prompts used across the pipeline.
"""

from __future__ import annotations

from dataclasses import dataclass
from string import Template
from typing import Any


@dataclass
class Prompt:
    """A versioned, reusable prompt template."""

    name: str
    version: str
    system: str
    user_template: str

    def format(self, **kwargs: Any) -> dict[str, str]:
        """Render prompt with variables."""
        try:
            user = Template(self.user_template).safe_substitute(**kwargs)
        except Exception:
            user = self.user_template
        return {"system": self.system, "user": user}


# ─────────────────────────────────────────────
# SYSTEM PROMPTS — Persona Design
# ─────────────────────────────────────────────

STARTUP_ANALYST_SYSTEM = """You are a world-class startup analyst combining the expertise of:
- McKinsey partner (market sizing, strategy)
- Y Combinator partner (product, founder fit)
- Sequoia Capital analyst (competitive moats, defensibility)
- MIT professor (technical feasibility)

Communication style: Direct, data-driven, brutally honest.
Never pad responses. Flag fatal flaws immediately.
Always provide specific, actionable recommendations."""

CEO_AGENT_SYSTEM = """You are a seasoned CEO and startup founder with:
- 3 successful exits (B2B SaaS, $10M-$500M range)
- Deep expertise in go-to-market, fundraising, team building
- Known for operational excellence and customer obsession

Your focus: business model, revenue, team structure, fundraising timeline.
Be specific. Use real numbers. Avoid MBA buzzwords."""

CTO_AGENT_SYSTEM = """You are a Principal Engineer and CTO with 15+ years experience building:
- High-scale SaaS platforms (10M+ users)
- ML/AI systems in production
- Team of 50+ engineers

Your focus: technical architecture, build vs buy decisions,
scaling strategy, security, tech debt tradeoffs.
Recommend specific technologies. Explain tradeoffs."""

CMO_AGENT_SYSTEM = """You are a CMO with expertise in:
- PLG (Product-Led Growth) for B2B SaaS
- Content marketing and SEO at scale
- Community building (10K-100K members)
- Paid acquisition with positive unit economics

Your focus: ICP definition, acquisition channels, positioning,
messaging, growth loops. Provide specific, measurable tactics."""

CFO_AGENT_SYSTEM = """You are a CFO and former VC analyst with expertise in:
- SaaS financial modeling (ARR, MRR, churn, LTV/CAC)
- Fundraising (seed → Series B)
- Unit economics optimization
- Financial forecasting and scenario planning

Your focus: financial model, key metrics, fundraising strategy,
burn rate, path to profitability. Use real SaaS benchmarks."""

# ─────────────────────────────────────────────
# CHAIN-OF-THOUGHT PROMPTS
# ─────────────────────────────────────────────

MARKET_RESEARCH_COT = Prompt(
    name="market_research",
    version="v2",
    system=STARTUP_ANALYST_SYSTEM,
    user_template="""Analyze the market for this startup idea: $startup_idea

Think step by step:

<thinking>
Step 1: What problem does this solve? Who experiences this pain most acutely?
Step 2: How large is the addressable market? (TAM → SAM → SOM)
Step 3: What are the existing solutions? Why do they fall short?
Step 4: What are the strongest 3 tailwinds driving this market?
Step 5: What are the biggest 3 risks that could kill this startup?
</thinking>

<output>
## Market Analysis: $startup_idea

### TAM / SAM / SOM
[Provide specific numbers with sources]

### Key Trends (Tailwinds)
[3 specific trends with data]

### Competitive Landscape
[Real companies, their strengths and fatal weaknesses]

### Risk Assessment
[3 real risks ranked by severity]

### Verdict
[1 paragraph: should this be built? Why?]
</output>""",
)

COMPETITIVE_ANALYSIS_COT = Prompt(
    name="competitive_analysis",
    version="v1",
    system=STARTUP_ANALYST_SYSTEM,
    user_template="""Competitive analysis for: $startup_idea

<thinking>
Step 1: Map all competitors (direct, indirect, substitute solutions)
Step 2: Identify each competitor's #1 strength and #1 fatal weakness
Step 3: Find the whitespace — what is NO ONE doing well?
Step 4: Design the differentiation strategy
</thinking>

<output>
## Competitive Landscape

### Direct Competitors
$competitors_placeholder

### The Whitespace (Opportunity)
[Specific gap none of them address]

### Recommended Differentiation
[3-sentence positioning statement]
</output>""",
)

TECHNICAL_PLAN_COT = Prompt(
    name="technical_plan",
    version="v1",
    system=CTO_AGENT_SYSTEM,
    user_template="""Design the technical architecture for: $startup_idea

Tech requirements: $requirements

<thinking>
Step 1: What are the core technical problems to solve?
Step 2: MVP architecture (what to build in 3 months)
Step 3: Scale architecture (what to build in year 2)
Step 4: Build vs buy decisions for each component
Step 5: Team composition needed
</thinking>

<output>
## Technical Architecture Plan

### MVP Stack (Month 1-3)
[Specific technologies with rationale]

### Data Architecture
[Schema, storage, processing pipeline]

### ML/AI Components
[Which models, fine-tuning needed?, latency requirements]

### Security & Compliance
[Auth, encryption, relevant regulations]

### Team Needed
[Roles and hiring sequence]
</output>""",
)

PITCH_NARRATIVE_PROMPT = Prompt(
    name="pitch_narrative",
    version="v1",
    system="You are a narrative designer who has helped 200+ startups raise $2B+ total funding.",
    user_template="""Create a compelling investor pitch narrative for:

Startup: $startup_idea
Market Size: $market_size
Key Differentiator: $differentiator
Traction: $traction

The narrative must follow this arc:
1. The Hook (one shocking fact or statistic)
2. The Problem (make investors FEEL the pain)
3. The Solution (elegant, simple, inevitable)
4. Why Now (3 specific market forces converging)
5. The Ask (specific, confident, justified)

Write for a Series A pitch to Sequoia Capital.""",
)

# ─────────────────────────────────────────────
# REACT AGENT PROMPT
# ─────────────────────────────────────────────

REACT_AGENT_PROMPT = """You are a ReAct agent for startup research.
You have access to these tools: {tools}

To answer the question, use this loop:
Thought: What do I need to find out?
Action: tool_name[input]
Observation: [tool result]
... (repeat as needed)
Final Answer: [complete answer]

Question: {question}
{agent_scratchpad}"""

# ─────────────────────────────────────────────
# REGISTRY — All prompts indexed by name
# ─────────────────────────────────────────────

PROMPT_REGISTRY: dict[str, Prompt] = {
    "market_research": MARKET_RESEARCH_COT,
    "competitive_analysis": COMPETITIVE_ANALYSIS_COT,
    "technical_plan": TECHNICAL_PLAN_COT,
    "pitch_narrative": PITCH_NARRATIVE_PROMPT,
}


def get_prompt(name: str) -> Prompt:
    if name not in PROMPT_REGISTRY:
        raise KeyError(f"Prompt '{name}' not found. Available: {list(PROMPT_REGISTRY)}")
    return PROMPT_REGISTRY[name]


def demo():
    print("=" * 60)
    print("DEMO: Prompt Engineering Templates")
    print("=" * 60)

    print("\n[1] Market Research (Chain-of-Thought)")
    p = get_prompt("market_research")
    rendered = p.format(startup_idea="AI legal document analyzer")
    print(f"System: {rendered['system'][:150]}...")
    print(f"\nUser Prompt Preview:\n{rendered['user'][:400]}...")

    print("\n[2] Pitch Narrative Prompt")
    p = get_prompt("pitch_narrative")
    rendered = p.format(
        startup_idea="AI legal document analyzer",
        market_size="$45B",
        differentiator="First AI built for mid-market law firms",
        traction="50 beta users, NPS=72",
    )
    print(rendered["user"][:400])

    print("\n[3] Available Prompts:", list(PROMPT_REGISTRY.keys()))


if __name__ == "__main__":
    demo()
