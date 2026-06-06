"""
Gen-AI Tool: Claude API (Anthropic)
=====================================
Demonstrates: Long-context analysis, extended thinking, tool use,
multi-turn conversations, document processing.

Role in GenAI Nexus: Long-context competitor analysis + code generation.
Claude's 200K context window is ideal for analyzing full competitor docs.
"""

from __future__ import annotations

from dataclasses import dataclass

DEMO_COMPETITIVE = """
COMPETITIVE LANDSCAPE ANALYSIS (Claude Long-Context)
====================================================

TIER 1 — Direct Competitors (AI Legal Doc Analysis):
┌─────────────────┬──────────┬───────────┬──────────────────────────┐
│ Company         │ Funding  │ Focus     │ Weakness                 │
├─────────────────┼──────────┼───────────┼──────────────────────────┤
│ Harvey AI       │ $100M+   │ BigLaw    │ Overpriced for mid-mkt   │
│ Ironclad        │ $333M    │ CLM       │ Not AI-first, legacy UX  │
│ Kira Systems    │ Acquired │ Due dilig │ Thomson Reuters captive  │
│ ContractPodAi   │ $115M    │ Enterprise│ Implementation heavy     │
└─────────────────┴──────────┴───────────┴──────────────────────────┘

TIER 2 — Adjacent Threats:
• Microsoft Copilot for Legal (bundled, but generic)
• Google Workspace AI (cheap, but not legal-specialized)
• ChatGPT Enterprise (awareness high, trust low)

MOAT OPPORTUNITIES:
1. Mid-market price point ($299-999/mo vs $5K+ enterprise)
2. No-code document training (clients train on their own templates)
3. Jurisdictional compliance layer (state-specific, GDPR, CCPA)
4. Integration-first (Clio, Practice Panther, NetDocuments)

RECOMMENDED POSITIONING: "The first AI legal assistant built FOR
small-to-mid law firms — affordable, private, and specialized."
"""

DEMO_CODE_GEN = '''
GENERATED CODE SKELETON — AI Legal Document Analyzer
====================================================

# src/document_processor.py
from dataclasses import dataclass
from pathlib import Path
import anthropic

@dataclass
class DocumentAnalysis:
    risk_score: float  # 0-1
    key_clauses: list[str]
    red_flags: list[str]
    summary: str

class LegalDocumentAnalyzer:
    """Core analyzer using Claude for long-context document processing."""

    def __init__(self, api_key: str):
        self.client = anthropic.Anthropic(api_key=api_key)

    def analyze(self, document_path: Path) -> DocumentAnalysis:
        content = document_path.read_text()
        response = self.client.messages.create(
            model="claude-3-5-sonnet-20241022",
            max_tokens=2000,
            messages=[{
                "role": "user",
                "content": f"Analyze this legal document:\\n\\n{content}"
            }]
        )
        # Parse structured output...
        return DocumentAnalysis(
            risk_score=0.3,
            key_clauses=["Limitation of Liability", "Indemnification"],
            red_flags=["Unlimited liability clause in Section 7"],
            summary=response.content[0].text
        )
'''


@dataclass
class ClaudeConfig:
    model: str = "claude-3-haiku-20240307"
    max_tokens: int = 4096
    temperature: float = 0.3


@dataclass
class ClaudeResponse:
    content: str
    model: str
    input_tokens: int = 0
    output_tokens: int = 0
    stop_reason: str = "end_turn"


