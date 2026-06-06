# FastAPI - Complete Guide (Basic to Advanced)

## 🎯 What is FastAPI?

**FastAPI** is a modern, fast (high-performance) web framework for building APIs with Python 3.7+ based on standard Python type hints. It's the framework you use in Modules 04 and 05 for your ML APIs.

### Why FastAPI?
- **Fast**: One of the fastest Python frameworks (comparable to Node.js)
- **Easy**: Simple to use, learn, and code
- **Type Safety**: Built on Python type hints
- **Auto Docs**: Automatic interactive API documentation
- **Modern**: Based on latest standards (OpenAPI, JSON Schema)

---

## 📚 Learning Path: Basic → Intermediate → Advanced

---

## 🟢 LEVEL 1: BASIC (Getting Started)

### Basic FastAPI Application

```python
from fastapi import FastAPI

app = FastAPI()

@app.get("/")
def read_root():
    return {"message": "Hello World"}

@app.get("/items/{item_id}")
def read_item(item_id: int):
    return {"item_id": item_id}
```

### Key Concepts

#### 1. **Routes & Endpoints**
```python
@app.get("/users")      # GET request
@app.post("/users")     # POST request
@app.put("/users/{id}") # PUT request
@app.delete("/users/{id}") # DELETE request
```

#### 2. **Path Parameters**
```python
@app.get("/items/{item_id}")
def get_item(item_id: int):  # Type hint = validation
    return {"item_id": item_id}
```

#### 3. **Query Parameters**
```python
@app.get("/items")
def get_items(skip: int = 0, limit: int = 10):
    return {"skip": skip, "limit": limit}
```

#### 4. **Request Body**
```python
from pydantic import BaseModel

class Item(BaseModel):
    name: str
    price: float

@app.post("/items")
def create_item(item: Item):
    return {"item": item}
```

### Basic Example: ML Prediction API

```python
from fastapi import FastAPI
from pydantic import BaseModel
import joblib

app = FastAPI(title="ML Prediction API")

# Load model
model = joblib.load("model.pkl")

class PredictionRequest(BaseModel):
    feature1: float
    feature2: float

@app.post("/predict")
def predict(request: PredictionRequest):
    prediction = model.predict([[request.feature1, request.feature2]])
    return {"prediction": float(prediction[0])}
```

---

## 🟡 LEVEL 2: INTERMEDIATE (Production Patterns)

### Dependency Injection

```python
from fastapi import Depends

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

@app.get("/users")
def get_users(db: Session = Depends(get_db)):
    return db.query(User).all()
```

### Error Handling

```python
from fastapi import HTTPException

@app.get("/items/{item_id}")
def get_item(item_id: int):
    if item_id not in items:
        raise HTTPException(status_code=404, detail="Item not found")
    return items[item_id]
```

### Background Tasks

```python
from fastapi import BackgroundTasks

def log_prediction(prediction: dict):
    # Log to database
    pass

@app.post("/predict")
def predict(request: PredictionRequest, background_tasks: BackgroundTasks):
    prediction = model.predict([[request.feature1, request.feature2]])
    result = {"prediction": float(prediction[0])}
    
    background_tasks.add_task(log_prediction, result)
    return result
```

### Async/Await

```python
import asyncio
from fastapi import FastAPI

@app.get("/async-endpoint")
async def async_endpoint():
    # Async operations
    result = await some_async_function()
    return result
```

### Middleware

```python
from fastapi import Request
import time

@app.middleware("http")
async def add_process_time_header(request: Request, call_next):
    start_time = time.time()
    response = await call_next(request)
    process_time = time.time() - start_time
    response.headers["X-Process-Time"] = str(process_time)
    return response
```

### CORS

```python
from fastapi.middleware.cors import CORSMiddleware

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production, specify domains
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
```

---

## 🔴 LEVEL 3: ADVANCED (Production Excellence)

### Advanced Request Validation

