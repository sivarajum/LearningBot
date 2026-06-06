# Google BigQuery

## Overview

Google BigQuery is a fully managed, serverless data warehouse that enables scalable analysis over petabytes of data. It is part of the Google Cloud Platform and supports SQL queries with extremely fast performance using a columnar storage format and tree architecture called Dremel.

## Key Features

- **Serverless Architecture**: No infrastructure to manage. BigQuery automatically scales compute resources based on query complexity.
- **Columnar Storage**: Data is stored in a columnar format, which is highly efficient for analytical queries that scan specific columns across large datasets.
- **Standard SQL**: Supports ANSI SQL, making it accessible for analysts and engineers already familiar with SQL.
- **Streaming Inserts**: Real-time data ingestion via streaming inserts, enabling near real-time analytics.
- **Machine Learning (BQML)**: Build and deploy ML models directly in BigQuery using SQL with BigQuery ML.

## Common Use Cases

1. **Data Warehousing**: Centralized repository for structured and semi-structured data from multiple sources.
2. **Business Intelligence**: Power dashboards and reports using tools like Looker, Data Studio, or Tableau.
3. **Log Analytics**: Analyze application logs, clickstream data, and IoT sensor data at scale.
4. **Machine Learning**: Train classification, regression, and clustering models using BQML without moving data.

## Pricing Model

BigQuery uses a pay-per-query pricing model. You are charged based on the amount of data scanned by your queries. Storage costs are separate and based on the volume of data stored. Flat-rate pricing is also available for predictable workloads.

## Integration Points

BigQuery integrates with Apache Airflow for orchestration, dbt for data transformation, Dataflow for stream processing, and Pub/Sub for event-driven architectures. It also connects to Vertex AI for advanced ML workflows.
