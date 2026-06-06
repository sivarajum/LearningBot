# Kubernetes Visual Architecture Guide

## Kubernetes Cluster Architecture

```mermaid
graph TB
    %% Define styles
    classDef controlPlaneClass fill:#e3f2fd,stroke:#1976d2,stroke-width:3px,color:#0d47a1
    classDef etcdClass fill:#f3e5f5,stroke:#7b1fa2,stroke-width:3px,color:#4a148c
    classDef nodeClass fill:#e8f5e8,stroke:#388e3c,stroke-width:3px,color:#1b5e20
    classDef userClass fill:#fff3e0,stroke:#f57c00,stroke-width:3px,color:#e65100

    subgraph "🎛️ Control Plane"
        API[🔌 API Server<br/>kube-apiserver]
        CM[⚙️ Controller Manager<br/>kube-controller-manager]
        SCHED[📅 Scheduler<br/>kube-scheduler]
    end

    subgraph "💾 etcd"
        ETCD[💾 etcd<br/>Distributed Store]
    end

    subgraph "🖥️ Worker Nodes"
        NODE1[💻 Node 1]
        NODE2[💻 Node 2]
        NODE3[💻 Node 3]
    end

    subgraph "👤 Users"
        ADMIN[👑 Cluster Admin]
        DEV[👨‍💻 Developer]
        KUBECTL[kubectl CLI]
    end

    ADMIN --> KUBECTL
    DEV --> KUBECTL
    KUBECTL --> API

    API --> CM
    API --> SCHED
    CM --> ETCD
    SCHED --> ETCD
    API --> ETCD

    API --> NODE1
    API --> NODE2
    API --> NODE3

    %% Apply styles
    class API,CM,SCHED controlPlaneClass
    class ETCD etcdClass
    class NODE1,NODE2,NODE3 nodeClass
    class ADMIN,DEV,KUBECTL userClass
```

## Node Architecture

```mermaid
graph TD
    %% Define styles
    classDef kubeletClass fill:#e3f2fd,stroke:#1976d2,stroke-width:3px,color:#0d47a1
    classDef proxyClass fill:#f3e5f5,stroke:#7b1fa2,stroke-width:3px,color:#4a148c
    classDef runtimeClass fill:#e8f5e8,stroke:#388e3c,stroke-width:3px,color:#1b5e20
    classDef podClass fill:#fff3e0,stroke:#f57c00,stroke-width:2px,color:#e65100

    subgraph "💻 Worker Node"
        KUBELET[🤖 Kubelet<br/>Node Agent]
        KUBE_PROXY[🌐 Kube Proxy<br/>Network Proxy]
        CRI[📦 Container Runtime<br/>Docker/containerd]
    end

    subgraph "🐳 Pods"
        POD1[📦 Pod 1<br/>App Container + Sidecar]
        POD2[📦 Pod 2<br/>Web Server]
        POD3[📦 Pod 3<br/>Database]
    end

    subgraph "🏠 Host Resources"
        CPU[⚡ CPU]
        MEMORY[🧠 RAM]
        STORAGE[💾 Disk]
        NETWORK[🌐 Network]
    end

    KUBELET --> CRI
    KUBELET --> KUBE_PROXY
    CRI --> POD1
    CRI --> POD2
    CRI --> POD3

    KUBELET --> CPU
    KUBELET --> MEMORY
    KUBELET --> STORAGE
    KUBELET --> NETWORK

    %% Apply styles
    class KUBELET kubeletClass
    class KUBE_PROXY proxyClass
    class CRI runtimeClass
    class POD1,POD2,POD3 podClass
```

## Pod Architecture

