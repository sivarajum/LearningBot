# Load Balancing - Interview Questions & Scenarios

## Core Concepts

### Q1: Explain the difference between global and regional load balancers in GCP. When would you choose each?

**Answer:**
Global load balancers (HTTP(S), SSL Proxy, TCP Proxy) distribute traffic across multiple regions, providing:
- Global anycast IP addresses
- Cross-region failover
- Geo-based routing to closest healthy backend
- Content-based routing (Layer 7)

Regional load balancers (Network, Internal, Internal HTTP(S)) operate within a single region:
- Regional IP addresses
- Lower latency for regional traffic
- Cost-effective for regional workloads
- Support for internal-only traffic

**Choose global when:**
- Multi-region deployment
- Global user base requiring low latency
- Need for cross-region failover
- Content-based routing requirements

**Choose regional when:**
- Single region deployment
- Internal service communication
- Cost sensitivity
- Lower latency requirements within region

---

### Q2: How does health checking work in GCP load balancers? What are the different types?

**Answer:**
Health checks monitor backend health and route traffic only to healthy instances:

**Types:**
1. **HTTP/HTTPS**: Checks HTTP status codes (200-399 healthy)
2. **TCP**: Verifies TCP connection establishment
3. **SSL**: Validates SSL certificate and TCP connection
4. **UDP**: Sends UDP packets and expects responses

**Configuration parameters:**
- **Check interval**: How often to check (10-300 seconds)
- **Timeout**: How long to wait for response (1-60 seconds)
- **Healthy threshold**: Consecutive successful checks to mark healthy (2-10)
- **Unhealthy threshold**: Consecutive failed checks to mark unhealthy (2-10)

**Health check scopes:**
- Regional health checks for regional LBs
- Global health checks for global LBs (probes from multiple regions)

---

### Q3: Describe the architecture of an HTTP Load Balancer. How does traffic flow from client to backend?

**Answer:**
HTTP Load Balancer uses a global distributed architecture:

**Traffic Flow:**
1. **Client** → **Edge PoP** (anycast IP: 74.125.0.0/16)
2. **SSL Termination** (if HTTPS) and certificate validation
3. **Content-based routing** using URL maps and host/path rules
4. **Backend selection** based on routing rules and load balancing algorithm
5. **Health checking** ensures only healthy backends receive traffic
6. **Load distribution** across healthy instances

**Key Components:**
- **URL Maps**: Define routing rules (host/path matching)
- **Target Proxies**: Handle SSL termination and protocol conversion
- **Backend Services**: Define backends and load balancing configuration
- **Backends**: Instance groups, NEGs, or serverless services

---

## Configuration Scenarios

### Q4: You need to configure a global load balancer for a web application with static content served from Cloud Storage and dynamic content from Compute Engine. How would you set this up?

**Answer:**
This requires content-based routing with multiple backend services:

**Steps:**
1. **Create backend buckets** for static content:
   ```
   gcloud compute backend-buckets create static-backend \
     --gcs-bucket-name=my-static-bucket
   ```

2. **Create instance group** for dynamic content:
   ```
   gcloud compute instance-groups managed create web-servers \
     --size=3 --template=web-server-template --region=us-central1
   ```

3. **Create backend services**:
   ```
   # For dynamic content
   gcloud compute backend-services create web-backend \
     --protocol=HTTP --port-name=http --timeout=30 \
     --health-checks=http-health-check --global

   # Add instance group to backend service
   gcloud compute backend-services add-backend web-backend \
     --instance-group=web-servers --instance-group-region=us-central1 \
     --global
   ```

4. **Create URL map** for routing:
   ```
   gcloud compute url-maps create web-url-map --default-service=web-backend

   # Route static content to Cloud Storage
   gcloud compute url-maps add-path-matcher web-url-map \
     --path-matcher-name=static-matcher \
     --default-backend-bucket=static-backend \
     --path-rules="/static/*=static-backend"
   ```

5. **Create target HTTP proxy** and **global forwarding rule**

---

### Q5: How would you implement blue-green deployment using GCP load balancers?

**Answer:**
Blue-green deployment routes traffic between two identical environments:

**Implementation:**
1. **Create two backend services** (blue and green)
2. **Use traffic splitting** in the load balancer:
   ```
   gcloud compute backend-services update blue-backend \
     --global --rate=100  # 100% to blue

   gcloud compute backend-services update green-backend \
     --global --rate=0    # 0% to green initially
   ```

3. **Gradual rollout**:
   - Start with 10% traffic to green
   - Monitor metrics (latency, errors, custom metrics)
   - Gradually increase to 100% if successful
   - Keep blue as rollback option

4. **Validation checks**:
   - Health checks pass
   - Application metrics within thresholds
   - Database connections working
   - External API integrations functional

5. **Rollback procedure**:
   - Switch traffic back to blue immediately
   - Investigate issues in green environment
   - Fix and re-deploy to green

---

### Q6: Explain how to configure session affinity (sticky sessions) in GCP load balancers.

**Answer:**
Session affinity ensures requests from the same client go to the same backend:

**Types:**
1. **Client IP affinity**: Routes based on client IP (Layer 4)
2. **Generated cookie affinity**: LB generates cookie (Layer 7)
3. **Header field affinity**: Based on HTTP header value
4. **HTTP cookie affinity**: Based on application cookie

**Configuration:**
```
gcloud compute backend-services update my-backend \
  --session-affinity=GENERATED_COOKIE \
  --affinity-cookie-ttl=3600 \
  --global
```

**Use cases:**
- Stateful applications requiring session persistence
- Shopping carts, user sessions
- Long-running transactions

**Considerations:**
- Reduces load distribution effectiveness
- Can cause uneven load if sessions are long
- Consider using external session stores (Redis, database) instead

---

## Troubleshooting Scenarios

### Q7: Your load balancer is returning 502 errors. What could be the causes and how would you troubleshoot?

**Answer:**
502 errors indicate backend server issues:

**Possible causes:**
1. **Backend health check failures**
2. **Backend servers not responding**
3. **SSL certificate issues**
4. **Backend service configuration problems**

**Troubleshooting steps:**
1. **Check backend health**:
   ```
   gcloud compute backend-services get-health my-backend --global
   ```

2. **Review health check configuration**:
   ```
   gcloud compute health-checks describe http-health-check
   ```

3. **Check backend instance logs**:
   ```
   gcloud logging read "resource.type=gce_instance AND jsonPayload.message:*502*"
   ```

4. **Verify SSL certificates** (for HTTPS backends)

5. **Check Cloud Monitoring** for backend metrics

6. **Test backend directly** (bypass load balancer)

---

### Q8: Traffic is not being distributed evenly across your backend instances. What could be causing this and how would you fix it?

**Answer:**
Uneven load distribution can cause performance issues:

**Possible causes:**
1. **Session affinity enabled** (sticky sessions)
2. **Different instance capacities**
3. **Health check configuration issues**
4. **Load balancing algorithm problems**

**Investigation:**
1. **Check load balancing mode**:
   ```
   gcloud compute backend-services describe my-backend
   ```

2. **Monitor instance metrics**:
   - CPU utilization per instance
   - Request count per instance
   - Response times

3. **Review health status** of all instances

4. **Check for session affinity** configuration

**Solutions:**
- **Disable session affinity** if not required
- **Use UTILIZATION balancing mode** instead of RATE
- **Ensure instances have similar capacity**
- **Configure proper health checks**
- **Use managed instance groups** with auto-scaling

---

### Q9: How would you handle a sudden traffic spike that exceeds your current backend capacity?

**Answer:**
Traffic spikes require rapid scaling and load management:

**Immediate actions:**
1. **Enable auto-scaling** on instance groups:
   ```
   gcloud compute instance-groups managed set-autoscaling my-group \
     --max-num-replicas=50 --min-num-replicas=3 \
     --target-cpu-utilization=0.7 --cool-down-period=60
   ```

2. **Configure load shedding** (if applicable):
   - Return 503 for non-critical requests
   - Implement request queuing
   - Use circuit breaker pattern

3. **Scale horizontally**:
   - Increase instance group size manually
   - Add more regions if using global LB
   - Use Cloud Run for serverless scaling

4. **Optimize performance**:
   - Enable CDN for static content
   - Implement caching layers
   - Optimize database queries

5. **Monitor and alert**:
   - Set up alerts for high latency/errors
   - Monitor queue depths
   - Track scaling events

---

## Advanced Scenarios

### Q10: How would you implement a multi-region active-active setup with global load balancing?

**Answer:**
Active-active setup serves traffic from multiple regions simultaneously:

**Architecture:**
1. **Global HTTP Load Balancer** with anycast IP
2. **Regional backend services** in multiple regions
3. **Cross-region data synchronization** (Cloud Spanner, global databases)
4. **Regional health checks** and failover

**Configuration:**
```
# Create global backend service
gcloud compute backend-services create global-backend \
  --protocol=HTTP --port-name=http --timeout=30 \
  --health-checks=http-health-check --global

# Add backends from multiple regions
gcloud compute backend-services add-backend global-backend \
  --instance-group=us-central1-group --instance-group-region=us-central1 --global

gcloud compute backend-services add-backend global-backend \
  --instance-group=europe-west1-group --instance-group-region=europe-west1 --global
```

**Considerations:**
- **Data consistency** across regions
- **Latency optimization** (route to closest region)
- **Cost optimization** (regional vs global resources)
- **Disaster recovery** (regional failover)

---

### Q11: Explain how to implement zero-downtime deployments with GCP load balancers.

**Answer:**
Zero-downtime deployments ensure continuous availability during updates:

**Rolling update strategy:**
1. **Create new instance template** with updated code
2. **Update managed instance group** with rolling update:
   ```
   gcloud compute instance-groups managed rolling-action start-update my-group \
     --version template=new-template --max-surge=3 --max-unavailable=0 \
     --min-ready 30s --replacement-method=RECREATE
   ```

3. **Health checks** ensure new instances are ready before old ones are removed

4. **Gradual traffic shifting** using traffic splitting

