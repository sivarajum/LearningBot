# Redis Database Guide

## What is Redis?

Redis (Remote Dictionary Server) is an open-source, in-memory data structure store used as a database, cache, and message broker. It supports various data structures and provides high performance for read/write operations.

### Key Characteristics

- **In-memory storage**: Extremely fast data access
- **Data structures**: Strings, hashes, lists, sets, sorted sets, bitmaps, hyperloglogs, geospatial indexes
- **Persistence**: Optional disk persistence with RDB snapshots and AOF
- **Replication**: Master-slave replication for high availability
- **Clustering**: Horizontal scaling with Redis Cluster
- **Pub/Sub**: Publish-subscribe messaging pattern
- **Lua scripting**: Server-side scripting capabilities
- **Transactions**: Atomic operations with MULTI/EXEC

## Core Data Structures

### Strings

Strings are the most basic Redis data type. They can store any kind of data: strings, integers, floats, or binary data.

```bash
# Set a string value
SET name "John Doe"

# Get a string value
GET name
# "John Doe"

# Set multiple values
MSET firstname "John" lastname "Doe" age "30"

# Get multiple values
MGET firstname lastname age
# 1) "John"
# 2) "Doe"
# 3) "30"

# Increment a numeric value
SET counter 100
INCR counter
# 101

INCRBY counter 5
# 106

# String operations
SET message "Hello World"
STRLEN message
# 11

GETRANGE message 0 4
# "Hello"

SETBIT bitstring 7 1
GETBIT bitstring 7
# 1
```

### Hashes

Hashes are maps between string fields and string values, perfect for representing objects.

```bash
# Set hash fields
HSET user:1000 name "John Doe" email "john@example.com" age "30"

# Get hash fields
HGET user:1000 name
# "John Doe"

HGETALL user:1000
# 1) "name"
# 2) "John Doe"
# 3) "email"
# 4) "john@example.com"
# 5) "age"
# 6) "30"

# Set multiple fields
HMSET user:1001 name "Jane Smith" email "jane@example.com" city "New York"

# Get multiple fields
HMGET user:1001 name email city
# 1) "Jane Smith"
# 2) "jane@example.com"
# 3) "New York"

# Check if field exists
HEXISTS user:1000 age
# 1

# Get all field names
HKEYS user:1000
# 1) "name"
# 2) "email"
# 3) "age"

# Get all values
HVALS user:1000
# 1) "John Doe"
# 2) "john@example.com"
# 3) "30"

# Get number of fields
HLEN user:1000
# 3

# Increment numeric field
HINCRBY user:1000 age 1
# 31
```

### Lists

Lists are linked lists of strings, ordered by insertion order.

```bash
# Push elements to the left
LPUSH mylist "world"
LPUSH mylist "hello"
# 2

LRANGE mylist 0 -1
# 1) "hello"
# 2) "world"

# Push elements to the right
RPUSH mylist "!"
# 3

LRANGE mylist 0 -1
# 1) "hello"
# 2) "world"
# 3) "!"

# Pop elements
LPOP mylist
# "hello"

RPOP mylist
# "!"

# Get list length
LLEN mylist
# 1

# Get element by index
LINDEX mylist 0
# "world"

# Set element by index
LSET mylist 0 "redis"
LRANGE mylist 0 -1
# 1) "redis"

# Insert before/after
LINSERT mylist BEFORE "redis" "hello"
LRANGE mylist 0 -1
# 1) "hello"
# 2) "redis"

# Remove elements
LREM mylist 1 "redis"
LRANGE mylist 0 -1
# 1) "hello"
```

### Sets

Sets are unordered collections of unique strings.

