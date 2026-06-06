# Elasticsearch Database Guide

## Elasticsearch Fundamentals

### What is Elasticsearch?

Elasticsearch is a distributed, RESTful search and analytics engine capable of addressing a growing number of use cases. It centrally stores your data for lightning-fast search, fine-tuned relevancy, and powerful analytics that scale with ease.

### Key Characteristics

- **Distributed**: Horizontally scalable distributed system
- **RESTful**: REST APIs for all operations
- **Real-time**: Near real-time search and analytics
- **Full-text Search**: Advanced full-text search capabilities
- **Schema-free**: Dynamic mapping of JSON documents
- **Multitenant**: Multiple indices with shared resources
- **High Availability**: Built-in clustering and replication

### Core Concepts

```json
// Document - Basic unit of storage
{
  "_index": "products",
  "_id": "1",
  "_version": 1,
  "_source": {
    "name": "Wireless Headphones",
    "brand": "AudioTech",
    "price": 199.99,
    "category": "Electronics",
    "tags": ["wireless", "bluetooth", "music"],
    "created_at": "2023-01-15T10:30:00Z"
  }
}

// Index - Collection of documents
{
  "settings": {
    "number_of_shards": 3,
    "number_of_replicas": 1
  },
  "mappings": {
    "properties": {
      "name": { "type": "text" },
      "brand": { "type": "keyword" },
      "price": { "type": "double" },
      "category": { "type": "keyword" },
      "tags": { "type": "keyword" },
      "created_at": { "type": "date" }
    }
  }
}
```

## Installation and Setup

### Single Node Installation

```bash
# Download and install Elasticsearch
wget https://artifacts.elastic.co/downloads/elasticsearch/elasticsearch-8.11.0-linux-x86_64.tar.gz
tar -xzf elasticsearch-8.11.0-linux-x86_64.tar.gz
cd elasticsearch-8.11.0/

# Start Elasticsearch
./bin/elasticsearch

# Verify installation
curl -X GET "localhost:9200/?pretty"
```

### Docker Installation

```yaml
# docker-compose.yml
version: '3.8'
services:
  elasticsearch:
    image: docker.elastic.co/elasticsearch/elasticsearch:8.11.0
    container_name: elasticsearch
    environment:
      - discovery.type=single-node
      - "ES_JAVA_OPTS=-Xms512m -Xmx512m"
      - ELASTIC_PASSWORD=my_password
    ports:
      - "9200:9200"
      - "9300:9300"
    volumes:
      - elasticsearch-data:/usr/share/elasticsearch/data
    networks:
      - elastic

  kibana:
    image: docker.elastic.co/kibana/kibana:8.11.0
    container_name: kibana
    ports:
      - "5601:5601"
    environment:
      - ELASTICSEARCH_HOSTS=http://elasticsearch:9200
      - ELASTICSEARCH_USERNAME=elastic
      - ELASTICSEARCH_PASSWORD=my_password
    depends_on:
      - elasticsearch
    networks:
      - elastic

volumes:
  elasticsearch-data:

networks:
  elastic:
    driver: bridge
```

### Cluster Configuration

```yaml
# elasticsearch.yml
cluster.name: my-cluster
node.name: node-1
path.data: /var/lib/elasticsearch
path.logs: /var/log/elasticsearch
network.host: 0.0.0.0
http.port: 9200
discovery.seed_hosts: ["host1:9300", "host2:9300", "host3:9300"]
cluster.initial_master_nodes: ["node-1", "node-2", "node-3"]
xpack.security.enabled: true
xpack.security.http.ssl.enabled: false
xpack.security.transport.ssl.enabled: false
```

## Index Management

### Creating Indices

```bash
# Create index with default settings
curl -X PUT "localhost:9200/products" -H 'Content-Type: application/json' -d'
{
  "settings": {
    "number_of_shards": 3,
    "number_of_replicas": 1
  }
}'

# Create index with mappings
curl -X PUT "localhost:9200/ecommerce" -H 'Content-Type: application/json' -d'
{
  "settings": {
    "number_of_shards": 2,
    "number_of_replicas": 1,
    "analysis": {
      "analyzer": {
        "my_analyzer": {
          "type": "custom",
          "tokenizer": "standard",
          "filter": ["lowercase", "stop"]
        }
      }
    }
  },
  "mappings": {
    "properties": {
      "title": {
        "type": "text",
        "analyzer": "my_analyzer",
        "fields": {
          "keyword": {
            "type": "keyword",
            "ignore_above": 256
          }
        }
      },
      "description": {
        "type": "text",
        "analyzer": "my_analyzer"
      },
      "price": {
        "type": "scaled_float",
        "scaling_factor": 100
      },
      "category": {
        "type": "keyword"
      },
      "tags": {
        "type": "keyword"
      },
      "location": {
        "type": "geo_point"
      },
      "created_at": {
        "type": "date",
        "format": "yyyy-MM-dd HH:mm:ss||yyyy-MM-dd||epoch_millis"
      }
    }
  }
}'
```

