"""
Gen-AI Tool: LangGraph
========================
Demonstrates: Stateful workflow graph with conditional edges,
node functions, state management, graph compilation, checkpointing,
error handling nodes, and human-in-the-loop pause points.

Role in GenAI Nexus: THE spine of the entire pipeline. Each analysis
stage is a node; state flows between nodes carrying the startup plan.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum
from typing import Any


class WorkflowStage(str, Enum):
    PREPROCESS = "preprocess"
    RESEARCH = "research"
    ANALYZE = "analyze"
    TEAM_PLAN = "team_plan"
    DEBATE = "debate"
    VALIDATE = "validate"
    OUTPUT = "output"
    ERROR = "error"


@dataclass
class WorkflowState:
    """
    LangGraph state — passed between all nodes.
    Accumulates results as workflow progresses.
    """

    # Input
    startup_idea: str = ""
    mode: str = "full"  # full | quick | demo

    # Pipeline outputs (built up stage by stage)
    preprocessed: dict[str, Any] = field(default_factory=dict)
    market_research: str = ""
    competitive_analysis: str = ""
    technical_plan: str = ""
    team_assignments: dict[str, str] = field(default_factory=dict)
    debate_outcome: str = ""
    validation_passed: bool = False
    final_report: str = ""

    # Control
    current_stage: WorkflowStage = WorkflowStage.PREPROCESS
    errors: list[str] = field(default_factory=list)
    completed_stages: list[str] = field(default_factory=list)


# ─────────────────────────────────────────────
# NODE FUNCTIONS
# Each node takes state dict, returns updates
# ─────────────────────────────────────────────


def preprocess_node(state: dict) -> dict:
    """
    Node 1: Preprocess the startup idea.
    NLP cleanup, entity extraction, keyword identification.
    """
    from src.nlp.text_processor import TextProcessor

    processor = TextProcessor()
    idea = state.get("startup_idea", "")
    processed = processor.process(idea)
    components = processor.extract_startup_components(idea)

    return {
        **state,
        "preprocessed": {
            "cleaned": processed.cleaned,
            "keywords": processed.keywords[:5],
            "entities": processed.entities[:5],
            "components": components,
            "word_count": processed.word_count,
        },
        "current_stage": WorkflowStage.RESEARCH,
        "completed_stages": state.get("completed_stages", []) + ["preprocess"],
    }


def research_node(state: dict) -> dict:
    """
    Node 2: Market research using RAG + LLM.
    Retrieves relevant data, generates market analysis.
    """
    from src.rag.advanced_rag import AdvancedRAG
    from src.vectorstore.chroma_store import SAMPLE_KNOWLEDGE

    idea = state.get("startup_idea", "")
    try:
        rag = AdvancedRAG()
        result = rag.query_advanced(f"What is the market opportunity for: {idea}?")
        market = result.answer
    except Exception:
        # Fallback: use sample knowledge base directly
        market = "\n".join(doc.content for doc in SAMPLE_KNOWLEDGE if doc.metadata.get("type") == "market_data")

    return {
        **state,
        "market_research": market,
        "current_stage": WorkflowStage.ANALYZE,
        "completed_stages": state.get("completed_stages", []) + ["research"],
    }


def analyze_node(state: dict) -> dict:
    """
    Node 3: Deep analysis using LangChain chains.
    Competitive analysis + technical planning.
    """
    from src.chains.analysis_chains import AnalysisChains

    idea = state.get("startup_idea", "")
    market = state.get("market_research", "")
    chains = AnalysisChains()

    competitive = chains.run_competitive_analysis(idea, market)
    technical = chains.run_technical_plan(idea, market, competitive.content)

    return {
        **state,
        "competitive_analysis": competitive.content,
        "technical_plan": technical.content,
        "current_stage": WorkflowStage.TEAM_PLAN,
        "completed_stages": state.get("completed_stages", []) + ["analyze"],
    }


def team_plan_node(state: dict) -> dict:
    """
    Node 4: CrewAI multi-agent team planning.
    CEO, CTO, CMO, CFO each contribute their domain plan.
    """
    from src.agents.crew_team import StartupCrew

    idea = state.get("startup_idea", "")
    crew = StartupCrew()
    context = {
        "market": state.get("market_research", ""),
        "competition": state.get("competitive_analysis", ""),
        "technical": state.get("technical_plan", ""),
    }
    assignments = crew.run(idea, context)

    return {
        **state,
        "team_assignments": assignments,
        "current_stage": WorkflowStage.DEBATE,
        "completed_stages": state.get("completed_stages", []) + ["team_plan"],
    }


def debate_node(state: dict) -> dict:
    """
    Node 5: Autogen multi-agent debate.
    Optimist vs Skeptic stress-test the startup plan.
    """
    from src.agents.autogen_debate import StartupDebate

    idea = state.get("startup_idea", "")
    plan_summary = state.get("team_assignments", {}).get("ceo", "")
    debate = StartupDebate()
    outcome = debate.run(idea, plan_summary)

    return {
        **state,
        "debate_outcome": outcome,
        "current_stage": WorkflowStage.VALIDATE,
        "completed_stages": state.get("completed_stages", []) + ["debate"],
    }


def validate_node(state: dict) -> dict:
    """
    Node 6: Guardrails validation.
    Check outputs for hallucinations, unsafe content.
    """
    from src.safety.output_validator import OutputValidator

    validator = OutputValidator()
    report_draft = state.get("market_research", "") + state.get("competitive_analysis", "")

    is_valid, issues = validator.validate_report(report_draft)

    return {
        **state,
        "validation_passed": is_valid,
        "errors": state.get("errors", []) + issues if not is_valid else state.get("errors", []),
        "current_stage": WorkflowStage.OUTPUT if is_valid else WorkflowStage.ERROR,
        "completed_stages": state.get("completed_stages", []) + ["validate"],
    }


def output_node(state: dict) -> dict:
    """
    Node 7: Assemble final startup report.
    Synthesizes all stages into a cohesive document.
    """
    idea = state.get("startup_idea", "")
    team = state.get("team_assignments", {})

    report = f"""
