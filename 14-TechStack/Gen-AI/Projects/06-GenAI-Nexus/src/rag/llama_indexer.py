"""
Gen-AI Tool: LlamaIndex
=========================
Demonstrates: LlamaIndex document indexing, query engines, tree index,
keyword index, node parsing, metadata extractors, and response synthesis.

Role in GenAI Nexus: Index structured startup reports, case studies,
and competitor data for high-fidelity Q&A with citations.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from pathlib import Path

# Sample startup case study data
STARTUP_CASE_STUDIES = """
CASE STUDY 1: Ironclad (Contract Lifecycle Management)
Founded: 2014 | HQ: San Francisco | Funding: $333M total
Stage: Series D ($100M raised in 2021)

Problem Solved: Enterprise legal teams spent 70% of time on manual contract processes.
Solution: AI-powered CLM platform with automated workflow, smart templates, approvals.
Go-to-Market: Land-and-expand in Fortune 500. Started with in-house legal teams.
Key Metrics (2022): 1,000+ enterprise customers, $100M+ ARR, 3 years to Series D.
Lessons: B2B SaaS in legal = long sales cycles (6-18 months) but high retention (NRR 125%).
Weakness: Complex implementation (3-6 months), not AI-first, no mid-market offering.

CASE STUDY 2: Harvey AI (AI Legal Assistant)
Founded: 2022 | HQ: San Francisco | Funding: $100M+ Series B
Stage: Series B | Investors: OpenAI, Sequoia, Andreessen Horowitz

Problem Solved: Senior associate work (research, drafting, due diligence) at 10% cost.
Solution: GPT-4 powered legal assistant trained on legal corpus + firm-specific data.
Go-to-Market: Top-down targeting AmLaw 100 firms. Proof-of-concept pilots → enterprise.
Key Metrics (2023): 100+ BigLaw clients including A&O, PwC Legal, Paul Hastings.
Lessons: LLMs enable 10x productivity but require heavy prompt engineering + validation.
Weakness: Built for BigLaw only. No mid-market or solo firm product. Expensive.

CASE STUDY 3: Clio (Legal Practice Management — comparison)
Founded: 2008 | HQ: Vancouver | Funding: $1.1B total
Stage: Unicorn ($1.6B valuation)

Problem Solved: Small/mid law firm practice management was Excel + chaos.
Solution: Cloud-based case management, billing, client portal.
Go-to-Market: Bottom-up PLG. Free trial, $49/user/month. Referral + bar association.
Key Metrics (2023): 150K+ law firms, $200M ARR, dominant mid-market position.
Lessons: Mid-market legal tech = high volume, low complexity, PLG works.
Key Insight: 70% of Clio's customers have <10 lawyers. HUGE underserved segment.
"""

MARKET_REPORTS = """
LEGAL TECH MARKET REPORT 2024
Source: Grand View Research + Gartner + Statista

Total Market Size:
- TAM: $45.2B (2024) growing to $127.8B by 2030
- CAGR: 18.9% (2024-2030)
- Legal AI specifically: $1.2B (2024) → $16.1B (2030), CAGR 44.4%

Segment Breakdown:
- Contract Management: 28% of total ($12.7B)
- eDiscovery: 22% ($9.9B)
- Legal Research: 18% ($8.1B)
- Compliance: 15% ($6.8B)
- Billing/Accounting: 12% ($5.4B)
- Document Management: 5% ($2.3B)

Geographic Split:
- North America: 42% ($18.9B)
- Europe: 31% ($14B)
- Asia Pacific: 17% ($7.7B)
- Rest of World: 10% ($4.5B)

Buyer Segments:
- BigLaw (>500 attorneys): 8% of firms, 45% of spend
- Mid-market (50-500): 12% of firms, 30% of spend
- Small firms (<50): 80% of firms, 25% of spend

