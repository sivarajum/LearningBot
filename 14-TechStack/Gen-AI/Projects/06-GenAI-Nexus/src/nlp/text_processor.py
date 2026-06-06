"""
Gen-AI Tool: NLP (Natural Language Processing)
================================================
Demonstrates: Text preprocessing, Named Entity Recognition (spaCy),
keyword extraction, text summarization, sentiment prep,
sentence tokenization, and text cleaning pipeline.

Role in GenAI Nexus: Preprocesses raw startup idea text before feeding
to LLMs — extracts entities, keywords, cleans noise.
"""

from __future__ import annotations

import re
from dataclasses import dataclass, field


@dataclass
class ProcessedText:
    """Output of NLP pipeline."""

    original: str
    cleaned: str
    tokens: list[str] = field(default_factory=list)
    sentences: list[str] = field(default_factory=list)
    entities: list[dict[str, str]] = field(default_factory=list)  # [{text, label}]
    keywords: list[str] = field(default_factory=list)
    word_count: int = 0
    language: str = "en"


class TextProcessor:
    """
    NLP text processing pipeline using spaCy + regex fallbacks.

    Demonstrates:
    - Text cleaning (HTML removal, normalization)
    - Tokenization and sentence splitting
    - Named Entity Recognition (ORG, PRODUCT, MONEY, GPE)
    - Keyword extraction (TF-IDF style scoring)
    - Domain-specific entity detection for startups
    """

    def __init__(self, use_spacy: bool = True):
        self._nlp = None
        if use_spacy:
            try:
                import spacy

                try:
                    self._nlp = spacy.load("en_core_web_sm")
                except OSError:
                    # Model not downloaded yet
                    pass
            except ImportError:
                pass

        # Startup domain vocabulary for keyword scoring boost
        self._domain_terms = {
            "saas", "api", "ai", "ml", "nlp", "llm", "b2b", "b2c",
            "mvp", "arr", "mrr", "churn", "nps", "cac", "ltv", "vc",
            "seed", "series", "pivot", "moat", "tam", "sam", "som",
            "legal", "contract", "document", "analyzer", "automation",
            "compliance", "workflow", "integration",
        }

    def clean(self, text: str) -> str:
        """Remove HTML, normalize whitespace, fix encoding."""
        # Strip HTML tags
        text = re.sub(r"<[^>]+>", " ", text)
        # Remove URLs
        text = re.sub(r"https?://\S+", "[URL]", text)
        # Normalize whitespace
        text = re.sub(r"\s+", " ", text)
        # Fix common encoding artifacts
        text = text.replace("\u2019", "'").replace("\u201c", '"').replace("\u201d", '"')
        return text.strip()

    def tokenize(self, text: str) -> list[str]:
        """Word tokenization — spaCy or fallback."""
        if self._nlp:
            doc = self._nlp(text)
            return [token.text for token in doc if not token.is_space]
        # Simple regex fallback
        return re.findall(r"\b\w+\b", text)

    def split_sentences(self, text: str) -> list[str]:
        """Sentence splitting — spaCy or regex fallback."""
        if self._nlp:
            doc = self._nlp(text)
            return [sent.text.strip() for sent in doc.sents]
        # Regex fallback
        sentences = re.split(r"(?<=[.!?])\s+", text)
        return [s.strip() for s in sentences if s.strip()]

    def extract_entities(self, text: str) -> list[dict[str, str]]:
        """
        Named Entity Recognition using spaCy.
        Detects: ORG, PRODUCT, MONEY, GPE, PERSON, DATE
        """
        if self._nlp:
            doc = self._nlp(text)
            return [
                {"text": ent.text, "label": ent.label_, "description": ent.label}
                for ent in doc.ents
                if ent.label_ in {"ORG", "PRODUCT", "MONEY", "GPE", "PERSON", "DATE", "PERCENT"}
            ]

        # Fallback: regex-based extraction for key patterns
        entities = []

        # Money patterns ($45B, $1.5M, ₹5K)
        for match in re.finditer(r"[\$₹€£]\d+(?:\.\d+)?[BMKbmk]?", text):
            entities.append({"text": match.group(), "label": "MONEY", "description": "Currency"})

        # Percentage patterns
        for match in re.finditer(r"\d+(?:\.\d+)?%", text):
            entities.append({"text": match.group(), "label": "PERCENT", "description": "Percentage"})

        # Known company patterns (capitalized sequences)
        for match in re.finditer(r"\b[A-Z][a-z]+ (?:AI|Tech|Labs|Systems|Inc|Ltd)\b", text):
            entities.append({"text": match.group(), "label": "ORG", "description": "Organization"})

        return entities

    def extract_keywords(self, text: str, top_n: int = 10) -> list[str]:
        """
        Keyword extraction using term frequency + domain boosting.
        No TF-IDF corpus needed — simple but effective for startup text.
        """
        tokens = self.tokenize(text.lower())

        # Stop words
        stop_words = {
            "the", "a", "an", "and", "or", "but", "in", "on", "at", "to",
            "for", "of", "with", "by", "from", "is", "are", "was", "were",
            "be", "been", "have", "has", "had", "do", "does", "did", "will",
            "would", "could", "should", "may", "might", "this", "that",
            "these", "those", "it", "its", "we", "you", "they", "their",
        }

        # Count term frequency
        freq: dict[str, float] = {}
        for token in tokens:
            if len(token) < 3 or token in stop_words:
                continue
            freq[token] = freq.get(token, 0) + 1

        # Boost domain terms
        for term in self._domain_terms:
            if term in freq:
                freq[term] *= 2.0

        # Sort by score
        sorted_terms = sorted(freq.items(), key=lambda x: x[1], reverse=True)
        return [term for term, _ in sorted_terms[:top_n]]

    def process(self, text: str) -> ProcessedText:
        """Full NLP pipeline — clean → tokenize → entities → keywords."""
        cleaned = self.clean(text)
        tokens = self.tokenize(cleaned)
        sentences = self.split_sentences(cleaned)
        entities = self.extract_entities(cleaned)
        keywords = self.extract_keywords(cleaned)

        return ProcessedText(
            original=text,
            cleaned=cleaned,
            tokens=tokens,
            sentences=sentences,
            entities=entities,
            keywords=keywords,
            word_count=len(tokens),
        )

    def extract_startup_components(self, idea: str) -> dict[str, str]:
        """
        Domain-specific extraction for startup idea text.
        Identifies: problem, solution, target customer, tech.
        """
        result: dict[str, str] = {
            "problem": "",
            "solution": "",
            "customer": "",
            "technology": "",
            "market": "",
        }

        idea_lower = idea.lower()

        # Problem signals
        problem_phrases = ["problem", "pain", "struggle", "difficult", "waste", "lose", "manual"]
        for phrase in problem_phrases:
            if phrase in idea_lower:
                result["problem"] = f"Detected problem signal: '{phrase}'"
                break

        # Technology signals
        tech_keywords = ["ai", "ml", "nlp", "llm", "blockchain", "api", "cloud", "saas"]
        detected_tech = [kw for kw in tech_keywords if kw in idea_lower]
        result["technology"] = ", ".join(detected_tech) if detected_tech else "Not specified"

        # Customer signals
        if any(w in idea_lower for w in ["law firm", "lawyer", "attorney", "legal"]):
            result["customer"] = "Legal professionals"
        elif any(w in idea_lower for w in ["hospital", "doctor", "patient", "medical"]):
            result["customer"] = "Healthcare professionals"
        elif any(w in idea_lower for w in ["finance", "bank", "trading", "investment"]):
            result["customer"] = "Financial services"
        else:
            result["customer"] = "B2B (general)"

        return result


