# OpenAI GPT Models - Interview Q&A Guide

## Beginner Level (8 Questions)

### Q1: What is a token and why do I need to count them?

**Answer:**
A token is the smallest unit that GPT models process. Roughly, 1 token ≈ 4 characters or ~0.75 words.

**Why it matters:**
- **Billing**: You pay per token (input + output)
- **Limits**: Each model has maximum token limits (GPT-4: 8K, GPT-4 Turbo: 128K)
- **Cost estimation**: Need to know token count to predict API costs
- **Performance**: More tokens = slower response time

**Code Example:**
```python
import tiktoken
from openai import OpenAI

# Count tokens
encoding = tiktoken.encoding_for_model("gpt-4")
text = "Hello, how are you today?"
tokens = encoding.encode(text)
print(f"Tokens: {len(tokens)}")  # ~5 tokens

# Cost calculation
client = OpenAI()
response = client.chat.completions.create(
    model="gpt-4",
    messages=[{"role": "user", "content": text}]
)
total_tokens = response.usage.total_tokens
cost = total_tokens * (0.00003)  # Approximate
print(f"Cost: ${cost:.4f}")
```

---

### Q2: What does temperature mean in GPT models?

**Answer:**
Temperature controls the randomness of the model's responses on a scale of 0 to 1+.

| Temperature | Behavior | Use Case |
|-------------|----------|----------|
| 0 | Deterministic (same answer) | Math, facts, consistency needed |
| 0.5 | Balanced | General-purpose tasks |
| 0.8 | Creative | Writing, brainstorming |
| 1.0+ | Very random | Creative writing, poetry |

**Code Example:**
```python
from openai import OpenAI

client = OpenAI()

# For factual questions (use low temperature)
response = client.chat.completions.create(
    model="gpt-4",
    messages=[{"role": "user", "content": "What is the capital of France?"}],
    temperature=0  # Always "Paris"
)

# For creative writing (use high temperature)
response = client.chat.completions.create(
    model="gpt-4",
    messages=[{"role": "user", "content": "Write a short poem"}],
    temperature=0.9  # Different each time
)
```

---

### Q3: What is a system prompt and why is it important?

**Answer:**
A system prompt defines the AI model's behavior, role, and constraints. It's like giving the model "instructions" on how to behave.

**Why it's important:**
- Sets the context and tone
- Defines the model's expertise area
- Controls response style
- Improves consistency
- Enables role-playing

**Code Example:**
```python
from openai import OpenAI

client = OpenAI()

# Without system prompt (generic)
response = client.chat.completions.create(
    model="gpt-4",
    messages=[
        {"role": "user", "content": "How do I debug Python?"}
    ]
)

# With system prompt (specific)
response = client.chat.completions.create(
    model="gpt-4",
    messages=[
        {
            "role": "system",
            "content": "You are an expert Python developer with 15 years of experience. "
                      "Provide concise, practical answers with code examples."
        },
        {"role": "user", "content": "How do I debug Python?"}
    ]
)
```

---

### Q4: What are the main differences between GPT-3.5-turbo and GPT-4?

**Answer:**

| Aspect | GPT-3.5-turbo | GPT-4 |
|--------|---------------|-------|
| **Intelligence** | Good | Excellent |
| **Cost** | $0.0005/1K input | $0.03/1K input |
| **Speed** | Fast (1-2s) | Medium (2-3s) |
| **Accuracy** | 90% | 98% |
| **Context** | 4K-16K | 8K-128K |
| **Best for** | Cost-sensitive tasks | Complex reasoning |

**Code Example:**
```python
from openai import OpenAI

client = OpenAI()

# Choose based on task complexity
def select_model(task_type):
    if task_type == "chatbot":
        return "gpt-3.5-turbo"  # Fast, cheap
    elif task_type == "code_review":
        return "gpt-4"  # Accurate
    else:
        return "gpt-3.5-turbo"  # Default to cheap

model = select_model("chatbot")
response = client.chat.completions.create(
    model=model,
    messages=[{"role": "user", "content": "Hello!"}]
)
```