```python
from pydantic import BaseModel, Field, validator
from typing import List, Optional

class PredictionRequest(BaseModel):
    customer_id: str = Field(..., min_length=1, max_length=50)
    features: List[float] = Field(..., min_items=5, max_items=20)
    timestamp: Optional[str] = None
    
    @validator('features')
    def validate_features(cls, v):
        if any(x < 0 or x > 1 for x in v):
            raise ValueError('Features must be between 0 and 1')
        return v
```

### Response Models

```python
class PredictionResponse(BaseModel):
    customer_id: str
    prediction: float
    confidence: float
    timestamp: str

@app.post("/predict", response_model=PredictionResponse)
def predict(request: PredictionRequest):
    # Your logic
    return PredictionResponse(...)
```

### WebSockets

```python
from fastapi import WebSocket

@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    await websocket.accept()
    while True:
        data = await websocket.receive_text()
        await websocket.send_text(f"Message: {data}")
```

### File Uploads

```python
from fastapi import UploadFile, File

@app.post("/upload")
async def upload_file(file: UploadFile = File(...)):
    contents = await file.read()
    # Process file
    return {"filename": file.filename}
```

### Security

```python
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from fastapi import Depends, HTTPException, status

security = HTTPBearer()

def verify_token(credentials: HTTPAuthorizationCredentials = Depends(security)):
    token = credentials.credentials
    if not is_valid_token(token):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid token"
        )
    return token

@app.get("/protected")
def protected_route(token: str = Depends(verify_token)):
    return {"message": "Access granted"}
```

### Database Integration

```python
from sqlalchemy.orm import Session
from fastapi import Depends

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

@app.post("/users")
def create_user(user: UserCreate, db: Session = Depends(get_db)):
    db_user = User(**user.dict())
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    return db_user
```

### Testing

```python
from fastapi.testclient import TestClient

client = TestClient(app)

def test_predict():
    response = client.post(
        "/predict",
        json={"feature1": 1.0, "feature2": 2.0}
    )
    assert response.status_code == 200
    assert "prediction" in response.json()
```

---

## 🏗️ Architecture Patterns

### Pattern 1: Simple API
```
Client → FastAPI → Model → Response
```

### Pattern 2: API with Database
```
Client → FastAPI → Database → Response
```

### Pattern 3: API with Caching
```
Client → FastAPI → Cache → (if miss) → Model → Cache → Response
```

### Pattern 4: Microservices
```
Client → API Gateway → FastAPI Service 1
                    → FastAPI Service 2
                    → FastAPI Service 3
```

---

## 🔗 Integration with Your POCs

### Module 04: ML Pipeline
- **File**: `04-End-to-End-ML-Pipeline/src/api_server.py`
- **Usage**: Serves churn prediction model
- **Features**: Single and batch predictions, health checks

### Module 05: RAG System
- **File**: `05-Generative-AI-RAG/src/api_server.py`
- **Usage**: Serves RAG queries
- **Features**: Query endpoint, pipeline building

---

## 📊 Best Practices

### 1. **Use Type Hints**
```python
def predict(features: List[float]) -> Dict[str, float]:
    # Type hints enable validation
```

### 2. **Use Pydantic Models**
```python
# Automatic validation and serialization
class Request(BaseModel):
    field: str
```

### 3. **Handle Errors Properly**
```python
try:
    result = process()
except ValueError as e:
    raise HTTPException(status_code=400, detail=str(e))
```

### 4. **Use Dependency Injection**
```python
# Reusable dependencies
def get_model():
    return load_model()
```

### 5. **Add Logging**
```python
import logging
logger = logging.getLogger(__name__)

@app.post("/predict")
def predict(request: PredictionRequest):
    logger.info(f"Prediction request: {request.customer_id}")
    # ...
```

---

## 🎯 Key Takeaways

1. **FastAPI = Fast + Type-Safe + Auto-Docs**
2. **Pydantic = Validation + Serialization**
3. **Dependencies = Reusable Logic**
4. **Async = Better Performance**
5. **Type Hints = Better Code**

---

## 📚 Next Steps

1. ✅ Read this guide
2. 📊 Review `Visual.md` for flows
3. 💬 Practice `Interview.md` questions
4. 🏗️ Build with Module 04/05
5. 🎯 Explain it confidently

