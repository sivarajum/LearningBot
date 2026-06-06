# Docker Interview Questions & Answers

## 🔰 Beginner Level

### Q1: What is Docker and why is it important?
**Answer:**
Docker is a platform for developing, shipping, and running applications inside containers. Containers are lightweight, portable, and self-sufficient units that package an application and its dependencies together.

**Why important:**
- **Consistency**: Eliminates "works on my machine" problems
- **Isolation**: Applications run in isolated environments
- **Portability**: Run anywhere Docker runs
- **Efficiency**: Better resource utilization than VMs
- **Scalability**: Easy horizontal scaling

### Q2: What is the difference between a Docker image and a container?
**Answer:**
- **Docker Image**: A read-only template containing application code, dependencies, and instructions to create a container. It's like a blueprint or recipe.
- **Docker Container**: A running instance of an image. It's the actual executable environment where the application runs.

**Analogy**: Image is like a class, container is like an object instantiated from that class.

### Q3: Explain basic Docker commands
**Answer:**
```bash
# Build an image
docker build -t myapp .

# Run a container
docker run -d --name mycontainer -p 8080:80 myapp

# List running containers
docker ps

# List all containers
docker ps -a

# Stop a container
docker stop mycontainer

# Remove a container
docker rm mycontainer

# Remove an image
docker rmi myapp

# View logs
docker logs mycontainer

# Execute commands in running container
docker exec -it mycontainer bash
```

### Q4: What is a Dockerfile?
**Answer:**
A Dockerfile is a text file containing instructions to build a Docker image. It defines the base image, dependencies, application code, and runtime configuration.

**Basic structure:**
```dockerfile
FROM ubuntu:20.04          # Base image
WORKDIR /app               # Working directory
COPY . .                   # Copy files
RUN apt-get update && apt-get install -y python3  # Install dependencies
EXPOSE 8080                # Expose port
CMD ["python3", "app.py"]  # Start command
```

## 🏗️ Intermediate Level

### Q5: Explain Docker architecture
**Answer:**
Docker uses a client-server architecture:

- **Docker Client**: CLI tool that accepts commands and communicates with Docker daemon
- **Docker Daemon**: Background service that manages containers, images, networks, and volumes
- **Docker Registry**: Repository for storing and distributing images (Docker Hub, private registries)

**Key components:**
- **containerd**: Container runtime for lifecycle management
- **runc**: Low-level container runtime implementing OCI specification
- **Linux Kernel features**: Namespaces, cgroups, UnionFS for isolation and resource management

### Q6: What are Docker layers and how do they work?
**Answer:**
Docker images are composed of layers, each representing a set of filesystem changes:

- **Base Layer**: OS (Ubuntu, Alpine, etc.)
- **Dependency Layers**: Package installations
- **Application Layers**: Code and configuration
- **Read-write Layer**: Container-specific changes

**Benefits:**
- **Caching**: Rebuild only changed layers
- **Sharing**: Common layers shared between images
- **Storage efficiency**: Reduced disk usage

### Q7: How does Docker networking work?
**Answer:**
Docker provides several network drivers:

- **Bridge (default)**: Containers communicate via virtual bridge
- **Host**: Container uses host's network stack (no isolation)
- **Overlay**: Multi-host networking for Swarm
- **Macvlan**: Assign MAC addresses to containers
- **None**: No networking

**Commands:**
```bash
# Create custom network
docker network create mynetwork

# Run container on specific network
docker run --network mynetwork myapp

# Connect running container to network
docker network connect mynetwork container_name
```

### Q8: Explain Docker volumes vs bind mounts
**Answer:**
- **Volumes**: Managed by Docker, stored in `/var/lib/docker/volumes/`
  - Better performance on Docker Desktop
  - Easy backup and migration
  - Named volumes for data sharing

- **Bind Mounts**: Host filesystem mounted into container
  - Full host filesystem access
  - Exact host path mapping
  - Better for development (code changes reflect immediately)

**Usage:**
```bash
# Named volume
docker run -v myvolume:/data myapp

# Bind mount
docker run -v /host/path:/container/path myapp
```

### Q9: What is Docker Compose and when to use it?
**Answer:**
Docker Compose is a tool for defining and running multi-container applications using YAML files.

**Use cases:**
- Development environments
- Microservices applications
- Testing complex applications
- CI/CD pipelines

