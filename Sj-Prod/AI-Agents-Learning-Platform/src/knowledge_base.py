"""Knowledge base: comprehensive data about AI agent frameworks and patterns."""

import logging

logger = logging.getLogger(__name__)

FRAMEWORKS = {
    "langchain": {
        "name": "LangChain",
        "category": "orchestration",
        "description": "Framework for building applications powered by language models. Provides chains, agents, and tools for composing LLM workflows.",
        "key_features": [
            "Chains for sequential LLM operations",
            "Agents with tool-use capabilities",
            "Memory systems for conversation context",
            "Document loaders and text splitters",
            "Vector store integrations",
            "Output parsers for structured responses",
        ],
        "best_for": "General-purpose LLM application development",
        "complexity": "medium",
        "language": "Python, JavaScript",
        "github_stars": "90k+",
        "license": "MIT",
    },
    "langgraph": {
        "name": "LangGraph",
        "category": "orchestration",
        "description": "Library for building stateful, multi-agent applications as graphs. Extends LangChain with cyclical computation and state management.",
        "key_features": [
            "State machines for agent workflows",
            "Conditional edges for branching logic",
            "Persistence and checkpointing",
            "Human-in-the-loop support",
            "Streaming intermediate results",
            "Multi-agent coordination",
        ],
        "best_for": "Complex multi-agent workflows with loops and state",
        "complexity": "medium-high",
        "language": "Python",
        "github_stars": "10k+",
        "license": "MIT",
    },
    "autogen": {
        "name": "AutoGen (Microsoft)",
        "category": "multi-agent",
        "description": "Framework for building multi-agent conversational systems. Agents can chat with each other to solve tasks collaboratively.",
        "key_features": [
            "Multi-agent conversations",
            "Code execution capabilities",
            "Human-agent collaboration",
            "Customizable agent roles",
            "Group chat orchestration",
            "Function calling support",
        ],
        "best_for": "Multi-agent collaborative problem solving",
        "complexity": "medium",
        "language": "Python",
        "github_stars": "35k+",
        "license": "CC-BY-4.0",
    },
    "crewai": {
        "name": "CrewAI",
        "category": "multi-agent",
        "description": "Framework for orchestrating role-playing AI agents. Agents are given roles, goals, and backstories to work together on tasks.",
        "key_features": [
            "Role-based agent design",
            "Task delegation between agents",
            "Sequential and parallel task execution",
            "Memory and learning across tasks",
            "Tool integration",
            "Process management (sequential, hierarchical)",
        ],
        "best_for": "Team-based agent workflows with clear roles",
        "complexity": "low-medium",
        "language": "Python",
        "github_stars": "20k+",
        "license": "MIT",
    },
    "openai_assistants": {
        "name": "OpenAI Assistants API",
        "category": "platform",
        "description": "OpenAI's managed platform for building AI assistants with built-in tools like Code Interpreter, file search, and function calling.",
        "key_features": [
            "Managed infrastructure",
            "Built-in code interpreter",
            "File search with vector store",
            "Function calling",
            "Persistent threads",
            "Streaming responses",
        ],
        "best_for": "Quick deployment of AI assistants with minimal infrastructure",
        "complexity": "low",
        "language": "REST API (any language)",
        "github_stars": "N/A (managed service)",
        "license": "Proprietary",
    },
    "claude_agent_sdk": {
        "name": "Claude Agent SDK (Anthropic)",
        "category": "platform",
        "description": "Anthropic's SDK for building production-ready AI agents with Claude models. Supports tool use, multi-turn conversations, and structured outputs.",
        "key_features": [
            "Tool use with structured schemas",
            "Multi-turn conversation support",
            "Computer use capabilities",
            "MCP (Model Context Protocol)",
            "Extended thinking for complex reasoning",
            "Streaming with real-time updates",
        ],
        "best_for": "Building reliable, safe AI agents with Claude",
        "complexity": "low-medium",
        "language": "Python, TypeScript",
        "github_stars": "5k+",
        "license": "MIT",
    },
    "llamaindex": {
        "name": "LlamaIndex",
        "category": "rag",
        "description": "Data framework for building LLM applications with custom data. Specializes in ingestion, indexing, and querying of data sources.",
        "key_features": [
            "Data connectors for 100+ sources",
            "Advanced indexing strategies",
            "Query engines and retrievers",
            "Agent abstractions",
            "Evaluation framework",
            "Fine-tuning support",
        ],
        "best_for": "RAG applications and data-augmented LLM apps",
        "complexity": "medium",
        "language": "Python, TypeScript",
        "github_stars": "35k+",
        "license": "MIT",
    },
    "dspy": {
        "name": "DSPy (Stanford)",
        "category": "optimization",
        "description": "Framework for programming with foundation models using declarative signatures. Automatically optimizes prompts and weights.",
        "key_features": [
            "Declarative signatures for LLM tasks",
            "Automatic prompt optimization",
            "Modular and composable programs",
            "Built-in evaluation metrics",
            "Few-shot learning automation",
            "Chain-of-thought reasoning",
        ],
        "best_for": "Systematic prompt engineering and LLM program optimization",
        "complexity": "high",
        "language": "Python",
        "github_stars": "20k+",
        "license": "MIT",
    },
}

