# Claude API: Interview Questions & Answers

## Beginner Level

### Q1: What is the Claude API and what models are available?
**A:** The Claude API from Anthropic provides access to Claude models via a Messages API.

| Model | Use Case | Cost | Speed |
|-------|----------|------|-------|
| Claude Opus 4 | Complex reasoning, agentic tasks, research | Highest | Slowest |
| Claude Sonnet 4 | Best balance — coding, analysis, general | Medium | Medium |
| Claude Haiku 3.5 | Classification, extraction, fast tasks | Lowest | Fastest |

All share 200K context window. Choose Haiku for simple tasks, Sonnet for most work, Opus for hard problems.

### Q2: Show a basic Claude API call with system prompt.
**A:**
```python
import anthropic

client = anthropic.Anthropic()  # reads ANTHROPIC_API_KEY
response = client.messages.create(
    model="claude-sonnet-4-20250514",
    max_tokens=1024,
    system="You are a financial analyst specializing in Indian equities.",
    messages=[{"role": "user", "content": "What's the PE ratio outlook for NIFTY50?"}],
)
print(response.content[0].text)
print(f"Tokens: {response.usage.input_tokens} in, {response.usage.output_tokens} out")
```

### Q3: How does Claude's tool use (function calling) work?
**A:** You define tools as JSON schemas. Claude decides when to call them and returns structured input.

```python
tools = [{
    "name": "get_stock_price",
    "description": "Get current NSE stock price",
    "input_schema": {
        "type": "object",
        "properties": {"symbol": {"type": "string"}},
        "required": ["symbol"],
    },
}]

response = client.messages.create(
    model="claude-sonnet-4-20250514",
    max_tokens=1024,
    tools=tools,
    messages=[{"role": "user", "content": "What's RELIANCE trading at?"}],
)

# Check if Claude wants to use a tool
if response.stop_reason == "tool_use":
    tool_block = next(b for b in response.content if b.type == "tool_use")
    # Execute: get_stock_price(symbol="RELIANCE")
    result = get_stock_price(tool_block.input["symbol"])
    # Send result back
    messages.append({"role": "assistant", "content": response.content})
    messages.append({"role": "user", "content": [
        {"type": "tool_result", "tool_use_id": tool_block.id, "content": str(result)}
    ]})
```

### Q4: What is the difference between stop_reason values?
**A:**
| stop_reason | Meaning | Action |
|-------------|---------|--------|
| `end_turn` | Claude finished naturally | Use the response |
| `max_tokens` | Hit token limit, response truncated | Increase max_tokens or continue |
| `tool_use` | Claude wants to call a tool | Execute tool, send result back |
| `stop_sequence` | Hit a custom stop sequence | Process partial response |

Always check `stop_reason` — ignoring `tool_use` means Claude's response is incomplete.

---

## Intermediate Level

### Q5: How do you implement streaming for real-time responses?
**A:**
```python
# Method 1: Context manager
with client.messages.stream(
    model="claude-sonnet-4-20250514",
    max_tokens=2048,
    messages=[{"role": "user", "content": "Explain options pricing"}],
) as stream:
    for text in stream.text_stream:
        print(text, end="", flush=True)

# Method 2: Event-based (more control)
with client.messages.stream(
    model="claude-sonnet-4-20250514",
    max_tokens=2048,
    messages=[{"role": "user", "content": "Analyze market"}],
) as stream:
    for event in stream:
        if event.type == "content_block_delta":
            if event.delta.type == "text_delta":
                print(event.delta.text, end="")
        elif event.type == "message_stop":
            print("\n[Done]")

# Get final message with usage stats
final_message = stream.get_final_message()
print(f"Total tokens: {final_message.usage.input_tokens + final_message.usage.output_tokens}")
```

### Q6: How does prompt caching work and when should you use it?
**A:** Prompt caching stores large, repeated content server-side for 90% cost reduction.

```python
# Large reference document cached across calls
response = client.messages.create(
    model="claude-sonnet-4-20250514",
    max_tokens=1024,
    system=[{
        "type": "text",
        "text": company_financial_report,   # 50K tokens
        "cache_control": {"type": "ephemeral"},  # Cache this
    }],
    messages=[{"role": "user", "content": "What was Q3 revenue?"}],
)

# First call: cache_creation_input_tokens (1.25x price)
# Next calls: cache_read_input_tokens (0.1x price = 90% savings)

# Also works in messages (cache a long conversation prefix)
messages = [
    {"role": "user", "content": [
        {"type": "text", "text": long_document, "cache_control": {"type": "ephemeral"}},
        {"type": "text", "text": "Summarize this document"},
    ]},
]
```

**Use when:** System prompt > 1024 tokens AND reused across 3+ calls.
**Cache lifetime:** ~5 minutes, refreshed on each cache hit.