**Example docker-compose.yml:**
```yaml
version: '3.8'
services:
  web:
    build: .
    ports:
      - "8080:80"
  db:
    image: postgres:13
    environment:
      POSTGRES_PASSWORD: password
```

## 🚀 Advanced Level

### Q10: Explain multi-stage builds and their benefits
**Answer:**
Multi-stage builds allow creating multiple intermediate images and copying artifacts between them, resulting in smaller final images.

**Benefits:**
- **Smaller images**: Only production dependencies included
- **Security**: Build tools not present in final image
- **Performance**: Faster deployments and pulls

**Example:**
```dockerfile
# Build stage
FROM node:16 AS builder
WORKDIR /app
COPY package*.json ./
RUN npm ci --only=production
COPY . .
RUN npm run build

# Production stage
FROM nginx:alpine
COPY --from=builder /app/dist /usr/share/nginx/html
EXPOSE 80
CMD ["nginx", "-g", "daemon off;"]
```

### Q11: How do you secure Docker containers?
**Answer:**
**Security best practices:**

1. **Image Security:**
   - Use trusted base images
   - Scan images for vulnerabilities
   - Keep images updated

2. **Container Runtime:**
   - Run as non-root user
   - Use read-only filesystems where possible
   - Limit capabilities with `--cap-drop`

3. **Network Security:**
   - Don't expose unnecessary ports
   - Use internal networks for service communication
   - Implement proper firewall rules

4. **Secrets Management:**
   - Don't bake secrets into images
   - Use Docker secrets or external secret managers

**Commands:**
```bash
# Run as non-root
docker run --user 1000:1000 myapp

# Drop capabilities
docker run --cap-drop ALL --cap-add NET_BIND_SERVICE myapp

# Read-only filesystem
docker run --read-only myapp
```

### Q12: Explain Docker Swarm vs Kubernetes
**Answer:**

| Aspect | Docker Swarm | Kubernetes |
|--------|-------------|------------|
| **Setup** | Easier, built-in | Complex, steep learning curve |
| **Scaling** | Simple auto-scaling | Advanced scaling policies |
| **Load Balancing** | Built-in | Service mesh required |
| **Storage** | Basic volume support | Advanced persistent volumes |
| **Ecosystem** | Docker ecosystem | Cloud-native ecosystem |
| **Use Case** | Simple deployments | Complex, production-grade |

**When to choose Swarm:**
- Small to medium deployments
- Docker-native workflows
- Quick setup needed
- Less operational overhead

### Q13: How do you troubleshoot Docker containers?
**Answer:**
**Common troubleshooting steps:**

1. **Check container status:**
   ```bash
   docker ps -a
   docker logs container_name
   docker inspect container_name
   ```

2. **Debug running containers:**
   ```bash
   docker exec -it container_name bash
   docker stats container_name
   ```

3. **Check resource usage:**
   ```bash
   docker stats
   docker system df
   ```

4. **Network debugging:**
   ```bash
   docker network ls
   docker network inspect network_name
   ```

5. **Image and build issues:**
   ```bash
   docker build --no-cache .
   docker history image_name
   ```

### Q14: Explain Docker resource management
**Answer:**
Docker uses Linux kernel features for resource control:

- **CPU Limits:**
  ```bash
  docker run --cpus=1.5 myapp  # 1.5 CPU cores
  docker run --cpu-shares=1024 myapp  # Relative weight
  ```

- **Memory Limits:**
  ```bash
  docker run --memory=512m myapp  # Hard limit
  docker run --memory-reservation=256m myapp  # Soft limit
  ```

- **I/O Limits:**
  ```bash
  docker run --device-read-bps /dev/sda:1mb myapp  # Read limit
  docker run --device-write-bps /dev/sda:1mb myapp  # Write limit
  ```

**Monitoring:**
```bash
docker stats
docker system df -v  # Detailed disk usage
```

### Q15: How do you optimize Docker images?
**Answer:**
**Optimization techniques:**

1. **Base Image Selection:**
   - Use Alpine Linux for smaller images
   - Use specific version tags (avoid `latest`)

2. **Layer Optimization:**
   - Combine RUN commands to reduce layers
   - Clean up package manager cache
   - Use `.dockerignore` file

