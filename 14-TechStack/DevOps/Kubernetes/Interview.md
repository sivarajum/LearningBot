# Kubernetes Interview Questions & Answers

## 🔰 Beginner Level

### Q1: What is Kubernetes and why do we need it?
**Answer:**
Kubernetes (K8s) is an open-source container orchestration platform that automates the deployment, scaling, and management of containerized applications. It was originally developed by Google and is now maintained by the Cloud Native Computing Foundation (CNCF).

**Why we need it:**
- **Automated deployment and scaling**: Handles complex application deployments
- **Self-healing**: Automatically restarts failed containers, replaces unhealthy pods
- **Load balancing**: Distributes traffic across multiple instances
- **Resource optimization**: Efficiently utilizes cluster resources
- **Rolling updates**: Zero-downtime application updates
- **Multi-cloud portability**: Run on any cloud provider or on-premises

### Q2: Explain the basic Kubernetes architecture
**Answer:**
Kubernetes follows a master-worker node architecture:

**Control Plane (Master Node):**
- **API Server**: Frontend for Kubernetes API, handles all operations
- **etcd**: Distributed key-value store for cluster state
- **Controller Manager**: Runs controllers that regulate cluster state
- **Scheduler**: Assigns pods to worker nodes

**Worker Nodes:**
- **Kubelet**: Agent that ensures containers are running in pods
- **Kube Proxy**: Maintains network rules for pod communication
- **Container Runtime**: Runs containers (Docker, containerd, CRI-O)

**Key concept**: Control plane makes decisions, worker nodes execute them.

### Q3: What is a Pod in Kubernetes?
**Answer:**
A Pod is the smallest deployable unit in Kubernetes, representing one or more containers that share:

- **Network namespace**: Same IP address and port space
- **Storage volumes**: Shared storage between containers
- **Runtime environment**: Same node, same underlying container runtime

**Characteristics:**
- Ephemeral (can be destroyed and recreated)
- Atomic unit of scaling
- Usually contains one main container + optional sidecars
- Has its own IP address within the cluster

### Q4: What is the difference between a Deployment and a Pod?
**Answer:**
- **Pod**: Single instance of running containers, can be ephemeral
- **Deployment**: Higher-level abstraction that manages ReplicaSets and Pods

**Deployment provides:**
- Declarative updates for Pods
- Rolling updates and rollbacks
- Scaling (horizontal pod autoscaling)
- Self-healing (restarts failed pods)

**Analogy**: Pod is like a single server instance, Deployment is like an auto-scaling group.

### Q5: How do you create and expose a simple web application?
**Answer:**
```bash
# Create deployment
kubectl create deployment nginx --image=nginx

# Scale to 3 replicas
kubectl scale deployment nginx --replicas=3

# Expose as service
kubectl expose deployment nginx --port=80 --type=LoadBalancer

# Check status
kubectl get pods,services
```

## 🏗️ Intermediate Level

### Q6: Explain Services and their types in Kubernetes
**Answer:**
Services provide stable network endpoints for pods, abstracting the dynamic nature of pod IPs.

**Service Types:**

1. **ClusterIP (default)**: Internal cluster access only
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
     type: ClusterIP
   ```

2. **NodePort**: Exposes service on each node's port (30000-32767)
3. **LoadBalancer**: Creates external load balancer (cloud provider)
4. **ExternalName**: Maps to external DNS name

**Key concept**: Services use label selectors to find pods.

### Q7: How does Kubernetes handle storage?
**Answer:**
Kubernetes provides abstracted storage through:

**Persistent Volumes (PV):** Storage provisioned by administrator
**Persistent Volume Claims (PVC):** Requests for storage by users
**Storage Classes:** Define different storage types and provisioners

**Example PVC:**
```yaml
apiVersion: v1
kind: PersistentVolumeClaim
metadata:
  name: mysql-pvc
spec:
  accessModes:
    - ReadWriteOnce
  resources:
    requests:
      storage: 10Gi
  storageClassName: fast-ssd
```

**Access Modes:**
- ReadWriteOnce: Single node read-write
- ReadOnlyMany: Multiple nodes read-only
- ReadWriteMany: Multiple nodes read-write

### Q8: Explain ConfigMaps and Secrets
**Answer:**
Both store configuration data separately from application code.

**ConfigMaps:** Non-sensitive configuration data
```yaml
apiVersion: v1
kind: ConfigMap
metadata:
  name: app-config
