# Virtual Private Cloud (VPC) - What is it?

## Overview

Virtual Private Cloud (VPC) is Google Cloud's networking service that provides a private, isolated section of Google Cloud Platform where you can launch GCP resources in a virtual network that you define. VPC provides complete control over your virtual networking environment, including IP address ranges, subnets, routing tables, and network gateways.

## Core Concepts

### VPC Network
A VPC network is a virtual version of a physical network, implemented inside Google's production network. Each VPC network consists of:
- **IP address ranges** (RFC 1918 private addresses)
- **Subnets** (regional IP address ranges)
- **Routes** (traffic forwarding rules)
- **Firewall rules** (traffic filtering)
- **VPN gateways** (hybrid connectivity)

### Subnets
Subnets are regional resources that divide the VPC network into smaller, manageable sections:
- **Regional scope**: Subnets exist in specific regions
- **IP address ranges**: CIDR blocks within the VPC range
- **Purpose**: Isolate resources and control traffic flow
- **Auto vs Custom**: Auto-subnets vs user-defined subnets

### Routes
Routes determine how traffic is directed within the VPC and to external destinations:
- **System routes**: Automatically created for subnet communication
- **Custom routes**: User-defined routes for specific destinations
- **Dynamic routes**: Learned through Cloud Router (BGP)
- **Route priority**: Higher priority routes take precedence

### Firewall Rules
Firewall rules control inbound and outbound traffic to VM instances:
- **Network-level**: Applied at the network interface level
- **Stateful**: Track connection state for return traffic
- **Priority-based**: Lower numbers = higher priority
- **Tags/Targets**: Apply rules to specific instances

## Architecture Types

### Auto Mode VPC
- **Automatic subnets**: One subnet per region (auto-created)
- **Default network**: Pre-configured auto mode VPC
- **Simplicity**: Easy to get started, less configuration
- **Limitations**: Fixed subnet ranges, less control

### Custom Mode VPC
- **Manual subnets**: User-defined subnets and IP ranges
- **Full control**: Complete control over IP addressing
- **Flexibility**: Custom subnet sizes and placements
- **Complexity**: More configuration required

## Key Features

### Global vs Regional Resources
- **VPC networks**: Global resources spanning all regions
- **Subnets**: Regional resources within specific regions
- **Firewall rules**: Can be global or regional
- **Routes**: Can be global or regional

### IP Addressing
- **Internal IP**: Private RFC 1918 addresses for VPC communication
- **External IP**: Public IP addresses for internet communication
- **Alias IP ranges**: Secondary IP ranges for pods/services (GKE)
- **Reserved IP addresses**: Static internal/external IPs

### Connectivity Options
- **Internet Gateway**: Default route for internet access
- **Cloud VPN**: Secure connection to on-premises networks
- **Cloud Interconnect**: Direct physical connections (Dedicated/Partner)
- **VPC Peering**: Connect VPC networks within GCP
- **Shared VPC**: Share a VPC network across projects

## Security & Isolation

### Network Isolation
- **Complete isolation**: VPC networks are logically isolated
- **No overlapping IPs**: Each VPC has unique IP ranges
- **Security boundaries**: Firewall rules control all traffic
- **Service isolation**: Separate networks for different environments

### Firewall Architecture
- **Implied deny**: All traffic denied by default
- **Explicit allow**: Rules required to permit traffic
- **Directional control**: Separate ingress/egress rules
- **Hierarchical application**: VPC → subnet → instance level

### Private Google Access
- **Private access**: Connect to Google APIs without external IPs
- **DNS resolution**: googleapis.com resolves to private IPs
- **Security**: Traffic stays within Google's network
- **Cost savings**: No external IP charges for API calls

## Advanced Networking

### VPC Peering
- **Network connectivity**: Connect VPC networks without VPN
- **Latency**: Traffic stays on Google's network
- **Transitivity**: Non-transitive (direct connections only)
- **Security**: Firewall rules still apply

