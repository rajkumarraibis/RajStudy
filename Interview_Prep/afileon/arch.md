flowchart LR
  subgraph Tenants
    A1[Tax Firm A<br/>ERP, DMS, CRM]
    A2[Tax Firm B<br/>ERP, DMS, CRM]
    A3[Tax Firm N<br/>Local Systems]
  end

  A1 --> LZ[(Landing Zone<br/>Object Storage<br/>/tenant=A/...)]
  A2 --> LZ
  A3 --> LZ

  subgraph Ingestion
    IG1[Batch Ingestion<br/>ADF / Glue / Autoloader]
    IG2[Streaming Ingestion<br/>Kafka Topics<br/>tenant-aware]
  end

  LZ --> IG1
  IG2 --> DBX

  IG1 --> DBX[Databricks Lakehouse<br/>Delta Bronze/Silver/Gold]

  subgraph Governance
    GOV[Unity Catalog<br/>RBAC, RLS, Lineage, DQ]
  end

  DBX <---> GOV

  DBX --> CH[ClickHouse Cluster<br/>Real-time Analytics DB]
  DBX --> ML[AI & ML on Databricks<br/>Feature Store & Models]

  CH --> BI[Dashboards & Self-Service BI<br/>Per-tenant & Group Views]
  ML --> Apps[AI Apps & APIs<br/>Copilots, Scoring, Recommendations]
