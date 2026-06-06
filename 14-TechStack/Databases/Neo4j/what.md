# Neo4j Database Guide

## Neo4j Fundamentals

### What is Neo4j?

Neo4j is a native graph database that stores and processes data in graph structures. It uses nodes, relationships, and properties to represent and store data, making it ideal for applications that require complex relationship traversals and pattern matching.

### Key Characteristics

- **Native Graph Storage**: Optimized for graph data structures
- **ACID Transactions**: Full ACID compliance with immediate consistency
- **Cypher Query Language**: Declarative graph query language
- **High Performance**: Fast traversals and pattern matching
- **Scalability**: Horizontal scaling with clustering
- **Schema Optional**: Flexible schema design

### Core Concepts

```cypher
// Node - Fundamental unit representing an entity
CREATE (person:Person {
  name: "John Doe",
  age: 30,
  email: "john@example.com"
})

// Relationship - Connection between nodes
CREATE (john:Person {name: "John"})-[:WORKS_FOR {since: 2020}]->(company:Company {name: "TechCorp"})

// Property - Key-value data stored on nodes/relationships
MATCH (p:Person {name: "John"})
SET p.salary = 75000, p.department = "Engineering"

// Label - Grouping mechanism for nodes
CREATE (u:User:Admin {name: "Admin User"})

// Path - Sequence of nodes and relationships
MATCH path = (start:Person)-[*]-(end:Company)
RETURN path
```

## Installation and Setup

### Single Instance Installation

```bash
# Download and install Neo4j
wget https://neo4j.com/artifact.php?name=neo4j-community-5.15.0-unix.tar.gz
tar -xzf neo4j-community-5.15.0-unix.tar.gz
cd neo4j-community-5.15.0

# Start Neo4j
./bin/neo4j start

# Access Neo4j Browser at http://localhost:7474
# Default credentials: neo4j/neo4j (change on first login)
```

### Docker Installation

```yaml
# docker-compose.yml
version: '3.8'
services:
  neo4j:
    image: neo4j:5.15
    container_name: neo4j
    ports:
      - "7474:7474"    # HTTP
      - "7687:7687"    # Bolt
    environment:
      - NEO4J_AUTH=neo4j/password
      - NEO4J_PLUGINS=["graph-data-science"]
    volumes:
      - neo4j-data:/data
      - neo4j-logs:/logs
    networks:
      - neo4j-net

volumes:
  neo4j-data:
  neo4j-logs:

networks:
  neo4j-net:
    driver: bridge
```

### Cluster Setup

```yaml
# docker-compose.yml for cluster
version: '3.8'
services:
  neo4j-core1:
    image: neo4j:5.15-enterprise
    ports:
      - "7474:7474"
      - "7687:7687"
    environment:
      - NEO4J_AUTH=neo4j/password
      - NEO4J_server_mode=CORE
      - NEO4J_initial_server_mode__constraint=PRIMARY
      - NEO4J_server_discovery_advertised__address=neo4j-core1:5000
      - NEO4J_server_discovery_listen__address=:5000
      - NEO4J_server_cluster_advertised__address=neo4j-core1:7688
      - NEO4J_server_cluster_listen__address=:7688
    volumes:
      - core1-data:/data
    networks:
      - neo4j-cluster

  neo4j-core2:
    image: neo4j:5.15-enterprise
    ports:
      - "7475:7474"
      - "7688:7687"
    environment:
      - NEO4J_AUTH=neo4j/password
      - NEO4J_server_mode=CORE
      - NEO4J_initial_server_mode__constraint=SECONDARY
      - NEO4J_server_discovery_advertised__address=neo4j-core2:5000
      - NEO4J_server_discovery_listen__address=:5000
      - NEO4J_server_cluster_advertised__address=neo4j-core2:7688
      - NEO4J_server_cluster_listen__address=:7688
      - NEO4J_server_discovery_advertised__address=neo4j-core1:5000
    volumes:
      - core2-data:/data
    depends_on:
      - neo4j-core1
    networks:
      - neo4j-cluster

volumes:
  core1-data:
  core2-data:

networks:
  neo4j-cluster:
    driver: bridge
```

## Cypher Query Language

### Basic CRUD Operations

