# What is LangGraph? - Complete Guide

## Table of Contents
1. [Definition & Problem Statement](#definition--problem-statement)
2. [Core Concepts & Principles](#core-concepts--principles)
3. [Key Features & Capabilities](#key-features--capabilities)
4. [Installation & Setup](#installation--setup)
5. [Beginner Examples](#beginner-examples)
6. [Intermediate Patterns](#intermediate-patterns)
7. [Advanced Architectures](#advanced-architectures)
8. [Best Practices & Optimization](#best-practices--optimization)
9. [Common Pitfalls & Solutions](#common-pitfalls--solutions)
10. [Comparison with Similar Tools](#comparison-with-similar-tools)
11. [Real-World Use Cases](#real-world-use-cases)
12. [Performance Considerations](#performance-considerations)

---

## Definition & Problem Statement

### What is LangGraph?

**LangGraph** is a low-level orchestration framework for building stateful, multi-actor applications with LLMs. Built by the LangChain team, it models your agent logic as a **graph** — with nodes (functions), edges (transitions), and state (shared data) — giving you full control over the execution flow.

Unlike high-level agent frameworks that hide the control flow behind abstractions, LangGraph exposes the graph explicitly. You define exactly which functions run, in what order, under what conditions, and how state flows between them.

### Problem It Solves

Standard LLM agent frameworks have critical limitations:

- **No durability**: If the process crashes mid-execution, you lose everything — no checkpointing, no recovery
- **Opaque control flow**: "Magic" routing hides what the agent is actually doing — impossible to debug or audit
- **No human-in-the-loop**: Can't pause execution, get human approval, then resume from the same state
- **Single-agent only**: No principled way to coordinate multiple agents with shared state
- **No streaming**: Can't stream intermediate results or tokens during multi-step execution
- **No persistence**: Conversation history lives in memory — restart = gone

**LangGraph fixes ALL of these:**

| Problem | Without LangGraph | With LangGraph |
|---------|-------------------|----------------|
| **Crash recovery** | Start over | Resume from last checkpoint |
| **Control flow** | Hidden behind `AgentExecutor` | Explicit graph you define |
| **Human approval** | Not possible mid-run | `interrupt()` at any node |
| **Multi-agent** | Hack multiple chains together | First-class `StateGraph` coordination |
| **Streaming** | Final output only | Token-level + node-level streaming |
| **Persistence** | In-memory only | SQLite, Postgres, Redis backends |

### Key Insight

LangGraph is to LangChain agents what **React** is to jQuery — it gives you a declarative, composable way to build complex interactive systems instead of imperative spaghetti code.

---

## Core Concepts & Principles

### 1. **StateGraph** — The Foundation

Everything in LangGraph starts with a `StateGraph`. It's a directed graph where:
- **State** = shared data structure (TypedDict or Pydantic model)
- **Nodes** = Python functions that read/modify state
- **Edges** = transitions between nodes

```python
from langgraph.graph import StateGraph, START, END
from typing import TypedDict, Annotated
from operator import add

# 1. Define the state
class AgentState(TypedDict):
    messages: Annotated[list, add]  # Append-only list
    next_step: str

# 2. Create the graph
graph = StateGraph(AgentState)
```

### 2. **Nodes** — The Workers

Nodes are regular Python functions (sync or async) that take state as input and return partial state updates.

```python
def chatbot(state: AgentState) -> dict:
    """Node: Call LLM and return response."""
    response = llm.invoke(state["messages"])
    return {"messages": [response]}

def tool_executor(state: AgentState) -> dict:
    """Node: Execute tool calls from the LLM."""
    last_message = state["messages"][-1]
    results = execute_tools(last_message.tool_calls)
    return {"messages": results}

# Add nodes to graph
graph.add_node("chatbot", chatbot)
graph.add_node("tools", tool_executor)
```

### 3. **Edges** — The Transitions

Edges define how execution flows between nodes.

```python
# Static edge: always go from tools → chatbot
graph.add_edge("tools", "chatbot")

# Entry edge: start at chatbot
graph.add_edge(START, "chatbot")
```

### 4. **Conditional Edges** — The Decision Points

The most powerful concept. A function inspects the state and decides the next node.

```python
def should_continue(state: AgentState) -> str:
    """Route based on whether the LLM wants to call tools."""
    last_message = state["messages"][-1]
    if last_message.tool_calls:
        return "tools"       # Go to tool node
    return END               # Done — return to user

# Conditional edge from chatbot
graph.add_conditional_edges(
    "chatbot",                         # Source node
    should_continue,                   # Router function
    {"tools": "tools", END: END}       # Mapping: return_value → node_name
)
```

### 5. **MessagesState** — Convenience Shortcut

For chat applications, LangGraph provides `MessagesState` which pre-defines a `messages` list with append semantics.

```python
from langgraph.graph import MessagesState

class State(MessagesState):
    """Extends MessagesState with custom fields."""
    current_tool: str
    iteration_count: int
```

### 6. **Checkpointing** — Durable Execution

Every state transition is saved. If the process crashes, resume from the last checkpoint.

```python
from langgraph.checkpoint.sqlite import SqliteSaver
from langgraph.checkpoint.postgres import PostgresSaver

# SQLite for development
memory = SqliteSaver.from_conn_string(":memory:")

# Postgres for production
memory = PostgresSaver.from_conn_string("postgresql://...")

# Compile graph with checkpointer
app = graph.compile(checkpointer=memory)

# Every invocation uses a thread_id
config = {"configurable": {"thread_id": "user-123"}}
result = app.invoke({"messages": [("user", "Hello")]}, config)
```

### 7. **Human-in-the-Loop** — Interrupts

Pause execution at any node, get human input, then resume.

```python
from langgraph.types import interrupt, Command

def sensitive_action(state):
    """Pause for human approval before executing."""
    approval = interrupt(
        {"question": f"Approve action: {state['action']}?"}
    )
    if approval == "yes":
        return execute_action(state)
    return {"messages": ["Action cancelled by human."]}

# Compile with interrupt_before
app = graph.compile(
    checkpointer=memory,
    interrupt_before=["sensitive_action"]  # Pause before this node
)
```

---

## Key Features & Capabilities

### Feature Overview

| Feature | Description |
|---------|-------------|
| **StateGraph** | Explicit graph-based control flow with typed state |
| **Persistence** | Built-in checkpointing (SQLite, Postgres, Redis) |
| **Streaming** | Token-level, node-level, and custom event streaming |
| **Human-in-the-Loop** | `interrupt()` / `interrupt_before` / `interrupt_after` |
| **Memory** | Short-term (thread) + long-term (cross-thread) memory |
| **Subgraphs** | Nested graphs for modular composition |
| **Multi-Agent** | Supervisor, swarm, and hierarchical patterns |
| **Time Travel** | Replay from any checkpoint, fork execution |
| **LangSmith** | Native tracing orientation and observability |
| **LangGraph Platform** | Managed deployment with APIs, cron, and webhooks |
| **Fault Tolerance** | Automatic retries with configurable retry policies |

### Streaming Modes

```python
# Token-level streaming
async for event in app.astream_events(
    {"messages": [("user", "Write a poem")]},
    config=config,
    version="v2"
):
    if event["event"] == "on_chat_model_stream":
        print(event["data"]["chunk"].content, end="")

# Node-level streaming (see each step)
async for chunk in app.astream(
    {"messages": [("user", "Research AI")]},
    config=config,
    stream_mode="updates"  # or "values"
):
    print(f"Node: {chunk}")
```

### Memory Types

```python
# Short-term: within a conversation thread
config = {"configurable": {"thread_id": "conv-123"}}

# Long-term: the Store API (cross-thread)
from langgraph.store.memory import InMemoryStore

store = InMemoryStore()
app = graph.compile(checkpointer=memory, store=store)

# In a node, access the store
def my_node(state, config, *, store):
    user_id = config["configurable"]["user_id"]
    memories = store.search(("users", user_id))
    # Use memories for personalization
    store.put(("users", user_id), "preference", {"theme": "dark"})
```

---

## Installation & Setup

### Basic Installation

```bash
# Core LangGraph
pip install langgraph

# With LangChain integration (most common)
pip install langgraph langchain-openai langchain-anthropic

# With persistence backends
pip install langgraph-checkpoint-sqlite    # SQLite
pip install langgraph-checkpoint-postgres  # PostgreSQL

# Full development stack
pip install langgraph langchain-openai langgraph-checkpoint-sqlite \
    langsmith python-dotenv
```

### Environment Setup

```python
import os
from dotenv import load_dotenv

load_dotenv()

# Required
os.environ["OPENAI_API_KEY"] = "sk-..."

# Optional: LangSmith tracing (highly recommended)
os.environ["LANGCHAIN_TRACING_V2"] = "true"
os.environ["LANGCHAIN_API_KEY"] = "lsv2_..."
os.environ["LANGCHAIN_PROJECT"] = "my-langgraph-app"
```

### Hello World

```python
from langgraph.graph import StateGraph, START, END
from typing import TypedDict

class State(TypedDict):
    message: str

def greet(state: State) -> dict:
    return {"message": f"Hello, {state['message']}!"}

# Build graph
graph = StateGraph(State)
graph.add_node("greet", greet)
graph.add_edge(START, "greet")
graph.add_edge("greet", END)

# Compile & run
app = graph.compile()
result = app.invoke({"message": "World"})
print(result["message"])  # "Hello, World!"
```

---

## Beginner Examples

### Example 1: Simple Chatbot with Memory

```python
from langgraph.graph import StateGraph, MessagesState, START, END
from langgraph.checkpoint.memory import MemorySaver
from langchain_openai import ChatOpenAI

llm = ChatOpenAI(model="gpt-4o")

def chatbot(state: MessagesState) -> dict:
    """Simple chatbot node."""
    response = llm.invoke(state["messages"])
    return {"messages": [response]}

# Build graph
graph = StateGraph(MessagesState)
graph.add_node("chatbot", chatbot)
graph.add_edge(START, "chatbot")
graph.add_edge("chatbot", END)

# Compile with memory
memory = MemorySaver()
app = graph.compile(checkpointer=memory)

# Conversation with persistence
config = {"configurable": {"thread_id": "user-001"}}

# Turn 1
result = app.invoke(
    {"messages": [("user", "Hi, my name is Alice")]},
    config
)
print(result["messages"][-1].content)

# Turn 2 — remembers context!
result = app.invoke(
    {"messages": [("user", "What's my name?")]},
    config
)
print(result["messages"][-1].content)  # "Your name is Alice"
```

### Example 2: Tool-Calling Agent

```python
from langgraph.graph import StateGraph, MessagesState, START, END
from langgraph.prebuilt import ToolNode, tools_condition
from langchain_openai import ChatOpenAI
from langchain_core.tools import tool

# Define tools
@tool
def get_weather(city: str) -> str:
    """Get the current weather for a city."""
    # In production, call a real weather API
    return f"The weather in {city} is 72°F and sunny."

@tool
def search_web(query: str) -> str:
    """Search the web for information."""
    return f"Search results for '{query}': [relevant info here]"

# LLM with tools bound
tools = [get_weather, search_web]
llm = ChatOpenAI(model="gpt-4o").bind_tools(tools)

def agent(state: MessagesState) -> dict:
    """Call the LLM with tools available."""
    response = llm.invoke(state["messages"])
    return {"messages": [response]}

# Build graph
graph = StateGraph(MessagesState)
graph.add_node("agent", agent)
graph.add_node("tools", ToolNode(tools))

graph.add_edge(START, "agent")
graph.add_conditional_edges(
    "agent",
    tools_condition,  # Built-in: routes to "tools" or END
)
graph.add_edge("tools", "agent")

app = graph.compile()

# Use it
result = app.invoke({
    "messages": [("user", "What's the weather in Tokyo?")]
})
print(result["messages"][-1].content)
```

### Example 3: Chatbot with Tool Calling (Full Pattern)

```python
from typing import Annotated, TypedDict
from langgraph.graph import StateGraph, START, END
from langgraph.graph.message import add_messages
from langgraph.prebuilt import ToolNode, tools_condition
from langgraph.checkpoint.memory import MemorySaver
from langchain_openai import ChatOpenAI
from langchain_core.tools import tool

# State
class State(TypedDict):
    messages: Annotated[list, add_messages]

# Tools
@tool
def multiply(a: float, b: float) -> float:
    """Multiply two numbers."""
    return a * b

@tool
def add_numbers(a: float, b: float) -> float:
    """Add two numbers together."""
    return a + b

tools = [multiply, add_numbers]
llm = ChatOpenAI(model="gpt-4o-mini").bind_tools(tools)

# Nodes
def assistant(state: State) -> dict:
    return {"messages": [llm.invoke(state["messages"])]}

# Graph
builder = StateGraph(State)
builder.add_node("assistant", assistant)
builder.add_node("tools", ToolNode(tools))

builder.add_edge(START, "assistant")
builder.add_conditional_edges("assistant", tools_condition)
builder.add_edge("tools", "assistant")

memory = MemorySaver()
graph = builder.compile(checkpointer=memory)

# Multi-turn conversation
config = {"configurable": {"thread_id": "math-session"}}

response = graph.invoke(
    {"messages": [("user", "What is 15 * 23?")]},
    config
)
print(response["messages"][-1].content)  # "15 * 23 = 345"

response = graph.invoke(
    {"messages": [("user", "Now add 100 to that")]},
    config
)
print(response["messages"][-1].content)  # "345 + 100 = 445"
```

---

## Intermediate Patterns

### Pattern 1: Multi-Agent Supervisor

A supervisor agent decides which worker agent to call next.

```python
from langgraph.graph import StateGraph, MessagesState, START, END
from langchain_openai import ChatOpenAI
from langchain_core.messages import HumanMessage, SystemMessage
import json

class SupervisorState(MessagesState):
    next_agent: str

# Worker agents
def researcher(state: SupervisorState) -> dict:
    """Research agent: finds information."""
    llm = ChatOpenAI(model="gpt-4o")
    response = llm.invoke([
        SystemMessage(content="You are a research assistant. Find relevant information."),
        *state["messages"]
    ])
    return {"messages": [response]}

def writer(state: SupervisorState) -> dict:
    """Writing agent: drafts content."""
    llm = ChatOpenAI(model="gpt-4o")
    response = llm.invoke([
        SystemMessage(content="You are a writing assistant. Draft well-structured content."),
        *state["messages"]
    ])
    return {"messages": [response]}

def reviewer(state: SupervisorState) -> dict:
    """Review agent: reviews and provides feedback."""
    llm = ChatOpenAI(model="gpt-4o")
    response = llm.invoke([
        SystemMessage(content="You are a reviewer. Provide constructive feedback."),
        *state["messages"]
    ])
    return {"messages": [response]}

# Supervisor node
def supervisor(state: SupervisorState) -> dict:
    """Supervisor: decides which agent to call next."""
    llm = ChatOpenAI(model="gpt-4o")
    response = llm.invoke([
        SystemMessage(content="""You are a supervisor managing a team:
        - researcher: finds information
        - writer: drafts content
        - reviewer: reviews quality

        Based on the conversation, decide who should act next.
        Respond with JSON: {"next": "researcher|writer|reviewer|FINISH"}"""),
        *state["messages"]
    ])
    decision = json.loads(response.content)
    return {"next_agent": decision["next"], "messages": [response]}

def route_supervisor(state: SupervisorState) -> str:
    """Route to the next agent or finish."""
    return state.get("next_agent", "FINISH")

# Build graph
graph = StateGraph(SupervisorState)
graph.add_node("supervisor", supervisor)
graph.add_node("researcher", researcher)
graph.add_node("writer", writer)
graph.add_node("reviewer", reviewer)

graph.add_edge(START, "supervisor")
graph.add_conditional_edges(
    "supervisor",
    route_supervisor,
    {
        "researcher": "researcher",
        "writer": "writer",
        "reviewer": "reviewer",
        "FINISH": END
    }
)

# After each worker, go back to supervisor
graph.add_edge("researcher", "supervisor")
graph.add_edge("writer", "supervisor")
graph.add_edge("reviewer", "supervisor")

app = graph.compile()
```

### Pattern 2: Conditional Branching with State

```python
from langgraph.graph import StateGraph, START, END
from typing import TypedDict, Literal

class TicketState(TypedDict):
    query: str
    category: str
    priority: str
    response: str

def classify(state: TicketState) -> dict:
    """Classify the support ticket."""
    query = state["query"].lower()
    if "billing" in query or "payment" in query:
        return {"category": "billing", "priority": "medium"}
    elif "bug" in query or "error" in query or "crash" in query:
        return {"category": "technical", "priority": "high"}
    elif "feature" in query or "request" in query:
        return {"category": "feature", "priority": "low"}
    return {"category": "general", "priority": "medium"}

def handle_billing(state: TicketState) -> dict:
    return {"response": f"Billing team will handle: {state['query']}"}

def handle_technical(state: TicketState) -> dict:
    return {"response": f"Engineering team alert (P{1 if state['priority']=='high' else 2}): {state['query']}"}

def handle_feature(state: TicketState) -> dict:
    return {"response": f"Feature request logged: {state['query']}"}

def handle_general(state: TicketState) -> dict:
    return {"response": f"General support: {state['query']}"}

def route_ticket(state: TicketState) -> str:
    return state["category"]

# Build graph
graph = StateGraph(TicketState)
graph.add_node("classify", classify)
graph.add_node("billing", handle_billing)
graph.add_node("technical", handle_technical)
graph.add_node("feature", handle_feature)
graph.add_node("general", handle_general)

graph.add_edge(START, "classify")
graph.add_conditional_edges(
    "classify",
    route_ticket,
    {
        "billing": "billing",
        "technical": "technical",
        "feature": "feature",
        "general": "general"
    }
)
graph.add_edge("billing", END)
graph.add_edge("technical", END)
graph.add_edge("feature", END)
graph.add_edge("general", END)

app = graph.compile()
result = app.invoke({"query": "I found a bug in the checkout page"})
print(result["response"])  # "Engineering team alert (P1): ..."
```

### Pattern 3: Human-in-the-Loop Approval

```python
from langgraph.graph import StateGraph, MessagesState, START, END
from langgraph.checkpoint.memory import MemorySaver
from langgraph.types import interrupt, Command

class ApprovalState(MessagesState):
    action: str
    approved: bool

def propose_action(state: ApprovalState) -> dict:
    """Agent proposes an action."""
    # LLM decides what action to take
    return {"action": "Delete all records older than 30 days"}

def human_review(state: ApprovalState) -> dict:
    """Pause for human review."""
    approval = interrupt({
        "question": f"Do you approve this action?\n\nAction: {state['action']}",
        "options": ["yes", "no"]
    })
    return {"approved": approval == "yes"}

def execute_action(state: ApprovalState) -> dict:
    if state["approved"]:
        return {"messages": [("assistant", f"Executed: {state['action']}")]}
    return {"messages": [("assistant", "Action cancelled by operator.")]}

def route_approval(state: ApprovalState) -> str:
    return "execute" if state.get("approved") is not None else "review"

graph = StateGraph(ApprovalState)
graph.add_node("propose", propose_action)
graph.add_node("review", human_review)
graph.add_node("execute", execute_action)

graph.add_edge(START, "propose")
graph.add_edge("propose", "review")
graph.add_edge("review", "execute")
graph.add_edge("execute", END)

memory = MemorySaver()
app = graph.compile(checkpointer=memory, interrupt_before=["review"])

# Step 1: Run until interrupt
config = {"configurable": {"thread_id": "approval-1"}}
result = app.invoke({"messages": [("user", "Clean up old data")]}, config)
# Execution pauses at "review" node

# Step 2: Resume with human input (after human reviews)
result = app.invoke(Command(resume="yes"), config)
print(result["messages"][-1])  # "Executed: Delete all records..."
```

### Pattern 4: Streaming Tokens and Steps

```python
import asyncio
from langgraph.graph import StateGraph, MessagesState, START, END
from langchain_openai import ChatOpenAI

llm = ChatOpenAI(model="gpt-4o", streaming=True)

def chatbot(state: MessagesState) -> dict:
    return {"messages": [llm.invoke(state["messages"])]}

graph = StateGraph(MessagesState)
graph.add_node("chatbot", chatbot)
graph.add_edge(START, "chatbot")
graph.add_edge("chatbot", END)
app = graph.compile()

# Stream tokens
async def stream_response():
    async for event in app.astream_events(
        {"messages": [("user", "Write a haiku about coding")]},
        version="v2"
    ):
        kind = event["event"]
        if kind == "on_chat_model_stream":
            content = event["data"]["chunk"].content
            if content:
                print(content, end="", flush=True)

asyncio.run(stream_response())
```

---

## Advanced Architectures

### Architecture 1: ReAct Agent (Reasoning + Acting)

```python
from langgraph.graph import StateGraph, MessagesState, START, END
from langgraph.prebuilt import ToolNode, tools_condition
from langchain_openai import ChatOpenAI
from langchain_core.tools import tool
from langchain_core.messages import SystemMessage

@tool
def search(query: str) -> str:
    """Search for information on the web."""
    return f"Results for '{query}': LangGraph is a framework for building stateful agents..."

@tool
def calculator(expression: str) -> str:
    """Evaluate a math expression."""
    return str(eval(expression))

@tool
def code_executor(code: str) -> str:
    """Execute Python code and return output."""
    import io, contextlib
    output = io.StringIO()
    with contextlib.redirect_stdout(output):
        exec(code)
    return output.getvalue()

tools = [search, calculator, code_executor]
llm = ChatOpenAI(model="gpt-4o").bind_tools(tools)

REACT_SYSTEM_PROMPT = """You are a helpful AI assistant with access to tools.
Think step-by-step:
1. Analyze the user's question
2. Decide if you need to use a tool
3. If yes, call the appropriate tool
4. Observe the result
5. Repeat 2-4 until you have enough information
6. Provide a final answer

Always show your reasoning."""

def agent(state: MessagesState) -> dict:
    messages = [SystemMessage(content=REACT_SYSTEM_PROMPT)] + state["messages"]
    response = llm.invoke(messages)
    return {"messages": [response]}

# Build ReAct graph
graph = StateGraph(MessagesState)
graph.add_node("agent", agent)
graph.add_node("tools", ToolNode(tools))

graph.add_edge(START, "agent")
graph.add_conditional_edges("agent", tools_condition)
graph.add_edge("tools", "agent")  # Loop back after tool execution

app = graph.compile()

result = app.invoke({
    "messages": [("user", "What is LangGraph and what is 2^10?")]
})
for msg in result["messages"]:
    print(f"{msg.type}: {msg.content[:200]}")
```

### Architecture 2: Plan-and-Execute

```python
from langgraph.graph import StateGraph, START, END
from langchain_openai import ChatOpenAI
from typing import TypedDict, Annotated
from operator import add

class PlanExecuteState(TypedDict):
    objective: str
    plan: list[str]
    completed_steps: Annotated[list[str], add]
    current_step: str
    results: Annotated[list[str], add]
    final_answer: str

llm = ChatOpenAI(model="gpt-4o")

def planner(state: PlanExecuteState) -> dict:
    """Create a step-by-step plan."""
    response = llm.invoke(
        f"Create a step-by-step plan to: {state['objective']}\n"
        f"Return each step on a new line, numbered 1-N."
    )
    steps = [s.strip() for s in response.content.split("\n") if s.strip()]
    return {"plan": steps, "current_step": steps[0] if steps else ""}

def executor(state: PlanExecuteState) -> dict:
    """Execute the current step."""
    step = state["current_step"]
    response = llm.invoke(
        f"Execute this step: {step}\n"
        f"Context from previous steps: {state['results']}"
    )
    return {
        "results": [f"{step}: {response.content}"],
        "completed_steps": [step]
    }

def replanner(state: PlanExecuteState) -> dict:
    """Check progress and decide next step."""
    remaining = [s for s in state["plan"] if s not in state["completed_steps"]]
    if remaining:
        return {"current_step": remaining[0]}
    return {"current_step": "DONE"}

def should_continue(state: PlanExecuteState) -> str:
    if state["current_step"] == "DONE":
        return "synthesize"
    return "executor"

def synthesize(state: PlanExecuteState) -> dict:
    """Synthesize final answer from all step results."""
    response = llm.invoke(
        f"Objective: {state['objective']}\n"
        f"Results: {state['results']}\n"
        f"Provide a comprehensive final answer."
    )
    return {"final_answer": response.content}

# Build plan-and-execute graph
graph = StateGraph(PlanExecuteState)
graph.add_node("planner", planner)
graph.add_node("executor", executor)
graph.add_node("replanner", replanner)
graph.add_node("synthesize", synthesize)

graph.add_edge(START, "planner")
graph.add_edge("planner", "executor")
graph.add_edge("executor", "replanner")
graph.add_conditional_edges(
    "replanner",
    should_continue,
    {"executor": "executor", "synthesize": "synthesize"}
)
graph.add_edge("synthesize", END)

app = graph.compile()
```

### Architecture 3: Self-RAG (Self-Reflective Retrieval)

```python
from langgraph.graph import StateGraph, START, END
from typing import TypedDict, Annotated
from operator import add

class SelfRAGState(TypedDict):
    question: str
    documents: list[str]
    generation: str
    is_relevant: bool
    is_hallucination: bool
    is_useful: bool
    retry_count: int

def retrieve(state: SelfRAGState) -> dict:
    """Retrieve relevant documents."""
    # In production: use a real retriever
    docs = vector_store.similarity_search(state["question"], k=4)
    return {"documents": [d.page_content for d in docs]}

def grade_documents(state: SelfRAGState) -> dict:
    """Grade retrieved documents for relevance."""
    relevant = []
    for doc in state["documents"]:
        score = llm.invoke(
            f"Is this document relevant to '{state['question']}'?\n"
            f"Document: {doc}\nAnswer yes or no."
        )
        if "yes" in score.content.lower():
            relevant.append(doc)
    return {"documents": relevant, "is_relevant": len(relevant) > 0}

def generate(state: SelfRAGState) -> dict:
    """Generate answer from documents."""
    context = "\n".join(state["documents"])
    response = llm.invoke(
        f"Answer based on context:\n{context}\n\nQuestion: {state['question']}"
    )
    return {"generation": response.content}

def check_hallucination(state: SelfRAGState) -> dict:
    """Check if generation is grounded in documents."""
    check = llm.invoke(
        f"Is this answer grounded in the documents?\n"
        f"Documents: {state['documents']}\n"
        f"Answer: {state['generation']}\nRespond yes or no."
    )
    return {"is_hallucination": "no" in check.content.lower()}

def check_usefulness(state: SelfRAGState) -> dict:
    """Check if the answer actually addresses the question."""
    check = llm.invoke(
        f"Does this answer address the question?\n"
        f"Question: {state['question']}\n"
        f"Answer: {state['generation']}\nRespond yes or no."
    )
    return {"is_useful": "yes" in check.content.lower()}

def route_after_grading(state: SelfRAGState) -> str:
    if not state["is_relevant"]:
        return "web_search"  # Fallback to web search
    return "generate"

def route_after_check(state: SelfRAGState) -> str:
    if state["is_hallucination"] or not state["is_useful"]:
        if state.get("retry_count", 0) < 3:
            return "generate"  # Retry
        return END  # Give up after 3 tries
    return END

# Build Self-RAG graph
graph = StateGraph(SelfRAGState)
graph.add_node("retrieve", retrieve)
graph.add_node("grade", grade_documents)
graph.add_node("generate", generate)
graph.add_node("check_hallucination", check_hallucination)
graph.add_node("check_usefulness", check_usefulness)

graph.add_edge(START, "retrieve")
graph.add_edge("retrieve", "grade")
graph.add_conditional_edges("grade", route_after_grading)
graph.add_edge("generate", "check_hallucination")
graph.add_edge("check_hallucination", "check_usefulness")
graph.add_conditional_edges("check_usefulness", route_after_check)

app = graph.compile()
```

### Architecture 4: Reflection Pattern

```python
from langgraph.graph import StateGraph, MessagesState, START, END
from langchain_openai import ChatOpenAI
from langchain_core.messages import SystemMessage, HumanMessage

class ReflectionState(MessagesState):
    draft: str
    critique: str
    iteration: int

def generate(state: ReflectionState) -> dict:
    """Generate or improve a draft."""
    llm = ChatOpenAI(model="gpt-4o")
    if state.get("critique"):
        prompt = f"Improve this draft based on feedback:\nDraft: {state['draft']}\nFeedback: {state['critique']}"
    else:
        prompt = f"Write a first draft for: {state['messages'][-1].content}"
    response = llm.invoke([SystemMessage(content="You are an expert writer."), HumanMessage(content=prompt)])
    return {"draft": response.content, "iteration": state.get("iteration", 0) + 1}

def reflect(state: ReflectionState) -> dict:
    """Critique the current draft."""
    llm = ChatOpenAI(model="gpt-4o")
    response = llm.invoke([
        SystemMessage(content="You are a tough editor. Provide specific, actionable feedback."),
        HumanMessage(content=f"Critique this draft:\n{state['draft']}")
    ])
    return {"critique": response.content}

def should_continue(state: ReflectionState) -> str:
    if state.get("iteration", 0) >= 3:
        return END
    return "reflect"

graph = StateGraph(ReflectionState)
graph.add_node("generate", generate)
graph.add_node("reflect", reflect)

graph.add_edge(START, "generate")
graph.add_conditional_edges("generate", should_continue)
graph.add_edge("reflect", "generate")

app = graph.compile()

result = app.invoke({
    "messages": [("user", "Write a blog post about LangGraph")]
})
print(result["draft"])  # Final polished draft after 3 iterations
```

### Architecture 5: Map-Reduce (Parallel Processing)

```python
from langgraph.graph import StateGraph, START, END
from langgraph.types import Send
from typing import TypedDict, Annotated
from operator import add

class MapReduceState(TypedDict):
    documents: list[str]
    summaries: Annotated[list[str], add]
    final_summary: str

class SummarizeState(TypedDict):
    document: str
    summary: str

def map_step(state: MapReduceState) -> list[Send]:
    """Fan out: send each document to a summarizer."""
    return [
        Send("summarize", {"document": doc})
        for doc in state["documents"]
    ]

def summarize(state: SummarizeState) -> dict:
    """Summarize a single document (runs in parallel)."""
    response = llm.invoke(f"Summarize this concisely:\n{state['document']}")
    return {"summaries": [response.content]}

def reduce_step(state: MapReduceState) -> dict:
    """Combine all summaries into a final summary."""
    all_summaries = "\n\n".join(state["summaries"])
    response = llm.invoke(
        f"Combine these summaries into one coherent summary:\n{all_summaries}"
    )
    return {"final_summary": response.content}

graph = StateGraph(MapReduceState)
graph.add_node("summarize", summarize)
graph.add_node("reduce", reduce_step)

graph.add_conditional_edges(START, map_step)
graph.add_edge("summarize", "reduce")
graph.add_edge("reduce", END)

app = graph.compile()

result = app.invoke({
    "documents": [
        "Document 1 content...",
        "Document 2 content...",
        "Document 3 content..."
    ]
})
print(result["final_summary"])
```

---

## Best Practices & Optimization

### 1. State Design

```python
# ✅ Good: Specific, typed state
class AgentState(TypedDict):
    messages: Annotated[list, add_messages]
    current_tool: str
    retry_count: int
    context: dict

# ❌ Bad: Overly generic state
class AgentState(TypedDict):
    data: dict  # What's in here? Nobody knows.
```

### 2. Node Design

```python
# ✅ Good: Small, focused nodes
def classify(state): ...
def retrieve(state): ...
def generate(state): ...

# ❌ Bad: God node that does everything
def do_everything(state):
    classify()
    retrieve()
    generate()
    validate()
    return result
```

### 3. Error Handling

```python
from langgraph.errors import NodeInterrupt

def risky_node(state):
    try:
        result = call_external_api(state)
        return {"result": result}
    except TimeoutError:
        # Retry logic via state
        retry = state.get("retry_count", 0)
        if retry < 3:
            return {"retry_count": retry + 1}
        raise NodeInterrupt("Max retries exceeded")
```

### 4. Always Use Checkpointing in Production

```python
# ✅ Production: PostgreSQL checkpointer
from langgraph.checkpoint.postgres import PostgresSaver

checkpointer = PostgresSaver.from_conn_string(
    "postgresql://user:pass@host:5432/dbname"
)
app = graph.compile(checkpointer=checkpointer)

# ❌ Never: No checkpointer in production
app = graph.compile()  # No persistence, no recovery
```

### 5. Subgraphs for Modularity

```python
# Define reusable subgraph
def build_rag_subgraph():
    graph = StateGraph(RAGState)
    graph.add_node("retrieve", retrieve)
    graph.add_node("generate", generate)
    graph.add_edge(START, "retrieve")
    graph.add_edge("retrieve", "generate")
    graph.add_edge("generate", END)
    return graph.compile()

# Use in parent graph
parent = StateGraph(ParentState)
parent.add_node("rag", build_rag_subgraph())
parent.add_node("other_logic", other_node)
```

---

## Common Pitfalls & Solutions

### Pitfall 1: State Mutation Instead of Return

```python
# ❌ WRONG: Mutating state directly
def bad_node(state):
    state["messages"].append("new message")  # Mutation!
    return state

# ✅ CORRECT: Return partial state update
def good_node(state):
    return {"messages": [("assistant", "new message")]}
```

### Pitfall 2: Missing Reducer for Append-Only Lists

```python
# ❌ WRONG: No reducer — messages get replaced, not appended
class State(TypedDict):
    messages: list

# ✅ CORRECT: Use Annotated with add or add_messages
from langgraph.graph.message import add_messages

class State(TypedDict):
    messages: Annotated[list, add_messages]
```

### Pitfall 3: Infinite Loops

```python
# ❌ DANGEROUS: No termination condition
graph.add_edge("agent", "tools")
graph.add_edge("tools", "agent")  # Loops forever!

# ✅ SAFE: Conditional edge with termination
graph.add_conditional_edges(
    "agent",
    tools_condition,  # Returns END when no tool calls
)
graph.add_edge("tools", "agent")
```

### Pitfall 4: Forgetting thread_id

```python
# ❌ WRONG: No thread_id with checkpointer
app.invoke({"messages": [("user", "hi")]})  # Raises error

# ✅ CORRECT: Always pass thread_id
config = {"configurable": {"thread_id": "unique-thread-123"}}
app.invoke({"messages": [("user", "hi")]}, config)
```

### Pitfall 5: Blocking Async in Sync Context

```python
# ❌ WRONG: Using sync invoke inside async function
async def handler():
    result = app.invoke(...)  # Blocks event loop!

# ✅ CORRECT: Use ainvoke in async context
async def handler():
    result = await app.ainvoke(...)
```

---

## Comparison with Similar Tools

### LangGraph vs Other Frameworks

| Feature | LangGraph | CrewAI | Autogen | Vanilla LangChain Agents |
|---------|:---------:|:------:|:-------:|:------------------------:|
| **Approach** | Graph-based | Role-based | Conversation-based | Chain-based |
| **Control Flow** | Explicit (you define) | Implicit (framework) | Implicit (chat) | Implicit (AgentExecutor) |
| **State Management** | First-class TypedDict | Internal | Message history | Memory classes |
| **Multi-Agent** | Supervisor, swarm, hierarchical | Crew + Tasks | GroupChat | Manual wiring |
| **Human-in-the-Loop** | `interrupt()` built-in | Manual | Human proxy agent | Not built-in |
| **Persistence** | SQLite/Postgres/Redis | No built-in | No built-in | No built-in |
| **Streaming** | Token + node + custom events | Limited | Limited | LCEL streaming |
| **Fault Tolerance** | Checkpointing + retry | Basic | Basic | None |
| **Observability** | LangSmith native | Basic logging | Basic logging | LangSmith |
| **Deployment** | LangGraph Platform | Docker | Docker | LangServe |
| **Learning Curve** | Medium (graph concepts) | Low (intuitive roles) | Low (chat-based) | Low (but limited) |
| **Flexibility** | Very High | Medium | Medium | Low |
| **Production Ready** | ✅ Yes | ⚠️ Growing | ⚠️ Growing | ⚠️ Limited |
| **Best For** | Complex, stateful agents | Quick team simulation | Research / prototyping | Simple tool-calling |

### When to Use What

```
Need full control over agent flow?           → LangGraph
Need quick multi-agent prototype?            → CrewAI
Need research multi-agent conversations?     → Autogen
Need simple tool-calling chatbot?            → LangChain AgentExecutor
Need production-grade, fault-tolerant agents? → LangGraph
Need human approval in the loop?             → LangGraph
Need to resume after crash?                  → LangGraph
```

---

## Real-World Use Cases

### 1. Customer Support Agent

```python
# Classifies ticket → routes to specialist → escalates if needed
# Uses human-in-the-loop for refund approvals
# Persists conversation state across sessions
```

### 2. Research Agent

```python
# Plans research steps → executes searches → synthesizes findings
# Uses map-reduce for parallel document analysis
# Self-reflects on answer quality before responding
```

### 3. Coding Agent

```python
# Plans implementation → writes code → tests → fixes bugs → iterates
# Uses reflection pattern for code review
# Human approval before merging
```

### 4. Data Pipeline Agent

```python
# Reads data source → transforms → validates → loads
# Checkpoints after each step for recovery
# Alerts human on anomalies via interrupt()
```

### 5. Multi-Agent Content Creation

```python
# Supervisor → Researcher → Writer → Editor → Publisher
# Each agent has specialized tools
# Quality gates between steps
```

---

## Performance Considerations

### Latency Optimization

| Strategy | Impact | When to Use |
|----------|--------|-------------|
| **Smaller models for routing** | 3-5x faster routing | Supervisor/classifier nodes |
| **Parallel tool execution** | Linear speedup | Independent tool calls |
| **Streaming** | Better perceived latency | User-facing applications |
| **Caching LLM responses** | Eliminates redundant calls | Repeated queries |
| **Subgraph compilation** | Faster graph traversal | Complex graphs |

### Memory Optimization

| Strategy | Impact | When to Use |
|----------|--------|-------------|
| **Trim old messages** | Reduces token usage | Long conversations |
| **Summary memory** | Compress history | Extended interactions |
| **Selective state** | Less checkpoint data | Large state objects |
| **PostgreSQL checkpointer** | Production-grade | Any production deployment |

### Cost Optimization

```python
# Use cheaper models for routing/classification
routing_llm = ChatOpenAI(model="gpt-4o-mini")  # Cheap, fast

# Use powerful models for generation
generation_llm = ChatOpenAI(model="gpt-4o")  # Accurate

# Cache responses
from langchain.cache import SQLiteCache
from langchain.globals import set_llm_cache
set_llm_cache(SQLiteCache(database_path=".langchain_cache.db"))
```

### Scalability

```
Single User    → In-memory checkpointer, single process
10-100 Users   → SQLite checkpointer, single server
100-10K Users  → PostgreSQL checkpointer, multiple workers
10K+ Users     → LangGraph Platform (managed), auto-scaling
```