data:
  DATABASE_URL: "postgres://db:5432/myapp"
  LOG_LEVEL: "info"
```

**Secrets:** Sensitive data, base64 encoded
```yaml
apiVersion: v1
kind: Secret
metadata:
name: db-secret
type: Opaque
data:
  password: bXlwYXNzd29yZA==  # base64 encoded
```

**Usage in pods:**
```yaml
envFrom:
- configMapRef:
    name: app-config
- secretRef:
    name: db-secret
```

### Q9: How do you troubleshoot a failing pod?
**Answer:**
**Systematic troubleshooting approach:**

1. **Check pod status:**
   ```bash
   kubectl get pods
   kubectl describe pod <pod-name>
   ```

2. **Check logs:**
   ```bash
   kubectl logs <pod-name>
   kubectl logs -f <pod-name>  # Follow logs
   kubectl logs -p <pod-name>  # Previous instance
   ```

3. **Check events:**
   ```bash
   kubectl get events --sort-by=.metadata.creationTimestamp
   ```

4. **Debug container:**
   ```bash
   kubectl exec -it <pod-name> -- /bin/bash
   ```

5. **Check resource usage:**
   ```bash
   kubectl top pods
   kubectl top nodes
   ```

**Common issues:**
- Image pull errors
- Insufficient resources
- Network connectivity
- Configuration errors

### Q10: Explain Kubernetes networking model
**Answer:**
Kubernetes networking follows these principles:

1. **Every pod gets its own IP address**
2. **Pods can communicate with all other pods without NAT**
3. **No need for explicit port mappings**

**Components:**
- **Container Network Interface (CNI)**: Plugs for networking (Calico, Flannel, Weave)
- **Kube Proxy**: Maintains network rules on nodes
- **Services**: Provide stable endpoints
- **Ingress**: HTTP/TCP load balancing

**Network Policies:** Control traffic flow between pods
```yaml
apiVersion: networking.k8s.io/v1
kind: NetworkPolicy
metadata:
  name: allow-frontend
spec:
  podSelector:
    matchLabels:
      app: frontend
  policyTypes:
  - Ingress
  ingress:
  - from:
    - podSelector:
        matchLabels:
          app: backend
```

## 🚀 Advanced Level

### Q11: How do you implement rolling updates and rollbacks?
**Answer:**
**Rolling Updates:** Gradually replace old pods with new ones.

**Deployment strategy:**
```yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: myapp
spec:
  replicas: 3
  strategy:
    type: RollingUpdate
    rollingUpdate:
      maxUnavailable: 1
      maxSurge: 1
  template:
    spec:
      containers:
      - name: app
        image: myapp:v2
```

**Commands:**
```bash
# Update image
kubectl set image deployment/myapp app=myapp:v2

# Check rollout status
kubectl rollout status deployment/myapp

# Rollback
kubectl rollout undo deployment/myapp

# Check history
kubectl rollout history deployment/myapp
```

### Q12: Explain Horizontal Pod Autoscaler (HPA)
**Answer:**
HPA automatically scales the number of pods based on observed metrics.

**Configuration:**
```yaml
apiVersion: autoscaling/v2
kind: HorizontalPodAutoscaler
metadata:
  name: myapp-hpa
spec:
  scaleTargetRef:
    apiVersion: apps/v1
    kind: Deployment
    name: myapp
  minReplicas: 1
  maxReplicas: 10
  metrics:
  - type: Resource
    resource:
      name: cpu
      target:
        type: Utilization
        averageUtilization: 70
```

**Scaling metrics:**
- CPU utilization
- Memory utilization
- Custom metrics (via metrics server)
- External metrics

**Requirements:**
- Metrics Server installed
- Resource requests defined on pods

### Q13: How do you secure a Kubernetes cluster?
**Answer:**
**Multi-layered security approach:**

1. **API Security:**
   - Use RBAC (Role-Based Access Control)
   - Certificate-based authentication
   - Service Account tokens

2. **Network Security:**
   - Network Policies to control pod-to-pod traffic
   - Service Mesh (Istio) for mTLS
   - Ingress controllers with TLS

3. **Pod Security:**
   - Pod Security Standards (privileged, baseline, restricted)
   - Security Contexts (run as non-root, drop capabilities)
   - Image scanning and vulnerability assessment

4. **Cluster Hardening:**
   - Regular security updates
   - Audit logging
   - Resource quotas and limits

**RBAC Example:**
```yaml
apiVersion: rbac.authorization.k8s.io/v1
kind: Role
metadata:
  name: pod-reader
