**Q1: Why did you choose ADF SAP CDC Connector instead of JDBC or SLT?**
**A:**

* JDBC: Only full extracts, no delta/change awareness → costly & not scalable.
* SLT: Powerful, but adds dependency on SAP Basis team, and licensing/infra overhead.
* ADF CDC: Uses ODP framework with delta queues → near real-time, idempotent, reliable, integrates directly into Azure ecosystem.
* Fits their Azure-first stack (ADLS, Synapse, Purview).

---

---

**Q2: Why Medallion architecture (Bronze/Silver/Gold)? Why not land straight into Gold?**
**A:**

* **Bronze:** Immutable raw capture for auditability + replay.
* **Silver:** Cleansed, deduped, standardized; quality gates applied (GE checks).
* **Gold:** Business-ready aggregates / DV2 hubs & satellites → supports BI & regulatory reporting.
* Skipping layers loses traceability, auditability, and flexibility to reprocess → key for compliance.

---

---

**Q3: How do you handle scalability in your design?**
**A:**

* **Argo + Kubernetes** orchestrates Spark → elastic scaling of jobs.
* Compute decoupled from storage (ADLS) → infinite storage scale.
* Partitioning + incremental CDC ingestion → avoids full reloads.
* Data Vault 2.0 enables scalable modeling (hubs/satellites independent).

---

---

**Q4: How does Purview fit into governance?**
**A:**

* Central catalog for all assets (SAP → ADLS → DV2 → BI).
* End-to-end lineage: which SAP extractor → which Gold/Postgres table → which Tableau dashboard.
* Role-based access via Azure AD integration.
* Sensitivity labeling for PII, crucial for GDPR.
* Equivalent to Unity Catalog (Databricks) or AWS Glue (AWS).

---

---

**Q5: How do you ensure cost control?**
**A:**

* On-demand Spark clusters (no idle cost).
* Lifecycle rules in ADLS (archive/cool tier for Bronze).
* Monitor per-job cost with Azure Cost Monitor.
* Purge/repartition with OPTIMIZE/VACUUM strategies.
* FinOps guardrails → budget alerts, spot usage targets.

---

## 2. **Data Modeling & DV2 (Preethini focus)**

---

**Q6: How do you implement SCD2 in your pipeline?**
**A:**

* In **Silver → Gold** transition:

  * Detect change via hash of descriptive columns.
  * If new values differ → close old record (`_valid_to = ts`, `is_current = false`), insert new (`_valid_from = ts`, `is_current = true`).
  * Implemented via PySpark MERGE for idempotency.
* DV2 satellites are perfect for this (history preservation + audit trail).

---

---

**Q7: How does idempotency work in your Silver merge?**
**A:**

* Re-running the same CDC batch won’t duplicate data.
* Deduplication by **(primary\_key + \_cdc\_ts)**.
* Use Spark MERGE (or Delta Lake UPSERT pattern).
* Ensures “exactly-once semantics” across retries.

---

---

**Q8: How would you validate the merge logic?**
**A:**

* PySpark unit tests on sample CDC events (inserts, updates, deletes).
* Great Expectations in Silver: schema check, PK uniqueness, type checks.
* Reconcile row counts and sums with SAP source for critical fields.

---

---

**Q9: What are the main entities in DV2 you’d design here?**
**A:**

* **Hubs:** e.g., `Customer_H`, `Material_H`, `Order_H`.
* **Satellites:** attributes with SCD2 (customer details, material attributes, order line details).
* **Links:** associations (e.g., `OrderLine_L` linking Orders ↔ Materials).
* Benefits: auditable, scalable, flexible for future changes.

---

---

**Q10: Python – how do you structure PySpark code for maintainability?**
**A:**

* Modularize transformations (bronze\_to\_silver.py, silver\_to\_gold.py).
* Use config-driven (YAML/JSON) for schema mapping & business rules.
* Add logging (structured JSON logs) + error handling.
* Unit tests with PyTest for transformation logic.
* CI/CD with Argo pipelines for deployment.

---

## 3. **Data Quality & Observability**

---

**Q11: Why use Great Expectations when Purview also has classification?**
**A:**

* Purview: governance (catalog, lineage, search, sensitivity classification).
* GE: fine-grained data validation (row-level, column-level checks, null %, ranges, regex).
* Example: GE ensures `InvoiceAmount > 0`, while Purview only catalogs it as “currency”.
* Both complement each other.

---

---

**Q12: How do you monitor pipeline health?**
**A:**

* Azure Monitor for infra-level (ADF pipelines, SHIR health).
* Prometheus + Grafana for Spark cluster metrics (executor memory, job runtime).
* Alerts on CDC lag, Bronze→Silver SLA breaches, GE validation failure rates.

---

## 4. **Risks & Mitigations (they may test this)**

