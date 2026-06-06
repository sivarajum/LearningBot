# Claude API (Anthropic): Complete Guide

## 1. What is the Claude API?

The Claude API provides programmatic access to Anthropic's Claude family of AI models. Claude excels at complex reasoning, coding, analysis, and long-context tasks with strong safety properties.

**Model Family (2025):**
| Model | Best For | Context | Speed |
|-------|----------|---------|-------|
| Claude Opus 4 | Complex reasoning, research, agentic coding | 200K | Slowest |
| Claude Sonnet 4 | Best balance of intelligence and speed | 200K | Medium |
| Claude Haiku 3.5 | Fast tasks, classification, extraction | 200K | Fastest |

---

## 2. Core Concepts

### Messages API
```python
import anthropic

client = anthropic.Anthropic()  # Uses ANTHROPIC_API_KEY env var

message = client.messages.create(
    model="claude-sonnet-4-20250514",
    max_tokens=1024,
    messages=[
        {"role": "user", "content": "Analyze RELIANCE Q3 results"}
    ],
)
print(message.content[0].text)
```

### System Prompts
```python
message = client.messages.create(
    model="claude-sonnet-4-20250514",
    max_tokens=2048,
    system="You are a senior quantitative analyst at a hedge fund specializing in Indian equities (NSE/BSE). Provide analysis with specific data points and actionable recommendations.",
    messages=[
        {"role": "user", "content": "What's the outlook for NIFTY50 given current FII outflows?"}
    ],
)
```

### Multi-Turn Conversations
```python
messages = [
    {"role": "user", "content": "Analyze RELIANCE stock"},
    {"role": "assistant", "content": "RELIANCE Industries (NSE: RELIANCE) overview..."},
    {"role": "user", "content": "Now compare with TCS on valuation metrics"},
]
response = client.messages.create(
    model="claude-sonnet-4-20250514",
    max_tokens=2048,
    messages=messages,
)
```

---

## 3. Key Features

### Streaming
```python
with client.messages.stream(
    model="claude-sonnet-4-20250514",
    max_tokens=1024,
    messages=[{"role": "user", "content": "Explain Black-Scholes model"}],
) as stream:
    for text in stream.text_stream:
        print(text, end="", flush=True)
```

### Vision (Image Analysis)
```python
import base64

with open("chart.png", "rb") as f:
    image_data = base64.standard_b64encode(f.read()).decode()

message = client.messages.create(
    model="claude-sonnet-4-20250514",
    max_tokens=1024,
    messages=[{
        "role": "user",
        "content": [
            {"type": "image", "source": {"type": "base64", "media_type": "image/png", "data": image_data}},
            {"type": "text", "text": "Analyze this stock chart. Identify support/resistance levels and patterns."},
        ],
    }],
)
```

### Tool Use (Function Calling)
```python
tools = [
    {
        "name": "get_stock_price",
        "description": "Get current stock price from NSE",
        "input_schema": {
            "type": "object",
            "properties": {
                "symbol": {"type": "string", "description": "NSE stock symbol, e.g. RELIANCE"},
                "exchange": {"type": "string", "enum": ["NSE", "BSE"], "default": "NSE"},
            },
            "required": ["symbol"],
        },
    },
    {
        "name": "calculate_greeks",
        "description": "Calculate option Greeks using Black-Scholes",
        "input_schema": {
            "type": "object",
            "properties": {
                "spot": {"type": "number"},
                "strike": {"type": "number"},
                "expiry_days": {"type": "integer"},
                "volatility": {"type": "number"},
                "option_type": {"type": "string", "enum": ["call", "put"]},
            },
            "required": ["spot", "strike", "expiry_days", "volatility", "option_type"],
        },
    },
]

response = client.messages.create(
    model="claude-sonnet-4-20250514",
    max_tokens=1024,
    tools=tools,
    messages=[{"role": "user", "content": "What's RELIANCE trading at? Calculate delta for a 3000 call expiring in 7 days with 25% IV"}],
)

# Handle tool use
for block in response.content:
    if block.type == "tool_use":
        tool_name = block.name
        tool_input = block.input
        # Execute your function
        result = execute_tool(tool_name, tool_input)

        # Send result back
        messages.append({"role": "assistant", "content": response.content})
        messages.append({
            "role": "user",
            "content": [{"type": "tool_result", "tool_use_id": block.id, "content": str(result)}],
        })
        final_response = client.messages.create(
            model="claude-sonnet-4-20250514", max_tokens=1024, tools=tools, messages=messages,
        )
```

