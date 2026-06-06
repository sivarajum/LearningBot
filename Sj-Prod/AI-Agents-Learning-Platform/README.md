# POC-06: AI Agent Framework Comparison Guide

## What This Is

A reference platform for understanding, comparing, and interactively exploring AI agent frameworks and agentic design patterns. The core deliverable is a structured Python knowledge base covering 8 frameworks and 6 agent patterns, served via a FastAPI REST API and a Streamlit exploration dashboard.

No LLM API key is required to run this POC. All agent pattern demonstrations are implemented as deterministic Python functions that illustrate the structure of each pattern without calling an LLM.

---

## What This POC Actually Implements

### Knowledge Base (`src/knowledge_base.py`)

A structured Python module containing authoritative data on:

**8 AI Agent Frameworks** (with description, key features, best-for, complexity, language, license for each):
- LangChain, LangGraph, AutoGen (Microsoft), CrewAI, OpenAI Assistants API, Claude Agent SDK (Anthropic), LlamaIndex, DSPy (Stanford)

**6 Agent Patterns** (with description, flow, strengths, weaknesses, example use for each):
- ReAct (Reason + Act), Plan and Execute, Reflection / Self-Critique, Multi-Agent Debate, Tool Use / Function Calling, Retrieval-Augmented Generation (RAG)

**Quantitative comparison matrix** — scores each of 6 frameworks across 6 dimensions (Ease of Setup, Multi-Agent Support, Production Readiness, RAG Capabilities, Flexibility, Community & Docs) on a 1–5 scale.

### Agent Pattern Demos (`src/agents/demos.py`)

Interactive demonstrations of 4 agent patterns implemented as pure Python. No LLM calls — the logic shows the structure of each pattern:

- `demo_react(task)` — simulates a Think → Act → Observe → Think → Act → Answer loop with tool selections
- `demo_plan_and_execute(task)` — generates a 4-step plan then executes each step with status and duration
- `demo_reflection(task)` — produces draft → critique → revision cycle with scoring at each stage
- `demo_multi_agent_debate(topic)` — three agents (optimist, skeptic, pragmatist) argue a topic, moderator synthesizes

### REST API (`src/api.py`)

FastAPI endpoints exposing all knowledge base data:
- `GET /frameworks` — full list of all 8 frameworks
- `GET /frameworks/{name}` — single framework detail
- `GET /patterns` — all 6 agent patterns
- `GET /patterns/{name}` — single pattern detail
- `GET /compare` — comparison matrix data
- `POST /demo/{pattern}` — run an agent pattern demo with a custom task string

### Streamlit Dashboard (`src/ui.py`)

Three-tab interactive dashboard: framework explorer, pattern visualizer, and live demo runner.

---

## Framework Comparison Table

| Framework | Complexity | Best For | Language | License | State Management | Tool Support |
|-----------|------------|----------|----------|---------|-----------------|--------------|
| LangChain | Medium | General-purpose LLM apps | Python, JS | MIT | Via memory modules | Yes (100+ integrations) |
| LangGraph | Medium-High | Multi-agent workflows with loops | Python | MIT | Built-in state machine | Yes |
| AutoGen | Medium | Multi-agent collaborative problem solving | Python | CC-BY-4.0 | Per-agent conversation history | Yes (function calling) |
| CrewAI | Low-Medium | Team-based workflows with clear roles | Python | MIT | Task-level memory | Yes |
| OpenAI Assistants API | Low | Quick deployment with minimal infrastructure | REST (any) | Proprietary | Persistent threads (managed) | Yes (Code Interpreter, file search) |
| Claude Agent SDK | Low-Medium | Reliable, safe agents with Claude | Python, TS | MIT | Conversation turns | Yes (MCP + tool schemas) |
| LlamaIndex | Medium | RAG and data-augmented LLM apps | Python, TS | MIT | Index-level retrieval state | Yes (100+ data connectors) |
| DSPy | High | Systematic prompt optimization | Python | MIT | Compiled program state | Limited |

---

## Running It Locally

**Prerequisites:**

```bash
pip install -r requirements.txt
```

**Start the REST API:**

```bash
python main.py api
# Server starts on http://localhost:8000
# Interactive docs: http://localhost:8000/docs
```

**Start the Streamlit dashboard:**

```bash
python main.py ui
# Opens on http://localhost:8501
```

**Query the knowledge base:**

```bash
# List all frameworks
curl http://localhost:8000/frameworks

# Get details on LangGraph
curl http://localhost:8000/frameworks/langgraph

# Run a ReAct pattern demo
curl -X POST http://localhost:8000/demo/react \
  -H "Content-Type: application/json" \
  -d '{"task": "Compare vector databases for a RAG system"}'

# Run a multi-agent debate
curl -X POST http://localhost:8000/demo/multi_agent_debate \
  -H "Content-Type: application/json" \
  -d '{"task": "Should we adopt LangChain for our production system?"}'
```

---

## What the Demo Functions Show

The 4 pattern demos in `src/agents/demos.py` demonstrate structure, not intelligence. Each function returns a structured trace of what a real LLM-driven implementation of that pattern would produce:

| Pattern | What the Demo Returns | What a Real LLM Implementation Adds |
|---------|----------------------|-------------------------------------|
| ReAct | Step-by-step thought/action/observation trace with tool names | The LLM generates actual thoughts; tool calls return real data |
| Plan and Execute | A 4-step plan with per-step status and duration | Planner LLM writes the actual plan; executor LLM runs each step |
| Reflection | Draft text, a scored critique, and a revised draft | Generator and critic LLMs produce context-specific content |
| Multi-Agent Debate | Arguments from 3 agent roles + moderator synthesis | Each agent role is a separate LLM call with a system prompt |

This separation makes the control flow clear — you can see exactly what each pattern does independently of any LLM's output.

---

## Extending This POC

**Add a new framework to the knowledge base:**

```python
# In src/knowledge_base.py, add to FRAMEWORKS dict:
FRAMEWORKS["smolagents"] = {
    "name": "SmolAgents (Hugging Face)",
    "category": "orchestration",
    "description": "Minimal agent framework from Hugging Face. Focuses on code agents that write and execute Python.",
    "key_features": ["Code agents", "Minimal abstraction", "Multi-provider LLM support"],
    "best_for": "Lightweight agents that execute code",
    "complexity": "low",
    "language": "Python",
    "github_stars": "10k+",
    "license": "Apache-2.0",
}
```

**Connect a demo to a real LLM:**

```python
# In src/agents/demos.py, replace the hardcoded thought with an actual LLM call:
import anthropic

client = anthropic.Anthropic()

def demo_react_live(task: str) -> list[dict]:
    steps = []
    message = client.messages.create(
        model="claude-opus-4-5",
        max_tokens=1024,
        messages=[{"role": "user", "content": f"Think about how to approach this task: {task}"}]
    )
    steps.append({"type": "thought", "content": message.content[0].text})
    # ... continue the ReAct loop
    return steps
```