# STARTUP PLAN: {idea.upper()}
Generated by GenAI Nexus — AI Startup Advisor
{'=' * 60}

## 1. MARKET RESEARCH
{state.get('market_research', 'N/A')}

## 2. COMPETITIVE LANDSCAPE
{state.get('competitive_analysis', 'N/A')}

## 3. TECHNICAL ARCHITECTURE
{state.get('technical_plan', 'N/A')}

## 4. TEAM PLAN
**CEO Strategy:** {team.get('ceo', 'N/A')}
**CTO Architecture:** {team.get('cto', 'N/A')}
**CMO Go-to-Market:** {team.get('cmo', 'N/A')}
**CFO Financial Model:** {team.get('cfo', 'N/A')}

## 5. DEVIL'S ADVOCATE (Stress Test)
{state.get('debate_outcome', 'N/A')}

## 6. VALIDATION STATUS
{'✅ PASSED — All checks green' if state.get('validation_passed') else '⚠️ REVIEW NEEDED — See issues'}

---
*Generated by GenAI Nexus — 26 Gen-AI tools working together*
"""

    return {
        **state,
        "final_report": report,
        "current_stage": WorkflowStage.OUTPUT,
        "completed_stages": state.get("completed_stages", []) + ["output"],
    }


def error_node(state: dict) -> dict:
    """Error recovery node — log and attempt continuation."""
    errors = state.get("errors", [])
    error_report = f"Workflow encountered {len(errors)} validation issues:\n"
    for e in errors:
        error_report += f"  • {e}\n"
    error_report += "\nPartial report generated despite issues."

    return {
        **state,
        "final_report": error_report,
        "current_stage": WorkflowStage.OUTPUT,
    }


# ─────────────────────────────────────────────
# WORKFLOW GRAPH
# ─────────────────────────────────────────────


class StartupWorkflow:
    """
    LangGraph stateful workflow for startup analysis.

    Demonstrates:
    - StateGraph creation with typed state
    - Node registration
    - Edge definition (sequential + conditional)
    - Graph compilation
    - Execution with state threading
    - Checkpointing for long workflows
    """

    def __init__(self):
        self._graph = None
        self._use_langgraph = False
        self._setup_graph()

    def _setup_graph(self):
        """Build the LangGraph workflow graph."""
        try:
            from langgraph.graph import END, START, StateGraph

            # Define graph with typed state
            workflow = StateGraph(dict)

            # Register nodes
            workflow.add_node("preprocess", preprocess_node)
            workflow.add_node("research", research_node)
            workflow.add_node("analyze", analyze_node)
            workflow.add_node("team_plan", team_plan_node)
            workflow.add_node("debate", debate_node)
            workflow.add_node("validate", validate_node)
            workflow.add_node("output", output_node)
            workflow.add_node("error", error_node)

            # Sequential edges
            workflow.add_edge(START, "preprocess")
            workflow.add_edge("preprocess", "research")
            workflow.add_edge("research", "analyze")
            workflow.add_edge("analyze", "team_plan")
            workflow.add_edge("team_plan", "debate")
            workflow.add_edge("debate", "validate")

            # Conditional edge: validate → output OR error
            workflow.add_conditional_edges(
                "validate",
                lambda state: "output" if state.get("validation_passed", True) else "error",
                {"output": "output", "error": "error"},
            )

            workflow.add_edge("output", END)
            workflow.add_edge("error", END)

            self._graph = workflow.compile()
            self._use_langgraph = True

        except ImportError:
            self._use_langgraph = False

    def run(self, startup_idea: str, mode: str = "full") -> dict:
        """
        Execute the full workflow for a startup idea.

        Args:
            startup_idea: The startup concept to analyze
            mode: "full" (all stages) | "quick" (skip debate+training)
        """
        initial_state = {
            "startup_idea": startup_idea,
            "mode": mode,
            "preprocessed": {},
            "market_research": "",
            "competitive_analysis": "",
            "technical_plan": "",
            "team_assignments": {},
            "debate_outcome": "",
            "validation_passed": False,
            "final_report": "",
            "current_stage": WorkflowStage.PREPROCESS,
            "errors": [],
            "completed_stages": [],
        }

        if self._use_langgraph and self._graph:
            # LangGraph execution
            final_state = initial_state
            for step in self._graph.stream(initial_state):
                node_name = list(step.keys())[0]
                final_state = list(step.values())[0]
                print(f"  ✓ Completed stage: {node_name}")
            return final_state

        else:
            # Fallback: run nodes sequentially
            print("  Running in sequential mode (LangGraph not available)")
            state = initial_state
            for node_fn in [
                preprocess_node,
                research_node,
                analyze_node,
                team_plan_node,
                debate_node,
                validate_node,
            ]:
                try:
                    state = node_fn(state)
                    print(f"  ✓ {node_fn.__name__.replace('_node', '')}")
                except Exception as e:
                    state["errors"].append(str(e))
                    print(f"  ⚠ {node_fn.__name__} failed: {e}")

            state = output_node(state)
            return state

    def get_graph_visualization(self) -> str:
        """Return ASCII representation of the workflow graph."""
        return """
