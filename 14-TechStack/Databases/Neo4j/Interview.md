# Neo4j Interview Questions and Answers

## Beginner Level Questions

### Q1: What is Neo4j and what problem does it solve?

**Answer:**

Neo4j is a graph database that stores data as nodes and relationships. It excels at querying complex relationships and is ideal for social networks, recommendation engines, and fraud detection.

**Key Use Cases:**
- Use case 1
- Use case 2
- Use case 3

### Q2: What are the core features of Neo4j?

**Answer:**

The core features include:

## Beginner Level Questions

### What is Neo4j and when should you use a graph database?

**Answer:**

Neo4j is a graph database storing data as nodes (entities) and relationships (edges). Use it for: social networks, recommendation engines, fraud detection, knowledge graphs, network analysis, and when relationships are as important as data. It excels at traversing complex relationships efficiently.

## Intermediate Level Questions

### Explain Cypher query language basics.

**Answer:**

Cypher is Neo4j's query language. Syntax: (node:Label) for nodes, -[relationship:TYPE]-> for relationships. MATCH finds patterns, WHERE filters, RETURN specifies output. Example: MATCH (p:Person)-[:KNOWS]->(f:Person) WHERE p.name = "Alice" RETURN f.name. It's declarative and pattern-matching based.


## References

- Official documentation
- Community resources
