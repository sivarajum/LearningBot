# Kubernetes - Complete Guide (Basic to Advanced)

## 🎯 What is Kubernetes?

**Kubernetes (K8s)** is a container orchestration platform for automating deployment, scaling, and management of containerized applications.

### Why Kubernetes?
- **Container Orchestration**: Manage containers at scale
- **Auto-Scaling**: Scale based on demand
- **Self-Healing**: Automatic recovery
- **Service Discovery**: Automatic networking
- **Industry Standard**: Most common orchestration tool

---

## 📚 Learning Path: Basic → Intermediate → Advanced

---

## 🟢 LEVEL 1: BASIC (Getting Started)

### Basic Concepts

```yaml
# Pod definition
apiVersion: v1
kind: Pod
metadata:
  name: my-pod
spec:
  containers:
  - name: app
    image: myapp:1.0
    ports:
    - containerPort: 8080
```

### Key Concepts

#### 1. **Pods**
- Smallest deployable unit
- One or more containers
- Shared network/storage

#### 2. **Deployments**
- Manage pod replicas
- Rolling updates
- Rollback capability

#### 3. **Services**
- Expose pods
- Load balancing
- Service discovery

#### 4. **Namespaces**
- Logical separation
- Resource isolation
- Access control

---

## 🟡 LEVEL 2: INTERMEDIATE (Production Patterns)

### Deployments

```yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: my-app
spec:
  replicas: 3
  selector:
    matchLabels:
      app: my-app
  template:
    metadata:
      labels:
        app: my-app
    spec:
      containers:
      - name: app
        image: myapp:1.0
```

### Services

```yaml
apiVersion: v1
kind: Service
metadata:
  name: my-service
spec:
  selector:
    app: my-app
  ports:
  - port: 80
    targetPort: 8080
  type: LoadBalancer
```

---

## 🔴 LEVEL 3: ADVANCED (Production Excellence)

### Horizontal Pod Autoscaler

```yaml
apiVersion: autoscaling/v2
kind: HorizontalPodAutoscaler
metadata:
  name: my-hpa
spec:
  scaleTargetRef:
    apiVersion: apps/v1
    kind: Deployment
    name: my-app
  minReplicas: 2
  maxReplicas: 10
  metrics:
  - type: Resource
    resource:
      name: cpu
      target:
        type: Utilization
        averageUtilization: 70
```

### ConfigMaps and Secrets

```yaml
# ConfigMap
apiVersion: v1
kind: ConfigMap
metadata:
  name: my-config
data:
  key: value

# Secret
apiVersion: v1
kind: Secret
metadata:
  name: my-secret
type: Opaque
data:
  password: base64encoded
```

---

## 🏗️ Architecture Patterns

### Pattern 1: Basic Deployment
```
Deployment → Pods → Service → External
```

### Pattern 2: Auto-Scaling
```
HPA → Deployment → Scale Pods → Service
```

---

## 📊 Best Practices

### 1. **Resource Limits**
- Set CPU/memory limits
- Prevent resource exhaustion
- Better scheduling

### 2. **Health Checks**
- Liveness probes
- Readiness probes
- Startup probes

### 3. **Security**
- Use secrets for sensitive data
- RBAC for access control
- Network policies

---

## 🎯 Key Takeaways

1. **Kubernetes = Container Orchestration**
2. **Pods = Containers**
3. **Deployments = Replica Management**
4. **Services = Networking**
5. **HPA = Auto-Scaling**

---

## 📚 Next Steps

1. ✅ Read this guide
2. 📊 Review `Visual.md` for flows
3. 💬 Practice `Interview.md` questions
4. 🏗️ Deploy with K8s
5. 🎯 Explain it confidently

