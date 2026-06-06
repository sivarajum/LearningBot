# AutoGen Interview Questions and Answers

## Beginner Level Questions

### Q1: What is AutoGen and what problem does it solve?

**Answer:**

AutoGen is Microsoft's open-source framework for building multi-agent AI applications. It enables multiple AI agents to converse, collaborate, use tools, and execute code to solve complex tasks.

**Key components (v0.4+):**
- **AgentChat**: High-level multi-agent conversation patterns
- **Core**: Event-driven agent runtime
- **Extensions**: OpenAI, Docker, MCP, gRPC integrations

```python
import asyncio
from autogen_agentchat.agents import AssistantAgent
from autogen_ext.models.openai import OpenAIChatCompletionClient

async def main():
    agent = AssistantAgent("assistant", OpenAIChatCompletionClient(model="gpt-4o"))
    print(await agent.run(task="Say 'Hello World!'"))

asyncio.run(main())
```

---

### Q2: What are the main conversation patterns in AutoGen?

**Answer:**

| Pattern | Class | How It Works |
|---------|-------|-------------|
| **Round Robin** | `RoundRobinGroupChat` | Agents take turns in fixed order |
| **Selector** | `SelectorGroupChat` | LLM decides which agent speaks next |
| **Swarm** | `Swarm` | Agents hand off to each other dynamically |
| **Two-Agent** | Direct `run()` | Simple back-and-forth between 2 agents |

---

### Q3: How do termination conditions work?

**Answer:**

Termination conditions define when agent conversations stop:

```python
from autogen_agentchat.conditions import (
    TextMentionTermination,    # Agent says specific text
    MaxMessageTermination,     # After N messages
    TokenUsageTermination,     # After token budget exhausted
)

# Combine with OR (|) or AND (&)
stop = TextMentionTermination("APPROVED") | MaxMessageTermination(20)
```

---

### Q4: How does code execution work in AutoGen?

**Answer:**

AutoGen provides sandboxed code execution via Docker:

```python
from autogen_ext.code_executors.docker import DockerCommandLineCodeExecutor
from autogen_agentchat.agents import CodeExecutorAgent

executor = DockerCommandLineCodeExecutor(
    image="python:3.12-slim",
    timeout=60,
)

agent = CodeExecutorAgent("executor", code_executor=executor)
# Agent receives code blocks → executes in Docker → returns output
```

---

## Intermediate Level Questions

### Q5: Explain the Swarm pattern and when to use it.

**Answer:**

Swarm enables **dynamic handoffs** between agents — each agent can transfer control to another based on conversation context.

```python
from autogen_agentchat.teams import Swarm

triage = AssistantAgent("triage", model_client=model,
    system_message="Route: 'billing' for payments, 'tech' for technical.",
    handoffs=["billing", "tech"])

billing = AssistantAgent("billing", model_client=model,
    system_message="Handle billing. Handoff to 'triage' if not billing.",
    handoffs=["triage"])

tech = AssistantAgent("tech", model_client=model,
    system_message="Handle tech support.",
    handoffs=["triage"])

team = Swarm([triage, billing, tech],
    termination_condition=MaxMessageTermination(15))
```

**Use when:** Customer support routing, multi-department workflows, dynamic task delegation.

---

### Q6: How do you add custom tools to agents?

**Answer:**

Tools are Python functions with type annotations and docstrings:

```python
def calculate_mortgage(principal: float, rate: float, years: int) -> str:
    """Calculate monthly mortgage payment.

    Args:
        principal: Loan amount in dollars
        rate: Annual interest rate (e.g., 0.05 for 5%)
        years: Loan term in years
    """
    monthly_rate = rate / 12
    n_payments = years * 12
    payment = principal * (monthly_rate * (1 + monthly_rate)**n_payments) / \
              ((1 + monthly_rate)**n_payments - 1)
    return f"Monthly payment: ${payment:,.2f}"

agent = AssistantAgent(
    "financial_advisor",
    model_client=model,
    system_message="Use the calculate_mortgage tool for loan calculations.",
    tools=[calculate_mortgage],
)
```

