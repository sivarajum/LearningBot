# Gemini API: Interview Questions & Answers

## Beginner Level

### Q1: What is the Gemini API and what makes it different?
**A:** Gemini is Google's natively multimodal AI model family. Key differentiators:
- **2M token context window** (largest available) — fit entire codebases or 100s of pages
- **Native multimodal** — processes text, images, audio, video in one model
- **Google Search grounding** — answers grounded in real-time web data
- **Free tier** — Gemini 2.0 Flash: 15 RPM, 1.5K requests/day, $0

### Q2: Show a basic Gemini API call with structured output.
**A:**
```python
import google.generativeai as genai
import typing_extensions as typing

genai.configure(api_key="YOUR_API_KEY")

class Sentiment(typing.TypedDict):
    label: str
    score: float
    reasoning: str

model = genai.GenerativeModel("gemini-2.5-flash")
response = model.generate_content(
    "Classify sentiment: 'RELIANCE profit surges 30% on Jio growth'",
    generation_config=genai.GenerationConfig(
        response_mime_type="application/json",
        response_schema=Sentiment,
    ),
)
import json
result = json.loads(response.text)
# {"label": "positive", "score": 0.95, "reasoning": "Strong profit growth..."}
```

### Q3: How does Gemini handle multimodal input?
**A:**
```python
import PIL.Image

model = genai.GenerativeModel("gemini-2.5-flash")

# Image analysis
image = PIL.Image.open("chart.png")
response = model.generate_content(["Analyze this chart", image])

# PDF analysis
pdf = genai.upload_file("report.pdf")
response = model.generate_content(["Summarize key metrics", pdf])

# Audio transcription
audio = genai.upload_file("earnings_call.mp3")
response = model.generate_content(["Transcribe and summarize", audio])

# Video analysis
video = genai.upload_file("presentation.mp4")
response = model.generate_content(["Key takeaways from this video", video])
```

All modalities go into a single prompt — no separate models needed.

### Q4: What are the safety settings and how do you configure them?
**A:**
```python
response = model.generate_content(
    "Analyze the financial risks of leveraged trading",
    safety_settings={
        "HARM_CATEGORY_DANGEROUS_CONTENT": "BLOCK_NONE",
        "HARM_CATEGORY_HARASSMENT": "BLOCK_MEDIUM_AND_ABOVE",
    },
)

# Check if blocked
if response.candidates[0].finish_reason == "SAFETY":
    print("Blocked by safety filter")
    print(response.candidates[0].safety_ratings)
```

For financial analysis, set `BLOCK_NONE` on `DANGEROUS_CONTENT` since legitimate financial risk discussion may trigger filters.

---

## Intermediate Level

### Q5: How does function calling work in Gemini?
**A:**
```python
# Define functions
tools = [
    genai.protos.Tool(function_declarations=[
        genai.protos.FunctionDeclaration(
            name="get_portfolio_value",
            description="Get current portfolio value and holdings",
            parameters=genai.protos.Schema(
                type=genai.protos.Type.OBJECT,
                properties={"account_id": genai.protos.Schema(type=genai.protos.Type.STRING)},
                required=["account_id"],
            ),
        ),
    ])
]

model = genai.GenerativeModel("gemini-2.5-flash", tools=tools)
chat = model.start_chat()

response = chat.send_message("What's my portfolio value for account A123?")

# Process function call
for part in response.parts:
    if fn := part.function_call:
        result = get_portfolio_value(fn.args["account_id"])
        response = chat.send_message(
            genai.protos.Content(parts=[
                genai.protos.Part(function_response=genai.protos.FunctionResponse(
                    name=fn.name, response={"result": result}
                ))
            ])
        )
        print(response.text)  # Natural language answer using function result
```

### Q6: How does context caching work and when to use it?
**A:**
```python
import datetime

# Upload and cache a large document
file = genai.upload_file("nifty50_annual_data.csv")  # 500K tokens

cache = genai.caching.CachedContent.create(
    model="gemini-2.5-flash",
    display_name="nifty50-data",
    system_instruction="You are a quantitative analyst with access to NIFTY50 historical data.",
    contents=[{"parts": [file], "role": "user"}],
    ttl=datetime.timedelta(hours=2),  # Cache for 2 hours
)

# Multiple queries against cached content (much cheaper)
model = genai.GenerativeModel.from_cached_content(cache)
r1 = model.generate_content("What was the max drawdown in 2020?")
r2 = model.generate_content("Calculate annual returns for each year")
r3 = model.generate_content("Which month has best average returns?")

# Cleanup
cache.delete()
```

**Use when:** Same large document/dataset queried 3+ times within TTL window.

### Q7: How do you use Google Search grounding?
**A:**
```python
from google.generativeai.types import Tool

model = genai.GenerativeModel(
    "gemini-2.5-flash",
    tools=[Tool(google_search=genai.protos.GoogleSearch())],
)

response = model.generate_content("What are the latest SEBI regulations on F&O trading?")

# Check grounding sources
metadata = response.candidates[0].grounding_metadata
if metadata:
    for chunk in metadata.grounding_chunks:
        print(f"Source: {chunk.web.title} - {chunk.web.uri}")
```

