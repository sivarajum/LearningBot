# VPC - Visual Architecture

## VPC Network Architecture

```mermaid
graph TD
    subgraph "Google Cloud Platform"
        A[GCP Organization]
        B[Projects]
        C[VPC Networks]
    end

    subgraph "VPC Network Components"
        D[VPC Network<br/>10.0.0.0/8]
        E[Subnets<br/>Regional]
        F[Routes<br/>Traffic forwarding]
        G[Firewall Rules<br/>Traffic filtering]
        H[VPN Gateways<br/>Hybrid connectivity]
    end

    subgraph "Regional Resources"
        I[us-central1<br/>Subnets]
        J[europe-west1<br/>Subnets]
        K[asia-east1<br/>Subnets]
    end

    subgraph "Subnet Details"
        L[Subnet A<br/>10.0.1.0/24]
        M[Subnet B<br/>10.0.2.0/24]
        N[Subnet C<br/>10.0.3.0/24]
    end

    A --> B
    B --> C
    C --> D
    D --> E
    D --> F
    D --> G
    D --> H
    E --> I
    E --> J
    E --> K
    I --> L
    I --> M
    I --> N

    style D fill:#2196f3
    style E fill:#ffb74d
    style I fill:#4caf50
```

## Auto Mode vs Custom Mode VPC

```mermaid
graph TD
    subgraph "Auto Mode VPC"
        A[Auto Mode VPC<br/>Default network]
        B[Automatic Subnets<br/>One per region]
        C[Fixed IP Ranges<br/>10.128.0.0/9 per region]
        D[Simple Setup<br/>Less configuration]
    end

    subgraph "Custom Mode VPC"
        E[Custom Mode VPC<br/>User-defined]
        F[Manual Subnets<br/>Custom IP ranges]
        G[Flexible Design<br/>Full control]
        H[Complex Setup<br/>More configuration]
    end

    subgraph "Auto Mode Example"
        I[us-central1<br/>10.128.0.0/16]
        J[europe-west1<br/>10.132.0.0/16]
        K[asia-east1<br/>10.136.0.0/16]
    end

    subgraph "Custom Mode Example"
        L[us-central1<br/>10.0.0.0/16]
        M[europe-west1<br/>10.1.0.0/16]
        N[asia-east1<br/>10.2.0.0/16]
    end

    A --> B
    A --> C
    A --> D
    B --> I
    B --> J
    B --> K
    E --> F
    E --> G
    E --> H
    F --> L
    F --> M
    F --> N

    style A fill:#2196f3
    style E fill:#ffb74d
    style I fill:#4caf50
```

## Subnet Architecture

```mermaid
graph TD
    subgraph "VPC Network"
        A[VPC<br/>10.0.0.0/8]
    end

    subgraph "Region: us-central1"
        B[us-central1 Region]
        C[Subnet 1<br/>10.0.1.0/24<br/>Zone A]
        D[Subnet 2<br/>10.0.2.0/24<br/>Zone B]
        E[Subnet 3<br/>10.0.3.0/24<br/>Zone C]
    end

    subgraph "Zone A Resources"
        F[VM Instance 1<br/>10.0.1.10]
        G[VM Instance 2<br/>10.0.1.11]
        H[GKE Cluster<br/>10.0.1.100-110]
    end

    subgraph "Zone B Resources"
        I[Cloud SQL<br/>10.0.2.50]
        J[Memorystore<br/>10.0.2.60]
        K[VM Instance 3<br/>10.0.2.20]
    end

    A --> B
    B --> C
    B --> D
    B --> E
    C --> F
    C --> G
    C --> H
    D --> I
    D --> J
    D --> K

    style B fill:#2196f3
    style C fill:#ffb74d
    style F fill:#4caf50
```

## Routing Architecture

