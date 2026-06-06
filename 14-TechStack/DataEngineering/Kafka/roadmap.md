# Kafka Roadmap – 6 Weeks

## Weeks 1-2: Foundations (🟢)
- [ ] Day 1: Core concepts (topics, partitions, replication)
- [ ] Day 2: Console producer/consumer; create/delete topics
- [ ] Day 3: Acks, retries, idempotent producer
- [ ] Day 4: Consumers: groups, offsets, rebalancing
- [ ] Day 5: Retention vs compaction; configs
- [ ] Day 6: Serialization: JSON/Avro/Protobuf; schema registry intro
- [ ] Day 7: Mini-project: simple produce/consume app
- [ ] Day 8: Monitoring basics: lag, ISR
- [ ] Day 9: ACLs basics; quotas overview
- [ ] Day 10: Review + tidy configs
- [ ] Day 11-12: Partitioning strategy; keys
- [ ] Day 13-14: Rebalancing behavior; cooperative vs eager

**Milestone**: Confident with producers/consumers and core configs.

## Weeks 3-4: Intermediate (🟡)
- [ ] Day 15: Producer tuning (batch.size, linger.ms, compression)
- [ ] Day 16: Consumer tuning (max.poll, heartbeat/session timeouts)
- [ ] Day 17: DLQ pattern; poison pill handling
- [ ] Day 18: Exactly-once vs at-least-once tradeoffs
- [ ] Day 19: Schema registry compatibility modes
- [ ] Day 20: Lag monitoring/alerting; rebalance storms
- [ ] Day 21: Storage tuning; rack awareness; fsync policies
- [ ] Day 22-23: Mini-project: idempotent producer + DLQ consumer
- [ ] Day 24-25: Security: TLS/SASL, ACLs, authN/Z
- [ ] Day 26-28: Capacity planning; partition sizing; quotas

**Milestone**: Production-ready configs, security, monitoring.

## Weeks 5-6: Advanced (🔴)
- [ ] Day 29: Kafka Streams basics; KStream/KTable; joins/windows
- [ ] Day 30: State stores; repartition topics; standby replicas
- [ ] Day 31: Flink/Spark integration; watermarking; event time
- [ ] Day 32: Backpressure strategies; consumer lag controls
- [ ] Day 33: Multi-dc/DR considerations; MirrorMaker2
- [ ] Day 34: Compliance/governance: schema policies, ACL governance
- [ ] Day 35: Performance tuning: page cache, network, compression
- [ ] Day 36: Cost: retention strategies; compaction policies
- [ ] Day 37-38: Capstone: stream app with DLQ, schemas, monitoring
- [ ] Day 39-42: Docs, runbooks, incident drills

**Milestone**: Streaming-ready Kafka with governance and DR.

## Resources
- Docs: https://kafka.apache.org/documentation/
- Kafka Streams: https://kafka.apache.org/documentation/streams/
- Confluent guides on EOS, schemas, and ops