rules:
- apiGroups: [""]
  resources: ["pods"]
  verbs: ["get", "list", "watch"]
---
apiVersion: rbac.authorization.k8s.io/v1
kind: RoleBinding
metadata:
  name: read-pods
subjects:
- kind: User
  name: alice
roleRef:
  kind: Role
  name: pod-reader
```

### Q14: Explain StatefulSets vs Deployments
**Answer:**

| Aspect | StatefulSet | Deployment |
|--------|-------------|------------|
| **Identity** | Stable pod identity (pod-0, pod-1) | Anonymous pods |
| **Storage** | Persistent storage per pod | Ephemeral or shared storage |
| **Scaling** | Ordered scaling | Unordered scaling |
| **Updates** | Rolling updates with identity preservation | Standard rolling updates |
| **Use cases** | Databases, stateful applications | Stateless web apps, APIs |

**StatefulSet example:**
```yaml
apiVersion: apps/v1
kind: StatefulSet
metadata:
  name: mysql
spec:
  serviceName: mysql
  replicas: 3
  template:
    spec:
      containers:
      - name: mysql
        image: mysql:8.0
        volumeMounts:
        - name: data
          mountPath: /var/lib/mysql
  volumeClaimTemplates:
  - metadata:
      name: data
    spec:
      accessModes: ["ReadWriteOnce"]
      resources:
        requests:
          storage: 10Gi