```mermaid
graph TD
    %% Define styles
    classDef podClass fill:#e3f2fd,stroke:#1976d2,stroke-width:3px,color:#0d47a1
    classDef containerClass fill:#f3e5f5,stroke:#7b1fa2,stroke-width:2px,color:#4a148c
    classDef volumeClass fill:#e8f5e8,stroke:#388e3c,stroke-width:2px,color:#1b5e20
    classDef networkClass fill:#fff3e0,stroke:#f57c00,stroke-width:2px,color:#e65100

    subgraph "📦 Pod"
        PAUSE[⏸️ Pause Container<br/>Infrastructure]
        APP[🚀 Application Container<br/>Main App]
        SIDECAR[🔧 Sidecar Container<br/>Logging/Proxy]
    end

    subgraph "💾 Shared Volumes"
        EMPTYDIR[📁 emptyDir<br/>Temporary]
        CONFIGMAP[⚙️ ConfigMap<br/>Configuration]
        SECRET[🔐 Secret<br/>Credentials]
        PVC[💽 PersistentVolumeClaim<br/>Persistent Data]
    end

    subgraph "🌐 Network Namespace"
        NETWORK[🌐 Shared Network<br/>Same IP, ports]
        LOOPBACK[🔄 localhost<br/>Inter-container comms]
    end

    PAUSE --> APP
    PAUSE --> SIDECAR

    APP --> EMPTYDIR
    APP --> CONFIGMAP
    APP --> SECRET
    APP --> PVC

    SIDECAR --> EMPTYDIR
    SIDECAR --> CONFIGMAP

    PAUSE --> NETWORK
    NETWORK --> LOOPBACK

    %% Apply styles
    class PAUSE podClass
    class APP,SIDECAR containerClass
    class EMPTYDIR,CONFIGMAP,SECRET,PVC volumeClass
    class NETWORK,LOOPBACK networkClass
```

## Service Architecture

```mermaid
graph TD
    %% Define styles
    classDef serviceClass fill:#e3f2fd,stroke:#1976d2,stroke-width:3px,color:#0d47a1
    classDef endpointClass fill:#f3e5f5,stroke:#7b1fa2,stroke-width:2px,color:#4a148c
    classDef podClass fill:#e8f5e8,stroke:#388e3c,stroke-width:2px,color:#1b5e20
    classDef proxyClass fill:#fff3e0,stroke:#f57c00,stroke-width:2px,color:#e65100

    subgraph "🔌 Service"
        SVC[🌐 Service<br/>myapp-service:80]
        SELECTOR[🏷️ Label Selector<br/>app=myapp]
    end

    subgraph "📍 Endpoints"
        EP1[🎯 Endpoint 1<br/>10.0.1.1:8080]
        EP2[🎯 Endpoint 2<br/>10.0.2.3:8080]
        EP3[🎯 Endpoint 3<br/>10.0.1.5:8080]
    end

    subgraph "🐳 Pods"
        POD1[📦 Pod A<br/>app=myapp<br/>10.0.1.1:8080]
        POD2[📦 Pod B<br/>app=myapp<br/>10.0.2.3:8080]
        POD3[📦 Pod C<br/>app=myapp<br/>10.0.1.5:8080]
    end

    subgraph "🌉 Kube Proxy"
        IPTABLES[📋 iptables Rules<br/>Load Balancing]
        IPVS[⚖️ IPVS<br/>Advanced LB]
    end

    SVC --> SELECTOR
    SELECTOR --> EP1
    SELECTOR --> EP2
    SELECTOR --> EP3

    EP1 --> POD1
    EP2 --> POD2
    EP3 --> POD3

    SVC --> IPTABLES
    SVC --> IPVS

    %% Apply styles
    class SVC,SELECTOR serviceClass
    class EP1,EP2,EP3 endpointClass
    class POD1,POD2,POD3 podClass
    class IPTABLES,IPVS proxyClass
```

## Deployment Architecture