### Index Templates

```bash
# Create index template
curl -X PUT "localhost:9200/_template/logs_template" -H 'Content-Type: application/json' -d'
{
  "index_patterns": ["logs-*"],
  "settings": {
    "number_of_shards": 2,
    "number_of_replicas": 1,
    "refresh_interval": "30s"
  },
  "mappings": {
    "properties": {
      "@timestamp": {
        "type": "date"
      },
      "level": {
        "type": "keyword"
      },
      "message": {
        "type": "text"
      },
      "service": {
        "type": "keyword"
      },
      "host": {
        "type": "keyword"
      }
    }
  }
}'

# Create component template
curl -X PUT "localhost:9200/_component_template/settings_template" -H 'Content-Type: application/json' -d'
{
  "template": {
    "settings": {
      "number_of_shards": 1,
      "number_of_replicas": 0,
      "refresh_interval": "10s"
    }
  }
}'

# Create index template using component templates
curl -X PUT "localhost:9200/_index_template/metrics_template" -H 'Content-Type: application/json' -d'
{
  "index_patterns": ["metrics-*"],
  "template": {
    "settings": {
      "number_of_shards": 1,
      "number_of_replicas": 0
    },
    "mappings": {
      "properties": {
        "@timestamp": {
          "type": "date"
        },
        "metric": {
          "type": "keyword"
        },
        "value": {
          "type": "double"
        },
        "tags": {
          "type": "object"
        }
      }
    }
  },
  "composed_of": ["settings_template"]
}'
```

### Index Operations

```bash
# Get index information
curl -X GET "localhost:9200/products"

# List all indices
curl -X GET "localhost:9200/_cat/indices?v"

# Get index settings
curl -X GET "localhost:9200/products/_settings"

# Get index mappings
curl -X GET "localhost:9200/products/_mappings"

# Update index settings
curl -X PUT "localhost:9200/products/_settings" -H 'Content-Type: application/json' -d'
{
  "index": {
    "refresh_interval": "10s",
    "number_of_replicas": 2
  }
}'

# Close index
curl -X POST "localhost:9200/products/_close"

# Open index
curl -X POST "localhost:9200/products/_open"

# Delete index
curl -X DELETE "localhost:9200/products"

# Force merge index
curl -X POST "localhost:9200/products/_forcemerge?max_num_segments=1"

# Shrink index
curl -X POST "localhost:9200/products/_shrink/products_small" -H 'Content-Type: application/json' -d'
{
  "settings": {
    "index.number_of_shards": 1
  }
}'
```

## Document Operations

### CRUD Operations

```bash
# Create document with auto-generated ID
curl -X POST "localhost:9200/products/_doc" -H 'Content-Type: application/json' -d'
{
  "name": "Wireless Headphones",
  "brand": "AudioTech",
  "price": 199.99,
  "category": "Electronics",
  "tags": ["wireless", "bluetooth", "music"],
  "created_at": "2023-01-15T10:30:00Z"
}'

# Create document with specific ID
curl -X PUT "localhost:9200/products/_doc/1" -H 'Content-Type: application/json' -d'
{
  "name": "Bluetooth Speaker",
  "brand": "SoundMax",
  "price": 79.99,
  "category": "Electronics",
  "tags": ["bluetooth", "portable", "waterproof"],
  "created_at": "2023-01-16T14:20:00Z"
}'

# Get document
curl -X GET "localhost:9200/products/_doc/1"

# Update document (full replacement)
curl -X PUT "localhost:9200/products/_doc/1" -H 'Content-Type: application/json' -d'
{
  "name": "Bluetooth Speaker Pro",
  "brand": "SoundMax",
  "price": 99.99,
  "category": "Electronics",
  "tags": ["bluetooth", "portable", "waterproof", "premium"],
  "created_at": "2023-01-16T14:20:00Z",
  "updated_at": "2023-01-20T09:15:00Z"
}'

# Partial update
curl -X POST "localhost:9200/products/_update/1" -H 'Content-Type: application/json' -d'
{
  "doc": {
    "price": 89.99,
    "tags": ["bluetooth", "portable", "waterproof", "premium", "sale"],
    "updated_at": "2023-01-21T11:30:00Z"
  }
}'

# Delete document
curl -X DELETE "localhost:9200/products/_doc/1"

# Bulk operations
curl -X POST "localhost:9200/_bulk" -H 'Content-Type: application/x-ndjson' -d'
{ "index": { "_index": "products", "_id": "1" } }
{ "name": "Laptop", "brand": "TechCorp", "price": 1299.99, "category": "Electronics" }
{ "index": { "_index": "products", "_id": "2" } }
{ "name": "Mouse", "brand": "InputDev", "price": 29.99, "category": "Electronics" }
{ "delete": { "_index": "products", "_id": "1" } }
{ "update": { "_index": "products", "_id": "2" } }
{ "doc": { "price": 24.99 } }
'
```