```bash
# Add members to set
SADD myset "apple"
SADD myset "banana"
SADD myset "cherry"
# 3

# Try to add duplicate
SADD myset "apple"
# 0

# Get all members
SMEMBERS myset
# 1) "cherry"
# 2) "banana"
# 3) "apple"

# Check if member exists
SISMEMBER myset "apple"
# 1

SISMEMBER myset "grape"
# 0

# Get set size
SCARD myset
# 3

# Remove member
SREM myset "banana"
# 1

SMEMBERS myset
# 1) "cherry"
# 2) "apple"

# Set operations
SADD set1 "a" "b" "c"
SADD set2 "c" "d" "e"

# Union
SUNION set1 set2
# 1) "a"
# 2) "b"
# 3) "c"
# 4) "d"
# 5) "e"

# Intersection
SINTER set1 set2
# 1) "c"

# Difference
SDIFF set1 set2
# 1) "a"
# 2) "b"

# Random member
SRANDMEMBER myset
# "apple"

# Pop random member
SPOP myset
# "apple"
```

### Sorted Sets

Sorted sets are like sets but where each member has an associated score used for sorting.

```bash
# Add members with scores
ZADD leaderboard 100 "Alice"
ZADD leaderboard 200 "Bob"
ZADD leaderboard 150 "Charlie"
# 3

# Get members by score range
ZRANGE leaderboard 0 -1 WITHSCORES
# 1) "Alice"
# 2) "100"
# 3) "Charlie"
# 4) "150"
# 5) "Bob"
# 6) "200"

# Get members in reverse order
ZREVRANGE leaderboard 0 -1 WITHSCORES
# 1) "Bob"
# 2) "200"
# 3) "Charlie"
# 4) "150"
# 5) "Alice"
# 6) "100"

# Get rank of member
ZRANK leaderboard "Bob"
# 2

ZREVRANK leaderboard "Bob"
# 0

# Get score of member
ZSCORE leaderboard "Bob"
# "200"

# Count members in score range
ZCOUNT leaderboard 100 200
# 3

# Remove member
ZREM leaderboard "Alice"
# 1

# Increment score
ZINCRBY leaderboard 50 "Charlie"
ZSCORE leaderboard "Charlie"
# "200"

# Get number of members
ZCARD leaderboard
# 2
```

## Advanced Features

### Transactions

Redis transactions allow executing multiple commands atomically.

```bash
# Start transaction
MULTI
# QUEUED

SADD myset "value1"
# QUEUED

SADD myset "value2"
# QUEUED

SET mykey "myvalue"
# QUEUED

# Execute transaction
EXEC
# 1) (integer) 1
# 2) (integer) 1
# 3) OK

# Discard transaction
MULTI
SADD myset "value3"
SET mykey2 "value"
DISCARD
# OK

# Check if commands were executed
SMEMBERS myset
# 1) "value2"
# 2) "value1"

EXISTS mykey2
# 0
```

### Pub/Sub

Redis provides publish/subscribe messaging paradigm.

```bash
# Subscribe to channels (in one client)
SUBSCRIBE news sports
# Reading messages... (press Ctrl-C to quit)

# Publish messages (in another client)
PUBLISH news "Breaking news: Redis 7.0 released!"
# (integer) 1

PUBLISH sports "Championship game tonight!"
# (integer) 1

# Pattern subscription
PSUBSCRIBE news:*
# Reading messages...

PUBLISH news:tech "New Redis features announced"
# (integer) 1

# Get subscribers count
PUBSUB NUMSUB news sports
# 1) "news"
# 2) (integer) 1
# 3) "sports"
# 4) (integer) 1

# Get active channels
PUBSUB CHANNELS
# 1) "news"
# 2) "sports"
```

### Lua Scripting

Redis supports Lua scripting for atomic execution of complex operations.

```lua
-- Simple script to increment and return value
local current = redis.call('GET', KEYS[1])
if not current then current = 0 end
local new_value = current + ARGV[1]
redis.call('SET', KEYS[1], new_value)
return new_value
```

```bash
# Load and execute script
SCRIPT LOAD "local current = redis.call('GET', KEYS[1]) if not current then current = 0 end local new_value = current + ARGV[1] redis.call('SET', KEYS[1], new_value) return new_value"
# "4e6d8fc8bb01276962cce5371fa98f4fb9c5f3"

# Execute script by SHA
EVALSHA 4e6d8fc8bb01276962cce5371fa98f4fb9c5f3 1 counter 5
# 5

EVALSHA 4e6d8fc8bb01276962cce5371fa98f4fb9c5f3 1 counter 10
# 15
```