### Extended Thinking
```python
response = client.messages.create(
    model="claude-sonnet-4-20250514",
    max_tokens=16000,
    thinking={
        "type": "enabled",
        "budget_tokens": 10000,  # Tokens for internal reasoning
    },
    messages=[{"role": "user", "content": "Design an optimal portfolio allocation for ₹50L across NSE stocks with max drawdown < 15%"}],
)

for block in response.content:
    if block.type == "thinking":
        print(f"Thinking: {block.thinking}")  # Shows reasoning steps
    elif block.type == "text":
        print(f"Answer: {block.text}")
```

### Prompt Caching
```python
# Cache large system prompts or reference docs (saves 90% on repeated calls)
response = client.messages.create(
    model="claude-sonnet-4-20250514",
    max_tokens=1024,
    system=[
        {
            "type": "text",
            "text": large_reference_document,  # 10K+ tokens
            "cache_control": {"type": "ephemeral"},  # Cache this block
        }
    ],
    messages=[{"role": "user", "content": "Based on the reference, what's the P/E ratio for RELIANCE?"}],
)
# cache_creation_input_tokens: first call (full price)
# cache_read_input_tokens: subsequent calls (90% discount)
```

### Batches API (50% Cost Reduction)
```python
# Process many requests asynchronously at half price
batch = client.messages.batches.create(
    requests=[
        {
            "custom_id": f"analysis-{symbol}",
            "params": {
                "model": "claude-sonnet-4-20250514",
                "max_tokens": 1024,
                "messages": [{"role": "user", "content": f"Analyze {symbol} stock fundamentals"}],
            },
        }
        for symbol in ["RELIANCE", "TCS", "INFY", "HDFC", "ICICIBANK"]
    ]
)
# Results available within 24 hours
```

---

## 4. Installation

```bash
pip install anthropic

# Set API key
export ANTHROPIC_API_KEY="sk-ant-api03-..."

# Verify
python -c "import anthropic; c = anthropic.Anthropic(); print(c.messages.create(model='claude-haiku-3-5-20241022', max_tokens=10, messages=[{'role':'user','content':'Hi'}]).content[0].text)"
```

---

## 5. Best Practices

### Prompt Engineering for Claude
```python
# 1. Use XML tags for structure
system = """You are a financial analyst. Use these guidelines:
<rules>
- Always cite specific numbers and dates
- Compare against sector benchmarks
- Highlight risks prominently
</rules>

<output_format>
## Summary
## Key Metrics (table)
## Risks
## Recommendation
</output_format>"""

# 2. Prefill assistant response for format control
messages = [
    {"role": "user", "content": "Analyze RELIANCE Q3 results"},
    {"role": "assistant", "content": '{"analysis": {'},  # Forces JSON output
]

# 3. Use examples (few-shot)
system = """Classify financial news sentiment.
<examples>
<example>
Input: "RELIANCE profit surges 30% on Jio growth"
Output: {"sentiment": "positive", "confidence": 0.95, "entities": ["RELIANCE", "Jio"]}
</example>
</examples>"""
```

### Error Handling
```python
import anthropic

try:
    response = client.messages.create(...)
except anthropic.RateLimitError:
    # Rate limited — implement exponential backoff
    time.sleep(retry_delay)
except anthropic.APIStatusError as e:
    if e.status_code == 529:  # Overloaded
        time.sleep(30)
    else:
        raise
except anthropic.APIConnectionError:
    # Network issue — retry
    pass
```

