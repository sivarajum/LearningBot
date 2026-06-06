# CrewAI: Interview Questions & Answers

## Beginner Level

### Q1: What is CrewAI and how does it differ from single-agent systems?
**A:** CrewAI is a multi-agent orchestration framework where AI agents are modeled as team members with **roles**, **goals**, and **backstories**. Unlike single-agent systems where one LLM handles everything, CrewAI distributes work across specialized agents — a researcher gathers data, an analyst processes it, and a writer produces output. This role-based approach mirrors human team dynamics and produces more focused, higher-quality results.

### Q2: Explain the core components: Agent, Task, Crew, Process.
**A:**
- **Agent** — An autonomous AI team member defined by role (job title), goal (objective), and backstory (context). Has tools and an LLM.
- **Task** — A specific unit of work with a description, expected output, and assigned agent. Tasks can reference prior task outputs via `context`.
- **Crew** — A team of agents organized to execute tasks. Configured with a process type and optional memory.
- **Process** — The execution strategy: `sequential` (tasks run in order), `hierarchical` (manager delegates), or `consensual` (agents vote).

```python
crew = Crew(
    agents=[researcher, writer],
    tasks=[research_task, write_task],
    process=Process.sequential,
)
result = crew.kickoff(inputs={"topic": "AI trends"})
```

### Q3: How do you create a custom tool in CrewAI?
**A:** Use the `@tool` decorator:

```python
from crewai.tools import tool

@tool("Stock Price Lookup")
def get_stock_price(symbol: str) -> str:
    """Fetches the current stock price for a given ticker symbol."""
    # In production, call a real API
    prices = {"RELIANCE": 2850.50, "TCS": 4200.75}
    price = prices.get(symbol, "Unknown")
    return f"{symbol}: ₹{price}"

analyst = Agent(
    role="Stock Analyst",
    goal="Analyze stock performance",
    tools=[get_stock_price],
)
```

The tool's docstring is critical — the LLM uses it to decide when to call the tool.

### Q4: What is the recommended project structure for CrewAI?
**A:** Use `crewai create crew project_name` which scaffolds:

```
project_name/
├── src/project_name/
│   ├── config/
│   │   ├── agents.yaml    # Agent definitions (role, goal, backstory)
│   │   └── tasks.yaml     # Task definitions (description, expected_output)
│   ├── crew.py            # @CrewBase class connecting agents + tasks
│   ├── main.py            # Entry point
│   └── tools/             # Custom tools
├── pyproject.toml
└── tests/
```

YAML configs separate agent/task definitions from orchestration logic, making it easy to iterate on prompts without touching code.

### Q5: How does task context chaining work?
**A:** The `context` parameter feeds the output of prior tasks as input:

```python
research = Task(
    description="Research {company}",
    expected_output="Research report",
    agent=researcher,
)
analysis = Task(
    description="Analyze the research findings",
    expected_output="Investment recommendation",
    agent=analyst,
    context=[research],  # Gets research output as context
)
```

In sequential process, tasks run in order and each task automatically receives prior outputs. Explicit `context` gives you control over which specific outputs are included.

---

## Intermediate Level

### Q6: Compare sequential vs hierarchical process. When do you use each?
**A:**

**Sequential:**
- Tasks execute in defined order
- Output of each task feeds into the next
- Deterministic flow — same order every run
- Best for: linear workflows (research → analyze → write)

**Hierarchical:**
- A manager agent (auto-created or custom) orchestrates
- Manager decides which agent handles each task
- Can dynamically reassign or split work
- Requires `manager_llm` parameter
- Best for: complex workflows where task routing depends on intermediate results

```python
# Hierarchical
crew = Crew(
    agents=[researcher, analyst, writer],
    tasks=[complex_task],
    process=Process.hierarchical,
    manager_llm=ChatOpenAI(model="gpt-4o"),
)
```

Use **sequential** for predictable pipelines. Use **hierarchical** when the optimal agent assignment depends on the content being processed.

### Q7: Explain CrewAI's memory system types and when to use each.
**A:** CrewAI has three memory types:

| Type | Scope | Persistence | Use Case |
|------|-------|-------------|----------|
| **Short-term** | Within a single run | Transient | Task context within the current crew execution |
| **Long-term** | Across multiple runs | Persistent (SQLite) | Learning from past successes/failures |
| **Entity** | Across runs | Persistent | Facts about specific entities (people, companies) |

```python
crew = Crew(
    agents=agents,
    tasks=tasks,
    memory=True,              # Enable all memory types
    # Or configure individually:
    # short_term_memory=True,
    # long_term_memory=True,
    # entity_memory=True,
)
```

Use **long-term memory** for crews that run repeatedly (daily reports, recurring analysis). Use **entity memory** when agents need to remember facts about specific subjects across sessions.

### Q8: How do you implement structured output validation?
**A:** Use Pydantic models with `output_pydantic`:

```python
from pydantic import BaseModel, Field
from typing import List, Literal

class StockAnalysis(BaseModel):
    symbol: str
    recommendation: Literal["BUY", "HOLD", "SELL"]
    target_price: float = Field(gt=0)
    risk_level: Literal["LOW", "MEDIUM", "HIGH"]
    key_factors: List[str] = Field(min_length=1, max_length=5)
    confidence: float = Field(ge=0.0, le=1.0)

analysis_task = Task(
    description="Analyze {symbol} stock fundamentals and technicals.",
    expected_output="Structured stock analysis with recommendation.",
    agent=analyst,
    output_pydantic=StockAnalysis,
)

result = crew.kickoff(inputs={"symbol": "INFY"})
analysis: StockAnalysis = result.pydantic
# Pydantic validates all fields — type errors raise exceptions
```

### Q9: How do you handle errors and retries in CrewAI?
**A:** CrewAI has built-in retry logic:

```python
agent = Agent(
    role="Analyst",
    goal="Produce accurate analysis",
    max_iter=5,        # Max reasoning iterations per task
    max_retry_limit=2, # Retries if output validation fails
)

task = Task(
    description="Analyze data",
    expected_output="Valid JSON report",
    agent=agent,
    output_pydantic=ReportModel,  # Validation triggers retry on failure
)
```

If the agent's output doesn't match `output_pydantic`, CrewAI feeds the validation error back to the agent and retries. For tool failures, wrap tools with try/except and return descriptive error messages the agent can act on.

### Q10: How do Flows work for multi-crew orchestration?
**A:** Flows connect multiple crews using event-driven decorators:

```python
from crewai.flow.flow import Flow, listen, start, router

class ETLFlow(Flow):
    @start()
    def extract(self):
        result = ExtractCrew().crew().kickoff()
        self.state.raw_data = result.raw

    @listen(extract)
    def transform(self):
        result = TransformCrew().crew().kickoff(
            inputs={"data": self.state.raw_data}
        )
        self.state.clean_data = result.raw

    @router(transform)
    def quality_check(self):
        if self.state.quality_score > 0.9:
            return "load"
        return "reprocess"

    @listen("load")
    def load(self):
        LoadCrew().crew().kickoff(
            inputs={"data": self.state.clean_data}
        )
```

`@start()` marks the entry point. `@listen(method)` triggers when the referenced method completes. `@router(method)` returns a string that determines which `@listen("string")` fires next.

---

## Advanced Level

### Q11: Design a production multi-agent system for financial report generation.
**A:**