```mermaid
graph TD
    %% Define styles
    classDef deploymentClass fill:#e3f2fd,stroke:#1976d2,stroke-width:3px,color:#0d47a1
    classDef replicasetClass fill:#f3e5f5,stroke:#7b1fa2,stroke-width:2px,color:#4a148c
    classDef podClass fill:#e8f5e8,stroke:#388e3c,stroke-width:2px,color:#1b5e20
    classDef hpaClass fill:#fff3e0,stroke:#f57c00,stroke-width:2px,color:#e65100

    subgraph "🚀 Deployment"
        DEPLOY[📋 Deployment<br/>nginx-deployment]
        DESIRED[🎯 Desired State<br/>replicas: 3]
        STRATEGY[🔄 Strategy<br/>RollingUpdate]
    end

    subgraph "🔄 ReplicaSet"
        RS[🔄 ReplicaSet<br/>nginx-6b474476c4]
        REPLICAS[📊 Current Replicas<br/>3/3]
    end

    subgraph "🐳 Pods"
        POD1[📦 nginx-6b474476c4-abc12<br/>Running]
        POD2[📦 nginx-6b474476c4-def34<br/>Running]
        POD3[📦 nginx-6b474476c4-ghi56<br/>Running]
    end

    subgraph "📈 HPA"
        HPA[📈 HorizontalPodAutoscaler<br/>Target CPU: 70%]
        METRICS[📊 Metrics Server<br/>CPU/Memory metrics]
    end

    DEPLOY --> DESIRED
    DEPLOY --> STRATEGY
    STRATEGY --> RS
    RS --> REPLICAS
    REPLICAS --> POD1
    REPLICAS --> POD2
    REPLICAS --> POD3

    HPA --> METRICS
    METRICS --> RS

    %% Apply styles
    class DEPLOY,DESIRED,STRATEGY deploymentClass
    class RS,REPLICAS replicasetClass
    class POD1,POD2,POD3 podClass
    class HPA,METRICS hpaClass
```

## Networking Model

```mermaid
graph TD
    %% Define styles
    classDef ingressClass fill:#e3f2fd,stroke:#1976d2,stroke-width:3px,color:#0d47a1
    classDef serviceClass fill:#f3e5f5,stroke:#7b1fa2,stroke-width:3px,color:#4a148c
    classDef podClass fill:#e8f5e8,stroke:#388e3c,stroke-width:2px,color:#1b5e20
    classDef networkClass fill:#fff3e0,stroke:#f57c00,stroke-width:2px,color:#e65100

    subgraph "🌐 External Traffic"
        USER[👤 User]
        LB[⚖️ Load Balancer]
    end

    subgraph "🚪 Ingress"
        INGRESS[🚪 Ingress<br/>api.example.com]
        INGRESS_CONTROLLER[🎛️ Ingress Controller<br/>nginx/traefik]
    end

    subgraph "🔌 Services"
        SVC1[🔌 Service A<br/>ClusterIP: 10.0.0.1:80]
        SVC2[🔌 Service B<br/>ClusterIP: 10.0.0.2:80]
    end

    subgraph "🐳 Pods"
        POD1[📦 Pod A1<br/>10.244.1.1:8080]
        POD2[📦 Pod A2<br/>10.244.1.2:8080]
        POD3[📦 Pod B1<br/>10.244.2.1:8080]
    end

    subgraph "🌉 CNI Plugin"
        CNI[🌉 Container Network Interface<br/>Calico/Flannel/Weave]
        OVERLAY[🕸️ Overlay Network<br/>Pod-to-Pod communication]
    end

    USER --> LB
    LB --> INGRESS
    INGRESS --> INGRESS_CONTROLLER
    INGRESS_CONTROLLER --> SVC1
    INGRESS_CONTROLLER --> SVC2

    SVC1 --> POD1
    SVC1 --> POD2
    SVC2 --> POD3

    POD1 --> CNI
    POD2 --> CNI
    POD3 --> CNI
    CNI --> OVERLAY

    %% Apply styles
    class INGRESS,INGRESS_CONTROLLER ingressClass
    class SVC1,SVC2 serviceClass
    class POD1,POD2,POD3 podClass
    class CNI,OVERLAY networkClass
```

## Storage Architecture