### Expiration

Redis can set expiration times on keys.

```bash
# Set key with expiration (seconds)
SET session:12345 "user_data" EX 3600

# Set key with expiration (milliseconds)
SET cache:key "cached_value" PX 5000

# Set expiration on existing key
EXPIRE session:12345 1800
# 1

# Set expiration at specific timestamp
EXPIREAT session:12345 1609459200
# 1

# Get time to live
TTL session:12345
# 1799

# Remove expiration
PERSIST session:12345
# 1

TTL session:12345
# -1 (no expiration)

# Get expiration timestamp
PEXPIRETIME session:12345
# 1609459200000
```

## Persistence

### RDB Snapshots

RDB persistence performs point-in-time snapshots of your dataset at specified intervals.

```redis.conf
# Save snapshots every 15 minutes if at least 1 key changed
save 900 1

# Save snapshots every 5 minutes if at least 10 keys changed
save 300 10

# Save snapshots every 1 minute if at least 10000 keys changed
save 60 10000

# RDB file name
dbfilename dump.rdb

# Directory where RDB files are stored
dir /var/lib/redis

# Compress RDB files
rdbcompression yes

# Check RDB file integrity
rdbchecksum yes
```

### AOF (Append Only File)

AOF persistence logs every write operation received by the server.

```redis.conf
# Enable AOF
appendonly yes

# AOF file name
appendfilename "appendonly.aof"

# AOF sync policy
# no: don't fsync, just let the OS flush the data when it wants
# always: fsync after every write to the append only log
# everysec: fsync only one time every second
appendfsync everysec

# Rewrite AOF file automatically
auto-aof-rewrite-percentage 100
auto-aof-rewrite-min-size 64mb

# Load AOF if it's corrupted
aof-load-truncated yes
```

## Replication

Redis replication allows slave Redis instances to be exact copies of master instances.

### Master-Slave Replication

```redis.conf
# On slave servers
slaveof <master_ip> <master_port>

# Optional: password for master
masterauth <password>

# Slave read-only mode
slave-read-only yes

# Replication timeout
repl-timeout 60

# Disable RDB snapshots on slaves
save ""
```

### Sentinel for High Availability

Redis Sentinel provides high availability for Redis.

```sentinel.conf
# Sentinel port
port 26379

# Master to monitor
sentinel monitor mymaster 127.0.0.1 6379 2

# Password for master
sentinel auth-pass mymaster mypassword

# Down-after-milliseconds
sentinel down-after-milliseconds mymaster 5000

# Failover timeout
sentinel failover-timeout mymaster 60000

# Parallel syncs
sentinel parallel-syncs mymaster 1
```

## Redis Cluster

Redis Cluster provides automatic sharding and high availability.

### Cluster Configuration

```redis.conf
# Enable cluster mode
cluster-enabled yes

# Cluster config file
cluster-config-file nodes.conf

# Cluster node timeout
cluster-node-timeout 5000

# Minimum slaves to write
cluster-migration-barrier 1

# Slave validity factor
cluster-slave-validity-factor 10
```

### Cluster Management

```bash
# Create cluster
redis-cli --cluster create 127.0.0.1:7001 127.0.0.1:7002 127.0.0.1:7003 127.0.0.1:7004 127.0.0.1:7005 127.0.0.1:7006 --cluster-replicas 1

# Check cluster
redis-cli --cluster check 127.0.0.1:7001

# Add node
redis-cli --cluster add-node 127.0.0.1:7007 127.0.0.1:7001

# Reshard cluster
redis-cli --cluster reshard 127.0.0.1:7001

# Rebalance cluster
redis-cli --cluster rebalance 127.0.0.1:7001
```

## Python Client (redis-py)

### Basic Usage