```cypher
// Create nodes
CREATE (p:Person {
  name: "Alice Johnson",
  age: 28,
  city: "New York"
})
RETURN p

// Create relationships
MATCH (a:Person {name: "Alice Johnson"})
MATCH (b:Person {name: "Bob Smith"})
CREATE (a)-[:FRIENDS_WITH {since: 2018}]->(b)
RETURN a, b

// Read operations
MATCH (p:Person)
RETURN p.name, p.age
ORDER BY p.age DESC

// Update nodes
MATCH (p:Person {name: "Alice Johnson"})
SET p.age = 29, p.title = "Software Engineer"
RETURN p

// Update relationships
MATCH (a:Person {name: "Alice"})-[r:FRIENDS_WITH]->(b:Person {name: "Bob"})
SET r.since = 2019, r.strength = "close"
RETURN r

// Delete relationships
MATCH (a:Person {name: "Alice"})-[r:FRIENDS_WITH]->(b:Person {name: "Bob"})
DELETE r

// Delete nodes
MATCH (p:Person {name: "Alice Johnson"})
DELETE p
```

### Pattern Matching

```cypher
// Simple pattern matching
MATCH (p:Person)-[:WORKS_FOR]->(c:Company)
RETURN p.name, c.name

// Complex patterns
MATCH (p:Person)-[:WORKS_FOR]->(c:Company {industry: "Technology"})
WHERE p.age > 25
RETURN p.name, p.age, c.name

// Path patterns
MATCH path = (start:Person)-[*]-(end:Company)
WHERE length(path) > 2
RETURN path

// Shortest path
MATCH (start:Person {name: "Alice"}),
      (end:Person {name: "Charlie"}),
      path = shortestPath((start)-[*]-(end))
RETURN path

// Variable-length relationships
MATCH (p:Person)-[:FRIENDS_WITH*1..3]-(friend:Person)
WHERE p.name = "Alice"
RETURN friend.name, length(friend) as distance

// Pattern with properties
MATCH (p:Person)-[r:FRIENDS_WITH {strength: "close"}]->(friend:Person)
RETURN p.name, friend.name, r.since
```

### Aggregations and Functions

```cypher
// Basic aggregations
MATCH (p:Person)
RETURN count(p) as total_people,
       avg(p.age) as average_age,
       min(p.age) as min_age,
       max(p.age) as max_age

// Group by aggregations
MATCH (p:Person)-[:WORKS_FOR]->(c:Company)
RETURN c.name, count(p) as employee_count
ORDER BY employee_count DESC

// Collect function
MATCH (p:Person)-[:WORKS_FOR]->(c:Company)
RETURN c.name, collect(p.name) as employees

// String functions
MATCH (p:Person)
RETURN p.name,
       toLower(p.name) as lowercase_name,
       toUpper(p.name) as uppercase_name,
       substring(p.name, 0, 3) as first_three_chars

// Date functions
MATCH (p:Person)
RETURN p.name,
       date(p.birth_date) as birth_date,
       duration.inDays(date(), p.birth_date).days as age_in_days

// Mathematical functions
MATCH (p:Person)
RETURN p.name, p.salary,
       round(p.salary * 1.1) as increased_salary,
       sqrt(p.salary) as salary_sqrt

// Conditional expressions
MATCH (p:Person)
RETURN p.name, p.age,
       CASE
         WHEN p.age < 25 THEN "Young"
         WHEN p.age < 35 THEN "Adult"
         ELSE "Senior"
       END as age_group
```

## Schema and Constraints

### Constraints

```cypher
// Unique constraints
CREATE CONSTRAINT person_email_unique
FOR (p:Person)
REQUIRE p.email IS UNIQUE

CREATE CONSTRAINT company_name_unique
FOR (c:Company)
REQUIRE c.name IS UNIQUE

// Property existence constraints
CREATE CONSTRAINT person_name_required
FOR (p:Person)
REQUIRE p.name IS NOT NULL

CREATE CONSTRAINT person_age_positive
FOR (p:Person)
REQUIRE p.age IS NOT NULL AND p.age > 0

// Node key constraints (unique + not null)
CREATE CONSTRAINT person_key
FOR (p:Person)
REQUIRE (p.name, p.email) IS NODE KEY

// Relationship property constraints
CREATE CONSTRAINT friendship_required_since
FOR ()-[r:FRIENDS_WITH]-()
REQUIRE r.since IS NOT NULL

// Drop constraints
DROP CONSTRAINT person_email_unique
```

### Indexes

