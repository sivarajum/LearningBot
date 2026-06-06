# Google Kubernetes Engine (GKE) Interview Questions and Answers

## Beginner Level Questions

### 1. What is Google Kubernetes Engine (GKE)?

**Answer:**
Google Kubernetes Engine (GKE) is a fully managed Kubernetes service that simplifies deploying, managing, and scaling containerized applications using Google infrastructure. It provides:

- **Managed Control Plane**: Google handles Kubernetes master components
- **Auto-Scaling**: Automatic scaling of nodes and pods
- **Security**: Built-in security features and compliance
- **Integration**: Deep integration with Google Cloud services
- **Reliability**: High availability with multi-zone clusters

GKE allows developers to focus on applications rather than infrastructure management.

### 2. What are the main components of a GKE cluster?

**Answer:**
A GKE cluster consists of:

- **Control Plane**: Managed by Google (API server, scheduler, controller manager)
- **Node Pools**: Groups of Compute Engine VMs running Kubernetes
- **Nodes**: Individual VMs that run pods
- **Pods**: Smallest deployable units containing containers
- **Services**: Network abstractions for accessing pods
- **Namespaces**: Virtual clusters within a physical cluster

The control plane manages the cluster state, while nodes run the actual workloads.

### 3. How do you create a GKE cluster?

**Answer:**
You can create GKE clusters through multiple methods:

**Google Cloud Console:**
1. Go to Kubernetes Engine > Clusters
2. Click "Create Cluster"
3. Choose Standard or Autopilot mode
4. Configure cluster basics (name, region, zones)
5. Configure node pools and networking
6. Click "Create"

**gcloud CLI:**
```bash
gcloud container clusters create my-cluster \
  --zone=us-central1-a \
  --num-nodes=3 \
  --machine-type=e2-medium
```

**Terraform:**
```hcl
resource "google_container_cluster" "primary" {
  name     = "my-gke-cluster"
  location = "us-central1"

  node_pool {
    name       = "default-pool"
    node_count = 3

    node_config {
      machine_type = "e2-medium"
    }
  }
}
```

### 4. What is the difference between Standard GKE and Autopilot?

**Answer:**
**Standard GKE:**
- Full control over node configuration and management
- Manual node pool management and scaling
- Access to all Kubernetes features
- More flexibility but requires more operational overhead

**Autopilot:**
- Fully managed by Google (nodes, scaling, security)
- Automatic optimization of resources
- Enhanced security with automatic updates
- Simplified operations with less configuration
- Higher cost but reduced operational complexity

Choose Standard for maximum control, Autopilot for simplicity.

## Intermediate Level Questions

### 5. How does node auto-scaling work in GKE?

**Answer:**
GKE provides two levels of auto-scaling:

**Cluster Autoscaler:**
- Automatically adds/removes nodes based on pod resource requests
- Works at the node pool level
- Considers pod scheduling constraints
- Helps optimize resource utilization and costs

**Node Auto-Provisioning (NAP):**
- Automatically creates new node pools with appropriate machine types
- Learns from past usage patterns
- Optimizes for cost and performance
- Available in Standard GKE

**Configuration:**
```yaml
# Enable cluster autoscaling
cluster:
  autoscaling:
    enableNodeAutoprovisioning: true
    autoscalingProfile: OPTIMIZE_UTILIZATION
    resourceLimits:
    - resourceType: cpu
      minimum: 1
      maximum: 100
    - resourceType: memory
      minimum: 1
      maximum: 1000
```

### 6. How do you implement horizontal pod autoscaling in GKE?

**Answer:**
Horizontal Pod Autoscaling (HPA) automatically scales pod replicas:

**How it works:**
- Monitors CPU utilization, memory usage, or custom metrics
- Compares current usage against target thresholds
- Adds or removes pod replicas to maintain target utilization
- Works with Deployments, StatefulSets, and custom resources

**Implementation:**
```yaml
apiVersion: autoscaling/v2
kind: HorizontalPodAutoscaler
metadata:
  name: web-app-hpa
spec:
  scaleTargetRef:
    apiVersion: apps/v1
    kind: Deployment
    name: web-app
  minReplicas: 2
  maxReplicas: 10
  metrics:
  - type: Resource
    resource:
      name: cpu
      target:
        type: Utilization
        averageUtilization: 70
  - type: Resource
    resource:
      name: memory
      target:
        type: Utilization
        averageUtilization: 80
```

