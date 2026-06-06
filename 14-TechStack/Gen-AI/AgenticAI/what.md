# Agentic AI: Complete Guide

## 1. What is Agentic AI?

Agentic AI refers to **autonomous AI systems** that can plan, reason, use tools, and take actions to achieve goals with minimal human intervention. Unlike simple chatbots that respond to single prompts, agentic systems execute multi-step workflows, maintain state across interactions, observe outcomes, and adapt their approach.

**Key traits of agentic systems:**
- **Autonomy** — Make decisions without step-by-step human guidance
- **Tool Use** — Call APIs, search databases, execute code, interact with external systems
- **Planning** — Break complex goals into sub-tasks and execute them in order
- **Memory** — Retain context across steps and sessions
- **Reflection** — Evaluate own outputs, detect errors, self-correct
- **Multi-agent collaboration** — Multiple specialized agents work together

---

## 2. Core Concepts

### Agent Architecture
```
Perception → Planning → Action → Observation → Reflection → Loop
```

1. **Perception** — Receive task/goal from user or system
2. **Planning** — Decompose into sub-tasks (chain-of-thought, tree-of-thought)
3. **Action** — Execute tools, call APIs, generate content
4. **Observation** — Receive results from actions
5. **Reflection** — Evaluate if goal is met, detect errors
6. **Loop** — Repeat until task complete or max iterations reached

### ReAct Pattern (Reasoning + Acting)
The foundational agent loop:
```
Thought: I need to find the stock price of RELIANCE
Action: search_stock_price(symbol="RELIANCE")
Observation: RELIANCE: ₹2850.50, +1.2% today
Thought: I have the price. Now I need to check the sector performance.
Action: get_sector_data(sector="Oil & Gas")
Observation: Sector up 0.8% today
Thought: I have all the information needed.
Final Answer: RELIANCE is trading at ₹2850.50 (+1.2%), outperforming its sector (+0.8%).
```

### Tool Use
Agents extend LLM capabilities by calling external tools:
- **APIs** — REST endpoints, GraphQL queries
- **Databases** — SQL queries, vector search
- **Code execution** — Python, JavaScript in sandboxed environments
- **File operations** — Read, write, parse documents
- **Web browsing** — Search, scrape, navigate

### Memory Types
| Type | Scope | Example |
|------|-------|---------|
| **Working memory** | Current task | Variables, intermediate results |
| **Short-term memory** | Current session | Conversation history |
| **Long-term memory** | Across sessions | User preferences, learned facts |
| **Episodic memory** | Past experiences | "Last time I tried X, it failed because Y" |
| **Semantic memory** | Knowledge base | Domain knowledge, documentation |

---

## 3. Agent Design Patterns

### Single Agent (Simple)
One agent with access to multiple tools. Good for straightforward tasks.

```python
from langchain.agents import create_tool_calling_agent

tools = [search_tool, calculator, database_query]
agent = create_tool_calling_agent(llm, tools, prompt)
result = agent.invoke({"input": "What's the PE ratio of RELIANCE?"})
```

### Multi-Agent (Collaborative)
Multiple specialized agents collaborate on complex tasks:

```python
# CrewAI approach
researcher = Agent(role="Researcher", tools=[search, scrape])
analyst = Agent(role="Analyst", tools=[calculator, database])
writer = Agent(role="Writer", tools=[])

crew = Crew(agents=[researcher, analyst, writer], process=Process.sequential)
```

### Hierarchical (Manager-Worker)
A manager agent delegates to specialized workers:

```python
# Manager decides which specialist to invoke
manager = Agent(role="Project Manager")
specialists = {
    "data": DataAgent(tools=[sql, api]),
    "analysis": AnalysisAgent(tools=[stats, ml]),
    "report": ReportAgent(tools=[chart, pdf]),
}
# Manager routes subtasks to appropriate specialist
```

### Supervisor Pattern
A supervisor monitors agent actions and can override or redirect:

```python
# LangGraph approach
def supervisor(state):
    """Decide next agent or finish."""
    if state["quality_score"] < 0.8:
        return "revise"
    if not state["all_sections_complete"]:
        return "next_agent"
    return "finish"
```

### Reflection Pattern
Agent self-evaluates and improves its outputs:

```python
# Generate → Evaluate → Revise loop
draft = agent.generate(task)
critique = agent.evaluate(draft, criteria)
if critique.score < threshold:
    final = agent.revise(draft, critique.feedback)
else:
    final = draft
```

---

## 4. Key Frameworks