---

### Q5: How do I handle API errors and rate limits?

**Answer:**
Rate limiting happens when you exceed API quotas. Need exponential backoff retry logic.

**Code Example:**
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
            wait_time = 2 ** attempt  # Exponential backoff: 1s, 2s, 4s
            print(f"Rate limited. Waiting {wait_time}s...")
            time.sleep(wait_time)
        except APIConnectionError as e:
            if attempt == max_retries - 1:
                raise
            time.sleep(2 ** attempt)
    
    raise Exception("Max retries exceeded")

result = robust_api_call("Tell me about AI")
```

---

### Q6: What is few-shot learning and how do I use it?

**Answer:**
Few-shot learning teaches the model by providing examples, not by retraining.

**Code Example:**
```python
from openai import OpenAI

client = OpenAI()

# Few-shot example: sentiment classification
response = client.chat.completions.create(
    model="gpt-4",
    messages=[
        {
            "role": "user",
            "content": """Classify the sentiment as positive, negative, or neutral.

Examples:
- "I love this product!" → positive
- "Worst purchase ever" → negative
- "It's a phone" → neutral

Now classify: "The movie was amazing!"
"""
        }
    ]
)

print(response.choices[0].message.content)  # "positive"
```

---

### Q7: How do embeddings work and what are they used for?

**Answer:**
Embeddings convert text into vectors (arrays of numbers) that capture semantic meaning. Used for similarity search and clustering.

**Code Example:**
```python
from openai import OpenAI
import numpy as np

client = OpenAI()

# Create embeddings
texts = ["dog", "puppy", "cat", "tree"]
response = client.embeddings.create(
    model="text-embedding-3-small",
    input=texts
)

# Get vectors
embeddings = [item.embedding for item in response.data]

# Calculate similarity
def cosine_similarity(vec1, vec2):
    return np.dot(vec1, vec2) / (np.linalg.norm(vec1) * np.linalg.norm(vec2))

similarity = cosine_similarity(embeddings[0], embeddings[1])  # dog vs puppy
print(f"Similarity: {similarity:.3f}")  # High similarity (~0.8)
```

---

### Q8: What is streaming and when should I use it?

**Answer:**
Streaming returns tokens one at a time as they're generated instead of waiting for the complete response. Good for user experience.

**Code Example:**
```python
from openai import OpenAI

client = OpenAI()

# Without streaming (wait for complete response)
response = client.chat.completions.create(
    model="gpt-4",
    messages=[{"role": "user", "content": "Tell a story"}],
    stream=False
)
print(response.choices[0].message.content)  # Takes 3-5 seconds

# With streaming (show text as it arrives)
with client.chat.completions.create(
    model="gpt-4",
    messages=[{"role": "user", "content": "Tell a story"}],
    stream=True
) as stream:
    for text in stream.text_stream:
        print(text, end="", flush=True)  # Shows immediately
```

---

## Intermediate Level (8 Questions)

### Q9: How do I implement function calling to make GPT call external APIs?

**Answer:**
Function calling lets GPT decide when to call external tools and what parameters to use.

**Code Example:**
```python
from openai import OpenAI
import json

client = OpenAI()

# Define available functions
tools = [
    {
        "type": "function",
        "function": {
            "name": "get_weather",
            "description": "Get weather for a location",
            "parameters": {
                "type": "object",
                "properties": {
                    "location": {"type": "string", "description": "City name"},
                    "unit": {"type": "string", "enum": ["celsius", "fahrenheit"]}
                },
                "required": ["location"]
            }
        }
    }
]

# Initial request
messages = [{"role": "user", "content": "What's the weather in NYC?"}]
response = client.chat.completions.create(
    model="gpt-4",
    messages=messages,
    tools=tools
)

