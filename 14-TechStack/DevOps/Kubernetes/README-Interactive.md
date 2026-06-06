# Kubernetes Interactive Cluster

This interactive visualization brings Kubernetes orchestration to life with real-time pod deployments, service communications, and cluster management simulations.

## Features

### 🚢 Live Cluster Simulation
- **Real-time Pod Deployment**: Watch pods being scheduled across worker nodes
- **Service Communication**: See data flowing between services and pods
- **Network Visualization**: Observe connection lines and data packets
- **Resource Monitoring**: Track CPU, memory, and pod counts

### 🎮 Interactive Controls
- **Deploy Pods**: Manually deploy new pods to random nodes
- **Scale Deployments**: Increase replica counts with visual feedback
- **Create Services**: Add new services with network endpoints
- **Traffic Simulation**: Generate realistic network traffic patterns
- **Reset Cluster**: Clean restart of the entire simulation

### 📊 Live Metrics Dashboard
- **Cluster Health**: Overall cluster status monitoring
- **Pod Counts**: Total pods across all nodes
- **Service Inventory**: Active services and endpoints
- **Resource Usage**: CPU and memory utilization
- **Deployment Tracking**: Active deployment counts

## How to Use

1. **Open the Visualization**: Open `interactive-cluster.html` in any modern web browser
2. **Deploy Components**: Use control buttons to deploy pods and create services
3. **Observe Orchestration**: Watch the scheduler place pods on nodes
4. **Simulate Traffic**: Generate network traffic to see data flow
5. **Monitor Resources**: Track cluster metrics in real-time
6. **Scale Applications**: Increase pod counts and observe load balancing

## Keyboard Shortcuts

- **D**: Deploy a new pod
- **S**: Scale up deployment
- **C**: Create a new service
- **T**: Toggle traffic simulation
- **R**: Reset cluster

## Kubernetes Components Visualized

### Control Plane
- **API Server**: Central management endpoint
- **Controller Manager**: Maintains desired cluster state
- **Scheduler**: Assigns pods to nodes

### Worker Nodes
- **Kubelet**: Node agent managing pods
- **Container Runtime**: Executes containers
- **Kube Proxy**: Network proxy for services

### Core Objects
- **Pods**: Smallest deployable units
- **Services**: Network abstractions for pod access
- **Deployments**: Manages replica sets and updates

### Storage
- **etcd**: Distributed key-value store for cluster state

## Educational Value

This interactive visualization helps users:
- **Understand Orchestration**: See how Kubernetes manages applications
- **Learn Scheduling**: Observe pod placement decisions
- **Visualize Networking**: Watch service discovery and load balancing
- **Experience Scaling**: See horizontal pod autoscaling in action
- **Monitor Health**: Track cluster and application metrics

## Technical Implementation

- **Pure HTML/CSS/JavaScript**: No external dependencies
- **Real-time Animations**: Smooth 60fps animations using CSS transforms
- **Dynamic Element Creation**: Pods and services created programmatically
- **Event-driven Architecture**: Interactive controls with immediate feedback
- **Responsive Design**: Works on desktop and mobile devices

## Browser Compatibility

- Chrome 60+, Firefox 60+, Safari 12+, Edge 79+
- Modern browsers with CSS Grid, Flexbox, and ES6+ JavaScript support
- Mobile browsers supported with touch interactions

## Integration with Documentation

This interactive visualization complements the existing Kubernetes documentation by providing:
- Dynamic alternatives to static Mermaid diagrams
- Hands-on experience with cluster operations
- Visual demonstrations of complex orchestration concepts
- Interactive learning for deployment and scaling scenarios

## Simulation Features

### Realistic Behaviors
- **Pod Scheduling**: Intelligent placement across nodes
- **Resource Constraints**: CPU and memory limitations
- **Network Latency**: Realistic data transmission delays
- **Failure Simulation**: Node and pod failure scenarios (future)

### Interactive Scenarios
- **Load Testing**: Traffic simulation with performance metrics
- **Scaling Events**: Horizontal and vertical scaling demonstrations
- **Service Discovery**: Dynamic service registration and lookup
- **Health Checks**: Pod and service health monitoring

## Future Enhancements

Potential improvements could include:
- **Multi-cluster Visualization**: Federation and cross-cluster communication
- **Custom Resource Definitions**: CRD and operator pattern demonstrations
- **Persistent Volumes**: Storage class and PVC lifecycle visualization
- **Ingress Controllers**: External traffic routing and load balancing
- **RBAC Visualization**: Role-based access control interactions
- **Helm Chart Deployment**: Package management and templating
- **CI/CD Integration**: Automated deployment pipelines
