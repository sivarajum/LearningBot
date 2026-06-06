# AI Agents Learning Platform -- Comprehensive Guide

A baby-step walkthrough of every layer in this project: what AI agents are,
how the knowledge base is structured, how each demo simulation works internally,
how the FastAPI backend serves data, how the Streamlit dashboard renders it,
and how to run, test, and troubleshoot the whole thing.

---

## Table of Contents

1.  [Prerequisites](#1-prerequisites)
2.  [Project Overview](#2-project-overview)
3.  [What Are AI Agents and Why Learn About Them](#3-what-are-ai-agents-and-why-learn-about-them)
4.  [Project Structure](#4-project-structure)
5.  [The Knowledge Base Layer](#5-the-knowledge-base-layer)
    - 5.1 Frameworks Dictionary
    - 5.2 Framework Categories Explained
    - 5.3 Agent Patterns Dictionary
    - 5.4 Comparison Matrix
    - 5.5 Helper Functions
6.  [Agent Pattern Deep Dives](#6-agent-pattern-deep-dives)
    - 6.1 ReAct (Reason + Act)
    - 6.2 Plan and Execute
    - 6.3 Reflection / Self-Critique
    - 6.4 Multi-Agent Debate
    - 6.5 Tool Use / Function Calling
    - 6.6 Retrieval-Augmented Generation (RAG)
7.  [Interactive Demo Simulations](#7-interactive-demo-simulations)
    - 7.1 How Demos Work Without an LLM
    - 7.2 demo_react() Step by Step
    - 7.3 demo_plan_and_execute() Step by Step
    - 7.4 demo_reflection() Step by Step
    - 7.5 demo_multi_agent_debate() Step by Step
    - 7.6 The Demo Registry and run_demo() Wrapper
8.  [The FastAPI Backend](#8-the-fastapi-backend)
    - 8.1 Application Setup and CORS
    - 8.2 Request / Response Models
    - 8.3 Endpoint Reference
9.  [The Streamlit Dashboard](#9-the-streamlit-dashboard)
    - 9.1 API Communication Helpers
    - 9.2 Tab 1 -- Frameworks
    - 9.3 Tab 2 -- Patterns
    - 9.4 Tab 3 -- Compare (Radar Chart)
    - 9.5 Tab 4 -- Interactive Demos
10. [The Entry Point (main.py)](#10-the-entry-point-mainpy)
11. [Running the Platform](#11-running-the-platform)
    - 11.1 Local Setup
    - 11.2 Running with Docker Compose
    - 11.3 Three Launch Modes
12. [API Testing Examples](#12-api-testing-examples)
13. [Framework Comparison Dimensions Explained](#13-framework-comparison-dimensions-explained)
14. [When to Use Which Framework](#14-when-to-use-which-framework)
15. [When to Use Which Pattern](#15-when-to-use-which-pattern)
16. [Troubleshooting](#16-troubleshooting)
17. [Extending the Platform](#17-extending-the-platform)
18. [Summary](#18-summary)

---

## 1. Prerequisites

Before you begin, make sure you have the following installed:

- **Python 3.11 or later.** The type-hint syntax `dict | None` used in the
  knowledge base requires Python 3.10+.
- **pip** (ships with Python).
- **Docker and Docker Compose** (optional, only if you want to use the
  containerised setup).
- A terminal (macOS Terminal, iTerm2, Windows Terminal, or any Linux shell).
- A web browser for accessing the Streamlit dashboard and the FastAPI
  interactive docs.

No API keys are required. The demo simulations run entirely locally without
calling any LLM provider.

---

## 2. Project Overview

This project is a self-contained learning platform that teaches you about the
landscape of AI agent frameworks and design patterns. It has three main layers:

```
+------------------------------------------------------------+
|                   Streamlit Dashboard (ui.py)               |
|   Tabs: Frameworks | Patterns | Compare | Interactive Demos |
+-----------------------------+------------------------------+
                              |  HTTP (requests library)
                              v
+------------------------------------------------------------+
|                   FastAPI Backend (api.py)                  |
|   /frameworks  /patterns  /comparisons  /demos/run         |
+-----------------------------+------------------------------+
                              |  Python imports
                              v
+------------------------------------------------------------+
|   Knowledge Base (knowledge_base.py)  +  Demos (demos.py)  |
|   8 frameworks, 6 patterns, 6x6 comparison matrix          |
|   4 interactive agent pattern simulations                   |
+------------------------------------------------------------+
```

The bottom layer holds all the data and simulation logic. The middle layer
exposes it over HTTP. The top layer renders it in a browser.

---

## 3. What Are AI Agents and Why Learn About Them

An AI agent is a software system that uses a large language model (LLM) as its
reasoning core and can take autonomous actions to accomplish goals. Unlike a
simple chatbot that only generates text, an agent can:

- **Reason** about what steps to take next.
- **Use tools** like web search, code execution, or database queries.
- **Maintain state** across multiple turns of interaction.
- **Self-correct** by observing the results of its actions and adjusting.

Why does this matter? Because agents are the bridge between "impressive demo"
and "production system." A standalone LLM call can answer a question, but an
agent can research a topic across multiple sources, verify its findings, write
code, run it, fix the bugs, and deliver a tested solution.

The ecosystem has grown rapidly. There are now at least a dozen serious
frameworks for building agents, each with different strengths. This platform
catalogues eight of the most important ones, explains six foundational design
patterns, and lets you run simulated demos to see how each pattern behaves
step by step.

---

## 4. Project Structure

```
POC-06-AI-Agents-Learning-Platform/
|
|-- main.py                  Entry point. Accepts "api", "ui", or "all".
|-- requirements.txt         Six dependencies: fastapi, uvicorn, streamlit,
|                            plotly, requests, pydantic.
|-- Dockerfile               Single-stage Python 3.11 slim image.
|-- docker-compose.yml       Two services: api (port 8000) and ui (port 8501).
|
+-- src/
    |-- __init__.py          Empty. Makes src a package.
    |-- knowledge_base.py    Data layer: FRAMEWORKS, AGENT_PATTERNS, COMPARISONS.
    |-- api.py               FastAPI app with 8 endpoints.
    |-- ui.py                Streamlit app with 4 tabs.
    |
    +-- agents/
        |-- __init__.py      Empty. Makes agents a sub-package.
        +-- demos.py         4 simulation functions + registry + run_demo wrapper.
```

Every file has a single, clear responsibility. There are no circular imports.
The dependency graph flows one way: ui.py -> api.py -> knowledge_base.py and
demos.py.

---

## 5. The Knowledge Base Layer

File: `src/knowledge_base.py`

This module is a pure-data layer. It contains three dictionaries and five small
helper functions. There is no I/O, no network access, and no randomness. It is
the single source of truth for everything the platform knows about frameworks,
patterns, and comparison scores.

### 5.1 Frameworks Dictionary

The `FRAMEWORKS` dictionary has eight entries, keyed by a snake_case identifier:

| Key                 | Name                        | Category      |
|---------------------|-----------------------------|---------------|
| `langchain`         | LangChain                   | orchestration |
| `langgraph`         | LangGraph                   | orchestration |
| `autogen`           | AutoGen (Microsoft)         | multi-agent   |
| `crewai`            | CrewAI                      | multi-agent   |
| `openai_assistants` | OpenAI Assistants API       | platform      |
| `claude_agent_sdk`  | Claude Agent SDK (Anthropic)| platform      |
| `llamaindex`        | LlamaIndex                  | rag           |
| `dspy`              | DSPy (Stanford)             | optimization  |

Each entry is itself a dictionary with exactly these fields:

- `name` -- Human-readable name.
- `category` -- One of: orchestration, multi-agent, platform, rag, optimization.
- `description` -- One or two sentences explaining what it does.
- `key_features` -- A list of exactly six strings.
- `best_for` -- A single sentence describing the ideal use case.
- `complexity` -- One of: low, low-medium, medium, medium-high, high.
- `language` -- Programming language(s) supported.
- `github_stars` -- Approximate star count as a string (e.g., "90k+").
- `license` -- The software license (MIT, Proprietary, etc.).

### 5.2 Framework Categories Explained

There are five categories. Here is what each one means and why the frameworks
are grouped this way:

**Orchestration** frameworks (LangChain, LangGraph) provide the plumbing to
chain LLM calls together with tools, memory, and control flow. They do not
prescribe a particular agent architecture; instead they give you building
blocks. LangChain focuses on sequential chains and simple agents. LangGraph
adds graph-based state machines with cycles, branches, and persistence.

**Multi-agent** frameworks (AutoGen, CrewAI) are built specifically for
scenarios where multiple agents collaborate. AutoGen models this as
multi-agent conversations. CrewAI models it as a crew of role-playing agents
with defined goals and backstories. Both handle delegation, turn-taking, and
result aggregation.

**Platform** offerings (OpenAI Assistants API, Claude Agent SDK) are
vendor-managed environments. You get built-in tools (code interpreter, file
search, computer use) without managing infrastructure. The trade-off is less
flexibility and vendor lock-in.

**RAG** frameworks (LlamaIndex) specialise in connecting LLMs to external data.
LlamaIndex provides data connectors for 100+ sources, advanced indexing
strategies, and query engines. While other frameworks support RAG as a feature,
LlamaIndex makes it the core focus.

**Optimization** frameworks (DSPy) take a fundamentally different approach.
Instead of hand-writing prompts, you declare what you want (signatures), and
DSPy automatically optimizes the prompts and few-shot examples. This is the
most academic and the highest-complexity category.

### 5.3 Agent Patterns Dictionary

The `AGENT_PATTERNS` dictionary has six entries. Each describes a well-known
design pattern for structuring agent behaviour:

| Key                  | Name                          |
|----------------------|-------------------------------|
| `react`              | ReAct (Reason + Act)          |
| `plan_and_execute`   | Plan and Execute              |
| `reflection`         | Reflection / Self-Critique    |
| `multi_agent_debate` | Multi-Agent Debate            |
| `tool_use`           | Tool Use / Function Calling   |
| `rag`                | Retrieval-Augmented Generation|

Each entry contains:

- `name` -- Display name.
- `description` -- What the pattern does and how it works.
- `flow` -- A short text string showing the step sequence (e.g., "Think -> Act
  -> Observe -> ...").
- `strengths` -- A list of strings (advantages).
- `weaknesses` -- A list of strings (disadvantages).
- `example_use` -- A concrete scenario where this pattern shines.

### 5.4 Comparison Matrix

The `COMPARISONS` list contains six dictionaries, one per evaluation dimension.
Each dictionary maps six framework keys to an integer score from 1 to 5:

```
Dimension            | langchain | langgraph | crewai | autogen | openai_asst | llamaindex
---------------------+-----------+-----------+--------+---------+-------------+-----------
Ease of Setup        |     4     |     3     |   5    |    4    |      5      |     4
Multi-Agent Support  |     3     |     5     |   5    |    5    |      2      |     2
Production Readiness |     4     |     4     |   3    |    3    |      5      |     4
RAG Capabilities     |     4     |     3     |   2    |    2    |      4      |     5
Flexibility          |     5     |     5     |   3    |    4    |      2      |     4
Community & Docs     |     5     |     4     |   4    |    4    |      5      |     5
```

Note: Claude Agent SDK and DSPy are intentionally excluded from the comparison
matrix. The matrix focuses on the six frameworks that are most directly
comparable across all six dimensions.

### 5.5 Helper Functions

Five thin wrappers provide the public API of this module:

```python
get_all_frameworks() -> dict          # Returns the full FRAMEWORKS dict
get_framework(name: str) -> dict|None # Returns one entry or None
get_all_patterns() -> dict            # Returns the full AGENT_PATTERNS dict
get_pattern(name: str) -> dict|None   # Returns one entry or None
get_comparisons() -> list[dict]       # Returns the COMPARISONS list
```

These functions exist so that other modules never import the raw dictionaries
directly. If the data source changes in the future (e.g., loaded from a
database), only these functions need to change.

---

## 6. Agent Pattern Deep Dives

This section explains each of the six patterns conceptually, with ASCII flow
diagrams showing how data moves through the system.

### 6.1 ReAct (Reason + Act)

The ReAct pattern interleaves reasoning and action. At each step, the agent
thinks about what to do, performs an action (typically a tool call), observes
the result, and decides whether to continue or produce a final answer.

```
                +----------+
                |  THINK   |  "I need to search for X"
                +----+-----+
                     |
                     v
                +----------+
                |   ACT    |  Call web_search("X")
                +----+-----+
                     |
                     v
                +----------+
                | OBSERVE  |  "Found 5 results about X"
                +----+-----+
                     |
              +------+------+
              |  Enough?    |
              +--+-------+--+
              No |       | Yes
                 v       v
           (loop back  +----------+
            to THINK)  |  ANSWER  |
                       +----------+
```

**Strengths:** Transparent chain of reasoning; naturally incorporates tools;
can self-correct when observations contradict expectations.

**Weaknesses:** Can loop indefinitely if the agent never reaches a satisfying
answer; overhead of reasoning at every step makes it slow for trivial tasks.

**When to use it:** Research tasks, question answering with tool access, any
scenario where the agent needs to gather information incrementally.

### 6.2 Plan and Execute

This pattern separates planning from execution. First, a planner (which may be
a separate LLM call) generates a complete step-by-step plan. Then an executor
carries out each step in order.

```
+-------------------------+
|        PLANNER          |
|  1. Research background |
|  2. Identify components |
|  3. Analyze trade-offs  |
|  4. Synthesize findings |
+------------+------------+
             |
             v
+------------+------------+
|  EXECUTOR: Step 1       |---> Result 1
+------------+------------+
             |
             v
+------------+------------+
|  EXECUTOR: Step 2       |---> Result 2
+------------+------------+
             |
             v
+------------+------------+
|  EXECUTOR: Step 3       |---> Result 3
+------------+------------+
             |
             v
+------------+------------+
|  EXECUTOR: Step 4       |---> Result 4
+------------+------------+
             |
             v
+------------+------------+
|      FINAL ANSWER       |
+-------------------------+
```

**Strengths:** Structured and predictable; easier to debug because you can
inspect the plan before execution; works well for complex multi-step tasks.

**Weaknesses:** Inflexible if the plan turns out to be wrong partway through;
upfront planning cost is wasted if the task is simple.

**When to use it:** Project decomposition, coding tasks that need multiple
files, any scenario with a clear sequence of subtasks.

### 6.3 Reflection / Self-Critique

The agent generates an initial output, then evaluates it against quality
criteria (sometimes using a separate "critic" agent). It revises, re-evaluates,
and repeats until the output passes.

```
+-----------+     +-----------+     +-------------+
| GENERATE  |---->| CRITIQUE  |---->|   REVISE    |
| (draft 1) |     | score: 5  |     | (draft 2)   |
+-----------+     | issues: 3 |     +------+------+
                  +-----------+            |
                                           v
                                    +-----------+
                                    | CRITIQUE  |
                                    | score: 8  |
                                    | approved  |
                                    +-----+-----+
                                          |
                                          v
                                    +-----------+
                                    |  OUTPUT   |
                                    +-----------+
```

**Strengths:** Produces higher-quality output; catches errors and omissions;
mimics how humans revise their work.

**Weaknesses:** Slower due to multiple rounds; can over-revise (polishing
endlessly without meaningful improvement); requires well-defined evaluation
criteria.

**When to use it:** Content generation, code writing with quality requirements,
any scenario where correctness matters more than speed.

### 6.4 Multi-Agent Debate

Multiple agents with different perspectives (roles, biases, expertise domains)
argue about a topic. A moderator agent synthesizes the debate into a balanced
conclusion.

```
+-------------+    +-------------+    +--------------+
|  OPTIMIST   |    |   SKEPTIC   |    |  PRAGMATIST  |
| "Invest     |    | "Too risky, |    | "Start small,|
|  heavily!"  |    |  wait."     |    |  measure."   |
+------+------+    +------+------+    +------+-------+
       |                  |                  |
       +------------------+------------------+
                          |
                          v
                  +-------+--------+
                  |   MODERATOR    |
                  | "Pilot program |
                  |  with metrics" |
                  +----------------+
```

**Strengths:** Surfaces diverse perspectives; reduces individual model bias;
produces more nuanced decisions.

**Weaknesses:** Expensive because it requires multiple LLM calls (one per agent
plus the moderator); the roles must be carefully designed to avoid groupthink.

**When to use it:** Strategic decisions, policy analysis, any scenario where
you want to hear multiple sides before committing.

### 6.5 Tool Use / Function Calling

The agent has a catalogue of available tools (functions, APIs, databases). When
it encounters a task that requires external capabilities, it selects the
appropriate tool, formats the input, calls it, and processes the result.

```
+------------------+
| UNDERSTAND TASK  |  "User wants a refund for order #123"
+--------+---------+
         |
         v
+------------------+
|   SELECT TOOL    |  Choose: database_lookup
+--------+---------+
         |
         v
+------------------+
|    CALL TOOL     |  database_lookup(order_id=123)
+--------+---------+
         |
         v
+------------------+
|  PROCESS RESULT  |  "Order found. Status: delivered."
+--------+---------+
         |
         v
+------------------+
|     RESPOND      |  "Your order was delivered on..."
+------------------+
```

**Strengths:** Extends the LLM beyond text generation; enables real-world
interactions (read databases, call APIs, execute code); precise for structured
tasks.

**Weaknesses:** Tool design is critical -- a poorly defined tool schema leads
to misuse; error handling adds complexity.

**When to use it:** Customer support, data analysis, any scenario where the
agent needs to interact with external systems.

### 6.6 Retrieval-Augmented Generation (RAG)

Before generating a response, the agent retrieves relevant documents from a
knowledge base. The retrieved text is injected into the prompt as context,
grounding the answer in real data rather than relying solely on the model's
training data.

```
+------------------+
|   USER QUERY     |  "What is our refund policy?"
+--------+---------+
         |
         v
+------------------+
| RETRIEVE DOCS    |  Search vector store -> 3 relevant chunks
+--------+---------+
         |
         v
+------------------+
| BUILD CONTEXT    |  Prepend chunks to the prompt
+--------+---------+
         |
         v
+------------------+
| GENERATE ANSWER  |  LLM produces answer grounded in docs
+--------+---------+
         |
         v
+------------------+
| ANSWER + SOURCES |  "Per our policy (doc #7)..."
+------------------+
```

**Strengths:** Grounded in real data; reduces hallucination; can incorporate
up-to-date or proprietary information that the model was not trained on.

**Weaknesses:** Quality depends heavily on retrieval (garbage in, garbage out);
chunking strategy and embedding model choice matter a lot.

**When to use it:** Enterprise Q&A, documentation search, any scenario where
accuracy and citations are required.

---

## 7. Interactive Demo Simulations

File: `src/agents/demos.py`

### 7.1 How Demos Work Without an LLM

A key design decision of this platform is that all four interactive demos run
entirely locally with no LLM API calls. They use Python's `random` module to
simulate variability (e.g., random tool selection, random scores) and
hard-coded text templates to produce realistic-looking agent traces.

This means:
- No API keys needed.
- No cost per demo run.
- Instant execution (sub-millisecond).
- Deterministic structure with controlled randomness.

The purpose is educational: you see the *shape* of each pattern (what steps
happen in what order) without needing a live model.

### 7.2 demo_react(task) Step by Step

Input: A task string (e.g., "How to build a scalable web app").
Output: A list of 7 step dictionaries.

Here is exactly what happens inside the function:

```
Step 1  type="thought"      Agent reasons about what info it needs.
Step 2  type="action"       Randomly picks tool A from [web_search, calculator,
                            database_lookup]. Formats a search query.
Step 3  type="observation"  Simulated result from tool A.
Step 4  type="thought"      Agent decides to verify with another source.
Step 5  type="action"       Picks tool B (different from tool A).
Step 6  type="observation"  Simulated confirmation from tool B.
Step 7  type="answer"       Final synthesised answer referencing both tools.
```

The action steps include a `tool` field and an `input` field. The observation
steps include only `content`. The final answer step mentions both tools by name.

### 7.3 demo_plan_and_execute(task) Step by Step

Input: A task string.
Output: A dictionary with keys: task, plan, executions, final_answer.

```
Planning phase:
  Generates a fixed 4-step plan:
    1. "Research background on '{task}'"
    2. "Identify key components and requirements"
    3. "Analyze trade-offs and alternatives"
    4. "Synthesize findings into a recommendation"

Execution phase:
  For each of the 4 steps, creates an execution record:
    - step:        1-based index
    - plan:        the plan text
    - status:      always "completed"
    - result:      text with a random count of data points (3-8)
    - duration_ms: random between 100 and 2000

Final answer:
  A summary string referencing the number of steps completed.
```

### 7.4 demo_reflection(task) Step by Step

Input: A task string.
Output: A dictionary with keys: task, iterations (list of 2), final_output.

```
Iteration 1:
  draft:    A vague, high-level initial analysis.
  critique:
    score:     Random integer 4-6 (mediocre).
    issues:    ["Too vague", "Missing quantitative analysis",
                "Conclusion could be stronger"]
    strengths: ["Good high-level structure", "Covers the main topic"]

Iteration 2:
  draft:    A revised analysis with specific examples, percentages,
            and a clear recommendation.
  critique:
    score:     Random integer 7-9 (good to excellent).
    issues:    ["Minor: could add more references"]
    strengths: ["Specific and actionable", "Includes quantitative data",
                "Clear structure and recommendation"]
    approved:  True

final_output: The revision from iteration 2.
```

The key teaching point is the quality jump between iteration 1 and iteration 2.
The first draft is intentionally weak so the critique has something substantive
to say.

### 7.5 demo_multi_agent_debate(topic) Step by Step

Input: A topic string.
Output: A dictionary with keys: topic, agents, synthesis, recommendation.

```
Three agents argue:

  Optimist:   "The potential is enormous. 2-3x productivity gains.
               Invest heavily now."

  Skeptic:    "30% failure rate in production. Overhyped.
               Wait for it to stabilize."

  Pragmatist: "Start with a small pilot project. Measure over 3 months.
               Allocate 20% of budget."

Moderator synthesis:
  Acknowledges all three perspectives. Recommends a measured pilot
  program with clear success criteria and a 3-month evaluation period.

Recommendation: "Proceed with controlled pilot"
```

### 7.6 The Demo Registry and run_demo() Wrapper

At the bottom of `demos.py`, a `DEMO_REGISTRY` dictionary maps pattern keys to
their functions and display names:

```python
DEMO_REGISTRY = {
    "react":              {"fn": demo_react,              "name": "ReAct (Reason + Act)"},
    "plan_and_execute":   {"fn": demo_plan_and_execute,   "name": "Plan and Execute"},
    "reflection":         {"fn": demo_reflection,         "name": "Reflection / Self-Critique"},
    "multi_agent_debate": {"fn": demo_multi_agent_debate, "name": "Multi-Agent Debate"},
}
```

The `run_demo(pattern, task)` function is the single entry point. It:

1. Checks whether `pattern` is a valid key in `DEMO_REGISTRY`. If not, returns
   an error dictionary listing the available patterns.
2. Records `time.time()` before calling the demo function.
3. Calls `DEMO_REGISTRY[pattern]["fn"](task)`.
4. Records `time.time()` after the call and computes elapsed seconds (rounded
   to 4 decimal places).
5. Returns a dictionary with: pattern, pattern_name, task, result, and
   elapsed_seconds.

This wrapper provides a uniform interface for the API layer and adds timing
instrumentation without cluttering the individual demo functions.

---

## 8. The FastAPI Backend

File: `src/api.py`

### 8.1 Application Setup and CORS

The FastAPI app is created with a title and version:

```python
app = FastAPI(title="AI Agents Learning Platform", version="1.0.0")
```

CORS middleware is added with fully permissive settings (all origins, all
methods, all headers). This is appropriate for a learning/demo environment
where the Streamlit UI may run on a different port or host.

### 8.2 Request / Response Models

There is one Pydantic model for incoming demo requests:

```python
class DemoRequest(BaseModel):
    pattern: str
    task: str = "Building a production ML pipeline"
```

The `task` field has a default value, so you can POST with just `{"pattern": "react"}`
and the default task will be used.

All response models are implicit (FastAPI auto-serializes dicts and lists).

### 8.3 Endpoint Reference

| Method | Path               | Description                        | Query Params          |
|--------|--------------------|------------------------------------|-----------------------|
| GET    | /health            | Health check                       | --                    |
| GET    | /frameworks        | List all frameworks                | ?category= (optional) |
| GET    | /frameworks/{name} | Get one framework by key           | --                    |
| GET    | /patterns          | List all agent patterns            | --                    |
| GET    | /patterns/{name}   | Get one pattern by key             | --                    |
| GET    | /comparisons       | Get the full comparison matrix     | --                    |
| GET    | /demos             | List available demo patterns       | --                    |
| POST   | /demos/run         | Run an interactive demo            | Body: DemoRequest     |

**Error handling:**

- `GET /frameworks/{name}` returns HTTP 404 if the name is not found.
- `GET /patterns/{name}` returns HTTP 404 if the name is not found.
- `POST /demos/run` returns HTTP 400 if the pattern is not in the registry.

**Response shapes:**

```
GET /health
  {"status": "healthy", "service": "ai-agents-learning-platform"}

GET /frameworks
  {"frameworks": { ... }, "total": 8}

GET /frameworks?category=orchestration
  {"frameworks": { ... }, "total": 2}

GET /frameworks/langchain
  {"name": "LangChain", "category": "orchestration", ... }

GET /patterns
  {"patterns": { ... }, "total": 6}

GET /patterns/react
  {"name": "ReAct (Reason + Act)", "description": "...", ... }

GET /comparisons
  {"comparisons": [ ... ]}

GET /demos
  {"demos": {"react": "ReAct (Reason + Act)", ...}, "total": 4}

POST /demos/run  {"pattern": "react", "task": "my task"}
  {"pattern": "react", "pattern_name": "ReAct (Reason + Act)",
   "task": "my task", "result": [...], "elapsed_seconds": 0.0001}
```

---

## 9. The Streamlit Dashboard

File: `src/ui.py`

### 9.1 API Communication Helpers

The dashboard communicates with the FastAPI backend over HTTP using the
`requests` library. Two helper functions handle this:

```python
API_URL = os.getenv("API_URL", "http://localhost:8000")

def api_get(path):   # GET request, 10s timeout
def api_post(path, data):  # POST request, 30s timeout
```

Both functions catch `requests.ConnectionError` and display a Streamlit error
message telling you to check whether the API server is running. The `API_URL`
is configurable via environment variable, which is how the Docker Compose
setup points the UI container at the API container (`http://api:8000`).

### 9.2 Tab 1 -- Frameworks

This tab fetches `GET /frameworks` and displays each framework as an
expandable card. At the top is a selectbox that lets you filter by category
(or view "All"). Each card shows:

- Name and category in the header.
- Description (bold).
- Best-for statement.
- Complexity and language on one line.
- GitHub stars and license on another line.
- A bulleted list of all six key features.

### 9.3 Tab 2 -- Patterns

This tab fetches `GET /patterns` and displays each pattern in an expander.
Each expander contains:

- The pattern description (bold).
- The flow string rendered as a code block (using `st.code()`).
- Two columns side by side: strengths on the left, weaknesses on the right.
- An example use case at the bottom.

### 9.4 Tab 3 -- Compare (Radar Chart)

This tab fetches `GET /comparisons` and renders two visualizations:

1. **Radar chart (Plotly).** Each of the six frameworks gets its own trace on
   a polar chart. The six dimensions form the axes. The radial axis runs from
   0 to 5. Each trace uses `fill="toself"` with 0.6 opacity so overlapping
   areas are visible. The chart is 500px tall.

2. **Score table.** A pandas DataFrame with dimensions as the index and
   frameworks as columns. Displayed using `st.dataframe()` at full container
   width.

How the radar chart data is constructed:

```python
df = pd.DataFrame(comparisons).set_index("dimension")
# df now has 6 rows (dimensions) and 6 columns (frameworks)
# For each framework column, the trace wraps around by appending
# the first value at the end:
r = df[col].tolist() + [df[col].tolist()[0]]
theta = df.index.tolist() + [df.index.tolist()[0]]
```

### 9.5 Tab 4 -- Interactive Demos

This tab is the most complex. It:

1. Fetches `GET /demos` to populate a selectbox with the four available demos.
   The `format_func` parameter maps internal keys (e.g., "react") to display
   names (e.g., "ReAct (Reason + Act)").

2. Shows a text input pre-filled with "How to build a scalable web application".

3. When the user clicks "Run Demo", it POSTs to `/demos/run` with the selected
   pattern and task. A spinner displays while waiting.

4. After the response arrives, it shows elapsed time as a success banner, then
   renders the result differently depending on the pattern:

   **ReAct:** Each step is rendered with a different Streamlit alert type:
   - thought -> `st.info()` (blue)
   - action -> `st.warning()` (yellow)
   - observation -> `st.success()` (green)
   - answer -> `st.markdown()` (plain)

   **Plan and Execute:** The plan is shown as a numbered list. Each execution
   step shows its status, duration in milliseconds, and result text. The final
   answer is displayed with `st.markdown()`.

   **Reflection:** Each iteration gets its own subheader. The draft text, score
   (as a metric widget), strengths, and issues are displayed. Two columns
   separate strengths and issues. The final output is shown at the bottom.

   **Multi-Agent Debate:** Each agent gets a subheader with its role name,
   followed by its argument text. The synthesis is shown with `st.markdown()`,
   and the recommendation is shown in bold.

---

## 10. The Entry Point (main.py)

File: `main.py`

This file provides a single command-line interface for launching the platform.
It accepts one argument:

| Argument | What it does                                    | Ports          |
|----------|-------------------------------------------------|----------------|
| `api`    | Starts only the FastAPI server with hot reload  | 8000           |
| `ui`     | Starts only the Streamlit dashboard             | 8501           |
| `all`    | Starts the API as a background process, then    | 8000 and 8501  |
|          | starts the UI in the foreground                 |                |

If no argument is given, the default is `api`.

When running in `all` mode:
- The API is launched as a subprocess using `subprocess.Popen` (non-blocking).
- The UI is launched using `subprocess.run` (blocking -- the script waits here).
- When the UI process ends (e.g., you press Ctrl+C), the `finally` block
  terminates the API subprocess cleanly.

When running in `api` mode, the server is started with `reload=True`, which
means any changes to source files will automatically restart the server. This
is convenient during development.

---

## 11. Running the Platform

### 11.1 Local Setup

Step 1: Navigate to the project directory.

```bash
cd /path/to/POC-06-AI-Agents-Learning-Platform
```

Step 2: Create and activate a virtual environment (recommended).

```bash
python -m venv .venv
source .venv/bin/activate       # macOS / Linux
# .venv\Scripts\activate        # Windows
```

Step 3: Install dependencies.

```bash
pip install -r requirements.txt
```

This installs six packages: fastapi, uvicorn, streamlit, plotly, requests,
and pydantic. Their transitive dependencies (starlette, click, etc.) will be
installed automatically.

Step 4: Start the platform. You have three options:

```bash
# Option A: API only (port 8000)
python main.py api

# Option B: UI only (port 8501) -- requires API to already be running
python main.py ui

# Option C: Both at once (ports 8000 and 8501)
python main.py all
```

Step 5: Open your browser.

- API interactive docs: http://localhost:8000/docs
- Streamlit dashboard:  http://localhost:8501

### 11.2 Running with Docker Compose

If you prefer containers:

```bash
docker compose up --build
```

This builds two images from the same Dockerfile and starts two containers:

- `api` on port 8000, with a health check that polls `/health` every 10
  seconds.
- `ui` on port 8501, which waits for the API to be healthy before starting.
  The `API_URL` environment variable is set to `http://api:8000` so the UI
  container can reach the API container by Docker's internal DNS.

To stop:

```bash
docker compose down
```

### 11.3 Three Launch Modes

Here is a decision tree for which mode to use:

```
Are you developing the API?
  YES -> python main.py api    (hot reload enabled)

Are you developing the UI?
  YES -> Run API in one terminal: python main.py api
         Run UI in another:       python main.py ui

Do you just want to explore the platform?
  YES -> python main.py all    (or docker compose up)
```

---

## 12. API Testing Examples

Once the API is running on port 8000, you can test every endpoint with curl.

**Health check:**

```bash
curl http://localhost:8000/health
```

Expected: `{"status":"healthy","service":"ai-agents-learning-platform"}`

**List all frameworks:**

```bash
curl http://localhost:8000/frameworks
```

Expected: JSON with `"total": 8` and all eight framework entries.

**Filter frameworks by category:**

```bash
curl "http://localhost:8000/frameworks?category=multi-agent"
```

Expected: Only `autogen` and `crewai` in the response.

**Get a single framework:**

```bash
curl http://localhost:8000/frameworks/langchain
```

Expected: Full detail for LangChain including all six key features.

**Get a framework that does not exist:**

```bash
curl http://localhost:8000/frameworks/nonexistent
```

Expected: HTTP 404 with `{"detail":"Framework 'nonexistent' not found"}`.

**List all patterns:**

```bash
curl http://localhost:8000/patterns
```

Expected: JSON with `"total": 6` and all six pattern entries.

**Get a single pattern:**

```bash
curl http://localhost:8000/patterns/react
```

Expected: Full detail for the ReAct pattern.

**Get the comparison matrix:**

```bash
curl http://localhost:8000/comparisons
```

Expected: A list of 6 dimension objects, each with scores for 6 frameworks.

**List available demos:**

```bash
curl http://localhost:8000/demos
```

Expected:
```json
{
  "demos": {
    "react": "ReAct (Reason + Act)",
    "plan_and_execute": "Plan and Execute",
    "reflection": "Reflection / Self-Critique",
    "multi_agent_debate": "Multi-Agent Debate"
  },
  "total": 4
}
```

**Run the ReAct demo:**

```bash
curl -X POST http://localhost:8000/demos/run \
  -H "Content-Type: application/json" \
  -d '{"pattern": "react", "task": "How to deploy ML models"}'
```

Expected: A response with 7 steps (thought, action, observation, thought,
action, observation, answer) and an elapsed_seconds field.

**Run the Plan and Execute demo (using default task):**

```bash
curl -X POST http://localhost:8000/demos/run \
  -H "Content-Type: application/json" \
  -d '{"pattern": "plan_and_execute"}'
```

Expected: A 4-step plan, 4 execution records, and a final answer. The default
task "Building a production ML pipeline" is used.

**Run the Reflection demo:**

```bash
curl -X POST http://localhost:8000/demos/run \
  -H "Content-Type: application/json" \
  -d '{"pattern": "reflection", "task": "Best practices for API design"}'
```

Expected: Two iterations with scores (first: 4-6, second: 7-9), issues,
strengths, and a final output.

**Run the Multi-Agent Debate demo:**

```bash
curl -X POST http://localhost:8000/demos/run \
  -H "Content-Type: application/json" \
  -d '{"pattern": "multi_agent_debate", "task": "Adopting microservices"}'
```

Expected: Three agent arguments (optimist, skeptic, pragmatist), a synthesis,
and a recommendation.

**Run a demo with an invalid pattern:**

```bash
curl -X POST http://localhost:8000/demos/run \
  -H "Content-Type: application/json" \
  -d '{"pattern": "invalid_pattern", "task": "test"}'
```

Expected: HTTP 400 with an error message listing available patterns.

You can also explore all endpoints interactively at http://localhost:8000/docs
(Swagger UI) or http://localhost:8000/redoc (ReDoc).

---

## 13. Framework Comparison Dimensions Explained

The comparison matrix scores six frameworks across six dimensions on a 1-5
scale. Here is what each dimension measures:

**Ease of Setup (How fast can you go from zero to a working agent?)**

- Score 5: Install one package, write 10 lines, and you have a working agent.
  (CrewAI, OpenAI Assistants)
- Score 3: Requires understanding multiple concepts (graphs, state, edges)
  before writing your first agent. (LangGraph)

**Multi-Agent Support (How well does it handle multiple agents collaborating?)**

- Score 5: Multi-agent is the core design primitive. Built-in orchestration,
  turn-taking, delegation. (LangGraph, CrewAI, AutoGen)
- Score 2: Single-agent focus. Multi-agent possible but requires custom code.
  (OpenAI Assistants, LlamaIndex)

**Production Readiness (How mature, stable, and battle-tested is it?)**

- Score 5: Managed infrastructure, SLAs, enterprise support. (OpenAI Assistants)
- Score 3: Active development, APIs still changing, fewer production case
  studies. (CrewAI, AutoGen)

**RAG Capabilities (How well does it handle retrieval-augmented generation?)**

- Score 5: RAG is the primary purpose. 100+ data connectors, advanced indexing,
  query engines. (LlamaIndex)
- Score 2: No built-in RAG. You must integrate retrieval yourself. (CrewAI,
  AutoGen)

**Flexibility (How much control do you have over agent behaviour?)**

- Score 5: Full control over every aspect -- prompts, tools, control flow,
  state, memory. (LangChain, LangGraph)
- Score 2: Opinionated / managed. You work within the provider's abstractions.
  (OpenAI Assistants)

**Community and Docs (How good are the docs, tutorials, and community support?)**

- Score 5: Extensive documentation, many tutorials, large Discord/GitHub
  community, regular updates. (LangChain, OpenAI Assistants, LlamaIndex)
- Score 4: Good documentation but smaller community or newer project. (LangGraph,
  CrewAI, AutoGen)

---

## 14. When to Use Which Framework

This section provides decision guidance based on your use case.

**"I am building a simple single-agent chatbot with tool access."**
  Use OpenAI Assistants API or Claude Agent SDK. They provide managed
  infrastructure and built-in tools with minimal code.

**"I need multiple agents working together as a team."**
  Use CrewAI if you want role-based agents with clear responsibilities.
  Use AutoGen if you want conversational multi-agent collaboration.
  Use LangGraph if you need fine-grained control over the state machine.

**"I am building a RAG application over enterprise documents."**
  Use LlamaIndex. It has purpose-built abstractions for data ingestion,
  indexing, and querying. LangChain is a solid second choice if you also need
  agent capabilities beyond RAG.

**"I want to optimize my prompts systematically, not by hand."**
  Use DSPy. Its declarative signatures and automatic optimization are
  unique in the ecosystem.

**"I need a general-purpose framework that can do a bit of everything."**
  Use LangChain. It has the largest ecosystem, the most integrations, and
  covers the widest range of use cases.

**"I need production-grade reliability with enterprise support."**
  Use OpenAI Assistants (managed by OpenAI) or LangGraph/LangChain (backed
  by LangChain Inc. with commercial offerings).

**"I want to build safe, reliable agents with Claude."**
  Use the Claude Agent SDK. It integrates MCP (Model Context Protocol),
  extended thinking, and computer use capabilities natively.

---

## 15. When to Use Which Pattern

**ReAct** -- Choose this when your agent needs to gather information
incrementally and you want transparent reasoning traces. Classic use: a
research assistant that searches, reads, and synthesizes.

**Plan and Execute** -- Choose this when the task is complex but decomposable
into clear steps. Classic use: a project manager agent that breaks work into
subtasks and executes them sequentially.

**Reflection** -- Choose this when output quality matters more than speed and
you want the agent to catch its own mistakes. Classic use: a code review agent
or a content editor.

**Multi-Agent Debate** -- Choose this when you want diverse perspectives on a
decision and the cost of multiple LLM calls is acceptable. Classic use: a
strategy evaluation system.

**Tool Use** -- Choose this when the agent needs to interact with external
systems (databases, APIs, calculators). This is less a standalone pattern and
more a capability that other patterns incorporate. Classic use: a customer
support agent.

**RAG** -- Choose this when answers must be grounded in specific documents and
you need citations. This is also often combined with other patterns. Classic
use: an enterprise Q&A bot.

In practice, production agents often combine multiple patterns. For example, a
ReAct agent might use Tool Use for its actions and RAG for its knowledge
retrieval. A Plan and Execute agent might use Reflection on each step's output.

---

## 16. Troubleshooting

### "Cannot reach the API. Is the server running?"

This error appears in the Streamlit UI when it cannot connect to the FastAPI
backend.

Causes and fixes:
- The API is not running. Start it with `python main.py api` in a separate
  terminal, then start the UI.
- The API is running on a different port. Check that it is on port 8000.
- You are using Docker Compose and the API container has not passed its health
  check yet. Wait 10-15 seconds and refresh.

### Port 8000 or 8501 is already in use

Find and kill the process using the port:

```bash
# macOS / Linux
lsof -i :8000
kill <PID>

# Or use a different port by editing main.py or passing args to uvicorn
```

### ModuleNotFoundError: No module named 'src'

This happens when you run a file directly instead of through main.py, or when
your working directory is wrong.

Fix: Always run from the project root:

```bash
cd /path/to/POC-06-AI-Agents-Learning-Platform
python main.py api
```

### ImportError: cannot import name ... from 'pydantic'

This happens if you have Pydantic v1 installed. The code requires Pydantic v2.

Fix:

```bash
pip install --upgrade pydantic>=2.0.0
```

### Streamlit "DuplicateWidgetID" error

This should not happen with the current code, but if you modify the UI and
create widgets in a loop without unique keys, you will see this error.

Fix: Add a `key` parameter to any widget created inside a loop:

```python
st.text_input("Label", key=f"input_{i}")
```

### Docker build fails with "pip: No matching distribution"

This usually means your Docker image is using an older Python version that
does not have a compatible wheel for one of the dependencies.

Fix: Ensure the Dockerfile uses `python:3.11-slim` or later.

### Radar chart does not display in the Compare tab

This happens if the API returns an empty comparisons list.

Fix: Verify the `/comparisons` endpoint returns data:

```bash
curl http://localhost:8000/comparisons
```

If it returns `{"comparisons": []}`, there is an issue with the knowledge base
import.

### Demo results contain "error" key

This means you passed an invalid pattern name to the `/demos/run` endpoint.

Fix: Check available patterns at `GET /demos` and use one of the listed keys.

---

## 17. Extending the Platform

Here are some ways to build on this project:

### Adding a new framework to the knowledge base

1. Open `src/knowledge_base.py`.
2. Add a new entry to the `FRAMEWORKS` dictionary following the exact same
   structure as existing entries (name, category, description, key_features
   with exactly 6 items, best_for, complexity, language, github_stars, license).
3. If you want it in the comparison matrix, add the new key to each of the six
   dictionaries in the `COMPARISONS` list.
4. Restart the API. The new framework will appear in the Frameworks tab and
   (if added to COMPARISONS) in the radar chart.

### Adding a new agent pattern

1. Open `src/knowledge_base.py`.
2. Add a new entry to the `AGENT_PATTERNS` dictionary.
3. Optionally, create a demo function in `src/agents/demos.py` and register it
   in `DEMO_REGISTRY`.
4. If you add a demo, the UI will automatically pick it up from `GET /demos`.

### Adding a new demo

1. Write a function in `src/agents/demos.py` that takes a `task` string and
   returns a dictionary or list.
2. Add it to `DEMO_REGISTRY`.
3. In `src/ui.py`, add an `elif pattern == "your_new_pattern":` block in
   Tab 4 to handle the rendering of your new demo's output.

### Connecting to a real LLM

The demo functions currently simulate agent behaviour. To connect to a real
LLM:

1. Add your LLM client library to `requirements.txt` (e.g., `openai`,
   `anthropic`).
2. Replace the hard-coded text in demo functions with actual LLM API calls.
3. Add your API key to environment variables (never hard-code keys).
4. Increase the POST timeout in `ui.py` (currently 30 seconds) if LLM calls
   take longer.

### Adding authentication

The API currently has no authentication (appropriate for local learning). To
add it:

1. Use FastAPI's built-in security utilities (`from fastapi.security import ...`).
2. Add a dependency to protected endpoints.
3. Update the Streamlit helpers to pass an Authorization header.

---

## 18. Summary

This platform is structured in three clean layers:

1. **Data layer** (`knowledge_base.py` and `demos.py`): Contains all
   structured data about 8 frameworks, 6 patterns, a 6x6 comparison matrix,
   and 4 interactive demo simulations. No I/O, no network calls. Pure Python
   data structures and functions.

2. **API layer** (`api.py`): A FastAPI application with 8 endpoints that
   expose the data layer over HTTP. Supports filtering, detail lookups, and
   running demos. Returns JSON with consistent response shapes.

3. **UI layer** (`ui.py`): A Streamlit dashboard with 4 tabs that fetches
   data from the API and renders it as expandable cards, flow diagrams, radar
   charts, score tables, and color-coded agent traces.

Key design decisions:

- **No LLM required.** Every demo runs locally using simulated data. This
  eliminates cost, latency, and API key management for a learning tool.
- **Separation of concerns.** The UI never imports from the knowledge base or
  demos directly -- it always goes through the API. This means you could
  replace the Streamlit frontend with a React app, a CLI tool, or anything
  else that speaks HTTP.
- **Uniform data shapes.** Every framework has the same fields. Every pattern
  has the same fields. This makes iteration in the UI straightforward.
- **Docker-ready.** The docker-compose.yml defines both services with a health
  check dependency, so the UI waits for the API to be ready.

The platform covers the most important frameworks (LangChain, LangGraph,
AutoGen, CrewAI, OpenAI Assistants, Claude Agent SDK, LlamaIndex, DSPy) and
the most fundamental patterns (ReAct, Plan and Execute, Reflection,
Multi-Agent Debate, Tool Use, RAG). It is designed to be a hands-on reference
that you can explore, extend, and eventually replace with real LLM-powered
agents as you learn.

---

## 19. Interview Questions

*Situation-based and technical questions from AI Engineer and ML Platform interviews. Sourced from LinkedIn posts, Glassdoor reports, and engineering blog discussions at companies building with LLMs.*

---

### Situational / Behavioral Questions

**Q: "A PM asks: should we use CrewAI or LangGraph for our new customer support bot? Walk through how you'd evaluate and recommend."**

A: I'd evaluate across four dimensions before giving a recommendation: (1) **Workflow topology** — is the workflow sequential with well-defined roles (triage → resolution → escalation)? CrewAI's role-based crew abstraction maps naturally to this. Does it need cycles, conditional routing, or precise state management? LangGraph's graph-based state machine handles complex topologies better. (2) **Team familiarity** — a team already using LangChain will find LangGraph's mental model familiar (it extends LangChain). CrewAI has its own concepts (agents, tasks, crews) that require a separate learning curve. (3) **Production readiness** — LangGraph (backed by LangChain Inc. with commercial offerings) has more mature monitoring (LangSmith), persistence, and deployment tooling. CrewAI is evolving rapidly but has a shorter production track record. (4) **Testability** — LangGraph's explicit state machine is easier to unit test: mock a node, inject a state, assert the output state. CrewAI's conversational multi-agent approach is harder to test deterministically. My recommendation: **LangGraph for production-grade workflows requiring reliability and observability**; **CrewAI for rapid prototyping** where you want human-readable role definitions and can tolerate less control over the execution flow.

**Q: "You built a ReAct agent for data analysis and it's getting stuck in a reasoning loop, calling the same tool 10 times. How do you diagnose and fix it?"**

A: ReAct loops happen when observations don't give the agent enough signal to decide it's done. Diagnosis: enable verbose logging — print every thought/action/observation tuple. Look for the pattern where the agent rephrases the same action repeatedly. Three common root causes: (1) **Tool output is ambiguous** — if `database_lookup()` returns an empty result set with no explanation, the agent reasons "maybe I searched wrong" and retries with slightly different phrasing. Fix: tools must return explicit status messages: `{"rows": [], "status": "no_results", "suggestion": "Try a broader date range or different customer_id format"}`. Give the agent something concrete to reason about. (2) **Stopping criteria unclear** — the system prompt doesn't tell the agent what "done" means. Fix: add explicit stopping language: "When you have gathered enough information to fully answer the user's question, output exactly: FINAL ANSWER: [your complete answer]. Do not make further tool calls after this." (3) **Missing max iterations cap** — always set `max_iterations=10` and `max_execution_time=60` in the agent constructor. Without a hard cap, the loop runs until context window overflow and the API returns an error rather than a graceful response.

**Q: "You're designing an AI agent for medical triage assistance. The team is debating between ReAct and Plan-and-Execute. Which do you recommend and why?"**

A: I'd recommend **Plan-and-Execute with Reflection** — and I'd push back on ReAct for this use case. Here's why: (1) **Auditability requirement** — medical triage decisions must be explainable and auditable. Plan-and-Execute generates an explicit step-by-step plan ("Step 1: assess chief complaint. Step 2: check vital signs against reference ranges. Step 3: cross-reference medications for contraindications.") that a clinician can review before execution begins. ReAct's interleaved reasoning and actions are harder to audit step-by-step. (2) **Predictability** — Plan-and-Execute follows a defined sequence. ReAct dynamically chooses the next action based on each observation — in a high-stakes domain, unexpected action sequences are a safety risk. (3) **Reflection improves accuracy** — add a Reflection node that reviews the triage recommendation against clinical guidelines before surfacing it to the clinician. If the reflection agent flags a concern, it revises. (4) **Human-in-the-loop gate** — Plan-and-Execute makes it natural to add a `requires_physician_confirmation` step in the plan for high-severity assessments. The plan literally says "Step 5: present findings to physician for final decision." This is architecturally harder to enforce in ReAct's dynamic action selection.

---

### Technical Deep-Dive Questions

**Q: "Explain the ReAct pattern in depth. What are its production failure modes?"**

A: ReAct (Reason + Act) interleaves reasoning steps ("I need the customer's order history to answer this") with action steps (calling `get_order_history(customer_id=123)`), followed by observations (the tool's return value). The agent iterates until it has enough information to produce a Final Answer. Strengths: transparent reasoning trace (every step is logged), adapts dynamically to unexpected tool results, handles open-ended tasks where the right action sequence isn't known upfront. Production failure modes: (1) **Tool call explosion** — the agent reasons "I need more precision" and makes 30 tool calls before concluding. Hard limit with `max_iterations`. (2) **Hallucinated tool inputs** — the agent generates a `customer_id` in its reasoning that doesn't exist, then calls the database with it. Result: valid tool call, empty result, confused agent. Fix: validate tool inputs against known ranges before execution. (3) **Error misinterpretation** — an API returns HTTP 429 (rate limit); the agent reasons about "rate limit" as a domain concept rather than a technical error, producing bizarre downstream reasoning. Tool wrappers must translate all technical errors to clear natural language: "The database is temporarily busy. Wait 30 seconds and retry."

**Q: "What's the architectural difference between tool use (function calling) and RAG for giving agents domain knowledge? When do you combine them?"**

A: **Tool use** (function calling) — the agent invokes a structured function at runtime to get information. Best for dynamic, query-specific data: current stock price, latest database record, live API response. The function executes, returns fresh data, and the agent incorporates it. Latency: 50–500ms per call. Knowledge is always real-time. **RAG** — a retrieval step (before or within the agent) searches a pre-indexed vector store for relevant passages. Best for static or semi-static knowledge: product documentation, policy manuals, company knowledge bases. Retrieval latency: < 100ms. Knowledge freshness: as of last indexing. **Combination pattern**: use RAG for background knowledge (product specs, company policies) and tool use for live data lookups (customer account state, real-time inventory). Example: a customer support agent uses RAG to retrieve the refund policy for the customer's product category, then uses function calling to check the customer's specific order status and purchase date. The policy (static) comes from RAG; the personalized data (dynamic) comes from tool calls. Neither alone is sufficient; the combination grounds the response in both authoritative documentation and accurate live data.

**Q: "How does the Multi-Agent Debate pattern improve decision quality? When is it too expensive to use?"**

A: Multi-Agent Debate has each agent argue from a distinct perspective (Optimist, Skeptic, Pragmatist in this POC), then a Moderator synthesizes. Quality improvement comes from three mechanisms: (1) **Devil's advocate effect** — the Skeptic is required to find problems; this surfaces risks that a single-agent analysis might rationalize away. (2) **Perspective diversity** — different agents have different priors, activating different parts of the LLM's knowledge. A question asked three ways with three answer personas explores more of the solution space than a single query. (3) **Synthesis quality** — the Moderator sees all three positions and must produce a recommendation that accounts for all of them, resulting in more nuanced output than a single-shot answer. When it's too expensive: (1) **Latency budget is tight** — debate requires 3+ LLM calls plus a synthesis call. If the total is 10 seconds vs. a direct 2-second answer, users notice. (2) **The question has a clear right answer** — factual lookups, math computations, data extraction. Debate adds noise, not signal. (3) **Low-stakes decisions** — for trivial routing choices (which FAQ tab to show first), debate is absurd overhead. Use debate for strategic, high-stakes, or genuinely ambiguous decisions.

---

### System Design Questions

**Q: "Design an agent-based ETL pipeline that can autonomously recover from upstream schema changes without human intervention."**

A: Three-agent LangGraph system: (1) **Schema Monitor Agent** — runs on a daily schedule (Airflow trigger). Uses function calling to fetch the current source schema from the upstream API or database. Compares against the last committed schema stored in a schema registry (S3/Git). Returns a diff: `{"new_columns": ["phone_verified"], "dropped_columns": [], "type_changes": [{"col": "age", "from": "int", "to": "float"}]}`. (2) **Impact Analyzer Agent** — receives the schema diff, uses RAG over the indexed pipeline codebase (dbt models, Airflow DAGs, FastAPI schemas) to find all downstream references to changed columns. Classifies changes as safe (additive, type widening) or breaking (dropped columns, type narrowing). For the impact list: `{"safe_changes": ["new column — add to Bronze model"], "breaking_changes": ["age type change breaks silver_customers.sql:45"]}`. (3) **Remediation Agent** — for safe, additive changes: generates a code patch (new column added to Bronze model `SELECT *` clause or schema.yml), commits it via GitHub API as a PR with AI-generated description, and triggers CI/CD. For breaking changes: creates a JIRA ticket with full impact analysis and blocks the pipeline with an appropriate error message. Humans review only the breaking change tickets — safe changes are fully automated.

**Q: "You're advising a fintech startup on which agent pattern to use for a financial report generation system. The reports must be auditable by regulators. Which pattern and why?"**

A: **Plan-and-Execute with Reflection and Human-in-the-Loop gate** — not ReAct, not Multi-Agent Debate. Regulatory auditability requirements drive this choice: (1) **Plan-and-Execute creates an explicit audit trail** — before any data is retrieved or calculations made, the system generates a documented step-by-step plan: "Step 1: retrieve Q3 revenue data for segments A, B, C. Step 2: apply GAAP adjustments. Step 3: compute YoY growth rates." Regulators can see exactly what was intended before execution. (2) **Reflection adds quality control** — a separate Reflection agent validates the draft report against internal accounting rules and known compliance requirements. Issues are logged with line-level citations: "Row 14 uses non-GAAP metric without disclosure footnote as required by SEC Rule 100." (3) **Human-in-the-loop gate is non-negotiable** — the Plan-and-Execute architecture naturally incorporates a `finance_controller_review` step in the plan before the report is published. The agent surfaces its work; a human approves. This step is explicitly logged with reviewer ID and timestamp. (4) **Full state logging** — every intermediate state (what data was fetched, what calculation was applied) is logged to an immutable audit database (append-only). Regulators can reconstruct the full decision trail from raw data to final report.