```mermaid
graph TD
    subgraph "Route Table"
        A[Route Table<br/>VPC Routes]
    end

    subgraph "System Routes"
        B[Subnet Routes<br/>Auto-created<br/>Priority: 1000]
        C[Default Internet<br/>0.0.0.0/0 → Internet<br/>Priority: 1000]
        D[Local Routes<br/>VPC CIDR<br/>Priority: 0]
    end

    subgraph "Custom Routes"
        E[Static Routes<br/>User-defined<br/>Priority: 100-999]
        F[Dynamic Routes<br/>Cloud Router BGP<br/>Priority: 100]
        G[VPC Peering Routes<br/>Auto-imported<br/>Priority: 1000]
    end

    subgraph "Route Priority"
        H[Lowest Priority<br/>Higher number wins]
        I[Route Matching<br/>Most specific prefix]
        J[Next Hop<br/>Gateway or instance]
    end

    A --> B
    A --> C
    A --> D
    A --> E
    A --> F
    A --> G
    B --> H
    C --> I
    D --> J
    E --> H
    F --> I
    G --> J

    style A fill:#2196f3
    style B fill:#ffb74d
    style E fill:#4caf50
```

## Firewall Rules Architecture

```mermaid
graph TD
    subgraph "Firewall Rules"
        A[Firewall Rules<br/>VPC Level]
    end

    subgraph "Rule Components"
        B[Direction<br/>Ingress/Egress]
        C[Priority<br/>1-65535<br/>Lower = Higher]
        D[Action<br/>Allow/Deny]
        E[Targets<br/>Tags/Service Accounts]
    end

    subgraph "Match Criteria"
        F[Source/Destination<br/>IP ranges/Tags]
        G[Protocols/Ports<br/>TCP:80,443]
        H[Implied Deny<br/>Default action]
    end

    subgraph "Rule Evaluation"
        I[Priority Order<br/>Lowest number first]
        J[First Match Wins<br/>Stop evaluation]
        K[Stateful Tracking<br/>Return traffic allowed]
    end

    subgraph "Example Rules"
        L[SSH Access<br/>Priority: 1000<br/>TCP:22 from admin IPs]
        M[Web Traffic<br/>Priority: 1000<br/>TCP:80,443 from 0.0.0.0/0]
        N[Internal Traffic<br/>Priority: 1000<br/>All protocols<br/>Source: internal tag]
    end

    A --> B
    A --> C
    A --> D
    A --> E
    B --> F
    C --> G
    D --> H
    E --> I
    F --> J
    G --> K
    H --> L
    I --> M
    J --> N

    style A fill:#2196f3
    style B fill:#ffb74d
    style F fill:#4caf50
```

## VPC Peering Architecture

```mermaid
graph TD
    subgraph "VPC Network A"
        A[VPC A<br/>10.0.0.0/16]
        B[Subnet A1<br/>10.0.1.0/24]
        C[VM in A<br/>10.0.1.10]
    end

    subgraph "VPC Peering Connection"
        D[VPC Peering<br/>Direct connection<br/>No gateways]
        E[Route Exchange<br/>Automatic routes]
        F[Latency<br/>Google network only]
    end

    subgraph "VPC Network B"
        G[VPC B<br/>10.1.0.0/16]
        H[Subnet B1<br/>10.1.1.0/24]
        I[VM in B<br/>10.1.1.10]
    end

    subgraph "Traffic Flow"
        J[Direct Routing<br/>No NAT/VPN]
        K[Firewall Rules<br/>Still enforced]
        L[Non-transitive<br/>A↔B direct only]
    end

    A --> D
    B --> D
    C --> D
    D --> G
    D --> H
    D --> I
    D --> J
    D --> K
    D --> L

    style D fill:#2196f3
    style E fill:#ffb74d
    style J fill:#4caf50
```

## Shared VPC Architecture