# Check if GPT wants to call a function
if response.choices[0].message.tool_calls:
    for tool_call in response.choices[0].message.tool_calls:
        if tool_call.function.name == "get_weather":
            args = json.loads(tool_call.function.arguments)
            # Actually call your API
            weather = get_weather_api(args["location"], args.get("unit", "celsius"))
            
            # Send result back to GPT
            messages.append({"role": "assistant", "content": response.choices[0].message.content})
            messages.append({
                "role": "user",
                "content": f"Weather data: {weather}"
            })
            
            # Get final response
            final_response = client.chat.completions.create(
                model="gpt-4",
                messages=messages
            )
```

---

### Q10: What's the best way to manage long conversations and token limits?

**Answer:**
Need to monitor token usage and implement conversation pruning strategies.

**Code Example:**
```python
from openai import OpenAI
import tiktoken

client = OpenAI()
encoding = tiktoken.encoding_for_model("gpt-4")

class ConversationManager:
    def __init__(self, max_tokens=4000, model="gpt-4"):
        self.messages = []
        self.max_tokens = max_tokens
        self.model = model
    
    def add_message(self, role, content):
        self.messages.append({"role": role, "content": content})
    
    def get_token_count(self):
        total = 0
        for msg in self.messages:
            total += len(encoding.encode(msg["content"]))
        return total
    
    def prune_old_messages(self):
        """Remove oldest messages if exceeding limit"""
        while self.get_token_count() > self.max_tokens:
            if len(self.messages) > 1:
                self.messages.pop(0)  # Remove oldest message
    
    def get_response(self, user_input):
        self.add_message("user", user_input)
        self.prune_old_messages()
        
        response = client.chat.completions.create(
            model=self.model,
            messages=self.messages
        )
        
        assistant_message = response.choices[0].message.content
        self.add_message("assistant", assistant_message)
        return assistant_message

# Usage
manager = ConversationManager(max_tokens=3000)
manager.add_message("system", "You are a helpful assistant")
response = manager.get_response("What is AI?")
```

---

### Q11: How should I optimize costs for production applications?

**Answer:**
Use combination of model selection, caching, and batch processing.

**Code Example:**
```python
from openai import OpenAI

client = OpenAI()

class CostOptimizer:
    # Cost per 1K tokens
    COSTS = {
        "gpt-4": {"input": 0.03, "output": 0.06},
        "gpt-3.5-turbo": {"input": 0.0005, "output": 0.0015}
    }
    
    @staticmethod
    def select_model(task_type):
        """Choose model based on task"""
        simple_tasks = ["summarization", "translation", "simple qa"]
        complex_tasks = ["reasoning", "code review", "analysis"]
        
        if task_type in simple_tasks:
            return "gpt-3.5-turbo"  # 100x cheaper
        return "gpt-4"
    
    @staticmethod
    def estimate_cost(prompt, model):
        import tiktoken
        encoding = tiktoken.encoding_for_model(model)
        tokens = len(encoding.encode(prompt))
        input_cost = (tokens / 1000) * CostOptimizer.COSTS[model]["input"]
        # Estimate output at 150% of input
        output_cost = (tokens * 1.5 / 1000) * CostOptimizer.COSTS[model]["output"]
        return input_cost + output_cost

# Usage
task = "summarization"
model = CostOptimizer.select_model(task)
cost = CostOptimizer.estimate_cost("Long document...", model)
print(f"Estimated cost: ${cost:.4f}")
```

---

### Q12: How do I handle sensitive data and maintain privacy with GPT?

**Answer:**
Never send PII/sensitive data. Use techniques like tokenization and local processing.

**Code Example:**
```python
from openai import OpenAI
import re

client = OpenAI()

def anonymize_text(text):
    """Replace sensitive patterns"""
    # Replace emails
    text = re.sub(r'\S+@\S+', '[EMAIL]', text)
    # Replace phone numbers
    text = re.sub(r'\b\d{3}[-.]?\d{3}[-.]?\d{4}\b', '[PHONE]', text)
    # Replace SSN
    text = re.sub(r'\d{3}-\d{2}-\d{4}', '[SSN]', text)
    return text