---

### Q7: How does SelectorGroupChat route to the right agent?

**Answer:**

SelectorGroupChat uses an LLM to decide which agent should speak next based on conversation history:

```python
from autogen_agentchat.teams import SelectorGroupChat

team = SelectorGroupChat(
    participants=[researcher, analyst, writer],
    model_client=model,  # This LLM does the routing
    termination_condition=MaxMessageTermination(12),
    selector_prompt="""Select the next speaker based on the conversation.
    - researcher: when facts or data are needed
    - analyst: when data needs interpretation
    - writer: when a report needs to be written
    Return only the agent name.""",
)
```

---

## Advanced Level Questions

### Q8: How do you build distributed multi-agent systems with AutoGen Core?

**Answer:**

AutoGen Core provides an event-driven runtime with gRPC for distributed agents:

```python
# Worker node (separate machine)
from autogen_ext.runtimes.grpc import GrpcWorkerAgentRuntime

runtime = GrpcWorkerAgentRuntime(host_address="worker1:50051")
await runtime.register("research_agent", lambda: ResearchAgent())
runtime.start()

# Orchestrator
from autogen_core import SingleThreadedAgentRuntime
runtime = SingleThreadedAgentRuntime()
# Publish messages — agents react to topics
await runtime.publish_message(
    ResearchRequest(query="quantum computing"),
    topic_id=TopicId("research", "default"),
)
```

---

### Q9: How do you implement human-in-the-loop with AutoGen?

**Answer:**

```python
from autogen_agentchat.agents import AssistantAgent
from autogen_agentchat.conditions import HandoffTermination
from autogen_agentchat.teams import Swarm

# Agent requests human approval before actions
agent = AssistantAgent(
    "trader",
    model_client=model,
    system_message="Analyze trades. Before executing, handoff to 'human' for approval.",
    handoffs=["human"],
)

# Human proxy
from autogen_agentchat.agents import UserProxyAgent
human = UserProxyAgent("human")

team = Swarm([agent, human],
    termination_condition=HandoffTermination(target="human") | MaxMessageTermination(20))
```

---

### Q10: How does AutoGen compare to CrewAI for production systems?

**Answer:**

| Aspect | AutoGen | CrewAI |
|--------|---------|--------|
| **Architecture** | Event-driven, async | Sequential/hierarchical processes |
| **Code Execution** | ✅ Docker sandbox | ❌ No built-in |
| **Distributed** | ✅ gRPC runtime | ❌ Single process |
| **No-code UI** | ✅ AutoGen Studio | ❌ |
| **Ease of use** | Moderate (async Python) | Easy (declarative) |
| **Enterprise** | Microsoft-backed | Startup |
| **MCP Support** | ✅ Native | Via tools |
| **Best for** | Research, complex workflows | Business automation |

---

## Advanced Level (5 Additional Q&As)

### Q11: How do you implement a multi-agent trading research system with AutoGen?
**Answer:**

```python
from autogen_agentchat.agents import AssistantAgent
from autogen_agentchat.teams import RoundRobinGroupChat

# 1. Technical Analyst Agent
tech_analyst = AssistantAgent(
    "technical_analyst",
    model_client=model,
    system_message="""Analyze OHLCV data for NSE stocks.
    Compute RSI, MACD, Bollinger Bands. Output BUY/SELL/HOLD with confidence.""",
    tools=[fetch_ohlcv, compute_indicators],
)

# 2. Fundamental Analyst Agent
fundamental = AssistantAgent(
    "fundamental_analyst",
    model_client=model,
    system_message="Analyze earnings, P/E, debt ratios. Focus on NIFTY 50 stocks.",
    tools=[fetch_financials, sector_comparison],
)

# 3. Risk Manager Agent (has veto power)
risk_manager = AssistantAgent(
    "risk_manager",
    model_client=model,
    system_message="""Evaluate proposed trades against:
    - SEBI 5% per-stock limit
    - 25% sector exposure limit
    - Max drawdown 20% circuit breaker
    VETO any trade that violates limits.""",
    tools=[check_portfolio_exposure, check_sebi_compliance],
)

# Orchestrate: each agent contributes, risk manager validates
team = RoundRobinGroupChat(
    [tech_analyst, fundamental, risk_manager],
    max_turns=6,
)
result = await team.run(task="Evaluate RELIANCE.NSE for a swing trade position")
```