```python
import redis

# Connect to Redis
r = redis.Redis(host='localhost', port=6379, db=0)

# Or with URL
r = redis.from_url('redis://localhost:6379/0')

# Strings
r.set('name', 'John')
name = r.get('name')
print(name)  # b'John'

# Hashes
r.hset('user:1000', 'name', 'John')
r.hset('user:1000', 'email', 'john@example.com')
user = r.hgetall('user:1000')
print(user)  # {b'name': b'John', b'email': b'john@example.com'}

# Lists
r.lpush('mylist', 'item1', 'item2', 'item3')
items = r.lrange('mylist', 0, -1)
print(items)  # [b'item3', b'item2', b'item1']

# Sets
r.sadd('myset', 'apple', 'banana', 'cherry')
fruits = r.smembers('myset')
print(fruits)  # {b'apple', b'cherry', b'banana'}

# Sorted Sets
r.zadd('leaderboard', {'Alice': 100, 'Bob': 200, 'Charlie': 150})
top_players = r.zrevrange('leaderboard', 0, 2, withscores=True)
print(top_players)  # [(b'Bob', 200.0), (b'Charlie', 150.0), (b'Alice', 100.0)]
```

### Advanced Usage

```python
import redis
import json
from typing import Optional, List, Dict

class RedisCache:
    def __init__(self, host='localhost', port=6379, db=0):
        self.r = redis.Redis(host=host, port=port, db=db)

    def set_json(self, key: str, data: dict, expire: int = None):
        """Set JSON data with optional expiration"""
        json_data = json.dumps(data)
        if expire:
            self.r.setex(key, expire, json_data)
        else:
            self.r.set(key, json_data)

    def get_json(self, key: str) -> Optional[dict]:
        """Get JSON data"""
        data = self.r.get(key)
        if data:
            return json.loads(data)
        return None

    def cache_user(self, user_id: int, user_data: dict):
        """Cache user data for 1 hour"""
        key = f"user:{user_id}"
        self.set_json(key, user_data, expire=3600)

    def get_cached_user(self, user_id: int) -> Optional[dict]:
        """Get cached user data"""
        key = f"user:{user_id}"
        return self.get_json(key)

class RedisQueue:
    def __init__(self, name: str, host='localhost', port=6379, db=0):
        self.r = redis.Redis(host=host, port=port, db=db)
        self.name = name

    def enqueue(self, item: dict):
        """Add item to queue"""
        json_item = json.dumps(item)
        self.r.lpush(self.name, json_item)

    def dequeue(self) -> Optional[dict]:
        """Remove and return item from queue"""
        item = self.r.rpop(self.name)
        if item:
            return json.loads(item)
        return None

    def size(self) -> int:
        """Get queue size"""
        return self.r.llen(self.name)

# Usage
cache = RedisCache()
queue = RedisQueue('tasks')

# Cache usage
user_data = {'id': 1, 'name': 'John', 'email': 'john@example.com'}
cache.cache_user(1, user_data)
cached_user = cache.get_cached_user(1)
print(cached_user)  # {'id': 1, 'name': 'John', 'email': 'john@example.com'}

# Queue usage
queue.enqueue({'task': 'send_email', 'user_id': 1})
queue.enqueue({'task': 'process_data', 'data_id': 123})

task = queue.dequeue()
print(task)  # {'task': 'send_email', 'user_id': 1}
print(queue.size())  # 1
```

### Connection Pooling

```python
import redis

# Create connection pool
pool = redis.ConnectionPool(host='localhost', port=6379, db=0, max_connections=20)

# Use pool in multiple clients
r1 = redis.Redis(connection_pool=pool)
r2 = redis.Redis(connection_pool=pool)

# All clients share the same connection pool
r1.set('key1', 'value1')
print(r2.get('key1'))  # b'value1'
```

### Pipelines

```python
import redis

r = redis.Redis()

# Create pipeline
pipe = r.pipeline()

# Queue multiple commands
pipe.set('name', 'John')
pipe.set('age', 30)
pipe.hset('user:1', 'name', 'John')
pipe.hset('user:1', 'age', 30)
pipe.expire('user:1', 3600)

# Execute all commands atomically
results = pipe.execute()
print(results)  # [True, True, 0, 0, True]
```

### Pub/Sub with Python

```python
import redis
import threading
import time

class RedisPubSub:
    def __init__(self, host='localhost', port=6379):
        self.r = redis.Redis(host=host, port=port)

    def publisher(self):
        """Publish messages to channels"""
        for i in range(5):
            self.r.publish('news', f'News item {i+1}')
            self.r.publish('sports', f'Sports update {i+1}')
            time.sleep(1)

    def subscriber(self):
        """Subscribe to channels"""
        pubsub = self.r.pubsub()
        pubsub.subscribe('news', 'sports')

        print("Subscribed to news and sports channels")
        for message in pubsub.listen():
            if message['type'] == 'message':
                print(f"Received: {message['channel']} - {message['data']}")

# Usage
pubsub = RedisPubSub()

# Start subscriber in background thread
subscriber_thread = threading.Thread(target=pubsub.subscriber)
subscriber_thread.daemon = True
subscriber_thread.start()

# Start publishing
pubsub.publisher()
```

## Performance Optimization

### Memory Optimization

```bash
# Monitor memory usage
INFO memory

# Get memory usage of key
MEMORY USAGE mykey

# Configure memory policies
CONFIG SET maxmemory 256mb
CONFIG SET maxmemory-policy allkeys-lru

# Memory policies:
# noeviction: Don't evict anything
# allkeys-lru: Evict least recently used keys
# allkeys-lfu: Evict least frequently used keys
# volatile-lru: Evict least recently used keys with expiration
# volatile-lfu: Evict least frequently used keys with expiration
# allkeys-random: Evict random keys
# volatile-random: Evict random keys with expiration
# volatile-ttl: Evict keys with shortest TTL
```

### Benchmarking

```bash
# Basic benchmark
redis-benchmark -n 100000 -c 50

# Benchmark specific commands
redis-benchmark -n 100000 -c 50 -t set,get

# Custom benchmark
redis-benchmark -n 100000 -c 50 -t set -d 100

# Pipeline benchmark
redis-benchmark -n 100000 -c 50 -P 10
```

### Monitoring

```bash
# Get server information
INFO

# Get specific section
INFO server
INFO clients
INFO memory
INFO persistence
INFO stats
INFO replication
INFO cpu
INFO cluster

# Monitor commands in real-time
MONITOR

# Get slow log
SLOWLOG GET 10

# Configure slow log
CONFIG SET slowlog-log-slower-than 10000
CONFIG SET slowlog-max-len 128
```

## Security

### Authentication

```redis.conf
# Require password
requirepass yourpassword

# Connect with password
redis-cli -a yourpassword

# Authenticate in session
AUTH yourpassword
```

### Network Security

```redis.conf
# Bind to specific interface
bind 127.0.0.1

# Disable dangerous commands
rename-command FLUSHDB ""
rename-command FLUSHALL ""
rename-command SHUTDOWN SHUTDOWN_REDIS

# Enable TLS
tls-port 6380
tls-cert-file /path/to/redis.crt
tls-key-file /path/to/redis.key
tls-ca-cert-file /path/to/ca.crt
```

## Common Use Cases

### Caching

```python
import redis
import json
from functools import wraps

class Cache:
    def __init__(self, host='localhost', port=6379):
        self.r = redis.Redis(host=host, port=port)

    def cache(self, expire=300):
        def decorator(func):
            @wraps(func)
            def wrapper(*args, **kwargs):
                # Create cache key
                key = f"{func.__name__}:{str(args)}:{str(kwargs)}"

                # Try to get from cache
                cached = self.r.get(key)
                if cached:
                    return json.loads(cached)

                # Execute function
                result = func(*args, **kwargs)

                # Cache result
                self.r.setex(key, expire, json.dumps(result))

                return result
            return wrapper
        return decorator

# Usage
cache = Cache()

@cache.cache(expire=600)
def get_user_data(user_id):
    # Simulate expensive operation
    time.sleep(2)
    return {'id': user_id, 'name': f'User {user_id}'}

# First call - slow
user = get_user_data(1)  # Takes 2 seconds

# Second call - fast (from cache)
user = get_user_data(1)  # Instant
```

### Session Store

```python
import redis
import json
import uuid
from datetime import datetime, timedelta

class SessionStore:
    def __init__(self, host='localhost', port=6379):
        self.r = redis.Redis(host=host, port=port)
        self.session_timeout = 3600  # 1 hour

    def create_session(self, user_data):
        """Create new session"""
        session_id = str(uuid.uuid4())
        session_key = f"session:{session_id}"

        session_data = {
            'user': user_data,
            'created_at': datetime.utcnow().isoformat(),
            'expires_at': (datetime.utcnow() + timedelta(seconds=self.session_timeout)).isoformat()
        }

        self.r.setex(session_key, self.session_timeout, json.dumps(session_data))
        return session_id

    def get_session(self, session_id):
        """Get session data"""
        session_key = f"session:{session_id}"
        data = self.r.get(session_key)

        if data:
            return json.loads(data)
        return None

    def destroy_session(self, session_id):
        """Destroy session"""
        session_key = f"session:{session_id}"
        self.r.delete(session_key)

    def extend_session(self, session_id):
        """Extend session expiration"""
        session_key = f"session:{session_id}"
        data = self.r.get(session_key)

        if data:
            session_data = json.loads(data)
            session_data['expires_at'] = (datetime.utcnow() + timedelta(seconds=self.session_timeout)).isoformat()
            self.r.setex(session_key, self.session_timeout, json.dumps(session_data))
            return True
        return False

# Usage
session_store = SessionStore()

# Create session
user_data = {'id': 1, 'username': 'john', 'role': 'admin'}
session_id = session_store.create_session(user_data)
print(f"Session created: {session_id}")

# Get session
session = session_store.get_session(session_id)
print(f"Session data: {session}")

# Extend session
session_store.extend_session(session_id)

# Destroy session
session_store.destroy_session(session_id)
```

### Rate Limiting

```python
import redis
import time
from typing import Optional

class RateLimiter:
    def __init__(self, host='localhost', port=6379):
        self.r = redis.Redis(host=host, port=port)

    def is_allowed(self, key: str, limit: int, window: int) -> bool:
        """
        Check if request is allowed under rate limit
        Args:
            key: Identifier (e.g., user_id, ip_address)
            limit: Maximum requests allowed
            window: Time window in seconds
        """
        current_time = int(time.time())
        window_start = current_time - window

        # Remove old requests outside the window
        self.r.zremrangebyscore(key, '-inf', window_start)

        # Count requests in current window
        request_count = self.r.zcard(key)

        if request_count < limit:
            # Add current request
            self.r.zadd(key, {str(current_time): current_time})
            # Set expiration on the key
            self.r.expire(key, window)
            return True

        return False

    def get_remaining_requests(self, key: str, limit: int, window: int) -> int:
        """Get remaining requests allowed in current window"""
        current_time = int(time.time())
        window_start = current_time - window

        # Remove old requests
        self.r.zremrangebyscore(key, '-inf', window_start)

        request_count = self.r.zcard(key)
        return max(0, limit - request_count)

    def get_reset_time(self, key: str, window: int) -> int:
        """Get time when rate limit resets"""
        current_time = int(time.time())
        window_start = current_time - window

        # Get oldest request in current window
        oldest = self.r.zrange(key, 0, 0, withscores=True)
        if oldest:
            return int(oldest[0][1]) + window
        return current_time + window

# Usage
limiter = RateLimiter()

# Rate limit: 10 requests per minute
user_id = "user123"
limit = 10
window = 60

for i in range(12):
    allowed = limiter.is_allowed(f"rate_limit:{user_id}", limit, window)
    remaining = limiter.get_remaining_requests(f"rate_limit:{user_id}", limit, window)
    reset_time = limiter.get_reset_time(f"rate_limit:{user_id}", window)

    print(f"Request {i+1}: Allowed={allowed}, Remaining={remaining}, Reset={reset_time}")
    time.sleep(1)
```

This comprehensive guide covers Redis fundamentals, data structures, advanced features, Python integration, performance optimization, security, and common use cases.