def process_safely(text):
    # Anonymize first
    safe_text = anonymize_text(text)
    
    # Process with GPT
    response = client.chat.completions.create(
        model="gpt-4",
        messages=[
            {
                "role": "system",
                "content": "Do not output any PII or sensitive information"
            },
            {"role": "user", "content": safe_text}
        ]
    )
    return response.choices[0].message.content

result = process_safely("Customer John Doe with email john@example.com")
```

---

### Q13: What techniques improve response quality and consistency?

**Answer:**
Techniques: prompt engineering, few-shot learning, chain-of-thought, structured outputs.

**Code Example:**
```python
from openai import OpenAI
import json

client = OpenAI()

# Technique 1: Chain-of-thought (make model explain reasoning)
response = client.chat.completions.create(
    model="gpt-4",
    messages=[{
        "role": "user",
        "content": "Solve step by step: If it takes 3 hours to paint a house, "
                  "and you have 2 painters, how long does it take?"
    }]
)

# Technique 2: Structured output with JSON
response = client.chat.completions.create(
    model="gpt-4",
    messages=[{
        "role": "user",
        "content": """Extract information and return JSON:
        {
            "name": "...",
            "age": "...",
            "email": "..."
        }
        
        Text: "John Smith is 30 years old and his email is john@example.com"
        """
    }]
)

output = json.loads(response.choices[0].message.content)

# Technique 3: Temperature tuning
response = client.chat.completions.create(
    model="gpt-4",
    messages=[{"role": "user", "content": "Generate 3 unique product names"}],
    temperature=0.8  # Creative but not too random
)
```

---

### Q14: How do I debug and monitor GPT API usage?

**Answer:**
Log requests, track token usage, monitor costs, and analyze performance metrics.

**Code Example:**
```python
from openai import OpenAI
import logging
import time
from datetime import datetime

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

client = OpenAI()

class APIMonitor:
    def __init__(self):
        self.total_tokens = 0
        self.total_cost = 0
        self.requests = []
    
    def call_with_monitoring(self, prompt, model="gpt-4"):
        start_time = time.time()
        
        response = client.chat.completions.create(
            model=model,
            messages=[{"role": "user", "content": prompt}]
        )
        
        duration = time.time() - start_time
        tokens = response.usage.total_tokens
        cost = tokens * 0.00003  # Approximate
        
        # Log metrics
        self.total_tokens += tokens
        self.total_cost += cost
        
        self.requests.append({
            "timestamp": datetime.now().isoformat(),
            "model": model,
            "tokens": tokens,
            "cost": cost,
            "duration": duration
        })
        
        logger.info(f"API call: {duration:.2f}s, {tokens} tokens, ${cost:.4f}")
        
        return response.choices[0].message.content
    
    def get_summary(self):
        return {
            "total_tokens": self.total_tokens,
            "total_cost": self.total_cost,
            "request_count": len(self.requests),
            "avg_duration": sum(r["duration"] for r in self.requests) / len(self.requests)
        }

# Usage
monitor = APIMonitor()
monitor.call_with_monitoring("What is AI?")
print(monitor.get_summary())
```

---

### Q15: What are common prompt engineering techniques?

**Answer:**
Techniques: clarity, specificity, role-playing, examples, constraints.

**Code Example:**
```python
from openai import OpenAI

client = OpenAI()

# ❌ Bad prompt (vague)
bad_prompt = "Tell me about Python"

# ✅ Good prompt (specific with role and format)
good_prompt = """You are a Python expert teaching beginners.
Explain list comprehensions in Python with:
1. Simple explanation (2 sentences)
2. Code example
3. When to use it

Keep it concise and beginner-friendly."""

response = client.chat.completions.create(
    model="gpt-4",
    messages=[{"role": "user", "content": good_prompt}]
)

