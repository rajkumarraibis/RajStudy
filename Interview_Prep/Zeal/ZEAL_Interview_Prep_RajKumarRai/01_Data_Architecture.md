# Data Architecture

As a Lead Data Engineer at Freeletics, I’ve designed and maintained a modern cloud-native data platform built primarily on AWS, Databricks, and S3. My architectural approach focuses on scalability, automation, and DataOps best practices.

## Key Points

- **Ingestion Layer:** Data from multiple sources (Braze, Apple transactions, Amplitude, internal microservices) lands in S3 via Lambda and Kinesis.
- **Processing Layer:** Databricks jobs (Spark) perform enrichment and aggregation. I use job clusters with project tags and parallel fetch logic (e.g., DynamoDB user metadata) to optimize compute.
- **Storage Layer:** Data is structured into Bronze–Silver–Gold layers in S3, optimized for Redshift Spectrum and BI access.
- **Serving Layer:** Analysts and ML teams consume through Athena, Databricks SQL, or APIs.
- **Governance:** Tags, versioning, and logging are strictly enforced across layers.

## What I’d Highlight to Christian

This architecture aligns well with ZEAL’s Modern Data Stack — decoupled ingestion (Kafka/Kinesis), modular transformation (dbt/Spark), and scalable serving (Redshift/Snowflake). My focus has been on reliability, monitoring, and cost optimization while supporting analytics and ML workloads.