**Custom Metrics:**
```yaml
metrics:
- type: Pods
  pods:
    metric:
      name: packets-per-second
    target:
      type: AverageValue
      averageValue: 1k
```

### 7. What are the networking options in GKE?

**Answer:**
GKE provides comprehensive networking capabilities:

**VPC-Native Networking:**
- Direct integration with Google Cloud VPC
- Each pod gets a unique IP address
- No overlay networking required
- Better performance and observability

**Network Policies:**
- Control traffic between pods
- Implement zero-trust networking
- Support for Calico network plugin

**Load Balancing:**
- HTTP(S) Load Balancing for web applications
- Network Load Balancing for TCP/UDP traffic
- Internal Load Balancing within VPC

**Service Types:**
- ClusterIP: Internal cluster access
- NodePort: Access via node IP and static port
- LoadBalancer: External load balancer
- ExternalName: CNAME records

### 8. How do you manage persistent storage in GKE?

**Answer:**
GKE provides multiple storage options for stateful applications:

**Persistent Volumes (PV) and Claims (PVC):**
```yaml
apiVersion: v1
kind: PersistentVolumeClaim
metadata:
  name: my-pvc
spec:
  accessModes:
    - ReadWriteOnce
  resources:
    requests:
      storage: 50Gi
  storageClassName: standard
```

**Storage Classes:**
- standard: HDD-based persistent disks
- premium-rwo: SSD persistent disks
- standard-rwo: Regional persistent disks

**StatefulSets for Stateful Applications:**
```yaml
apiVersion: apps/v1
kind: StatefulSet
metadata:
  name: mysql
spec:
  serviceName: mysql
  replicas: 3
  selector:
    matchLabels:
      app: mysql
  template:
    spec:
      containers:
      - name: mysql
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
          storage: 100Gi
```

### 9. What are the security best practices for GKE?

**Answer:**
GKE security encompasses multiple layers:

**Cluster Security:**
- Use private clusters to avoid public IPs
- Enable Binary Authorization for container verification
- Implement Pod Security Standards
- Use shielded GKE nodes

**Network Security:**
- Implement network policies for pod isolation
- Use VPC Service Controls for data protection
- Enable Cloud Armor for DDoS protection

**Access Control:**
- Use RBAC for fine-grained permissions
- Implement Workload Identity for GCP service access
- Use service accounts with minimal privileges

**Container Security:**
- Scan images for vulnerabilities
- Use distroless or minimal base images
- Run containers as non-root users
- Implement security contexts

### 10. How do you monitor GKE clusters?

**Answer:**
GKE monitoring uses Google Cloud's observability suite:

**Cloud Monitoring:**
- System metrics (CPU, memory, disk, network)
- Kubernetes metrics (pod status, node health)
- Custom application metrics
- Alerting policies for proactive monitoring

**Cloud Logging:**
- Container logs from all pods
- System logs from Kubernetes components
- Audit logs for API server access
- Log-based metrics and alerts

**Key Metrics to Monitor:**
```sql
-- Pod resource usage
SELECT
  pod_name,
  container_name,
  AVG(cpu_usage) as avg_cpu,
  AVG(memory_usage) as avg_memory
FROM `my-project.global._Default._Default`
WHERE resource.type = "k8s_container"
  AND metric.type = "kubernetes.io/container/cpu/core_usage_time"
GROUP BY pod_name, container_name;

-- Node health
SELECT
  node_name,
  status,
  cpu_allocatable,
  memory_allocatable
FROM `my-project.global._Default._Default`
WHERE resource.type = "k8s_node";
```

**Dashboards:**
- GKE-specific dashboards in Cloud Monitoring
- Custom dashboards for application metrics
- Uptime checks for service availability

## Advanced Level Questions

### 11. How do you implement CI/CD with GKE?

**Answer:**
GKE integrates seamlessly with Google Cloud CI/CD tools:

