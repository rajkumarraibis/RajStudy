flowchart LR
    %% ================================
    %% Tenants / Source Systems
    %% ================================
    subgraph T[Tenants' Source Systems]
        A1[Tax Firm A<br/>ERP / DMS / CRM]
        A2[Tax Firm B<br/>ERP / DMS / CRM]
        A3[Tax Firm N<br/>Local Systems]
    end

    A1 --> LZ
    A2 --> LZ
    A3 --> LZ

    %% ================================
    %% Ingestion Layer
    %% ================================
    subgraph ING[Ingestion Layer]
        IG1[Batch Ingestion<br/>ADF / Glue / Autoloader]
        IG2[Streaming Ingestion<br/>Kafka (tenant-aware)]
    end

    LZ[(Landing Zone<br/>Object Storage<br/>/tenant=<id>/...)]
    LZ --> IG1
    IG2 --> DBX

    %% ================================
    %% Lakehouse (Bronze/Silver/Gold)
    %% ================================
    subgraph DBX[Databricks Lakehouse<br/>Delta Bronze / Silver / Gold]
        BR[Bronze<br/>Raw Delta Tables]
        SV[Silver<br/>Standardized Data Models]
        GD[Gold<br/>Marts & AI-Ready Tables]
    end

    IG1 --> BR
    BR --> SV
    SV --> GD

    %% ================================
    %% Governance Layer
    %% ================================
    GOV[[Unity Catalog<br/>RBAC • RLS • Lineage • Quality]]

    DBX <--> GOV

    %% ================================
    %% Serving / AI / BI
    %% ================================
    DBX --> CH[ClickHouse Cluster<br/>Real-Time Analytics DB]
    DBX --> ML[AI & ML on Databricks<br/>Feature Store • Models • LLMs]

    CH --> BI[Dashboards & Self-Service BI<br/>Per-Tenant & Group-wide]

    ML --> APP[AI Apps & APIs<br/>Scoring • Recommendations • Copilots]
