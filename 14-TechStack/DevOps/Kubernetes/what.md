# Kubernetes (K8s) - Complete Technical Guide

## What is Kubernetes?

Kubernetes is an open-source container orchestration platform that automates the deployment, scaling, and management of containerized applications. Originally developed by Google and now maintained by the Cloud Native Computing Foundation (CNCF), Kubernetes provides a framework for running distributed systems resiliently.

## Core Concepts and Architecture

### Control Plane Components

#### API Server (kube-apiserver)
The API server is the front-end for the Kubernetes control plane. It exposes the Kubernetes API and handles all REST operations.

**Key responsibilities:**
- Validates and processes API requests
- Updates etcd with current state
- Serves as the primary interface for all cluster operations
- Handles authentication and authorization

#### etcd
A distributed key-value store that serves as Kubernetes' backing store for all cluster data.

**Characteristics:**
- Consistent and highly available
- Stores cluster state, configuration, and metadata
- Uses Raft consensus algorithm for consistency
- Critical for cluster recovery and state management

#### Controller Manager (kube-controller-manager)
Runs controller processes that regulate the state of the cluster.

**Built-in controllers:**
- **Node Controller**: Manages node availability
- **Replication Controller**: Maintains correct pod count
- **Endpoints Controller**: Populates endpoint objects
- **Service Account & Token Controllers**: Manage accounts and API tokens

#### Scheduler (kube-scheduler)
Assigns pods to nodes based on resource requirements and constraints.

**Scheduling decisions based on:**
- Resource requirements (CPU, memory)
- Node affinity/anti-affinity rules
- Pod affinity/anti-affinity rules
- Taints and tolerations
- Custom scheduler policies

### Node Components

#### Kubelet
An agent that runs on each node in the cluster.

**Responsibilities:**
- Registers node with API server
- Monitors pod specifications via API server
- Reports node and pod status
- Manages container lifecycle (via container runtime)
- Handles node maintenance operations

#### Kube Proxy
Maintains network rules on nodes for pod communication.

**Functions:**
- Implements Kubernetes Service concept
- Load balances traffic across pods
- Manages iptables rules or IPVS
- Handles service discovery within cluster

#### Container Runtime
Software responsible for running containers (Docker, containerd, CRI-O).

## Kubernetes Objects

### Pods
The smallest deployable unit in Kubernetes, representing one or more containers that share storage and network resources.

**Pod characteristics:**
- Ephemeral (not durable)
- Share same network namespace
- Can have multiple containers (sidecar pattern)
- Atomic deployment unit

**Pod lifecycle phases:**
- Pending: Accepted but not scheduled
- Running: Bound to node, all containers running
- Succeeded: All containers terminated successfully
- Failed: At least one container failed
- Unknown: State cannot be determined

### Services
An abstraction that defines a logical set of pods and a policy for accessing them.

**Service types:**
- **ClusterIP**: Internal cluster access (default)
- **NodePort**: Exposes service on each node's port
- **LoadBalancer**: Creates external load balancer
- **ExternalName**: Maps service to external DNS name

### Deployments
Provides declarative updates for Pods and ReplicaSets.

**Features:**
- Rolling updates and rollbacks
- Scaling applications
- Pause/resume deployments
- Declarative configuration

### ReplicaSets
Ensures specified number of pod replicas are running at any time.

**Responsibilities:**
- Maintains desired pod count
- Creates/deletes pods as needed
- Used by Deployments for scaling

### ConfigMaps and Secrets
Store configuration data separately from application code.

**ConfigMaps:** Non-sensitive configuration data
**Secrets:** Sensitive data (API keys, passwords, certificates)

### Persistent Volumes (PV) and Persistent Volume Claims (PVC)
Abstract storage details from pods.

**PV:** Storage provisioned by administrator or dynamically
**PVC:** Request for storage by user

**Access modes:**
- ReadWriteOnce: Single node read-write
- ReadOnlyMany: Multiple nodes read-only
- ReadWriteMany: Multiple nodes read-write

### Namespaces
Virtual clusters within physical cluster for resource isolation.

**Use cases:**
- Multi-tenant environments
- Environment separation (dev/staging/prod)
- Resource quota management
- Access control