```mermaid
graph TD
    subgraph "Host Project"
        A[Host Project<br/>Network Admin]
        B[Shared VPC Network<br/>10.0.0.0/16]
        C[Shared Subnets<br/>us-central1-a<br/>10.0.1.0/24]
    end

    subgraph "Service Projects"
        D[Service Project 1<br/>Application Team]
        E[Service Project 2<br/>Data Team]
        F[Service Project 3<br/>Analytics Team]
    end

    subgraph "Shared Resources"
        G[VM in Project 1<br/>10.0.1.10]
        H[VM in Project 2<br/>10.0.1.11]
        I[GKE in Project 3<br/>10.0.1.100-110]
    end

    subgraph "Network Admin Control"
        J[Firewall Rules<br/>Central management]
        K[Routes<br/>Central control]
        L[Subnets<br/>Shared across projects]
        M[IAM Permissions<br/>Network admin role]
    end

    A --> B
    B --> C
    C --> D
    C --> E
    C --> F
    D --> G
    E --> H
    F --> I
    B --> J
    B --> K
    B --> L
    A --> M

    style B fill:#2196f3
    style C fill:#ffb74d
    style G fill:#4caf50
```

## Hybrid Connectivity

```mermaid
graph TD
    subgraph "On-Premises"
        A[Corporate Network<br/>192.168.0.0/16]
        B[VPN Gateway<br/>On-prem router]
        C[Applications<br/>Internal systems]
    end

    subgraph "Cloud VPN"
        D[Cloud VPN Gateway<br/>HA VPN]
        E[IPsec Tunnels<br/>Encrypted]
        F[BGP Sessions<br/>Dynamic routing]
    end

    subgraph "VPC Network"
        G[VPC<br/>10.0.0.0/16]
        H[Cloud Router<br/>BGP speaker]
        I[Subnets<br/>Regional]
    end

    subgraph "Cloud Resources"
        J[VM Instances<br/>10.0.1.0/24]
        K[GKE Clusters<br/>10.0.2.0/24]
        L[Cloud SQL<br/>Private IP]
    end

    A --> B
    B --> D
    D --> E
    E --> F
    F --> H
    H --> G
    G --> I
    I --> J
    I --> K
    I --> L

    style D fill:#2196f3
    style F fill:#ffb74d
    style I fill:#4caf50
```

## Cloud Interconnect

```mermaid
graph TD
    subgraph "On-Premises"
        A[Data Center<br/>192.168.0.0/16]
        B[Router<br/>BGP enabled]
        C[Applications<br/>High bandwidth needs]
    end

    subgraph "Cloud Interconnect"
        D[Dedicated Interconnect<br/>10Gbps-100Gbps]
        E[VLAN Attachments<br/>802.1q tagged]
        F[Cloud Router<br/>BGP peering]
    end

    subgraph "VPC Network"
        G[VPC<br/>10.0.0.0/16]
        H[Cloud Router<br/>BGP routes]
        I[Subnets<br/>Regional]
    end

    subgraph "Cloud Resources"
        J[VM Instances<br/>10.0.1.0/24]
        K[BigQuery<br/>Data transfer]
        L[Cloud Storage<br/>Large datasets]
    end

    A --> B
    B --> D
    D --> E
    E --> F
    F --> H
    H --> G
    G --> I
    I --> J
    I --> K
    I --> L

    style D fill:#2196f3
    style F fill:#ffb74d
    style I fill:#4caf50
```

## Private Google Access

```mermaid
graph TD
    subgraph "Private Subnet"
        A[Private Subnet<br/>10.0.1.0/24<br/>No external IP]
        B[VM Instance<br/>10.0.1.10]
        C[GKE Pod<br/>10.0.1.50]
    end

    subgraph "Private Google Access"
        D[Private Access<br/>googleapis.com<br/>199.36.153.0/24]
        E[Restricted API<br/>restricted.googleapis.com<br/>199.36.153.0/24]
        F[DNS Resolution<br/>Internal IPs]
    end

    subgraph "Google APIs"
        G[Cloud Storage API<br/>Private IP]
        H[BigQuery API<br/>Private IP]
        I[Cloud PubSub API<br/>Private IP]
    end

    subgraph "Traffic Flow"
        J[VPC Internal<br/>No internet egress]
        K[Secure Connection<br/>Google network]
        L[Cost Savings<br/>No external IP charges]
    end

    A --> B
    B --> D
    C --> E
    D --> F
    E --> F
    F --> G
    F --> H
    F --> I
    D --> J
    E --> K
    F --> L

    style D fill:#2196f3
    style F fill:#ffb74d
    style G fill:#4caf50
```

