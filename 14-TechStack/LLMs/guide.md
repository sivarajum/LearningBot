# LLMs Guide – Basic → Architect

## Level 1 – Launch & Basics

### 1. **OpenAI API**
```python
import openai

openai.api_key = "your-key"

response = openai.ChatCompletion.create(
    model="gpt-4",
    messages=[{"role": "user", "content": "Hello"}]
)

print(response.choices[0].message.content)
```

### 2. **Hugging Face**
```python
from transformers import pipeline

generator = pipeline("text-generation", model="gpt2")
result = generator("Hello, I am", max_length=50)
```

### 3. **Embeddings**
```python
from sentence_transformers import SentenceTransformer

model = SentenceTransformer('all-MiniLM-L6-v2')
embeddings = model.encode(["Hello world", "Hi there"])
```

## Level 2 – Production Patterns

### Fine-Tuning
```python
from transformers import Trainer, TrainingArguments

training_args = TrainingArguments(
    output_dir='./results',
    num_train_epochs=3
)

trainer = Trainer(
    model=model,
    args=training_args,
    train_dataset=train_dataset
)

trainer.train()
```

### Prompt Engineering
```python
prompt = """
You are a helpful assistant. Answer the following question:

Question: {question}

Answer:
"""

formatted = prompt.format(question="What is AI?")
response = llm(formatted)
```

## Level 3 – Architect Playbook

### Multi-Modal
```python
from openai import OpenAI

client = OpenAI()

response = client.chat.completions.create(
    model="gpt-4-vision-preview",
    messages=[{
        "role": "user",
        "content": [
            {"type": "text", "text": "What's in this image?"},
            {"type": "image_url", "image_url": {"url": "https://..."}}
        ]
    }]
)
```

## Ops Cheat Sheet

| Task | Tool | Notes |
| --- | --- | --- |
| Generate | OpenAI API | Text generation |
| Embed | Sentence Transformers | Create embeddings |
| Fine-tune | Hugging Face | Customize model |

## Architecture Patterns

```mermaid
flowchart LR
  Data[Data (text/code)] --> Embed[Embeddings/Vector DB]
  Data --> Train[Fine-tune / RAG Prep]
  Query[User Query] --> Router[Prompt/Routing Layer]
  Router --> LLM[Model (Hosted/Open Source)]
  Embed --> RAG[RAG Retriever]
  RAG --> LLM
  LLM --> Post[Post-processing/Guardrails]
  LLM --> Obs[Logging/Telemetry/Safety]
```

## Checklist Before Production

- [ ] Choose appropriate model (quality/latency/cost constraints)
- [ ] Prompt/routing tuned; guardrails for safety
- [ ] API keys/credentials managed securely
- [ ] Error handling, retries, and timeouts in clients
- [ ] Observability: logs/metrics/traces; capture prompts/errors
- [ ] Cost tracking and rate limits; quotas enforced
- [ ] Red-team/safety tests; evals on target tasks
- [ ] Document usage and known limitations