# Advanced: Template-based prompts
def generate_with_template(task, context, requirements):
    prompt = f"""Task: {task}

Context:
{context}

Requirements:
{requirements}

Provide a detailed response."""
    
    response = client.chat.completions.create(
        model="gpt-4",
        messages=[{"role": "user", "content": prompt}]
    )
    return response.choices[0].message.content
```

---

## Advanced Level (8 Questions)

### Q16: How would you design a multi-model routing system for optimal cost and performance?

**Answer:**
Implement intelligent routing that selects models based on task complexity, cost constraints, and quality requirements.

**Code Example:**
```python
from openai import OpenAI
import tiktoken
from enum import Enum

class TaskComplexity(Enum):
    SIMPLE = 1
    MEDIUM = 2
    COMPLEX = 3

class ModelRouter:
    MODELS = {
        TaskComplexity.SIMPLE: {
            "model": "gpt-3.5-turbo",
            "cost_per_1k": 0.0005,
            "latency_ms": 500
        },
        TaskComplexity.MEDIUM: {
            "model": "gpt-3.5-turbo",
            "cost_per_1k": 0.0005,
            "latency_ms": 500
        },
        TaskComplexity.COMPLEX: {
            "model": "gpt-4",
            "cost_per_1k": 0.03,
            "latency_ms": 2000
        }
    }
    
    def __init__(self, max_cost_per_request=0.10, max_latency_ms=5000):
        self.max_cost = max_cost_per_request
        self.max_latency = max_latency_ms
    
    def detect_complexity(self, prompt):
        """Analyze prompt to determine complexity"""
        complexity_signals = {
            "reasoning": ["reason", "why", "explain", "analyze"],
            "coding": ["code", "function", "algorithm", "debug"],
            "simple": ["what", "define", "list", "how many"]
        }
        
        prompt_lower = prompt.lower()
        
        if any(word in prompt_lower for word in complexity_signals["coding"]):
            return TaskComplexity.COMPLEX
        elif any(word in prompt_lower for word in complexity_signals["reasoning"]):
            return TaskComplexity.COMPLEX
        else:
            return TaskComplexity.MEDIUM
    
    def route(self, prompt, strict_cost=False):
        """Select best model"""
        complexity = self.detect_complexity(prompt)
        model_config = self.MODELS[complexity]
        
        # Can override to cheaper model if cost is critical
        if strict_cost and model_config["cost_per_1k"] > self.max_cost:
            return self.MODELS[TaskComplexity.SIMPLE]["model"]
        
        return model_config["model"]

# Usage
router = ModelRouter(max_cost_per_request=0.05)
model = router.route("Write a complex algorithm")  # Routes to gpt-4
```

---

### Q17: How would you implement RAG (Retrieval Augmented Generation) with OpenAI?

**Answer:**
Combine document retrieval with GPT to ground responses in specific knowledge.

**Code Example:**
```python
from openai import OpenAI
from sklearn.feature_extraction.text import TfidfVectorizer
import numpy as np

client = OpenAI()

class RAGSystem:
    def __init__(self, documents):
        self.documents = documents
        self.vectorizer = TfidfVectorizer()
        self.vectors = self.vectorizer.fit_transform(documents)
    
    def retrieve(self, query, top_k=3):
        """Find most relevant documents"""
        query_vector = self.vectorizer.transform([query])
        similarities = (self.vectors * query_vector.T).toarray().flatten()
        top_indices = np.argsort(similarities)[-top_k:][::-1]
        return [self.documents[i] for i in top_indices]
    
    def answer(self, query):
        """Retrieve documents and generate answer"""
        # Step 1: Retrieve relevant documents
        relevant_docs = self.retrieve(query, top_k=3)
        context = "\n".join(relevant_docs)
        
        # Step 2: Generate answer with context
        response = client.chat.completions.create(
            model="gpt-4",
            messages=[
                {
                    "role": "system",
                    "content": "You are a helpful assistant. Answer based on the provided context."
                },
                {
                    "role": "user",
                    "content": f"""Context:
{context}

Question: {query}

Answer based only on the context above."""
                }
            ]
        )
        
        return response.choices[0].message.content

