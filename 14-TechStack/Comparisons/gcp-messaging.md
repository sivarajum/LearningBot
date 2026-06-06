# Messaging: Pub/Sub vs Kafka (self/managed)
- Pub/Sub: fully managed, at-least-once, simple ops.
- Kafka: more control, exactly-once via patterns, ops heavy unless managed.
- Decision: managed, simple -> Pub/Sub; need fine-grain control/interop -> Kafka.
