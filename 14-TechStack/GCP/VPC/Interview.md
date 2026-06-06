# VPC - Interview Questions & Scenarios

## Core Concepts

### Q1: Explain the difference between auto mode and custom mode VPC networks. When would you choose each?

**Answer:**
**Auto Mode VPC:**
- **Automatic subnets**: One subnet per region, auto-created with fixed /20 CIDR blocks
- **Default network**: Pre-configured auto mode VPC in every project
- **Simplicity**: Minimal configuration, good for getting started quickly
- **Limitations**: Less control over IP ranges, all regions get subnets even if unused

**Custom Mode VPC:**
- **Manual subnets**: User defines subnet names, regions, and IP ranges
- **Full control**: Complete control over IP addressing and network design
- **Flexibility**: Only create subnets where needed, custom CIDR blocks
- **Complexity**: More planning and configuration required

**Choose auto mode when:**
- Learning GCP or proof-of-concepts
- Simple architectures with basic networking needs
- Quick deployment without complex network planning

**Choose custom mode when:**
- Production environments requiring specific IP ranges
- Complex architectures with multiple environments
- Need for network isolation and security segmentation
- Compliance requirements for IP address management

---

### Q2: How do routes work in GCP VPC? Explain the route priority and matching logic.

**Answer:**
Routes in GCP determine how packets are forwarded within VPC networks and to external destinations:

**Route Components:**
- **Destination**: IP range (CIDR) the route applies to
- **Next hop**: Where to send traffic (gateway, instance, VPN tunnel, etc.)
- **Priority**: Number from 0-65535 (lower = higher priority)
- **Tags**: Network tags for route application

**Route Types:**
1. **System routes** (Priority 1000):
   - Local routes: VPC CIDR → local VPC
   - Default internet: 0.0.0.0/0 → default internet gateway

2. **Custom routes** (Priority 100-999):
   - Static routes: User-defined routes
   - Dynamic routes: Learned via Cloud Router (BGP)

3. **Peering routes** (Priority 1000):
   - Imported from peered VPC networks

**Route Matching Logic:**
1. **Most specific prefix wins**: /32 beats /24 beats /16
2. **Priority breaks ties**: Lower priority number wins
3. **Route type**: System > Custom > Peering (same priority)

**Example:**
```
Destination: 10.0.0.0/16, Next hop: local, Priority: 0 (system)
Destination: 0.0.0.0/0, Next hop: internet, Priority: 1000 (system)
Destination: 192.168.1.0/24, Next hop: VPN, Priority: 100 (custom)
```

---

### Q3: Describe VPC firewall rules and their evaluation order. How do implied rules work?

**Answer:**
VPC firewall rules control traffic flow at the network level:

**Rule Components:**
- **Direction**: Ingress (inbound) or Egress (outbound)
- **Priority**: 0-65535 (lower number = higher priority)
- **Action**: Allow or Deny
- **Targets**: Network tags, service accounts, or "all instances"
- **Source/Destination**: IP ranges, network tags, or service accounts
- **Protocols/Ports**: TCP/UDP ports or "all protocols"

**Evaluation Order:**
1. **Priority order**: Rules evaluated from lowest to highest priority number
2. **First match wins**: Processing stops at first matching rule
3. **Implied deny**: If no rule matches, traffic is denied by default

**Implied Rules:**
- **Implied allow egress**: Allows all outbound traffic (lowest priority)
- **Implied deny ingress**: Denies all inbound traffic (lowest priority)
- **Cannot be deleted**: Always present as safety mechanism

**Example Rule:**
```
Name: allow-ssh
Direction: Ingress
Priority: 1000
Action: Allow
Targets: ssh-access
Source: 203.0.113.0/24
Protocol: tcp:22
```

---

## Network Design Scenarios

### Q4: Design a VPC architecture for a 3-tier web application (web, application, database) with high availability across multiple regions.

**Answer:**
**Architecture Design:**

**Global VPC Network:**
- Custom mode VPC: `production-vpc` (10.0.0.0/16)

**Regional Subnets (us-central1):**
- `web-subnet`: 10.0.1.0/24 (public)
- `app-subnet`: 10.0.2.0/24 (private)
- `db-subnet`: 10.0.3.0/24 (private)