| Framework | Paradigm | Best For |
|-----------|----------|----------|
| **LangGraph** | Graph-based state machine | Complex stateful workflows |
| **CrewAI** | Role-based teams | Business process automation |
| **AutoGen** | Conversation-based | Code generation, research |
| **LlamaIndex** | Data-agent workflows | RAG + agent hybrid |
| **Semantic Kernel** | Planner + plugins | Enterprise (.NET/Python) |
| **OpenAI Assistants** | Managed agent API | Quick prototypes |
| **Claude MCP** | Tool protocol standard | Cross-platform tool use |

---

## 5. Building Agents with LangGraph

```python
from langgraph.graph import StateGraph, END
from typing import TypedDict, Annotated
import operator

class AgentState(TypedDict):
    messages: Annotated[list, operator.add]
    plan: str
    current_step: int
    results: dict

def planner(state: AgentState) -> AgentState:
    """Break task into steps."""
    plan = llm.invoke(
        f"Break this into 3-5 steps: {state['messages'][-1]}"
    )
    return {"plan": plan.content, "current_step": 0}

def executor(state: AgentState) -> AgentState:
    """Execute current step using tools."""
    step = state["plan"].split("\n")[state["current_step"]]
    result = agent_executor.invoke({"input": step})
    return {
        "results": {**state["results"], state["current_step"]: result},
        "current_step": state["current_step"] + 1,
        "messages": [f"Completed step {state['current_step']}: {result}"],
    }

def should_continue(state: AgentState) -> str:
    total_steps = len(state["plan"].split("\n"))
    if state["current_step"] >= total_steps:
        return "synthesize"
    return "execute"

def synthesizer(state: AgentState) -> AgentState:
    """Combine all step results into final answer."""
    summary = llm.invoke(f"Summarize results: {state['results']}")
    return {"messages": [summary.content]}

# Build graph
graph = StateGraph(AgentState)
graph.add_node("plan", planner)
graph.add_node("execute", executor)
graph.add_node("synthesize", synthesizer)

graph.set_entry_point("plan")
graph.add_edge("plan", "execute")
graph.add_conditional_edges("execute", should_continue)
graph.add_edge("synthesize", END)

app = graph.compile()
result = app.invoke({"messages": ["Analyze top 5 Nifty stocks"], "results": {}})
```

---

## 6. MCP (Model Context Protocol)

MCP standardizes how agents connect to external tools:

```python
# MCP Server (tool provider)
from mcp.server import Server

server = Server("stock-data")

@server.tool("get_stock_price")
async def get_price(symbol: str) -> str:
    """Get current stock price."""
    price = await fetch_live_price(symbol)
    return f"{symbol}: ₹{price}"

@server.tool("get_financials")
async def get_financials(symbol: str, metric: str) -> str:
    """Get financial metrics (PE, EPS, etc)."""
    data = await fetch_financials(symbol)
    return f"{symbol} {metric}: {data[metric]}"

# MCP Client (agent-side)
from mcp.client import ClientSession

async with ClientSession(server) as session:
    tools = await session.list_tools()
    result = await session.call_tool("get_stock_price", {"symbol": "TCS"})
```

---

## 7. Safety & Guardrails for Agents

Agents are more dangerous than simple LLM calls because they take actions:

| Risk | Mitigation |
|------|-----------|
| Infinite loops | Max iterations limit (e.g., 10 steps) |
| Unintended actions | Sandbox execution, read-only by default |
| Cost explosion | Token budgets, rate limits per agent |
| Hallucinated tool calls | Validate tool names against registry |
| Data leakage | Input/output guardrails (PII, secrets) |
| Cascading failures | Circuit breaker pattern, timeout per tool |

```python
# Safety wrapper
class SafeAgent:
    MAX_ITERATIONS = 10
    MAX_TOKENS = 50000
    TIMEOUT_SECONDS = 120

    def run(self, task):
        for i in range(self.MAX_ITERATIONS):
            if self.token_count > self.MAX_TOKENS:
                return "Token budget exceeded"
            result = self.step(task)
            if result.done:
                return result
        return "Max iterations reached — task incomplete"
```

---

## 8. Best Practices

| Practice | Why |
|----------|-----|
| Start simple, add complexity | Single agent → multi-agent only when needed |
| Explicit tool descriptions | LLMs choose tools based on descriptions |
| Structured outputs | Pydantic models prevent parsing errors |
| Deterministic where possible | Use conditional edges, not LLM routing, for known branches |
| Human-in-the-loop for critical actions | Approve before destructive operations |
| Log everything | Every tool call, every LLM response, every decision |
| Test with diverse inputs | Edge cases, adversarial inputs, empty results |
| Set token budgets | Prevent runaway agents from burning money |