### Q12: Explain AutoGen's event-driven architecture and how it differs from v0.2.
**Answer:**

**AutoGen v0.4 (current) — Event-Driven:**
- Built on `autogen-core` with async message passing
- Agents communicate via typed messages (not just strings)
- Runtime manages agent lifecycle, routing, and serialization
- Supports distributed execution (gRPC transport)
- Topic-based pub/sub for broadcast patterns

**AutoGen v0.2 (legacy) — Conversational:**
- Agents had `initiate_chat()` — synchronous, blocking
- `GroupChat` manager passed messages sequentially
- No distributed support, single-process only
- Everything was a string message

**Migration key:** v0.2 `ConversableAgent` → v0.4 `AssistantAgent` + explicit message types + async/await everywhere.

### Q13: How do you implement tool use with error recovery in AutoGen?
**Answer:**

```python
from autogen_core import FunctionTool

# Define tool with validation
async def place_order(symbol: str, qty: int, side: str) -> str:
    """Place an order on NSE. Args: symbol (e.g. RELIANCE), qty (lot size), side (BUY/SELL)"""
    if qty > 1000:
        raise ValueError(f"Qty {qty} exceeds single-order limit")
    # ... execute via Kite API
    return f"Order placed: {side} {qty} {symbol}"

tool = FunctionTool(place_order, description="Place NSE trade order")

# Agent with retry behavior
agent = AssistantAgent(
    "executor",
    model_client=model,
    tools=[tool],
    system_message="""Execute trades. If a tool call fails:
    1. Parse the error message
    2. Adjust parameters (reduce qty, check symbol)
    3. Retry with corrected params
    Never retry more than 3 times.""",
)
```

AutoGen automatically handles: tool schema generation, argument parsing, error message routing back to the agent, and reflection on failures.

### Q14: How do you implement state persistence and checkpointing in AutoGen teams?
**Answer:**

AutoGen v0.4 supports state save/load:

```python
# Save team state (all agent memories + conversation history)
state = await team.save_state()
with open("checkpoint.json", "w") as f:
    json.dump(state, f)

# Restore from checkpoint (resume after crash)
with open("checkpoint.json") as f:
    state = json.load(f)
await team.load_state(state)
await team.run(task="Continue previous analysis...")
```

For production:
- Save checkpoints to GCS/Firestore after each significant step
- Use idempotency keys to prevent duplicate tool executions on resume
- Version state schemas for backward compatibility

### Q15: Design a production AutoGen deployment for real-time market monitoring.
**Answer:**

```
Architecture:
┌──────────────┐    ┌──────────────┐    ┌──────────────┐
│ Data Agent    │    │ Signal Agent │    │ Alert Agent  │
│ (WebSocket)  │───▶│ (Analysis)   │───▶│ (Telegram)   │
└──────────────┘    └──────────────┘    └──────────────┘
       │                    │                    │
       └────────────────────┴────────────────────┘
                    ▼
           ┌──────────────┐
           │ Risk Guardian │  (veto power, always listening)
           └──────────────┘

Deployment:
- Runtime: autogen-core DistributedRuntime on Cloud Run
- Transport: gRPC between agents (low latency)
- State: Firestore (agent memory) + BigQuery (audit log)
- Scale: Each agent = separate container, independent scaling
- Monitoring: OpenTelemetry traces for agent interactions

Key considerations:
1. Data Agent streams Kite WebSocket → publishes price events
2. Signal Agent subscribes → generates signals within 100ms
3. Risk Guardian intercepts ALL tool calls → validates SEBI compliance
4. Alert Agent → Telegram notification with confidence + reasoning
5. All decisions logged to BigQuery for audit trail (8yr retention)
```