**Cloud Build Integration:**
```yaml
steps:
  - name: 'gcr.io/cloud-builders/docker'
    args: ['build', '-t', 'gcr.io/$PROJECT_ID/my-app:$COMMIT_SHA', '.']
  - name: 'gcr.io/cloud-builders/docker'
    args: ['push', 'gcr.io/$PROJECT_ID/my-app:$COMMIT_SHA']
  - name: 'gcr.io/cloud-builders/kubectl'
    args: ['set', 'image', 'deployment/my-app', 'my-app=gcr.io/$PROJECT_ID/my-app:$COMMIT_SHA']
    env:
    - 'CLOUDSDK_COMPUTE_ZONE=us-central1-a'
    - 'CLOUDSDK_CONTAINER_CLUSTER=my-cluster'
```

**Deployment Strategies:**
- **Rolling Updates**: Gradual replacement of pods
- **Blue-Green**: Switch between two environments
- **Canary**: Route percentage of traffic to new version

**GitOps with Config Sync:**
```yaml
apiVersion: configsync.gke.io/v1beta1
kind: RepoSync
metadata:
  name: repo-sync
  namespace: config-management-system
spec:
  sourceFormat: unstructured
  git:
    repo: https://github.com/my-org/my-app
    branch: main
    dir: "config"
    auth: token
```

### 12. What are the high availability features of GKE?

**Answer:**
GKE provides multiple layers of high availability:

**Regional Clusters:**
- Control plane replicated across zones
- Automatic failover between zones
- Survives zone-level failures

**Multi-Zone Node Pools:**
- Nodes distributed across multiple zones
- Workload resilience to zone failures
- Load balancing across healthy nodes

**Pod Disruption Budgets:**
```yaml
apiVersion: policy/v1
kind: PodDisruptionBudget
metadata:
  name: web-app-pdb
spec:
  minAvailable: 2
  selector:
    matchLabels:
      app: web-app
```

**Anti-Affinity Rules:**
```yaml
affinity:
  podAntiAffinity:
    requiredDuringSchedulingIgnoredDuringExecution:
    - labelSelector:
        matchExpressions:
        - key: app
          operator: In
          values:
          - web-app
      topologyKey: kubernetes.io/zone
```

### 13. How do you optimize costs in GKE?

**Answer:**
Cost optimization strategies for GKE:

**Resource Optimization:**
- Set appropriate resource requests and limits
- Use HPA to scale based on actual usage
- Implement cluster autoscaling

**Node Pool Optimization:**
- Use spot VMs for non-critical workloads (up to 80% savings)
- Choose right machine types for workloads
- Use node auto-provisioning for optimal sizing

**Storage Optimization:**
- Use appropriate storage classes
- Implement storage lifecycle policies
- Use emptyDir for temporary data

**Monitoring Costs:**
```sql
-- Monitor GKE costs
SELECT
  service.description,
  sku.description,
  SUM(cost) as total_cost
FROM `project.billing.gcp_billing_export_v1_xxxxxx`
WHERE service.description = "Kubernetes Engine"
  AND DATE(_PARTITIONTIME) >= "2023-01-01"
GROUP BY service.description, sku.description
ORDER BY total_cost DESC;
```

### 14. How do you implement service mesh with GKE?

**Answer:**
GKE integrates with Istio for service mesh capabilities:

**Anthos Service Mesh:**
- Managed Istio distribution
- Automatic sidecar injection
- Integrated observability
- Security features (mTLS, authorization)

**Traffic Management:**
```yaml
apiVersion: networking.istio.io/v1alpha3
kind: VirtualService
metadata:
  name: web-app
spec:
  http:
  - match:
    - uri:
        prefix: "/api"
    route:
    - destination:
        host: api-service
  - route:
    - destination:
        host: web-service
```

**Security Policies:**
```yaml
apiVersion: security.istio.io/v1beta1
kind: PeerAuthentication
metadata:
  name: default
  namespace: istio-system
spec:
  mtls:
    mode: STRICT
```

**Observability:**
- Kiali for service mesh visualization
- Jaeger for distributed tracing
- Prometheus for metrics collection

### 15. What are the performance limits of GKE?

**Answer:**
Understanding GKE scale and performance limits:

**Cluster Limits:**
- Nodes per cluster: 15,000
- Pods per cluster: 110,000
- Pods per node: 256 (default), 512 (maximum)
- Services per cluster: 65,536

**Performance Considerations:**
- Network throughput: Up to 100 Gbps per node
- API server requests: Rate limited
- etcd performance: Scales with cluster size

**Optimization Techniques:**
- Use node pools for workload isolation
- Implement resource quotas and limits
- Use cluster autoscaling for dynamic scaling
- Monitor and optimize pod scheduling