---

**Q13: What are risks of ADF SAP CDC connector?**
**A:**

* Requires **self-hosted IR** → single point of failure (mitigate with HA nodes).
* Limited throughput if many objects are extracted at once (parallelize pipelines).
* SAP Basis dependency for ODP setup (plan joint runbook).
* Network/firewall issues → solve with private endpoints.

---

---

**Q14: What if SAP schema changes (new column, type change)?**
**A:**

* Bronze: append-only, schema drift allowed.
* Silver: schema evolution rules + column mapping config.
* Alert → Purview picks up new schema → reviewed by data team before promoted to Gold.

---

## 5. **Team & Process**

---

**Q15: How would you onboard new data sources quickly?**
**A:**

* Use Terraform (IaC) for provisioning ADLS zones, Purview collections, ADF pipelines.
* Metadata-driven ingestion configs (table\_name, PK, schedule).
* Standardized QA expectations (GE suites reusable per domain).
* DV2 model extendable by just adding new hubs/satellites.

---

---

**Q16: If BI users complain about slow queries, what do you do?**
**A:**

* Indexing & partitioning in Postgres.
* Pre-aggregations in Gold (fact tables, summary views).
* Optimize CDC loads to avoid bloat (VACUUM, analyze).
* Push BI caching layer (Tableau extracts, Power BI incremental refresh).

---

Perfect 👍 thanks for the update.
If the **Yannik round is done**, then with **Preethini (Senior Data Engineer)** you should expect **deep dives into DV2, Python, PySpark, pipeline design, QA, transformations, idempotency**.

Here’s a **focused Q\&A set from her perspective**, with **detailed answers** you can adapt live.

---

## 🔹 DV2 / Data Modeling

---

**Q1: How would you model SAP data in DV2?**
**A:**

* **Hubs** → represent business keys, e.g. `Customer_H`, `Order_H`, `Material_H`.
* **Links** → relationships, e.g. `OrderLine_L` (connects Order ↔ Material).
* **Satellites** → descriptive attributes, time-variant, e.g. `Customer_S` (name, address), `Order_S` (status, amount).
* For SAP:

  * `SalesOrder` hub from VBELN, `Customer` hub from KUNNR, `Material` hub from MATNR.
  * Satellites capture changes over time (address updates, order status changes).
* **Why DV2 fits here?**

  * SAP keys are stable and globally unique.
  * Satellites let you manage slowly changing attributes (SCD2).
  * Links keep schema flexible, so future joins/relationships can be added.

---

---

**Q2: How do you handle Slowly Changing Dimensions (SCD2) in DV2?**
**A:**

* Happens in **Silver → Gold transition**.
* Logic:

  * Hash key for descriptive attributes.
  * On new CDC event, compare hash with last satellite row.
  * If changed → close old row (`valid_to = new_ts, is_current = false`), insert new row (`valid_from = new_ts, is_current = true`).
* In PySpark, we use **MERGE** with `_business_key` + `_hash` + `_cdc_ts`.
* DV2 makes this natural → satellites are already designed for history handling.

---

---

**Q3: What are challenges when mapping SAP to DV2?**
**A:**

* **Composite keys:** Many SAP tables don’t have a single PK → need to generate surrogate hub keys (hash).
* **Business logic in SAP extractors:** A lot of logic is hidden in ABAP extractors → must decide whether to replicate logic in Silver or push to Gold.
* **High volume:** Sales documents, line items → need partitioning & incremental CDC.
* **Mitigation:** Start with key entities (Customer, Material, Orders), validate with SMEs, expand gradually.

---

## 🔹 Pipeline / PySpark / Python

---

**Q4: How do you ensure idempotency in PySpark merges?**
**A:**

* Deduplicate CDC events by `(business_key, _cdc_ts)`.
* Use `MERGE INTO` with unique keys so re-runs don’t double-insert.
* Example:

  ```python
  df_dedup = df.withColumn("rnk", row_number().over(Window.partitionBy("id").orderBy(col("_cdc_ts").desc()))) \
               .filter("rnk = 1")
  ```
* Store watermark (`last_processed_ts`) to avoid replaying old deltas.

---

---

**Q5: How would you validate Silver merge logic and SCD2 handling?**
**A:**

* Unit test scenarios in PySpark:

  * Insert-only events → appears once.
  * Update events → old row closed, new row opened.
  * Delete events → soft delete marker set.
* Compare record counts with SAP source (sanity check).
* QA layer with **Great Expectations**:

  * PK uniqueness, non-null checks, ranges (e.g., `amount > 0`).
  * Write failures into DLQ for analysis.

---

---

**Q6: How would you structure your PySpark project for maintainability?**
**A:**

* **Layered codebase:**

  * `ingestion/` → Bronze ingestion jobs.
  * `transforms/` → Silver cleaning, deduplication, typing.
  * `business/` → Gold DV2 models.
