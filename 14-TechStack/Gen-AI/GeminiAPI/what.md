# Gemini API (Google): Complete Guide

## 1. What is the Gemini API?

Google's Gemini API provides access to the Gemini family of multimodal AI models. Gemini is natively multimodal (text, images, audio, video, code) with the largest context window available (2M tokens for Gemini 2.5 Pro).

**Model Family (2025):**
| Model | Best For | Context | Speed |
|-------|----------|---------|-------|
| Gemini 2.5 Pro | Complex reasoning, coding, long context | 1M (2M preview) | Medium |
| Gemini 2.5 Flash | Fast, cost-efficient, thinking mode | 1M | Fast |
| Gemini 2.0 Flash | Free tier, high throughput | 1M | Fastest |

---

## 2. Core Concepts

### Basic Generation
```python
import google.generativeai as genai

genai.configure(api_key="YOUR_API_KEY")
model = genai.GenerativeModel("gemini-2.5-flash")

response = model.generate_content("Analyze NIFTY50 outlook for Q4 2025")
print(response.text)
```

### System Instructions
```python
model = genai.GenerativeModel(
    "gemini-2.5-flash",
    system_instruction="""You are a SEBI-registered financial advisor specializing in Indian equities.
    Always include risk disclaimers. Cite specific market data.
    Format responses with clear sections and tables.""",
)
response = model.generate_content("Should I invest in RELIANCE at current levels?")
```

### Multi-Turn Chat
```python
chat = model.start_chat(history=[])
response = chat.send_message("What sectors are performing well on NSE?")
print(response.text)
response = chat.send_message("Deep dive into the top sector")
print(response.text)

# Access full history
for msg in chat.history:
    print(f"{msg.role}: {msg.parts[0].text[:100]}")
```

---

## 3. Key Features

### Multimodal Input (Image + Text)
```python
import PIL.Image

model = genai.GenerativeModel("gemini-2.5-flash")
image = PIL.Image.open("stock_chart.png")

response = model.generate_content([
    "Analyze this stock chart. Identify:",
    "1. Support and resistance levels",
    "2. Trend direction",
    "3. Volume patterns",
    image,
])
print(response.text)
```

### Video Analysis
```python
video_file = genai.upload_file("earnings_call.mp4")

# Wait for processing
import time
while video_file.state.name == "PROCESSING":
    time.sleep(10)
    video_file = genai.get_file(video_file.name)

response = model.generate_content([
    video_file,
    "Summarize the key financial metrics discussed in this earnings call",
])
```

### Function Calling
```python
get_stock_price = genai.protos.FunctionDeclaration(
    name="get_stock_price",
    description="Get current stock price from NSE",
    parameters=genai.protos.Schema(
        type=genai.protos.Type.OBJECT,
        properties={
            "symbol": genai.protos.Schema(type=genai.protos.Type.STRING),
            "exchange": genai.protos.Schema(type=genai.protos.Type.STRING, enum=["NSE", "BSE"]),
        },
        required=["symbol"],
    ),
)

model = genai.GenerativeModel(
    "gemini-2.5-flash",
    tools=[get_stock_price],
)

response = model.generate_content("What's RELIANCE trading at on NSE?")

# Handle function call
for part in response.parts:
    if fn := part.function_call:
        result = execute_function(fn.name, dict(fn.args))
        response = chat.send_message(
            genai.protos.Content(parts=[
                genai.protos.Part(function_response=genai.protos.FunctionResponse(
                    name=fn.name, response={"result": result}
                ))
            ])
        )
```

### Structured Output (JSON Mode)
```python
import typing_extensions as typing

class StockAnalysis(typing.TypedDict):
    symbol: str
    sentiment: str
    confidence: float
    key_factors: list[str]
    recommendation: str

model = genai.GenerativeModel("gemini-2.5-flash")
response = model.generate_content(
    "Analyze TCS stock",
    generation_config=genai.GenerationConfig(
        response_mime_type="application/json",
        response_schema=StockAnalysis,
    ),
)
import json
analysis = json.loads(response.text)
```

