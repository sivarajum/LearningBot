"""
Gen-AI Tool: Few-Shot & Zero-Shot Prompting
=============================================
Demonstrates: Few-shot example selection, domain-specific examples,
dynamic example retrieval, zero-shot CoT, self-consistency.

Role in GenAI Nexus: Domain-specific examples for each analysis task
that dramatically improve LLM output quality for startup analysis.
"""

from __future__ import annotations

from dataclasses import dataclass


@dataclass
class Example:
    """A single few-shot example."""

    input: str
    output: str
    metadata: dict | None = None


# ─────────────────────────────────────────────
# FEW-SHOT EXAMPLES BY DOMAIN
# ─────────────────────────────────────────────

MARKET_SIZING_EXAMPLES: list[Example] = [
    Example(
        input="What is the TAM for AI-powered HR software?",
        output="""TAM: $376B (global HR software market 2024, Gartner)
SAM: $45B (AI-enhanced HRIS + ATS segment)
SOM: $450M (realistic 3-year capture, 1% SAM with focused ICP)

Calculation:
- 500K companies with 50-500 employees globally
- Average HR software spend: $75K/year
- AI premium: 1.3x multiplier
- TAM = 500K × $75K × 1.3 = $48.75B (cross-check vs Gartner ✓)""",
        metadata={"domain": "hr_tech", "method": "bottom_up"},
    ),
    Example(
        input="What is the TAM for AI-powered legal document analysis?",
        output="""TAM: $45.2B (global legal technology market 2024, Statista)
SAM: $8.1B (contract management + document automation sub-segment)
SOM: $81M (Year 1 realistic, 1% SAM in mid-market US/UK)

Calculation:
- 450K law firms globally (US: 180K, UK: 11K, rest: 260K)
- Avg annual software spend per firm: $18K (US solo/small firm average)
- AI adoption premium: 1.5x by 2026
- Bottom-up TAM = 450K × $18K × 1.5 = $12.15B
- Blended with top-down $45.2B = $28.6B (conservative estimate used)""",
        metadata={"domain": "legal_tech", "method": "blended"},
    ),
]

COMPETITIVE_MOAT_EXAMPLES: list[Example] = [
    Example(
        input="What are Stripe's competitive moats?",
        output="""Stripe's moats (strongest to weakest):

1. DATA MOAT (strongest): Processes $1T+/yr. Fraud patterns, conversion
   benchmarks, and payment behavior insights no competitor can replicate.
   Switching cost: ALL historical transaction data stays with Stripe.

2. NETWORK MOAT: Stripe Atlas, Stripe Treasury, Stripe Capital create
   ecosystem lock-in. Once you use Atlas to incorporate, you're on Stripe.

3. DEVELOPER MOAT: Best-in-class docs + SDK. Millions of developers
   prefer Stripe. This is a hiring/talent moat for companies using Stripe.

4. SWITCHING COST: Payment integration is 3-12 months of engineering work.
   Token vaulting means customer card data can't easily move to competitors.

Fatal weakness: Enterprise procurement process (vs Adyen's white-glove).
""",
        metadata={"company": "stripe", "stage": "late"},
    ),
    Example(
        input="What competitive moats should an AI legal doc startup build?",
        output="""Recommended moats in build sequence:

1. DATA MOAT (build first): Every document analyzed trains your models.
   Collect anonymized clause data, risk patterns, negotiation outcomes.
   After 1M documents: your AI outperforms any generic LLM.
   Switching cost: "Your AI knows your firm's preferred clause language"

2. WORKFLOW MOAT (month 6): Deep integration into Clio, PracticePanther,
   NetDocuments. When AI lives inside existing workflows, switching = pain.

3. COMMUNITY MOAT (month 12): Build community of solo/small firm lawyers
   who share templates, playbooks. Network effects make platform sticky.

4. COMPLIANCE MOAT (year 2): First to achieve SOC2 + ABA ethics opinion
   for AI legal tools. Becomes procurement requirement for clients.
""",
        metadata={"stage": "seed", "domain": "legal_tech"},
    ),
]