```cypher
// Single property index
CREATE INDEX person_name_index
FOR (p:Person)
ON (p.name)

CREATE INDEX person_age_index
FOR (p:Person)
ON (p.age)

// Composite index
CREATE INDEX person_name_age_index
FOR (p:Person)
ON (p.name, p.age)

// Text index
CREATE TEXT INDEX person_bio_index
FOR (p:Person)
ON (p.bio)

// Point index for spatial data
CREATE POINT INDEX location_index
FOR (p:Person)
ON (p.location)

// Full-text index
CREATE FULLTEXT INDEX person_search_index
FOR (p:Person)
ON EACH [p.name, p.bio, p.skills]

// Relationship index
CREATE INDEX works_for_since_index
FOR ()-[r:WORKS_FOR]-()
ON (r.since)

// Drop indexes
DROP INDEX person_name_index
```

## Data Modeling

### Graph Data Modeling Patterns

```cypher
// Entity-Attribute-Value pattern
CREATE (product:Product {id: "P001", name: "Laptop"})
CREATE (attr1:Attribute {name: "color", value: "black"})
CREATE (attr2:Attribute {name: "ram", value: "16GB"})
CREATE (product)-[:HAS_ATTRIBUTE]->(attr1)
CREATE (product)-[:HAS_ATTRIBUTE]->(attr2)

// Time-based versioning
CREATE (user:User {id: "U001", name: "John"})
CREATE (user_v1:UserVersion {name: "John Doe", valid_from: date("2020-01-01")})
CREATE (user_v2:UserVersion {name: "John Smith", valid_from: date("2023-01-01")})
CREATE (user)-[:VERSION]->(user_v1)
CREATE (user)-[:VERSION]->(user_v2)

// Hyper edges (connecting multiple nodes)
CREATE (meeting:Meeting {title: "Team Standup"})
CREATE (person1:Person {name: "Alice"})
CREATE (person2:Person {name: "Bob"})
CREATE (person3:Person {name: "Charlie"})
CREATE (meeting)-[:ATTENDEE]->(person1)
CREATE (meeting)-[:ATTENDEE]->(person2)
CREATE (meeting)-[:ATTENDEE]->(person3)

// Bill of Materials (BOM)
CREATE (car:Product {name: "Car"})
CREATE (engine:Product {name: "Engine"})
CREATE (wheel:Product {name: "Wheel"})
CREATE (car)-[:CONTAINS {quantity: 1}]->(engine)
CREATE (car)-[:CONTAINS {quantity: 4}]->(wheel)
CREATE (engine)-[:CONTAINS {quantity: 4}]->(piston:Product {name: "Piston"})
```

### Social Network Modeling

```cypher
// Basic social network
CREATE (alice:Person {name: "Alice", age: 30})
CREATE (bob:Person {name: "Bob", age: 32})
CREATE (charlie:Person {name: "Charlie", age: 28})
CREATE (diana:Person {name: "Diana", age: 29})

CREATE (alice)-[:FRIENDS_WITH {since: 2018}]->(bob)
CREATE (bob)-[:FRIENDS_WITH {since: 2018}]->(alice)
CREATE (alice)-[:FRIENDS_WITH {since: 2019}]->(charlie)
CREATE (charlie)-[:FRIENDS_WITH {since: 2019}]->(alice)
CREATE (bob)-[:FRIENDS_WITH {since: 2020}]->(diana)
CREATE (diana)-[:FRIENDS_WITH {since: 2020}]->(bob)

// Find mutual friends
MATCH (p1:Person {name: "Alice"})-[:FRIENDS_WITH]-(mutual:Person)-[:FRIENDS_WITH]-(p2:Person {name: "Bob"})
RETURN mutual.name

// Find friends of friends
MATCH (p:Person {name: "Alice"})-[:FRIENDS_WITH]-()-[:FRIENDS_WITH]-(foaf:Person)
WHERE foaf <> p
RETURN DISTINCT foaf.name

// Shortest path between people
MATCH (start:Person {name: "Alice"}),
      (end:Person {name: "Diana"}),
      path = shortestPath((start)-[*]-(end))
RETURN path
```

### Recommendation System Modeling

