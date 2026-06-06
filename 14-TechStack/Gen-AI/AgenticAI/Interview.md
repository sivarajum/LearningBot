# Agentic AI: Interview Questions & Answers

## Beginner Level

### Q1: What distinguishes agentic AI from traditional chatbots?
**A:** Traditional chatbots are **reactive** — they respond to a single prompt and return a single response. Agentic AI is **proactive and autonomous**:

| Aspect | Chatbot | Agentic AI |
|--------|---------|------------|
| Interaction | Single turn | Multi-step autonomous |
| Tools | None | APIs, databases, code execution |
| Planning | None | Decomposes goals into sub-tasks |
| Memory | Conversation history | Working + long-term memory |
| Self-correction | None | Evaluates and revises outputs |
| Actions | Text generation only | Real-world actions (API calls, file ops) |

An agent asked "Analyze RELIANCE stock" will: search for financial data → calculate ratios → compare with sector → generate report. A chatbot would give a generic answer from training data.

### Q2: Explain the ReAct (Reasoning + Acting) pattern.
**A:** ReAct interleaves reasoning (chain-of-thought) with tool actions:

```
Thought: I need RELIANCE's P/E ratio. Let me query the database.
Action: query_db("SELECT pe_ratio FROM stocks WHERE symbol='RELIANCE'")
Observation: pe_ratio = 28.5
Thought: Now I need the sector average for comparison.
Action: query_db("SELECT AVG(pe_ratio) FROM stocks WHERE sector='Oil & Gas'")
Observation: avg_pe = 22.3
Thought: RELIANCE P/E (28.5) is above sector average (22.3), suggesting premium valuation.
Final Answer: RELIANCE trades at a P/E of 28.5, a 28% premium to the Oil & Gas sector average of 22.3.
```

The key insight: by making the LLM think out loud before acting, it makes better tool-use decisions. Without "Thought" steps, LLMs often call wrong tools or miss steps.

### Q3: What are the main types of agent memory?
**A:**
- **Working memory** — Current task variables and intermediate results (like CPU registers)
- **Short-term memory** — Conversation history within a session (like RAM)
- **Long-term memory** — Persistent knowledge across sessions, stored in vector DB or file (like disk)
- **Episodic memory** — Memories of past task executions: "Last time I analyzed RELIANCE, I used the PE approach and the user found it helpful"

In practice:
```python
# Short-term: message history
messages = [HumanMessage("Analyze TCS"), AIMessage("TCS PE is...")]

# Long-term: vector store
memory_store.add("User prefers technical analysis over fundamental")

# Episodic: task outcomes
episodes.add("2024-01-15: Stock analysis task succeeded using 3-step approach")
```

### Q4: What is tool calling and why is it important for agents?
**A:** Tool calling lets LLMs interact with the real world by invoking functions:

```python
# Define a tool
def get_stock_price(symbol: str) -> float:
    """Get real-time stock price from exchange."""
    return api.get_price(symbol)

# LLM decides to call it
# Input: "What's TCS trading at?"
# LLM output: {"tool": "get_stock_price", "args": {"symbol": "TCS"}}
# System executes tool, feeds result back to LLM
# LLM: "TCS is currently trading at ₹4200.50"
```

Without tools, LLMs can only use knowledge from training data (stale). With tools, they can access real-time data, execute calculations, and take actions.

### Q5: Name 3 popular agentic AI frameworks and their strengths.
**A:**

| Framework | Strength | Best For |
|-----------|----------|----------|
| **LangGraph** | Fine-grained control via state graphs | Complex workflows needing precise routing, checkpointing, human-in-the-loop |
| **CrewAI** | Simple role-based team abstraction | Business automation where you think in "teams" of specialists |
| **AutoGen** | Multi-agent conversation with code execution | Research, coding tasks, collaborative dialogue |

---

## Intermediate Level

### Q6: Compare single-agent vs multi-agent architectures. When do you use each?
**A:**

**Single Agent:**
- One LLM instance with multiple tools
- Simpler to debug and reason about
- Lower cost (fewer LLM calls)
- Best for: tasks within one domain, <5 tools

**Multi-Agent:**
- Multiple specialized LLM instances
- Each agent has domain-specific prompt and tools
- Can use different models per agent (GPT-4o for analysis, GPT-4o-mini for data gathering)
- Best for: cross-domain tasks, complex workflows, when specialization improves quality

```python
# Decision criteria
if num_tools <= 5 and single_domain:
    use_single_agent()
elif cross_domain or requires_different_expertise:
    use_multi_agent()
elif task_has_clear_pipeline_stages:
    use_multi_agent_with_sequential_process()
```

**Rule of thumb:** Start with single agent. Add agents only when quality degrades due to prompt complexity or tool overload.