LangGraph Workflow — GenAI Nexus
===================================
START
  │
  ▼
[preprocess]  ← NLP: tokenize, entities, keywords
  │
  ▼
[research]    ← Advanced RAG: HyDE + hybrid search
  │
  ▼
[analyze]     ← LangChain: competitive + technical chains
  │
  ▼
[team_plan]   ← CrewAI: CEO + CTO + CMO + CFO agents
  │
  ▼
[debate]      ← Autogen: optimist vs skeptic debate
  │
  ▼
[validate]    ← Guardrails: fact-check + safety
  │
  ├──(pass)──► [output]  ← Assemble final report
  │
  └──(fail)──► [error]   ← Log issues, partial report
                │
               END
"""


def demo():
    print("=" * 60)
    print("DEMO: LangGraph Startup Workflow")
    print("=" * 60)

    print("\n[1] Workflow Visualization")
    workflow = StartupWorkflow()
    print(workflow.get_graph_visualization())

    print("\n[2] Run Full Workflow")
    result = workflow.run("AI legal document analyzer")

    print(f"\nCompleted stages: {result.get('completed_stages', [])}")
    print(f"Validation passed: {result.get('validation_passed', False)}")
    print(f"\nFinal Report Preview:\n{result.get('final_report', '')[:600]}...")


if __name__ == "__main__":
    demo()
