"""Reviewer agent: evaluates draft quality and provides feedback."""

import json

from src.llm import get_llm


def _fallback_review(draft: str) -> dict:
    """Basic heuristic review when no LLM is available."""
    score = 5
    feedback_items = []

    word_count = len(draft.split())
    if word_count > 200:
        score += 1
        feedback_items.append(f"Good length ({word_count} words).")
    else:
        feedback_items.append(f"Short article ({word_count} words). Consider expanding.")

    has_headings = draft.count("#") >= 3
    if has_headings:
        score += 1
        feedback_items.append("Good use of section headings.")
    else:
        feedback_items.append("Add more section headings for structure.")

    has_conclusion = "conclusion" in draft.lower()
    if has_conclusion:
        score += 1
        feedback_items.append("Conclusion section present.")
    else:
        feedback_items.append("Missing conclusion section.")

    paragraph_count = len([p for p in draft.split("\n\n") if len(p.strip()) > 30])
    if paragraph_count >= 4:
        score += 1
        feedback_items.append(f"Well-structured ({paragraph_count} paragraphs).")
    else:
        feedback_items.append("Add more detailed paragraphs.")

    # Cap score at 10
    score = min(score, 10)

    return {
        "score": score,
        "feedback": "\n".join(f"- {item}" for item in feedback_items),
        "approved": score >= 7,
    }


def review(state: dict) -> dict:
    """Reviewer agent node: evaluates the draft and returns feedback.

    Args:
        state: Current AgentState with 'draft' populated.

    Returns:
        Updated state with 'review_feedback', 'status', and 'iteration'.
    """
    draft = state["draft"]
    iteration = state.get("iteration", 0) + 1

    llm = get_llm()
    if llm:
        prompt = (
            "You are a content reviewer. Evaluate this article draft.\n"
            "Respond with valid JSON only: "
            '{"score": <1-10>, "feedback": "<detailed feedback>", '
            '"approved": <true/false>}\n'
            "Score 7+ means approved.\n\n"
            f"Draft:\n{draft}"
        )
        response = llm.invoke(prompt)
        try:
            result = json.loads(response.content)
        except json.JSONDecodeError:
            result = _fallback_review(draft)
    else:
        result = _fallback_review(draft)

    score = result.get("score", 5)
    feedback = result.get("feedback", "No feedback.")
    approved = result.get("approved", score >= 7)

    # After max iterations, force approval
    if iteration >= 3:
        approved = True

    if approved:
        next_status = "complete"
    else:
        next_status = "writing"

    return {
        "review_feedback": f"Score: {score}/10\n{feedback}",
        "iteration": iteration,
        "status": next_status,
    }