# Usage
docs = [
    "Python is a programming language",
    "Machine learning uses algorithms",
    "Data science analyzes data"
]
rag = RAGSystem(docs)
answer = rag.answer("What is Python?")
```

---

### Q18: How do you handle edge cases like context window overflow and invalid outputs?

**Answer:**
Implement validation, chunking, and fallback strategies.

**Code Example:**
```python
from openai import OpenAI
import json
import tiktoken

client = OpenAI()

class RobustGPTHandler:
    def __init__(self, model="gpt-4"):
        self.model = model
        self.encoding = tiktoken.encoding_for_model(model)
        self.max_tokens = 8000
    
    def chunk_if_needed(self, text, reserve_tokens=500):
        """Chunk text if it exceeds limits"""
        tokens = self.encoding.encode(text)
        max_input_tokens = self.max_tokens - reserve_tokens
        
        if len(tokens) > max_input_tokens:
            chunks = []
            for i in range(0, len(tokens), max_input_tokens):
                chunk_tokens = tokens[i:i + max_input_tokens]
                chunks.append(self.encoding.decode(chunk_tokens))
            return chunks
        return [text]
    
    def validate_response(self, response, expected_format=None):
        """Validate response format"""
        content = response.choices[0].message.content
        
        if expected_format == "json":
            try:
                return json.loads(content)
            except json.JSONDecodeError:
                return {"error": "Invalid JSON response"}
        
        return content
    
    def safe_call(self, prompt, expected_format=None):
        """Safe API call with error handling"""
        try:
            chunks = self.chunk_if_needed(prompt)
            
            for chunk in chunks:
                response = client.chat.completions.create(
                    model=self.model,
                    messages=[{"role": "user", "content": chunk}]
                )
                
                validated = self.validate_response(response, expected_format)
                if not (isinstance(validated, dict) and "error" in validated):
                    return validated
            
            return None
        except Exception as e:
            return {"error": str(e)}

# Usage
handler = RobustGPTHandler()
result = handler.safe_call("Process this large document...", expected_format="json")
```

---

### Q19: What strategies would you use for fine-tuning GPT models for specific domains?

**Answer:**
Prepare training data, monitor metrics, and validate on held-out test set.

**Code Example:**
```python
import json
from openai import OpenAI

client = OpenAI()

class FineTuningPipeline:
    @staticmethod
    def prepare_training_data(examples):
        """Format data for fine-tuning"""
        training_data = []
        for example in examples:
            training_data.append({
                "messages": [
                    {"role": "system", "content": "You are an expert"},
                    {"role": "user", "content": example["input"]},
                    {"role": "assistant", "content": example["output"]}
                ]
            })
        return training_data
    
    @staticmethod
    def save_training_file(data, filename):
        """Save in JSONL format"""
        with open(filename, "w") as f:
            for example in data:
                f.write(json.dumps(example) + "\n")
    
    @staticmethod
    def submit_fine_tune(training_file, model="gpt-3.5-turbo"):
        """Submit fine-tuning job"""
        # First upload the file
        with open(training_file, "rb") as f:
            file_response = client.files.create(
                file=f,
                purpose="fine-tune"
            )
        
        # Create fine-tuning job
        fine_tune = client.fine_tuning.jobs.create(
            training_file=file_response.id,
            model=model,
            hyperparameters={"n_epochs": 3}
        )
        
        return fine_tune.id
    
    @staticmethod
    def monitor_job(job_id):
        """Monitor fine-tuning progress"""
        job = client.fine_tuning.jobs.retrieve(job_id)
        return {
            "status": job.status,
            "trained_tokens": job.trained_tokens,
            "fine_tuned_model": job.fine_tuned_model
        }

