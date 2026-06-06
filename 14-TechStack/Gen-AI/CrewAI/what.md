# CrewAI: Complete Guide

## 1. What is CrewAI?

CrewAI is a **role-based multi-agent orchestration framework** that models AI teams as real-world organizational units — agents with **roles**, **goals**, and **backstories** collaborate on structured **tasks** using defined **processes** (sequential, hierarchical, or consensual). Built for production use with built-in memory, tool integration, and the CrewAI Enterprise platform.

**Core Philosophy:** "AI agents work best when organized like expert teams with clear responsibilities."

**Key differentiator vs AutoGen/LangGraph:** CrewAI focuses on **declarative role definition** — you describe WHO agents are and WHAT they do, not HOW messages flow. The framework handles orchestration.

---

## 2. Core Concepts

### Agents
Autonomous units with:
- **Role:** Senior Data Analyst, QA Engineer, Technical Writer
- **Goal:** What they aim to achieve
- **Backstory:** Context shaping personality and approach
- **Tools:** Functions the agent can call
- **LLM:** Which model backs the agent

### Tasks
Units of work assigned to agents:
- **Description:** What needs to be done
- **Expected output:** Format/content of the result
- **Agent:** Who performs this task
- **Context:** Output from prior tasks fed as input
- **Tools:** Task-specific tool overrides

### Crews
Teams of agents executing tasks:
- **Agents:** List of agent members
- **Tasks:** Ordered list of work items
- **Process:** Execution strategy (sequential, hierarchical)
- **Memory:** Shared knowledge across tasks

### Processes
- **Sequential:** Tasks run in order, output chains to next
- **Hierarchical:** Manager agent delegates to workers
- **Consensual:** (Experimental) Agents vote on decisions

### Flows
Multi-crew orchestration with:
- **@start, @listen, @router** decorators
- Event-driven connections between crews
- Conditional branching and state management

---

## 3. Key Features

| Feature | Description |
|---------|-------------|
| Role-Based Agents | Agents defined by role, goal, backstory |
| Built-in Memory | Short-term, long-term, entity memory |
| Tool Integration | 60+ built-in tools (search, scrape, file, DB) |
| Delegation | Agents can delegate tasks to each other |
| Human-in-the-Loop | `human_input=True` for approval gates |
| Guardrails | Output validation and retry logic |
| Flows | Multi-crew orchestration with event routing |
| CrewAI Enterprise | Cloud platform with monitoring, deployment |
| Async Support | Parallel task execution |
| Training | Improve agent performance via training data |
| Testing | Built-in testing and benchmarking |

---

## 4. Installation

```bash
# Install CrewAI
pip install crewai

# Install with tools
pip install 'crewai[tools]'

# Create new project (recommended)
crewai create crew my_project
cd my_project

# Project structure
# my_project/
# ├── src/my_project/
# │   ├── config/
# │   │   ├── agents.yaml    # Agent definitions
# │   │   └── tasks.yaml     # Task definitions
# │   ├── crew.py             # Crew orchestration
# │   ├── main.py             # Entry point
# │   └── tools/              # Custom tools
# ├── pyproject.toml
# └── README.md
```

---

## 5. Beginner Examples

### Simple Research Crew

```python
from crewai import Agent, Task, Crew, Process

# Define agents
researcher = Agent(
    role="Senior Research Analyst",
    goal="Find comprehensive information about {topic}",
    backstory="You are an expert researcher with 20 years of experience "
              "in finding and synthesizing information from diverse sources.",
    verbose=True,
    allow_delegation=False,
)

writer = Agent(
    role="Technical Content Writer",
    goal="Write clear, engaging content based on research findings",
    backstory="You are an award-winning technical writer who excels at "
              "making complex topics accessible to broad audiences.",
    verbose=True,
    allow_delegation=False,
)

# Define tasks
research_task = Task(
    description="Research {topic} thoroughly. Cover key concepts, "
                "recent developments, and practical applications.",
    expected_output="A detailed research report with key findings, "
                    "statistics, and cited sources.",
    agent=researcher,
)

write_task = Task(
    description="Write a comprehensive article about {topic} based on "
                "the research findings. Make it engaging and informative.",
    expected_output="A well-structured article of 800-1000 words with "
                    "introduction, body sections, and conclusion.",
    agent=writer,
    context=[research_task],  # Gets output from research_task
)

# Create and run crew
crew = Crew(
    agents=[researcher, writer],
    tasks=[research_task, write_task],
    process=Process.sequential,
    verbose=True,
)

result = crew.kickoff(inputs={"topic": "AI in Healthcare 2025"})
print(result)
```

### Using YAML Configuration (Recommended)

```yaml
# config/agents.yaml
researcher:
  role: "Senior Research Analyst"
  goal: "Find comprehensive information about {topic}"
  backstory: "Expert researcher with deep analytical skills."

writer:
  role: "Technical Writer"
  goal: "Create engaging articles from research"
  backstory: "Award-winning writer who simplifies complex topics."
```