### Batch Processing

```javascript
const { Client } = require('@elastic/elasticsearch');

const client = new Client({ node: 'http://localhost:9200' });

// Bulk indexing with Node.js client
async function bulkIndex() {
  const dataset = [
    { id: 1, name: 'Product A', price: 10.99 },
    { id: 2, name: 'Product B', price: 15.49 },
    { id: 3, name: 'Product C', price: 8.99 }
  ];

  const body = dataset.flatMap(doc => [
    { index: { _index: 'products', _id: doc.id } },
    doc
  ]);

  const { body: bulkResponse } = await client.bulk({ body });

  if (bulkResponse.errors) {
    console.log('Bulk indexing had errors');
    bulkResponse.items.forEach(item => {
      if (item.index && item.index.error) {
        console.log(item.index.error);
      }
    });
  } else {
    console.log(`Successfully indexed ${dataset.length} documents`);
  }
}

// Scroll API for large result sets
async function scrollSearch() {
  const { body } = await client.search({
    index: 'products',
    scroll: '1m', // Keep search context alive for 1 minute
    size: 1000,
    body: {
      query: {
        match_all: {}
      }
    }
  });

  let scrollId = body._scroll_id;
  let results = body.hits.hits;

  while (results.length > 0) {
    console.log(`Processing ${results.length} documents`);

    // Process results here
    results.forEach(hit => {
      console.log(hit._source);
    });

    // Get next batch
    const scrollResponse = await client.scroll({
      scroll_id: scrollId,
      scroll: '1m'
    });

    scrollId = scrollResponse.body._scroll_id;
    results = scrollResponse.body.hits.hits;
  }

  // Clear scroll context
  await client.clearScroll({ scroll_id: scrollId });
}
```

## Search Operations

### Basic Search

```bash
# Search all documents
curl -X GET "localhost:9200/products/_search?pretty"

# Search with query string
curl -X GET "localhost:9200/products/_search?q=wireless&pretty"

# Search in specific field
curl -X GET "localhost:9200/products/_search?q=category:Electronics&pretty"

# Search with JSON query
curl -X GET "localhost:9200/products/_search" -H 'Content-Type: application/json' -d'
{
  "query": {
    "match": {
      "name": "wireless headphones"
    }
  }
}'

# Search with filters
curl -X GET "localhost:9200/products/_search" -H 'Content-Type: application/json' -d'
{
  "query": {
    "bool": {
      "must": [
        { "match": { "category": "Electronics" } }
      ],
      "filter": [
        { "range": { "price": { "gte": 50, "lte": 200 } } }
      ]
    }
  }
}'

# Search with pagination
curl -X GET "localhost:9200/products/_search" -H 'Content-Type: application/json' -d'
{
  "from": 0,
  "size": 10,
  "query": {
    "match_all": {}
  }
}'

# Search with sorting
curl -X GET "localhost:9200/products/_search" -H 'Content-Type: application/json' -d'
{
  "query": {
    "match_all": {}
  },
  "sort": [
    { "price": { "order": "desc" } },
    { "_score": { "order": "desc" } }
  ]
}'
```

### Advanced Search Queries