```

### Q15: How do you implement multi-environment deployments?
**Answer:**
**Strategies for multiple environments:**

1. **Namespaces:** Logical separation
   ```bash
   kubectl create namespace dev
   kubectl create namespace staging
   kubectl create namespace prod
   ```

2. **Helm Charts:** Templated deployments
   ```yaml
   # values-dev.yaml
   image:
     tag: "latest"
   replicas: 1

   # values-prod.yaml
   image:
     tag: "v1.2.3"
   replicas: 5
   ```

3. **Kustomize:** Configuration customization
   ```yaml
   # kustomization.yaml
   resources:
   - deployment.yaml
   patchesStrategicMerge:
   - prod-patches.yaml
   ```

4. **GitOps:** Declarative deployments (ArgoCD, Flux)

**Environment-specific configurations:**
- Resource limits (dev: minimal, prod: generous)
- Image versions (dev: latest, prod: tagged)
- Secrets management
- Monitoring and logging levels

## 🎯 Scenario-Based Questions

### Q16: Pod is in CrashLoopBackOff status, how do you debug?
**Answer:**
**Step-by-step debugging:**

1. **Check pod status and events:**
   ```bash
   kubectl describe pod <pod-name>
   # Look for crash events, resource constraints
   ```

2. **Check container logs:**
   ```bash
   kubectl logs <pod-name> --previous
   # Check what caused the crash
   ```

3. **Check resource limits:**
   ```bash
   kubectl get pod <pod-name> -o yaml
   # Verify requests/limits are appropriate
   ```

4. **Debug in running container:**
   ```bash
   kubectl run debug --image=busybox --rm -it --restart=Never -- sh
   # Manual testing of dependencies
   ```

5. **Check application configuration:**
   - Environment variables
   - ConfigMaps/Secrets
   - Network connectivity

**Common causes:**
- Application errors (exceptions, missing dependencies)
- Resource exhaustion (OOM killed)
- Configuration issues
- Health check failures

### Q17: How do you migrate from Docker Compose to Kubernetes?
**Answer:**
**Migration strategy:**

1. **Analyze docker-compose.yml:**
   - Identify services, networks, volumes
   - Map to Kubernetes objects

2. **Create Kubernetes manifests:**
   ```yaml
   # Convert service to Deployment + Service
   apiVersion: apps/v1
   kind: Deployment
   metadata:
     name: web
   spec:
     replicas: 1
     template:
       spec:
         containers:
         - name: web
           image: nginx
   ---
   apiVersion: v1
   kind: Service
   metadata:
     name: web
   spec:
     selector:
       app: web
     ports:
     - port: 80
   ```

3. **Handle volumes:**
   - Convert named volumes to PVCs
   - Use ConfigMaps for configuration files

4. **Network considerations:**
   - Services replace networks
   - Ingress for external access

5. **Tools:**
   - `kompose`: Automated conversion
   - Manual conversion for complex setups

### Q18: How do you implement blue-green deployment?
**Answer:**
**Blue-green deployment process:**

1. **Create blue environment (current):**
   ```yaml
   apiVersion: apps/v1
   kind: Deployment
   metadata:
     name: myapp-blue
   spec:
     replicas: 3
     selector:
       matchLabels:
         app: myapp
         version: blue
     template:
       metadata:
         labels:
           app: myapp
           version: blue
       spec:
         containers:
         - name: app
           image: myapp:v1
   ```

2. **Create green environment (new):**
   ```yaml
   # Similar deployment with version: green and new image
   ```

3. **Test green environment:**
   - Health checks
   - Smoke tests
   - Integration tests

4. **Switch traffic:**
   ```yaml
   # Update service selector
   apiVersion: v1
   kind: Service
   metadata:
     name: myapp
   spec:
     selector:
       app: myapp
       version: green  # Switch from blue to green
   ```

5. **Monitor and cleanup:**
   - Monitor error rates, latency
   - Keep blue environment for rollback
   - Clean up after successful deployment

### Q19: How do you handle database migrations in Kubernetes?
**Answer:**
**Database migration strategies:**

1. **Init Containers:**
   ```yaml
   apiVersion: apps/v1
   kind: Deployment
   metadata:
     name: app
   spec:
     template:
       spec:
         initContainers:
         - name: migrate
           image: migrate-tool
           command: ["migrate", "up"]
         containers:
         - name: app
           image: myapp
   ```

2. **Jobs for migrations:**
   ```yaml
   apiVersion: batch/v1
   kind: Job
   metadata:
     name: db-migrate
   spec:
     template:
       spec:
         containers:
         - name: migrate
           image: flyway/flyway
           command: ["flyway", "migrate"]
         restartPolicy: Never
   ```

3. **Operator-based migrations:**
   - Use database operators (PostgreSQL, MySQL operators)
   - Built-in migration handling

4. **StatefulSets for databases:**
   - Persistent storage
   - Ordered updates
   - Backup/restore capabilities

### Q20: How do you implement disaster recovery?
**Answer:**
**Comprehensive disaster recovery plan:**

1. **etcd Backup:**
   ```bash
   # Backup etcd
   ETCDCTL_API=3 etcdctl snapshot save snapshot.db \
     --endpoints=https://127.0.0.1:2379 \
     --cacert=/etc/kubernetes/pki/etcd/ca.crt \
     --cert=/etc/kubernetes/pki/etcd/server.crt \
     --key=/etc/kubernetes/pki/etcd/server.key
   ```

2. **Application Backups:**
   - Database backups (pg_dump, mysqldump)
   - Persistent volume snapshots
   - Configuration backups

3. **Multi-cluster setup:**
   - Cross-region replication
   - Federation for multi-cluster management

4. **Recovery procedures:**
   - Restore etcd from snapshot
   - Recreate PVs from snapshots
   - Redeploy applications

5. **Testing:**
   - Regular disaster recovery drills
   - Automated recovery testing

## 🧠 Expert Level

### Q21: Explain Custom Resource Definitions (CRDs)
**Answer:**
CRDs extend the Kubernetes API with custom resources.

**Creating a CRD:**
```yaml
apiVersion: apiextensions.k8s.io/v1
kind: CustomResourceDefinition
metadata:
  name: databases.example.com
spec:
  group: example.com
  versions:
  - name: v1
    served: true
    storage: true
    schema:
      openAPIV3Schema:
        type: object
        properties:
          spec:
            type: object
            properties:
              replicas:
                type: integer
  scope: Namespaced
  names:
    plural: databases
    singular: database
    kind: Database
```

**Custom Controller:** Watches for CRD changes and reconciles desired state.

**Use cases:**
- Custom operators
- Domain-specific abstractions
- Third-party integrations

### Q22: How do you implement service mesh with Istio?
**Answer:**
**Istio service mesh architecture:**

1. **Data Plane:** Envoy proxies as sidecars
2. **Control Plane:** Istio components (Pilot, Citadel, Galley)

**Traffic Management:**
```yaml
apiVersion: networking.istio.io/v1beta1
kind: VirtualService
metadata:
  name: reviews
