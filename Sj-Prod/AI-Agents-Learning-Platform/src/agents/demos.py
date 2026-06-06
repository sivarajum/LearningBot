"""Interactive agent pattern demonstrations (no LLM required)."""

import logging
import random
import time

logger = logging.getLogger(__name__)


def demo_react(task: str) -> list[dict]:
    """Simulate a ReAct (Reason + Act) agent loop.

    Returns a list of steps showing the think-act-observe cycle.
    """
    steps = []
    tools = ["web_search", "calculator", "database_lookup"]

    # Step 1: Think
    steps.append({
        "type": "thought",
        "content": f"I need to break down the task: '{task}'. Let me figure out what information I need.",
    })

    # Step 2: Act
    tool = random.choice(tools)
    steps.append({
        "type": "action",
        "tool": tool,
        "input": f"Search for information about: {task}",
    })

    # Step 3: Observe
    steps.append({
        "type": "observation",
        "content": f"[{tool}] Found relevant information about {task}. Key points: efficiency, scalability, best practices.",
    })

    # Step 4: Think again
    steps.append({
        "type": "thought",
        "content": "I have some initial information. Let me verify with another source.",
    })

    # Step 5: Act again
    tool2 = random.choice([t for t in tools if t != tool])
    steps.append({
        "type": "action",
        "tool": tool2,
        "input": f"Verify and expand on: {task}",
    })

    # Step 6: Observe
    steps.append({
        "type": "observation",
        "content": f"[{tool2}] Confirmed findings. Additional insight: modern approaches emphasize iterative improvement.",
    })

    # Step 7: Final answer
    steps.append({
        "type": "answer",
        "content": f"Based on my research using {tool} and {tool2}, here is what I found about '{task}': "
                   f"The topic involves multiple dimensions including implementation, best practices, "
                   f"and real-world considerations. Key recommendations include starting small, "
                   f"iterating quickly, and measuring outcomes.",
    })

    return steps


def demo_plan_and_execute(task: str) -> dict:
    """Simulate a Plan-and-Execute agent.

    Returns the plan and execution results for each step.
    """
    # Planning phase
    plan = [
        f"Research background on '{task}'",
        "Identify key components and requirements",
        "Analyze trade-offs and alternatives",
        "Synthesize findings into a recommendation",
    ]

    # Execution phase
    executions = []
    for i, step in enumerate(plan):
        executions.append({
            "step": i + 1,
            "plan": step,
            "status": "completed",
            "result": f"Step {i+1} completed: gathered information about {step.lower()}. "
                      f"Found {random.randint(3, 8)} relevant data points.",
            "duration_ms": random.randint(100, 2000),
        })

    return {
        "task": task,
        "plan": plan,
        "executions": executions,
        "final_answer": f"After executing all {len(plan)} steps, the analysis of '{task}' "
                        f"reveals a multi-faceted topic requiring careful consideration of "
                        f"trade-offs between simplicity and capability.",
    }


def demo_reflection(task: str) -> dict:
    """Simulate a Reflection/Self-Critique agent.

    Returns the generation, critique, and revision cycle.
    """
    # Initial generation
    draft = (
        f"Initial analysis of '{task}': This is an important topic that involves "
        f"several key considerations. The main approach should focus on fundamental "
        f"principles and practical implementation."
    )

    # Critique
    critique = {
        "score": random.randint(4, 6),
        "issues": [
            "Too vague - needs specific examples",
            "Missing quantitative analysis",
            "Conclusion could be stronger",
        ],
        "strengths": [
            "Good high-level structure",
            "Covers the main topic",
        ],
    }

    # Revised version
    revision = (
        f"Revised analysis of '{task}': This topic requires attention to three specific areas: "
        f"(1) Implementation patterns with concrete examples like modular design and testing, "
        f"(2) Performance metrics showing 40-60% improvement with proper practices, and "
        f"(3) A clear recommendation to adopt an incremental approach with measurable milestones."
    )

    # Final critique
    final_critique = {
        "score": random.randint(7, 9),
        "issues": ["Minor: could add more references"],
        "strengths": [
            "Specific and actionable",
            "Includes quantitative data",
            "Clear structure and recommendation",
        ],
        "approved": True,
    }

    return {
        "task": task,
        "iterations": [
            {"draft": draft, "critique": critique},
            {"draft": revision, "critique": final_critique},
        ],
        "final_output": revision,
    }


def demo_multi_agent_debate(topic: str) -> dict:
    """Simulate a Multi-Agent Debate.

    Returns arguments from different agent perspectives and a synthesis.
    """
    agents = {
        "optimist": {
            "role": "Optimist Agent",
            "argument": f"The potential of '{topic}' is enormous. Early adopters are seeing "
                        f"2-3x productivity gains. The technology is maturing rapidly and will "
                        f"become essential within 2 years. We should invest heavily now.",
        },
        "skeptic": {
            "role": "Skeptic Agent",
            "argument": f"While '{topic}' shows promise, we must consider the risks. "
                        f"Current implementations have a 30% failure rate in production. "
                        f"The technology is overhyped and we should wait for it to stabilize.",
        },
        "pragmatist": {
            "role": "Pragmatist Agent",
            "argument": f"A balanced approach to '{topic}' is best. Start with a small pilot "
                        f"project, measure results over 3 months, then scale based on data. "
                        f"Allocate 20% of budget to experimentation.",
        },
    }

    synthesis = (
        f"After considering all perspectives on '{topic}': The technology has real potential "
        f"(optimist) but carries risks (skeptic). The recommended approach is a measured "
        f"pilot program (pragmatist) with clear success criteria and a 3-month evaluation period."
    )

    return {
        "topic": topic,
        "agents": agents,
        "synthesis": synthesis,
        "recommendation": "Proceed with controlled pilot",
    }


DEMO_REGISTRY = {
    "react": {"fn": demo_react, "name": "ReAct (Reason + Act)"},
    "plan_and_execute": {"fn": demo_plan_and_execute, "name": "Plan and Execute"},
    "reflection": {"fn": demo_reflection, "name": "Reflection / Self-Critique"},
    "multi_agent_debate": {"fn": demo_multi_agent_debate, "name": "Multi-Agent Debate"},
}


def run_demo(pattern: str, task: str) -> dict:
    """Run an agent pattern demo."""
    if pattern not in DEMO_REGISTRY:
        logger.warning("Unknown demo pattern requested: %s", pattern)
        return {"error": f"Unknown pattern: {pattern}. Available: {list(DEMO_REGISTRY.keys())}"}

    logger.info("Starting demo: pattern=%s, task=%s", pattern, task[:80])
    start = time.time()
    result = DEMO_REGISTRY[pattern]["fn"](task)
    elapsed = round(time.time() - start, 4)
    logger.info("Demo completed: pattern=%s, elapsed=%.4fs", pattern, elapsed)

    return {
        "pattern": pattern,
        "pattern_name": DEMO_REGISTRY[pattern]["name"],
        "task": task,
        "result": result,
        "elapsed_seconds": elapsed,
    }