* **Config-driven:** YAML/JSON for schema, mappings, thresholds.
* **Testing:** Pytest for business logic; small sample CDC files.
* **CI/CD:** Argo workflows → GitOps style deployments.

---

## 🔹 QA / Observability

---

**Q7: Why Great Expectations when Purview also exists?**
**A:**

* Purview → governance, metadata, lineage.
* GE → row-level quality validation, e.g.:

  * `InvoiceAmount > 0`
  * `OrderDate <= CurrentDate`
  * `CountryCode IN ('DE','FR','IT')`
* GE fits naturally in Spark (Python API).
* Together → Purview catalogs dataset, GE ensures it’s *trustworthy*.

---

---

**Q8: How do you monitor and debug Spark jobs in Kubernetes?**
**A:**

* Prometheus collects metrics from Spark driver/executors.
* Grafana dashboards show job duration, executor memory, shuffle read/write.
* Azure Monitor → logs & alerts for pipeline failures.
* Strategy:

  * **Infra:** pod health, node autoscaling.
  * **App:** job SLA, row counts, CDC lag.
  * **Business:** quality checks (GE pass rate).

---

## 🔹 Edge Cases & Risk Handling

---

**Q9: What happens if SAP schema changes?**
**A:**

* Bronze → stores as-is (schema drift allowed).
* Silver → schema evolution rules + default values for new columns.
* Purview → flags schema drift in catalog.
* Manual review before promoting to Gold.

---

---

**Q2: How do you handle SCD2 in DV2?**
**A:**

* Happens in **Silver → Gold**.
* Logic:

  * Detect changes with hash of descriptive columns.
  * If changed → close old row (`valid_to = new_ts, is_current = false`) and insert new (`valid_from = new_ts, is_current = true`).
* **In Python:** compare current record vs. previous, version new record if changed.
* **In Spark SQL (if scaling):** use `MERGE` into satellite table.
* DV2 satellites are designed for this — you always keep history.

---

---

**Q3: What challenges exist mapping SAP → DV2?**
**A:**

* Composite keys (need surrogate hub keys).
* Hidden ABAP logic in SAP extractors (decide what to replicate).
* High-volume tables (line items) → must partition + incremental load.
* Mitigation: Start small (Orders, Materials, Customers), expand gradually.

---

## 🔹 ETL / Python / Pipelines

---

**Q4: How do you ensure idempotency in pipelines?**
**A:**

* **Python:** deduplicate by `(business_key, change_timestamp)`. Re-run produces same result.
* **Spark SQL flavor:** `MERGE` with condition `src._cdc_ts > tgt._cdc_ts`.
* Use watermarks (`last_processed_ts`) to avoid replaying old data.
* Idempotency ensures safe retries and reproducibility.

---

---

**Q5: How do you validate merge logic?**
**A:**

* Test with sample CDC events: insert-only, update, delete.
* Schema validation, PK uniqueness, null checks.
* Business checks: e.g., `InvoiceAmount > 0`.
* Row counts & sums reconciled with SAP totals.
* Failures → Dead Letter Queue for review.

---

---

**Q6: How do you structure Python projects for maintainability?**
**A:**

* **Layered:** ingestion (bronze), cleansing (silver), business logic (gold).
* **Config-driven:** schema mappings, PKs, thresholds in YAML/JSON.
* **Testing:** Pytest for transformation functions.
* **Logging:** structured JSON logs for observability.
* **CI/CD:** Deploy workflows via Argo pipelines, version-controlled in Git.

---

## 🔹 Data Quality & Governance

---

**Q7: Why Great Expectations if Purview exists?**
**A:**

* Purview: metadata, lineage, sensitivity labels, catalog.
* GE: row-level validation, null %, regex, ranges, thresholds.
* Example: Purview says *column = Currency*, GE enforces *Currency ∈ {EUR, USD}*.
* Together → governance + quality gate.

---

---

**Q8: How do you monitor pipelines?**
**A:**

* Infra health: Azure Monitor (ADF, SHIR).
* Application health: job runtimes, row counts, CDC lag.
* Business health: validation pass rate (GE).
* Alerts on SLA breaches or validation failures.

---

## 🔹 Risk & Edge Cases

---

**Q9: What risks exist with ADF SAP CDC?**
**A:**

* Needs self-hosted IR (can fail → mitigate with HA).
* Throughput limits (solve with parallel pipelines).
* Dependency on SAP Basis for ODP setup.
* Network/firewall issues (solve with private endpoints).

---

---

**Q10: What if SAP schema changes?**
**A:**

* Bronze: store as-is (schema drift allowed).
* Silver: config-driven mappings + default values.
* Purview: captures schema change for review.
* Promote to Gold only after validation.

---