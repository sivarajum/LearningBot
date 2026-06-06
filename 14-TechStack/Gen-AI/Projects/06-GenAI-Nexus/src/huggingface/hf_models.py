"""
Gen-AI Tool: HuggingFace Transformers
========================================
Demonstrates: HuggingFace pipeline API, sentiment analysis,
NER with transformers, text classification, zero-shot classification,
and model inference patterns.

Role in GenAI Nexus: Analyze sentiment of market news about the startup's
sector, classify competitor mentions, extract entities from news articles.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any

# Demo responses (used when transformers not available)
DEMO_SENTIMENT_RESULTS = [
    {"label": "POSITIVE", "score": 0.9234, "text": "Legal tech AI market booming..."},
    {"label": "NEGATIVE", "score": 0.8120, "text": "Lawyers resist AI adoption..."},
    {"label": "POSITIVE", "score": 0.7890, "text": "Harvey AI raises $100M Series B..."},
]

DEMO_ZERO_SHOT = {
    "sequence": "AI legal document analyzer for law firms",
    "labels": ["legal tech", "fintech", "healthtech", "edtech"],
    "scores": [0.892, 0.053, 0.031, 0.024],
}

DEMO_NER = [
    {"entity": "ORG", "word": "Harvey AI", "score": 0.99},
    {"entity": "MONEY", "word": "$100M", "score": 0.97},
    {"entity": "LOC", "word": "San Francisco", "score": 0.95},
]


@dataclass
class SentimentResult:
    text: str
    label: str  # POSITIVE | NEGATIVE | NEUTRAL
    score: float
    compound: float = 0.0  # -1 to 1


@dataclass
class ClassificationResult:
    text: str
    predicted_label: str
    scores: dict[str, float] = field(default_factory=dict)


@dataclass
class NERResult:
    text: str
    entities: list[dict[str, Any]] = field(default_factory=list)


class HuggingFaceModels:
    """
    HuggingFace model hub integration for startup news analysis.

    Demonstrates:
    - Sentiment pipeline (distilbert-base-uncased-finetuned-sst-2-english)
    - NER pipeline (dbmdz/bert-large-cased-finetuned-conll03-english)
    - Zero-shot classification (facebook/bart-large-mnli)
    - Text summarization (sshleifer/distilbart-cnn-12-6)
    - Batch inference patterns
    """

    def __init__(self, use_gpu: bool = False, lazy_load: bool = True):
        self._demo = True
        self._device = 0 if use_gpu else -1  # -1 = CPU
        self._pipelines: dict[str, Any] = {}

        if not lazy_load:
            self._init_pipelines()
        else:
            self._try_init_sentiment()

    def _try_init_sentiment(self):
        """Try to load sentiment pipeline (smallest, most likely available)."""
        try:
            from transformers import pipeline

            self._pipelines["sentiment"] = pipeline(
                "sentiment-analysis",
                model="distilbert-base-uncased-finetuned-sst-2-english",
                device=self._device,
            )
            self._demo = False
        except (ImportError, Exception):
            pass  # Stay in demo mode

    def _init_pipelines(self):
        """Initialize all pipelines (heavy — only on demand)."""
        try:
            from transformers import pipeline

            self._pipelines["sentiment"] = pipeline(
                "sentiment-analysis",
                model="distilbert-base-uncased-finetuned-sst-2-english",
                device=self._device,
            )
            self._pipelines["ner"] = pipeline(
                "ner",
                model="dbmdz/bert-large-cased-finetuned-conll03-english",
                aggregation_strategy="simple",
                device=self._device,
            )
            self._pipelines["zero_shot"] = pipeline(
                "zero-shot-classification",
                model="facebook/bart-large-mnli",
                device=self._device,
            )
            self._pipelines["summarizer"] = pipeline(
                "summarization",
                model="sshleifer/distilbart-cnn-12-6",
                device=self._device,
            )
            self._demo = False
        except (ImportError, Exception):
            pass

    def analyze_sentiment(self, texts: list[str]) -> list[SentimentResult]:
        """
        Analyze sentiment of market news headlines.
        Returns positive/negative scores for market trend analysis.
        """
        if self._demo or "sentiment" not in self._pipelines:
            return [
                SentimentResult(
                    text=t,
                    label="POSITIVE" if i % 2 == 0 else "NEGATIVE",
                    score=0.85 + (i * 0.01),
                    compound=0.7 - (i * 0.1),
                )
                for i, t in enumerate(texts)
            ]

        results = self._pipelines["sentiment"](texts, batch_size=8, truncation=True)
        return [
            SentimentResult(
                text=text,
                label=r["label"],
                score=round(r["score"], 4),
                compound=round(r["score"] if r["label"] == "POSITIVE" else -r["score"], 4),
            )
            for text, r in zip(texts, results)
        ]

    def extract_entities(self, text: str) -> NERResult:
        """Extract named entities (companies, people, money, locations)."""
        if self._demo or "ner" not in self._pipelines:
            return NERResult(text=text, entities=DEMO_NER)

        raw = self._pipelines["ner"](text[:512])  # truncate for speed
        entities = [
            {
                "entity": e["entity_group"],
                "word": e["word"],
                "score": round(e["score"], 4),
                "start": e["start"],
                "end": e["end"],
            }
            for e in raw
        ]
        return NERResult(text=text, entities=entities)

    def classify_domain(self, text: str, candidate_labels: list[str] | None = None) -> ClassificationResult:
        """
        Zero-shot classify text into domain categories.
        No fine-tuning needed — BART-MNLI handles unseen labels.
        """
        labels = candidate_labels or [
            "legal tech", "fintech", "healthtech", "edtech",
            "enterprise SaaS", "consumer app", "infrastructure",
        ]

        if self._demo or "zero_shot" not in self._pipelines:
            scores = {label: round(0.9 - i * 0.1, 3) for i, label in enumerate(labels)}
            return ClassificationResult(
                text=text,
                predicted_label=labels[0],
                scores=scores,
            )

        result = self._pipelines["zero_shot"](
            text[:512], candidate_labels=labels, multi_label=False
        )
        scores = dict(zip(result["labels"], result["scores"]))
        return ClassificationResult(
            text=text,
            predicted_label=result["labels"][0],
            scores={k: round(v, 4) for k, v in scores.items()},
        )

    def summarize_article(self, text: str, max_length: int = 150) -> str:
        """Summarize long news article to key points."""
        if self._demo or "summarizer" not in self._pipelines:
            words = text.split()[:50]
            return " ".join(words) + " [... auto-summarized]"

        result = self._pipelines["summarizer"](
            text[:1024],
            max_length=max_length,
            min_length=30,
            do_sample=False,
        )
        return result[0]["summary_text"]

    def market_sentiment_score(self, headlines: list[str]) -> dict[str, float]:
        """
        Aggregate market sentiment score from a list of headlines.
        Returns overall market sentiment for the startup's sector.
        """
        sentiments = self.analyze_sentiment(headlines)
        if not sentiments:
            return {"overall": 0.0, "positive_pct": 0.0, "negative_pct": 0.0}

        positive = [s for s in sentiments if s.label == "POSITIVE"]
        negative = [s for s in sentiments if s.label == "NEGATIVE"]

        overall_compound = sum(s.compound for s in sentiments) / len(sentiments)

        return {
            "overall": round(overall_compound, 4),
            "positive_pct": round(len(positive) / len(sentiments), 4),
            "negative_pct": round(len(negative) / len(sentiments), 4),
            "total_analyzed": len(sentiments),
            "interpretation": (
                "BULLISH" if overall_compound > 0.3
                else "BEARISH" if overall_compound < -0.3
                else "NEUTRAL"
            ),
        }


def demo():
    print("=" * 60)
    print("DEMO: HuggingFace Models")
    print("=" * 60)
    hf = HuggingFaceModels()

    # Sample legal tech news headlines
    headlines = [
        "Harvey AI raises $100M Series B as BigLaw embraces AI tools",
        "Legal professionals skeptical of AI accuracy in complex cases",
        "AI document review cuts costs by 90% for mid-market law firms",
        "State bars issue warnings about AI ethics in legal practice",
        "LegalTech investment hits record $2.1B in 2023",
        "Small law firms struggle to afford enterprise AI solutions",
    ]

    print("\n[1] Sentiment Analysis — Legal Tech News")
    sentiments = hf.analyze_sentiment(headlines)
    for s in sentiments:
        emoji = "🟢" if s.label == "POSITIVE" else "🔴"
        print(f"  {emoji} [{s.label}:{s.score:.3f}] {s.text[:60]}...")

    print("\n[2] Market Sentiment Score")
    score = hf.market_sentiment_score(headlines)
    print(f"  Overall compound: {score['overall']}")
    print(f"  Positive: {score['positive_pct']:.0%} | Negative: {score['negative_pct']:.0%}")
    print(f"  Market interpretation: {score['interpretation']}")

    print("\n[3] Domain Classification (Zero-Shot)")
    idea = "AI-powered legal document analyzer for law firms"
    result = hf.classify_domain(idea)
    print(f"  Input: {idea}")
    print(f"  Predicted: {result.predicted_label}")
    print("  All scores:")
    for label, score_val in sorted(result.scores.items(), key=lambda x: x[1], reverse=True)[:4]:
        print(f"    {label}: {score_val:.3f}")

    print("\n[4] Named Entity Recognition")
    news = "Harvey AI, backed by OpenAI and Sequoia, raised $100M in San Francisco."
    ner_result = hf.extract_entities(news)
    print(f"  Text: {news}")
    print("  Entities:")
    for ent in ner_result.entities:
        print(f"    [{ent['entity']}] {ent['word']} (score={ent['score']:.3f})")

    print("\n[5] Article Summarization")
    long_text = """
    The legal technology market continues to evolve rapidly as artificial intelligence
    transforms how law firms operate. Harvey AI, founded in 2022 by former Google and
    Casetext engineers, has emerged as a leading AI legal assistant used by over 100
    BigLaw firms globally. The company's focus on large law firms with 500+ attorneys
    has created a significant gap in the market for mid-size and solo practitioners.
    Industry analysts estimate that 80% of law firms have fewer than 10 attorneys but
    only 25% of legal tech spending, representing a massive underserved opportunity.
    """
    summary = hf.summarize_article(long_text)
    print(f"  Summary: {summary}")


if __name__ == "__main__":
    demo()
