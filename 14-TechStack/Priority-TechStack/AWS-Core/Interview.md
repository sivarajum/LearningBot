# AWS Core Services - Interview Questions (Basic to Advanced)

## 🎯 Interview Preparation Guide

Practice these questions to ace your AWS interviews. Critical for multi-cloud expertise.

---

## 🟢 BASIC LEVEL Questions

### Q1: What are the key AWS services for data workloads?

**Answer:**
"Key AWS services for data:

**Storage:**
- **S3**: Object storage, data lake foundation
- **Redshift**: Data warehouse, SQL analytics

**Processing:**
- **Glue**: Serverless ETL, data catalog
- **EMR**: Managed Spark/Hadoop clusters
- **Lambda**: Serverless functions

**Analytics:**
- **Athena**: Serverless SQL on S3
- **QuickSight**: BI and dashboards

**Orchestration:**
- **Step Functions**: Workflow orchestration

I use S3 as data lake, Glue for ETL, EMR for Spark processing, and Redshift for analytics, creating a complete data platform."

**Key Points:**
- S3 for storage
- Glue for ETL
- EMR for processing
- Redshift for analytics

---

### Q2: How does S3 work as a data lake?

**Answer:**
"S3 is perfect for data lakes because:

**Features:**
- **Scalable**: Unlimited storage
- **Durable**: 99.999999999% durability
- **Cost-effective**: Multiple storage classes
- **Integrated**: Works with all AWS services

**Data Lake Structure:**
```
s3://data-lake/
  raw/          # Raw data
  processed/    # ETL output
  curated/      # Analytics-ready
```

**Benefits:**
- Store any data format
- Schema-on-read
- Cost-effective storage
- Easy integration

I organize data in S3 with clear separation of raw, processed, and curated layers, enabling efficient data processing."

**Key Points:**
- Unlimited storage
- Multiple storage classes
- Schema-on-read
- Cost-effective

---

### Q3: What's the difference between Glue and EMR?

**Answer:**
"**Glue:**
- Serverless ETL service
- Managed Spark environment
- Data catalog included
- Pay per job execution
- Best for: Scheduled ETL jobs

**EMR:**
- Managed Spark/Hadoop clusters
- Full control over cluster
- Pay for cluster uptime
- Best for: Long-running jobs, custom configs

**When to Use:**
- **Glue**: Scheduled ETL, serverless, cost-effective
- **EMR**: Long-running, custom requirements, cost optimization

I use Glue for scheduled ETL jobs and EMR for ad-hoc analysis and long-running Spark jobs."

**Key Points:**
- Glue = Serverless
- EMR = Managed clusters
- Choose based on use case

---

## 🟡 INTERMEDIATE LEVEL Questions

### Q4: How do you optimize AWS data pipeline costs?

**Answer:**
"**1. S3 Storage Classes**
- Standard for frequent access
- Intelligent-Tiering for unknown patterns
- Glacier for archival

**2. Data Compression**
- Use Parquet format
- 70-90% size reduction
- Faster queries

**3. Partitioning**
- Partition by date/category
- Reduce data scanned
- Lower Athena costs

**4. Right-Sizing**
- Choose appropriate instance types
- Use spot instances for EMR
- Auto-scaling

**5. Lifecycle Policies**
- Move to cheaper storage
- Delete old data
- Automated management

**6. Athena Optimization**
- Use columnar formats
- Partition data
- Limit data scanned

I optimize costs by using Parquet, partitioning, lifecycle policies, and right-sizing, reducing costs by 60%."

**Key Points:**
- Storage classes
- Compression
- Partitioning
- Right-sizing
- Lifecycle policies

---

### Q5: How do you design a data pipeline on AWS?

**Answer:**
"**Architecture:**

**1. Ingestion**
- S3 for batch data
- Kinesis for streaming
- Lambda for event processing

**2. Storage**
- S3 data lake (raw → processed → curated)
- Redshift for analytics

**3. Processing**
- Glue for ETL
- EMR for Spark
- Lambda for serverless

**4. Orchestration**
- Step Functions for workflows
- EventBridge for scheduling

**5. Analytics**
- Athena for ad-hoc queries
- Redshift for data warehouse
- QuickSight for BI

**Flow:**
```
S3 (Raw) → Glue (ETL) → S3 (Processed) → 
  → Redshift (Analytics) → QuickSight (BI)
```

**Components:**
- S3 data lake
- Glue ETL
- Redshift warehouse
- Step Functions orchestration

This architecture handles petabytes of data with 99.9% reliability."

**Key Points:**
- Multi-layer architecture
- Serverless components
- Scalable design
- Cost-optimized

---

## 🔴 ADVANCED LEVEL Questions

### Q6: How do you handle data security on AWS?

**Answer:**
"**1. Encryption**
- S3: Encryption at rest (SSE-S3, SSE-KMS)
- In transit: TLS/SSL
- Redshift: Encryption enabled

**2. IAM**
- Least privilege access
- Role-based access control
- Service roles for Glue/EMR

**3. VPC**
- Private subnets for resources
- Security groups
- Network ACLs

**4. Monitoring**
- CloudTrail for API logging
- CloudWatch for metrics
- S3 access logging

**5. Data Governance**
- Glue Data Catalog for metadata
- Tagging for compliance
- Lifecycle policies

**Best Practices:**
- Encrypt everything
- Use IAM roles
- Monitor access
- Regular audits

I implement encryption, IAM policies, VPC isolation, and monitoring, ensuring data security and compliance."

**Key Points:**
- Encryption at rest/transit
- IAM policies
- VPC isolation
- Monitoring

---

## 🎯 Key Takeaways

1. **S3 = Data Lake**
2. **Glue = ETL**
3. **EMR = Spark**
4. **Redshift = Warehouse**
5. **Lambda = Serverless**

---

## ✅ Practice Checklist

- [ ] Can explain AWS services in 2 minutes
- [ ] Understand S3 data lake
- [ ] Know Glue vs EMR
- [ ] Understand cost optimization
- [ ] Know security best practices
- [ ] Ready for system design questions

---

**Remember**: AWS is critical for multi-cloud expertise!