### 16. How do you implement disaster recovery for GKE?

**Answer:**
Disaster recovery strategies for GKE:

**Multi-Cluster Architecture:**
- Primary and backup clusters in different regions
- Cross-region replication for data
- Automated failover procedures

**Backup and Restore:**
- Use Velero for Kubernetes resource backup
- Persistent volume snapshots for data protection
- Config Sync for configuration replication

**Failover Implementation:**
```yaml
# DNS-based failover
resource "google_dns_record_set" "app" {
  name = "app.example.com."
  type = "CNAME"
  ttl  = 300

  # Point to primary load balancer initially
  rrdatas = [google_compute_global_address.primary.address]

  # Update to backup during failover
  # rrdatas = [google_compute_global_address.backup.address]
}
```

**Testing DR:**
- Regular failover testing
- Validate backup integrity
- Test recovery time objectives (RTO)
- Document and automate recovery procedures

### 17. How do you migrate workloads to GKE?

**Answer:**
Migration strategies and tools:

**Lift and Shift:**
- Use Migrate for Compute Engine to GKE
- Containerize existing applications
- Minimal code changes required

**Application Modernization:**
- Break down monoliths into microservices
- Implement service mesh
- Adopt GitOps practices

**Migration Tools:**
```bash
# Migrate for GKE
gcloud alpha migration vms initialize \
  --project=my-project \
  --source=aws \
  --region=us-central1

# Create migration
gcloud alpha migration migration-plans create my-migration \
  --project=my-project \
  --region=us-central1 \
  --source-vm-id=i-1234567890abcdef0 \
  --target-vm-name=migrated-vm
```

**Post-Migration:**
- Optimize resource allocation
- Implement monitoring and alerting
- Update CI/CD pipelines
- Train teams on Kubernetes operations

### 18. What are the differences between GKE and other Kubernetes services?

**Answer:**
Comparison with other managed Kubernetes services:

**vs Amazon EKS:**
- **Integration**: GKE has deeper GCP integration
- **Networking**: VPC-native vs AWS VPC CNI
- **Security**: GKE has Binary Authorization, EKS has IAM integration
- **Autopilot**: GKE offers fully managed mode

**vs Azure AKS:**
- **Scaling**: Both offer excellent scaling capabilities
- **Pricing**: GKE Autopilot vs AKS automatic mode
- **AI/ML**: GKE has better TPU integration
- **Global**: Both support multi-region deployments

**vs Self-Managed Kubernetes:**
- **Operations**: Managed control plane reduces operational burden
- **Upgrades**: Automatic upgrades vs manual management
- **Security**: Built-in security features and compliance
- **Cost**: Pay for managed service vs infrastructure costs

### 19. How do you implement GitOps with GKE?

**Answer:**
GitOps implementation for declarative deployment:

**Config Sync (Anthos):**
```yaml
apiVersion: configmanagement.gke.io/v1
kind: ConfigManagement
metadata:
  name: config-management
spec:
  clusterName: my-cluster
  git:
    syncRepo: https://github.com/my-org/config-repo
    syncBranch: main
    secretType: token
    policyDir: "clusters/my-cluster"
```

**Flux CD:**
```yaml
apiVersion: source.toolkit.fluxcd.io/v1beta1
kind: GitRepository
metadata:
  name: my-app
  namespace: flux-system
spec:
  interval: 1m
  url: https://github.com/my-org/my-app
  ref:
    branch: main

---
apiVersion: kustomize.toolkit.fluxcd.io/v1beta1
kind: Kustomization
metadata:
  name: my-app
  namespace: flux-system
spec:
  interval: 5m
  path: "./kustomize"
  prune: true
  sourceRef:
    kind: GitRepository
    name: my-app
```

**Benefits:**
- Declarative configuration management
- Version control for infrastructure
- Automated deployment of changes
- Rollback capabilities

### 20. How do you troubleshoot GKE issues?

**Answer:**
Systematic troubleshooting approach for GKE:

**Cluster Issues:**
```bash
# Check cluster status
gcloud container clusters describe my-cluster

# Check node pools
gcloud container node-pools list --cluster=my-cluster

# Check cluster events
kubectl get events --sort-by=.metadata.creationTimestamp
```