```bash
# Full-text search
curl -X GET "localhost:9200/products/_search" -H 'Content-Type: application/json' -d'
{
  "query": {
    "multi_match": {
      "query": "wireless bluetooth",
      "fields": ["name", "description", "tags"],
      "type": "best_fields"
    }
  }
}'

# Fuzzy search
curl -X GET "localhost:9200/products/_search" -H 'Content-Type: application/json' -d'
{
  "query": {
    "fuzzy": {
      "name": {
        "value": "headphones",
        "fuzziness": "AUTO"
      }
    }
  }
}'

# Phrase search
curl -X GET "localhost:9200/products/_search" -H 'Content-Type: application/json' -d'
{
  "query": {
    "match_phrase": {
      "description": "wireless headphones"
    }
  }
}'

# Wildcard search
curl -X GET "localhost:9200/products/_search" -H 'Content-Type: application/json' -d'
{
  "query": {
    "wildcard": {
      "name": "head*"
    }
  }
}'

# Regular expression search
curl -X GET "localhost:9200/products/_search" -H 'Content-Type: application/json' -d'
{
  "query": {
    "regexp": {
      "name": "headphones|earbuds"
    }
  }
}'

# Geospatial search
curl -X GET "localhost:9200/products/_search" -H 'Content-Type: application/json' -d'
{
  "query": {
    "bool": {
      "must": {
        "match_all": {}
      },
      "filter": {
        "geo_distance": {
          "distance": "100km",
          "location": {
            "lat": 40.7128,
            "lon": -74.0060
          }
        }
      }
    }
  }
}'

# Date range search
curl -X GET "localhost:9200/products/_search" -H 'Content-Type: application/json' -d'
{
  "query": {
    "range": {
      "created_at": {
        "gte": "2023-01-01",
        "lte": "2023-12-31",
        "format": "yyyy-MM-dd"
      }
    }
  }
}'

# Nested query
curl -X GET "localhost:9200/products/_search" -H 'Content-Type: application/json' -d'
{
  "query": {
    "nested": {
      "path": "reviews",
      "query": {
        "bool": {
          "must": [
            { "match": { "reviews.rating": 5 } },
            { "range": { "reviews.date": { "gte": "2023-01-01" } } }
          ]
        }
      }
    }
  }
}'
```

### Aggregations

```bash
# Terms aggregation
curl -X GET "localhost:9200/products/_search" -H 'Content-Type: application/json' -d'
{
  "size": 0,
  "aggs": {
    "categories": {
      "terms": {
        "field": "category",
        "size": 10
      }
    }
  }
}'

# Range aggregation
curl -X GET "localhost:9200/products/_search" -H 'Content-Type: application/json' -d'
{
  "size": 0,
  "aggs": {
    "price_ranges": {
      "range": {
        "field": "price",
        "ranges": [
          { "to": 50 },
          { "from": 50, "to": 100 },
          { "from": 100, "to": 200 },
          { "from": 200 }
        ]
      }
    }
  }
}'

# Date histogram aggregation
curl -X GET "localhost:9200/products/_search" -H 'Content-Type: application/json' -d'
{
  "size": 0,
  "aggs": {
    "sales_over_time": {
      "date_histogram": {
        "field": "created_at",
        "calendar_interval": "month",
        "format": "yyyy-MM"
      }
    }
  }
}'

# Metrics aggregations
curl -X GET "localhost:9200/products/_search" -H 'Content-Type: application/json' -d'
{
  "size": 0,
  "aggs": {
    "price_stats": {
      "stats": {
        "field": "price"
      }
    },
    "avg_price": {
      "avg": {
        "field": "price"
      }
    },
    "price_percentiles": {
      "percentiles": {
        "field": "price",
        "percents": [25, 50, 75, 95]
      }
    }
  }
}'

# Nested aggregations
curl -X GET "localhost:9200/products/_search" -H 'Content-Type: application/json' -d'
{
  "size": 0,
  "aggs": {
    "categories": {
      "terms": {
        "field": "category"
      },
      "aggs": {
        "avg_price": {
          "avg": {
            "field": "price"
          }
        },
        "price_ranges": {
          "range": {
            "field": "price",
            "ranges": [
              { "to": 50 },
              { "from": 50, "to": 100 },
              { "from": 100 }
            ]
          }
        }
      }
    }
  }
}'

# Pipeline aggregations
curl -X GET "localhost:9200/sales/_search" -H 'Content-Type: application/json' -d'
{
  "size": 0,
  "aggs": {
    "monthly_sales": {
      "date_histogram": {
        "field": "date",
        "calendar_interval": "month"
      },
      "aggs": {
        "total_sales": {
          "sum": {
            "field": "amount"
          }
        },
        "moving_avg": {
          "moving_avg": {
            "buckets_path": "total_sales",
            "window": 3
          }
        }
      }
    }
  }
}'
```

## Analysis and Tokenization

### Analyzers