**Regional Subnets (europe-west1):**
- `web-subnet-eu`: 10.1.1.0/24 (public)
- `app-subnet-eu`: 10.1.2.0/24 (private)
- `db-subnet-eu`: 10.1.3.0/24 (private)

**Security Design:**
```bash
# Firewall rules
gcloud compute firewall-rules create allow-web \
  --direction=INGRESS --priority=1000 --network=production-vpc \
  --action=ALLOW --rules=tcp:80,tcp:443 --source-ranges=0.0.0.0/0 \
  --target-tags=web-tier

gcloud compute firewall-rules create allow-app \
  --direction=INGRESS --priority=1000 --network=production-vpc \
  --action=ALLOW --rules=tcp:8080 --source-tags=web-tier \
  --target-tags=app-tier

gcloud compute firewall-rules create allow-db \
  --direction=INGRESS --priority=1000 --network=production-vpc \
  --action=ALLOW --rules=tcp:5432 --source-tags=app-tier \
  --target-tags=db-tier
```

**High Availability:**
- Load balancers span both regions
- Instance groups in multiple zones per region
- Cloud SQL with cross-region replicas
- Global DNS with geo-routing

---

### Q5: How would you implement network isolation for development, staging, and production environments?

**Answer:**
**Option 1: Separate VPCs (Recommended for production):**

**Three VPC Networks:**
- `dev-vpc`: 10.10.0.0/16
- `staging-vpc`: 10.20.0.0/16
- `prod-vpc`: 10.30.0.0/16

**VPC Peering for cross-environment access:**
```bash
# Peer dev to shared services
gcloud compute networks peerings create dev-to-shared \
  --network=dev-vpc --peer-network=shared-vpc

# Peer staging to shared (controlled access)
gcloud compute networks peerings create staging-to-shared \
  --network=staging-vpc --peer-network=shared-vpc

# No direct peering between dev/staging/prod
```

**Option 2: Shared VPC with service projects:**
- Host project: `network-host`
- Service projects: `dev-team`, `staging-team`, `prod-team`
- Shared subnets with IAM permissions

**Security Considerations:**
- Different firewall rules per environment
- Network tags for environment identification
- VPC Service Controls for data exfiltration prevention
- Cloud NAT for outbound internet access in private subnets

---

### Q6: Explain how to set up hybrid connectivity between GCP VPC and on-premises network using Cloud VPN.

**Answer:**
**Cloud VPN Setup:**

**1. Create VPC network and subnets:**
```bash
gcloud compute networks create hybrid-vpc --subnet-mode=custom
gcloud compute networks subnets create hybrid-subnet \
  --network=hybrid-vpc --region=us-central1 --range=10.0.0.0/24
```

**2. Reserve external IP for VPN gateway:**
```bash
gcloud compute addresses create vpn-external-ip \
  --region=us-central1 --ip-version=IPV4
```

**3. Create Cloud VPN gateway:**
```bash
gcloud compute vpn-gateways create cloud-vpn-gateway \
  --network=hybrid-vpc --region=us-central1
```

**4. Create Cloud Router for BGP:**
```bash
gcloud compute routers create cloud-router \
  --network=hybrid-vpc --region=us-central1 \
  --asn=65001 --advertise-mode=CUSTOM
```

**5. Create VPN tunnels:**
```bash
gcloud compute vpn-tunnels create tunnel-1 \
  --peer-address=203.0.113.1 --shared-secret=secret123 \
  --ike-version=2 --local-traffic-selector=0.0.0.0/0 \
  --remote-traffic-selector=0.0.0.0/0 \
  --router=cloud-router --vpn-gateway=cloud-vpn-gateway
```

**6. Configure BGP session:**
```bash
gcloud compute routers add-interface cloud-router \
  --interface-name=tunnel-1 --vpn-tunnel=tunnel-1

gcloud compute routers add-bgp-peer cloud-router \
  --peer-name=on-prem-router --interface=tunnel-1 \
  --peer-ip-address=169.254.1.2 --peer-asn=65002 \
  --advertised-route-priority=100
```

**High Availability:**
- Create second VPN tunnel with different external IP
- Use HA VPN for 99.9% SLA
- Configure redundant tunnels on on-premises side

---

## Troubleshooting Scenarios

### Q7: A VM instance cannot reach the internet. What steps would you take to troubleshoot?

**Answer:**
**Systematic troubleshooting approach:**

