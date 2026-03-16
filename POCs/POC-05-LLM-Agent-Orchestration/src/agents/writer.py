"""Writer agent: produces a structured article from research findings."""

from src.llm import get_llm


def _fallback_article(topic: str, research: str, feedback: str) -> str:
    """Generate a template-based article without an LLM."""
    # Extract lines that look like content from the research
    lines = [l.strip() for l in research.split("\n") if l.strip() and len(l.strip()) > 20]
    key_points = lines[:8]  # Take up to 8 substantial lines

    sections = [
        f"# {topic}",
        "",
        "## Introduction",
        f"This report covers key findings on the topic of {topic}, "
        "compiled from multiple web sources.",
        "",
        "## Key Findings",
    ]
    for i, point in enumerate(key_points, 1):
        # Clean up search-result formatting
        clean = point.lstrip("[0123456789] ").strip()
        sections.append(f"{i}. {clean}")

    sections.extend([
        "",
        "## Analysis",
        f"Based on the research gathered, {topic} is a multifaceted subject "
        "with several important dimensions worth exploring further.",
        "",
        "## Conclusion",
        f"The research highlights important aspects of {topic} that merit "
        "continued attention and deeper investigation.",
    ])

    if feedback:
        sections.extend([
            "",
            "---",
            f"*Revision note: incorporated feedback from review iteration.*",
        ])

    return "\n".join(sections)


def write(state: dict) -> dict:
    """Writer agent node: creates an article from research results.

    Args:
        state: Current AgentState with 'research' populated.

    Returns:
        Updated state with 'draft' and 'status' fields.
    """
    topic = state["topic"]
    research = state["research"]
    feedback = state.get("review_feedback", "")

    llm = get_llm(temperature=0.7)
    if llm:
        revision_note = ""
        if feedback:
            revision_note = (
                f"\n\nPrevious review feedback to address:\n{feedback}"
            )
        prompt = (
            f"You are an expert content writer. Write a well-structured article "
            f"about '{topic}' using the research below. Include an introduction, "
            f"key findings, analysis, and conclusion. Use markdown formatting."
            f"\n\nResearch:\n{research}{revision_note}"
        )
        response = llm.invoke(prompt)
        draft = response.content
    else:
        draft = _fallback_article(topic, research, feedback)

    return {
        "draft": draft,
        "status": "reviewing",
    }
