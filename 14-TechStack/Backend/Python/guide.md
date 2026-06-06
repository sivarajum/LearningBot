# Python Backend Guide – Basic → Architect

## Level 1 – Launch & Basics

### 1. **Flask Basics**
```python
from flask import Flask

app = Flask(__name__)

@app.route('/')
def hello():
    return {'message': 'Hello World'}

if __name__ == '__main__':
    app.run(debug=True)
```

### 2. **FastAPI Basics**
```python
from fastapi import FastAPI

app = FastAPI()

@app.get("/")
def read_root():
    return {"message": "Hello World"}
```

### 3. **Database Integration**
```python
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

engine = create_engine("postgresql://user:pass@localhost/db")
Session = sessionmaker(bind=engine)
session = Session()
```

## Level 2 – Production Patterns

### Async Operations
```python
from fastapi import FastAPI
import asyncio

app = FastAPI()

@app.get("/async")
async def async_endpoint():
    result = await long_running_task()
    return {"result": result}
```

### Background Tasks
```python
from fastapi import BackgroundTasks

@app.post("/task")
def create_task(background_tasks: BackgroundTasks):
    background_tasks.add_task(process_data, data)
    return {"status": "processing"}
```

## Level 3 – Architect Playbook

### Microservices
```python
import httpx

async def call_service(url: str):
    async with httpx.AsyncClient() as client:
        response = await client.get(url)
        return response.json()
```

## Ops Cheat Sheet

| Task | Command | Notes |
| --- | --- | --- |
| Run Flask | `flask run` | Development server |
| Run FastAPI | `uvicorn main:app --reload` | Development server |
| Install | `pip install -r requirements.txt` | Install dependencies |

## Checklist Before Production

- [ ] Set up proper error handling
- [ ] Implement authentication
- [ ] Configure environment variables
- [ ] Set up logging
- [ ] Implement rate limiting
- [ ] Set up database pooling
- [ ] Configure HTTPS
- [ ] Set up CI/CD