**1. Check VM configuration:**
```bash
# Check if VM has external IP
gcloud compute instances describe vm-instance --zone=us-central1-a

# Check network interface
gcloud compute instances get-serial-port-output vm-instance --zone=us-central1-a
```

**2. Verify subnet and route configuration:**
```bash
# Check subnet details
gcloud compute networks subnets describe subnet-name --region=us-central1

# List routes
gcloud compute routes list --filter="network=VPC_NAME"
```

**3. Check firewall rules:**
```bash
# List egress firewall rules
gcloud compute firewall-rules list --filter="direction=EGRESS AND network=VPC_NAME"

# Check for blocking rules
gcloud compute firewall-rules list --filter="action=DENY"
```

**4. Test connectivity from VM:**
```bash
# Ping external host
ping 8.8.8.8

# Check default route
ip route show

# Test DNS resolution
nslookup google.com
```

**5. Check Cloud NAT (if applicable):**
```bash
# List NAT gateways
gcloud compute routers nats list --router=router-name --region=us-central1
```

**Common issues:**
- Missing external IP on VM
- Blocking egress firewall rules
- Incorrect route configuration
- Cloud NAT not configured for private subnet

---

### Q8: Two VMs in the same VPC cannot communicate. What could be the causes and how would you fix them?

**Answer:**
**Possible causes and solutions:**

**1. Firewall rules blocking traffic:**
```bash
# Check ingress rules for target VM
gcloud compute firewall-rules list --filter="direction=INGRESS AND network=VPC_NAME"

# Create allow rule if needed
gcloud compute firewall-rules create allow-internal \
  --direction=INGRESS --priority=1000 --network=VPC_NAME \
  --action=ALLOW --rules=all --source-tags=internal \
  --target-tags=internal
```

**2. VMs in different subnets without routes:**
```bash
# Check if subnets are in same VPC
gcloud compute networks subnets list --network=VPC_NAME

# Verify local routes exist
gcloud compute routes list --filter="network=VPC_NAME AND nextHopGateway=default-internet-gateway"
```

**3. Network tags not applied correctly:**
```bash
# Check VM tags
gcloud compute instances describe vm-instance --zone=us-central1-a --format="value(tags.items)"

# Update tags if needed
gcloud compute instances add-tags vm-instance --tags=internal --zone=us-central1-a
```

**4. VPC Service Controls blocking:**
- Check if VPC SC is enabled
- Verify service perimeter configuration
- Check access levels

**5. Private Google Access issues:**
- Ensure VMs are in subnets with Private Google Access enabled
- Check DNS configuration

**Testing connectivity:**
```bash
# From source VM
ping destination-internal-ip
traceroute destination-internal-ip
```

---

### Q9: How would you troubleshoot VPC peering connectivity issues?

**Answer:**
**VPC Peering troubleshooting steps:**

**1. Verify peering status:**
```bash
# Check peering state
gcloud compute networks peerings list

# Should show ACTIVE state
gcloud compute networks peerings describe PEERING_NAME --network=VPC_NAME
```

**2. Check routes are exchanged:**
```bash
# List routes from peering
gcloud compute routes list --filter="nextHopPeering=PEERING_NAME"

# Verify remote VPC CIDR is present
gcloud compute routes list --filter="network=VPC_NAME"
```

**3. Firewall rules across peered networks:**
```bash
# Firewall rules don't automatically allow cross-network traffic
gcloud compute firewall-rules create allow-peered \
  --direction=INGRESS --priority=1000 --network=VPC_NAME \
  --action=ALLOW --rules=all \
  --source-ranges=REMOTE_VPC_CIDR
```

**4. Test connectivity:**
```bash
# Ping remote VM
ping remote-vm-internal-ip

# Check ARP table
arp -a

# Verify routing table
ip route show
```

**5. Common issues:**
- Peering in INACTIVE state (check project permissions)
- Missing firewall rules for peered traffic
- Overlapping IP ranges (not allowed in peering)
- VPC Service Controls blocking peered access

---

## Advanced Scenarios

### Q10: How would you implement a hub-and-spoke network architecture using VPC peering?

**Answer:**
**Hub-and-Spoke Architecture:**

**Hub VPC (Network Operations):**
- `hub-vpc`: 10.0.0.0/16
- Central services: Cloud NAT, VPN gateways, security tools
- Shared services subnets

