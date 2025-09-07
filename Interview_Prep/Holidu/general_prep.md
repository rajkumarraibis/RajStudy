Perfect 👍 — I’ll give you a **playbook of 10 high-probability questions** André (team manager) might ask, with **model answers** tailored to your real stack (Databricks + AWS). These balance **technical depth + architectural thinking + team fit**.

---

# 🔟 Probable Questions & Best Answers

---

### **1. How do you design a scalable data pipeline?**

**Answer:**

> “I follow a **layered approach: Bronze → Silver → Gold**.
>
> * **Bronze:** raw ingestion from multiple sources (e.g., Airbyte jobs landing JSON into S3).
> * **Silver:** cleaning, schema enforcement, deduplication in Databricks using PySpark/SparkSQL.
> * **Gold:** business-ready tables, standardized using dbt Core, with tests and lineage.
>
> Orchestration is handled in Airflow, where tasks run dbt models and Spark jobs. This ensures scalability, transparency, and separation of concerns.”

---

### **2. How do you handle schema evolution?**

**Answer:**

> “On Databricks Delta, I enable `mergeSchema` or `autoMerge` when needed. In dbt Core, schema changes are managed through version-controlled models and tests, so failures are caught early. I also use incremental models with `on_schema_change=append_new_columns` to allow new attributes without breaking pipelines.
> This gives analysts flexibility while keeping governance intact.”

---

### **3. What role does dbt play in your pipeline?**

**Answer:**

> “Databricks + PySpark handles the **heavy lifting** — joins, enrichment, and large-scale transformations.
> dbt Core runs inside Databricks Jobs as a **standardization layer**:
>
> * Incremental models for efficient updates.
> * YAML tests for data quality (e.g., not\_null, unique).
> * Auto-generated lineage docs.
>
> Analysts trust dbt outputs because they’re tested and documented. Engineers like me benefit from its reproducibility and integration with Airflow.”

---

### **4. Can you explain incremental models in dbt?**

**Answer:**

> “Yes. In dbt I use the `is_incremental()` macro.
>
> * First run creates the table with full history.
> * Subsequent runs only process new rows, usually based on a timestamp or unique key.
>
> For example, I built a toy model in Databricks that appends yesterday’s date on each run. In production, I’d filter on `event_date >= max(event_date in target)` to handle incremental appends.
> This reduces cost and makes pipelines more efficient.”

---

### **5. How do you ensure data quality in pipelines?**

**Answer:**

> “At ingestion, I enforce schemas using PySpark’s `StructType`.
> In the transformation layer, dbt provides automated **tests**: not\_null, unique, accepted\_values, relationships.
> For critical datasets, I add anomaly checks in Airflow (row counts, freshness).
> Combined, this creates multiple layers of defense: schema validation, dbt tests, and monitoring.”

---

### **6. What’s the difference between batch and streaming? When do you use each?**

**Answer:**

> “Batch is best for predictable, periodic loads (e.g., daily bookings sync). Streaming is for near real-time needs (e.g., clickstream or payment events).
> In Databricks, I’ve built **Spark Structured Streaming jobs** for event ingestion. Most of our curated models, though, run as batch dbt jobs since analysts work with daily/hourly granularity.
> I always balance latency requirements vs cost before deciding.”

---

### **7. How do you optimize cost in cloud data platforms?**

**Answer:**

> “On AWS, I optimize at three layers:
>
> * **Storage:** Use S3 lifecycle rules to move old data to Glacier; partition data by date for Athena pruning.
> * **Compute:** Run Databricks jobs on spot instances where possible, auto-terminate idle clusters.
> * **Transformations:** In dbt, prefer incremental models over full-refresh; in Spark, use partition filters and Z-ordering for Delta Lake.
>   This keeps compute and storage costs predictable.”

---

### **8. How do you orchestrate dbt and Spark jobs together?**

**Answer:**

> “Airflow DAGs manage orchestration:
>
> * Spark jobs handle enrichment and heavy ETL.
> * Downstream dbt tasks run `dbt run` and `dbt test` to build silver/gold layers.
>
> Dependencies are explicit: Spark output tables feed into dbt sources.
> This ensures reproducibility, better monitoring, and clear lineage.”

---

### **9. Can you walk me through a challenging project you delivered?**

**Answer:**

> “At Freeletics, I built an enrichment pipeline for **Apple transaction events**:
>
> * Ingested raw webhook data into S3.
> * Used PySpark in Databricks to parse nested JSON, enrich with DynamoDB metadata.
> * Applied business rules and wrote curated Delta tables.
> * Recently refactored the pipeline to integrate dbt for Silver/Gold transformations, adding quality tests and lineage.
>
> The challenge was avoiding duplicates and ensuring high trust in financial data. I solved it by removing retries, improving logging, and saving per-user enrichment status to S3. This improved reliability and transparency.”

---

### **10. How do you mentor or collaborate with analysts and data scientists?**

**Answer:**

> “I make transformations transparent and accessible: dbt models are version-controlled, tested, and documented so analysts can explore lineage without asking engineering.
> I also write automation and documentation, so handovers are smooth.
> In my current role, I’ve reduced dependency on engineers by enabling analysts to query curated dbt models directly, speeding up insights.”

---

✅ These 10 cover:

* **Tech depth (dbt, Databricks, AWS)**
* **Architecture (pipeline design, orchestration, cost optimization)**
* **Soft skills (teamwork, mentoring, challenges)**

---

👉 Do you want me to also prepare **one whiteboard-style architecture diagram (in words)** you can explain to André if he asks you to “draw your current pipeline”?
