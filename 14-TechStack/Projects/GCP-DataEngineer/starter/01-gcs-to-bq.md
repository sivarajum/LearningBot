# Starter: GCS Ingest to Partitioned BigQuery
- Goal: create bucket, load CSV->BQ partitioned table, verify pruning.
- Steps: gsutil mb; gsutil cp; bq load with --time_partitioning_field; run sample query with bytes processed.
- Validation: table exists with partitions; query bytes < raw scan; docs: commands + output.