Grounding ensures answers are based on current real-world data — critical for financial analysis.

### Q8: How do you implement streaming with Gemini?
**A:**
```python
model = genai.GenerativeModel("gemini-2.5-flash")

# Streaming response
response = model.generate_content(
    "Detailed analysis of Indian IT sector outlook",
    stream=True,
)

full_text = ""
for chunk in response:
    print(chunk.text, end="", flush=True)
    full_text += chunk.text

# Usage stats (after streaming completes)
print(f"\nTokens: {response.usage_metadata}")
```

---

## Advanced Level

### Q9: Design a multi-agent financial analysis system using Gemini.
**A:**
```python
class GeminiFinanceSystem:
    def __init__(self):
        genai.configure(api_key=os.getenv("GOOGLE_API_KEY"))

        # Specialized agents
        self.screener = genai.GenerativeModel(
            "gemini-2.5-flash",
            system_instruction="You screen stocks. Output JSON with symbols and scores.",
            tools=[Tool(google_search=genai.protos.GoogleSearch())],
        )

        self.analyst = genai.GenerativeModel(
            "gemini-2.5-pro",  # More powerful for deep analysis
            system_instruction="You are a deep fundamental analyst.",
        )

        self.risk = genai.GenerativeModel(
            "gemini-2.5-flash",
            system_instruction="You assess portfolio risk. Be conservative.",
        )

    async def analyze_opportunity(self, sector: str) -> dict:
        # Step 1: Screen (with live data via Search grounding)
        screen = self.screener.generate_content(
            f"Top 5 stocks in {sector} sector on NSE by momentum. Return JSON.",
            generation_config=genai.GenerationConfig(
                response_mime_type="application/json",
            ),
        )
        candidates = json.loads(screen.text)

        # Step 2: Deep analysis on top picks
        analyses = []
        for stock in candidates["stocks"][:3]:
            analysis = self.analyst.generate_content(
                f"Deep fundamental analysis of {stock['symbol']}: valuation, growth, moat",
            )
            analyses.append({"symbol": stock["symbol"], "analysis": analysis.text})

        # Step 3: Risk assessment
        risk = self.risk.generate_content(
            f"Risk assessment for portfolio: {json.dumps(analyses)}",
        )

        return {
            "screened": candidates,
            "analyses": analyses,
            "risk_assessment": risk.text,
        }
```

### Q10: How do you optimize Gemini API costs for high-volume use?
**A:**

| Strategy | Implementation | Saving |
|----------|---------------|--------|
| Free tier (Flash 2.0) | Use for classification, extraction | 100% (free) |
| Context caching | Cache large docs, reuse across queries | ~75% |
| Model routing | Flash for simple, Pro for complex | 5-10x |
| Batch processing | Process in off-peak hours | Variable |
| Token counting | Pre-check with `model.count_tokens()` | Avoid surprises |

```python
class CostRouter:
    def __init__(self):
        self.flash = genai.GenerativeModel("gemini-2.5-flash")   # Cheap
        self.pro = genai.GenerativeModel("gemini-2.5-pro")       # Expensive
        self.free = genai.GenerativeModel("gemini-2.0-flash")    # Free

    def route(self, query: str, complexity: str = "auto"):
        # Count tokens first
        token_count = self.flash.count_tokens(query)
        if token_count.total_tokens > 100000:
            print(f"Warning: {token_count.total_tokens} tokens")

        if complexity == "simple" or len(query) < 100:
            return self.free.generate_content(query)
        elif complexity == "complex":
            return self.pro.generate_content(query)
        else:
            return self.flash.generate_content(query)
```

---

## Advanced Level (5 Additional Q&As)

### Q11: How do you implement Gemini function calling for trading workflows?
**A:**

```python
import google.generativeai as genai

# Define tools the model can call
def get_stock_price(symbol: str) -> dict:
    """Get current price and key metrics for an NSE stock."""
    return {"symbol": symbol, "price": 2456.50, "rsi": 68, "volume": 12500000}

def place_paper_trade(symbol: str, side: str, quantity: int) -> dict:
    """Place a paper trade order. Side: BUY or SELL."""
    return {"order_id": "PT-001", "status": "PLACED", "symbol": symbol, "side": side, "qty": quantity}

model = genai.GenerativeModel(
    "gemini-2.5-flash",
    tools=[get_stock_price, place_paper_trade],
    system_instruction="You are a trading assistant. Always check stock price before trading. Follow SEBI limits.",
)

chat = model.start_chat(enable_automatic_function_calling=True)
response = chat.send_message("Check RELIANCE price and buy 100 if RSI < 70")
# Gemini automatically: calls get_stock_price("RELIANCE") → checks RSI 68 < 70 → calls place_paper_trade
```