**Spoke VPCs (Application Teams):**
- `app1-vpc`: 10.1.0.0/16
- `app2-vpc`: 10.2.0.0/16
- Isolated application environments

**Peering Configuration:**
```bash
# Peer spokes to hub
gcloud compute networks peerings create app1-to-hub \
  --network=app1-vpc --peer-network=hub-vpc \
  --export-custom-routes --import-custom-routes

gcloud compute networks peerings create app2-to-hub \
  --network=app2-vpc --peer-network=hub-vpc \
  --export-custom-routes --import-custom-routes
```

**Route Configuration:**
- Hub exports routes to internet gateway
- Spokes import hub routes for external access
- No direct spoke-to-spoke communication (security)

**Security:**
- Hub controls all external access via Cloud NAT
- Central firewall rules in hub VPC
- Network logging and monitoring in hub

**Benefits:**
- Centralized network management
- Cost-effective shared internet access
- Security controls at hub level
- Isolation between application environments

---

### Q11: Explain how to implement network security using VPC features and best practices.

**Answer:**
**Defense in Depth Security:**

**1. Network Segmentation:**
```bash
# Create separate subnets for different tiers
gcloud compute networks subnets create web-subnet \
  --network=secure-vpc --region=us-central1 --range=10.0.1.0/24

gcloud compute networks subnets create app-subnet \
  --network=secure-vpc --region=us-central1 --range=10.0.2.0/24

gcloud compute networks subnets create db-subnet \
  --network=secure-vpc --region=us-central1 --range=10.0.3.0/24
```

**2. Firewall Rules - Least Privilege:**
```bash
# Specific rules instead of allow-all
gcloud compute firewall-rules create allow-ssh-from-bastion \
  --direction=INGRESS --priority=1000 --network=secure-vpc \
  --action=ALLOW --rules=tcp:22 --source-tags=bastion \
  --target-tags=ssh-access
```

**3. Private Google Access:**
```bash
# Enable Private Google Access on private subnets
gcloud compute networks subnets update app-subnet \
  --region=us-central1 --enable-private-ip-google-access
```

**4. VPC Service Controls:**
- Create service perimeter
- Protect sensitive APIs
- Prevent data exfiltration

**5. Cloud NAT for outbound:**
```bash
# Controlled outbound access
gcloud compute routers nats create cloud-nat \
  --router=router-name --region=us-central1 \
  --nat-external-ip-pool=nat-ips --nat-all-subnet-ip-ranges
```

**6. Network Monitoring:**
- Enable VPC Flow Logs
- Set up Cloud Monitoring alerts
- Regular security audits

---

### Q12: How would you design a VPC for compliance with PCI DSS or HIPAA requirements?

**Answer:**
**Compliance VPC Design:**

**Network Segmentation:**
- **DMZ subnets**: Public-facing resources (10.0.1.0/24)
- **Application subnets**: Business logic (10.0.2.0/24)
- **Data subnets**: Sensitive data (10.0.3.0/24)
- **Management subnets**: Admin access (10.0.4.0/24)

**Security Controls:**
```bash
# Restrict management access
gcloud compute firewall-rules create allow-mgmt-ssh \
  --direction=INGRESS --priority=100 --network=compliance-vpc \
  --action=ALLOW --rules=tcp:22 --source-ranges=COMPANY_IPS \
  --target-tags=mgmt-access

# Deny all other inbound
gcloud compute firewall-rules create deny-all-inbound \
  --direction=INGRESS --priority=2000 --network=compliance-vpc \
  --action=DENY --rules=all --source-ranges=0.0.0.0/0
```

**Encryption:**
- SSL/TLS for data in transit
- Customer-managed encryption keys for data at rest
- IPsec for hybrid connectivity

**Monitoring & Auditing:**
- VPC Flow Logs enabled on all subnets
- Cloud Audit Logs for all API calls
- Real-time security monitoring
- Regular compliance assessments

**Access Controls:**
- IAM roles with least privilege
- Service accounts for applications
- Network tags for resource grouping
- VPC Service Controls for data protection

**High Availability & Disaster Recovery:**
- Multi-region deployment
- Cross-region VPN backups
- Automated failover procedures
- Regular backup and testing

---

### Q13: Describe how to implement zero-trust networking in GCP VPC.

**Answer:**
**Zero-Trust Architecture:**

