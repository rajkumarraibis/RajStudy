# 📘 dbt Core – My Experience (Databricks Focused)

This is how I’ve learned and used **dbt Core** directly with **Databricks Jobs**.

---

## 🔹 How I Set It Up

* Created a **dbt project** (`dbt_project.yml` + `models/`).
* Uploaded it into **Databricks Workspace** under my user folder.
* Configured a **Databricks Job** with task type = `dbt`.
* Job ran the commands: `dbt deps`, `dbt run`, `dbt test`.
* Used a **Databricks SQL Warehouse** as the execution engine.

---

## 🔹 Simple Model I Built

**`models/hello_world.sql`**

```sql
{{ config(materialized='table') }}

SELECT
    1 as id,
    'hello dbt on databricks' as message,
    current_date() as run_date
```

* dbt compiled this SQL and created a Delta table in the warehouse.
* Verified the result with:

  ```sql
  SELECT * FROM default.hello_world;
  ```

---

## 🔹 Incremental Model I Practiced

**`models/incremental_dates.sql`**

```sql
{{ config(
    materialized='incremental',
    unique_key='run_date'
) }}

SELECT
    current_date() as run_date,
    'daily load' as note

{% if is_incremental() %}
  -- Only add new rows not already in table
  WHERE current_date() > (SELECT max(run_date) FROM {{ this }})
{% endif %}
```

* First run: creates the table with today’s date.
* Next runs: only append new dates if missing.
* Shows how dbt handles **incremental appends** automatically.

---

## 🔹 Tests I Added

**`models/hello_world.yml`**

```yaml
version: 2

models:
  - name: hello_world
    description: "Simple hello world dbt model"
    columns:
      - name: id
        tests:
          - not_null
          - unique

  - name: incremental_dates
    description: "Demo incremental model appending run dates"
    columns:
      - name: run_date
        tests:
          - not_null
          - unique
```

* dbt ran these automatically with `dbt test`.
* Ensured **data quality** for both models.

---

## 🔹 What I Learned

* **dbt Core in Databricks Jobs** = project lives in Workspace, job runs transformations on SQL Warehouse.
* dbt provides:

  * **Models**: organized SQL/Python transformations.
  * **Tests**: simple YAML-based data quality checks.
  * **Docs**: lineage and descriptions auto-generated.
  * **Incrementals**: efficient way to append only new data.
* Heavy processing is still **Databricks + Spark**; dbt standardizes, tests, and documents results.

---

## 🔹 My Story for Interview

* I’ve used **dbt Core only inside Databricks**.
* I understand **incremental models, tests, docs, and orchestration**.
* The **concepts are portable** → the only thing that changes in Holidu is the adapter (Databricks → Redshift/Athena/DuckDB).

👉 This keeps my story authentic, simple, and aligned with my real hands-on use.