```mermaid
graph TD
    %% Define styles
    classDef pvcClass fill:#e3f2fd,stroke:#1976d2,stroke-width:3px,color:#0d47a1
    classDef pvClass fill:#f3e5f5,stroke:#7b1fa2,stroke-width:2px,color:#4a148c
    classDef storageClass fill:#e8f5e8,stroke:#388e3c,stroke-width:2px,color:#1b5e20
    classDef provisionerClass fill:#fff3e0,stroke:#f57c00,stroke-width:2px,color:#e65100

    subgraph "📋 PVC"
        PVC[📋 PersistentVolumeClaim<br/>mysql-pvc<br/>size: 10Gi<br/>accessMode: ReadWriteOnce]
    end

    subgraph "💾 PV"
        PV[💾 PersistentVolume<br/>pv-12345<br/>capacity: 10Gi<br/>status: Bound]
    end

    subgraph "🏪 Storage Class"
        SC[🏪 StorageClass<br/>fast-ssd<br/>provisioner: kubernetes.io/aws-ebs<br/>reclaimPolicy: Delete]
    end

    subgraph "🔧 Provisioner"
        PROVISIONER[🔧 Dynamic Provisioner<br/>AWS EBS/GCE PD/Azure Disk]
        EXTERNAL[🔧 External Provisioner<br/>NFS/GlusterFS]
    end

    subgraph "💽 Physical Storage"
        EBS[💽 AWS EBS Volume]
        GCE[💽 GCE Persistent Disk]
        NFS[💽 NFS Share]
    end

    PVC --> PV
    PV --> SC
    SC --> PROVISIONER
    PROVISIONER --> EBS
    PROVISIONER --> GCE
    EXTERNAL --> NFS

    %% Apply styles
    class PVC pvcClass
    class PV pvClass
    class SC storageClass
    class PROVISIONER,EXTERNAL provisionerClass
```

## RBAC Architecture

```mermaid
graph TD
    %% Define styles
    classDef userClass fill:#e3f2fd,stroke:#1976d2,stroke-width:3px,color:#0d47a1
    classDef roleClass fill:#f3e5f5,stroke:#7b1fa2,stroke-width:2px,color:#4a148c
    classDef bindingClass fill:#e8f5e8,stroke:#388e3c,stroke-width:2px,color:#1b5e20
    classDef resourceClass fill:#fff3e0,stroke:#f57c00,stroke-width:2px,color:#e65100

    subgraph "👤 Subjects"
        USER[👨‍💻 User<br/>alice@example.com]
        GROUP[👥 Group<br/>developers]
        SA[🤖 ServiceAccount<br/>default]
    end

    subgraph "🔒 Roles"
        ROLE[🎭 Role<br/>pod-reader<br/>- get, list pods<br/>- namespace: default]
        CLUSTER_ROLE[🌍 ClusterRole<br/>cluster-admin<br/>- * all resources<br/>- cluster-wide]
    end

    subgraph "🔗 Bindings"
        ROLE_BINDING[🔗 RoleBinding<br/>alice-pod-reader<br/>role: pod-reader<br/>subject: alice]
        CLUSTER_ROLE_BINDING[🔗 ClusterRoleBinding<br/>admin-binding<br/>role: cluster-admin<br/>subject: alice]
    end

    subgraph "📦 Resources"
        PODS[📦 Pods<br/>get, list, watch]
        SERVICES[🔌 Services<br/>get, create, update]
        DEPLOYMENTS[🚀 Deployments<br/>* all operations]
    end

    USER --> ROLE_BINDING
    GROUP --> CLUSTER_ROLE_BINDING
    SA --> ROLE_BINDING

    ROLE_BINDING --> ROLE
    CLUSTER_ROLE_BINDING --> CLUSTER_ROLE

    ROLE --> PODS
    ROLE --> SERVICES
    CLUSTER_ROLE --> DEPLOYMENTS
    CLUSTER_ROLE --> PODS
    CLUSTER_ROLE --> SERVICES

    %% Apply styles
    class USER,GROUP,SA userClass
    class ROLE,CLUSTER_ROLE roleClass
    class ROLE_BINDING,CLUSTER_ROLE_BINDING bindingClass
    class PODS,SERVICES,DEPLOYMENTS resourceClass
```