### Grounding with Google Search
```python
from google.generativeai.types import Tool

model = genai.GenerativeModel(
    "gemini-2.5-flash",
    tools=[Tool(google_search=genai.protos.GoogleSearch())],
)
response = model.generate_content("What are today's top gainers on NSE?")
# Response includes grounding metadata with source URLs
```

### Context Caching (Cost Reduction)
```python
# Cache large documents for repeated queries
cache = genai.caching.CachedContent.create(
    model="gemini-2.5-flash",
    display_name="annual_report",
    system_instruction="You are a financial analyst.",
    contents=[{
        "parts": [genai.upload_file("reliance_annual_report.pdf")],
        "role": "user",
    }],
    ttl=datetime.timedelta(hours=1),
)

# Use cached content (cheaper)
model = genai.GenerativeModel.from_cached_content(cache)
response = model.generate_content("What was the revenue growth?")
```

### Thinking Mode (Gemini 2.5 Flash)
```python
model = genai.GenerativeModel("gemini-2.5-flash")
response = model.generate_content(
    "Design an optimal hedging strategy for NIFTY50 using options",
    generation_config=genai.GenerationConfig(
        thinking_config=genai.types.ThinkingConfig(thinking_budget=8192),
    ),
)
# Response includes thinking process + final answer
for part in response.candidates[0].content.parts:
    if part.thought:
        print(f"[Thinking]: {part.text[:200]}")
    else:
        print(f"[Answer]: {part.text}")
```

---

## 4. Installation

```bash
pip install google-generativeai

# Set API key
export GOOGLE_API_KEY="AIza..."

# Or for Vertex AI (enterprise)
pip install google-cloud-aiplatform
gcloud auth application-default login
```

---

## 5. Free Tier (Gemini 2.0 Flash)

| Limit | Value |
|-------|-------|
| Requests per minute | 15 |
| Tokens per minute | 1,000,000 |
| Requests per day | 1,500 |
| Cost | FREE |

```python
# Free tier usage — perfect for prototyping
model = genai.GenerativeModel("gemini-2.0-flash")
response = model.generate_content("Classify: 'RELIANCE profit surges 30%'")
```

---

## 6. Best Practices

1. **Use structured output** — `response_mime_type="application/json"` for reliable parsing
2. **Grounding for real-time data** — Google Search grounding for current market info
3. **Context caching** — Cache annual reports, research documents (save on repeated queries)
4. **Thinking mode** — Enable for complex analysis (math, strategy design)
5. **Safety settings** — Configure for financial content (may trigger safety filters)
6. **Retry on 429** — Rate limits hit easily on free tier; use exponential backoff
7. **Token counting** — `model.count_tokens(content)` before sending large prompts

---

## 7. Common Pitfalls

| Pitfall | Solution |
|---------|----------|
| Safety filter blocks financial content | Adjust safety_settings to BLOCK_NONE for analysis tasks |
| Free tier rate limits (15 RPM) | Queue requests, implement backoff |
| File upload timeout | Check `file.state`, poll until READY |
| JSON output invalid | Use response_schema for strict typing |
| Missing grounding sources | Check `response.candidates[0].grounding_metadata` |
| Context caching expiry | Set appropriate TTL, refresh proactively |

---

## 8. Gemini vs Claude vs GPT

| Feature | Gemini 2.5 | Claude Sonnet 4 | GPT-4o |
|---------|-----------|----------------|--------|
| Context | 1M-2M tokens | 200K tokens | 128K tokens |
| Multimodal | ✅ Native (text, image, video, audio) | ✅ (text, image) | ✅ (text, image, audio) |
| Free tier | ✅ (15 RPM) | ❌ | ❌ |
| Grounding (search) | ✅ Built-in | ❌ (need MCP) | ✅ (web browsing) |
| JSON mode | ✅ (schema enforcement) | ✅ (tool_use) | ✅ |
| Thinking | ✅ (Flash thinking) | ✅ (Extended thinking) | ✅ (o1 reasoning) |
| Code execution | ✅ (built-in sandbox) | ❌ | ✅ (Code Interpreter) |

---

## 9. Advanced: Context Caching

Context caching lets you upload large documents once and reuse them across queries — dramatically reducing cost for repeated analysis.