```cypher
// User-Item-Preference model
CREATE (user1:User {id: "U001", name: "Alice"})
CREATE (user2:User {id: "U002", name: "Bob"})
CREATE (movie1:Movie {id: "M001", title: "Inception"})
CREATE (movie2:Movie {id: "M002", title: "Matrix"})
CREATE (movie3:Movie {id: "M003", title: "Interstellar"})

CREATE (user1)-[:RATED {rating: 5, timestamp: datetime()}]->(movie1)
CREATE (user1)-[:RATED {rating: 4, timestamp: datetime()}]->(movie2)
CREATE (user2)-[:RATED {rating: 5, timestamp: datetime()}]->(movie1)
CREATE (user2)-[:RATED {rating: 3, timestamp: datetime()}]->(movie3)

// Collaborative filtering - find similar users
MATCH (u1:User)-[r1:RATED]->(m:Movie)<-[r2:RATED]-(u2:User)
WHERE u1.id = "U001" AND u2.id <> "U001"
WITH u2, count(m) as common_movies,
     sum((r1.rating - avg(r1.rating)) * (r2.rating - avg(r2.rating))) /
     (sqrt(sum((r1.rating - avg(r1.rating))^2)) * sqrt(sum((r2.rating - avg(r2.rating))^2))) as similarity
RETURN u2.name, similarity
ORDER BY similarity DESC

// Content-based recommendations
CREATE (movie1)-[:HAS_GENRE]->(:Genre {name: "Sci-Fi"})
CREATE (movie1)-[:HAS_GENRE]->(:Genre {name: "Thriller"})
CREATE (movie2)-[:HAS_GENRE]->(:Genre {name: "Sci-Fi"})
CREATE (movie2)-[:HAS_GENRE]->(:Genre {name: "Action"})

MATCH (u:User {id: "U001"})-[:RATED {rating: 5}]->(liked:Movie)-[:HAS_GENRE]->(g:Genre)<-[:HAS_GENRE]-(recommend:Movie)
WHERE NOT (u)-[:RATED]->(recommend)
RETURN recommend.title, count(g) as genre_matches
ORDER BY genre_matches DESC
```

## Advanced Queries

### Graph Algorithms

```cypher
// PageRank algorithm
CALL gds.pageRank.stream('myGraph', {
  maxIterations: 20,
  dampingFactor: 0.85
})
YIELD nodeId, score
RETURN gds.util.asNode(nodeId).name AS name, score
ORDER BY score DESC

// Community detection (Louvain)
CALL gds.louvain.stream('myGraph', {})
YIELD nodeId, communityId
RETURN communityId, collect(gds.util.asNode(nodeId).name) AS members
ORDER BY size(members) DESC

// Shortest path with Dijkstra
MATCH (start:Location {name: "New York"}),
      (end:Location {name: "Los Angeles"})
CALL gds.shortestPath.dijkstra.stream('roadNetwork', {
  sourceNode: start,
  targetNode: end,
  relationshipWeightProperty: 'distance'
})
YIELD nodeIds, totalCost
RETURN [node IN nodeIds | gds.util.asNode(node).name] AS path, totalCost

// Centrality measures
CALL gds.betweenness.stream('myGraph')
YIELD nodeId, score
RETURN gds.util.asNode(nodeId).name AS name, score
ORDER BY score DESC

// Similarity algorithms
CALL gds.nodeSimilarity.stream('myGraph', {
  similarityCutoff: 0.5
})
YIELD node1, node2, similarity
RETURN gds.util.asNode(node1).name AS person1,
       gds.util.asNode(node2).name AS person2,
       similarity
ORDER BY similarity DESC
```

### Temporal Queries

```cypher
// Time-based queries
MATCH (p:Person)-[r:WORKS_FOR]->(c:Company)
WHERE r.start_date <= date() AND (r.end_date IS NULL OR r.end_date >= date())
RETURN p.name, c.name, r.position

// Historical queries
MATCH (p:Person)-[r:WORKS_FOR]->(c:Company)
WHERE r.start_date >= date("2020-01-01") AND r.start_date <= date("2022-12-31")
RETURN p.name, c.name, r.position, r.start_date

// Duration calculations
MATCH (p:Person)-[r:EMPLOYED_AT]->(c:Company)
RETURN p.name, c.name,
       duration.inDays(r.end_date, r.start_date).days as days_employed,
       duration.inMonths(r.end_date, r.start_date).months as months_employed

// Trend analysis
MATCH (p:Post)
WHERE p.created >= date() - duration("P30D")
RETURN date(p.created) as date, count(p) as posts_per_day
ORDER BY date
```

### Full-Text Search