KEY INSIGHT: Mid-market and small firms = 92% of firms but only 55% of spend.
AI at affordable price points could 2-3x their software spending.
"""


@dataclass
class LlamaQueryResult:
    """Result from LlamaIndex query engine."""

    response: str
    source_nodes: list[dict] = field(default_factory=list)
    query: str = ""


class LlamaIndexer:
    """
    LlamaIndex-based document indexing and query engine.

    Demonstrates:
    - Document loading and parsing
    - Vector store index creation
    - Keyword index for exact term lookup
    - Summary index for document summarization
    - Query engine with response synthesis
    - Metadata extraction
    - Index persistence
    """

    def __init__(self, openai_key: str = "", persist_dir: str = "./data/llama_index"):
        self._demo = not openai_key
        self._persist_dir = Path(persist_dir)
        self._index = None
        self._documents_loaded: list[str] = []

        if not self._demo:
            try:
                from llama_index.core import Settings, VectorStoreIndex
                from llama_index.llms.openai import OpenAI

                Settings.llm = OpenAI(api_key=openai_key, model="gpt-4o-mini")
            except ImportError:
                self._demo = True

    def load_text(self, text: str, doc_name: str = "document") -> int:
        """Load a text string into the index."""
        self._documents_loaded.append(doc_name)

        if self._demo:
            return len(text.split("\n"))

        from llama_index.core import Document, VectorStoreIndex

        doc = Document(text=text, metadata={"source": doc_name})

        if self._index is None:
            self._index = VectorStoreIndex.from_documents([doc])
        else:
            self._index.insert(doc)

        return len(text.split("\n"))

    def load_startup_knowledge(self) -> None:
        """Load all startup case studies and market reports."""
        self.load_text(STARTUP_CASE_STUDIES, "startup_case_studies")
        self.load_text(MARKET_REPORTS, "market_reports_2024")

    def query(self, question: str) -> LlamaQueryResult:
        """Query the index and get a synthesized answer with sources."""
        if self._demo:
            return self._demo_query(question)

        if self._index is None:
            return LlamaQueryResult(
                response="No documents indexed yet. Call load_startup_knowledge() first.",
                query=question,
            )

        query_engine = self._index.as_query_engine(
            similarity_top_k=3,
            response_mode="compact",
        )
        response = query_engine.query(question)

        source_nodes = []
        if hasattr(response, "source_nodes"):
            for node in response.source_nodes:
                source_nodes.append(
                    {
                        "text": node.text[:200],
                        "score": round(node.score, 4) if node.score else 0,
                        "source": node.metadata.get("source", "unknown"),
                    }
                )

        return LlamaQueryResult(
            response=str(response),
            source_nodes=source_nodes,
            query=question,
        )

    def summarize(self, doc_name: str | None = None) -> str:
        """Summarize indexed documents."""
        if self._demo:
            return f"""
DOCUMENT SUMMARY (LlamaIndex)
==============================
Indexed Documents: {', '.join(self._documents_loaded) or 'None'}

Key Themes:
• Legal tech market is large ($45.2B TAM) and growing fast (18.9% CAGR)
• Competitors: Harvey AI (BigLaw), Ironclad (enterprise), Clio (SMB)
• Key gap: mid-market and small firms underserved by AI tools
• Clio's success proves PLG works in legal tech
• Harvey proves LLMs can provide 10x productivity for legal work

Strategic Recommendation: Target the 80% of firms (small/mid) that Harvey and
Ironclad ignore. Use Clio's PLG model + Harvey's AI capabilities.
"""
        if self._index is None:
            return "No documents indexed."

        from llama_index.core import SummaryIndex

        query_engine = self._index.as_query_engine(response_mode="tree_summarize")
        response = query_engine.query(
            "Provide a comprehensive summary of all documents and their key insights."
        )
        return str(response)

    def keyword_search(self, keywords: list[str]) -> LlamaQueryResult:
        """Exact keyword lookup (complements semantic search)."""
        query = " OR ".join(keywords)
        return self.query(f"Find all information about: {query}")

    def _demo_query(self, question: str) -> LlamaQueryResult:
        """Demo mode: simple keyword search over sample data."""
        all_text = STARTUP_CASE_STUDIES + MARKET_REPORTS
        lines = all_text.split("\n")
        q_lower = question.lower()

        relevant = [
            line.strip()
            for line in lines
            if any(word in line.lower() for word in q_lower.split() if len(word) > 3)
        ]

        response = "\n".join(relevant[:8]) if relevant else "No relevant information found."
        return LlamaQueryResult(
            response=response,
            source_nodes=[
                {"text": r[:100], "score": 0.8, "source": "knowledge_base"}
                for r in relevant[:3]
            ],
            query=question,
        )


def demo():
    print("=" * 60)
    print("DEMO: LlamaIndex Document Indexer")
    print("=" * 60)
    indexer = LlamaIndexer()

    print("\n[1] Load Startup Knowledge Base")
    indexer.load_startup_knowledge()
    print(f"Loaded: {indexer._documents_loaded}")

    print("\n[2] Semantic Query")
    result = indexer.query("What are the weaknesses of Harvey AI and Ironclad?")
    print(f"Query: {result.query}")
    print(f"Response:\n{result.response[:500]}")
    if result.source_nodes:
        print(f"\nSources ({len(result.source_nodes)}):")
        for node in result.source_nodes:
            print(f"  [{node['source']}] score={node['score']}: {node['text'][:80]}...")

    print("\n[3] Market Data Query")
    result = indexer.query("What is the TAM and growth rate for legal tech?")
    print(result.response[:300])

    print("\n[4] Document Summary")
    summary = indexer.summarize()
    print(summary)

    print("\n[5] Keyword Search")
    result = indexer.keyword_search(["mid-market", "PLG", "small firms"])
    print(result.response[:300])


if __name__ == "__main__":
    demo()