### Q7: How do you implement a multi-tool agentic loop?
**A:**
```python
def run_agent(user_query: str, tools: list, max_iterations: int = 10):
    messages = [{"role": "user", "content": user_query}]

    for i in range(max_iterations):
        response = client.messages.create(
            model="claude-sonnet-4-20250514",
            max_tokens=4096,
            tools=tools,
            messages=messages,
        )

        # If Claude is done (no more tool calls)
        if response.stop_reason == "end_turn":
            return response.content[0].text

        # Process tool calls
        messages.append({"role": "assistant", "content": response.content})
        tool_results = []
        for block in response.content:
            if block.type == "tool_use":
                result = execute_tool(block.name, block.input)
                tool_results.append({
                    "type": "tool_result",
                    "tool_use_id": block.id,
                    "content": str(result),
                })

        messages.append({"role": "user", "content": tool_results})

    return "Max iterations reached"
```

### Q8: How does Extended Thinking work?
**A:** Extended Thinking gives Claude a reasoning scratchpad before answering.

```python
response = client.messages.create(
    model="claude-sonnet-4-20250514",
    max_tokens=16000,
    thinking={"type": "enabled", "budget_tokens": 10000},
    messages=[{"role": "user", "content": "Design an optimal hedging strategy for a ₹10Cr NIFTY portfolio using options"}],
)

for block in response.content:
    if block.type == "thinking":
        print(f"[Reasoning]: {block.thinking[:200]}...")  # Internal chain-of-thought
    elif block.type == "text":
        print(f"[Answer]: {block.text}")
```

When to use: math, coding, complex analysis, multi-step reasoning.
Cost: thinking tokens count toward output tokens but improve answer quality significantly.

---

## Advanced Level

### Q9: Design a production trading analysis system using Claude API.
**A:**

```python
class TradingAnalyst:
    def __init__(self):
        self.client = anthropic.Anthropic()
        self.model = "claude-sonnet-4-20250514"
        self.tools = self._define_tools()
        self.system = self._build_system_prompt()

    def _build_system_prompt(self):
        return [{
            "type": "text",
            "text": """You are a quantitative trading analyst for NSE/BSE.
            <rules>
            - Always verify data before making recommendations
            - Include risk metrics (VaR, max drawdown) in analysis
            - SEBI compliance: max 5% per stock, 25% per sector
            - Cite specific numbers with dates
            </rules>""",
            "cache_control": {"type": "ephemeral"},
        }]

    def analyze(self, query: str) -> dict:
        messages = [{"role": "user", "content": query}]

        for _ in range(5):  # Max tool iterations
            response = self.client.messages.create(
                model=self.model,
                max_tokens=4096,
                system=self.system,
                tools=self.tools,
                messages=messages,
                thinking={"type": "enabled", "budget_tokens": 5000},
            )

            if response.stop_reason == "end_turn":
                return {
                    "analysis": next(b.text for b in response.content if b.type == "text"),
                    "reasoning": next((b.thinking for b in response.content if b.type == "thinking"), None),
                    "tokens": response.usage,
                }

            # Handle tools
            messages.append({"role": "assistant", "content": response.content})
            results = []
            for block in response.content:
                if block.type == "tool_use":
                    result = self._execute(block.name, block.input)
                    results.append({"type": "tool_result", "tool_use_id": block.id, "content": str(result)})
            messages.append({"role": "user", "content": results})
```

### Q10: How do you optimize Claude API costs for high-throughput systems?
**A:**

| Strategy | Implementation | Saving |
|----------|---------------|--------|
| Model routing | Haiku for classification, Sonnet for analysis | 10-20x on simple tasks |
| Prompt caching | Cache system prompts + reference docs | 90% on cached tokens |
| Batches API | Non-urgent analysis (EOD reports) | 50% off |
| Token management | Truncate old messages, summarize context | Proportional |
| Response length | Set appropriate max_tokens per task | Avoid waste |

```python
class CostOptimizedClient:
    def classify(self, text: str) -> str:
        """Simple task → Haiku (cheapest)"""
        return self.client.messages.create(
            model="claude-haiku-3-5-20241022", max_tokens=50, messages=[...]
        )

    def analyze(self, data: dict) -> str:
        """Complex task → Sonnet with caching"""
        return self.client.messages.create(
            model="claude-sonnet-4-20250514", max_tokens=2048,
            system=[{"type": "text", "text": self.cached_context, "cache_control": {"type": "ephemeral"}}],
            messages=[...],
        )

    def batch_reports(self, symbols: list) -> str:
        """EOD reports → Batches API (50% off, 24h delivery)"""
        return self.client.messages.batches.create(
            requests=[{"custom_id": s, "params": {...}} for s in symbols]
        )
```

### Q11: How do you handle Claude API rate limits and reliability?
**A:**

```python
import anthropic
import time
import random

class ResilientClient:
    def __init__(self):
        self.client = anthropic.Anthropic(
            max_retries=3,          # Built-in retry
            timeout=120.0,          # 2 min timeout
        )

    def call_with_fallback(self, messages, **kwargs):
        models = ["claude-sonnet-4-20250514", "claude-haiku-3-5-20241022"]
        for model in models:
            try:
                return self.client.messages.create(model=model, messages=messages, **kwargs)
            except anthropic.RateLimitError:
                delay = 2 ** models.index(model) + random.uniform(0, 1)
                time.sleep(delay)
            except anthropic.APIStatusError as e:
                if e.status_code == 529:  # Overloaded
                    time.sleep(30)
                    continue
                raise
        raise Exception("All models exhausted")
```
