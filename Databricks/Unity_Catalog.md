## 🧠 Databricks Unity Catalog – Markdown Revision Guide

Perfect for quick interview prep, this markdown guide distills core concepts, object model, setup, security, lineage, sharing, and more—sourced from the Databricks website, official docs, and a technical YouTube deep‑dive video.
Check out the video for demos and insights:

[A Technical Deep Dive into Unity Catalog’s Practitioner Playbook](https://www.youtube.com/watch?v=vwIujIbqEKQ&utm_source=chatgpt.com)

---

### ## 1. What Is Unity Catalog?

* Unity Catalog is a **centralized metadata and governance layer** across your Databricks workspaces for structured/unstructured data, metrics, AI models, notebooks, dashboards and more ([Databricks Documentation][1], [Databricks][2]).
* Enables **data discovery**, **auditing**, **access control**, **automated lineage**, and **data quality monitoring** ([Databricks Documentation][1]).
* Works across open formats like Delta Lake, Apache Iceberg, Hudi, Parquet, with full interoperability via open APIs ([Databricks][2]).

---

### ## FEATURES

## Data and AI Catalog
<img src="/images/uc-feature-image-1.png" alt="Data and AI Catalog" style="width:80%"/>
Unified catalog for all structured data, unstructured data, business metrics and AI models across open data formats like Delta Lake, Apache Iceberg, Hudi, Parquet and more.

add more features from
https://www.databricks.com/product/unity-catalog#features
---

### ## 2. Object Model & Terminology

* A **metastore** is the top-level metadata container — one per region, shared across workspaces ([Databricks Documentation][1]).
* Hierarchy:

  ```
  Metastore → Catalog → Schema (Database) → Table / View / Volume / Model / Function
  ```
* Tables can be **managed** (full lifecycle managed by Unity Catalog) or **external** (data stored externally but governed via UC) ([Databricks Documentation][1]).
* Other securable objects: **storage credentials**, **external locations**, **connections**, and **service credentials** — used for enabling secure access to data sources and external assets ([Databricks Documentation][1]).

---

### ## 3. Setup & Requirements

1. **Enable Unity Catalog:**

   * New workspaces created after Nov 2023 are auto-enabled ([Databricks Documentation][3]).
   * Older workspaces need manual enablement: create metastore, attach it, convert groups to account-level groups ([Databricks Documentation][3]).
2. **Permissions:**

   * Admins must be **account‑level or metastore admins**; workspace admins can manage UC if auto-enabled ([Databricks Documentation][3]).
3. **Compute prerequisites:**

   * Clusters must run on Databricks Runtime **11.3 LTS+**, use standard or dedicated access modes ([Databricks Documentation][1]).
   * SQL warehouses fully supported by default.
4. **File formats:**

   * Managed tables: `delta`.
   * External tables: `delta`, `csv`, `json`, `avro`, `parquet`, `ORC`, `text` ([Databricks Documentation][1]).

---

### ## 4. Access Control & Governance

* **Role-based access control (RBAC)** with ANSI SQL–based grants; supports row- and column-level policies, with auto‑classification for sensitive data like PII ([Databricks][2]).
* **Audit logging:** Captures user-level operations across languages & workloads; available via system tables in metastore ([Databricks Documentation][1]).
* **Lineage:** Automated, real-time lineage captured at table- and column-level, across SQL/Python/Scala/R and even AI assets. Available via UI or REST APIs for integration ([Databricks][4]).

---

### ## 5. Data Discovery & Business Context

* **Catalog Explorer** UI enables search, tagging, documentation, and previews—permission‑scoped for users ([advancinganalytics.co.uk][5]).
* **Business Metrics Registry:** Define and govern metrics in UC so BI/AI teams use consistent business logic ([Databricks][2]).
* **AI‑powered documentation & natural‑language search:** Helps technical and business users to find and understand data faster ([Databricks][2]).

---

### ## 6. Data Sharing & Federation

* **Delta Sharing:** Secure, live data sharing across organizations, regions, or clouds—without replication. Works with Unity Catalog governance policies ([Databricks][2]).
* **Lakehouse Federation:** Govern and query data residing in external sources (MySQL, PostgreSQL, Snowflake, Redshift, BigQuery, SAP, Hive, Glue, Azure SQL, etc.) without migration ([Databricks][2]).

---

### ## 7. Comparing with Traditional Catalogs

* Unity Catalog acts as a **“super-metastore”** tightly integrated with Databricks runtime—offering governance, lineage, and access control without third-party tools like Collibra or Alation ([Reddit][6]).
* While not as full-featured as enterprise governance suites, it covers core needs within Databricks and now open-sources core UC functionality too.

---

### ## 8. Quick SQL Examples

```sql
-- Grant schema creation rights at catalog level
GRANT CREATE SCHEMA ON catalog_name TO `data-team`;

-- Query which metastore is active
SELECT CURRENT_METASTORE();

-- Create a table in Unity Catalog
CREATE TABLE catalog_name.schema_name.table_name (
  id INT,
  name STRING
);

-- Fine‑grained access
GRANT SELECT (id) ON catalog_name.schema_name.table_name TO `reports_role`;
```

*(Use backticks and lowercase-only object names due to naming constraints)* ([Databricks Documentation][1])

---

### ## 📋 Summary Table

| Dimension                | Unity Catalog Highlights                                      |
| ------------------------ | ------------------------------------------------------------- |
| **Metadata governance**  | Centralized across region, workspace‑agnostic                 |
| **Access control**       | Fine‑grained row/column-level, RBAC, PII auto-classification  |
| **Lineage & auditing**   | Automatic, cross-language, visible via system tables and APIs |
| **Discovery**            | Search, tagging, business semantics, natural‑language support |
| **Sharing & federation** | Delta Sharing + federation across external data stores        |
| **Setup requirements**   | Premium plan, Runtime ≥11.3, supported compute modes          |

---

### 💡 Interview Tips

* Emphasize UC’s integration with the **lakehouse architecture** and **attributes-based access**.
* Be ready to discuss **object model**, **metastore structure**, and **interop with external systems via federation and Delta Sharing**.
* Explain how **lineage, audit, and metrics** support compliance and trustworthy analytics pipelines.
* Mention **new open‑source edition** of Unity Catalog and UCX utilities for migration and automation ([Databricks Documentation][1], [Databricks][2], [advancinganalytics.co.uk][5], [Microsoft Learn][7], [Medium][8], [Databricks Documentation][3]).

---

### 🧩 Visual Diagram Description

*(Image above)* depicts the metadata architecture: Metastore at the top level, branching into multiple catalogs → schemas → data assets (tables, views, volumes, models). It also shows securable objects like external locations and credentials alongside shared data sources federated in.

---

Use this reference to review quickly before your interviews—feel free to ask follow‑ups on any section!

[1]: https://docs.databricks.com/aws/en/data-governance/unity-catalog/?utm_source=chatgpt.com "What is Unity Catalog? - Databricks Documentation"
[2]: https://www.databricks.com/product/unity-catalog?utm_source=chatgpt.com "Unity Catalog | Databricks"
[3]: https://docs.databricks.com/aws/en/data-governance/unity-catalog/get-started?utm_source=chatgpt.com "Get started with Unity Catalog - Databricks Documentation"
[4]: https://www.databricks.com/resources/demos/videos/data-governance/unity-catalog-overview?utm_source=chatgpt.com "Unified Governance for All Data and AI Assets - Databricks"
[5]: https://www.advancinganalytics.co.uk/blog/2024/2/5/guide-to-databricks-unity-catalog?utm_source=chatgpt.com "An Ultimate Guide to Databricks Unity Catalog - Advancing Analytics"
[6]: https://www.reddit.com/r/dataengineering/comments/1dgfm2m/can_someone_explain_unity_catalog_from_first/?utm_source=chatgpt.com "Can someone explain unity catalog from first principles? Is there a ..."
[7]: https://learn.microsoft.com/en-us/azure/databricks/data-governance/unity-catalog/?utm_source=chatgpt.com "What is Unity Catalog? - Azure Databricks | Microsoft Learn"
[8]: https://oindrila-chakraborty88.medium.com/introduction-to-unity-catalog-in-databricks-214980333008?utm_source=chatgpt.com "Introduction to Unity Catalog in Databricks | by Oindrila Chakraborty"
