# Elasticsearch Guide – Basic → Architect

## Level 1 – Launch & Basics

### 1. **Quick Setup**
```bash
# Install Elasticsearch
# Download from elastic.co

# Start
./bin/elasticsearch

# Verify
curl http://localhost:9200
```

### 2. **Basic Operations**
```python
from elasticsearch import Elasticsearch

es = Elasticsearch([{'host': 'localhost', 'port': 9200}])

# Index document
es.index(
    index='users',
    id=1,
    body={'name': 'John', 'email': 'john@example.com'}
)

# Search
result = es.search(
    index='users',
    body={'query': {'match': {'name': 'John'}}}
)
```

### 3. **Mapping**
```python
mapping = {
    'properties': {
        'name': {'type': 'text'},
        'email': {'type': 'keyword'},
        'age': {'type': 'integer'}
    }
}
es.indices.create(index='users', body={'mappings': mapping})
```

## Level 2 – Production Patterns

### Advanced Queries
```python
query = {
    'bool': {
        'must': [
            {'match': {'name': 'John'}},
            {'range': {'age': {'gte': 18}}}
        ]
    }
}
result = es.search(index='users', body={'query': query})
```

### Aggregations
```python
aggs = {
    'age_groups': {
        'terms': {'field': 'age'}
    }
}
result = es.search(index='users', body={'aggs': aggs})
```

## Level 3 – Architect Playbook

### Cluster Setup
```yaml
# elasticsearch.yml
cluster.name: my-cluster
node.name: node-1
network.host: 0.0.0.0
discovery.seed_hosts: ["node-1", "node-2"]
```

### Index Templates
```python
template = {
    'index_patterns': ['logs-*'],
    'settings': {
        'number_of_shards': 3,
        'number_of_replicas': 1
    }
}
es.indices.put_index_template(name='logs-template', body=template)
```

## Ops Cheat Sheet

| Task | Command | Notes |
| --- | --- | --- |
| Health | `curl localhost:9200/_cluster/health` | Check cluster |
| List indices | `curl localhost:9200/_cat/indices` | List indices |
| Search | `curl -X GET "localhost:9200/users/_search"` | Search |

## Checklist Before Production

- [ ] Configure proper sharding
- [ ] Set up cluster
- [ ] Configure monitoring
- [ ] Set up backup strategy
- [ ] Implement proper security
- [ ] Optimize queries
- [ ] Set up index lifecycle management
- [ ] Configure proper mappings