## Cloud NAT Architecture

```mermaid
graph TD
    subgraph "Private Subnet"
        A[Private Subnet<br/>10.0.1.0/24]
        B[VM Instance<br/>No external IP]
        C[GKE Pod<br/>No external IP]
    end

    subgraph "Cloud NAT Gateway"
        D[Cloud NAT<br/>Regional gateway]
        E[NAT IP Pool<br/>External IPs]
        F[Port Allocation<br/>Dynamic ports]
    end

    subgraph "Outbound Traffic"
        G[HTTP Requests<br/>apt update]
        H[API Calls<br/>External services]
        I[Software Updates<br/>Package repos]
    end

    subgraph "Internet"
        J[External Services<br/>Public IPs]
        K[Package Repositories<br/>Public IPs]
        L[API Endpoints<br/>Public IPs]
    end

    A --> B
    B --> D
    C --> D
    D --> E
    D --> F
    B --> G
    C --> H
    B --> I
    G --> J
    H --> K
    I --> L

    style D fill:#2196f3
    style E fill:#ffb74d
    style G fill:#4caf50
```

## Multi-Environment Architecture

```mermaid
graph TD
    subgraph "Development VPC"
        A[Dev VPC<br/>10.10.0.0/16]
        B[Dev Subnets<br/>10.10.1.0/24]
        C[Dev Resources<br/>VMs, GKE]
    end

    subgraph "Staging VPC"
        D[Staging VPC<br/>10.20.0.0/16]
        E[Staging Subnets<br/>10.20.1.0/24]
        F[Staging Resources<br/>VMs, GKE]
    end

    subgraph "Production VPC"
        G[Prod VPC<br/>10.30.0.0/16]
        H[Prod Subnets<br/>10.30.1.0/24]
        I[Prod Resources<br/>VMs, GKE]
    end

    subgraph "Shared Services VPC"
        J[Shared VPC<br/>10.0.0.0/16]
        K[Shared Subnets<br/>10.0.1.0/24]
        L[Shared Resources<br/>Cloud SQL, Memorystore]
    end

    subgraph "VPC Peering"
        M[Dev ↔ Shared<br/>Peering connection]
        N[Staging ↔ Shared<br/>Peering connection]
        O[Prod ↔ Shared<br/>Peering connection]
    end

    A --> M
    D --> N
    G --> O
    M --> J
    N --> J
    O --> J
    B --> C
    E --> F
    H --> I
    K --> L

    style A fill:#2196f3
    style D fill:#ffb74d
    style G fill:#4caf50
    style J fill:#ba68c8
```

## Network Security Architecture

```mermaid
graph TD
    subgraph "Internet"
        A[External Traffic<br/>0.0.0.0/0]
    end

    subgraph "Cloud Armor"
        B[Cloud Armor<br/>WAF & DDoS]
        C[Security Policies<br/>Rate limiting]
        D[Custom Rules<br/>IP blocking]
    end

    subgraph "Load Balancer"
        E[HTTP(S) Load Balancer<br/>Global distribution]
        F[SSL Termination<br/>Certificate validation]
        G[Health Checks<br/>Backend monitoring]
    end

    subgraph "VPC Network"
        H[VPC Firewall<br/>Network level]
        I[Network Tags<br/>Instance grouping]
        J[Service Accounts<br/>Identity-based]
    end

    subgraph "Subnet Isolation"
        K[Public Subnet<br/>DMZ resources]
        L[Private Subnet<br/>Application tier]
        M[Database Subnet<br/>Data layer]
    end

    subgraph "Instance Level"
        N[OS Firewall<br/>iptables]
        O[Endpoint Verification<br/>Device security]
        P[IAM Permissions<br/>Access control]
    end

    A --> B
    B --> C
    C --> D
    D --> E
    E --> F
    F --> G
    G --> H
    H --> I
    I --> J
    J --> K
    K --> L
    L --> M
    M --> N
    N --> O
    O --> P

    style B fill:#2196f3
    style E fill:#ffb74d
    style H fill:#4caf50
    style K fill:#ba68c8
```

