"""Researcher agent: gathers information on a topic via web search."""

from src.llm import get_llm
from src.tools import web_search


def _search_topic(topic: str) -> str:
    """Run multiple search queries and combine results."""
    queries = [
        topic,
        f"{topic} latest developments",
        f"{topic} key facts and statistics",
    ]
    all_results = []
    for q in queries:
        result = web_search.invoke(q)
        all_results.append(f"Query: {q}\n{result}")

    # Offline fallback: if every search failed, return canned data
    if all("Search failed" in r for r in all_results):
        return (
            f"[Offline mode] {topic} is a rapidly evolving field. "
            "Key areas include architecture patterns, best practices, "
            "and production considerations. Further research recommended "
            "when internet is available."
        )

    return "\n\n---\n\n".join(all_results)


def research(state: dict) -> dict:
    """Researcher agent node: searches the web and summarizes findings.

    Args:
        state: Current AgentState with 'topic' populated.

    Returns:
        Updated state with 'research' and 'status' fields.
    """
    topic = state["topic"]
    raw_results = _search_topic(topic)

    llm = get_llm()
    if llm:
        prompt = (
            f"You are a research analyst. Summarize the following search results "
            f"about '{topic}' into a clear, structured research brief with key "
            f"findings, facts, and statistics. Use bullet points.\n\n"
            f"Search Results:\n{raw_results}"
        )
        response = llm.invoke(prompt)
        research_output = response.content
    else:
        # Fallback: format raw results neatly
        research_output = (
            f"Research Brief: {topic}\n"
            f"{'=' * 40}\n"
            f"(Fallback mode - raw search results)\n\n"
            f"{raw_results}"
        )

    return {
        "research": research_output,
        "status": "writing",
        "iteration": state.get("iteration", 0),
    }