**Pod Issues:**
```bash
# Check pod status
kubectl get pods -o wide

# Check pod logs
kubectl logs my-pod

# Debug pod issues
kubectl describe pod my-pod

# Check resource usage
kubectl top pods
kubectl top nodes
```

**Network Issues:**
```bash
# Check services
kubectl get services

# Check endpoints
kubectl get endpoints

# Test connectivity
kubectl run test-pod --image=busybox --rm -it -- wget --spider http://my-service
```

**Common Issues:**
- Resource constraints (CPU/memory)
- Image pull errors
- Network policies blocking traffic
- RBAC permission issues
- Storage mount failures

## Scenario-Based Questions

### 21. How would you design a microservices architecture on GKE?

**Answer:**
Microservices design principles on GKE:

**Service Architecture:**
```yaml
# API Gateway service
apiVersion: networking.istio.io/v1alpha3
kind: Gateway
metadata:
  name: api-gateway
spec:
  selector:
    istio: ingressgateway
  servers:
  - port:
      number: 80
      name: http
      protocol: HTTP
    hosts:
    - "api.example.com"

---
# Virtual service for routing
apiVersion: networking.istio.io/v1alpha3
kind: VirtualService
metadata:
  name: api-routing
spec:
  hosts:
  - "api.example.com"
  http:
  - match:
    - uri:
        prefix: "/users"
    route:
    - destination:
        host: user-service
  - match:
    - uri:
        prefix: "/orders"
    route:
    - destination:
        host: order-service
```

**Inter-Service Communication:**
- Use service mesh for mTLS
- Implement circuit breakers
- Use distributed tracing
- Implement retry and timeout policies

**Data Management:**
- Database per service pattern
- Event-driven communication with Pub/Sub
- Saga pattern for distributed transactions
- CQRS for complex read models

### 22. How would you implement a canary deployment strategy?

**Answer:**
Canary deployment for gradual rollout:

**Implementation:**
```yaml
# Create canary deployment
apiVersion: apps/v1
kind: Deployment
metadata:
  name: web-app-canary
spec:
  replicas: 1
  selector:
    matchLabels:
      app: web-app
      version: canary
  template:
    metadata:
      labels:
        app: web-app
        version: canary
    spec:
      containers:
      - name: web-app
        image: gcr.io/my-project/web-app:v2.0.0

---
# Istio virtual service for traffic splitting
apiVersion: networking.istio.io/v1alpha3
kind: VirtualService
metadata:
  name: web-app
spec:
  hosts:
  - web-app
  http:
  - route:
    - destination:
        host: web-app
        subset: v1
      weight: 90
    - destination:
        host: web-app
        subset: canary
      weight: 10
```

**Monitoring Canary:**
- Track error rates and latency
- Monitor custom business metrics
- Set up automated rollback triggers
- Gradually increase canary traffic

**Promotion Process:**
- Automated promotion based on success criteria
- Gradual traffic shifting (10% → 25% → 50% → 100%)
- Rollback capability if issues detected

### 23. How would you handle a production outage in GKE?

**Answer:**
Production incident response:

**Immediate Response:**
1. **Assess Impact**: Determine affected services and users
2. **Gather Information**: Check monitoring dashboards and alerts
3. **Communicate**: Notify stakeholders and customers
4. **Mitigate**: Implement temporary workarounds

**Investigation:**
```bash
# Check recent events
kubectl get events --sort-by=.lastTimestamp | tail -20

# Check pod status
kubectl get pods -A | grep -v Running

# Check node status
kubectl get nodes | grep -v Ready

# Review logs
kubectl logs deployment/my-deployment --previous
```

**Root Cause Analysis:**
- Review deployment history
- Check for recent configuration changes
- Analyze resource utilization patterns
- Review application and infrastructure logs

**Recovery:**
- Scale up affected services
- Roll back to previous version if needed
- Implement permanent fixes
- Test recovery procedures

**Post-Incident:**
- Document incident timeline and resolution
- Implement preventive measures
- Update monitoring and alerting
- Conduct post-mortem analysis

## Summary

GKE interview questions typically cover:
- Basic cluster creation and management
- Auto-scaling and resource optimization
- Networking and security
- Monitoring and troubleshooting
- CI/CD integration and deployment strategies
- High availability and disaster recovery
- Cost optimization
- Migration and modernization approaches

Focus on understanding GKE's role in modernizing applications, its integration with Google Cloud, and best practices for operating Kubernetes at scale.