## VPC Flow Logs

```mermaid
graph TD
    subgraph "Network Traffic"
        A[VM to VM<br/>Internal traffic]
        B[VM to Internet<br/>External traffic]
        C[VM to Google APIs<br/>Private access]
        D[Load Balancer<br/>Health checks]
    end

    subgraph "VPC Flow Logs"
        E[Flow Sampling<br/>1:10 default]
        F[Metadata Capture<br/>5-tuple + more]
        G[Log Export<br/>Cloud Logging]
        H[Storage Options<br/>BigQuery, Storage]
    end

    subgraph "Log Contents"
        I[Source IP/Port<br/>Destination IP/Port]
        J[Protocol<br/>TCP/UDP/ICMP]
        K[Bytes/Packets<br/>Traffic volume]
        L[Start/End Time<br/>Connection duration]
        M[Instance Details<br/>VM metadata]
    end

    subgraph "Analysis & Monitoring"
        N[Security Monitoring<br/>Anomaly detection]
        O[Network Troubleshooting<br/>Connectivity issues]
        P[Cost Optimization<br/>Traffic analysis]
        Q[Compliance Auditing<br/>Traffic logs]
    end

    A --> E
    B --> E
    C --> E
    D --> E
    E --> F
    F --> G
    G --> H
    F --> I
    F --> J
    F --> K
    F --> L
    F --> M
    H --> N
    H --> O
    H --> P
    H --> Q

    style E fill:#2196f3
    style F fill:#ffb74d
    style I fill:#4caf50
```

## Global VPC with Cross-Region Connectivity

```mermaid
graph TD
    subgraph "Global VPC"
        A[Global VPC<br/>10.0.0.0/8]
    end

    subgraph "Region 1: us-central1"
        B[us-central1<br/>Subnets]
        C[Zone A<br/>10.0.1.0/24]
        D[Zone B<br/>10.0.2.0/24]
        E[Zone C<br/>10.0.3.0/24]
    end

    subgraph "Region 2: europe-west1"
        F[europe-west1<br/>Subnets]
        G[Zone A<br/>10.1.1.0/24]
        H[Zone B<br/>10.1.2.0/24]
        I[Zone C<br/>10.1.3.0/24]
    end

    subgraph "Region 3: asia-east1"
        J[asia-east1<br/>Subnets]
        K[Zone A<br/>10.2.1.0/24]
        L[Zone B<br/>10.2.2.0/24]
        M[Zone C<br/>10.2.3.0/24]
    end

    subgraph "Global Resources"
        N[Global Load Balancer<br/>Anycast IP]
        O[Cloud DNS<br/>Global DNS]
        P[Cloud CDN<br/>Global caching]
    end

    A --> B
    A --> F
    A --> J
    B --> C
    B --> D
    B --> E
    F --> G
    F --> H
    F --> I
    J --> K
    J --> L
    J --> M
    A --> N
    A --> O
    A --> P

    style A fill:#2196f3
    style B fill:#ffb74d
    style C fill:#4caf50
```

These diagrams illustrate the comprehensive VPC architecture in Google Cloud, showing how networks are structured, how traffic flows, and how various connectivity and security features work together to create secure, scalable network environments.