spec:
  http:
  - route:
    - destination:
        host: reviews
        subset: v1
      weight: 90
    - destination:
        host: reviews
        subset: v2
      weight: 10
```

**Security:**
- mTLS between services
- Authorization policies
- Certificate management

**Observability:**
- Distributed tracing (Jaeger)
- Metrics collection (Prometheus)
- Service mesh dashboard (Kiali)

### Q23: Explain Kubernetes operators pattern
**Answer:**
Operators extend Kubernetes to manage complex applications.

**Operator Components:**
1. **Custom Resource Definitions (CRDs)**
2. **Custom Controllers** that watch CRDs
3. **Reconciliation logic** to achieve desired state

**Example: PostgreSQL Operator**
```yaml
apiVersion: postgresql.example.com/v1
kind: PostgreSQLCluster
metadata:
  name: my-db
spec:
  replicas: 3
  version: "13"
  storage:
    size: 10Gi
```

**Operator responsibilities:**
- Deploy and configure PostgreSQL cluster
- Handle scaling and failover
- Perform backups and restores
- Monitor health and performance

### Q24: How do you implement GitOps with Kubernetes?
**Answer:**
**GitOps workflow:**

1. **Git as single source of truth:**
   - All manifests in Git repository
   - Version controlled infrastructure

2. **Automated deployment:**
   ```yaml
   # ArgoCD Application
   apiVersion: argoproj.io/v1alpha1
   kind: Application
   metadata:
     name: myapp
   spec:
     project: default
     source:
       repoURL: https://github.com/myorg/myapp
       path: k8s
       targetRevision: HEAD
     destination:
       server: https://kubernetes.default.svc
       namespace: default
   ```

3. **Sync process:**
   - ArgoCD monitors Git repository
   - Automatically deploys changes
   - Provides drift detection and correction

4. **Benefits:**
   - Declarative deployments
   - Audit trail of changes
   - Easy rollbacks
   - Multi-environment consistency

### Q25: How do you scale Kubernetes to thousands of nodes?
**Answer:**
**Large-scale Kubernetes considerations:**

1. **Cluster Architecture:**
   - Multiple control planes (HA control plane)
   - Sharded etcd clusters
   - Regional distribution

2. **Networking:**
   - Efficient CNI plugins (Cilium for performance)
   - Network policies for isolation
   - Service mesh for advanced routing

3. **Storage:**
   - Distributed storage systems (Ceph, Portworx)
   - CSI drivers for cloud storage
   - Backup and disaster recovery

4. **Resource Management:**
   - Resource quotas and limits
   - Cluster autoscaling
   - Node affinity/anti-affinity

5. **Observability:**
   - Centralized logging (EFK stack)
   - Metrics aggregation (Thanos)
   - Distributed tracing

6. **Security:**
   - Pod Security Standards
   - Network policies
   - Service mesh security

7. **Automation:**
   - GitOps for deployments
   - Operators for application lifecycle
   - CI/CD pipelines

**Performance optimizations:**
- API server tuning
- etcd performance optimization
- Node resource management
- Application optimization

## 📚 Additional Resources

- [Kubernetes Documentation](https://kubernetes.io/docs/)
- [Kubernetes Best Practices](https://kubernetes.io/docs/concepts/)
- [CNCF Landscape](https://landscape.cncf.io/)
- [Kubernetes Security](https://kubernetes.io/docs/concepts/security/)

## 🎯 Key Takeaways

- **Master kubectl commands**: get, describe, logs, exec, apply
- **Understand core objects**: Pods, Services, Deployments, ConfigMaps
- **Know networking**: Services, Ingress, Network Policies
- **Security first**: RBAC, Pod Security Standards, Network Policies
- **Storage concepts**: PV, PVC, Storage Classes
- **Scaling**: HPA, Cluster Autoscaler, rolling updates
- **Troubleshooting**: Events, logs, describe, exec
- **Advanced patterns**: Operators, CRDs, service mesh
- **Production readiness**: Backup, monitoring, high availability

Remember: Kubernetes is about declarative configuration and self-healing systems. Focus on understanding the "why" behind each component and how they work together to provide reliable, scalable infrastructure.