```python
import google.generativeai as genai

# Cache an annual report (one-time cost)
cache = genai.caching.CachedContent.create(
    model="gemini-2.5-flash",
    display_name="reliance-annual-report-2025",
    contents=[
        genai.protos.Content(
            parts=[genai.protos.Part(text=annual_report_text)],
            role="user",
        )
    ],
    ttl=datetime.timedelta(hours=6),  # Cache for 6 hours
)

# Query against cached content — 75% cheaper!
model = genai.GenerativeModel.from_cached_content(cache)
response = model.generate_content("What was the EBITDA margin trend?")
```

**When to cache:** Analyst reports, regulatory filings, codebases — any content queried repeatedly.

---

## 10. Function Calling / Tool Use

```python
# Define tools the model can call
tools = [
    genai.protos.Tool(
        function_declarations=[
            genai.protos.FunctionDeclaration(
                name="get_stock_price",
                description="Get current stock price from NSE",
                parameters=genai.protos.Schema(
                    type=genai.protos.Type.OBJECT,
                    properties={
                        "symbol": genai.protos.Schema(type=genai.protos.Type.STRING),
                        "exchange": genai.protos.Schema(type=genai.protos.Type.STRING),
                    },
                    required=["symbol"],
                ),
            ),
        ]
    )
]

model = genai.GenerativeModel("gemini-2.5-flash", tools=tools)
chat = model.start_chat()
response = chat.send_message("What's RELIANCE trading at right now?")

# Model returns function_call — you execute it, send result back
fc = response.candidates[0].content.parts[0].function_call
# Execute: result = get_stock_price(symbol="RELIANCE")
response2 = chat.send_message(
    genai.protos.Content(parts=[genai.protos.Part(function_response=...)])
)
```

---

## 11. Embedding Models

```python
# Gemini embedding — useful for RAG, similarity search
result = genai.embed_content(
    model="models/text-embedding-004",
    content="NIFTY50 hit all-time high on strong FII inflows",
    task_type="retrieval_document",  # or retrieval_query, similarity, classification
)
embedding = result["embedding"]  # 768-dim vector
```

**Task types matter:** `retrieval_document` for indexing, `retrieval_query` for searching — different encoding optimized for asymmetric retrieval.

---

## 12. Pricing & Budget Planning

| Model | Input (per 1M tokens) | Output (per 1M tokens) | Free Tier |
|-------|----------------------|------------------------|-----------|
| Gemini 2.0 Flash | $0.00 | $0.00 | ✅ 15 RPM, 1M tokens/day |
| Gemini 2.5 Flash | $0.15 | $0.60 | ✅ 5 RPM |
| Gemini 2.5 Pro | $1.25 | $10.00 | ✅ 2 RPM |

**Budget example (₹5K/month):**
- Free tier: 30M tokens/month (Gemini 2.0 Flash) = ₹0
- Paid: ~900K input tokens on Gemini 2.5 Flash = ~₹12 (~$0.14)
- Strategy: Use free tier for 90% tasks, paid only for complex analysis

---

## 13. Real-World: Gemini for Trading Analysis

```python
# Sentiment analysis of market news — free tier
model = genai.GenerativeModel(
    "gemini-2.0-flash",
    system_instruction="You are a financial sentiment analyzer for Indian markets.",
    generation_config=genai.GenerationConfig(
        response_mime_type="application/json",
        response_schema={
            "type": "object",
            "properties": {
                "sentiment": {"type": "string", "enum": ["BULLISH", "BEARISH", "NEUTRAL"]},
                "confidence": {"type": "number"},
                "key_factors": {"type": "array", "items": {"type": "string"}},
                "affected_sectors": {"type": "array", "items": {"type": "string"}},
            },
        },
    ),
)

headlines = [
    "RBI keeps repo rate unchanged at 6.5%",
    "FII net buyers for 10th consecutive session",
    "Global crude oil prices surge above $90/barrel",
]
response = model.generate_content(f"Analyze market impact: {headlines}")
# Returns structured JSON: {"sentiment": "BULLISH", "confidence": 0.72, ...}
```
