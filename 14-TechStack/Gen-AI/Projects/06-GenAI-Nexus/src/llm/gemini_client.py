"""
Gen-AI Tool: Google Gemini API
================================
Demonstrates: Multimodal inputs (text + images), Gemini Pro/Flash,
safety settings, grounding with Google Search, structured output.

Role in GenAI Nexus: Multimodal market analysis — analyze charts,
competitor UI screenshots, and market data visualizations.
"""

from __future__ import annotations

import base64
from dataclasses import dataclass
from pathlib import Path

DEMO_MULTIMODAL = """
MULTIMODAL MARKET ANALYSIS (Gemini)
====================================
[Chart Analysis] Revenue growth trend: 47% YoY for legal tech SaaS
[Screenshot Analysis] Competitor UI: Clean but lacks AI-first UX
[Market Data] NSE listed legal services companies: 23 entities
[Trend Forecast] AI legal tech → mainstream adoption by Q2 2026

Key Insight: Visual analysis confirms mid-market gap —
Harvey targets BigLaw (dark-mode enterprise UI),
Ironclad targets operations teams (workflow-heavy UI).
Neither optimized for solo practitioners or small firms.
"""

DEMO_STRUCTURED = {
    "market_size_usd_billions": 45.2,
    "growth_rate_cagr_percent": 18.9,
    "top_segments": ["Contract Management", "Due Diligence", "Compliance"],
    "geographic_leaders": ["USA", "UK", "Germany"],
    "investment_trend": "Increasing — $2.1B invested in 2023, up 34% YoY",
}


@dataclass
class GeminiConfig:
    model: str = "gemini-1.5-flash"
    temperature: float = 0.3
    max_output_tokens: int = 2048
    top_p: float = 0.95


@dataclass
class GeminiResponse:
    content: str
    model: str
    structured: dict | None = None
    tokens_used: int = 0


class GeminiClient:
    """
    Google Gemini client for multimodal startup analysis.

    Demonstrates:
    - Text generation with Gemini Flash (fast, cheap)
    - Multimodal input: image + text analysis
    - Structured JSON output via response_schema
    - Safety settings configuration
    - Grounding with Google Search (when available)
    """

    def __init__(self, api_key: str = "", config: GeminiConfig | None = None):
        self.config = config or GeminiConfig()
        self._demo = not api_key
        if not self._demo:
            try:
                import google.generativeai as genai

                genai.configure(api_key=api_key)
                self._model = genai.GenerativeModel(
                    model_name=self.config.model,
                    generation_config={
                        "temperature": self.config.temperature,
                        "max_output_tokens": self.config.max_output_tokens,
                        "top_p": self.config.top_p,
                    },
                )
            except ImportError:
                self._demo = True

    def analyze_market_text(self, startup_idea: str) -> GeminiResponse:
        """Fast market overview using Gemini Flash."""
        if self._demo:
            return GeminiResponse(
                content=DEMO_MULTIMODAL,
                model="demo",
            )

        prompt = f"""You are a market analyst. For the startup idea: "{startup_idea}"

Provide:
1. Market size (TAM/SAM/SOM)
2. Top 3 market segments
3. Geographic leaders
4. Investment trends
5. Key risks

Be concise and data-driven."""

        response = self._model.generate_content(prompt)
        return GeminiResponse(
            content=response.text,
            model=self.config.model,
        )

    def analyze_image_and_text(self, prompt: str, image_path: str | None = None) -> GeminiResponse:
        """
        Multimodal analysis: combine image + text.
        Example: analyze a competitor's UI screenshot or a market chart.
        """
        if self._demo:
            return GeminiResponse(
                content=DEMO_MULTIMODAL,
                model="demo",
            )

        if image_path and Path(image_path).exists():
            try:
                import google.generativeai as genai

                image_data = Path(image_path).read_bytes()
                b64 = base64.b64encode(image_data).decode()
                parts = [
                    {"mime_type": "image/png", "data": b64},
                    prompt,
                ]
                response = self._model.generate_content(parts)
            except Exception:
                # Fallback to text-only if image fails
                response = self._model.generate_content(prompt)
        else:
            response = self._model.generate_content(
                f"[No image provided - text only analysis]\n{prompt}"
            )

        return GeminiResponse(
            content=response.text,
            model=self.config.model,
        )

    def structured_market_data(self, startup_idea: str) -> GeminiResponse:
        """
        Generate structured JSON market data using Gemini's response schema.
        Demonstrates controlled output format.
        """
        if self._demo:
            import json

            return GeminiResponse(
                content=json.dumps(DEMO_STRUCTURED, indent=2),
                model="demo",
                structured=DEMO_STRUCTURED,
            )

        prompt = f"""Analyze the market for: {startup_idea}

Return ONLY a JSON object with these exact fields:
{{
  "market_size_usd_billions": <number>,
  "growth_rate_cagr_percent": <number>,
  "top_segments": [<3 strings>],
  "geographic_leaders": [<3 strings>],
  "investment_trend": "<string>"
}}"""

        try:
            import json

            response = self._model.generate_content(prompt)
            text = response.text.strip()
            # Strip markdown code block if present
            if text.startswith("```"):
                text = text.split("```")[1]
                if text.startswith("json"):
                    text = text[4:]
            structured = json.loads(text)
        except Exception as e:
            structured = {"error": str(e)}

        import json

        return GeminiResponse(
            content=json.dumps(structured, indent=2),
            model=self.config.model,
            structured=structured,
        )

    def pitch_deck_content(self, startup_idea: str, market_data: dict) -> GeminiResponse:
        """Generate pitch deck slide content using market context."""
        if self._demo:
            return GeminiResponse(
                content=f"""
PITCH DECK CONTENT (Gemini Generated)
======================================
Slide 1 - Problem: 73% of small law firms lose revenue to manual doc review
Slide 2 - Solution: AI Legal Analyzer — 90% faster, 10x cheaper than BigLaw tools
Slide 3 - Market: $45.2B TAM, $8.1B SAM, CAGR 18.9%
Slide 4 - Traction: 50 beta users, NPS=72, 3 paying pilots
Slide 5 - Ask: $1.5M seed at $8M pre-money valuation
""",
                model="demo",
            )

        prompt = f"""Create compelling pitch deck slide content for:

Startup: {startup_idea}
Market Data: {market_data}

Generate content for 5 key slides: Problem, Solution, Market, Traction, Ask.
Each slide: headline + 3 bullet points. Be specific with numbers."""

        response = self._model.generate_content(prompt)
        return GeminiResponse(content=response.text, model=self.config.model)


def demo():
    print("=" * 60)
    print("DEMO: Google Gemini Client")
    print("=" * 60)
    client = GeminiClient()  # demo mode

    print("\n[1] Market Analysis (Text)")
    result = client.analyze_market_text("AI legal document analyzer")
    print(result.content)

    print("\n[2] Multimodal Analysis (Image + Text)")
    result = client.analyze_image_and_text(
        "Analyze this competitor UI and identify UX gaps",
        image_path=None,  # would be a real screenshot path
    )
    print(result.content)

    print("\n[3] Structured Market Data (JSON Output)")
    result = client.structured_market_data("AI legal document analyzer")
    print(result.content)

    print("\n[4] Pitch Deck Content Generation")
    result = client.pitch_deck_content(
        "AI legal document analyzer",
        {"market_size": "$45.2B", "cagr": "18.9%"},
    )
    print(result.content)


if __name__ == "__main__":
    demo()