## Application Deployment Strategies

```mermaid
flowchart TD
    %% Define styles
    classDef strategyClass fill:#e3f2fd,stroke:#1976d2,stroke-width:3px,color:#0d47a1
    classDef deploymentClass fill:#f3e5f5,stroke:#7b1fa2,stroke-width:2px,color:#4a148c
    classDef trafficClass fill:#e8f5e8,stroke:#388e3c,stroke-width:2px,color:#1b5e20

    subgraph "🔄 Rolling Update"
        OLD_DEPLOY[🚀 v1 Deployment<br/>3 replicas]
        NEW_DEPLOY[🚀 v2 Deployment<br/>Gradual rollout]
        TRAFFIC[🚦 Traffic Split<br/>75% v1, 25% v2]
    end

    subgraph "🔵 Blue-Green"
        BLUE[🔵 Blue Environment<br/>v1 - stable]
        GREEN[🟢 Green Environment<br/>v2 - new]
        SWITCH[🔀 Traffic Switch<br/>Instant cutover]
    end

    subgraph "🐦 Canary"
        STABLE[🚀 Stable Release<br/>95% traffic]
        CANARY[🐦 Canary Release<br/>5% traffic]
        MONITOR[📊 Monitor Metrics<br/>Error rates, latency]
    end

    OLD_DEPLOY --> TRAFFIC
    TRAFFIC --> NEW_DEPLOY

    BLUE --> SWITCH
    SWITCH --> GREEN

    STABLE --> MONITOR
    MONITOR --> CANARY

    %% Apply styles
    class OLD_DEPLOY,NEW_DEPLOY,TRAFFIC strategyClass
    class BLUE,GREEN,SWITCH deploymentClass
    class STABLE,CANARY,MONITOR trafficClass
```

## Service Mesh Integration

```mermaid
graph TD
    %% Define styles
    classDef istioClass fill:#e3f2fd,stroke:#1976d2,stroke-width:3px,color:#0d47a1
    classDef envoyClass fill:#f3e5f5,stroke:#7b1fa2,stroke-width:2px,color:#4a148c
    classDef serviceClass fill:#e8f5e8,stroke:#388e3c,stroke-width:2px,color:#1b5e20
    classDef controlClass fill:#fff3e0,stroke:#f57c00,stroke-width:2px,color:#e65100

    subgraph "🎛️ Istio Control Plane"
        PILOT[🎮 Pilot<br/>Service Discovery<br/>Traffic Management]
        CITadel[🔐 Citadel<br/>Certificate Authority<br/>Security]
        GALLEY[📋 Galley<br/>Configuration<br/>Validation]
    end

    subgraph "🌐 Data Plane"
        ENVOY1[🌐 Envoy Proxy<br/>Sidecar - Service A]
        ENVOY2[🌐 Envoy Proxy<br/>Sidecar - Service B]
        ENVOY3[🌐 Envoy Proxy<br/>Sidecar - Service C]
    end

    subgraph "🐳 Application Services"
        SVC_A[🔌 Service A<br/>v1.0 + v2.0]
        SVC_B[🔌 Service B<br/>v1.0]
        SVC_C[🔌 Service C<br/>v1.0]
    end

    subgraph "📊 Observability"
        JAEGER[🔍 Jaeger<br/>Distributed Tracing]
        PROMETHEUS[📈 Prometheus<br/>Metrics]
        KIALI[🗺️ Kiali<br/>Service Mesh Dashboard]
    end

    PILOT --> ENVOY1
    PILOT --> ENVOY2
    PILOT --> ENVOY3

    CITadel --> ENVOY1
    CITadel --> ENVOY2
    CITadel --> ENVOY3

    GALLEY --> PILOT

    ENVOY1 --> SVC_A
    ENVOY2 --> SVC_B
    ENVOY3 --> SVC_C

    ENVOY1 --> JAEGER
    ENVOY2 --> PROMETHEUS
    ENVOY3 --> KIALI

    %% Apply styles
    class PILOT,CITadel,GALLEY istioClass
    class ENVOY1,ENVOY2,ENVOY3 envoyClass
    class SVC_A,SVC_B,SVC_C serviceClass
    class JAEGER,PROMETHEUS,KIALI controlClass
```