```bash
# Create custom analyzer
curl -X PUT "localhost:9200/products" -H 'Content-Type: application/json' -d'
{
  "settings": {
    "analysis": {
      "analyzer": {
        "product_analyzer": {
          "type": "custom",
          "tokenizer": "standard",
          "filter": [
            "lowercase",
            "stop",
            "porter_stem"
          ]
        },
        "keyword_analyzer": {
          "type": "custom",
          "tokenizer": "keyword",
          "filter": [
            "lowercase"
          ]
        }
      },
      "filter": {
        "my_stop": {
          "type": "stop",
          "stopwords": ["a", "an", "and", "the"]
        }
      }
    }
  },
  "mappings": {
    "properties": {
      "name": {
        "type": "text",
        "analyzer": "product_analyzer",
        "fields": {
          "keyword": {
            "type": "keyword"
          }
        }
      },
      "brand": {
        "type": "text",
        "analyzer": "keyword_analyzer"
      }
    }
  }
}'

# Test analyzer
curl -X GET "localhost:9200/products/_analyze" -H 'Content-Type: application/json' -d'
{
  "analyzer": "product_analyzer",
  "text": "The quick brown fox jumps over the lazy dog"
}'

# Test tokenizer
curl -X GET "localhost:9200/_analyze" -H 'Content-Type: application/json' -d'
{
  "tokenizer": "standard",
  "filter": ["lowercase"],
  "text": "Elasticsearch is awesome!"
}'
```

## Cluster Management

### Cluster Health

```bash
# Get cluster health
curl -X GET "localhost:9200/_cluster/health?pretty"

# Get cluster state
curl -X GET "localhost:9200/_cluster/state?pretty"

# Get cluster settings
curl -X GET "localhost:9200/_cluster/settings?pretty"

# Update cluster settings
curl -X PUT "localhost:9200/_cluster/settings" -H 'Content-Type: application/json' -d'
{
  "persistent": {
    "cluster.routing.allocation.enable": "all"
  },
  "transient": {
    "cluster.routing.allocation.enable": "primaries"
  }
}'

# Get node information
curl -X GET "localhost:9200/_nodes?pretty"

# Get node stats
curl -X GET "localhost:9200/_nodes/stats?pretty"
```

### Index Lifecycle Management

```bash
# Create ILM policy
curl -X PUT "localhost:9200/_ilm/policy/logs_policy" -H 'Content-Type: application/json' -d'
{
  "policy": {
    "phases": {
      "hot": {
        "min_age": "0ms",
        "actions": {
          "rollover": {
            "max_size": "50gb",
            "max_age": "30d"
          },
          "set_priority": {
            "priority": 100
          }
        }
      },
      "warm": {
        "min_age": "30d",
        "actions": {
          "allocate": {
            "number_of_replicas": 1
          },
          "shrink": {
            "number_of_shards": 1
          },
          "set_priority": {
            "priority": 50
          }
        }
      },
      "cold": {
        "min_age": "60d",
        "actions": {
          "allocate": {
            "number_of_replicas": 0
          },
          "set_priority": {
            "priority": 0
          }
        }
      },
      "delete": {
        "min_age": "90d",
        "actions": {
          "delete": {}
        }
      }
    }
  }
}'

# Apply policy to index template
curl -X PUT "localhost:9200/_template/logs_template" -H 'Content-Type: application/json' -d'
{
  "index_patterns": ["logs-*"],
  "settings": {
    "index.lifecycle.name": "logs_policy",
    "index.lifecycle.rollover_alias": "logs"
  }
}'

# Manual rollover
curl -X POST "localhost:9200/logs/_rollover" -H 'Content-Type: application/json' -d'
{
  "conditions": {
    "max_age": "7d",
    "max_size": "5gb"
  }
}'
```

## Security

### Authentication and Authorization

```bash
# Enable security
curl -X POST "localhost:9200/_security/user/elastic/_password" -H 'Content-Type: application/json' -d'
{
  "password": "new_password"
}'

# Create user
curl -X POST "localhost:9200/_security/user/app_user" -u elastic:new_password -H 'Content-Type: application/json' -d'
{
  "password": "user_password",
  "roles": ["app_role"],
  "full_name": "Application User",
  "email": "app@example.com"
}'

# Create role
curl -X POST "localhost:9200/_security/role/app_role" -u elastic:new_password -H 'Content-Type: application/json' -d'
{
  "cluster": ["manage_index_templates"],
  "indices": [
    {
      "names": ["products", "logs-*"],
      "privileges": ["create_index", "index", "read", "search"]
    }
  ]
}'

# Get user information
curl -X GET "localhost:9200/_security/user" -u elastic:new_password

# Change password
curl -X POST "localhost:9200/_security/user/app_user/_password" -u elastic:new_password -H 'Content-Type: application/json' -d'
{
  "password": "new_user_password"
}'
```

