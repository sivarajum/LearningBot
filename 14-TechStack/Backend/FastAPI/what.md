# FastAPI: Modern Python Web Framework

## Overview

FastAPI is a modern, fast (high-performance), web framework for building APIs with Python 3.7+ based on standard Python type hints. It is designed to be easy to use, fast to code, and ready for production.

**Key Features:**
- **Fast**: Very high performance, on par with NodeJS and Go (thanks to Starlette and Pydantic)
- **Fast to code**: Increase development speed by 200-300%
- **Fewer bugs**: Reduce human-induced errors by 40%
- **Intuitive**: Great editor support with auto-completion
- **Easy**: Designed to be easy to use and learn
- **Short**: Minimize code duplication
- **Robust**: Get production-ready code with automatic interactive documentation
- **Standards-based**: Based on (and fully compatible with) the open standards for APIs: OpenAPI and JSON Schema

## Core Concepts

### Path Parameters

```python
from fastapi import FastAPI

app = FastAPI()

# Path parameter with type annotation
@app.get("/items/{item_id}")
async def read_item(item_id: int):
    return {"item_id": item_id}

# Multiple path parameters
@app.get("/users/{user_id}/posts/{post_id}")
async def read_user_post(user_id: int, post_id: int):
    return {"user_id": user_id, "post_id": post_id}

# Path parameter with validation
from fastapi import Path
from typing import Annotated

@app.get("/items/{item_id}")
async def read_item(
    item_id: Annotated[int, Path(title="The ID of the item", ge=1, le=1000)]
):
    return {"item_id": item_id}
```

### Query Parameters

```python
from fastapi import FastAPI
from typing import Optional

app = FastAPI()

# Simple query parameters
@app.get("/items/")
async def read_items(skip: int = 0, limit: int = 10):
    return {"skip": skip, "limit": limit}

# Optional query parameters
@app.get("/search/")
async def search_items(
    q: Optional[str] = None,
    category: Optional[str] = None,
    price_min: Optional[float] = None,
    price_max: Optional[float] = None
):
    results = {"query": q, "category": category}
    if price_min is not None:
        results["price_min"] = price_min
    if price_max is not None:
        results["price_max"] = price_max
    return results

# Query parameter validation
from fastapi import Query
from typing import Annotated

@app.get("/items/")
async def read_items(
    q: Annotated[
        Optional[str],
        Query(max_length=50, pattern="^fixedquery$")
    ] = None
):
    return {"q": q}
```

### Request Body

```python
from fastapi import FastAPI
from pydantic import BaseModel
from typing import Optional

app = FastAPI()

# Basic request body model
class Item(BaseModel):
    name: str
    price: float
    is_offer: Optional[bool] = None

@app.post("/items/")
async def create_item(item: Item):
    return item

# Nested models
class User(BaseModel):
    username: str
    full_name: Optional[str] = None

class ItemWithOwner(BaseModel):
    name: str
    price: float
    owner: User

@app.post("/items-with-owner/")
async def create_item_with_owner(item: ItemWithOwner):
    return item

# Request body with path and query parameters
@app.put("/items/{item_id}")
async def update_item(
    item_id: int,
    item: Item,
    q: Optional[str] = None
):
    result = {"item_id": item_id, **item.dict()}
    if q:
        result.update({"q": q})
    return result
```

### Response Models

