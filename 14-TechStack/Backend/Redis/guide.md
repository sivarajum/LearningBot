# Redis Guide – Basic → Architect

## Level 1 – Launch & Basics

### 1. **Quick Setup**
```bash
# Install Redis
# macOS: brew install redis
# Linux: apt-get install redis-server

# Start Redis
redis-server

# CLI
redis-cli
```

### 2. **Basic Operations**
```python
import redis

r = redis.Redis(host='localhost', port=6379, db=0)

# Set/Get
r.set('key', 'value')
value = r.get('key')

# Lists
r.lpush('list', 'item1')
r.rpop('list')

# Sets
r.sadd('set', 'member1')
r.smembers('set')
```

### 3. **Pub/Sub**
```python
# Publisher
r.publish('channel', 'message')

# Subscriber
pubsub = r.pubsub()
pubsub.subscribe('channel')
for message in pubsub.listen():
    print(message)
```

## Level 2 – Production Patterns

### Transactions
```python
pipe = r.pipeline()
pipe.set('key1', 'value1')
pipe.set('key2', 'value2')
pipe.execute()
```

### Lua Scripting
```python
script = """
    local value = redis.call('GET', KEYS[1])
    return value
"""
result = r.eval(script, 1, 'key')
```

## Level 3 – Architect Playbook

### Clustering
```python
from rediscluster import RedisCluster

startup_nodes = [{"host": "127.0.0.1", "port": "7000"}]
rc = RedisCluster(startup_nodes=startup_nodes, decode_responses=True)
rc.set('key', 'value')
```

## Ops Cheat Sheet

| Task | Command | Notes |
| --- | --- | --- |
| Start | `redis-server` | Start server |
| CLI | `redis-cli` | Command line |
| Monitor | `redis-cli monitor` | Monitor commands |
| Info | `redis-cli info` | Server info |

## Checklist Before Production

- [ ] Configure persistence (RDB/AOF)
- [ ] Set up replication
- [ ] Configure memory limits
- [ ] Set up monitoring
- [ ] Implement proper security
- [ ] Configure clustering if needed
- [ ] Set up backup strategy
- [ ] Optimize performance