```yaml
# config/tasks.yaml
research_task:
  description: "Research {topic} covering key concepts and trends."
  expected_output: "Detailed research report with findings."
  agent: researcher

writing_task:
  description: "Write article about {topic} from research."
  expected_output: "800-word structured article."
  agent: writer
  context:
    - research_task
```

```python
# crew.py
from crewai import Agent, Crew, Process, Task
from crewai.project import CrewBase, agent, crew, task

@CrewBase
class MyResearchCrew:
    agents_config = "config/agents.yaml"
    tasks_config = "config/tasks.yaml"

    @agent
    def researcher(self) -> Agent:
        return Agent(config=self.agents_config["researcher"])

    @agent
    def writer(self) -> Agent:
        return Agent(config=self.agents_config["writer"])

    @task
    def research_task(self) -> Task:
        return Task(config=self.tasks_config["research_task"])

    @task
    def writing_task(self) -> Task:
        return Task(config=self.tasks_config["writing_task"])

    @crew
    def crew(self) -> Crew:
        return Crew(
            agents=self.agents,
            tasks=self.tasks,
            process=Process.sequential,
            verbose=True,
        )
```

---

## 6. Intermediate Patterns

### Tool Integration

```python
from crewai import Agent, Task, Crew
from crewai.tools import tool
from crewai_tools import SerperDevTool, ScrapeWebsiteTool

# Built-in tools
search_tool = SerperDevTool()
scrape_tool = ScrapeWebsiteTool()

# Custom tool
@tool("Calculate ROI")
def calculate_roi(investment: float, returns: float) -> str:
    """Calculate Return on Investment percentage."""
    roi = ((returns - investment) / investment) * 100
    return f"ROI: {roi:.2f}%"

analyst = Agent(
    role="Financial Analyst",
    goal="Analyze investment opportunities",
    backstory="Expert financial analyst with CFA certification.",
    tools=[search_tool, scrape_tool, calculate_roi],
)
```

### Hierarchical Process (Manager Delegation)

```python
from crewai import Agent, Crew, Process
from langchain_openai import ChatOpenAI

manager_llm = ChatOpenAI(model="gpt-4o")

crew = Crew(
    agents=[researcher, analyst, writer],
    tasks=[research_task, analysis_task, write_task],
    process=Process.hierarchical,
    manager_llm=manager_llm,  # Manager created automatically
    verbose=True,
)
# Manager decides which agent handles each task
# and can split/reassign work dynamically
```

### Memory Systems

```python
crew = Crew(
    agents=[researcher, analyst],
    tasks=[task1, task2],
    memory=True,  # Enable all memory types
    # Short-term: conversation context within a run
    # Long-term: learnings across multiple runs
    # Entity: facts about specific entities (people, companies)
    verbose=True,
)
```

### Structured Output

```python
from pydantic import BaseModel
from typing import List

class InvestmentReport(BaseModel):
    company: str
    recommendation: str  # BUY, HOLD, SELL
    target_price: float
    risk_factors: List[str]
    confidence: float

analysis_task = Task(
    description="Analyze {company} stock and provide recommendation.",
    expected_output="Investment recommendation with target price.",
    agent=analyst,
    output_pydantic=InvestmentReport,
)

result = crew.kickoff(inputs={"company": "RELIANCE"})
report: InvestmentReport = result.pydantic
print(f"Rec: {report.recommendation}, Target: ₹{report.target_price}")
```

### Human-in-the-Loop

```python
review_task = Task(
    description="Review the analysis and provide final recommendation.",
    expected_output="Approved or revised recommendation.",
    agent=reviewer,
    human_input=True,  # Pauses for human approval
)
```

---

## 7. Advanced Patterns

### Flows (Multi-Crew Orchestration)

```python
from crewai.flow.flow import Flow, listen, start, router

class InvestmentFlow(Flow):
    @start()
    def gather_data(self):
        """First step: collect market data."""
        result = DataGatherCrew().crew().kickoff(
            inputs={"symbols": self.state.symbols}
        )
        self.state.market_data = result.raw

    @listen(gather_data)
    def analyze(self):
        """Triggered after data gathering."""
        result = AnalysisCrew().crew().kickoff(
            inputs={"data": self.state.market_data}
        )
        self.state.analysis = result.raw

    @router(analyze)
    def decide_action(self):
        """Route based on analysis outcome."""
        if "BUY" in self.state.analysis:
            return "execute_buy"
        elif "SELL" in self.state.analysis:
            return "execute_sell"
        return "hold"

    @listen("execute_buy")
    def place_buy_order(self):
        ExecutionCrew().crew().kickoff(
            inputs={"action": "BUY", "data": self.state.analysis}
        )

    @listen("execute_sell")
    def place_sell_order(self):
        ExecutionCrew().crew().kickoff(
            inputs={"action": "SELL", "data": self.state.analysis}
        )

    @listen("hold")
    def log_hold(self):
        print("No action taken — HOLD position.")

# Run the flow
flow = InvestmentFlow()
flow.kickoff(inputs={"symbols": ["RELIANCE", "TCS", "INFY"]})
```