**Identity-Based Access:**
```bash
# Use service accounts instead of network tags
gcloud compute firewall-rules create allow-app-access \
  --direction=INGRESS --priority=1000 --network=zero-trust-vpc \
  --action=ALLOW --rules=tcp:8080 \
  --target-service-accounts=app-service@project.iam.gserviceaccount.com \
  --source-service-accounts=web-service@project.iam.gserviceaccount.com
```

**Micro-Segmentation:**
- Subnet per application component
- Individual firewall rules per service
- No broad "allow all internal" rules

**Continuous Verification:**
- IAP (Identity-Aware Proxy) for admin access
- Continuous validation of device security
- Short-lived credentials

**Network-Level Controls:**
- VPC Flow Logs for traffic analysis
- Cloud Armor for external threat protection
- Private Google Access for API calls

**Monitoring & Response:**
- Real-time anomaly detection
- Automated response to suspicious activity
- Comprehensive audit logging

**Implementation Steps:**
1. **Inventory all resources** and their communication patterns
2. **Implement least-privilege firewall rules**
3. **Enable advanced security features** (VPC Service Controls, IAP)
4. **Set up monitoring and alerting**
5. **Regular policy reviews** and updates

---

### Q14: How would you optimize VPC costs while maintaining security and performance?

**Answer:**
**Cost Optimization Strategies:**

**1. Right-size subnets and IP ranges:**
```bash
# Use appropriate subnet sizes
gcloud compute networks subnets create optimized-subnet \
  --network=vpc-name --region=us-central1 --range=10.0.0.0/25  # 128 IPs instead of /24
```

**2. Use Private Google Access:**
- Eliminates need for external IPs on VMs
- Reduces data transfer costs for Google API calls

**3. Optimize Cloud NAT:**
```bash
# Configure NAT with specific IP ranges
gcloud compute routers nats create cost-optimized-nat \
  --router=nat-router --region=us-central1 \
  --nat-custom-subnet-ip-ranges=app-subnet \
  --nat-external-ip-pool=shared-nat-ips
```

**4. Leverage VPC peering instead of VPN:**
- No VPN gateway costs
- Lower latency and cost for cross-VPC traffic

**5. Use Shared VPC for multi-project:**
- Centralized network management
- Avoid duplicate network resources

**6. Monitor and clean up:**
```bash
# Find unused resources
gcloud compute networks subnets list --network=vpc-name
gcloud compute firewall-rules list --network=vpc-name

# Set up budget alerts
gcloud billing budgets create vpc-budget --amount=1000 \
  --filter-services=compute-engine-networking
```

**7. Choose appropriate connectivity:**
- Cloud Interconnect for high-volume on-prem traffic
- Cloud VPN for low-volume or backup connectivity

---

### Q15: Explain how to implement disaster recovery networking across regions.

**Answer:**
**Multi-Region DR Networking:**

**Primary Region Setup:**
- `prod-vpc`: 10.0.0.0/16
- Active application subnets
- Cloud SQL with cross-region replicas

**DR Region Setup:**
- `dr-vpc`: 10.0.0.0/16 (same CIDR for simplicity)
- Standby application subnets
- Replica databases

**Connectivity:**
```bash
# VPN between regions for data replication
gcloud compute vpn-tunnels create primary-to-dr \
  --peer-address=DR_EXTERNAL_IP --shared-secret=secret \
  --ike-version=2 --router=primary-router --vpn-gateway=primary-gateway

# Cloud Interconnect for high-bandwidth DR traffic
gcloud compute interconnects attachments create dr-interconnect \
  --interconnect=dr-interconnect-1 --router=dr-router \
  --region=us-west1
```

**DNS and Traffic Management:**
```bash
# Cloud DNS with geo-routing
gcloud dns managed-zones create dr-zone --dns-name=example.com --description="DR zone"

# Global load balancer with backend in both regions
gcloud compute backend-services create dr-backend \
  --protocol=HTTP --port-name=http --timeout=30 --global
```

**Failover Process:**
1. **Promote DR database replicas**
2. **Update DNS to point to DR region**
3. **Scale up DR instances**
4. **Update load balancer backends**

**Testing:**
- Regular DR drills
- Automated failover testing
- Network connectivity validation
- Application functionality testing

These scenarios demonstrate the depth and breadth of VPC networking concepts, from basic configuration to advanced enterprise architectures and troubleshooting techniques.