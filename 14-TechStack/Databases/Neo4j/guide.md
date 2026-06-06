# Neo4j Guide – Basic → Architect

## Level 1 – Launch & Basics

### 1. **Quick Setup**
```bash
# Install Neo4j
# Download from neo4j.com

# Start
neo4j start

# Access Browser
# http://localhost:7474
```

### 2. **Basic Cypher**
```cypher
// Create nodes
CREATE (a:Person {name: 'John', age: 30})
CREATE (b:Person {name: 'Jane', age: 25})

// Create relationship
MATCH (a:Person {name: 'John'}), (b:Person {name: 'Jane'})
CREATE (a)-[:KNOWS]->(b)

// Query
MATCH (a:Person)-[:KNOWS]->(b:Person)
RETURN a, b
```

### 3. **Python Integration**
```python
from neo4j import GraphDatabase

driver = GraphDatabase.driver("bolt://localhost:7687", auth=("neo4j", "password"))

def create_person(tx, name, age):
    tx.run("CREATE (a:Person {name: $name, age: $age})", name=name, age=age)

with driver.session() as session:
    session.write_transaction(create_person, "John", 30)
```

## Level 2 – Production Patterns

### Graph Algorithms
```cypher
// Shortest path
MATCH path = shortestPath(
    (a:Person {name: 'John'})-[*]-(b:Person {name: 'Jane'})
)
RETURN path

// PageRank
CALL gds.pageRank.stream('myGraph')
YIELD nodeId, score
RETURN gds.util.asNode(nodeId).name AS name, score
ORDER BY score DESC
```

### Indexes
```cypher
CREATE INDEX person_name FOR (p:Person) ON (p.name)
```

## Level 3 – Architect Playbook

### Clustering
```yaml
# neo4j.conf
dbms.mode=CORE
causal_clustering.minimum_core_cluster_size_at_formation=3
causal_clustering.initial_discovery_members=core1:5000,core2:5000,core3:5000
```

## Ops Cheat Sheet

| Task | Command | Notes |
| --- | --- | --- |
| Start | `neo4j start` | Start server |
| Stop | `neo4j stop` | Stop server |
| Status | `neo4j status` | Check status |

## Checklist Before Production

- [ ] Set up proper indexing
- [ ] Configure clustering
- [ ] Set up monitoring
- [ ] Implement proper security
- [ ] Set up backup strategy
- [ ] Optimize queries
- [ ] Configure memory settings
- [ ] Set up proper access controls
