# LangGraph Interview Questions and Answers

## Table of Contents
1. [Beginner Level Questions](#beginner-level-questions)
2. [Intermediate Level Questions](#intermediate-level-questions)
3. [Advanced Level Questions](#advanced-level-questions)

---

## Beginner Level Questions

### Q1: What is LangGraph and why was it created?

**Answer:**

LangGraph is a **low-level orchestration framework** for building stateful, multi-actor applications with LLMs. Built by the LangChain team, it models agent logic as a **directed graph** where:

- **Nodes** = Python functions (the "workers")
- **Edges** = transitions between functions
- **State** = shared typed data that flows through the graph

**Why it was created:**

LangChain's original `AgentExecutor` was a black box — you couldn't control the execution flow, add human approval steps, recover from crashes, or coordinate multiple agents. LangGraph was created to solve all of these:

| LangChain AgentExecutor | LangGraph |
|------------------------|-----------|
| Opaque loop | Explicit graph |
| No persistence | Built-in checkpointing |
| No human-in-the-loop | `interrupt()` at any node |
| Single agent only | Multi-agent patterns |
| No crash recovery | Resume from checkpoint |

**Example — Minimal graph:**
```python
from langgraph.graph import StateGraph, START, END
from typing import TypedDict

class State(TypedDict):
    message: str

def greet(state: State) -> dict:
    return {"message": f"Hello, {state['message']}!"}

graph = StateGraph(State)
graph.add_node("greet", greet)
graph.add_edge(START, "greet")
graph.add_edge("greet", END)

app = graph.compile()
result = app.invoke({"message": "World"})
# {"message": "Hello, World!"}
```

---

### Q2: What is the difference between StateGraph and MessagesState?

**Answer:**

**`StateGraph`** is the core graph builder that takes any `TypedDict` as its state schema. You define all state fields yourself.

**`MessagesState`** is a convenience class that pre-defines a `messages` field with append semantics — perfect for chat applications.

```python
# Using StateGraph with custom state
from langgraph.graph import StateGraph
from typing import TypedDict, Annotated
from operator import add

class CustomState(TypedDict):
    messages: Annotated[list, add]  # You must define reducer manually
    counter: int
    context: str

graph = StateGraph(CustomState)
```

```python
# Using MessagesState (shortcut for chat apps)
from langgraph.graph import StateGraph, MessagesState

# MessagesState already has: messages: Annotated[list, add_messages]
class MyState(MessagesState):
    # Just add your extra fields
    current_tool: str
    iteration: int

graph = StateGraph(MyState)
```

**Key differences:**

| Aspect | StateGraph (Custom) | MessagesState |
|--------|:------------------:|:-------------:|
| `messages` field | Manual definition | Pre-defined |
| Message dedup | Manual | Automatic (by ID) |
| Reducer | Must specify | Built-in `add_messages` |
| Custom fields | ✅ Yes | ✅ Yes (extend class) |
| Use case | Non-chat workflows | Chat/agent apps |

**When to use which:**
- **MessagesState** → Any chat or agent application (90% of use cases)
- **Custom StateGraph** → Data pipelines, non-chat workflows, specialized state

---

### Q3: Explain nodes and edges in LangGraph. How do they work together?

**Answer:**

**Nodes** are Python functions that:
1. Receive the current state as input
2. Perform some computation (call LLM, run tool, process data)
3. Return a **partial state update** (dict with only changed fields)

**Edges** are transitions that define execution order:
- **Static edges**: Always go from A → B
- **Conditional edges**: Check state and decide next node
- **Entry edge**: `START → first_node`
- **Terminal edge**: `last_node → END`

```python
from langgraph.graph import StateGraph, START, END, MessagesState
from langchain_openai import ChatOpenAI

llm = ChatOpenAI(model="gpt-4o")

# NODE 1: Call LLM
def chatbot(state: MessagesState) -> dict:
    response = llm.invoke(state["messages"])
    return {"messages": [response]}  # Partial update — only messages

# NODE 2: Execute tools
def tool_node(state: MessagesState) -> dict:
    # Execute tool calls from last message
    results = run_tools(state["messages"][-1].tool_calls)
    return {"messages": results}

# Build graph with EDGES
graph = StateGraph(MessagesState)
graph.add_node("chatbot", chatbot)         # Register node
graph.add_node("tools", tool_node)         # Register node

graph.add_edge(START, "chatbot")           # Entry edge
graph.add_edge("tools", "chatbot")         # Static edge: tools always → chatbot

# Conditional edge: chatbot → tools OR END
def route(state):
    if state["messages"][-1].tool_calls:
        return "tools"
    return END

graph.add_conditional_edges("chatbot", route)

app = graph.compile()
```

**Visual flow:**
```
START → chatbot → [has tool calls?] → YES → tools → chatbot → ...
                                    → NO  → END
```

---

### Q4: Why use LangGraph instead of LangChain's AgentExecutor?

**Answer:**

LangChain's `AgentExecutor` was the original way to build agents. It works but has fundamental limitations that LangGraph solves:

**1. Control Flow Visibility**
```python
# AgentExecutor: Black box loop — can't see or control what happens
agent = AgentExecutor(agent=agent_runnable, tools=tools)
result = agent.invoke({"input": "..."})  # What happened inside? 🤷

# LangGraph: Every step is visible and controllable
graph = StateGraph(MessagesState)
graph.add_node("agent", agent_node)
graph.add_node("tools", tool_node)
graph.add_conditional_edges("agent", route_function)
# You SEE the graph. You CONTROL the flow.
```

**2. Human-in-the-Loop**
```python
# AgentExecutor: No way to pause mid-execution
# LangGraph: Interrupt at any node
app = graph.compile(interrupt_before=["dangerous_tool"])
```

**3. Persistence & Recovery**
```python
# AgentExecutor: Crash = lose everything
# LangGraph: Resume from last checkpoint
app = graph.compile(checkpointer=PostgresSaver(...))
```

**4. Multi-Agent**
```python
# AgentExecutor: Single agent only
# LangGraph: Supervisor → Worker1, Worker2, Worker3
```

**5. Streaming**
```python
# AgentExecutor: Final output only
# LangGraph: Stream tokens, stream node outputs, stream custom events
async for event in app.astream_events(...):
    print(event)
```

**Bottom line:** `AgentExecutor` is deprecated in favor of LangGraph for all new projects. LangGraph gives you the same capabilities plus control, persistence, and multi-agent support.

---

### Q5: Walk through the steps to get started building a LangGraph agent.

**Answer:**

**Step 1: Install packages**
```bash
pip install langgraph langchain-openai langgraph-checkpoint-sqlite
```

**Step 2: Define state**
```python
from langgraph.graph import StateGraph, MessagesState, START, END

# MessagesState has: messages: Annotated[list, add_messages]
```

**Step 3: Define tools**
```python
from langchain_core.tools import tool

@tool
def search(query: str) -> str:
    """Search the web."""
    return f"Results for: {query}"
```

**Step 4: Create LLM with tools**
```python
from langchain_openai import ChatOpenAI

tools = [search]
llm = ChatOpenAI(model="gpt-4o").bind_tools(tools)
```

**Step 5: Define nodes**
```python
from langgraph.prebuilt import ToolNode, tools_condition

def agent(state: MessagesState) -> dict:
    return {"messages": [llm.invoke(state["messages"])]}
```

**Step 6: Build graph**
```python
graph = StateGraph(MessagesState)
graph.add_node("agent", agent)
graph.add_node("tools", ToolNode(tools))

graph.add_edge(START, "agent")
graph.add_conditional_edges("agent", tools_condition)
graph.add_edge("tools", "agent")
```

**Step 7: Compile with checkpointer**
```python
from langgraph.checkpoint.memory import MemorySaver

app = graph.compile(checkpointer=MemorySaver())
```

**Step 8: Invoke**
```python
config = {"configurable": {"thread_id": "demo-1"}}
result = app.invoke(
    {"messages": [("user", "Search for LangGraph tutorials")]},
    config
)
print(result["messages"][-1].content)
```

**Total: ~30 lines of code for a persistent, tool-calling agent with streaming support.**

---

## Intermediate Level Questions

### Q6: How do conditional edges work? Explain with a real routing example.

**Answer:**

Conditional edges let you **dynamically choose the next node** based on the current state. You provide a routing function that returns the name of the next node.

**Syntax:**
```python
graph.add_conditional_edges(
    source_node,     # Node after which the decision is made
    routing_function, # Function(state) → str (next node name)
    path_map          # Optional: {return_value: node_name}
)
```

**Real Example — Customer Support Router:**

```python
from langgraph.graph import StateGraph, START, END
from typing import TypedDict

class SupportState(TypedDict):
    query: str
    language: str
    category: str
    urgency: str
    response: str

def detect_language(state: SupportState) -> dict:
    """Detect query language."""
    query = state["query"]
    # Simple detection (use LLM in production)
    if any(c > '\u0900' and c < '\u097F' for c in query):
        return {"language": "hindi"}
    return {"language": "english"}

def classify_query(state: SupportState) -> dict:
    """Classify the support query."""
    query = state["query"].lower()
    if any(w in query for w in ["refund", "charge", "bill", "payment"]):
        return {"category": "billing", "urgency": "high"}
    elif any(w in query for w in ["bug", "crash", "error", "broken"]):
        return {"category": "technical", "urgency": "critical"}
    elif any(w in query for w in ["how to", "help", "guide"]):
        return {"category": "how-to", "urgency": "low"}
    return {"category": "general", "urgency": "medium"}

def handle_billing(state: SupportState) -> dict:
    return {"response": f"[Billing Team] Processing: {state['query']}"}

def handle_technical(state: SupportState) -> dict:
    return {"response": f"[Engineering - CRITICAL] Bug report: {state['query']}"}

def handle_howto(state: SupportState) -> dict:
    return {"response": f"[Knowledge Base] Here's how: {state['query']}"}

def handle_general(state: SupportState) -> dict:
    return {"response": f"[General Support] We'll help with: {state['query']}"}

# ROUTING FUNCTION — this is the key!
def route_by_category(state: SupportState) -> str:
    """Route to appropriate handler based on classification."""
    category = state["category"]
    routing_map = {
        "billing": "billing_handler",
        "technical": "tech_handler",
        "how-to": "howto_handler",
        "general": "general_handler"
    }
    return routing_map.get(category, "general_handler")

# Build graph
graph = StateGraph(SupportState)
graph.add_node("detect_lang", detect_language)
graph.add_node("classify", classify_query)
graph.add_node("billing_handler", handle_billing)
graph.add_node("tech_handler", handle_technical)
graph.add_node("howto_handler", handle_howto)
graph.add_node("general_handler", handle_general)

graph.add_edge(START, "detect_lang")
graph.add_edge("detect_lang", "classify")

# CONDITIONAL EDGE — the decision point
graph.add_conditional_edges(
    "classify",
    route_by_category,
    {
        "billing_handler": "billing_handler",
        "tech_handler": "tech_handler",
        "howto_handler": "howto_handler",
        "general_handler": "general_handler"
    }
)

# All handlers end the graph
for handler in ["billing_handler", "tech_handler", "howto_handler", "general_handler"]:
    graph.add_edge(handler, END)

app = graph.compile()

# Test
result = app.invoke({"query": "The app crashes when I open settings"})
print(result["response"])
# "[Engineering - CRITICAL] Bug report: The app crashes when I open settings"
```

---

### Q7: How does checkpointing and persistence work in LangGraph?

**Answer:**

Checkpointing saves the graph state after **every node execution**. This enables:
1. **Crash recovery** — Resume from last successful node
2. **Conversation memory** — Persist across sessions
3. **Time travel** — Replay from any checkpoint
4. **Forking** — Branch execution from any point

**How it works internally:**

```
Node A executes → State saved (checkpoint 1)
    ↓
Node B executes → State saved (checkpoint 2)
    ↓
[CRASH]
    ↓
Resume from checkpoint 2 → Continue from Node C
```

**Backend options:**

```python
# 1. In-memory (development/testing)
from langgraph.checkpoint.memory import MemorySaver
checkpointer = MemorySaver()

# 2. SQLite (local development)
from langgraph.checkpoint.sqlite import SqliteSaver
checkpointer = SqliteSaver.from_conn_string("checkpoints.db")

# 3. PostgreSQL (production)
from langgraph.checkpoint.postgres import PostgresSaver
checkpointer = PostgresSaver.from_conn_string(
    "postgresql://user:pass@host:5432/langgraph"
)
```

**Using checkpoints:**

```python
app = graph.compile(checkpointer=checkpointer)

# Thread ID groups related interactions
config = {"configurable": {"thread_id": "user-alice-session-1"}}

# Invoke — each call checkpoints automatically
result1 = app.invoke({"messages": [("user", "Hi")]}, config)
result2 = app.invoke({"messages": [("user", "Remind me what I said")]}, config)
# result2 has full history from result1!

# Get state at any checkpoint
state = app.get_state(config)
print(state.values)  # Current state
print(state.next)    # Next node to execute

# Time travel — get all checkpoints
for checkpoint in app.get_state_history(config):
    print(checkpoint.config, checkpoint.values)

# Fork — update state and resume from a specific point
app.update_state(config, {"messages": [("user", "Override message")]})
result = app.invoke(None, config)  # Continue from updated state
```

**Production pattern:**

```python
# PostgreSQL with connection pooling
import asyncpg

async def create_checkpointer():
    pool = await asyncpg.create_pool(
        "postgresql://user:pass@host:5432/langgraph",
        min_size=5, max_size=20
    )
    return PostgresSaver(pool)
```

---

### Q8: How do you implement human-in-the-loop interrupts in LangGraph?

**Answer:**

LangGraph provides two mechanisms for human-in-the-loop:

**Method 1: `interrupt_before` / `interrupt_after` (compile-time)**

```python
# Pause BEFORE a specific node
app = graph.compile(
    checkpointer=memory,
    interrupt_before=["execute_trade"]  # Pause before this node
)

config = {"configurable": {"thread_id": "trade-1"}}

# Step 1: Run until interrupt
result = app.invoke({"messages": [("user", "Buy 100 AAPL")]}, config)
# Execution pauses BEFORE execute_trade node

# Step 2: Inspect the state
state = app.get_state(config)
print(f"Next node: {state.next}")  # ('execute_trade',)
print(f"Pending action: {state.values}")

# Step 3: Resume (human approves)
result = app.invoke(None, config)  # Continue execution

# Or: Modify state before resuming (human edits)
app.update_state(config, {"quantity": 50})  # Human reduces to 50
result = app.invoke(None, config)
```

**Method 2: `interrupt()` function (runtime, inside nodes)**

```python
from langgraph.types import interrupt, Command

def execute_trade(state):
    """Pause and ask human for approval."""
    trade = state["proposed_trade"]

    # This PAUSES execution and sends data to the caller
    approval = interrupt({
        "action": "approve_trade",
        "details": f"Buy {trade['quantity']} shares of {trade['symbol']} at ${trade['price']}",
        "options": ["approve", "reject", "modify"]
    })

    if approval == "approve":
        return {"status": "executed", "messages": ["Trade executed"]}
    elif approval == "reject":
        return {"status": "cancelled", "messages": ["Trade cancelled"]}
    else:
        return {"status": "modified", "messages": ["Please resubmit"]}

# Resume with human decision
result = app.invoke(Command(resume="approve"), config)
```

**Pattern: Multi-step approval chain**

```python
def node_with_multiple_approvals(state):
    # First approval
    risk_ok = interrupt({"question": "Risk check passed. Proceed?"})
    if risk_ok != "yes":
        return {"status": "rejected_at_risk"}

    # Second approval
    compliance_ok = interrupt({"question": "Compliance approved. Execute?"})
    if compliance_ok != "yes":
        return {"status": "rejected_at_compliance"}

    return {"status": "fully_approved"}
```

---

### Q9: How does streaming work in LangGraph? What are the different modes?

**Answer:**

LangGraph supports **3 streaming modes** for different use cases:

**Mode 1: `values` — Full state after each node**

```python
for chunk in app.stream(
    {"messages": [("user", "Hello")]},
    config,
    stream_mode="values"
):
    # chunk = entire state after each node completes
    print(chunk["messages"][-1])
```

**Mode 2: `updates` — Only the state changes per node**

```python
for chunk in app.stream(
    {"messages": [("user", "Hello")]},
    config,
    stream_mode="updates"
):
    # chunk = {node_name: {partial_state_update}}
    for node_name, update in chunk.items():
        print(f"Node '{node_name}' updated: {update}")
```

**Mode 3: `astream_events` — Token-level streaming (most granular)**

```python
async for event in app.astream_events(
    {"messages": [("user", "Write a poem")]},
    config=config,
    version="v2"
):
    kind = event["event"]

    if kind == "on_chat_model_start":
        print("LLM started generating...")

    elif kind == "on_chat_model_stream":
        # Individual tokens
        token = event["data"]["chunk"].content
        if token:
            print(token, end="", flush=True)

    elif kind == "on_chat_model_end":
        print("\nLLM finished.")

    elif kind == "on_tool_start":
        print(f"Tool called: {event['name']}")

    elif kind == "on_tool_end":
        print(f"Tool result: {event['data']['output']}")
```

**Custom event streaming:**

```python
from langchain_core.callbacks import adispatch_custom_event

async def research_node(state):
    # Emit custom events during execution
    await adispatch_custom_event("research_started", {"topic": state["topic"]})

    for i, source in enumerate(sources):
        result = analyze(source)
        await adispatch_custom_event("source_analyzed", {
            "source": source, "progress": f"{i+1}/{len(sources)}"
        })

    await adispatch_custom_event("research_complete", {"findings": results})
    return {"research": results}
```

---

### Q10: How do multiple agents communicate in LangGraph?

**Answer:**

LangGraph supports several multi-agent communication patterns:

**Pattern 1: Shared State (most common)**

All agents read from and write to the same state object.

```python
class TeamState(MessagesState):
    research_findings: str
    draft: str
    feedback: str

def researcher(state: TeamState) -> dict:
    findings = llm.invoke(f"Research: {state['messages'][-1].content}")
    return {"research_findings": findings.content}

def writer(state: TeamState) -> dict:
    draft = llm.invoke(f"Write based on: {state['research_findings']}")
    return {"draft": draft.content}

def reviewer(state: TeamState) -> dict:
    feedback = llm.invoke(f"Review: {state['draft']}")
    return {"feedback": feedback.content}

# Sequential communication via shared state
graph.add_edge("researcher", "writer")
graph.add_edge("writer", "reviewer")
```

**Pattern 2: Supervisor Routing**

A supervisor agent decides who speaks next.

```python
def supervisor(state: TeamState) -> dict:
    decision = llm.invoke(
        "Who should act next: researcher, writer, reviewer, or FINISH?"
    )
    return {"next_agent": parse_decision(decision)}

graph.add_conditional_edges(
    "supervisor",
    lambda state: state["next_agent"],
    {"researcher": "researcher", "writer": "writer",
     "reviewer": "reviewer", "FINISH": END}
)
# Workers always return to supervisor
graph.add_edge("researcher", "supervisor")
graph.add_edge("writer", "supervisor")
graph.add_edge("reviewer", "supervisor")
```

**Pattern 3: Handoff (Agent-to-Agent)**

Agents directly hand off to specific other agents.

```python
from langgraph.types import Command

def researcher(state: TeamState) -> Command:
    findings = do_research(state)
    # Directly hand off to writer
    return Command(
        update={"research_findings": findings},
        goto="writer"  # Skip supervisor, go directly
    )
```

**Pattern 4: Subgraphs (Nested Teams)**

Each team is a subgraph that can be composed into a larger graph.

```python
# Team 1: Research team (subgraph)
research_graph = build_research_subgraph()

# Team 2: Writing team (subgraph)
writing_graph = build_writing_subgraph()

# Parent graph coordinates teams
parent = StateGraph(ParentState)
parent.add_node("research_team", research_graph)
parent.add_node("writing_team", writing_graph)
parent.add_edge("research_team", "writing_team")
```

---

## Advanced Level Questions

### Q11: Design a multi-agent supervisor system with hierarchical delegation. How do you handle state across subgraphs?

**Answer:**

**Architecture: Hierarchical Multi-Agent System**

```
Top Supervisor
├── Research Team (subgraph)
│   ├── Web Researcher
│   ├── Document Analyst
│   └── Research Supervisor
├── Writing Team (subgraph)
│   ├── Drafter
│   ├── Editor
│   └── Writing Supervisor
└── QA Team (subgraph)
    ├── Fact Checker
    ├── Grammar Checker
    └── QA Supervisor
```

**Implementation:**

```python
from langgraph.graph import StateGraph, MessagesState, START, END
from typing import TypedDict, Annotated
from operator import add

# ============ SHARED STATE ============
class ProjectState(MessagesState):
    objective: str
    research: str
    draft: str
    final: str
    team_status: dict

# ============ RESEARCH SUBGRAPH ============
class ResearchState(MessagesState):
    topic: str
    web_results: Annotated[list[str], add]
    doc_analysis: str
    synthesis: str

def web_researcher(state: ResearchState) -> dict:
    results = search_web(state["topic"])
    return {"web_results": [results]}

def doc_analyst(state: ResearchState) -> dict:
    analysis = analyze_docs(state["topic"])
    return {"doc_analysis": analysis}

def research_supervisor(state: ResearchState) -> dict:
    synthesis = llm.invoke(
        f"Synthesize:\nWeb: {state['web_results']}\nDocs: {state['doc_analysis']}"
    )
    return {"synthesis": synthesis.content}

def build_research_subgraph():
    graph = StateGraph(ResearchState)
    graph.add_node("web_researcher", web_researcher)
    graph.add_node("doc_analyst", doc_analyst)
    graph.add_node("research_supervisor", research_supervisor)

    graph.add_edge(START, "web_researcher")
    graph.add_edge(START, "doc_analyst")  # Parallel!
    graph.add_edge("web_researcher", "research_supervisor")
    graph.add_edge("doc_analyst", "research_supervisor")
    graph.add_edge("research_supervisor", END)

    return graph.compile()

# ============ TOP-LEVEL GRAPH ============
def top_supervisor(state: ProjectState) -> dict:
    """Decides which team to activate next."""
    if not state.get("research"):
        return {"team_status": {"next": "research"}}
    elif not state.get("draft"):
        return {"team_status": {"next": "writing"}}
    elif not state.get("final"):
        return {"team_status": {"next": "qa"}}
    return {"team_status": {"next": "done"}}

def route_team(state: ProjectState) -> str:
    return state["team_status"]["next"]

# State mapping: parent ↔ subgraph
def call_research(state: ProjectState) -> dict:
    """Map parent state → subgraph → parent state."""
    research_graph = build_research_subgraph()
    result = research_graph.invoke({
        "messages": state["messages"],
        "topic": state["objective"]
    })
    return {"research": result["synthesis"]}

parent = StateGraph(ProjectState)
parent.add_node("supervisor", top_supervisor)
parent.add_node("research", call_research)
parent.add_node("writing", call_writing)  # Similar pattern
parent.add_node("qa", call_qa)            # Similar pattern

parent.add_edge(START, "supervisor")
parent.add_conditional_edges("supervisor", route_team, {
    "research": "research",
    "writing": "writing",
    "qa": "qa",
    "done": END
})
parent.add_edge("research", "supervisor")
parent.add_edge("writing", "supervisor")
parent.add_edge("qa", "supervisor")

app = parent.compile(checkpointer=PostgresSaver(...))
```

**State handling across subgraphs:**
- Parent graph maintains the **project-level** state
- Each subgraph has its **own internal state** (isolated)
- The parent node wrapping the subgraph handles **state mapping** (parent → child → parent)
- Checkpointing happens at **both levels** — parent and subgraph checkpoints are independent

---

### Q12: Explain the map-reduce pattern in LangGraph. How does `Send` work for parallel execution?

**Answer:**

The map-reduce pattern in LangGraph uses `Send` to **fan out** work to multiple nodes in parallel, then **collect** results.

**How `Send` works:**

Instead of returning a state update from a node, you return a `list[Send]`. Each `Send` object creates a **separate execution** of the target node with its own input.

```python
from langgraph.types import Send
from langgraph.graph import StateGraph, START, END
from typing import TypedDict, Annotated
from operator import add

# ============ STATE ============
class OverallState(TypedDict):
    topics: list[str]
    analyses: Annotated[list[str], add]  # Reducer: append
    final_report: str

class AnalysisState(TypedDict):
    topic: str

# ============ MAP FUNCTION ============
def fan_out(state: OverallState) -> list[Send]:
    """Fan out: create one Send per topic → parallel execution."""
    return [
        Send("analyze", {"topic": topic})
        for topic in state["topics"]
    ]

# ============ WORKER (runs in parallel) ============
def analyze(state: AnalysisState) -> dict:
    """Analyze a single topic. Multiple instances run concurrently."""
    result = llm.invoke(f"Analyze this topic thoroughly: {state['topic']}")
    return {"analyses": [f"## {state['topic']}\n{result.content}"]}

# ============ REDUCE ============
def synthesize(state: OverallState) -> dict:
    """Combine all parallel results into one report."""
    combined = "\n\n".join(state["analyses"])
    report = llm.invoke(f"Create a unified report from:\n{combined}")
    return {"final_report": report.content}

# ============ BUILD GRAPH ============
graph = StateGraph(OverallState)
graph.add_node("analyze", analyze)
graph.add_node("synthesize", synthesize)

# Fan-out from START → multiple "analyze" instances
graph.add_conditional_edges(START, fan_out)
# All "analyze" instances → synthesize
graph.add_edge("analyze", "synthesize")
graph.add_edge("synthesize", END)

app = graph.compile()

# Usage
result = app.invoke({
    "topics": ["AI in healthcare", "AI in finance", "AI in education"]
})
print(result["final_report"])
# All 3 topics analyzed in parallel, then combined
```

**Key points:**
1. `Send("node_name", state_dict)` creates a parallel instance
2. The target node receives `AnalysisState` (not `OverallState`)
3. Results merge into the parent state via the **reducer** (`Annotated[list, add]`)
4. The reduce node (`synthesize`) sees all results collected
5. If one `Send` fails, the checkpoint lets you retry just that one

**Advanced: Nested map-reduce**

```python
def fan_out_sections(state):
    return [Send("analyze_section", {"section": s}) for s in state["sections"]]

def analyze_section(state):
    # This can itself fan out further!
    subsections = split_into_parts(state["section"])
    return [Send("analyze_subsection", {"part": p}) for p in subsections]
```

---

### Q13: How do you deploy LangGraph agents to production using LangGraph Platform?

**Answer:**

**LangGraph Platform** is the managed deployment solution. It provides:
- API server for your graphs
- Built-in persistence (Postgres)
- Cron jobs and webhooks
- Horizontal scaling
- LangSmith integration

**Step 1: Project structure**

```
my-agent/
├── src/
│   └── agent/
│       ├── __init__.py
│       ├── graph.py        # Graph definition
│       ├── nodes.py        # Node functions
│       └── state.py        # State definitions
├── langgraph.json          # LangGraph config
├── pyproject.toml
└── .env
```

**Step 2: `langgraph.json` configuration**

```json
{
  "dependencies": ["."],
  "graphs": {
    "my_agent": "./src/agent/graph.py:graph"
  },
  "env": ".env",
  "python_version": "3.11",
  "pip_config_file": null,
  "dockerfile_lines": []
}
```

**Step 3: Define the graph (must be a `CompiledGraph`)**

```python
# src/agent/graph.py
from langgraph.graph import StateGraph, MessagesState, START, END
from langgraph.prebuilt import ToolNode, tools_condition
from langchain_openai import ChatOpenAI

llm = ChatOpenAI(model="gpt-4o")

def assistant(state: MessagesState):
    return {"messages": [llm.invoke(state["messages"])]}

builder = StateGraph(MessagesState)
builder.add_node("assistant", assistant)
builder.add_node("tools", ToolNode([...]))
builder.add_edge(START, "assistant")
builder.add_conditional_edges("assistant", tools_condition)
builder.add_edge("tools", "assistant")

# Export the compiled graph
graph = builder.compile()
```

**Step 4: Deploy**

```bash
# Option A: LangGraph Cloud (hosted)
langgraph deploy --config langgraph.json

# Option B: Self-hosted with Docker
langgraph build --config langgraph.json -t my-agent:latest
docker run -p 8000:8000 \
  -e OPENAI_API_KEY=sk-... \
  -e LANGSMITH_API_KEY=lsv2-... \
  -e POSTGRES_URI=postgresql://... \
  my-agent:latest
```

**Step 5: Use the API**

```python
from langgraph_sdk import get_client

client = get_client(url="http://localhost:8000")

# Create a thread
thread = await client.threads.create()

# Run the agent
run = await client.runs.create(
    thread["thread_id"],
    "my_agent",
    input={"messages": [{"role": "user", "content": "Hello!"}]}
)

# Stream responses
async for event in client.runs.stream(
    thread["thread_id"],
    "my_agent",
    input={"messages": [{"role": "user", "content": "Hello!"}]},
    stream_mode="events"
):
    print(event)
```

**Step 6: Cron jobs and webhooks**

```python
# Create a scheduled run (cron)
cron = await client.crons.create(
    "my_agent",
    schedule="0 9 * * *",  # Every day at 9 AM
    input={"messages": [{"role": "user", "content": "Daily report"}]}
)
```

---

### Q14: How do you implement custom state management with reducers for complex data types?

**Answer:**

Reducers define **how node outputs merge into existing state**. Without a reducer, the value is **replaced**. With a reducer, values are **combined**.

**Built-in reducers:**

```python
from typing import Annotated
from operator import add
from langgraph.graph.message import add_messages

class State(TypedDict):
    # REPLACE (default — no reducer): last write wins
    current_step: str

    # APPEND (add reducer): concatenate lists
    logs: Annotated[list[str], add]

    # SMART MERGE (add_messages): dedup by message ID
    messages: Annotated[list, add_messages]
```

**Custom reducers:**

```python
from typing import Annotated

# Reducer 1: Keep maximum value
def keep_max(existing: float, new: float) -> float:
    return max(existing, new)

# Reducer 2: Merge dictionaries (deep merge)
def deep_merge(existing: dict, new: dict) -> dict:
    result = {**existing}
    for key, value in new.items():
        if key in result and isinstance(result[key], dict) and isinstance(value, dict):
            result[key] = deep_merge(result[key], value)
        else:
            result[key] = value
    return result

# Reducer 3: Deduplicated set-like list
def unique_append(existing: list, new: list) -> list:
    seen = set(existing)
    return existing + [item for item in new if item not in seen]

# Reducer 4: Capped history (keep last N)
def last_n(n: int):
    def reducer(existing: list, new: list) -> list:
        combined = existing + new
        return combined[-n:]
    return reducer

class ComplexState(TypedDict):
    messages: Annotated[list, add_messages]
    max_confidence: Annotated[float, keep_max]
    metadata: Annotated[dict, deep_merge]
    seen_tools: Annotated[list[str], unique_append]
    recent_errors: Annotated[list[str], last_n(10)]
```

**Pydantic state (for validation):**

```python
from pydantic import BaseModel, Field
from langgraph.graph import StateGraph

class ValidatedState(BaseModel):
    messages: Annotated[list, add_messages] = Field(default_factory=list)
    temperature: float = Field(ge=0.0, le=2.0, default=0.7)
    max_tokens: int = Field(ge=1, le=4096, default=1024)
    allowed_tools: list[str] = Field(default_factory=list)

    class Config:
        validate_assignment = True  # Validate on every update

graph = StateGraph(ValidatedState)
# Now any node that returns {"temperature": 5.0} will raise ValidationError
```

**State channels (fine-grained control):**

```python
from langgraph.graph import StateGraph
from langgraph.channels import LastValue, BinaryOperatorAggregate

# Low-level channel API
graph = StateGraph({
    "messages": BinaryOperatorAggregate(list, add_messages),
    "step_count": BinaryOperatorAggregate(int, lambda a, b: a + b),
    "status": LastValue(str),  # Replace semantics
})
```

---

### Q15: Design a self-improving agent that uses reflection and memory across sessions. How do you implement long-term memory with the Store API?

**Answer:**

**Architecture: Self-Improving Agent with Long-Term Memory**

The agent:
1. Executes tasks using tools
2. Reflects on its performance after each task
3. Stores lessons learned in long-term memory (Store API)
4. Retrieves relevant past lessons for new tasks
5. Improves over time

```python
from langgraph.graph import StateGraph, MessagesState, START, END
from langgraph.checkpoint.postgres import PostgresSaver
from langgraph.store.memory import InMemoryStore
from langchain_openai import ChatOpenAI
from datetime import datetime
import json

# ============ STATE ============
class AgentState(MessagesState):
    task: str
    result: str
    reflection: str
    past_lessons: list[str]
    confidence: float

# ============ STORES ============
memory_store = InMemoryStore()  # Use PostgresStore in production
checkpointer = PostgresSaver.from_conn_string("postgresql://...")

llm = ChatOpenAI(model="gpt-4o")

# ============ NODES ============
def retrieve_lessons(state: AgentState, config, *, store) -> dict:
    """Retrieve relevant past lessons from long-term memory."""
    user_id = config["configurable"]["user_id"]
    namespace = ("lessons", user_id)

    # Search for relevant past lessons
    all_lessons = store.search(namespace)
    relevant = [
        item.value["lesson"]
        for item in all_lessons
        if any(keyword in state["task"].lower()
               for keyword in item.value.get("keywords", []))
    ]

    return {"past_lessons": relevant[-5:]}  # Last 5 relevant lessons

def execute_task(state: AgentState) -> dict:
    """Execute the task with context from past lessons."""
    lessons_context = ""
    if state.get("past_lessons"):
        lessons_context = (
            "\n\nLessons from past experience:\n"
            + "\n".join(f"- {l}" for l in state["past_lessons"])
        )

    response = llm.invoke(
        f"Task: {state['task']}{lessons_context}\n\n"
        f"Execute this task thoroughly."
    )
    return {"result": response.content}

def reflect(state: AgentState) -> dict:
    """Reflect on performance and extract lessons."""
    response = llm.invoke(
        f"Task: {state['task']}\n"
        f"Result: {state['result']}\n"
        f"Past lessons applied: {state.get('past_lessons', [])}\n\n"
        f"Reflect on this execution:\n"
        f"1. What went well?\n"
        f"2. What could be improved?\n"
        f"3. What lesson should be remembered for future similar tasks?\n"
        f"4. Confidence score (0-1)?\n"
        f"Respond as JSON: {{\"reflection\": ..., \"lesson\": ..., "
        f"\"keywords\": [...], \"confidence\": 0.X}}"
    )

    try:
        parsed = json.loads(response.content)
    except json.JSONDecodeError:
        parsed = {
            "reflection": response.content,
            "lesson": "Parse reflection manually",
            "keywords": [],
            "confidence": 0.5
        }

    return {
        "reflection": parsed["reflection"],
        "confidence": parsed.get("confidence", 0.5)
    }

def store_lesson(state: AgentState, config, *, store) -> dict:
    """Store the lesson in long-term memory."""
    user_id = config["configurable"]["user_id"]
    namespace = ("lessons", user_id)

    # Parse lesson from reflection
    lesson_data = {
        "lesson": state["reflection"],
        "task": state["task"],
        "confidence": state["confidence"],
        "keywords": extract_keywords(state["task"]),
        "timestamp": datetime.now().isoformat()
    }

    # Store with unique key
    key = f"lesson-{datetime.now().strftime('%Y%m%d-%H%M%S')}"
    store.put(namespace, key, lesson_data)

    return {}

def should_retry(state: AgentState) -> str:
    """If confidence is low, retry the task."""
    if state.get("confidence", 0) < 0.6:
        return "execute"  # Re-do with reflection applied
    return END

# ============ BUILD GRAPH ============
graph = StateGraph(AgentState)
graph.add_node("retrieve_lessons", retrieve_lessons)
graph.add_node("execute", execute_task)
graph.add_node("reflect", reflect)
graph.add_node("store_lesson", store_lesson)

graph.add_edge(START, "retrieve_lessons")
graph.add_edge("retrieve_lessons", "execute")
graph.add_edge("execute", "reflect")
graph.add_edge("reflect", "store_lesson")
graph.add_conditional_edges("store_lesson", should_retry)

app = graph.compile(checkpointer=checkpointer, store=memory_store)

# ============ USAGE ============
config = {
    "configurable": {
        "thread_id": "task-001",
        "user_id": "alice"
    }
}

# First task — no lessons yet
result = app.invoke({"task": "Write a Python function to parse CSV files"}, config)

# Second similar task — retrieves lessons from first task!
config["configurable"]["thread_id"] = "task-002"
result = app.invoke({"task": "Write a Python function to parse JSON files"}, config)
# Agent now uses lessons from CSV parsing experience
```

**Key concepts:**

| Concept | Implementation |
|---------|---------------|
| **Short-term memory** | Checkpointer (per-thread conversation) |
| **Long-term memory** | Store API (cross-thread, persistent) |
| **Reflection** | Separate node that evaluates and extracts lessons |
| **Self-improvement** | Low-confidence → retry loop; high-confidence → store & move on |
| **Retrieval** | Keyword-based search over stored lessons |

**Production considerations:**
- Use `PostgresStore` instead of `InMemoryStore` for persistence
- Add embedding-based similarity search for better lesson retrieval
- Implement lesson pruning (remove outdated or low-value lessons)
- Add confidence decay over time (old lessons become less relevant)
- Use separate threads for task execution but shared store namespace for lessons
