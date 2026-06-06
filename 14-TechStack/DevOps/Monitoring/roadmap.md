# Monitoring Roadmap – 6 Weeks

## Weeks 1-2: Foundations (🟢)
- [ ] Day 1: Metrics vs logs vs traces; SLI/SLO/error budget
- [ ] Day 2: Install Prometheus + node_exporter locally
- [ ] Day 3: Scrape app metrics; PromQL basics (rate, sum by, histograms)
- [ ] Day 4: Grafana dashboards; variables; panels
- [ ] Day 5: Alertmanager basics; simple alerts
- [ ] Day 6: Blackbox exporter for HTTP checks
- [ ] Day 7: Logging basics; structured JSON; centralize to Loki/ELK
- [ ] Day 8: Tracing intro; OpenTelemetry SDK; local Jaeger/Tempo
- [ ] Day 9: Correlate logs/metrics/traces via trace_id
- [ ] Day 10: Cleanup and review
- [ ] Day 11-12: Mini-project: monitor a 2-service app
- [ ] Day 13-14: Harden basics; doc runbook

**Milestone**: End-to-end metrics/logs/traces on a small app.

## Weeks 3-4: Intermediate (🟡)
- [ ] Day 15: Recording rules; dashboards with templating
- [ ] Day 16: Histograms for latency; bucket tuning
- [ ] Day 17: RED/USE methods applied to services
- [ ] Day 18: Alert design: multi-window burn-rate SLO alerts
- [ ] Day 19: Routing/silencing; on-call hygiene; runbooks linked
- [ ] Day 20: Cardinality control; label hygiene
- [ ] Day 21: Long-term metrics storage (Thanos/Mimir/Cortex)
- [ ] Day 22: Logs: retention tiers; PII scrubbing
- [ ] Day 23: Traces: sampling strategies; baggage/attrs
- [ ] Day 24-25: Mini-project: SLOs + burn-rate alerts for 3 services
- [ ] Day 26-28: Refine dashboards; add error budget tracking

**Milestone**: Production-grade signals with sane alerts and dashboards.

## Weeks 5-6: Advanced (🔴)
- [ ] Day 29: HA Prometheus; scaling scrapes; sharding/federation
- [ ] Day 30: Service mesh metrics + tracing integration
- [ ] Day 31: Policy: RBAC in Grafana; alert ownership
- [ ] Day 32: Security: TLS, auth, secret handling in exporters
- [ ] Day 33: Cost controls: retention, sampling, scrape intervals
- [ ] Day 34: Performance tuning: query optimization, recording rules
- [ ] Day 35: Compliance: audits, data residency, PII governance
- [ ] Day 36: Runbooks and incident drills; simulate outages
- [ ] Day 37-38: Capstone: SLOs, burn alerts, HA stack, DR tested
- [ ] Day 39-42: Documentation, handover, continuous improvement plan

**Milestone**: HA, secure, cost-aware, policy-driven observability stack.

## Resources
- Prometheus: https://prometheus.io/docs/introduction/overview/
- PromQL: https://prometheus.io/docs/prometheus/latest/querying/basics/
- RED/USE: https://www.weave.works/blog/the-red-method-key-metrics-for-microservices-architecture
- OpenTelemetry: https://opentelemetry.io/docs/

