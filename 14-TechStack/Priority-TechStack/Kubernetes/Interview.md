# Kubernetes - Interview Questions (Basic to Advanced)

## 🎯 Interview Preparation Guide

Practice these questions to ace your Kubernetes interviews.

---

## 🟢 BASIC LEVEL Questions

### Q1: What is Kubernetes?

**Answer:**
"Kubernetes is a container orchestration platform for automating deployment, scaling, and management of containerized applications.

Key features:
- **Container Orchestration**: Manage containers at scale
- **Auto-Scaling**: Scale based on demand
- **Self-Healing**: Automatic recovery
- **Service Discovery**: Automatic networking
- **Rolling Updates**: Zero-downtime deployments

I use Kubernetes to deploy and manage containerized applications, leveraging auto-scaling and self-healing for production reliability."

**Key Points:**
- Container orchestration
- Auto-scaling
- Self-healing
- Service discovery

---

### Q2: What are Pods, Deployments, and Services?

**Answer:**
"**Pods:**
- Smallest deployable unit
- One or more containers
- Shared network/storage

**Deployments:**
- Manage pod replicas
- Rolling updates
- Rollback capability

**Services:**
- Expose pods
- Load balancing
- Service discovery

**Relationship:**
```
Deployment → Pods → Service → External
```

I use Deployments to manage pod replicas, Services to expose them, and Pods as the execution unit."

**Key Points:**
- Pods = containers
- Deployments = management
- Services = networking
- Work together

---

## 🟡 INTERMEDIATE LEVEL Questions

### Q3: How does auto-scaling work in Kubernetes?

**Answer:**
"**Horizontal Pod Autoscaler (HPA):**
- Scales pods based on metrics
- CPU, memory, custom metrics
- Min/max replicas

**Example:**
```yaml
minReplicas: 2
maxReplicas: 10
targetCPUUtilization: 70%
```

**Process:**
1. Monitor metrics
2. Calculate desired replicas
3. Scale up/down
4. Update deployment

I use HPA to automatically scale applications based on CPU/memory, ensuring optimal resource utilization."

**Key Points:**
- HPA for scaling
- Metric-based
- Min/max limits
- Automatic

---

## 🔴 ADVANCED LEVEL Questions

### Q4: How do you design a Kubernetes-based architecture?

**Answer:**
"**Architecture:**

**1. Namespaces**
- Logical separation
- Resource quotas
- Access control

**2. Deployments**
- Application deployments
- Replica management
- Rolling updates

**3. Services**
- Internal networking
- Load balancing
- Service discovery

**4. Ingress**
- External access
- SSL termination
- Routing

**5. ConfigMaps/Secrets**
- Configuration
- Sensitive data
- Environment variables

**Components:**
- Control plane
- Worker nodes
- Networking
- Storage

This architecture provides scalable, reliable container orchestration."

**Key Points:**
- Multi-layer architecture
- Namespaces
- Services and ingress
- Config management

---

## 🎯 Key Takeaways

1. **Kubernetes = Orchestration**
2. **Pods = Containers**
3. **Deployments = Management**
4. **Services = Networking**
5. **HPA = Auto-Scaling**

---

## ✅ Practice Checklist

- [ ] Can explain Kubernetes in 2 minutes
- [ ] Understand pods/deployments/services
- [ ] Know auto-scaling
- [ ] Understand architecture
- [ ] Ready for system design questions

---

**Remember**: Kubernetes is critical for container orchestration!