### Q7: How do you handle agent failures and infinite loops?
**A:**

```python
class RobustAgent:
    MAX_ITERATIONS = 10
    MAX_TOOL_RETRIES = 3
    TIMEOUT = 120  # seconds

    def run(self, task: str) -> str:
        seen_actions = set()
        for i in range(self.MAX_ITERATIONS):
            action = self.think(task)

            # Detect loops
            action_key = f"{action.tool}:{action.args}"
            if action_key in seen_actions:
                return self.force_synthesize("Detected repeated action")
            seen_actions.add(action_key)

            # Execute with retry
            for retry in range(self.MAX_TOOL_RETRIES):
                try:
                    result = self.execute_tool(action, timeout=30)
                    break
                except TimeoutError:
                    if retry == self.MAX_TOOL_RETRIES - 1:
                        return self.force_synthesize("Tool timeout")
                except Exception as e:
                    self.add_observation(f"Tool error: {e}")

            if self.is_task_complete(result):
                return self.synthesize()

        return self.force_synthesize("Max iterations reached")
```

Key strategies:
1. **Max iterations** — Hard cap on reasoning loops
2. **Action deduplication** — Detect repeated tool calls
3. **Timeout per tool** — No tool runs forever
4. **Retry with backoff** — Transient failures get retried
5. **Force synthesize** — Always produce some output, even if incomplete

### Q8: Explain the plan-and-execute agent pattern.
**A:** Separates planning from execution:

```python
# Step 1: Planner creates a plan
planner_prompt = """
Given this goal: {goal}
Create a step-by-step plan. Each step should be a specific, actionable task.
"""
plan = planner_llm.invoke(planner_prompt.format(goal=user_goal))
# Output:
# 1. Query NIFTY 50 constituent list
# 2. Fetch last 30 days OHLCV for each stock
# 3. Calculate RSI and MACD indicators
# 4. Rank stocks by momentum score
# 5. Generate top 10 recommendations

# Step 2: Executor runs each step
for step in plan.steps:
    result = executor_agent.run(step)
    update_state(step, result)

    # Optional: Replan if step fails
    if result.failed:
        plan = replanner.invoke(
            f"Step '{step}' failed with: {result.error}. "
            f"Revise the remaining plan."
        )
```

**Advantages over pure ReAct:**
- Better for long tasks (10+ step)
- Planner uses a powerful model (GPT-4o), executor can use cheaper model
- Can checkpoint and resume mid-plan
- Easier to show progress to users

### Q9: How do you implement human-in-the-loop for agentic systems?
**A:**

```python
# LangGraph approach
from langgraph.graph import StateGraph
from langgraph.checkpoint.memory import MemorySaver

def should_approve(state):
    """Route to human approval for high-risk actions."""
    if state["action_type"] in ["place_order", "delete_data", "send_email"]:
        return "human_review"
    return "auto_execute"

graph = StateGraph(AgentState)
graph.add_node("analyze", analyze_node)
graph.add_node("propose_action", propose_node)
graph.add_node("human_review", human_review_node)  # Interrupt here
graph.add_node("auto_execute", execute_node)

graph.add_conditional_edges("propose_action", should_approve)

# Compile with checkpointing
app = graph.compile(
    checkpointer=MemorySaver(),
    interrupt_before=["human_review"],  # Pause here
)

# Run until interrupt
result = app.invoke(input, config={"configurable": {"thread_id": "1"}})
# Agent pauses at human_review node

# Human approves
app.update_state(config, {"approved": True})
result = app.invoke(None, config)  # Resume
```

### Q10: What is the Model Context Protocol (MCP) and why does it matter?
**A:** MCP is an **open standard** (by Anthropic) that standardizes how AI agents discover and use tools:

**Before MCP:** Every framework had its own tool format — LangChain tools, OpenAI function calling, AutoGen tools. Building a tool meant implementing it N times.

**With MCP:** One tool implementation works everywhere. Like USB for AI tools.

| Component | Role |
|-----------|------|
| MCP Server | Exposes tools and resources (like a plugin) |
| MCP Client | Connects agents to servers (built into Claude, Copilot, etc.) |
| Transport | stdio, HTTP SSE, WebSocket |

```python
# MCP Server — write once
@server.tool("query_stocks")
async def query_stocks(sector: str) -> str:
    """Query stocks by sector."""
    return await db.query(f"SELECT * FROM stocks WHERE sector='{sector}'")

# Works with: Claude Desktop, VS Code Copilot, any MCP client
```

---

## Advanced Level

### Q11: Design an autonomous trading research agent system.
**A:**

