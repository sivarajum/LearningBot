# Elasticsearch — Cheatsheet

## Architecture (30-second mental model)
```mermaid
graph TB
    Client -->|REST API| Coord[Coordinating Node]
    Coord --> D1[Data Node 1<br/>Shard P0, R1]
    Coord --> D2[Data Node 2<br/>Shard P1, R0]
    Coord --> D3[Data Node 3<br/>Shard P2, R2]
    M[Master Node] -.->|cluster state| D1
    M -.->|cluster state| D2
    M -.->|cluster state| D3
    subgraph Index = N primary shards + R replicas
        D1; D2; D3
    end
```

## When to use vs alternatives

| Need | Use Elasticsearch | Not Elasticsearch |
|------|-------------------|-------------------|
| Full-text search with relevance scoring | Yes -- Lucene-powered BM25/TF-IDF out of box | PostgreSQL `tsvector` if dataset is small (<10M docs) |
| Log/observability analytics (ELK) | Yes -- purpose-built with Kibana | ClickHouse or Loki if cost is primary concern |
| Primary transactional database | No -- not ACID, no joins | PostgreSQL or MySQL for OLTP |
| Vector similarity / ANN search | Possible (8.x kNN) but maturing | Pinecone / pgvector for dedicated vector workloads |
| Simple key-value lookups | Overkill -- inverted index overhead | Redis or DynamoDB |

## 5 things you always forget

1. **Mapping is immutable after first document** -- You cannot change a field's type (e.g., `text` to `keyword`) once indexed. You must reindex into a new index with the corrected mapping. Use index aliases to swap transparently.
2. **`text` vs `keyword` determines query behavior** -- `text` fields are analyzed (tokenized, lowercased) for full-text search. `keyword` fields are exact-match only. If you need both, use multi-fields: `"title": {"type":"text", "fields":{"raw":{"type":"keyword"}}}`.
3. **Shard count is set at index creation and cannot be changed** -- Over-sharding (too many small shards) wastes heap; under-sharding limits parallelism. Target 10-50 GB per shard. Use `_shrink` or reindex to fix after the fact.
4. **`refresh_interval` controls search visibility, not durability** -- Default is 1s. For bulk ingestion, set to `"30s"` or `"-1"` to disable, then reset after. This alone can double indexing throughput.
5. **Deep pagination with `from`+`size` breaks past 10,000 hits** -- Default `index.max_result_window` is 10000. Use `search_after` with a sort tiebreaker for deep pagination, or the Scroll API for full exports.

## Interview killer answer

> "We ran a 12-node Elasticsearch cluster indexing 2TB/day of application logs with a hot-warm-cold ILM policy: 3 hot nodes with SSDs held the latest 7 days, warm nodes stored 30 days compressed with force-merged segments, and cold moved to object storage via searchable snapshots. The key operational wins were setting refresh_interval to 30s during bulk ingestion, using index aliases for zero-downtime reindexing when mappings changed, and alerting on `jvm.mem.heap_used_percent > 75%` because GC pressure is the first sign of trouble before you see slow queries."