# Usage
examples = [
    {"input": "Classify: great product", "output": "positive"},
    {"input": "Classify: terrible experience", "output": "negative"}
]
data = FineTuningPipeline.prepare_training_data(examples)
FineTuningPipeline.save_training_file(data, "training.jsonl")
job_id = FineTuningPipeline.submit_fine_tune("training.jsonl")
```

---

### Q20: How would you implement vision capabilities with GPT-4 for image analysis?

**Answer:**
Use gpt-4-vision to analyze images alongside text.

**Code Example:**
```python
from openai import OpenAI
import base64

client = OpenAI()

class VisionAnalyzer:
    @staticmethod
    def encode_image(image_path):
        """Encode image to base64"""
        with open(image_path, "rb") as image_file:
            return base64.b64encode(image_file.read()).decode('utf-8')
    
    @staticmethod
    def analyze_image(image_path, query):
        """Analyze image with vision model"""
        base64_image = VisionAnalyzer.encode_image(image_path)
        
        response = client.chat.completions.create(
            model="gpt-4-vision-preview",
            messages=[
                {
                    "role": "user",
                    "content": [
                        {"type": "text", "text": query},
                        {
                            "type": "image_url",
                            "image_url": {
                                "url": f"data:image/jpeg;base64,{base64_image}"
                            }
                        }
                    ]
                }
            ]
        )
        
        return response.choices[0].message.content
    
    @staticmethod
    def analyze_from_url(image_url, query):
        """Analyze image from URL"""
        response = client.chat.completions.create(
            model="gpt-4-vision-preview",
            messages=[
                {
                    "role": "user",
                    "content": [
                        {"type": "text", "text": query},
                        {
                            "type": "image_url",
                            "image_url": {"url": image_url}
                        }
                    ]
                }
            ]
        )
        
        return response.choices[0].message.content

# Usage
analysis = VisionAnalyzer.analyze_from_url(
    "https://example.com/image.jpg",
    "What objects are in this image?"
)
print(analysis)
```

---

### Q21: How would you design a production-grade GPT application with caching, batching, and monitoring?

**Answer:**
Combine multiple optimization techniques for reliability and cost efficiency.

**Code Example:**
```python
from openai import OpenAI
from functools import lru_cache
import logging
from datetime import datetime

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

client = OpenAI()

class ProductionGPTApp:
    def __init__(self, cache_size=1000):
        self.cache_size = cache_size
        self.metrics = {
            "total_requests": 0,
            "cache_hits": 0,
            "total_tokens": 0,
            "total_cost": 0
        }
    
    @lru_cache(maxsize=1000)
    def cached_query(self, prompt, temperature=0):
        """Cached API calls"""
        response = client.chat.completions.create(
            model="gpt-4",
            messages=[{"role": "user", "content": prompt}],
            temperature=temperature
        )
        return response.choices[0].message.content
    
    def query(self, prompt, use_cache=True):
        """Main query method"""
        self.metrics["total_requests"] += 1
        
        # Try cache first
        if use_cache:
            cached_result = self.cached_query.__cache_info__()
            if cached_result.hits > self.metrics["cache_hits"]:
                self.metrics["cache_hits"] += 1
                logger.info("Cache hit")
                return self.cached_query(prompt)
        
        # Fresh query
        response = client.chat.completions.create(
            model="gpt-4",
            messages=[{"role": "user", "content": prompt}]
        )
        
        tokens = response.usage.total_tokens
        cost = tokens * 0.00003
        
        self.metrics["total_tokens"] += tokens
        self.metrics["total_cost"] += cost
        
        logger.info(f"Request completed: {tokens} tokens, ${cost:.4f}")
        
        return response.choices[0].message.content
    
    def get_metrics(self):
        """Get performance metrics"""
        return {
            **self.metrics,
            "cache_hit_rate": (self.metrics["cache_hits"] / 
                             max(self.metrics["total_requests"], 1) * 100)
        }

