# ZEAL Interview Cheat Sheet – Raj Kumar Rai

This 30-minute call is about **technical alignment + collaboration fit**. Keep answers concise (~1–2 minutes each) and end with a value statement.

---
## 🔹 Top Technical Topics
1. **Data Architecture:** Scalable AWS–Databricks–S3 design, clear ingestion/processing/serving layers.
2. **Airflow & DataOps:** Reliability, automation, testing, observability.
3. **Kafka / Real-time:** Event-driven design, schema management, idempotency.
4. **dbt & Data Warehouse:** Modular transformations, CI/CD, testing, lineage.
5. **Collaboration:** Ownership, mentoring, and cross-functional delivery.

---
## 💬 Sample Questions & Model Answers

### 1. Tell me about your current data platform.
> “At Freeletics, our AWS-based platform ingests data from multiple sources via Lambda/Kinesis into S3. Spark (Databricks) performs enrichment and aggregation, structured into Bronze–Silver–Gold zones. Airflow orchestrates daily jobs, and analysts consume via Databricks SQL or Athena.”

### 2. How do you ensure data quality?
> “We integrate validation tasks in Airflow using Great Expectations and schema checks during ingestion. Any deviation triggers Slack alerts and stops downstream jobs.”

### 3. How do you design reliable Airflow DAGs?
> “Each DAG is modular, with explicit dependencies and retries. I use dynamic task generation for daily runs and integrate Slack + CloudWatch for monitoring.”

### 4. Describe your experience with Kafka or streaming.
> “I’ve implemented Kinesis-based enrichment similar to Kafka — schema-defined, idempotent, with replay mechanisms. This pattern scales easily for user events or transaction pipelines.”

### 5. How do you apply DataOps / GitOps in practice?
> “All DAGs, dbt models, and config files are versioned in Git. Deployments happen via CI/CD with automatic validation — no manual changes in production.”

### 6. What’s your experience with dbt or modular data modeling?
> “We follow dbt-style modeling in Databricks SQL — layered design, version control, and automated testing — so onboarding to dbt would be natural.”

### 7. How do you collaborate with Data Scientists?
> “I help design feature-ready datasets and ensure reliable refresh logic. We coordinate through shared schema repos and clear SLAs.”

### 8. Tell me about a project you’re proud of.
> “The Apple transaction enrichment pipeline. I eliminated retries to avoid duplicates, captured detailed per-user logs to S3, and improved reliability — a strong DataOps win.”

### 9. What’s your leadership style?
> “Servant-leadership — I mentor engineers, ensure clarity, and create an environment where reliability and autonomy go hand-in-hand.”

### 10. Why ZEAL?
> “ZEAL’s modern data stack — Airflow, dbt, Kafka, Data Mesh — aligns perfectly with what I’ve built at Freeletics. I’d love to contribute to scaling it further with automation and reliability.”

---
## ⚡ Key Phrases to Drop
- “Modern Data Stack mindset.”
- “Data Mesh and domain ownership.”
- “DataOps maturity — automation, testing, observability.”
- “End-to-end ownership and measurable reliability.”
- “CI/CD-driven data pipelines.”

---
## 🎯 Mindset to Show
✅ Strategic, collaborative, data-obsessed, automation-driven.  
❌ Not overly tactical or tool-focused.  
End strong with: *“I love building reliable, high-impact data ecosystems that empower teams and scale with the business.”*