### Cost Optimization
| Strategy | Savings |
|----------|---------|
| Use Haiku for simple tasks (classification, extraction) | 10-20x cheaper than Opus |
| Prompt caching for repeated large contexts | 90% on cached tokens |
| Batches API for async processing | 50% off |
| Reduce max_tokens (don't set 4096 if you need 200) | Proportional |
| Cache system prompts across conversations | 90% on system prompt |

---

## 6. Common Pitfalls

| Pitfall | Solution |
|---------|----------|
| Ignoring stop_reason | Always check: `end_turn`, `max_tokens`, `tool_use` |
| Not handling tool_use responses | Must send tool_result back to continue |
| Setting max_tokens too low | Claude stops mid-sentence; check stop_reason |
| Not using streaming for long outputs | Users wait for full response; use stream |
| Hardcoding model names | Use constants: `MODEL_SONNET = "claude-sonnet-4-20250514"` |
| Ignoring rate limits | Implement exponential backoff with jitter |

---

## 7. Claude vs GPT vs Gemini

| Feature | Claude | GPT-4 | Gemini |
|---------|--------|-------|--------|
| Context window | 200K | 128K | 2M |
| Best at | Reasoning, safety, coding | General, plugins | Long context, multimodal |
| Tool use | ✅ JSON schema | ✅ Function calling | ✅ Function calling |
| Vision | ✅ | ✅ | ✅ (best multimodal) |
| Extended thinking | ✅ | ✅ (o1 reasoning) | ✅ (Gemini thinking) |
| Streaming | ✅ | ✅ | ✅ |
| Batch pricing | 50% off | 50% off | ❌ |
| Prompt caching | ✅ 90% saving | ❌ | ✅ Context caching |

---

## 8. Extended Thinking (Claude's Reasoning Mode)

```python
# Enable deep reasoning for complex analysis
response = client.messages.create(
    model="claude-sonnet-4-20250514",
    max_tokens=16000,
    thinking={
        "type": "enabled",
        "budget_tokens": 10000,  # Allow 10K tokens of thinking
    },
    messages=[{
        "role": "user",
        "content": "Analyze whether RELIANCE is undervalued based on DCF, "
                   "peer comparison, and sum-of-parts valuation."
    }],
)

# Access thinking process
for block in response.content:
    if block.type == "thinking":
        print(f"REASONING: {block.thinking}")  # See Claude's work
    elif block.type == "text":
        print(f"ANSWER: {block.text}")
```

**When to use:** Complex financial modeling, multi-step math, strategy design, code architecture decisions.

---

## 9. Prompt Caching (90% Cost Reduction)

```python
# Cache large system prompts and documents
response = client.messages.create(
    model="claude-sonnet-4-20250514",
    max_tokens=1024,
    system=[
        {
            "type": "text",
            "text": large_system_prompt,  # Your 5000+ token system prompt
            "cache_control": {"type": "ephemeral"},  # Mark for caching
        }
    ],
    messages=[{"role": "user", "content": "Quick question about the data"}],
)

# First call: full price
# Subsequent calls (within 5 min): 90% cheaper on cached tokens!
# Check: response.usage.cache_creation_input_tokens
# Check: response.usage.cache_read_input_tokens
```

**Ideal for:** Repeated queries against same context (annual reports, codebases, regulatory docs).

---

## 10. Model Context Protocol (MCP)

MCP allows Claude to connect to external tools and data sources via a standardized protocol.

```python
# MCP server example: expose trading data to Claude
from mcp.server import Server

server = Server("trading-data")

@server.tool()
async def get_portfolio_positions():
    """Get current portfolio positions with P&L."""
    return await portfolio_store.get_active_positions()

@server.tool()
async def get_market_regime(symbol: str):
    """Get current market regime classification for a symbol."""
    return await regime_classifier.classify(symbol)

@server.tool()
async def check_sebi_compliance(order: dict):
    """Validate an order against SEBI regulations."""
    return await sebi_validator.validate(order)
```

---

## 11. Batches API (50% Cost Reduction)

```python
# For non-time-sensitive workloads: batch processing at half price
batch = client.batches.create(
    requests=[
        {
            "custom_id": f"earnings-{symbol}",
            "params": {
                "model": "claude-sonnet-4-20250514",
                "max_tokens": 1024,
                "messages": [{"role": "user", "content": f"Analyze {symbol} Q3 earnings"}],
            },
        }
        for symbol in ["RELIANCE", "TCS", "INFY", "HDFC", "ICICI"]
    ],
)

# Results available within 24 hours — 50% cheaper
results = client.batches.results(batch.id)
```

**Use cases:** Bulk analysis, overnight report generation, dataset annotation, backtesting narratives.

---

## 12. Production Architecture

```
┌─────────────────────────────────────────────────────┐
│  Application Layer                                  │
│  sjarvis CLI / API / Telegram                       │
├─────────────────────────────────────────────────────┤
│  Agent Layer (Jarvis AI)                            │
│  AlphaLab | RiskGuard | ExecOps | DataPulse         │
├─────────────────────────────────────────────────────┤
│  Claude API (with prompt caching)                   │
│  System prompt cached → 90% cost savings            │
│  Extended thinking for complex analysis             │
│  Tool use for data access                           │
├─────────────────────────────────────────────────────┤
│  MCP Servers                                        │
│  Trading Data | Market Regime | SEBI Validator       │
└─────────────────────────────────────────────────────┘
```