## Monitoring and Performance

### Performance Tuning

```bash
# Get index statistics
curl -X GET "localhost:9200/products/_stats?pretty"

# Get search performance
curl -X GET "localhost:9200/_nodes/stats/indices/search?pretty"

# Get indexing performance
curl -X GET "localhost:9200/_nodes/stats/indices/indexing?pretty"

# Profile search query
curl -X GET "localhost:9200/products/_search" -H 'Content-Type: application/json' -d'
{
  "profile": true,
  "query": {
    "match": {
      "name": "wireless"
    }
  }
}'

# Get hot threads
curl -X GET "localhost:9200/_nodes/hot_threads?pretty"

# Get pending tasks
curl -X GET "localhost:9200/_cluster/pending_tasks?pretty"
```

### Backup and Recovery

```bash
# Create snapshot repository
curl -X PUT "localhost:9200/_snapshot/my_backup" -H 'Content-Type: application/json' -d'
{
  "type": "fs",
  "settings": {
    "location": "/mnt/backup/elasticsearch",
    "compress": true
  }
}'

# Create snapshot
curl -X PUT "localhost:9200/_snapshot/my_backup/snapshot_1?wait_for_completion=true" -H 'Content-Type: application/json' -d'
{
  "indices": "products,logs-*",
  "ignore_unavailable": true,
  "include_global_state": false
}'

# List snapshots
curl -X GET "localhost:9200/_snapshot/my_backup/_all?pretty"

# Restore snapshot
curl -X POST "localhost:9200/_snapshot/my_backup/snapshot_1/_restore?wait_for_completion=true" -H 'Content-Type: application/json' -d'
{
  "indices": "products",
  "ignore_unavailable": true,
  "include_global_state": false
}'

# Delete snapshot
curl -X DELETE "localhost:9200/_snapshot/my_backup/snapshot_1"
```

## Integration with Other Tools

### Logstash Integration

```ruby
# logstash.conf
input {
  file {
    path => "/var/log/application/*.log"
    start_position => "beginning"
  }
}

filter {
  grok {
    match => { "message" => "%{TIMESTAMP_ISO8601:timestamp} %{LOGLEVEL:level} %{DATA:service} %{GREEDYDATA:message}" }
  }
  
  date {
    match => ["timestamp", "ISO8601"]
  }
}

output {
  elasticsearch {
    hosts => ["localhost:9200"]
    index => "logs-%{+YYYY.MM.dd}"
    user => "elastic"
    password => "password"
  }
}
```

### Kibana Integration

```bash
# Create index pattern
curl -X POST "localhost:5601/api/saved_objects/index-pattern" -H 'Content-Type: application/json' -H 'kbn-xsrf: true' -d'
{
  "attributes": {
    "title": "products",
    "timeFieldName": "created_at"
  }
}'

# Create visualization
curl -X POST "localhost:5601/api/saved_objects/visualization" -H 'Content-Type: application/json' -H 'kbn-xsrf: true' -d'
{
  "attributes": {
    "title": "Product Categories",
    "visState": "{\"type\":\"pie\",\"params\":{\"addTooltip\":true,\"addLegend\":true,\"legendPosition\":\"right\",\"isDonut\":true},\"aggs\":[{\"id\":\"1\",\"enabled\":true,\"type\":\"count\",\"schema\":\"metric\",\"params\":{}},{\"id\":\"2\",\"enabled\":true,\"type\":\"terms\",\"schema\":\"segment\",\"params\":{\"field\":\"category\",\"orderBy\":\"1\",\"order\":\"desc\",\"size\":5,\"otherBucket\":false,\"otherBucketLabel\":\"Other\",\"missingBucket\":false,\"missingBucketLabel\":\"Missing\"}}]}",
    "uiStateJSON": "{}",
    "description": "",
    "version": 1,
    "kibanaSavedObjectMeta": {
      "searchSourceJSON": "{\"index\":\"products\",\"filter\":[],\"query\":{\"query\":\"\",\"language\":\"lucene\"}}"
    }
  }
}'
```

This comprehensive guide covers Elasticsearch from basic operations to advanced features including search, aggregations, cluster management, security, and performance optimization.