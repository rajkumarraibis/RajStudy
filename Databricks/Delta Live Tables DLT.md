
````markdown
# 📘 Why I Liked Delta Live Tables in Databricks  
*by Mariusz Kujawski*  
🔗 [Read the original article on Medium](https://medium.com/@mariusz_kujawski/why-i-liked-delta-live-tables-in-databricks-b55b5a97c55c)

---

## Introduction

Databricks has created something that every data engineer will love: **Delta Live Tables (DLT)**.

DLT enables you to declare data transformations using simple SQL or Python and orchestrate your pipeline with built-in monitoring, testing, and error handling. Let's go through why it's awesome.

---

## 🔹 Orchestration in DLT

DLT eliminates the need for external orchestration tools like Apache Airflow or Azure Data Factory.

> Instead of building DAGs manually, your DLT pipeline is the DAG!

📷  
![DLT DAG with SQL and Python pipelines](\images\dlt_dag.png)

---

## 🔍 Built-in Monitoring and Observability

With DLT, you get monitoring out of the box. You can view the status of your tables, lineage, and metrics in a clean UI.

📷  
![DLT UI with table status and progress](\images\dlt_ui_monitoring.png)

---

## ⚙️ Testing & Data Quality Rules

DLT supports data quality rules natively:

```sql
CREATE OR REFRESH LIVE bronze_table
AS SELECT *
FROM cloud_files("/path", "json")
CONSTRAINT valid_data EXPECT (id IS NOT NULL);
````

You can flag or drop invalid rows easily and log the violations.

📷
![DLT test rule UI](\images\dlt_data_quality.png)

---

## 🧪 Development Flow

With DLT, you can develop in "development" mode and deploy confidently in "production" mode using the same code.

* Fast iteration during development.
* Version-controlled deployment in production.

📷
![DLT development and production modes](\images\dlt_dev_prod.png)

---

## 🔄 Auto Scaling & Error Recovery

DLT handles job retries, cluster restarts, and retries automatically. You focus on logic, Databricks takes care of operations.

📷
![DLT pipeline error handling](\images\dlt_autoscale.png)

---

## 🧱 SQL or Python — Your Choice

You can choose SQL:

```sql
CREATE OR REFRESH LIVE gold_users
AS SELECT * FROM silver_users WHERE is_active = true
```

Or Python:

```python
@dlt.table
def gold_users():
    return spark.sql("SELECT * FROM silver_users WHERE is_active = true")
```

📷
![SQL and Python examples](\images\dlt_sql_python.png)

---

## ✅ Summary

Delta Live Tables:

* Remove orchestration overhead
* Provide visibility and monitoring
* Support data quality rules
* Handle retries and errors
* Work with SQL and Python
* Accelerate development and deployment

If you’re building data pipelines — DLT is worth exploring!

---

📚 **Reference**
[Why I Liked Delta Live Tables in Databricks – Medium Article](https://medium.com/@mariusz_kujawski/why-i-liked-delta-live-tables-in-databricks-b55b5a97c55c)

```

---
