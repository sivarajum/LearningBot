# FastAPI - Interview Questions (Basic to Advanced)

## 🎯 Interview Preparation Guide

Practice these questions to ace your FastAPI interviews. Answers connect to your POC projects.

---

## 🟢 BASIC LEVEL Questions

### Q1: What is FastAPI and why use it?

**Answer:**
"FastAPI is a modern Python web framework for building APIs. It's built on Python type hints and uses Pydantic for data validation. I chose it for Modules 04 and 05 because:

1. **Performance**: One of the fastest Python frameworks
2. **Type Safety**: Automatic validation with type hints
3. **Auto Documentation**: Swagger UI and ReDoc automatically generated
4. **Easy to Use**: Simple syntax, great developer experience
5. **Async Support**: Built-in async/await for better performance

In Module 04, I used it to serve my ML model with sub-100ms latency, and the automatic validation caught errors before they reached the model."

**Key Points:**
- Fast performance
- Type hints = validation
- Auto docs
- Async support

---

### Q2: How does FastAPI handle request validation?

**Answer:**
"FastAPI uses Pydantic models for automatic validation. When you define a request model with type hints, FastAPI automatically validates incoming requests.

Example from Module 04:
```python
class PredictionRequest(BaseModel):
    customer_id: str
    feature1: float = Field(..., ge=0, le=1)
    feature2: int = Field(..., ge=0)
```

If a request doesn't match the schema, FastAPI returns a 422 validation error with details about what's wrong. This happens before your handler function is called, so invalid data never reaches your business logic."

**Key Points:**
- Pydantic models
- Automatic validation
- Type hints
- Error messages

---

### Q3: What's the difference between path parameters and query parameters?

**Answer:**
"Path parameters are part of the URL path, while query parameters come after `?` in the URL.

**Path Parameters:**
```python
@app.get("/users/{user_id}")
def get_user(user_id: int):  # user_id is in the path
    return {"user_id": user_id}
# URL: /users/123
```

**Query Parameters:**
```python
@app.get("/users")
def get_users(skip: int = 0, limit: int = 10):  # skip, limit are query params
    return {"skip": skip, "limit": limit}
# URL: /users?skip=0&limit=10
```

Path parameters are required and identify a resource. Query parameters are optional and used for filtering, pagination, etc."

**Key Points:**
- Path = required, identifies resource
- Query = optional, filtering/pagination

---

## 🟡 INTERMEDIATE LEVEL Questions

### Q4: How do you handle dependencies in FastAPI?

**Answer:**
"FastAPI uses dependency injection. You define a dependency function and use `Depends()` to inject it into route handlers.

Example from Module 04:
```python
def get_model():
    model = joblib.load("model.pkl")
    return model

@app.post("/predict")
def predict(request: PredictionRequest, model = Depends(get_model)):
    return model.predict([request.features])
```

Benefits:
- **Reusability**: Use same dependency in multiple routes
- **Testing**: Easy to mock dependencies
- **Lifecycle Management**: Dependencies can have setup/teardown (like DB connections)

For database connections, I use:
```python
def get_db():
    db = SessionLocal()
    try:
        yield db  # Generator = cleanup after use
    finally:
        db.close()
```"

**Key Points:**
- Dependency injection
- Reusability
- Testing
- Lifecycle management

---

### Q5: How does async/await work in FastAPI?

**Answer:**
"FastAPI supports async handlers. When you use `async def`, FastAPI runs the handler in an async context, allowing non-blocking I/O operations.

**Sync (Blocking):**
```python
@app.get("/data")
def get_data():
    result = slow_database_query()  # Blocks until complete
    return result
```

**Async (Non-blocking):**
```python
@app.get("/data")
async def get_data():
    result = await async_database_query()  # Doesn't block
    return result
```

In async mode, while waiting for the database, FastAPI can handle other requests. This significantly improves throughput.

In Module 05, I use async for the RAG API because it makes multiple async calls (vector search, LLM API), and async allows them to run concurrently."

**Key Points:**
- Non-blocking I/O
- Better concurrency
- Use for I/O-bound operations

