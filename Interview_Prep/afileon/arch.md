## Unified Multi-Tenant Data & AI Platform (Databricks + ClickHouse)

Tenants' Systems (ERP, DMS, CRM, Tax Tools)
    ├── Tax Firm A
    ├── Tax Firm B
    └── Tax Firm N
            |
            v

[ Ingestion Layer ]
    ├── Batch: ADF / AWS Glue / Databricks Autoloader
    ├── Streaming: Kafka (tenant-aware topics)
    └── Metadata: tenant_id, source_system, timestamps
            |
            v

[ Landing Zone (Object Storage: S3 / ADLS) ]
    └── Partitioned by: tenant_id / system / date
            |
            v

[ Databricks Lakehouse (Delta) ]
    ├── Bronze  – Raw, append-only data
    ├── Silver  – Cleaned, standardized domain models
    ├── Gold    – Curated marts, KPIs, AI-ready tables
    ├── ETL/ELT Pipelines via Databricks Workflows
    └── Streaming ETL via Spark Structured Streaming
            |
            |-------> [ AI & ML on Databricks ]
            |            ├── Feature Store
            |            ├── ML/LLM Models
            |            └── Model Registry
            |
            |-------> [ ClickHouse Analytics DB ]
            |            ├── Fast OLAP queries
            |            ├── Tenant-aware schemas
            |            └── Real-time dashboards
            |
            v

[ BI & Apps ]
    ├── Power BI / Tableau / Superset
    ├── Firm-level dashboards (tenant-isolated)
    └── Group-level analytics (aggregated)

[ Governance & Security (Unity Catalog) ]
    ├── RBAC & ACLs
    ├── Row/Column Level Security (tenant_id)
    ├── Auditing, Lineage
    └── Data Quality (DQ checks, SLAs)