3. **Multi-stage Builds:**
   - Separate build and runtime environments
   - Copy only necessary artifacts

4. **Caching Strategies:**
   - Order Dockerfile instructions for better caching
   - Use stable dependencies first

**Example optimized Dockerfile:**
```dockerfile
FROM node:16-alpine AS builder
WORKDIR /app
COPY package*.json ./
RUN npm ci --only=production && npm cache clean --force

FROM node:16-alpine AS runtime
RUN addgroup -g 1001 -S nodejs && adduser -S nextjs -u 1001
WORKDIR /app
COPY --from=builder --chown=nextjs:nodejs /app/node_modules ./node_modules
COPY --chown=nextjs:nodejs . .
USER nextjs
EXPOSE 3000
CMD ["npm", "start"]
```

## 🎯 Scenario-Based Questions

### Q16: Container keeps crashing, how do you debug?
**Answer:**
**Debugging steps:**

1. **Check logs:**
   ```bash
   docker logs container_name
   docker logs -f container_name  # Follow logs
   ```

2. **Inspect container:**
   ```bash
   docker inspect container_name | grep -A 10 "State"
   ```

3. **Check resource constraints:**
   ```bash
   docker stats container_name
   ```

4. **Execute into container:**
   ```bash
   docker exec -it container_name bash
   # Check running processes, disk space, etc.
   ```

5. **Check application configuration:**
   - Environment variables
   - Configuration files
   - Network connectivity

### Q17: How do you handle database persistence in containers?
**Answer:**
**Best practices:**

1. **Use named volumes:**
   ```bash
   docker run -d --name postgres -v postgres_data:/var/lib/postgresql/data postgres
   ```

2. **Backup strategy:**
   ```bash
   docker run --rm -v postgres_data:/data -v $(pwd):/backup alpine tar czf /backup/backup.tar.gz -C /data .
   ```

3. **Database migration:**
   - Use initialization scripts
   - Handle schema updates in application code
   - Use database migration tools

4. **Production considerations:**
   - Use managed database services
   - Implement proper backup/restore procedures
   - Monitor disk usage

### Q18: How do you scale Docker applications?
**Answer:**
**Scaling approaches:**

1. **Manual scaling:**
   ```bash
   docker-compose up -d --scale web=3
   ```

2. **Docker Swarm scaling:**
   ```bash
   docker service scale myapp_web=5
   ```

3. **Load balancing:**
   - Use nginx or traefik as reverse proxy
   - Docker Swarm built-in load balancing
   - Kubernetes services

4. **Auto-scaling considerations:**
   - Monitor resource usage
   - Implement health checks
   - Use orchestration platform features

### Q19: Container is slow, how do you optimize performance?
**Answer:**
**Performance optimization:**

1. **Resource allocation:**
   ```bash
   docker run --cpus=2 --memory=4g myapp
   ```

2. **Image optimization:**
   - Use multi-stage builds
   - Minimize image layers
   - Use appropriate base images

3. **Storage optimization:**
   - Use volumes for persistent data
   - Avoid storing data in container filesystem

4. **Network optimization:**
   - Use host networking for low-latency requirements
   - Optimize network driver selection

5. **Application optimization:**
   - Profile application performance
   - Optimize database queries
   - Implement caching strategies

### Q20: How do you implement CI/CD with Docker?
**Answer:**
**CI/CD pipeline with Docker:**

1. **Build stage:**
   ```yaml
   # GitHub Actions example
   - name: Build Docker image
     run: docker build -t myapp:${{ github.sha }} .
   ```

2. **Test stage:**
   ```yaml
   - name: Run tests
     run: docker run --rm myapp:${{ github.sha }} npm test
   ```

3. **Security scan:**
   ```yaml
   - name: Scan image
     run: docker scan myapp:${{ github.sha }}
   ```

4. **Deploy stage:**
   ```yaml
   - name: Deploy
     run: |
       docker tag myapp:${{ github.sha }} myapp:latest
       docker push myregistry.com/myapp:latest
   ```

**Best practices:**
- Use multi-stage builds for faster builds
- Cache dependencies between builds
- Implement proper tagging strategy
- Use secrets management for credentials

## 🧠 Expert Level

### Q21: Explain Docker's copy-on-write mechanism
**Answer:**
Docker uses copy-on-write (CoW) for efficient storage:

