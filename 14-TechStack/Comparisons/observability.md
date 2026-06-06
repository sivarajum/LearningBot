# Observability: Logging vs Metrics vs Traces
- Logs: structured JSON + trace/span IDs.
- Metrics: SLOs, alerts; avoid cardinality explosion.
- Traces: request path, latency breakdown.
- Decision: use all three; correlate via trace IDs; alerts on SLO burn.
