# LLMOps Guide – Basic → Architect

## Level 1 – Launch & Basics

### 1. **Model Deployment**
```python
from fastapi import FastAPI
import openai

app = FastAPI()

@app.post("/chat")
def chat(message: str):
    response = openai.ChatCompletion.create(
        model="gpt-4",
        messages=[{"role": "user", "content": message}]
    )
    return {"response": response.choices[0].message.content}
```

### 2. **Prompt Management**
```python
prompts = {
    "summarize": "Summarize the following text: {text}",
    "translate": "Translate to {language}: {text}"
}

def get_prompt(task, **kwargs):
    return prompts[task].format(**kwargs)
```

## Level 2 – Production Patterns

### RAG System
```python
from langchain.vectorstores import Chroma
from langchain.chains import RetrievalQA

vectorstore = Chroma.from_documents(documents, embeddings)
qa = RetrievalQA.from_chain_type(
    llm=llm,
    retriever=vectorstore.as_retriever()
)
```

### Model Monitoring
```python
import wandb

wandb.init(project="llm-monitoring")

wandb.log({
    "prediction": prediction,
    "ground_truth": true_value,
    "latency": latency,
    "cost": cost
})
```

## Level 3 – Architect Playbook

### Agent Systems
```python
from langchain.agents import initialize_agent

agent = initialize_agent(
    tools,
    llm,
    agent=AgentType.ZERO_SHOT_REACT_DESCRIPTION
)

result = agent.run("What is the weather?")
```

## Ops Cheat Sheet

| Task | Tool | Notes |
| --- | --- | --- |
| Deploy | FastAPI, Flask | Serve model |
| Monitor | W&B, MLflow | Track metrics |
| Test | pytest | Test system |

## Checklist Before Production

- [ ] Set up proper prompt management
- [ ] Implement RAG if needed
- [ ] Set up monitoring
- [ ] Configure cost tracking
- [ ] Implement error handling
- [ ] Set up rate limiting
- [ ] Test thoroughly
- [ ] Document system