**Key features:**
- Auto function calling (model decides when to call tools)
- Parallel function calling (multiple tools in one turn)
- Function response validation before sending back to model

### Q12: How do you use Gemini's context caching for large document analysis?
**A:**

```python
import google.generativeai as genai
from datetime import timedelta

# Cache a large document (e.g., SEBI regulations PDF — 500 pages)
cache = genai.caching.CachedContent.create(
    model="gemini-2.0-flash",
    display_name="sebi-regulations-2024",
    contents=[
        genai.upload_file("sebi_master_circular_2024.pdf"),
        genai.upload_file("nse_trading_rules.pdf"),
    ],
    ttl=timedelta(hours=24),  # Cache for 24 hours
)

# Use cached context (75% cheaper than re-sending)
model = genai.GenerativeModel.from_cached_content(cache)
response = model.generate_content("What is the maximum F&O position limit for individual stocks?")

# Multiple queries against same cache — massive savings
for query in trading_queries:
    response = model.generate_content(query)  # Each query uses cached context
```

**Cost savings calculation:**
- 500-page doc ≈ 200K tokens
- Without cache: 200K × $0.075/1M = $0.015 per query
- With cache: 200K × $0.01875/1M = $0.00375 per query (75% savings!)
- 1000 queries/day: $15 → $3.75/day

### Q13: How do you implement structured output with Gemini?
**A:**

```python
import google.generativeai as genai
from pydantic import BaseModel
from typing import Literal

# Define schema
class TradingSignal(BaseModel):
    symbol: str
    action: Literal["BUY", "SELL", "HOLD"]
    confidence: float  # 0.0 to 1.0
    reasoning: str
    target_price: float
    stop_loss: float

model = genai.GenerativeModel("gemini-2.5-flash")
response = model.generate_content(
    "Analyze INFY.NSE: Price 1580, RSI 32, MACD bearish diverging, support at 1550",
    generation_config=genai.GenerationConfig(
        response_mime_type="application/json",
        response_schema=TradingSignal,
    ),
)
signal = TradingSignal.model_validate_json(response.text)
print(f"{signal.symbol}: {signal.action} (confidence: {signal.confidence:.0%})")
```

Gemini enforces the schema at generation time — no post-processing or retry needed.

### Q14: How do you build a Gemini-powered multi-modal trading analysis system?
**A:**

```python
# Analyze chart images + text data simultaneously
import google.generativeai as genai

model = genai.GenerativeModel("gemini-2.5-pro")

# Upload chart image
chart = genai.upload_file("nifty50_daily_chart.png")

response = model.generate_content([
    chart,  # Visual: candlestick chart with indicators
    """Analyze this NIFTY 50 daily chart. Identify:
    1. Current trend (uptrend/downtrend/sideways)
    2. Key support/resistance levels from the chart
    3. Pattern formations (head & shoulders, double top/bottom, flags)
    4. Volume analysis (confirming or diverging from price)
    
    Also consider this data:
    - FII: Net sellers ₹2,500 Cr last 5 days
    - VIX: 18.5 (elevated)
    - PCR: 0.85 (slightly bearish)
    
    Output a structured trading recommendation.""",
])

# Multi-modal = can read chart patterns + combine with numerical data
```

**Use cases:**
- Chart pattern recognition (visual)
- Financial document extraction (PDF/images)
- Video analysis of earnings calls (audio + video)
- Combined technical + fundamental analysis

### Q15: Compare Gemini API vs Claude API vs OpenAI for enterprise GenAI deployment.
**A:**

| Feature | Gemini | Claude | OpenAI |
|---------|--------|--------|--------|
| **Free tier** | ✅ Flash 2.0 (15 RPM, 1M tok/day) | ❌ | ❌ |
| **Context window** | 2M tokens (Pro) | 200K tokens | 128K tokens |
| **Multi-modal** | Text, image, video, audio | Text, image, PDF | Text, image, audio |
| **Structured output** | Native JSON schema | Tool use | JSON mode |
| **Function calling** | Auto + parallel | Tool use | Function calling |
| **Code execution** | ✅ Built-in sandbox | ❌ | ✅ Code Interpreter |
| **Context caching** | ✅ (75% savings) | ✅ Prompt caching | ❌ |
| **Grounding** | ✅ Google Search | ❌ | ✅ Web browsing |
| **Extended thinking** | ✅ Flash Thinking | ✅ Extended thinking | ✅ o1/o3 |
| **Latency** | Fast (Flash) | Medium | Fast (GPT-4o-mini) |
| **Best for** | Multi-modal, cost-sensitive | Complex reasoning, safety | Ecosystem, tools |
| **Enterprise** | Google Cloud integration | AWS Bedrock + direct | Azure OpenAI |

**For trading systems:** Gemini Flash free tier for high-volume classification → Claude for complex reasoning → OpenAI for ecosystem compatibility.