```python
from fastapi import FastAPI
from pydantic import BaseModel
from typing import List, Optional

app = FastAPI()

class Item(BaseModel):
    name: str
    price: float
    is_offer: Optional[bool] = None

class User(BaseModel):
    username: str
    email: str
    full_name: Optional[str] = None

# Response model
@app.post("/items/", response_model=Item)
async def create_item(item: Item):
    return item

# Response model with exclusion
@app.get("/items/{item_id}", response_model=Item)
async def read_item(item_id: int):
    return {
        "name": "Foo",
        "price": 42.0,
        "is_offer": True,
        "internal_id": 123  # This will be excluded from response
    }

# Multiple response models
@app.get("/items/{item_id}/public", response_model=Item)
async def read_item_public(item_id: int):
    return {"name": "Foo", "price": 42.0}

@app.get("/items/{item_id}/private")
async def read_item_private(item_id: int):
    return {
        "name": "Foo",
        "price": 42.0,
        "internal_id": 123
    }

# List response
@app.get("/items/", response_model=List[Item])
async def read_items():
    return [
        {"name": "Foo", "price": 42.0},
        {"name": "Bar", "price": 24.0}
    ]
```

### Form Data and File Uploads

```python
from fastapi import FastAPI, File, UploadFile, Form
from fastapi.responses import HTMLResponse
from typing import List

app = FastAPI()

# File upload
@app.post("/uploadfile/")
async def create_upload_file(file: UploadFile = File(...)):
    return {
        "filename": file.filename,
        "content_type": file.content_type,
        "size": len(await file.read())
    }

# Multiple file uploads
@app.post("/uploadfiles/")
async def create_upload_files(files: List[UploadFile] = File(...)):
    return [
        {
            "filename": file.filename,
            "content_type": file.content_type
        }
        for file in files
    ]

# Form data
@app.post("/login/")
async def login(username: str = Form(...), password: str = Form(...)):
    return {"username": username}

# Mixed form data and file
@app.post("/create-item/")
async def create_item(
    name: str = Form(...),
    price: float = Form(...),
    file: UploadFile = File(...)
):
    return {
        "name": name,
        "price": price,
        "filename": file.filename
    }
```

### Dependencies

```python
from fastapi import FastAPI, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from pydantic import BaseModel
from typing import Optional
from datetime import datetime, timedelta
from jose import JWTError, jwt
from passlib.context import CryptContext

app = FastAPI()

# Password hashing
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

def verify_password(plain_password, hashed_password):
    return pwd_context.verify(plain_password, hashed_password)

def get_password_hash(password):
    return pwd_context.hash(password)

# JWT token
SECRET_KEY = "your-secret-key"
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30

class Token(BaseModel):
    access_token: str
    token_type: str

class TokenData(BaseModel):
    username: Optional[str] = None

class User(BaseModel):
    username: str
    email: Optional[str] = None
    full_name: Optional[str] = None
    disabled: Optional[bool] = None

class UserInDB(User):
    hashed_password: str

# Mock database
fake_users_db = {
    "johndoe": {
        "username": "johndoe",
        "full_name": "John Doe",
        "email": "johndoe@example.com",
        "hashed_password": get_password_hash("secret"),
        "disabled": False,
    }
}

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")

def get_user(db, username: str):
    if username in db:
        user_dict = db[username]
        return UserInDB(**user_dict)

def authenticate_user(fake_db, username: str, password: str):
    user = get_user(fake_db, username)
    if not user:
        return False
    if not verify_password(password, user.hashed_password):
        return False
    return user

def create_access_token(data: dict, expires_delta: Optional[timedelta] = None):
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=15)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt

async def get_current_user(token: str = Depends(oauth2_scheme)):
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        username: str = payload.get("sub")
        if username is None:
            raise credentials_exception
        token_data = TokenData(username=username)
    except JWTError:
        raise credentials_exception

    user = get_user(fake_users_db, username=token_data.username)
    if user is None:
        raise credentials_exception
    return user

async def get_current_active_user(current_user: User = Depends(get_current_user)):
    if current_user.disabled:
        raise HTTPException(status_code=400, detail="Inactive user")
    return current_user

@app.post("/token", response_model=Token)
async def login_for_access_token(form_data: OAuth2PasswordRequestForm = Depends()):
    user = authenticate_user(fake_users_db, form_data.username, form_data.password)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={"sub": user.username}, expires_delta=access_token_expires
    )
    return {"access_token": access_token, "token_type": "bearer"}

@app.get("/users/me/", response_model=User)
async def read_users_me(current_user: User = Depends(get_current_active_user)):
    return current_user

@app.get("/users/me/items/")
async def read_own_items(current_user: User = Depends(get_current_active_user)):
    return [{"item_id": "Foo", "owner": current_user.username}]
```

