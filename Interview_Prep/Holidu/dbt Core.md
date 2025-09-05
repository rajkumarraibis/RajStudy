
---

# 📘 dbt Core – Dumbed Down Cheat Sheet (for Interview)

dbt = **Data Build Tool**

* Think of it as: *“SQL + config + tests + docs + lineage”*.
* Runs on top of your **warehouse/engine** (Databricks/SparkSQL, Redshift, Athena, DuckDB).
* **Core idea**: Organize transformations into **models** → build **DAGs** → test + document them.

---

## 🔹 1. dbt Project Basics

Every dbt project has:

```
dbt_project.yml   # configs
models/           # SQL or Python models
  ├─ staging/
  ├─ intermediate/
  └─ marts/
```

* **staging** = raw sources (Bronze).
* **intermediate** = cleaned, joined (Silver).
* **marts** = business-friendly tables (Gold).

---

## 🔹 2. A Simple SQL Model

`models/staging/stg_bookings.sql`

```sql
{{ config(
    materialized='incremental',
    unique_key='booking_id'
) }}

SELECT
    booking_id,
    user_id,
    destination,
    price,
    booking_date
FROM {{ source('raw', 'bookings') }}

{% if is_incremental() %}
  WHERE booking_date >= (SELECT max(booking_date) FROM {{ this }})
{% endif %}
```

✅ What happens:

* dbt builds this table in your warehouse (Delta, Redshift, etc.).
* Runs incrementally = only new rows since last run.
* Uses macros (`{{ }}`) to make SQL smarter.

---

## 🔹 3. A Simple Python Model (Databricks/Spark)

`models/bronze/tracking_events.py`

```python
{{ config(materialized="incremental", unique_key="event_id") }}

def model(dbt, session):
    import json
    from datetime import datetime, timedelta
    
    # read yesterday's events (like your PySpark job)
    yesterday = (datetime.utcnow() - timedelta(days=1)).strftime("%Y-%m-%d")
    path = f"s3://ppm-analytics-share-dev/tracking/events/{yesterday}/*/*.json"

    df = session.read.json(path)

    return df
```

✅ dbt will:

* Run this on Databricks/SparkSQL.
* Save results as a **Delta table**.
* Handle incrementals & schema merge.

---

## 🔹 4. Adding Tests

`models/staging/stg_bookings.yml`

```yaml
version: 2

models:
  - name: stg_bookings
    description: "Bookings data cleaned from raw layer"
    columns:
      - name: booking_id
        tests:
          - not_null
          - unique
      - name: price
        tests:
          - not_null
```

✅ If a test fails, dbt raises error in logs/Airflow.

---

## 🔹 5. Documentation & Lineage

* Add descriptions in `.yml`.
* Run:

  ```bash
  dbt docs generate
  dbt docs serve
  ```
* Opens a web UI with **lineage graph** + schema docs.

---

## 🔹 6. Orchestration with Airflow

Airflow DAG task (simplified):

```python
from airflow.operators.bash import BashOperator

dbt_run = BashOperator(
    task_id="dbt_run",
    bash_command="dbt run --profiles-dir . --project-dir ."
)

dbt_test = BashOperator(
    task_id="dbt_test",
    bash_command="dbt test --profiles-dir . --project-dir ."
)

dbt_run >> dbt_test
```

✅ Airflow schedules & runs dbt models in order.

---

## 🔹 7. How to Explain in Interview

Use this **one-liner**:

> “In our pipelines, Databricks + PySpark does the heavy lifting, and dbt Core standardizes the transformations: incremental models, tests, docs, and orchestration via Airflow. That way, analysts get trusted data with clear lineage.”

---

# 📝 Key Phrases to Drop in Interview

* “We use **staging → silver → marts** structure.”
* “I configure **incremental models** with `is_incremental()`.”
* “dbt tests ensure **data quality at transformation layer**.”
* “dbt docs give **lineage graphs** for analysts.”
* “Airflow triggers **dbt run + dbt test** in sequence.”

---