## Multi-Cluster Architecture

```mermaid
graph TD
    %% Define styles
    classDef clusterClass fill:#e3f2fd,stroke:#1976d2,stroke-width:3px,color:#0d47a1
    classDef federationClass fill:#f3e5f5,stroke:#7b1fa2,stroke-width:3px,color:#4a148c
    classDef serviceClass fill:#e8f5e8,stroke:#388e3c,stroke-width:2px,color:#1b5e20

    subgraph "🌍 Federation Control Plane"
        FED_API[🔌 Federation API Server]
        FED_CONTROLLER[⚙️ Federation Controllers]
        FED_DNS[🌐 Federation DNS]
    end

    subgraph "☁️ Cluster 1 (AWS)"
        K8S1[☸️ Kubernetes Cluster 1]
        SVC1_A[🔌 Service A]
        SVC1_B[🔌 Service B]
    end

    subgraph "☁️ Cluster 2 (GCP)"
        K8S2[☸️ Kubernetes Cluster 2]
        SVC2_A[🔌 Service A]
        SVC2_B[🔌 Service B]
    end

    subgraph "☁️ Cluster 3 (Azure)"
        K8S3[☸️ Kubernetes Cluster 3]
        SVC3_C[🔌 Service C]
    end

    FED_API --> FED_CONTROLLER
    FED_CONTROLLER --> FED_DNS

    FED_CONTROLLER --> K8S1
    FED_CONTROLLER --> K8S2
    FED_CONTROLLER --> K8S3

    K8S1 --> SVC1_A
    K8S1 --> SVC1_B

    K8S2 --> SVC2_A
    K8S2 --> SVC2_B

    K8S3 --> SVC3_C

    %% Apply styles
    class FED_API,FED_CONTROLLER,FED_DNS federationClass
    class K8S1,K8S2,K8S3 clusterClass
    class SVC1_A,SVC1_B,SVC2_A,SVC2_B,SVC3_C serviceClass
```

## CI/CD Pipeline with Kubernetes

```mermaid
flowchart TD
    A[👨‍💻 Developer Push] --> B[🔄 CI Pipeline]
    B --> C[🧪 Run Tests]
    C --> D[🏗️ Build Container Image]
    D --> E[📤 Push to Registry]
    E --> F[🚀 Deploy to Kubernetes]

    F --> G[📋 Apply Manifests]
    G --> H[🔍 Health Checks]
    H --> I[🧪 Integration Tests]
    I --> J{Tests Pass?}

    J -->|No| K[❌ Rollback]
    J -->|Yes| L[✅ Promote to Production]

    L --> M[📊 Monitor & Alert]
    M --> N[🔄 Feedback Loop]
    N --> A

    K --> O[🐛 Debug Issues]
    O --> P[🔧 Fix & Redeploy]
    P --> F
```

## Resource Management