---

### Q6: How do you handle errors in FastAPI?

**Answer:**
"FastAPI has built-in exception handling. You can raise `HTTPException` for specific status codes:

```python
from fastapi import HTTPException

@app.get("/items/{item_id}")
def get_item(item_id: int):
    if item_id not in items:
        raise HTTPException(
            status_code=404,
            detail="Item not found"
        )
    return items[item_id]
```

For global exception handling, use exception handlers:
```python
@app.exception_handler(ValueError)
async def value_error_handler(request, exc):
    return JSONResponse(
        status_code=400,
        content={"detail": str(exc)}
    )
```

In Module 04, I use this pattern to handle model prediction errors gracefully and return meaningful error messages to clients."

**Key Points:**
- HTTPException for specific errors
- Exception handlers for global handling
- Meaningful error messages

---

## 🔴 ADVANCED LEVEL Questions

### Q7: How would you design a scalable FastAPI application?

**Answer:**
"Here's my architecture:

**1. Application Structure:**
```
app/
├── main.py          # FastAPI app
├── routers/         # Route modules
├── models/          # Pydantic models
├── services/        # Business logic
├── dependencies/    # Dependency functions
└── utils/           # Utilities
```

**2. Horizontal Scaling:**
- Run multiple FastAPI instances behind a load balancer
- Use stateless design (no in-memory state)
- Shared database/cache for state

**3. Caching:**
- Redis for response caching
- Cache frequent predictions
- Cache database queries

**4. Database:**
- Connection pooling
- Read replicas for read-heavy workloads
- Async database drivers

**5. Monitoring:**
- Health check endpoints
- Metrics collection (Prometheus)
- Logging (structured logs)

**6. Deployment:**
- Docker containers
- Kubernetes or Cloud Run
- Auto-scaling based on traffic

In Module 04, I implemented this with Docker, Cloud Run auto-scaling, and Redis caching, achieving 1000+ requests/minute capacity."

**Key Points:**
- Stateless design
- Horizontal scaling
- Caching strategy
- Monitoring

---

### Q8: How do you implement authentication and authorization?

**Answer:**
"**Authentication (Who are you?):**

```python
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from fastapi import Depends, HTTPException

security = HTTPBearer()

def verify_token(credentials: HTTPAuthorizationCredentials = Depends(security)):
    token = credentials.credentials
    if not is_valid_token(token):
        raise HTTPException(status_code=401, detail="Invalid token")
    return decode_token(token)

@app.get("/protected")
def protected_route(user = Depends(verify_token)):
    return {"user": user}
```

**Authorization (What can you do?):**

```python
def require_role(required_role: str):
    def check_role(user = Depends(verify_token)):
        if user.role != required_role:
            raise HTTPException(status_code=403, detail="Insufficient permissions")
        return user
    return check_role

@app.delete("/admin/users/{id}")
def delete_user(user = Depends(require_role("admin"))):
    # Only admins can access
    pass
```

**Best Practices:**
- Use JWT tokens
- Store secrets in environment variables
- Implement role-based access control (RBAC)
- Use OAuth2 for third-party auth"

**Key Points:**
- HTTPBearer for token auth
- Dependency-based authorization
- JWT tokens
- RBAC

---

### Q9: How do you handle file uploads and large requests?

**Answer:**
"**File Uploads:**
```python
from fastapi import UploadFile, File

@app.post("/upload")
async def upload_file(file: UploadFile = File(...)):
    contents = await file.read()
    # Process file
    return {"filename": file.filename, "size": len(contents)}
```

**Large Requests:**
- Use streaming for large files
- Implement chunked uploads
- Set request size limits:
```python
from fastapi import Request
from fastapi.exceptions import RequestValidationError

@app.exception_handler(RequestValidationError)
async def validation_exception_handler(request: Request, exc):
    if "body" in str(exc) and "too large" in str(exc):
        return JSONResponse(
            status_code=413,
            content={"detail": "Request too large"}
        )
```