### Middleware and CORS

```python
from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.trustedhost import TrustedHostMiddleware
from fastapi.responses import JSONResponse
import time

app = FastAPI()

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "http://localhost:8080"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Trusted host middleware
app.add_middleware(
    TrustedHostMiddleware,
    allowed_hosts=["localhost", "127.0.0.1", "example.com"]
)

# Custom middleware
@app.middleware("http")
async def add_process_time_header(request: Request, call_next):
    start_time = time.time()
    response = await call_next(request)
    process_time = time.time() - start_time
    response.headers["X-Process-Time"] = str(process_time)
    return response

# Exception handlers
@app.exception_handler(ValueError)
async def value_error_exception_handler(request: Request, exc: ValueError):
    return JSONResponse(
        status_code=400,
        content={"message": f"Value error: {str(exc)}"},
    )

@app.exception_handler(Exception)
async def general_exception_handler(request: Request, exc: Exception):
    return JSONResponse(
        status_code=500,
        content={"message": "Internal server error"},
    )
```

### Background Tasks

```python
from fastapi import FastAPI, BackgroundTasks, Depends
import time
import smtplib
from email.mime.text import MIMEText

app = FastAPI()

def write_notification(email: str, message=""):
    # Simulate writing to database
    time.sleep(2)
    with open("log.txt", "a") as f:
        f.write(f"Notification sent to {email}: {message}\n")

def send_email_background(email: str, message: str):
    # Simulate sending email
    time.sleep(5)
    print(f"Email sent to {email}: {message}")

@app.post("/send-notification/{email}")
async def send_notification(
    email: str,
    background_tasks: BackgroundTasks,
    q: str = None
):
    message = f"Notification for {email}"
    if q:
        message += f" with query: {q}"

    background_tasks.add_task(write_notification, email, message)
    background_tasks.add_task(send_email_background, email, message)

    return {"message": "Notification sent in the background"}

# Dependency with background tasks
def get_db():
    # Simulate database connection
    return {"db": "connected"}

def close_db(db):
    # Simulate closing database connection
    print("Database connection closed")

@app.get("/items/")
async def read_items(
    background_tasks: BackgroundTasks,
    db = Depends(get_db)
):
    background_tasks.add_task(close_db, db)
    return {"items": ["item1", "item2"]}
```

### WebSockets

```python
from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from typing import List

app = FastAPI()

class ConnectionManager:
    def __init__(self):
        self.active_connections: List[WebSocket] = []

    async def connect(self, websocket: WebSocket):
        await websocket.accept()
        self.active_connections.append(websocket)

    def disconnect(self, websocket: WebSocket):
        self.active_connections.remove(websocket)

    async def send_personal_message(self, message: str, websocket: WebSocket):
        await websocket.send_text(message)

    async def broadcast(self, message: str):
        for connection in self.active_connections:
            await connection.send_text(message)

manager = ConnectionManager()

@app.websocket("/ws/{client_id}")
async def websocket_endpoint(websocket: WebSocket, client_id: int):
    await manager.connect(websocket)
    try:
        while True:
            data = await websocket.receive_text()
            await manager.send_personal_message(f"You wrote: {data}", websocket)
            await manager.broadcast(f"Client #{client_id} says: {data}")
    except WebSocketDisconnect:
        manager.disconnect(websocket)
        await manager.broadcast(f"Client #{client_id} left the chat")

# WebSocket with JSON
from pydantic import BaseModel

class Message(BaseModel):
    type: str
    content: str
    timestamp: float

@app.websocket("/ws-json/")
async def websocket_json_endpoint(websocket: WebSocket):
    await websocket.accept()
    try:
        while True:
            data = await websocket.receive_json()
            message = Message(**data)
            await websocket.send_json({
                "type": "echo",
                "content": f"Echo: {message.content}",
                "timestamp": time.time()
            })
    except WebSocketDisconnect:
        pass
```