def demo():
    print("=" * 60)
    print("DEMO: NLP Text Processor")
    print("=" * 60)
    processor = TextProcessor(use_spacy=True)

    sample_text = """
    I want to build an AI-powered legal document analyzer for law firms.
    The problem: lawyers spend 40% of their time reviewing contracts manually.
    Our solution uses NLP and LLMs to review NDAs in 90 seconds.
    Target market: $45.2B legal tech, growing at 18.9% CAGR.
    Key competitors: Harvey AI ($100M funded), Ironclad ($333M).
    We're targeting firms with $50M-$500M revenue in the US and UK.
    """

    print("\n[1] Text Cleaning")
    cleaned = processor.clean(sample_text)
    print(cleaned[:200])

    print("\n[2] Keyword Extraction")
    keywords = processor.extract_keywords(sample_text)
    print("Top keywords:", keywords)

    print("\n[3] Entity Extraction")
    entities = processor.extract_entities(sample_text)
    for ent in entities:
        print(f"  {ent['label']:10} → {ent['text']}")

    print("\n[4] Full Pipeline")
    result = processor.process(sample_text)
    print(f"Words: {result.word_count}")
    print(f"Sentences: {len(result.sentences)}")
    print(f"Entities: {len(result.entities)}")
    print(f"Keywords: {result.keywords[:5]}")

    print("\n[5] Startup Component Extraction")
    components = processor.extract_startup_components(sample_text)
    for key, val in components.items():
        print(f"  {key}: {val}")


if __name__ == "__main__":
    demo()