**Optimization:**
- Stream processing instead of loading entire file
- Use background tasks for processing
- Store files in object storage (GCS, S3)"

**Key Points:**
- UploadFile for file uploads
- Streaming for large files
- Size limits
- Background processing

---

### Q10: How would you implement rate limiting?

**Answer:**
"**Using Middleware:**
```python
from fastapi import Request
from collections import defaultdict
import time

rate_limits = defaultdict(list)

@app.middleware("http")
async def rate_limit_middleware(request: Request, call_next):
    client_ip = request.client.host
    current_time = time.time()
    
    # Clean old entries
    rate_limits[client_ip] = [
        t for t in rate_limits[client_ip]
        if current_time - t < 60  # 1 minute window
    ]
    
    # Check limit (e.g., 100 requests per minute)
    if len(rate_limits[client_ip]) >= 100:
        return JSONResponse(
            status_code=429,
            content={"detail": "Rate limit exceeded"}
        )
    
    rate_limits[client_ip].append(current_time)
    response = await call_next(request)
    return response
```

**Better Approach (Redis):**
```python
import redis
r = redis.Redis()

def rate_limit(key: str, limit: int = 100, window: int = 60):
    current = r.incr(key)
    if current == 1:
        r.expire(key, window)
    if current > limit:
        raise HTTPException(status_code=429, detail="Rate limit exceeded")
```

In production, I'd use Redis for distributed rate limiting across multiple instances."

**Key Points:**
- Middleware-based
- Redis for distributed
- Per-IP or per-user limits
- 429 status code

---

## 🎯 System Design Questions

### Q11: Design a FastAPI service for ML predictions at scale.

**Answer:**
"**Architecture:**

**Components:**
1. **API Gateway**: Rate limiting, authentication
2. **FastAPI Service**: Request handling, validation
3. **Model Service**: Model loading, prediction
4. **Cache Layer**: Redis for frequent predictions
5. **Database**: Store predictions, metadata
6. **Monitoring**: Metrics, logging, alerts

**Flow:**
```
Request → API Gateway → FastAPI → Cache Check →
  → If hit: Return cached
  → If miss: Model Service → Cache Store → Response
```

**Scaling:**
- Multiple FastAPI instances (load balanced)
- Model service can scale independently
- Redis cluster for caching
- Database read replicas

**Optimization:**
- Batch predictions when possible
- Async processing for non-real-time
- Connection pooling
- Response compression

**From Module 04:**
I implemented this with FastAPI, Redis caching, and Cloud Run auto-scaling, handling 1000+ requests/minute with <100ms latency."

---

## 💡 STAR Framework Examples

### Situation: Building ML API with FastAPI

**Situation**: Needed to serve ML model predictions via REST API.

**Task**: Build production-ready API with validation, error handling, and monitoring.

**Action**: 
- Used FastAPI for type-safe API
- Implemented Pydantic models for validation
- Added Redis caching for performance
- Set up health checks and monitoring
- Deployed with Docker on Cloud Run

**Result**: 
- <100ms latency
- 1000+ requests/minute capacity
- Automatic validation catches errors
- Auto-scaling handles traffic spikes

---

## 📊 Quick Reference

### Key Concepts
1. **Type Hints**: Automatic validation
2. **Pydantic**: Data validation
3. **Dependencies**: Reusable logic
4. **Async**: Non-blocking I/O
5. **Middleware**: Request/response processing
6. **Error Handling**: HTTPException
7. **Security**: Authentication, CORS
8. **Testing**: TestClient

### Common Interview Topics
- Request validation
- Dependency injection
- Async/await
- Error handling
- Authentication
- Scaling strategies
- Performance optimization

---

## ✅ Practice Checklist

- [ ] Can explain FastAPI in 2 minutes
- [ ] Understand type hints and validation
- [ ] Know dependency injection
- [ ] Understand async/await
- [ ] Can handle errors properly
- [ ] Know authentication patterns
- [ ] Can explain your POC usage
- [ ] Ready for system design questions

---

**Remember**: Connect answers to your actual POC projects (Modules 04, 05).

