
---

````markdown
# 🎯 Senior Data Engineer Interview Prep (Cosnova – 1st Round)

This guide summarizes the key topics and soundbites for the first interview with Head of Data Analytics & Engineering.

---

## 1️⃣ Governance & Data Quality

### Unity Catalog
- **Role:** Central governance layer for Databricks (schemas, tables, views, ML models).  
- **Features:**  
  - Catalog → Schema → Table hierarchy.  
  - Fine-grained ACLs (row/column-level).  
  - **Lineage tracking** (table-level, column-level preview).  
  - Auditing + access logs.

**Freeletics Example:**  
- All DV2 tables (`Hub_User`, `Link_Subscription`, `Sat_SubscriptionEvents`) registered in UC.  
- Analysts query only Gold marts via UC with permissions.  
- UC lineage shows: `bronze.stripe_events → silver.sat_subscriptionevents → gold.fact_subscriptionevents → finance.revenue_dashboard`.

**Soundbite:**  
*“Unity Catalog gave us schema consistency, column-level ACLs for PII, and lineage so we could trace a revenue number from dashboard back to raw Stripe events.”*

---

### Data Quality (Great Expectations)
- Embedded in ETL (Silver layer).  
- Expectations: null checks, uniqueness, referential integrity.  
- Failures block promotion from Silver → Gold.

**Example:**  
- `expect_column_values_to_not_be_null(User_ID)`  
- `expect_column_values_to_be_unique(Event_ID)`  
- `expect_table_row_count_to_be_between(1000,100000)`

**Soundbite:**  
*“At Freeletics, we embedded Great Expectations checks in Databricks Jobs so bad data never polluted Silver or Gold. This built trust with Finance and Marketing.”*

---

## 2️⃣ Azure + Databricks Ecosystem

- **ADLS Gen2** → Bronze raw landing.  
- **Databricks Jobs** → Batch & streaming orchestration.  
- **Event Hubs / Kafka** → Real-time ingestion.  
- **Azure Data Factory (ADF)** → Orchestrates cross-service pipelines.  
- **Power BI** → BI/visualization layer on Gold marts.  
- **Key Vault** → Secrets for service principals.

**Soundbite:**  
*“In Azure, we landed raw events in ADLS, processed with Databricks into Silver DV2, and exposed Gold marts for Power BI. ADF triggered the orchestration, and service principals handled secrets.”*

---

## 3️⃣ Streaming & CDC

### CDC with Delta Lake
- Staging table → deduplicate by `_ts`.  
- `MERGE INTO` Silver tables.  
- Satellites store row-level history (DV2).  

```sql
MERGE INTO silver.users t
USING staging.users s
ON t.user_id = s.user_id
WHEN MATCHED AND s._ts > t._ts THEN UPDATE SET *
WHEN NOT MATCHED THEN INSERT *;
````

### Streaming (Structured Streaming)

* **Auto Loader** (`cloudFiles`) for incremental ingest.
* **Watermarking** for late data.
* **Checkpointing** ensures exactly-once delivery.

**Soundbite:**
*“We used Auto Loader for CDC streams with checkpointing and watermarking to guarantee idempotency. MERGE INTO maintained historized Satellites in DV2.”*

---

## 4️⃣ CI/CD & Data as Code

* All pipelines stored in GitHub.
* **GitHub Actions**: run PySpark unit tests, GE suites, linting, deploy notebooks/configs to workspaces.
* Promotion Dev → QA → Prod with approvals.

**Soundbite:**
*“Pipelines were code: PRs triggered unit & data tests, then GitHub Actions deployed to Databricks. That gave us consistency, rollback safety, and auditability.”*

---

## 5️⃣ Observability & Cost Control

### Monitoring

* **Freshness dashboards** (last update timestamp).
* Job run SLAs + alerts.
* Spark UI for shuffle/skew profiling.

### Cost Management

* **Delta OPTIMIZE** & Z-Order → compact small files.
* File size target 128–512MB.
* Cluster autoscaling + spot for non-critical jobs.
* Photon execution engine for SQL-heavy workloads.

**Soundbite:**
*“We tracked freshness SLAs, compacted small files daily with OPTIMIZE, and tuned partitions to match cluster size. This cut job runtimes by 30% and reduced compute cost.”*

---

## 6️⃣ Security & Privacy

* **PII handling:** column masking (Unity Catalog), tokenization if required.
* **Secrets:** stored in Key Vault, injected via service principals.
* **Least privilege:** Analysts only Gold access, engineers on Silver/Bronze.

**Soundbite:**
*“PII was masked at Gold; UC enforced column ACLs, and secrets came from Key Vault. This gave auditors confidence that GDPR controls were enforced.”*

---

## 7️⃣ Data Modeling Edges

### DV2 Patterns

* **PIT (Point-In-Time)** tables for faster joins (user status as of X date).
* **Bridge tables** for many-to-many joins.

### SCD in Star Schema

* Type 2 for historized dims (e.g., product price history, campaign details).

**Soundbite:**
*“We used PIT tables to avoid heavy join chains in DV2 and SCD2 in Gold dims for campaign history. This made analyst queries much faster.”*

---

## 8️⃣ Domain Translation: Freeletics → Cosnova

* **Freeletics:** Users, Subscriptions, Campaigns.
* **Cosnova:** Customers, Products, Promotions.

| Freeletics             | Cosnova                         | Parallel                                              |
| ---------------------- | ------------------------------- | ----------------------------------------------------- |
| Subscription lifecycle | Product lifecycle               | Both need DV2 Satellites for history (price, status). |
| Campaign attribution   | Promotion attribution           | Link tables to track user/product → campaign.         |
| Churn / cancellations  | Product returns, promo response | Facts at event grain.                                 |

**Soundbite:**
*“At Freeletics, I modeled subscription events (start, renew, cancel) in DV2, exposing a Fact for churn analysis. At Cosnova, I’d do the same for product lifecycle and promotions — capturing every price change or campaign response historically.”*

---

# 🎤 Common Interview Prompts & Answers

**Q: How do you prevent a data lake from becoming a swamp?**
A: Governance (Unity Catalog), quality gates (GE), clear Bronze/Silver/Gold layering, and SLAs on freshness.

**Q: How would you onboard a new source fast?**
A: Land with Auto Loader → validate schema & quality with GE → DV2 mapping in Silver → expose minimal Gold mart → iterate.

**Q: How do you debug if “numbers look off” in a dashboard?**
A: Use UC lineage to trace Gold → Silver → Bronze; compare row counts, re-run GE checks, and verify recent CDC merges.

---

# ✅ Summary for Yannick Round

* Highlight **DV2 + Star Schema** (already strong).
* Sprinkle **optimization awareness** (broadcast joins, pruning, Z-Order).
* Stress **governance & quality** (UC + GE).
* Show awareness of **Azure stack**.
* Use **Freeletics→Cosnova domain mapping** for credibility.
* Keep tone **collaborative, pragmatic, and business-oriented**.

```

---

👉 Raj, this file is **comprehensive for Round 1**.  
Would you like me to also make a **shorter “flashcard version”** (just soundbites & keywords, 1-pager) for last-minute review before the call?
```
