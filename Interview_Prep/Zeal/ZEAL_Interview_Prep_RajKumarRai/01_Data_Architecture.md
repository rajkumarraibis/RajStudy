
# **Data Architecture**

As a Lead Data Engineer at Freeletics, I’ve designed and maintained a **cloud-native, modern data platform** built on **AWS, Databricks, and S3**, combining principles from **Lambda Architecture**, **Medallion Architecture**, and the **Delta Lakehouse paradigm**.
My design philosophy focuses on **scalability, modularity, and DataOps-driven automation**.

### **Architecture Overview**

The platform follows a hybrid **Lambda + Medallion** approach:

* **Lambda layer:**
  Application and backend services stream data via **Kinesis** into **AWS Step Functions** and **Lambda** workflows, which deliver data to both **Amplitude** (for analytics) and **S3** (Bronze & Silver layers).
  This ensures **low-latency event capture** and **reliable batch persistence**.

* **Medallion / Delta Lakehouse layer:**
  From S3 (Bronze/Silver), **Databricks Spark jobs** transform, enrich, and write curated data into **Gold Delta Tables**, forming the **Delta Lakehouse**.
  Dashboards and analytics run directly on these **Gold Delta tables** using **Databricks SQL**.

* **Governance and Metadata:**
  The entire ecosystem is managed through **Unity Catalog** for **data dictionary**, **data discovery**, and **lineage tracking**, ensuring consistency and compliance.

* **Architecture Principles:**
  Every component is **modular and loosely coupled**, enabling independent scaling and simpler maintenance.
  The architecture supports both **real-time streaming** and **batch workloads**, enabling a unified analytical layer.

* **Data Warehousing:**
  Our data warehouse is built on **Delta Lake**; however, I’m also comfortable with **Amazon Redshift** for traditional DWH workloads when needed.

---

### **Key Points**

* **Ingestion Layer:** Multi-source ingestion from Braze, Apple transactions, Amplitude, and internal microservices via Lambda + Kinesis into S3.
* **Processing Layer:** Databricks jobs (Spark) handle enrichment, aggregation, and schema evolution; parallel DynamoDB lookups for enrichment.
* **Storage Layer:** Bronze → Silver → Gold layers organized in S3, stored as Delta tables for performance and versioning.
* **Serving Layer:** Consumers access through Databricks SQL, Athena, or APIs for analytics and ML use cases.
* **Governance:** Unity Catalog manages access, lineage, and metadata; tagging and versioning enforced across all layers.

---

### **What I’d Highlight to Christian**

This architecture embodies ZEAL’s **Modern Data Stack philosophy** — decoupled ingestion (Kafka/Kinesis), modular transformation (dbt/Spark), and scalable serving (Redshift/Snowflake).
It’s built with a strong **DataOps foundation**, emphasizing **reliability**, **observability**, and **cost efficiency** while enabling analytics, experimentation, and ML at scale.

