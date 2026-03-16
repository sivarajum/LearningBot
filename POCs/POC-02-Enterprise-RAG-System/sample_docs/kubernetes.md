# Kubernetes (K8s)

## Overview

Kubernetes is an open-source container orchestration platform originally developed by Google. It automates the deployment, scaling, and management of containerized applications across clusters of machines.

## Core Concepts

### Pods
A Pod is the smallest deployable unit in Kubernetes. It represents a single instance of a running process and can contain one or more tightly coupled containers that share networking and storage. Pods are ephemeral by design.

### Deployments
Deployments manage the desired state for Pods. You declare how many replicas of a Pod should run, and the Deployment controller ensures that state is maintained. Deployments support rolling updates and rollbacks.

### Services
Services provide stable networking for Pods. Since Pods are ephemeral and get new IP addresses when restarted, a Service provides a consistent DNS name and load-balances traffic across healthy Pods. Types include ClusterIP, NodePort, and LoadBalancer.

### ConfigMaps and Secrets
ConfigMaps store non-sensitive configuration data as key-value pairs. Secrets store sensitive data like API keys and passwords in base64-encoded format. Both can be mounted as environment variables or files inside Pods.

## Scaling Strategies

- **Horizontal Pod Autoscaler (HPA)**: Automatically adjusts the number of Pod replicas based on CPU/memory utilization or custom metrics.
- **Vertical Pod Autoscaler (VPA)**: Adjusts the CPU and memory requests for containers in a Pod.
- **Cluster Autoscaler**: Adds or removes nodes from the cluster based on pending Pods that cannot be scheduled.

## Common Tools

- **kubectl**: The CLI tool for interacting with Kubernetes clusters.
- **Helm**: A package manager for Kubernetes that uses charts to define, install, and upgrade applications.
- **Kustomize**: A configuration management tool built into kubectl for customizing Kubernetes resources.

## Production Best Practices

Use namespaces for resource isolation, set resource requests and limits on all containers, implement health checks with liveness and readiness probes, and use network policies to control Pod-to-Pod communication.