### Async Parallel Tasks

```python
import asyncio

# Tasks with async_execution run in parallel
task_a = Task(
    description="Research company A",
    agent=researcher,
    async_execution=True,
)
task_b = Task(
    description="Research company B",
    agent=researcher,
    async_execution=True,
)
# This task waits for both async tasks
summary = Task(
    description="Summarize both companies",
    agent=writer,
    context=[task_a, task_b],  # Waits for both
)

crew = Crew(
    agents=[researcher, writer],
    tasks=[task_a, task_b, summary],
    process=Process.sequential,
)
```

### Training and Testing

```python
# Train the crew on examples
crew.train(
    n_iterations=5,
    filename="training_data.pkl",
    inputs={"topic": "AI regulation"},
)

# Test crew performance
crew.test(
    n_iterations=3,
    inputs={"topic": "Quantum computing"},
)
# Outputs metrics: task completion, quality scores, latency
```

### Agent Delegation

```python
researcher = Agent(
    role="Lead Researcher",
    goal="Coordinate research across team",
    backstory="Senior researcher who delegates effectively.",
    allow_delegation=True,  # Can ask other agents for help
)

junior = Agent(
    role="Junior Researcher",
    goal="Assist with data collection",
    backstory="Eager researcher focused on data gathering.",
    allow_delegation=False,
)
```

---

## 8. Best Practices

| Practice | Why |
|----------|-----|
| Use YAML configs for agents/tasks | Separates config from logic, easier to iterate |
| Keep backstories specific | Vague backstories produce vague outputs |
| Chain tasks via `context` | Explicit data flow between tasks |
| Use `output_pydantic` for structured data | Type-safe, validated outputs |
| Set `verbose=True` during development | See agent reasoning and tool calls |
| Use Flows for complex workflows | Better than nesting crews manually |
| Enable memory for multi-run systems | Agents improve over time |
| Use `human_input=True` for critical decisions | Safety gate before actions |

---

## 9. Common Pitfalls

| Pitfall | Solution |
|---------|----------|
| Agent does not use tools | Ensure tool descriptions are clear; verify tool is in agent's tool list |
| Tasks produce inconsistent output | Use `output_pydantic` to enforce structure |
| Hierarchical process loops | Set `max_iter` on agents; provide clear task descriptions |
| Context not flowing between tasks | Explicitly set `context=[prior_task]` |
| Memory slowing down runs | Disable memory for one-shot tasks |
| Agent hallucinating tool names | Use `@tool` decorator with clear docstrings |
| LLM rate limits in big crews | Use `max_rpm` on agents to throttle |

---

## 10. CrewAI vs Alternatives

| Feature | CrewAI | AutoGen | LangGraph |
|---------|--------|---------|-----------|
| Paradigm | Role-based crews | Conversation-based | Graph-based state machines |
| Agent Definition | Role + Goal + Backstory | System message | Node function |
| Orchestration | Process (seq/hier) | GroupChat | StateGraph edges |
| Learning Curve | Low | Medium | High |
| Tool Integration | 60+ built-in | Function calling | LangChain tools |
| Memory | Built-in (3 types) | Manual | Checkpointer |
| Production | CrewAI Enterprise | AutoGen Studio | LangGraph Platform |
| Flow Control | Flows (decorators) | Swarm handoffs | Conditional edges |
| Best For | Business workflows | Code generation | Complex state machines |

---

## 11. Real-World Use Cases

1. **Automated Report Generation** — Research crew gathers data, analysis crew processes it, writing crew produces report
2. **Customer Support Triage** — Triage agent routes to billing, tech support, or account specialist crews
3. **Code Review Pipeline** — Developer agent writes code, reviewer agent checks quality, security agent scans vulnerabilities
4. **Market Research** — Competitor analysis crew, trend analysis crew, and synthesis crew collaborate via Flows
5. **Content Marketing** — SEO researcher, content strategist, writer, and editor as a sequential crew

---

## 12. Performance Considerations

- **LLM Costs:** Each agent turn = 1 LLM call. Minimize unnecessary delegation.
- **Token Usage:** Long backstories and contexts consume tokens. Keep them focused.
- **Parallelism:** Use `async_execution=True` for independent tasks.
- **Caching:** CrewAI caches tool results by default. Disable for real-time data: `cache=False`.
- **Rate Limits:** Set `max_rpm` per agent to avoid API throttling.
- **Memory DB:** Long-term memory uses embeddings — costs scale with run count.