```cypher
// Create full-text index
CREATE FULLTEXT INDEX post_content_index
FOR (p:Post)
ON EACH [p.title, p.content]

// Search with full-text
CALL db.index.fulltext.queryNodes("post_content_index", "graph database")
YIELD node, score
RETURN node.title, node.content, score

// Fuzzy search
CALL db.index.fulltext.queryNodes("post_content_index", "databas~")
YIELD node, score
RETURN node.title, score

// Phrase search
CALL db.index.fulltext.queryNodes("post_content_index", '"graph database"')
YIELD node, score
RETURN node.title, score

// Boolean search
CALL db.index.fulltext.queryNodes("post_content_index", "graph AND database")
YIELD node, score
RETURN node.title, score
```

## Performance Optimization

### Query Optimization

```cypher
// Use EXPLAIN for query analysis
EXPLAIN MATCH (p:Person)-[:WORKS_FOR]->(c:Company)
WHERE p.age > 25
RETURN p.name, c.name

// PROFILE for detailed performance analysis
PROFILE MATCH (p:Person)-[:WORKS_FOR]->(c:Company)
WHERE p.age > 25
RETURN p.name, c.name

// Optimize with indexes
CREATE INDEX person_age_index FOR (p:Person) ON (p.age)
CREATE INDEX works_for_company_index FOR ()-[r:WORKS_FOR]-() ON (r.company_id)

// Use parameters to avoid query plan recompilation
MATCH (p:Person {name: $personName})-[:WORKS_FOR]->(c:Company)
RETURN p, c

// Limit result sets
MATCH (p:Person)-[:FRIENDS_WITH*1..3]-(friend:Person)
WHERE p.name = "Alice"
RETURN friend.name
LIMIT 100

// Use shortestPath for performance
MATCH (start:Person {name: "Alice"}),
      (end:Person {name: "Charlie"}),
      path = shortestPath((start)-[*..10]-(end))
RETURN path

// Avoid unnecessary pattern matching
// Bad: MATCH (p:Person)-[r]-(x) WHERE type(r) = "FRIENDS_WITH"
// Good: MATCH (p:Person)-[:FRIENDS_WITH]-(x)
```

### Memory and Caching

```cypher
// Configure memory settings in neo4j.conf
dbms.memory.heap.initial_size=2G
dbms.memory.heap.max_size=4G
dbms.memory.pagecache.size=2G

// Query result caching
CALL db.resample.index("person_name_index")

// Clear query cache
CALL db.clearQueryCaches()

// Memory monitoring
CALL dbms.listConfig()
YIELD name, value
WHERE name CONTAINS 'memory'
RETURN name, value
```

## Security

### Authentication and Authorization

```cypher
// Create users
CALL dbms.security.createUser('app_user', 'secure_password', false)

// Create roles
CALL dbms.security.createRole('reader')
CALL dbms.security.createRole('writer')
CALL dbms.security.createRole('admin')

// Assign roles to users
CALL dbms.security.addRoleToUser('reader', 'app_user')
CALL dbms.security.addRoleToUser('writer', 'app_user')

// Grant privileges
GRANT TRAVERSE ON GRAPH * TO reader
GRANT READ {*} ON GRAPH * TO reader
GRANT WRITE ON GRAPH * TO writer
GRANT ALL ON DBMS TO admin

// Database-level permissions
GRANT ACCESS ON DATABASE * TO reader
GRANT START ON DATABASE * TO reader
GRANT STOP ON DATABASE * TO admin

// Subgraph restrictions
GRANT READ {name, age} ON GRAPH * TO reader
DENY READ {salary} ON GRAPH * TO reader

// Revoke privileges
REVOKE READ {*} ON GRAPH * FROM reader
```

## Backup and Recovery

### Backup Operations

```bash
# Online backup
neo4j-admin database backup --to-path=/backup/neo4j-backup --verbose graph.db

# Backup with compression
neo4j-admin database backup --to-path=/backup/neo4j-backup --compress graph.db

# Incremental backup
neo4j-admin database backup --to-path=/backup/neo4j-backup --incremental graph.db

# Backup specific database
neo4j-admin database backup --to-path=/backup/neo4j-backup --verbose mydatabase

# Schedule automated backups
# Add to crontab: 0 2 * * * /path/to/neo4j/bin/neo4j-admin database backup --to-path=/backup/neo4j-backup graph.db
```

### Restore Operations