**Blue-green deployment:**
1. **Deploy to green environment** (separate instance group)
2. **Run comprehensive tests** on green
3. **Gradually shift traffic** from blue to green (0% → 10% → 50% → 100%)
4. **Monitor metrics** throughout the process
5. **Complete switch or rollback** based on results

**Canary deployment:**
1. **Route small percentage** of traffic to new version
2. **Monitor performance** and error rates
3. **Gradually increase** traffic if successful
4. **Full rollout or rollback** based on metrics

---

### Q12: How would you secure a load balancer against common web attacks?

**Answer:**
Load balancer security involves multiple layers:

**Cloud Armor integration:**
```
# Create security policy
gcloud compute security-policies create my-security-policy \
  --description="Block common attacks"

# Add rules for SQL injection
gcloud compute security-policies rules create 1000 \
  --security-policy=my-security-policy \
  --expression="evaluatePreconfiguredExpr('sqli-stable')" \
  --action=deny-403

# Add rules for XSS
gcloud compute security-policies rules create 1001 \
  --security-policy=my-security-policy \
  --expression="evaluatePreconfiguredExpr('xss-stable')" \
  --action=deny-403

# Apply to backend service
gcloud compute backend-services update my-backend \
  --security-policy=my-security-policy --global
```

**Additional security measures:**
1. **SSL/TLS configuration**: Use TLS 1.3, disable weak ciphers
2. **Rate limiting**: Prevent DDoS attacks
3. **IP allowlisting/blocking**: Restrict access by IP ranges
4. **WAF rules**: Block malicious patterns
5. **Bot management**: Detect and block automated attacks

**Monitoring:**
- **Security logs**: Monitor blocked requests
- **Alerting**: Set up alerts for attack patterns
- **Regular updates**: Keep security policies current

---

### Q13: Describe how to implement custom load balancing algorithms or routing rules.

**Answer:**
GCP provides flexible routing options beyond basic load balancing:

**Content-based routing:**
```
# Route based on URL path
gcloud compute url-maps add-path-matcher my-url-map \
  --path-matcher-name=api-matcher \
  --path-rules="/api/v1/*=api-backend,/api/v2/*=api-v2-backend" \
  --default-backend-bucket=static-backend
```

**Header-based routing:**
```
# Route based on custom headers
gcloud compute url-maps add-path-matcher my-url-map \
  --path-matcher-name=version-matcher \
  --header-action="set-x-version:v2" \
  --path-rules="/api/*=api-backend"
```

**Traffic splitting for A/B testing:**
```
# Split traffic between versions
gcloud compute backend-services update backend-v1 --global --rate=90
gcloud compute backend-services update backend-v2 --global --rate=10
```

**Custom routing with Cloud Functions:**
- Use serverless NEGs as backends
- Implement custom logic in Cloud Functions
- Route based on user attributes, time, location, etc.

---

### Q14: How would you monitor and optimize the performance of a load balancer?

**Answer:**
Comprehensive monitoring ensures optimal performance:

**Key metrics to monitor:**
1. **Latency**: Backend latency, total latency
2. **Error rates**: 4xx, 5xx response codes
3. **Throughput**: Requests per second, bandwidth
4. **Backend health**: Healthy vs unhealthy instances
5. **Connection counts**: Active connections, new connections/sec

**Monitoring setup:**
```
# Create dashboard in Cloud Monitoring
gcloud monitoring dashboards create my-lb-dashboard \
  --config-from-file=dashboard.json
```

**Optimization strategies:**
1. **Enable compression** for text-based responses
2. **Configure appropriate timeouts** (30-60 seconds typical)
3. **Use connection draining** for graceful shutdowns
4. **Implement caching** with CDN integration
5. **Optimize SSL** (use ECDHE ciphers, session resumption)

**Alerting:**
- High latency (>500ms)
- High error rates (>5%)
- Backend capacity issues
- SSL certificate expiration

---

### Q15: Explain the cost implications of different load balancer types and how to optimize costs.

**Answer:**
Load balancer costs vary by type and usage:

**Cost breakdown:**
- **Global HTTP(S) LB**: $0.025/hour + $0.008/GB egress
- **SSL Proxy LB**: $0.035/hour + $0.008/GB egress
- **TCP Proxy LB**: $0.045/hour + $0.008/GB egress
- **Network LB**: $0.025/hour (no data charges)
- **Internal LB**: $0.025/hour (no data charges)

**Cost optimization strategies:**
1. **Choose appropriate LB type**:
   - Use Network LB for TCP/UDP (cheapest)
   - Use HTTP LB only when content-based routing needed
   - Use regional LBs for single-region deployments

2. **Minimize data egress**:
   - Use CDN for static content
   - Compress responses
   - Cache frequently accessed data

3. **Optimize backend usage**:
   - Use auto-scaling to match capacity to demand
   - Use preemptible instances for non-critical workloads
   - Schedule workloads during off-peak hours

4. **Monitor and alert on costs**:
   ```
   gcloud billing budgets create my-budget --amount=1000 --thresholds=0.5,0.9,1.0
   ```

These scenarios cover the most common load balancing challenges and solutions in GCP, focusing on practical implementation and troubleshooting approaches.