```python
from crewai.flow.flow import Flow, listen, start, router

class FinancialReportFlow(Flow):
    @start()
    def gather_market_data(self):
        """Crew 1: Data collection from multiple sources."""
        result = DataCrew().crew().kickoff(
            inputs={"symbols": self.state.portfolio}
        )
        self.state.market_data = result.pydantic

    @listen(gather_market_data)
    def analyze_fundamentals(self):
        """Crew 2: Fundamental analysis — sequential process."""
        result = FundamentalsCrew().crew().kickoff(
            inputs={"data": self.state.market_data}
        )
        self.state.fundamentals = result.pydantic

    @listen(gather_market_data)
    def analyze_technicals(self):
        """Crew 3: Technical analysis — runs PARALLEL with fundamentals."""
        result = TechnicalsCrew().crew().kickoff(
            inputs={"data": self.state.market_data}
        )
        self.state.technicals = result.pydantic

    @listen(analyze_fundamentals, analyze_technicals)
    def synthesize(self):
        """Crew 4: Combine both analyses."""
        result = SynthesisCrew().crew().kickoff(
            inputs={
                "fundamentals": self.state.fundamentals,
                "technicals": self.state.technicals,
            }
        )
        self.state.report = result.pydantic

    @router(synthesize)
    def compliance_gate(self):
        if self.state.report.risk_score > 0.8:
            return "human_review"
        return "publish"

    @listen("human_review")
    def escalate(self):
        ReviewCrew().crew().kickoff(
            inputs={"report": self.state.report}
        )

    @listen("publish")
    def distribute(self):
        DistributionCrew().crew().kickoff(
            inputs={"report": self.state.report}
        )
```

Key design principles:
- **Parallel crews** for independent analyses (fundamentals + technicals)
- **Router** for compliance gating before publishing
- **Structured output** (Pydantic) ensures type-safe data flow between crews
- **Human-in-the-loop** for high-risk reports

### Q12: How do you optimize CrewAI for cost and latency in production?
**A:**

1. **Right-size LLMs per agent:**
```python
researcher = Agent(role="Researcher", llm="gpt-4o-mini")  # Cheaper for data gathering
analyst = Agent(role="Analyst", llm="gpt-4o")              # Smarter for analysis
```

2. **Control iterations:** `max_iter=3` prevents runaway reasoning loops
3. **Async execution:** Mark independent tasks with `async_execution=True`
4. **Caching:** Tool results cached by default — disable for real-time: `cache=False`
5. **Rate limiting:** Set `max_rpm=30` per agent to avoid API throttling
6. **Batch inputs:** Process multiple items in one crew run vs separate kickoffs
7. **Memory pruning:** Limit long-term memory to recent N runs to reduce context size
8. **Monitoring:** Use CrewAI callbacks to log token usage per agent per task

### Q13: How would you implement testing for a CrewAI application?
**A:**

```python
# Unit test: Verify tool works correctly
def test_stock_price_tool():
    result = get_stock_price.run("RELIANCE")
    assert "RELIANCE" in result
    assert "₹" in result

# Integration test: Verify crew produces valid output
def test_analysis_crew():
    crew = AnalysisCrew().crew()
    result = crew.kickoff(inputs={"symbol": "TCS"})
    analysis = result.pydantic
    assert analysis.recommendation in ["BUY", "HOLD", "SELL"]
    assert 0 <= analysis.confidence <= 1

# Benchmark test: Measure quality across runs
def test_crew_consistency():
    results = []
    for _ in range(3):
        result = crew.kickoff(inputs={"topic": "AI trends"})
        results.append(result)
    # Check outputs are consistent in structure
    for r in results:
        assert r.pydantic is not None

# CrewAI built-in testing
crew.test(n_iterations=5, inputs={"topic": "Test"})
```

### Q14: Explain delegation between agents and when it helps vs hurts.
**A:** When `allow_delegation=True`, an agent can ask other crew agents for help:

```python
lead = Agent(
    role="Lead Analyst",
    goal="Produce comprehensive analysis",
    allow_delegation=True,  # Can delegate to junior
)
junior = Agent(
    role="Junior Researcher",
    goal="Gather supporting data",
    allow_delegation=False,  # Cannot delegate further
)
```

**When it helps:**
- Lead agent recognizes it needs specialized data (delegates data gathering)
- Reduces prompt complexity — each agent stays focused

**When it hurts:**
- Adds LLM calls (delegation = extra reasoning turns)
- Can create loops if multiple agents delegate to each other
- Less predictable execution path

**Best practice:** Enable delegation only on "manager" agents. Set `max_iter` to prevent infinite delegation loops. In sequential processes, delegation is rarely needed since task chaining handles data flow explicitly.