## Networking Model

### Container-to-Container Communication
Containers within same pod communicate via localhost.

### Pod-to-Pod Communication
All pods can communicate with each other without NAT.

### Service-to-Service Communication
Services provide stable endpoints for pod groups.

### External-to-Service Communication
Services expose applications to external traffic.

### Network Policies
Control traffic flow between pods and network endpoints.

**Capabilities:**
- Allow/deny traffic based on labels
- Namespace isolation
- Ingress/egress rules

## Storage Architecture

### Volume Types
- **emptyDir**: Temporary storage, pod lifetime
- **hostPath**: Host node filesystem access
- **nfs**: Network File System
- **persistentVolumeClaim**: Abstracted storage
- **configMap/secret**: Configuration data
- **cloud provider volumes**: AWS EBS, GCP PD, Azure Disk

### Storage Classes
Define different storage types and provisioners.

**Dynamic provisioning:**
- Automatically creates PVs based on PVC requests
- Supports different storage backends
- Configurable via StorageClass manifests

## Security Model

### Authentication
Multiple authentication methods:
- Client certificates
- Bearer tokens
- HTTP Basic authentication
- Service Account tokens

### Authorization
Controls what authenticated users can do.

**Authorization modes:**
- RBAC (Role-Based Access Control)
- ABAC (Attribute-Based Access Control)
- Webhook
- Node authorization

### RBAC Components
- **Role/ClusterRole**: Define permissions
- **RoleBinding/ClusterRoleBinding**: Bind roles to subjects
- **Subjects**: Users, groups, service accounts

### Pod Security
- **SecurityContext**: Container-level security settings
- **PodSecurityPolicy** (deprecated): Cluster-wide pod security
- **Pod Security Standards**: privileged, baseline, restricted

## Application Deployment Strategies

### Rolling Updates
Gradually replace old pods with new ones.

**Configuration:**
```yaml
strategy:
  type: RollingUpdate
  rollingUpdate:
    maxUnavailable: 25%
    maxSurge: 25%
```

### Blue-Green Deployment
Maintain two identical environments.

**Process:**
1. Deploy new version alongside old
2. Test new version
3. Switch traffic instantly
4. Keep old version for rollback

### Canary Deployment
Gradually roll out changes to subset of users.

**Implementation:**
- Use service mesh (Istio) for traffic splitting
- Multiple deployments with different labels
- Weighted load balancing

### A/B Testing
Route traffic based on user characteristics.

## Scaling and Performance

### Horizontal Pod Autoscaler (HPA)
Automatically scales pod count based on metrics.

**Scaling metrics:**
- CPU utilization
- Memory utilization
- Custom metrics (via metrics server)
- External metrics

### Vertical Pod Autoscaler (VPA)
Automatically adjusts pod resource requests/limits.

### Cluster Autoscaler
Automatically adjusts node count in cloud environments.

### Resource Management
- **Requests**: Guaranteed resources
- **Limits**: Maximum allowed resources
- **QoS Classes**: Guaranteed, Burstable, BestEffort

## Observability

### Monitoring
- **Metrics Server**: Basic resource metrics
- **Prometheus**: Comprehensive monitoring
- **Grafana**: Visualization dashboards

### Logging
- **Container logs**: Via kubectl logs
- **Cluster-level logging**: Fluentd, ELK stack
- **Centralized logging**: Aggregated log collection

### Tracing
- **Jaeger**: Distributed tracing
- **OpenTelemetry**: Observability framework

## Kubernetes Ecosystem

### Package Management
- **Helm**: Package manager for Kubernetes
- **Kustomize**: Configuration customization
- **Operator Framework**: Application lifecycle management

### Service Mesh
- **Istio**: Traffic management, security, observability
- **Linkerd**: Lightweight service mesh
- **Consul**: Service discovery and configuration

### CI/CD Integration
- **Jenkins X**: Kubernetes-native CI/CD
- **Tekton**: Cloud-native CI/CD pipelines
- **ArgoCD**: GitOps continuous delivery

### Cloud Providers
- **GKE (Google)**: Managed Kubernetes
- **EKS (AWS)**: Managed Kubernetes
- **AKS (Azure)**: Managed Kubernetes