- **Shared base layers**: All containers share read-only base image layers
- **Copy-on-write**: When a container modifies a file, Docker creates a copy in the container's writable layer
- **Union filesystem**: Presents unified view of all layers

**Benefits:**
- **Space efficiency**: Common files shared across containers
- **Performance**: No need to copy entire filesystem
- **Snapshot-like behavior**: Easy rollback and branching

### Q22: How does Docker handle process signals?
**Answer:**
Docker properly handles Linux signals for graceful shutdown:

- **SIGTERM**: Sent first, allows graceful shutdown (30 seconds)
- **SIGKILL**: Sent after timeout if process doesn't respond

**Best practices:**
```dockerfile
# Handle signals properly
STOPSIGNAL SIGTERM
CMD ["nginx", "-g", "daemon off;"]
```

**In application code:**
```python
import signal
import sys

def signal_handler(signum, frame):
    print("Shutting down gracefully...")
    # Cleanup code here
    sys.exit(0)

signal.signal(signal.SIGTERM, signal_handler)
```

### Q23: Explain Docker's security model in depth
**Answer:**
Docker security is based on Linux kernel features:

1. **Namespaces**: Provide isolation
   - PID: Process isolation
   - NET: Network isolation
   - MNT: Filesystem isolation
   - UTS: Hostname isolation
   - IPC: Inter-process communication isolation
   - USER: User ID mapping

2. **Control Groups (cgroups)**: Resource limits
   - CPU, memory, I/O limits
   - Quality of service guarantees

3. **Capabilities**: Fine-grained privileges
   - Drop unnecessary capabilities
   - Add only required ones

4. **Seccomp**: System call filtering
5. **AppArmor/SELinux**: Mandatory access control

**Security challenges:**
- Kernel shared between containers
- Privileged containers bypass isolation
- Vulnerable images compromise security

### Q24: How do you implement zero-downtime deployments?
**Answer:**
**Blue-green deployment with Docker:**

1. **Create new version:**
   ```bash
   docker build -t myapp:v2 .
   docker run -d --name myapp-v2 -p 8081:80 myapp:v2
   ```

2. **Health check:**
   ```bash
   curl http://localhost:8081/health
   ```

3. **Switch traffic:**
   ```bash
   # Update load balancer configuration
   # Or use docker service update for Swarm
   docker service update --image myapp:v2 myapp
   ```

4. **Cleanup old version:**
   ```bash
   docker stop myapp-v1
   docker rm myapp-v1
   ```

**Rolling updates in Swarm:**
```bash
docker service update \
  --update-parallelism 2 \
  --update-delay 10s \
  --image myapp:v2 \
  myapp
```

### Q25: Explain Docker's role in microservices architecture
**Answer:**
Docker enables microservices by providing:

1. **Service Isolation:**
   - Each service runs in its own container
   - Independent scaling and deployment

2. **Technology Diversity:**
   - Different services can use different tech stacks
   - Polyglot development

3. **Environment Consistency:**
   - Same environment from development to production
   - Eliminates environment-specific bugs

4. **Resource Efficiency:**
   - Better resource utilization than VMs
   - Faster startup times

5. **Orchestration Integration:**
   - Works with Kubernetes, Swarm for service discovery
   - Automated scaling and load balancing

**Challenges:**
- Network complexity between services
- Data consistency across services
- Service discovery and configuration management
- Monitoring and logging distributed systems

## 📚 Additional Resources

- [Docker Documentation](https://docs.docker.com/)
- [Docker Best Practices](https://docs.docker.com/develop/dev-best-practices/)
- [Docker Security](https://docs.docker.com/engine/security/)
- [Docker Compose Documentation](https://docs.docker.com/compose/)

## 🎯 Key Takeaways

- **Master basic commands**: build, run, ps, logs, exec
- **Understand image layers**: For efficient caching and storage
- **Know networking options**: Bridge, host, overlay, none
- **Security first**: Run as non-root, scan images, limit capabilities
- **Multi-stage builds**: For optimized production images
- **Orchestration**: Choose between Swarm and Kubernetes based on needs
- **Troubleshooting**: Logs, inspect, stats are your friends
- **Performance**: Resource limits, image optimization, proper networking

Remember: Docker is a tool that solves real problems in software development and deployment. Focus on understanding the "why" behind each concept, not just memorizing commands.