```python
class TradingResearchSystem:
    """Multi-agent system for autonomous trading research."""

    def __init__(self):
        self.agents = {
            "data": DataAgent(
                tools=[bq_query, kite_api, nse_scraper],
                llm="gpt-4o-mini",  # Cheap for data fetching
            ),
            "quant": QuantAgent(
                tools=[stats_calculator, backtest_engine],
                llm="gpt-4o",  # Smart for analysis
            ),
            "risk": RiskAgent(
                tools=[var_calculator, sebi_validator],
                llm="gpt-4o",  # Critical decisions
            ),
            "narrator": NarratorAgent(
                tools=[chart_generator, pdf_writer],
                llm="gpt-4o-mini",  # Cheap for writing
            ),
        }
        self.supervisor = SupervisorAgent(llm="gpt-4o")

    async def research(self, universe: list[str]) -> Report:
        # Phase 1: Data collection (parallel)
        data_tasks = [
            self.agents["data"].fetch_ohlcv(sym) for sym in universe
        ]
        market_data = await asyncio.gather(*data_tasks)

        # Phase 2: Quantitative analysis
        signals = await self.agents["quant"].analyze(market_data)

        # Phase 3: Risk assessment (blocking)
        approved = await self.agents["risk"].validate(
            signals, portfolio_state
        )

        # Phase 4: Supervisor review
        decision = await self.supervisor.review(approved)
        if decision.needs_revision:
            # Send back to quant with feedback
            signals = await self.agents["quant"].revise(
                signals, decision.feedback
            )

        # Phase 5: Report generation
        report = await self.agents["narrator"].generate_report(
            signals=approved, data=market_data
        )
        return report
```

### Q12: How do you evaluate agentic system quality?
**A:**

| Metric | Measures | How |
|--------|----------|-----|
| **Task completion rate** | Does agent finish the task? | Run 100 tasks, count successes |
| **Accuracy** | Are results correct? | Compare against gold answers |
| **Efficiency** | How many steps/tokens? | Count LLM calls, tool calls |
| **Cost** | Dollar cost per task | Track API costs per run |
| **Latency** | End-to-end time | Wall clock time |
| **Robustness** | Handles edge cases? | Adversarial inputs, empty results |
| **Safety** | Avoids harmful actions? | Red-team with attack scenarios |

```python
class AgentEvaluator:
    def evaluate(self, agent, test_suite):
        results = []
        for case in test_suite:
            start = time.time()
            output = agent.run(case.input)
            duration = time.time() - start

            results.append({
                "task": case.name,
                "correct": self.check_answer(output, case.expected),
                "steps": output.step_count,
                "tokens": output.total_tokens,
                "cost": output.total_cost,
                "latency": duration,
                "tools_used": output.tools_called,
            })
        return pd.DataFrame(results).describe()
```

### Q13: How do you handle state management in long-running agents?
**A:** Long-running agents (hours/days) need durable state:

```python
# LangGraph checkpointing
from langgraph.checkpoint.postgres import PostgresSaver

checkpointer = PostgresSaver(connection_string)
app = graph.compile(checkpointer=checkpointer)

# Run resumes from last checkpoint on crash
config = {"configurable": {"thread_id": "research-2025-01"}}
result = app.invoke(input, config)

# Later: query state
state = app.get_state(config)
print(f"Current step: {state.values['current_step']}")
print(f"Completed: {state.values['completed_tasks']}")
```

Key patterns:
1. **Checkpoint after every tool call** — Never lose work
2. **Idempotent tool execution** — Re-running a tool should be safe
3. **State serialization** — All state must be JSON-serializable
4. **Garbage collection** — Prune old checkpoints to save storage
5. **Concurrent access** — Lock state during writes if multiple agents share state

### Q14: Compare the supervisor, hierarchical, and swarm multi-agent patterns.
**A:**

| Pattern | Controller | Best For | Risk |
|---------|-----------|----------|------|
| **Supervisor** | LLM routes to agents | Dynamic task distribution | Supervisor is bottleneck |
| **Hierarchical** | Manager delegates down | Clear org structures | Deep hierarchies add latency |
| **Swarm** | Agents hand off to each other | Customer support flows | Can loop without termination |

```python
# Supervisor: Central router
def supervisor(state):
    next_agent = llm.invoke(
        f"Given task '{state['task']}' and progress so far, "
        f"which agent should act next? Options: {agent_names}"
    )
    return next_agent

# Hierarchical: Manager-worker
manager → [researcher, analyst, writer]
manager decides task assignment, reviews results

# Swarm: Peer-to-peer handoffs
triage_agent → billing_agent (if billing issue)
triage_agent → tech_agent (if tech issue)
billing_agent → triage_agent (if needs escalation)
```

Choose **supervisor** when tasks are diverse and routing logic is complex. Choose **hierarchical** when there is a clear approval chain. Choose **swarm** when agents are peers with domain expertise and natural handoff points.
