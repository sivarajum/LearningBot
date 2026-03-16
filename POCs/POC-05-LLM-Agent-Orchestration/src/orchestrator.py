"""LangGraph orchestrator: wires Researcher -> Writer -> Reviewer into a state machine."""

from langgraph.graph import StateGraph, END

from src.state import AgentState
from src.agents.researcher import research
from src.agents.writer import write
from src.agents.reviewer import review


def _should_revise(state: AgentState) -> str:
    """Conditional edge: route back to writer if not approved, else finish."""
    if state["status"] == "complete":
        return "end"
    return "writer"


def build_graph() -> StateGraph:
    """Build and compile the agent orchestration graph.

    Graph structure:
        START -> researcher -> writer -> reviewer
        reviewer -> writer   (if score < 7 and iteration < 3)
        reviewer -> END      (if approved or max iterations reached)

    Returns:
        A compiled LangGraph that accepts AgentState.
    """
    graph = StateGraph(AgentState)

    # Add agent nodes
    graph.add_node("researcher", research)
    graph.add_node("writer", write)
    graph.add_node("reviewer", review)

    # Edges: linear flow with a review loop
    graph.set_entry_point("researcher")
    graph.add_edge("researcher", "writer")
    graph.add_edge("writer", "reviewer")
    graph.add_conditional_edges(
        "reviewer",
        _should_revise,
        {"writer": "writer", "end": END},
    )

    return graph.compile()


def run_pipeline(topic: str) -> dict:
    """Run the full agent pipeline for a given topic.

    Args:
        topic: The subject to research, write about, and review.

    Returns:
        Final AgentState dict with all intermediate outputs.
    """
    app = build_graph()

    initial_state: AgentState = {
        "messages": [],
        "topic": topic,
        "research": "",
        "draft": "",
        "review_feedback": "",
        "iteration": 0,
        "status": "researching",
    }

    final_state = app.invoke(initial_state)
    return dict(final_state)