PITCH_NARRATIVE_EXAMPLES: list[Example] = [
    Example(
        input="Write a 30-second elevator pitch for AI legal doc analyzer",
        output="""Every year, small law firms leave $50,000 on the table because
their lawyers spend 40% of their time reading contracts instead of
practicing law. We built LegalAI — the first AI document analyzer
designed specifically for firms with 1-50 lawyers. It reviews an NDA
in 90 seconds, flags every risk clause, and suggests better language —
for $299 a month, not $5,000. We have 50 beta users, 85% retention,
and an NPS of 72. We're raising $1.5M to reach 500 paying customers
by end of year.""",
        metadata={"format": "elevator_pitch", "duration": "30s"},
    ),
]

# ─────────────────────────────────────────────
# FEW-SHOT PROMPT BUILDER
# ─────────────────────────────────────────────


class FewShotBuilder:
    """
    Builds few-shot prompts dynamically.

    Demonstrates:
    - Static few-shot examples
    - Dynamic example selection by domain
    - Zero-shot chain-of-thought
    - Self-consistency sampling
    """

    def __init__(self):
        self._examples: dict[str, list[Example]] = {
            "market_sizing": MARKET_SIZING_EXAMPLES,
            "competitive_moat": COMPETITIVE_MOAT_EXAMPLES,
            "pitch_narrative": PITCH_NARRATIVE_EXAMPLES,
        }

    def build_few_shot_prompt(
        self, task: str, query: str, n_examples: int = 2
    ) -> str:
        """Build a few-shot prompt for the given task."""
        examples = self._examples.get(task, [])[:n_examples]

        prompt_parts = [
            f"Here are {len(examples)} examples of high-quality {task} analysis:\n"
        ]

        for i, ex in enumerate(examples, 1):
            prompt_parts.append(f"Example {i}:")
            prompt_parts.append(f"Input: {ex.input}")
            prompt_parts.append(f"Output: {ex.output}\n")

        prompt_parts.append("Now apply the same reasoning style to:")
        prompt_parts.append(f"Input: {query}")
        prompt_parts.append("Output:")

        return "\n".join(prompt_parts)

    def build_zero_shot_cot(self, query: str) -> str:
        """Zero-shot chain-of-thought: 'Let's think step by step'."""
        return f"""{query}

Let's think step by step:
1. First, let me identify the key factors...
2. Then, I'll quantify the market opportunity...
3. Next, I'll assess competitive dynamics...
4. Finally, I'll synthesize a recommendation...
"""

    def self_consistency_prompt(self, query: str, n_paths: int = 3) -> list[str]:
        """
        Generate N independent reasoning paths for the same query.
        Majority vote on the final answer increases accuracy.
        """
        return [
            f"[Reasoning Path {i}] {query}\nApproach: {approach}"
            for i, approach in enumerate(
                [
                    "Bottom-up market sizing → competitive mapping → risk weighting",
                    "Top-down TAM reduction → ICP identification → beachhead strategy",
                    "Analogous market analysis → growth rate benchmarking → scenario modeling",
                ][:n_paths],
                1,
            )
        ]

    def add_examples(self, task: str, examples: list[Example]) -> None:
        """Add new domain examples at runtime."""
        if task not in self._examples:
            self._examples[task] = []
        self._examples[task].extend(examples)

    def list_tasks(self) -> list[str]:
        return list(self._examples.keys())


def demo():
    print("=" * 60)
    print("DEMO: Few-Shot & Zero-Shot Prompting")
    print("=" * 60)
    builder = FewShotBuilder()

    print("\n[1] Few-Shot Market Sizing Prompt")
    prompt = builder.build_few_shot_prompt(
        task="market_sizing",
        query="What is the TAM for AI-powered legal document analysis?",
        n_examples=1,
    )
    print(prompt[:600] + "...")

    print("\n[2] Zero-Shot Chain-of-Thought")
    cot = builder.build_zero_shot_cot("How should an AI legal startup price its product?")
    print(cot)

    print("\n[3] Self-Consistency (3 reasoning paths)")
    paths = builder.self_consistency_prompt("What is the best go-to-market for legal AI?")
    for path in paths:
        print(f"  • {path[:100]}...")

    print("\n[4] Available Tasks:", builder.list_tasks())


if __name__ == "__main__":
    demo()