```bash
# Stop Neo4j before restore
neo4j stop

# Restore from backup
neo4j-admin database restore --from-path=/backup/neo4j-backup --verbose graph.db

# Restore to different location
neo4j-admin database restore --from-path=/backup/neo4j-backup --to-path=/data/neo4j/data/databases/graph.db graph.db

# Start Neo4j after restore
neo4j start

# Verify restore
# Access Neo4j Browser and run: MATCH (n) RETURN count(n)
```

## Integration with Applications

### Node.js Integration

```javascript
const neo4j = require('neo4j-driver');

const driver = neo4j.driver(
  'neo4j://localhost:7687',
  neo4j.auth.basic('neo4j', 'password')
);

async function createPerson(name, age) {
  const session = driver.session();
  try {
    const result = await session.run(
      'CREATE (p:Person {name: $name, age: $age}) RETURN p',
      { name, age }
    );
    return result.records[0].get('p');
  } finally {
    await session.close();
  }
}

async function findFriends(personName) {
  const session = driver.session();
  try {
    const result = await session.run(
      `MATCH (p:Person {name: $name})-[:FRIENDS_WITH]->(friend:Person)
       RETURN friend.name as name, friend.age as age`,
      { name: personName }
    );
    return result.records.map(record => ({
      name: record.get('name'),
      age: record.get('age')
    }));
  } finally {
    await session.close();
  }
}

async function recommendFriends(personName) {
  const session = driver.session();
  try {
    const result = await session.run(
      `MATCH (p:Person {name: $name})-[:FRIENDS_WITH]-()-[:FRIENDS_WITH]-(foaf:Person)
       WHERE foaf <> p AND NOT (p)-[:FRIENDS_WITH]-(foaf)
       RETURN foaf.name as name, count(*) as mutualFriends
       ORDER BY mutualFriends DESC LIMIT 5`,
      { name: personName }
    );
    return result.records.map(record => ({
      name: record.get('name'),
      mutualFriends: record.get('mutualFriends')
    }));
  } finally {
    await session.close();
  }
}

// Usage
async function main() {
  try {
    await createPerson('Alice', 30);
    await createPerson('Bob', 25);

    const friends = await findFriends('Alice');
    console.log('Friends:', friends);

    const recommendations = await recommendFriends('Alice');
    console.log('Recommendations:', recommendations);
  } finally {
    await driver.close();
  }
}

main();
```

### Python Integration

```python
from neo4j import GraphDatabase

class Neo4jConnection:
    def __init__(self, uri, user, password):
        self.driver = GraphDatabase.driver(uri, auth=(user, password))

    def close(self):
        self.driver.close()

    def create_person(self, name, age):
        with self.driver.session() as session:
            result = session.run(
                "CREATE (p:Person {name: $name, age: $age}) RETURN p",
                name=name, age=age
            )
            return result.single()[0]

    def find_friends(self, person_name):
        with self.driver.session() as session:
            result = session.run(
                """MATCH (p:Person {name: $name})-[:FRIENDS_WITH]->(friend:Person)
                   RETURN friend.name as name, friend.age as age""",
                name=person_name
            )
            return [dict(record) for record in result]

    def get_shortest_path(self, start_name, end_name):
        with self.driver.session() as session:
            result = session.run(
                """MATCH (start:Person {name: $start_name}),
                              (end:Person {name: $end_name}),
                              path = shortestPath((start)-[*]-(end))
                       RETURN path""",
                start_name=start_name, end_name=end_name
            )
            record = result.single()
            return record["path"] if record else None

# Usage
conn = Neo4jConnection("neo4j://localhost:7687", "neo4j", "password")

try:
    # Create people
    conn.create_person("Alice", 30)
    conn.create_person("Bob", 25)
    conn.create_person("Charlie", 35)

    # Create relationships
    with conn.driver.session() as session:
        session.run(
            """MATCH (a:Person {name: "Alice"}), (b:Person {name: "Bob"})
               CREATE (a)-[:FRIENDS_WITH]->(b)"""
        )
        session.run(
            """MATCH (b:Person {name: "Bob"}), (c:Person {name: "Charlie"})
               CREATE (b)-[:FRIENDS_WITH]->(c)"""
        )

    # Query data
    friends = conn.find_friends("Alice")
    print("Alice's friends:", friends)

    path = conn.get_shortest_path("Alice", "Charlie")
    print("Shortest path:", path)

finally:
    conn.close()
```

This comprehensive guide covers Neo4j from basic operations to advanced features including graph algorithms, performance optimization, security, and application integration.
