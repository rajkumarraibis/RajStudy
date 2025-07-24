# Medallion Architecture (Databricks)

<img src="/images/building-data-pipelines-with-delta-lake-120823.png" alt="Medallion Architecture Diagram" style="width:80%"/>

## 🔍 What is Medallion Architecture?

The **Medallion Architecture** is a **data design pattern** used in the **lakehouse paradigm** (e.g., Databricks), where data flows through **multiple layers (Bronze → Silver → Gold)**, each increasing in **data quality, structure, and business value**.

It helps ensure:
- Scalability
- Data quality enforcement
- Data lineage and traceability
- Efficient downstream analytics and ML

---

## 🥉 Bronze Layer – Raw / Ingested Data

- Stores **raw, unfiltered data** from source systems.
- Data is typically ingested via **streaming or batch pipelines**.
- Format: **JSON, CSV, Parquet**, or raw Delta.
- Little or no transformation; includes all columns and possible duplicates.

**Use Cases:**
- Archival
- Reprocessing
- Source-of-truth

---

## 🥈 Silver Layer – Cleaned / Refined Data

- Contains **cleaned, filtered, and deduplicated data**.
- Data is **conformed and joined** across sources.
- Ensures **schema enforcement**, data integrity.
- Often includes **business-level entities** (e.g., customers, transactions).

**Use Cases:**
- BI dashboards
- Self-service analytics
- Data science exploration

---

## 🥇 Gold Layer – Business-Level Aggregations

- Optimized for **specific business use cases**.
- Aggregated and enriched metrics (e.g., revenue by region, churn rates).
- Heavily used by **executive dashboards**, **ML models**, **operational systems**.

**Use Cases:**
- KPIs and reports
- AI/ML input tables
- Data apps and APIs

---

## 💡 Benefits of the Medallion Architecture

- **Data Quality Gradients**: Cleaner data as you move from Bronze → Gold.
- **Auditability**: Trace data lineage back to raw sources.
- **Incremental Processing**: Efficient updates using Delta Lake features.
- **Modular & Scalable**: Easy to extend or adapt to new data products.
- **Supports both Batch & Streaming**.

---

## 💡 DETAILS
Building data pipelines with medallion architecture
Databricks provides tools like Lakeflow Declarative Pipelines that allow users to instantly build data pipelines with Bronze, Silver and Gold tables from just a few lines of code. 
And, with streaming tables and materialized views, users can create streaming Lakeflow pipelines built on Apache Spark™️ Structured Streaming that are incrementally refreshed and updated. 
For more details, see Databricks documentation on combining streaming tables and materialized views in a single pipeline.

- **Bronze layer (raw data)**
The Bronze layer is where we land all the data from external source systems. 
The table structures in this layer correspond to the source system table structures "as-is," along with any additional metadata columns that capture the load date/time, process ID, etc. 
The focus in this layer is quick Change Data Capture and the ability to provide an historical archive of source (cold storage), data lineage, auditability, reprocessing if needed without rereading the data from the source system.

- **Silver layer (cleansed and conformed data)**
In the Silver layer of the lakehouse, the data from the Bronze layer is matched, merged, conformed and cleansed ("just-enough") so that the Silver layer can provide an "Enterprise view" of all its key business entities, concepts and transactions.
(e.g. master customers, stores, non-duplicated transactions and cross-reference tables).
The Silver layer brings the data from different sources into an Enterprise view and enables self-service analytics for ad-hoc reporting, advanced analytics and ML. 
It serves as a source for Departmental Analysts, Data Engineers and Data Scientists to further create projects and analysis to answer business problems via enterprise and departmental data projects in the Gold Layer.
In the lakehouse data engineering paradigm, typically the ELT methodology is followed vs. 
ETL - which means only minimal or "just-enough" transformations and data cleansing rules are applied while loading the Silver layer. Speed and agility to ingest and deliver the data in the data lake is prioritized, 
and a lot of project-specific complex transformations and business rules are applied while loading the data from the Silver to Gold layer. From a data modeling perspective, the Silver Layer has more 3rd-Normal Form like data models. 
Data Vault-like, write-performant data models can be used in this layer.

-- **Gold layer (curated business-level tables)**
Data in the Gold layer of the lakehouse is typically organized in consumption-ready "project-specific" databases. 
The Gold layer is for reporting and uses more de-normalized and read-optimized data models with fewer joins. The final layer of data transformations and data quality rules are applied here. 
Final presentation layer of projects such as Customer Analytics, Product Quality Analytics, Inventory Analytics, Customer Segmentation, Product Recommendations, Marking/Sales Analytics etc. 
fit in this layer. We see a lot of Kimball style star schema-based data models or Inmon style Data marts fit in this Gold Layer of the lakehouse.

So you can see that the data is curated as it moves through the different layers of a lakehouse. 
In some cases, we also see that lot of Data Marts and EDWs from the traditional RDBMS technology stack are ingested into the lakehouse, 
so that for the first time Enterprises can do "pan-EDW" advanced analytics and ML - which was just not possible or too cost prohibitive to do on a traditional stack. (e.g. IoT/Manufacturing data is tied with Sales and Marketing data for defect analysis or health care genomics, EMR/HL7 clinical data markets are tied with financial claims data to create a Healthcare Data Lake for timely and improved patient care analytics.)


## 🚀 Best Practices

- Use **Delta Lake** format for all layers (ACID transactions, versioning).
- Implement **schema enforcement** and **evolution**.
- Automate with **workflow orchestration** (e.g., Databricks Jobs, Airflow).
- Apply **data quality rules (expectations)** at Silver layer.
- Use **Unity Catalog or similar** for governance and access control.

---

## 📚 Related Concepts

- Lakehouse Architecture
- Delta Live Tables (DLT)
- Streaming Ingestion (Auto Loader)
- Data Lineage
- RAG + AI with Medallion (Emerging Pattern)

---

## 📌 Final Thought

The Medallion Architecture is not just a best practice — it's a **foundation** for any scalable, governed, and performant lakehouse on platforms like **Databricks**.  
By structuring your pipelines around **Bronze → Silver → Gold**, you can support **real-time, ML, BI, and operational workloads** with confidence.