### Testing

```python
from fastapi import FastAPI
from fastapi.testclient import TestClient

app = FastAPI()

@app.get("/")
async def read_main():
    return {"msg": "Hello World"}

@app.get("/items/{item_id}")
async def read_item(item_id: int, q: str = None):
    return {"item_id": item_id, "q": q}

client = TestClient(app)

def test_read_main():
    response = client.get("/")
    assert response.status_code == 200
    assert response.json() == {"msg": "Hello World"}

def test_read_item():
    response = client.get("/items/42?q=test")
    assert response.status_code == 200
    assert response.json() == {"item_id": 42, "q": "test"}

def test_read_item_default_q():
    response = client.get("/items/42")
    assert response.status_code == 200
    assert response.json() == {"item_id": 42, "q": None}

# Async tests
import pytest
from httpx import AsyncClient

@pytest.mark.asyncio
async def test_read_main_async():
    async with AsyncClient(app=app, base_url="http://testserver") as client:
        response = await client.get("/")
        assert response.status_code == 200
        assert response.json() == {"msg": "Hello World"}

# Testing with dependencies
from fastapi import Depends

def get_query_token(token: str):
    if token != "secret":
        raise HTTPException(status_code=400, detail="Invalid token")
    return token

@app.get("/protected/")
async def protected_route(token: str = Depends(get_query_token)):
    return {"token": token}

def test_protected_route():
    response = client.get("/protected/?token=secret")
    assert response.status_code == 200
    assert response.json() == {"token": "secret"}

def test_protected_route_invalid_token():
    response = client.get("/protected/?token=wrong")
    assert response.status_code == 400
    assert response.json() == {"detail": "Invalid token"}
```

### Deployment

```python
# main.py
from fastapi import FastAPI
import uvicorn

app = FastAPI(title="My API", version="1.0.0")

@app.get("/")
async def root():
    return {"message": "Hello World"}

@app.get("/health")
async def health_check():
    return {"status": "healthy"}

if __name__ == "__main__":
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=8000,
        reload=True,
        log_level="info"
    )

# Dockerfile
FROM python:3.9-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install -r requirements.txt

COPY . .

EXPOSE 8000

CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]

# requirements.txt
fastapi==0.104.1
uvicorn[standard]==0.24.0
pydantic==2.5.0
python-multipart==0.0.6
python-jose[cryptography]==3.3.0
passlib[bcrypt]==1.7.4

# docker-compose.yml
version: '3.8'

services:
  api:
    build: .
    ports:
      - "8000:8000"
    environment:
      - ENVIRONMENT=production
    volumes:
      - ./logs:/app/logs

  nginx:
    image: nginx:alpine
    ports:
      - "80:80"
    volumes:
      - ./nginx.conf:/etc/nginx/nginx.conf
    depends_on:
      - api

# nginx.conf
events {
    worker_connections 1024;
}

http {
    upstream api {
        server api:8000;
    }

    server {
        listen 80;

        location / {
            proxy_pass http://api;
            proxy_set_header Host $host;
            proxy_set_header X-Real-IP $remote_addr;
        }

        location /docs {
            proxy_pass http://api/docs;
        }

        location /redoc {
            proxy_pass http://api/redoc;
        }
    }
}
```

This comprehensive guide covers FastAPI's core features including routing, request/response handling, dependency injection, authentication, middleware, background tasks, WebSockets, testing, and deployment. FastAPI's automatic API documentation generation and type validation make it an excellent choice for modern Python web development.