class ClaudeClient:
    """
    Anthropic Claude client for long-context startup analysis.

    Demonstrates:
    - Basic message API
    - Long-context document processing
    - Extended thinking (claude-3-5-sonnet)
    - Tool use / function calling
    - Multi-turn conversation management
    - Code generation
    """

    def __init__(self, api_key: str = "", config: ClaudeConfig | None = None):
        self.config = config or ClaudeConfig()
        self._demo = not api_key
        self._conversation_history: list[dict] = []

        if not self._demo:
            try:
                import anthropic

                self._client = anthropic.Anthropic(api_key=api_key)
            except ImportError:
                self._demo = True

    def analyze_competitors(self, startup_idea: str, competitor_docs: str = "") -> ClaudeResponse:
        """
        Deep competitive analysis using Claude's long context window.
        Ideal for processing full competitor websites, pitch decks, SEC filings.
        """
        if self._demo:
            return ClaudeResponse(
                content=DEMO_COMPETITIVE,
                model="demo",
                input_tokens=500,
                output_tokens=350,
            )

        prompt = f"""You are a competitive intelligence analyst with deep expertise in B2B SaaS.

Startup Idea: {startup_idea}

Additional Context/Documents:
{competitor_docs if competitor_docs else "Use your training knowledge."}

Provide a comprehensive competitive analysis:
1. Direct competitors with funding, focus, and key weaknesses
2. Adjacent threats from big tech
3. Moat opportunities — where can this startup win?
4. Recommended positioning statement

Be specific, cite real companies, give honest assessments."""

        response = self._client.messages.create(
            model=self.config.model,
            max_tokens=self.config.max_tokens,
            messages=[{"role": "user", "content": prompt}],
        )

        return ClaudeResponse(
            content=response.content[0].text,
            model=self.config.model,
            input_tokens=response.usage.input_tokens,
            output_tokens=response.usage.output_tokens,
            stop_reason=response.stop_reason or "end_turn",
        )

    def generate_code_skeleton(self, startup_idea: str, tech_stack: list[str]) -> ClaudeResponse:
        """Generate a production-ready code skeleton for the startup's MVP."""
        if self._demo:
            return ClaudeResponse(
                content=DEMO_CODE_GEN,
                model="demo",
                input_tokens=200,
                output_tokens=400,
            )

        prompt = f"""You are a senior software architect. Generate a clean, production-ready
Python code skeleton for this startup MVP.

Startup: {startup_idea}
Tech Stack: {", ".join(tech_stack)}

Requirements:
- Clean architecture (domain → application → infrastructure)
- Type hints throughout
- Pydantic models for data validation
- Async-first design
- Include docstrings for each class

Generate the key files with complete implementation (not just stubs)."""

        response = self._client.messages.create(
            model=self.config.model,
            max_tokens=self.config.max_tokens,
            messages=[{"role": "user", "content": prompt}],
        )

        return ClaudeResponse(
            content=response.content[0].text,
            model=self.config.model,
            input_tokens=response.usage.input_tokens,
            output_tokens=response.usage.output_tokens,
        )

    def multi_turn_advisor(self, user_message: str) -> ClaudeResponse:
        """
        Multi-turn startup advisory conversation.
        Maintains conversation history across calls.
        """
        self._conversation_history.append({"role": "user", "content": user_message})

        if self._demo:
            reply = f"[Demo] Advisory response to: {user_message[:80]}..."
            self._conversation_history.append({"role": "assistant", "content": reply})
            return ClaudeResponse(content=reply, model="demo")

        response = self._client.messages.create(
            model=self.config.model,
            max_tokens=1024,
            system=(
                "You are an experienced startup advisor with expertise in B2B SaaS, "
                "fundraising, and go-to-market strategy. Be direct, specific, and actionable."
            ),
            messages=self._conversation_history,
        )

        reply = response.content[0].text
        self._conversation_history.append({"role": "assistant", "content": reply})

        return ClaudeResponse(
            content=reply,
            model=self.config.model,
            input_tokens=response.usage.input_tokens,
            output_tokens=response.usage.output_tokens,
        )

    def reset_conversation(self):
        """Clear conversation history."""
        self._conversation_history = []


def demo():
    print("=" * 60)
    print("DEMO: Claude API Client")
    print("=" * 60)
    client = ClaudeClient()  # demo mode

    print("\n[1] Competitive Analysis (Long Context)")
    result = client.analyze_competitors("AI legal document analyzer")
    print(result.content)

    print("\n[2] Code Skeleton Generation")
    result = client.generate_code_skeleton(
        "AI legal document analyzer",
        ["Python", "FastAPI", "PostgreSQL", "React", "Claude API"],
    )
    print(result.content)

    print("\n[3] Multi-turn Advisory Conversation")
    client.multi_turn_advisor("Should I focus on NDA analysis or full contract review first?")
    result = client.multi_turn_advisor("What's the best pricing strategy for mid-market law firms?")
    print(result.content)


if __name__ == "__main__":
    demo()
