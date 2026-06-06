# Docker - Interview Questions (Basic to Advanced)

## 🎯 Interview Preparation Guide

Practice these questions to ace your Docker interviews.

---

## 🟢 BASIC LEVEL Questions

### Q1: What is Docker and why use it?

**Answer:**
"Docker is a containerization platform that packages applications with all dependencies into containers. Containers are lightweight, isolated environments that run consistently anywhere.

I use it in Modules 01, 04, and 05 because:

1. **Consistency**: Same environment in dev, staging, production
2. **Isolation**: Containers don't interfere with each other
3. **Portability**: Run anywhere Docker runs
4. **Efficiency**: Much lighter than VMs
5. **Scalability**: Easy to scale containers

In Module 04, I containerize my ML API, making it easy to deploy to Cloud Run or any container platform."

**Key Points:**
- Containerization
- Consistency
- Portability
- Efficiency

---

### Q2: What's the difference between Docker image and container?

**Answer:**
"**Image**: Read-only template containing application code, runtime, libraries, and dependencies. It's like a blueprint.

**Container**: Running instance of an image. It's the actual running application.

**Analogy**: Image is like a class, container is like an object instance.

**Example:**
```bash
# Image (template)
docker build -t myapp:1.0 .

# Container (running instance)
docker run myapp:1.0
```

You can have one image and run multiple containers from it."

**Key Points:**
- Image = template
- Container = instance
- One image, many containers

---

### Q3: What is a Dockerfile?

**Answer:**
"Dockerfile is a text file with instructions to build a Docker image. It defines:
- Base image
- Dependencies to install
- Files to copy
- Commands to run
- Port to expose

**Example:**
```dockerfile
FROM python:3.9
WORKDIR /app
COPY requirements.txt .
RUN pip install -r requirements.txt
COPY . .
EXPOSE 8000
CMD ["python", "app.py"]
```

Each instruction creates a layer. Docker caches layers for faster rebuilds."

**Key Points:**
- Build instructions
- Creates layers
- Cached for efficiency

---

## 🟡 INTERMEDIATE LEVEL Questions

### Q4: How do you optimize Docker images?

**Answer:**
"**1. Use Multi-Stage Builds**
```dockerfile
# Build stage (large)
FROM python:3.9 as builder
RUN pip install --user -r requirements.txt

# Runtime stage (small)
FROM python:3.9-slim
COPY --from=builder /root/.local /root/.local
```

**2. Use .dockerignore**
```
__pycache__
*.pyc
.git
```

**3. Layer Optimization**
```dockerfile
# Bad: Many layers
RUN apt-get update
RUN apt-get install package1
RUN apt-get install package2

# Good: Single layer
RUN apt-get update && \
    apt-get install -y package1 package2 && \
    apt-get clean
```

**4. Use Specific Versions**
```dockerfile
FROM python:3.9.16-slim  # Not 'latest'
```

**5. Use Slim/Alpine Images**
```dockerfile
FROM python:3.9-slim  # Smaller than full image
```

These optimizations reduced my image size from 1.5GB to 200MB in Module 04."

**Key Points:**
- Multi-stage builds
- .dockerignore
- Layer optimization
- Specific versions

---

### Q5: What is Docker Compose?

**Answer:**
"Docker Compose is a tool for defining and running multi-container Docker applications. You define services in a YAML file.

**Example:**
```yaml
version: '3.8'
services:
  api:
    build: .
    ports:
      - "8000:8000"
    depends_on:
      - db
  
  db:
    image: postgres:13
    environment:
      POSTGRES_PASSWORD: password
```

**Benefits:**
- Define entire stack in one file
- Easy to start/stop all services
- Automatic networking between services
- Volume management

**Commands:**
```bash
docker-compose up -d    # Start all services
docker-compose down     # Stop all services
docker-compose logs     # View logs
```

I use Docker Compose in development to run my API with database and Redis together."

**Key Points:**
- Multi-container apps
- YAML configuration
- Easy orchestration

---

## 🔴 ADVANCED LEVEL Questions

### Q6: How do you handle secrets in Docker?

**Answer:**
"**1. Environment Variables (not for secrets)**
```dockerfile
ENV API_KEY=value  # Not secure
```

**2. Runtime Environment Variables**
```bash
docker run -e API_KEY=secret myapp
```

**3. Docker Secrets (Docker Swarm)**
```yaml
services:
  api:
    secrets:
      - api_key
secrets:
  api_key:
    external: true
```

**4. Secret Management Services**
- Use cloud secret managers (GCP Secret Manager)
- Mount secrets as files
- Use init containers to fetch secrets

**Best Practice:**
Never commit secrets in Dockerfile or code. Use secret management services or environment variables at runtime."

**Key Points:**
- No secrets in images
- Use secret managers
- Runtime injection

---

### Q7: How do you debug Docker containers?

**Answer:**
"**1. View Logs**
```bash
docker logs container_name
docker logs -f container_name  # Follow logs
```

**2. Execute Commands**
```bash
docker exec -it container_name bash
docker exec container_name ls /app
```

**3. Inspect Container**
```bash
docker inspect container_name
docker ps  # See running containers
```

**4. Health Checks**
```dockerfile
HEALTHCHECK --interval=30s CMD curl -f http://localhost:8000/health || exit 1
```

**5. Debugging Tools**
- Use debug images
- Add debugging tools to image
- Use docker-compose for local debugging

**Common Issues:**
- Port conflicts
- Volume mounts
- Network connectivity
- Resource limits"

**Key Points:**
- Logs
- Exec commands
- Inspect
- Health checks

---

## 🎯 Key Takeaways

1. **Docker = Containerization**
2. **Image = Template**
3. **Container = Instance**
4. **Compose = Multi-Container**
5. **Optimize = Smaller Images**

---

## ✅ Practice Checklist

- [ ] Can explain Docker in 2 minutes
- [ ] Understand image vs container
- [ ] Know Dockerfile basics
- [ ] Understand optimization
- [ ] Know Docker Compose
- [ ] Can explain your POC usage

---

**Remember**: Connect answers to your actual POC projects.