## Advanced Concepts

### Custom Resource Definitions (CRDs)
Extend Kubernetes API with custom resources.

**Use cases:**
- Custom controllers
- Domain-specific abstractions
- Third-party integrations

### Operators
Software extensions that manage applications and their components.

**Capabilities:**
- Automate complex deployments
- Handle upgrades and backups
- Monitor application health
- React to cluster events

### StatefulSets
Manage stateful applications with stable identities.

**Features:**
- Stable pod identities
- Ordered deployment/scaling
- Persistent storage per pod
- Stable network identifiers

### DaemonSets
Ensure one pod runs on each node.

**Use cases:**
- Log collection agents
- Monitoring agents
- Network plugins
- Storage daemons

### Jobs and CronJobs
Run tasks to completion.

**Job types:**
- **Non-parallel jobs**: Single pod
- **Parallel jobs**: Multiple pods
- **Work queues**: Process work items

## Production Considerations

### High Availability
- Multi-master setup
- Etcd clustering
- Load balancer for API server
- Pod anti-affinity for critical components

### Backup and Recovery
- etcd snapshots
- Persistent volume backups
- Application-level backups
- Disaster recovery planning

### Resource Optimization
- Right-sizing pods
- Cluster capacity planning
- Cost optimization
- Performance monitoring

### Security Hardening
- Network policies
- Pod security standards
- Image scanning
- RBAC configuration
- Audit logging

## Common Patterns and Anti-patterns

### Patterns
- **Sidecar Pattern**: Additional containers in pod
- **Init Containers**: Setup tasks before main containers
- **ConfigMaps for Configuration**: Externalize configuration
- **Secrets for Sensitive Data**: Secure credential management

### Anti-patterns
- **Pods with Multiple Responsibilities**: Violates single responsibility
- **Direct Pod Management**: Use controllers instead
- **Hardcoded Values**: Use ConfigMaps/Secrets
- **Resource Over-provisioning**: Leads to waste

## Kubernetes vs Other Orchestration Tools

### Docker Swarm
- **Simplicity**: Easier to set up and manage
- **Integration**: Native Docker integration
- **Features**: Basic orchestration features
- **Use case**: Small to medium deployments

### Kubernetes Advantages
- **Ecosystem**: Rich ecosystem and community
- **Scalability**: Handles larger, more complex deployments
- **Flexibility**: Highly customizable
- **Adoption**: Industry standard

## Getting Started

### Installation Options
- **Minikube**: Local single-node cluster
- **Kind**: Kubernetes in Docker
- **k3s**: Lightweight Kubernetes
- **Managed services**: GKE, EKS, AKS

### Basic Commands
```bash
# Cluster info
kubectl cluster-info

# Node status
kubectl get nodes

# Pod management
kubectl get pods
kubectl describe pod <pod-name>
kubectl logs <pod-name>

# Deployment management
kubectl create deployment <name> --image=<image>
kubectl scale deployment <name> --replicas=3
kubectl rollout status deployment/<name>
```

## Learning Path

1. **Fundamentals**: Pods, Services, Deployments
2. **Configuration**: ConfigMaps, Secrets, Resource management
3. **Networking**: Services, Ingress, Network Policies
4. **Storage**: Persistent Volumes, Storage Classes
5. **Security**: RBAC, Pod Security, Network Policies
6. **Observability**: Monitoring, Logging, Tracing
7. **Advanced**: Operators, Custom Resources, Service Mesh
8. **Production**: High availability, backup, disaster recovery

## Best Practices

- **Resource Management**: Always set requests and limits
- **Health Checks**: Implement readiness and liveness probes
- **Security**: Use RBAC, scan images, implement network policies
- **Monitoring**: Set up comprehensive monitoring and alerting
- **Documentation**: Document cluster configurations and procedures
- **Testing**: Test deployments, rollbacks, and scaling operations
- **Backup**: Regular backups of etcd and persistent data

Kubernetes represents the evolution of container orchestration, providing robust, scalable, and manageable infrastructure for modern applications. Its declarative approach and extensive ecosystem make it the de facto standard for container orchestration in production environments.