---

## 9. Common Pitfalls

| Pitfall | Solution |
|---------|----------|
| Over-engineering with agents | Not every task needs an agent — use simple chains first |
| Agent loops forever | Set `max_iterations`, add timeout, detect repeated actions |
| Wrong tool selection | Improve tool descriptions, reduce tool count |
| Context window overflow | Summarize intermediate results, prune old messages |
| Multi-agent coordination overhead | Start with 2-3 agents max, add only when justified |
| Inconsistent agent behavior | Lower temperature (0.0-0.3), add output validation |

---

## 10. Real-World Use Cases

1. **Automated Research** — Agent searches web, reads papers, synthesizes findings
2. **Customer Support** — Triage agent routes to specialist agents (billing, tech, account)
3. **Code Generation** — Planning agent designs, coding agent implements, review agent validates
4. **Data Analysis** — Agent queries databases, runs statistical tests, generates visualizations
5. **Trading Systems** — Signal generation, risk assessment, order execution as agent pipeline
6. **DevOps Automation** — Monitor agent detects issues, diagnosis agent investigates, fix agent deploys patches

---

## 11. Agent Architecture for Financial Trading

```python
# sjarvis 4-agent architecture
class TradingAgentSystem:
    """Multi-agent trading system with specialized agents."""
    
    def __init__(self):
        self.agents = {
            "alpha": AlphaAgent(),      # Quant research, alpha discovery
            "risk": RiskAgent(),        # SEBI limits, drawdown monitoring
            "execution": ExecAgent(),   # Order quality, slippage tracking
            "data": DataAgent(),        # Market data, regime analysis
        }
    
    async def process_signal(self, signal: TradingSignal):
        # Step 1: Alpha agent validates signal strength
        alpha_result = await self.agents["alpha"].evaluate(signal)
        if alpha_result.confidence < 0.6:
            return Rejected("Low confidence")
        
        # Step 2: Risk agent checks SEBI compliance
        risk_result = await self.agents["risk"].check_compliance(signal)
        if risk_result.has_violations:
            return Rejected(f"SEBI violation: {risk_result.violations}")
        
        # Step 3: Data agent enriches with market context
        context = await self.agents["data"].get_regime(signal.symbol)
        
        # Step 4: Execution agent handles order placement
        order = await self.agents["execution"].execute(
            signal, risk_result.position_size, context
        )
        return order
```

### Agent Communication Patterns

| Pattern | Best For | Complexity |
|---------|----------|-----------|
| **Sequential Pipeline** | Linear workflows (signal → risk → execute) | Low |
| **Supervisor** | Dynamic routing based on task type | Medium |
| **Hierarchical** | Complex orgs (manager → team leads → workers) | High |
| **Swarm** | Self-organizing, emergent behavior | Very High |
| **Debate** | Adversarial — bull vs bear analysis for better decisions | Medium |

---

## 12. Safety & Guardrails for Agents

```python
class AgentGuardrails:
    """Non-negotiable safety constraints for autonomous agents."""
    
    MAX_ITERATIONS = 25           # Prevent infinite loops
    MAX_TOKENS_PER_SESSION = 50000  # Budget control
    REQUIRE_HUMAN_APPROVAL = [    # Actions needing approval
        "place_order", "modify_order", "cancel_all",
        "change_risk_limits", "enable_live_trading",
    ]
    
    def check_action(self, action: str, context: dict) -> bool:
        # Circuit breaker — never trade when breaker is OPEN
        if action.startswith("trade") and circuit_breaker.state == "OPEN":
            return False
        
        # SEBI compliance — hard limits
        if action == "place_order":
            return self.sebi_validator.validate(context["order"])
        
        # Budget guard — stop if iteration limit reached
        if context["iteration"] >= self.MAX_ITERATIONS:
            return False
        
        return True
```

---

## 13. Evaluation: How to Measure Agent Quality

| Metric | Description | Target |
|--------|-------------|--------|
| **Task completion rate** | % of tasks successfully completed | > 85% |
| **Tool selection accuracy** | Correct tool chosen for task | > 90% |
| **Iteration efficiency** | Avg iterations to complete task | < 5 |
| **Cost per task** | Tokens consumed per completed task | < $0.10 |
| **Error recovery rate** | % of errors self-corrected | > 60% |
| **User satisfaction** | Post-task rating | > 4.0/5 |
| **Safety violations** | Unapproved actions attempted | 0 |