AGENT_PATTERNS = {
    "react": {
        "name": "ReAct (Reason + Act)",
        "description": "The agent alternates between reasoning about what to do and taking actions. It thinks step-by-step, uses tools, observes results, and iterates.",
        "flow": "Think -> Act -> Observe -> Think -> Act -> ... -> Answer",
        "strengths": ["Transparent reasoning", "Tool use", "Self-correction"],
        "weaknesses": ["Can loop indefinitely", "Slow for simple tasks"],
        "example_use": "Research assistant that searches the web, analyzes results, and synthesizes answers",
    },
    "plan_and_execute": {
        "name": "Plan and Execute",
        "description": "First creates a complete plan, then executes each step. The planner and executor can be separate agents or models.",
        "flow": "Plan (all steps) -> Execute Step 1 -> Execute Step 2 -> ... -> Done",
        "strengths": ["Structured approach", "Better for complex tasks", "Predictable"],
        "weaknesses": ["Inflexible if plan needs changing", "Upfront planning cost"],
        "example_use": "Project manager agent that breaks down a coding task and executes each part",
    },
    "reflection": {
        "name": "Reflection / Self-Critique",
        "description": "The agent generates output, then critically evaluates it and iteratively improves. Often uses a separate critic agent.",
        "flow": "Generate -> Critique -> Revise -> Critique -> ... -> Approved",
        "strengths": ["Higher quality output", "Self-improving", "Catches errors"],
        "weaknesses": ["Slower", "May over-revise", "Needs good evaluation criteria"],
        "example_use": "Code review agent that writes code, reviews it, and fixes issues",
    },
    "multi_agent_debate": {
        "name": "Multi-Agent Debate",
        "description": "Multiple agents with different perspectives debate a topic. A moderator synthesizes the final answer from the debate.",
        "flow": "Agent A argues -> Agent B argues -> Agent C argues -> Moderator synthesizes",
        "strengths": ["Diverse perspectives", "Reduces bias", "Better for complex decisions"],
        "weaknesses": ["Expensive (many LLM calls)", "Needs careful role design"],
        "example_use": "Decision-making system where optimist, pessimist, and realist agents evaluate a business strategy",
    },
    "tool_use": {
        "name": "Tool Use / Function Calling",
        "description": "The agent has access to external tools (APIs, databases, calculators) and decides when and how to use them.",
        "flow": "Understand task -> Select tool -> Call tool -> Process result -> Respond",
        "strengths": ["Extends LLM capabilities", "Real-world interaction", "Accurate for specific tasks"],
        "weaknesses": ["Tool design is critical", "Error handling complexity"],
        "example_use": "Customer support agent that queries a database, processes refunds, and sends emails",
    },
    "rag": {
        "name": "Retrieval-Augmented Generation",
        "description": "The agent retrieves relevant documents from a knowledge base before generating a response, grounding answers in real data.",
        "flow": "Query -> Retrieve documents -> Build context -> Generate answer with citations",
        "strengths": ["Grounded in real data", "Reduces hallucination", "Up-to-date knowledge"],
        "weaknesses": ["Quality depends on retrieval", "Chunking strategy matters"],
        "example_use": "Enterprise Q&A bot that answers questions using internal documentation",
    },
}

COMPARISONS = [
    {
        "dimension": "Ease of Setup",
        "langchain": 4, "langgraph": 3, "crewai": 5, "autogen": 4,
        "openai_assistants": 5, "llamaindex": 4,
    },
    {
        "dimension": "Multi-Agent Support",
        "langchain": 3, "langgraph": 5, "crewai": 5, "autogen": 5,
        "openai_assistants": 2, "llamaindex": 2,
    },
    {
        "dimension": "Production Readiness",
        "langchain": 4, "langgraph": 4, "crewai": 3, "autogen": 3,
        "openai_assistants": 5, "llamaindex": 4,
    },
    {
        "dimension": "RAG Capabilities",
        "langchain": 4, "langgraph": 3, "crewai": 2, "autogen": 2,
        "openai_assistants": 4, "llamaindex": 5,
    },
    {
        "dimension": "Flexibility",
        "langchain": 5, "langgraph": 5, "crewai": 3, "autogen": 4,
        "openai_assistants": 2, "llamaindex": 4,
    },
    {
        "dimension": "Community & Docs",
        "langchain": 5, "langgraph": 4, "crewai": 4, "autogen": 4,
        "openai_assistants": 5, "llamaindex": 5,
    },
]


def get_all_frameworks() -> dict:
    logger.debug("Returning all %d frameworks", len(FRAMEWORKS))
    return FRAMEWORKS


def get_framework(name: str) -> dict | None:
    fw = FRAMEWORKS.get(name)
    if fw is None:
        logger.debug("Framework lookup miss: %s", name)
    return fw


def get_all_patterns() -> dict:
    logger.debug("Returning all %d patterns", len(AGENT_PATTERNS))
    return AGENT_PATTERNS


def get_pattern(name: str) -> dict | None:
    pat = AGENT_PATTERNS.get(name)
    if pat is None:
        logger.debug("Pattern lookup miss: %s", name)
    return pat


def get_comparisons() -> list[dict]:
    logger.debug("Returning %d comparison dimensions", len(COMPARISONS))
    return COMPARISONS