### Shared VPC
- **Host project**: Contains the Shared VPC network
- **Service projects**: Attach to host project networks
- **Centralized control**: Network admin in host project
- **Resource sharing**: Subnets shared across projects

### Cloud NAT
- **Outbound internet**: NAT gateway for private instances
- **No external IPs**: Instances remain private
- **Security**: Inbound traffic blocked by default
- **Logging**: NAT connection logs available

## Hybrid Connectivity

### Cloud VPN
- **IPsec VPN**: Secure encrypted tunnels
- **High availability**: 99.9% SLA with redundant tunnels
- **Dynamic routing**: BGP for route exchange
- **Site-to-site**: Connect entire networks

### Cloud Interconnect
- **Dedicated Interconnect**: Direct physical connection (10Gbps-100Gbps)
- **Partner Interconnect**: Through service provider (50Mbps-50Gbps)
- **Low latency**: Traffic bypasses public internet
- **Cost effective**: For high-volume data transfer

## Network Monitoring & Management

### VPC Flow Logs
- **Traffic visibility**: Log all network traffic
- **Metadata**: Source/destination IPs, ports, protocols
- **Sampling**: Configurable sampling rate
- **Analysis**: Export to BigQuery/Cloud Logging

### Network Intelligence
- **Connectivity Tests**: Verify network reachability
- **Performance Dashboard**: Monitor network performance
- **Firewall Insights**: Analyze firewall rule usage
- **Network Analyzer**: Troubleshoot connectivity issues

## Best Practices

### Network Design
- **IP planning**: Plan IP ranges to avoid conflicts
- **Regional distribution**: Place resources close to users
- **Security zones**: Separate environments with different VPCs
- **Scalability**: Design for growth and expansion

### Security Best Practices
- **Least privilege**: Minimal required firewall rules
- **Network segmentation**: Use subnets to isolate workloads
- **Private access**: Use Private Google Access when possible
- **Regular audits**: Review firewall rules and routes

### Cost Optimization
- **Resource cleanup**: Remove unused VPC resources
- **Efficient IP usage**: Right-size subnets and IP ranges
- **Traffic optimization**: Use VPC peering instead of VPN where possible
- **Monitoring**: Track network usage and costs

## Common Use Cases

### Web Application Architecture
- **Public subnets**: Load balancers and web servers
- **Private subnets**: Application servers and databases
- **NAT gateways**: Outbound internet access for updates
- **Security groups**: Fine-grained traffic control

### Multi-Environment Setup
- **Development VPC**: Isolated development environment
- **Staging VPC**: Pre-production testing
- **Production VPC**: Live application environment
- **Shared services**: Common services across environments

### Hybrid Cloud Architecture
- **On-premises extension**: Extend data center to cloud
- **Cloud migration**: Gradual migration with VPN/Interconnect
- **Disaster recovery**: Backup site in cloud
- **Bursting**: Scale to cloud during peak loads

## Integration with GCP Services

### Compute Engine
- **Network interfaces**: Multiple network interfaces per VM
- **VPC-native**: Direct attachment to VPC subnets
- **Internal DNS**: Automatic hostname resolution
- **Metadata server**: Instance metadata via 169.254.169.254

### GKE (Google Kubernetes Engine)
- **VPC-native clusters**: Pods get VPC IP addresses
- **Alias IP ranges**: Efficient IP allocation for pods/services
- **Network policies**: Kubernetes network segmentation
- **Load balancing**: Integration with VPC load balancers

### Cloud SQL & Spanner
- **Private IP**: Connect via private VPC IP addresses
- **VPC peering**: Secure connection without public IPs
- **Private services access**: Managed peering for Google services
- **Serverless VPC access**: Connect from Cloud Functions

VPC forms the foundation of network architecture in Google Cloud, providing the networking layer that connects all GCP services and enables secure, scalable, and high-performance applications.