```mermaid
graph TD
    %% Define styles
    classDef requestClass fill:#e3f2fd,stroke:#1976d2,stroke-width:2px,color:#0d47a1
    classDef limitClass fill:#f3e5f5,stroke:#7b1fa2,stroke-width:2px,color:#4a148c
    classDef qosClass fill:#e8f5e8,stroke:#388e3c,stroke-width:2px,color:#1b5e20
    classDef evictionClass fill:#fff3e0,stroke:#f57c00,stroke-width:2px,color:#e65100

    subgraph "📊 Pod Resources"
        REQUESTS[📈 Requests<br/>Guaranteed resources<br/>cpu: 100m<br/>memory: 128Mi]
        LIMITS[📊 Limits<br/>Maximum resources<br/>cpu: 500m<br/>memory: 512Mi]
    end

    subgraph "🏆 QoS Classes"
        GUARANTEED[✅ Guaranteed<br/>Requests = Limits<br/>Highest priority]
        BURSTABLE[⚡ Burstable<br/>Requests < Limits<br/>Medium priority]
        BESTEFFORT[🎲 BestEffort<br/>No requests/limits<br/>Lowest priority]
    end

    subgraph "🚨 Eviction Manager"
        HARD_EVICT[⚠️ Hard Eviction<br/>Node pressure<br/>memory.available < 100Mi]
        SOFT_EVICT[🔔 Soft Eviction<br/>Graceful eviction<br/>memory.available < 200Mi]
    end

    REQUESTS --> GUARANTEED
    REQUESTS --> BURSTABLE
    LIMITS --> BURSTABLE

    GUARANTEED --> HARD_EVICT
    BURSTABLE --> SOFT_EVICT
    BESTEFFORT --> SOFT_EVICT

    %% Apply styles
    class REQUESTS requestClass
    class LIMITS limitClass
    class GUARANTEED,BURSTABLE,BESTEFFORT qosClass
    class HARD_EVICT,SOFT_EVICT evictionClass
```

## Security Architecture

```mermaid
graph TD
    %% Define styles
    classDef authClass fill:#e3f2fd,stroke:#1976d2,stroke-width:3px,color:#0d47a1
    classDef rbacClass fill:#f3e5f5,stroke:#7b1fa2,stroke-width:2px,color:#4a148c
    classDef networkClass fill:#e8f5e8,stroke:#388e3c,stroke-width:2px,color:#1b5e20
    classDef podClass fill:#fff3e0,stroke:#f57c00,stroke-width:2px,color:#e65100

    subgraph "🔐 Authentication"
        CERTS[📜 Client Certificates]
        TOKENS[🎫 Bearer Tokens]
        OIDC[🔗 OIDC]
        WEBHOOK[🪝 Webhook Auth]
    end

    subgraph "🛡️ Authorization"
        RBAC[🎭 RBAC<br/>Role-Based Access Control]
        ABAC[📋 ABAC<br/>Attribute-Based Access Control]
        NODE_AUTH[💻 Node Authorization]
    end

    subgraph "🌐 Network Security"
        NETWORK_POLICIES[🚧 Network Policies<br/>Pod-to-pod traffic control]
        SERVICE_MESH[🕸️ Service Mesh<br/>mTLS, traffic policies]
    end

    subgraph "🐳 Pod Security"
        SECURITY_CONTEXT[🔒 Security Context<br/>User, capabilities, SELinux]
        POD_SECURITY[🛡️ Pod Security Standards<br/>Privileged, Baseline, Restricted]
        PSP[📜 Pod Security Policies<br/>Deprecated but still used]
    end

    CERTS --> RBAC
    TOKENS --> RBAC
    OIDC --> RBAC
    WEBHOOK --> RBAC

    RBAC --> NETWORK_POLICIES
    RBAC --> SERVICE_MESH

    NETWORK_POLICIES --> SECURITY_CONTEXT
    SERVICE_MESH --> POD_SECURITY
    POD_SECURITY --> PSP

    %% Apply styles
    class CERTS,TOKENS,OIDC,WEBHOOK authClass
    class RBAC,ABAC,NODE_AUTH rbacClass
    class NETWORK_POLICIES,SERVICE_MESH networkClass
    class SECURITY_CONTEXT,POD_SECURITY,PSP podClass
```

## Summary

Kubernetes' visual architecture reveals a sophisticated, layered system designed for scalability, reliability, and extensibility. The separation of control plane and data plane, combined with declarative configuration and extensive ecosystem integrations, makes Kubernetes the standard for modern application orchestration.

Key visual insights:
- **Hierarchical control**: API Server as central hub
- **Distributed storage**: etcd for cluster state
- **Pod-centric design**: Atomic deployment units
- **Service abstraction**: Stable networking endpoints
- **Extensible architecture**: CRDs and operators
- **Security layers**: Multi-level protection
- **Observability integration**: Comprehensive monitoring stack

Understanding these visual relationships is crucial for effective Kubernetes operations and troubleshooting.
