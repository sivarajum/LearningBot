# OpenAI GPT Models - Complete Learning Guide

## Table of Contents
1. [Definition & Problem Statement](#definition--problem-statement)
2. [Core Concepts & Principles](#core-concepts--principles)
3. [Key Features & Capabilities](#key-features--capabilities)
4. [API Models & Comparison](#api-models--comparison)
5. [Installation & Setup](#installation--setup)
6. [Beginner Examples](#beginner-examples)
7. [Intermediate Patterns](#intermediate-patterns)
8. [Advanced Architectures](#advanced-architectures)
9. [Best Practices & Optimization](#best-practices--optimization)
10. [Common Pitfalls & Solutions](#common-pitfalls--solutions)
11. [Comparison with Competitors](#comparison-with-competitors)
12. [Real-World Use Cases](#real-world-use-cases)
13. [Performance & Cost Optimization](#performance--cost-optimization)

---

## Definition & Problem Statement

### What is OpenAI GPT?

**OpenAI GPT (Generative Pre-trained Transformer)** is a family of large language models trained by OpenAI that can understand and generate human-like text. GPT models power the most advanced conversational AI systems and are used across industries for content generation, coding, analysis, and automation.

### Problem It Solves

Before GPT, building intelligent text applications required:
- Manual feature engineering
- Limited context understanding
- Separate models for different tasks
- Significant labeled training data
- Complex prompt engineering per task

**With OpenAI GPT:**
- Single API for multiple tasks
- Deep contextual understanding
- Few-shot learning capabilities
- Minimal prompt engineering needed
- Production-ready with built-in safety

---

## Core Concepts & Principles

### 1. **Tokens**
Basic units of text that models process. Roughly 1 token = 4 characters.

```python
# Token counting
import tiktoken

encoding = tiktoken.encoding_for_model("gpt-4")
text = "Hello, how are you?"
tokens = encoding.encode(text)
print(f"Token count: {len(tokens)}")  # ~5 tokens
```

### 2. **Temperature**
Controls randomness in outputs. 0 = deterministic, 1 = very random.

```python
# Low temperature (deterministic)
response = openai.ChatCompletion.create(
    model="gpt-4",
    messages=[{"role": "user", "content": "What is 2+2?"}],
    temperature=0  # Exact same answer every time
)

# High temperature (creative)
response = openai.ChatCompletion.create(
    model="gpt-4",
    messages=[{"role": "user", "content": "Write a poem"}],
    temperature=0.9  # Different answer every time
)
```

### 3. **System Prompts**
Define the model's behavior and role.

```python
response = openai.ChatCompletion.create(
    model="gpt-4",
    messages=[
        {"role": "system", "content": "You are a helpful coding assistant"},
        {"role": "user", "content": "How do I reverse a list in Python?"}
    ]
)
```

### 4. **Few-Shot Learning**
Teach the model by example without training.

```python
response = openai.ChatCompletion.create(
    model="gpt-4",
    messages=[
        {"role": "user", "content": "Translate English to French\nHello → Bonjour\nGoodbye → Au revoir\nGood morning → "},
    ]
)
# Returns "Bon matin"
```

### 5. **Token Limits & Context Windows**
Each model has maximum input/output token limits.

```python
# Different models have different limits:
# GPT-4 Turbo: 128K tokens
# GPT-4: 8K tokens
# GPT-3.5-turbo: 4K or 16K tokens

def count_tokens(text, model="gpt-4"):
    import tiktoken
    encoding = tiktoken.encoding_for_model(model)
    return len(encoding.encode(text))
```

### 6. **Cost Structure**
Billing based on tokens (input + output).

```python
# Cost calculation example
input_tokens = 1000
output_tokens = 500

# GPT-4 pricing (as of 2024)
input_cost = input_tokens * (0.03 / 1000)  # $0.03 per 1K input tokens
output_cost = output_tokens * (0.06 / 1000)  # $0.06 per 1K output tokens

total_cost = input_cost + output_cost
print(f"Total cost: ${total_cost:.4f}")
```

### 7. **Function Calling**
Enable models to call functions and tools.

```python
tools = [
    {
        "type": "function",
        "function": {
            "name": "get_weather",
            "description": "Get the weather for a location",
            "parameters": {
                "type": "object",
                "properties": {
                    "location": {"type": "string"},
                    "unit": {"type": "string", "enum": ["celsius", "fahrenheit"]}
                },
                "required": ["location"]
            }
        }
    }
]

response = openai.ChatCompletion.create(
    model="gpt-4",
    messages=[{"role": "user", "content": "What's the weather in NYC?"}],
    tools=tools
)
```

---

## Key Features & Capabilities

### 1. **Model Variants**
- GPT-4 Turbo: Most capable, 128K context
- GPT-4: High intelligence, 8K context
- GPT-3.5-turbo: Fast and cost-effective
- Legacy models: Older but still supported

### 2. **Vision Capabilities**
```python
response = openai.ChatCompletion.create(
    model="gpt-4-vision-preview",
    messages=[
        {
            "role": "user",
            "content": [
                {"type": "text", "text": "What's in this image?"},
                {"type": "image_url", "image_url": {"url": "https://example.com/image.jpg"}}
            ]
        }
    ]
)
```

### 3. **Fine-Tuning**
Customize models with your own data.

```python
# Create training data
training_data = [
    {"messages": [
        {"role": "system", "content": "You are a helpful assistant"},
        {"role": "user", "content": "Classify this: excellent product"},
        {"role": "assistant", "content": "positive"}
    ]}
]

# Upload and fine-tune
file_response = openai.File.create(
    file=open("training.jsonl", "rb"),
    purpose="fine-tune"
)

fine_tune = openai.FineTune.create(
    training_file=file_response["id"],
    model="gpt-3.5-turbo"
)
```

### 4. **Embeddings**
Convert text to numerical vectors for similarity search.

```python
response = openai.Embedding.create(
    model="text-embedding-3-large",
    input="The quick brown fox"
)

embedding = response["data"][0]["embedding"]
print(f"Embedding dimension: {len(embedding)}")  # 3072
```

### 5. **Moderation API**
Content filtering and safety.

```python
response = openai.Moderation.create(
    input="I want to hurt someone"
)

if response["results"][0]["flagged"]:
    print("Content flagged as harmful")
```

---

## API Models & Comparison

| Model | Input Cost | Output Cost | Context | Speed | Best For |
|-------|-----------|------------|---------|-------|----------|
| GPT-4 Turbo | $0.01/1K | $0.03/1K | 128K | Medium | Complex reasoning |
| GPT-4 | $0.03/1K | $0.06/1K | 8K | Slow | High accuracy needed |
| GPT-3.5-turbo | $0.0005/1K | $0.0015/1K | 4K/16K | Fast | Cost-effective |
| text-embedding-3 | Variable | - | - | Fast | Semantic search |
| DALL-E 3 | Variable | - | - | Medium | Image generation |

---

## Installation & Setup

### Prerequisites
- Python 3.7+
- OpenAI API key

### Installation

```bash
# Install OpenAI Python library
pip install openai

# Install dependencies
pip install tiktoken python-dotenv
```

### Authentication

```python
# Method 1: Environment variable
import os
os.environ["OPENAI_API_KEY"] = "sk-..."

# Method 2: Direct
import openai
openai.api_key = "sk-..."

# Method 3: Using client
from openai import OpenAI
client = OpenAI(api_key="sk-...")

# Verify
import openai
models = openai.Model.list()
print(f"Available models: {len(models['data'])}")
```

---

## Beginner Examples

### Example 1: Simple Text Completion

```python
from openai import OpenAI

client = OpenAI()

response = client.completions.create(
    model="gpt-3.5-turbo-instruct",
    prompt="Explain artificial intelligence in one sentence:",
    max_tokens=100,
    temperature=0.7
)

print(response.choices[0].text)
```

### Example 2: Chat-based Conversation

```python
from openai import OpenAI

client = OpenAI()

response = client.chat.completions.create(
    model="gpt-4",
    messages=[
        {"role": "system", "content": "You are a helpful assistant"},
        {"role": "user", "content": "What is machine learning?"}
    ],
    temperature=0.7
)

print(response.choices[0].message.content)
```

### Example 3: Multi-turn Conversation

```python
from openai import OpenAI

client = OpenAI()
messages = []

# Initial system context
messages.append({
    "role": "system",
    "content": "You are a helpful Python programming tutor"
})

# Turn 1
messages.append({"role": "user", "content": "How do I sort a list?"})
response = client.chat.completions.create(model="gpt-4", messages=messages)
print(response.choices[0].message.content)
messages.append({"role": "assistant", "content": response.choices[0].message.content})

# Turn 2
messages.append({"role": "user", "content": "What about descending order?"})
response = client.chat.completions.create(model="gpt-4", messages=messages)
print(response.choices[0].message.content)
```

### Example 4: Using Embeddings

```python
from openai import OpenAI

client = OpenAI()

# Create embeddings
response = client.embeddings.create(
    model="text-embedding-3-small",
    input=["dog", "puppy", "cat", "tree"]
)

# Get embeddings
for i, item in enumerate(response.data):
    print(f"Embedding for item {i}: {item.embedding[:5]}...")  # First 5 dimensions
```

---

## Intermediate Patterns

### Pattern 1: Streaming Responses

```python
from openai import OpenAI

client = OpenAI()

# Stream tokens as they're generated
with client.chat.completions.create(
    model="gpt-4",
    messages=[{"role": "user", "content": "Write a poem about AI"}],
    stream=True
) as stream:
    for text in stream.text_stream:
        print(text, end="", flush=True)
```

### Pattern 2: Token Cost Estimation

```python
import tiktoken
from openai import OpenAI

def estimate_cost(prompt, model="gpt-4"):
    encoding = tiktoken.encoding_for_model(model)
    tokens = len(encoding.encode(prompt))

    # Pricing (2024)
    prices = {
        "gpt-4": {"input": 0.03, "output": 0.06},
        "gpt-3.5-turbo": {"input": 0.0005, "output": 0.0015}
    }

    input_cost = (tokens / 1000) * prices[model]["input"]
    # Estimate output at 150% of input
    output_cost = (tokens * 1.5 / 1000) * prices[model]["output"]

    return input_cost + output_cost

cost = estimate_cost("Tell me about quantum computing")
print(f"Estimated cost: ${cost:.4f}")
```

### Pattern 3: Function Calling (Tool Use)

```python
from openai import OpenAI
import json

client = OpenAI()

# Define available functions
tools = [
    {
        "type": "function",
        "function": {
            "name": "get_user_info",
            "description": "Get information about a user",
            "parameters": {
                "type": "object",
                "properties": {
                    "user_id": {"type": "integer", "description": "User ID"},
                    "include_history": {"type": "boolean"}
                },
                "required": ["user_id"]
            }
        }
    }
]

# User query
messages = [{"role": "user", "content": "Can you get info for user 123?"}]

# Request with tools
response = client.chat.completions.create(
    model="gpt-4",
    messages=messages,
    tools=tools
)

# Check if model wants to call a function
if response.choices[0].message.tool_calls:
    for tool_call in response.choices[0].message.tool_calls:
        if tool_call.function.name == "get_user_info":
            args = json.loads(tool_call.function.arguments)
            print(f"Getting user info for ID: {args['user_id']}")
```

### Pattern 4: Prompt Optimization

```python
from openai import OpenAI

client = OpenAI()

# Poor prompt (ambiguous)
poor_prompt = "Tell me about dogs"

# Better prompt (specific, structured)
better_prompt = """You are a dog breed expert. Provide information about dogs in the following format:
1. Physical characteristics
2. Temperament
3. Care requirements
4. Health concerns

Focus on Golden Retrievers specifically."""

response = client.chat.completions.create(
    model="gpt-4",
    messages=[{"role": "user", "content": better_prompt}],
    temperature=0.5
)

print(response.choices[0].message.content)
```

---

## Advanced Architectures

### Architecture 1: Multi-Model Fallback System

```python
from openai import OpenAI

client = OpenAI()

def query_with_fallback(prompt, max_retries=3):
    models = ["gpt-4", "gpt-3.5-turbo"]

    for model in models:
        try:
            response = client.chat.completions.create(
                model=model,
                messages=[{"role": "user", "content": prompt}],
                timeout=30
            )
            return response.choices[0].message.content, model
        except Exception as e:
            print(f"Model {model} failed: {e}")
            continue

    raise Exception("All models failed")

result, model_used = query_with_fallback("Complex reasoning task")
print(f"Result from {model_used}: {result}")
```

### Architecture 2: Batch Processing for Cost Optimization

```python
from openai import OpenAI
import json

client = OpenAI()

# Prepare batch requests
requests = []
for i, prompt in enumerate(["What is AI?", "What is ML?", "What is DL?"]):
    requests.append({
        "custom_id": f"request-{i}",
        "method": "POST",
        "url": "/v1/chat/completions",
        "body": {
            "model": "gpt-4",
            "messages": [{"role": "user", "content": prompt}],
            "max_tokens": 100
        }
    })

# Save to JSONL
with open("batch_requests.jsonl", "w") as f:
    for req in requests:
        f.write(json.dumps(req) + "\n")

# Submit batch (for bulk processing)
with open("batch_requests.jsonl", "rb") as f:
    batch_file = client.files.create(file=f, purpose="batch")

print(f"Batch file ID: {batch_file.id}")
```

### Architecture 3: Context Management for Long Documents

```python
from openai import OpenAI
import tiktoken

client = OpenAI()

def chunk_document(text, max_tokens=1000, model="gpt-4"):
    encoding = tiktoken.encoding_for_model(model)
    tokens = encoding.encode(text)

    chunks = []
    for i in range(0, len(tokens), max_tokens):
        chunk_tokens = tokens[i:i + max_tokens]
        chunks.append(encoding.decode(chunk_tokens))

    return chunks

def analyze_long_document(document, task):
    chunks = chunk_document(document)
    summaries = []

    # Process each chunk
    for i, chunk in enumerate(chunks):
        response = client.chat.completions.create(
            model="gpt-4",
            messages=[{
                "role": "user",
                "content": f"{task}\n\nDocument chunk {i+1}/{len(chunks)}:\n{chunk}"
            }]
        )
        summaries.append(response.choices[0].message.content)

    # Combine summaries
    combined = "\n\n".join(summaries)

    final_response = client.chat.completions.create(
        model="gpt-4",
        messages=[{
            "role": "user",
            "content": f"Synthesize these summaries into a final answer:\n{combined}"
        }]
    )

    return final_response.choices[0].message.content
```

---

## Best Practices & Optimization

### 1. **Cost Optimization**

```python
# Use appropriate model for task
def get_best_model(task_complexity):
    if task_complexity == "simple":
        return "gpt-3.5-turbo"  # 100x cheaper
    elif task_complexity == "medium":
        return "gpt-3.5-turbo"
    else:
        return "gpt-4"  # 20x more expensive but better quality

# Cache results
from functools import lru_cache

@lru_cache(maxsize=128)
def get_cached_response(prompt):
    response = client.chat.completions.create(
        model="gpt-4",
        messages=[{"role": "user", "content": prompt}]
    )
    return response.choices[0].message.content
```

### 2. **Reliability & Error Handling**

```python
from openai import OpenAI, RateLimitError, APIConnectionError
import time

client = OpenAI()

def robust_api_call(prompt, max_retries=3):
    for attempt in range(max_retries):
        try:
            response = client.chat.completions.create(
                model="gpt-4",
                messages=[{"role": "user", "content": prompt}],
                timeout=30
            )
            return response.choices[0].message.content
        except RateLimitError:
            wait_time = 2 ** attempt  # Exponential backoff
            print(f"Rate limited. Waiting {wait_time}s...")
            time.sleep(wait_time)
        except APIConnectionError as e:
            if attempt == max_retries - 1:
                raise
            time.sleep(2 ** attempt)

    raise Exception("Max retries exceeded")
```

### 3. **Monitoring & Logging**

```python
from openai import OpenAI
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

client = OpenAI()

def monitored_api_call(prompt):
    import time
    start = time.time()

    response = client.chat.completions.create(
        model="gpt-4",
        messages=[{"role": "user", "content": prompt}]
    )

    duration = time.time() - start
    tokens_used = response.usage.total_tokens
    cost = tokens_used * 0.00003  # Rough estimate

    logger.info(f"Query completed in {duration:.2f}s, "
                f"tokens: {tokens_used}, cost: ${cost:.4f}")

    return response.choices[0].message.content
```

---

## Common Pitfalls & Solutions

### Pitfall 1: Exceeding Token Limits

```python
# ❌ Bad: No token checking
response = openai.ChatCompletion.create(
    model="gpt-3.5-turbo",
    messages=[{"role": "user", "content": very_long_document}]
)

# ✅ Good: Check and chunk
import tiktoken

def safe_api_call(text, model="gpt-3.5-turbo"):
    encoding = tiktoken.encoding_for_model(model)
    tokens = len(encoding.encode(text))

    if tokens > 3000:  # Leave buffer for output
        text = text[:len(text) * (3000 // tokens)]

    return client.chat.completions.create(
        model=model,
        messages=[{"role": "user", "content": text}]
    )
```

### Pitfall 2: Inconsistent Responses

```python
# ❌ Bad: Random responses
response = client.chat.completions.create(
    model="gpt-4",
    messages=[{"role": "user", "content": "What is 2+2?"}],
    temperature=0.9
)

# ✅ Good: Deterministic when needed
response = client.chat.completions.create(
    model="gpt-4",
    messages=[{"role": "user", "content": "What is 2+2?"}],
    temperature=0  # Always same answer
)
```

### Pitfall 3: Cost Explosion

```python
# ❌ Bad: No cost tracking
for query in million_queries:
    response = client.chat.completions.create(
        model="gpt-4",  # Expensive!
        messages=[{"role": "user", "content": query}]
    )

# ✅ Good: Cost-aware routing
def cost_aware_query(query, budget=None):
    if budget and budget < 0.01:
        model = "gpt-3.5-turbo"
    else:
        model = "gpt-4"

    response = client.chat.completions.create(
        model=model,
        messages=[{"role": "user", "content": query}]
    )
    return response
```

---

## Comparison with Competitors

| Feature | OpenAI GPT-4 | Claude 3 Opus | Gemini | Llama |
|---------|-------------|---------------|--------|-------|
| **Context** | 128K | 200K | 1M | 32K-100K |
| **Cost** | $0.03-0.06/K | $0.015-0.075/K | Variable | Free (self-host) |
| **Quality** | Excellent | Excellent | Good | Good |
| **Speed** | Medium | Fast | Fast | Fast |
| **Latency** | 1-3s | 0.5-2s | 0.5-2s | Instant |
| **Vision** | Yes | Yes | Yes | Limited |
| **Fine-tuning** | Available | Available | Limited | Available |

---

## Real-World Use Cases

### 1. **Customer Support Chatbot**
- Multi-turn conversations
- Knowledge base integration
- Sentiment analysis
- Handoff to humans

### 2. **Content Generation Pipeline**
- Blog post creation
- Social media scheduling
- Email copywriting
- Product descriptions

### 3. **Code Generation & Review**
- Auto-complete coding
- Code explanation
- Bug detection
- Refactoring suggestions

### 4. **Data Analysis Assistant**
- Query interpretation
- SQL generation
- Result explanation
- Visualization suggestions

### 5. **Personalization Engine**
- Recommendation generation
- User preference learning
- Content adaptation
- Real-time personalization

---

## Performance & Cost Optimization

### Strategy 1: Model Selection

```python
task_costs = {
    "summarization": "gpt-3.5-turbo",  # Simple task
    "translation": "gpt-3.5-turbo",     # Standard task
    "reasoning": "gpt-4",                # Complex task
    "coding": "gpt-4",                   # High accuracy needed
}
```

### Strategy 2: Batch Processing

```python
# 50% cost reduction with batch API
client.batches.create(
    input_file_id="file-123",
    endpoint="/v1/chat/completions",
    completion_window="24h"
)
```

### Strategy 3: Caching

```python
# Use prompt caching (beta) for 90% cost reduction
# on repeated content
```

---

## Conclusion

OpenAI GPT models provide powerful, production-ready AI capabilities. Success depends on:
- Choosing the right model for your task
- Optimizing prompts for quality
- Managing costs through smart routing
- Handling errors gracefully
- Monitoring performance continuously
print(response.choices[0].text)

# Chat completion (GPT-3.5/4)
response = openai.ChatCompletion.create(
    model="gpt-3.5-turbo",
    messages=[
        {"role": "system", "content": "You are a helpful assistant."},
        {"role": "user", "content": "What is Python?"}
    ]
)
print(response.choices[0].message.content)
```

## Advanced Usage

```python
# Streaming responses
response = openai.ChatCompletion.create(
    model="gpt-3.5-turbo",
    messages=[{"role": "user", "content": "Tell me a story"}],
    stream=True
)

for chunk in response:
    if chunk.choices[0].delta.get("content"):
        print(chunk.choices[0].delta.content, end="")

# Function calling
functions = [{
    "name": "get_weather",
    "description": "Get current weather",
    "parameters": {
        "type": "object",
        "properties": {
            "location": {"type": "string"}
        }
    }
}]

response = openai.ChatCompletion.create(
    model="gpt-3.5-turbo",
    messages=[{"role": "user", "content": "What's the weather in NYC?"}],
    functions=functions
)
```

## Best Practices

1. Use appropriate temperature settings (0.7 for creative, 0 for deterministic)
2. Set max_tokens to control response length
3. Implement retry logic for rate limits
4. Use system messages to set behavior
5. Monitor token usage and costs
6. Handle errors gracefully
7. Use streaming for better UX in production

## References

- Official documentation:
- GitHub repository:
