# MongoDB Guide – Basic → Architect

## Level 1 – Launch & Basics

### 1. **Quick Setup**
```bash
# Install MongoDB
# macOS: brew install mongodb-community
# Linux: apt-get install mongodb

# Start
mongod

# Connect
mongo
```

### 2. **Basic Operations**
```python
from pymongo import MongoClient

client = MongoClient('mongodb://localhost:27017/')
db = client['mydb']
collection = db['users']

# Insert
collection.insert_one({'name': 'John', 'email': 'john@example.com'})

# Find
user = collection.find_one({'name': 'John'})

# Update
collection.update_one(
    {'name': 'John'},
    {'$set': {'email': 'new@example.com'}}
)
```

### 3. **Aggregation**
```python
pipeline = [
    {'$match': {'status': 'active'}},
    {'$group': {'_id': '$category', 'total': {'$sum': '$amount'}}}
]
results = collection.aggregate(pipeline)
```

## Level 2 – Production Patterns

### Indexes
```python
# Create index
collection.create_index([('email', 1)], unique=True)

# Compound index
collection.create_index([('category', 1), ('date', -1)])
```

### Transactions
```python
with client.start_session() as session:
    with session.start_transaction():
        collection1.insert_one(doc1, session=session)
        collection2.insert_one(doc2, session=session)
        session.commit_transaction()
```

## Level 3 – Architect Playbook

### Replica Set
```javascript
// Initialize replica set
rs.initiate({
    _id: "rs0",
    members: [
        { _id: 0, host: "localhost:27017" },
        { _id: 1, host: "localhost:27018" }
    ]
})
```

### Sharding
```javascript
// Enable sharding
sh.enableSharding("mydb")

// Shard collection
sh.shardCollection("mydb.collection", { "shard_key": 1 })
```

## Ops Cheat Sheet

| Task | Command | Notes |
| --- | --- | --- |
| Start | `mongod` | Start server |
| Connect | `mongo` | CLI access |
| Backup | `mongodump` | Backup database |
| Restore | `mongorestore` | Restore database |

## Checklist Before Production

- [ ] Set up proper indexing
- [ ] Configure replica sets
- [ ] Set up sharding if needed
- [ ] Configure authentication
- [ ] Set up monitoring
- [ ] Implement backup strategy
- [ ] Optimize queries
- [ ] Set up proper security