# Usage
app = ProductionGPTApp()
result = app.query("What is AI?")
print(app.get_metrics())
```

---

### Q22: How would you implement semantic search and knowledge management with embeddings?

**Answer:**
Use embeddings to build a searchable knowledge base.

**Code Example:**
```python
from openai import OpenAI
import numpy as np

client = OpenAI()

class KnowledgeBase:
    def __init__(self):
        self.documents = []
        self.embeddings = []
    
    def add_documents(self, docs):
        """Add documents and compute embeddings"""
        response = client.embeddings.create(
            model="text-embedding-3-small",
            input=docs
        )
        
        self.documents = docs
        self.embeddings = [item.embedding for item in response.data]
    
    def search(self, query, top_k=3):
        """Find most similar documents"""
        # Get query embedding
        query_response = client.embeddings.create(
            model="text-embedding-3-small",
            input=[query]
        )
        query_embedding = query_response.data[0].embedding
        
        # Calculate similarities
        similarities = []
        for embedding in self.embeddings:
            similarity = np.dot(query_embedding, embedding) / (
                np.linalg.norm(query_embedding) * np.linalg.norm(embedding)
            )
            similarities.append(similarity)
        
        # Return top-k
        top_indices = np.argsort(similarities)[-top_k:][::-1]
        return [(self.documents[i], similarities[i]) for i in top_indices]

# Usage
kb = KnowledgeBase()
kb.add_documents([
    "Python is a programming language",
    "Machine learning is a subset of AI",
    "Neural networks are inspired by biology"
])
results = kb.search("What about programming?", top_k=2)
for doc, score in results:
    print(f"{score:.2f}: {doc}")
```

---

### Q23: What are the key differences between OpenAI GPT and other LLMs, and how do you choose?

**Answer:**
Compare on quality, cost, speed, context, customization, and availability.

| Factor | OpenAI GPT-4 | Claude | Gemini | Llama |
|--------|-------------|--------|--------|-------|
| Quality | Excellent | Excellent | Good | Good |
| Cost | High | Medium | Variable | Free |
| Speed | Medium | Fast | Fast | Fast |
| Context | 128K | 200K | 1M | 32K-100K |
| Fine-tune | Yes | Limited | Limited | Yes |
| Self-hosted | No | No | No | Yes |

**Code Example:**
```python
from enum import Enum

class LLMChoice:
    CRITERIA = {
        "quality": {"weight": 0.4},
        "cost": {"weight": 0.2},
        "speed": {"weight": 0.2},
        "context": {"weight": 0.1},
        "customization": {"weight": 0.1}
    }
    
    SCORES = {
        "gpt-4": {"quality": 10, "cost": 3, "speed": 5, "context": 9, "customization": 8},
        "claude": {"quality": 9, "cost": 6, "speed": 8, "context": 10, "customization": 5},
        "gemini": {"quality": 8, "cost": 7, "speed": 8, "context": 10, "customization": 4}
    }
    
    @classmethod
    def recommend(cls, requirements):
        """Recommend model based on requirements"""
        best_score = -1
        best_model = None
        
        for model, scores in cls.SCORES.items():
            score = sum(
                scores[criterion] * cls.CRITERIA[criterion]["weight"]
                for criterion in cls.CRITERIA
            )
            if score > best_score:
                best_score = score
                best_model = model
        
        return best_model

# Usage
recommendation = LLMChoice.recommend({})
print(f"Recommended model: {recommendation}")
```

---

## Key Takeaways

**Beginner Foundation:**
- Tokens determine cost and limits
- Temperature controls randomness
- System prompts define behavior
- Model selection matters for cost

**Intermediate Skills:**
- Function calling enables tool use
- Token management for long conversations
- Cost optimization through routing
- Privacy and security best practices

**Advanced Mastery:**
- Multi-model routing systems
- RAG for grounded generation
- Fine-tuning for domain specialization
- Production-grade architectures with caching and monitoring
- Vision capabilities for multimodal understanding

**Remember:** Start simple, optimize based on metrics, and iterate continuously.
