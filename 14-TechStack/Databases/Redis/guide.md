# Redis (Databases) Guide – Basic → Architect

## Level 1 – Launch & Basics

### 1. **Quick Setup**
```bash
# Install Redis
brew install redis  # macOS
apt-get install redis-server  # Linux

# Start
redis-server

# CLI
redis-cli
```

### 2. **Basic Operations**
```python
import redis

r = redis.Redis(host='localhost', port=6379, db=0)

# Strings
r.set('key', 'value')
value = r.get('key')

# Lists
r.lpush('list', 'item')
r.rpop('list')

# Sets
r.sadd('set', 'member')
r.smembers('set')

# Hashes
r.hset('hash', 'field', 'value')
r.hget('hash', 'field')
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

### Advanced Data Structures
```python
# Sorted Sets
r.zadd('scores', {'player1': 100, 'player2': 200})
r.zrange('scores', 0, -1, withscores=True)

# HyperLogLog
r.pfadd('hll', 'item1', 'item2')
r.pfcount('hll')

# Streams
r.xadd('stream', {'field': 'value'})
r.xread({'stream': '0'})
```

### Transactions
```python
pipe = r.pipeline()
pipe.set('key1', 'value1')
pipe.set('key2', 'value2')
pipe.execute()
```

## Level 3 – Architect Playbook

### Clustering
```python
from rediscluster import RedisCluster

startup_nodes = [{"host": "127.0.0.1", "port": "7000"}]
rc = RedisCluster(startup_nodes=startup_nodes)
rc.set('key', 'value')
```

### Persistence
```conf
# redis.conf
save 900 1
save 300 10
save 60 10000

appendonly yes
appendfsync everysec
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
