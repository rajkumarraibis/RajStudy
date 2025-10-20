
---

## ✅ What dbt is + why it matters

* dbt = Data Build Tool: an open-source framework to perform **transformations** (T in ELT) inside your data warehouse using SQL rather than moving data out. ([DataCamp][1])
* Key use-cases:

  * Transform raw/ingested data into analytics-ready tables
  * Modularising SQL transformations (models)
  * Testing, documenting, and building lineage for data models
  * Building version-controlled, maintainable data pipelines
* Why it’s relevant in interviews: many analytics-engineering/data-engineering roles now expect familiarity with dbt or similar tools. ([ProjectPro][2])

---

## 🧱 Core Concepts & Terminology

Here are key terms you must know and be conversant with:

| Term                             | What it means                                                                                                       |
| -------------------------------- | ------------------------------------------------------------------------------------------------------------------- |
| **Model**                        | A `.sql` file in dbt that defines a transformation or table/view to build. ([Medium][3])                            |
| **ref()**                        | A function in dbt to reference another model inside your project. Encourages dependency tracking. ([ProjectPro][2]) |
| **source()**                     | Used to reference external/raw tables/data sources not managed by dbt transforms. ([Medium][3])                     |
| **Materialisation**              | How dbt builds the result of a model: as a view, table, incremental load, snapshot, etc. ([Medium][3])              |
| **Snapshot**                     | A model materialisation strategy to capture changes over time (historical state) of a table. ([Medium][3])          |
| **Macro**                        | Reusable SQL (via Jinja templating) to abstract common logic. ([Medium][3])                                         |
| **DAG (Directed Acyclic Graph)** | The dependency graph of models; dbt uses this to determine build order. ([Medium][3])                               |
| **Tests**                        | Built-in or custom tests in dbt to check data quality, e.g., uniqueness, not null, accepted values. ([Medium][3])   |

---

## 🔧 Typical Workflow / Project Setup

* Install dbt and initialise a project (via `dbt init` or equivalent)
* Define your connection to the data warehouse (Snowflake, BigQuery, Redshift, etc)
* Create models: write `.sql` files in `models/` directory
* Organise project structure: sources, models, macros, snapshots, tests, docs
* Use `ref()` and `source()` appropriately to manage dependencies
* Define tests in `schema.yml` or other config files
* Materialise models with correct strategy (view, table, incremental)
* Use `dbt run`, `dbt test`, `dbt compile`, etc to build and validate
* Generate documentation (`dbt docs generate`) and view lineage
* Integrate with version control (e.g., Git) and CI/CD + orchestrator (Airflow, Prefect, etc)
* Deploy to production: often via dbt Cloud or custom pipelines

---



---

## 📌 Best Practices & Things to Highlight

* Always use version control (Git) for your dbt project; collaborative workflows matter.
* Modularise your transformations: smaller models, clear naming, logical separation.
* Use `ref()` consistently rather than hard-coding table names; this improves dependency tracking and refactorability.
* Write tests for your models early; it helps maintain data quality and reliability.
* Document your models (using `docs` config and `schema.yml`); this helps team understanding and maintenance.
* Choose appropriate materialisation: incremental when dataset is large and you only need to load changes; snapshot when tracking history.
* Consider performance: large datasets may benefit from clustering/partitioning in your data warehouse; dbt can help but you’ll need to consider warehouse-specific features. (e.g., Snowflake clustering) ([DataCamp][1])
* Be mindful of environment separation: use dev/staging/prod, different schemas/databases for safety; use `target` variable for conditional logic.
* Monitor dependency graph / lineage to avoid build failures due to wrong model order or missing dependencies.
* Consider CI/CD: run tests on pull requests, ensure models pass before merging, automate docs generation.
* Use macros to avoid repeating SQL logic and make your project DRY (Don’t Repeat Yourself).
* When scaling, keep an eye on complexity: many models, many dependencies, large datasets => need monitoring, maybe orchestration, maybe modular architecture.

---

## 📝 Template for Your Document (You can fill this out)

**Title**: dbt Interview Cheat-Sheet
**Sections**:

Perfect 👍 — let’s prepare a **ready-to-use dbt (Data Build Tool) interview cheat sheet** with clear and confident answers for each of your listed points.
This will serve as your **personal dbt interview reference document** (beginner to intermediate level).

---

## 🧩 1. What is dbt & Why Use It

**Definition:**
dbt (Data Build Tool) is an open-source framework that helps data teams **transform raw data inside the data warehouse using SQL and Jinja templates**.

**Why use it:**

* It handles the **T (Transform)** in the ELT process.
* Converts messy staging data into **clean, analytics-ready tables**.
* Allows you to **version control SQL**, just like code.
* Automatically manages **dependencies** between tables.
* Provides **testing, documentation, and data lineage** out of the box.
* Helps analysts work like engineers — modular, tested, documented transformations.

👉 **Simple Example:**
Instead of writing SQL scripts in Airflow or notebooks, you write modular SQL models in dbt, test them, and let dbt build the right order and lineage.

---

## ⚙️ 2. Key Concepts & Terms

| Concept                          | Meaning                                                                                                               | Example                                 |
| -------------------------------- | --------------------------------------------------------------------------------------------------------------------- | --------------------------------------- |
| **Model**                        | A `.sql` file that represents a transformation (usually one SELECT statement). dbt builds each model as a view/table. | `models/stg_orders.sql`                 |
| **ref()**                        | A function to reference another model — creates dependencies and lineage automatically.                               | `SELECT * FROM {{ ref('stg_orders') }}` |
| **source()**                     | References raw/external data sources (not created by dbt).                                                            | `{{ source('raw', 'customers') }}`      |
| **Materialisation**              | Defines how dbt stores a model — `view`, `table`, `incremental`, or `ephemeral`.                                      | Incremental for large tables            |
| **Snapshot**                     | Captures **historical changes** in data (Slowly Changing Dimensions).                                                 | Track user status change over time      |
| **Macro**                        | Reusable SQL logic using **Jinja templating** (like SQL functions).                                                   | `{{ my_macro('arg1') }}`                |
| **DAG (Directed Acyclic Graph)** | Visual map of model dependencies; dbt builds models in correct order.                                                 | Run `dbt docs serve` to see lineage     |
| **Tests**                        | Assertions that validate data quality — e.g. uniqueness, not_null, accepted_values.                                   | Defined in `.yml` files                 |

---

## 🧱 3. Workflow / Project Setup

**Typical Steps:**

1. **Install & Initialise Project**

   ```bash
   pip install dbt-core dbt-bigquery  # or dbt-snowflake / dbt-redshift etc.
   dbt init my_project
   ```
2. **Set Up Connection**
   Configure `profiles.yml` → connection details for your warehouse.
3. **Create Models**
   Add `.sql` files under `models/` — each file = one model.
4. **Define Sources & Tests**
   Create `schema.yml` for sources, tests, and documentation.
5. **Use ref() to Build Dependencies**
   Each model references another → dbt builds DAG automatically.
6. **Materialise Models**
   Choose how they are stored (`view`, `table`, `incremental`).
7. **Run Project**

   ```bash
   dbt run     # build models
   dbt test    # validate data
   dbt docs generate && dbt docs serve
   ```
8. **Integrate with CI/CD**
   Add Git, pull requests, and automated runs (dbt Cloud or Airflow).

---

## 🎯 4. Common Interview Questions & Model Answers

### Q1. What’s the difference between ETL and ELT?

**Answer:**
ETL extracts, transforms, and then loads data — transformations happen before loading.
ELT loads raw data into the warehouse first, then transforms it **inside** using SQL/dbt.
👉 dbt is designed for **ELT**, leveraging the compute of modern warehouses.

---

### Q2. Difference between `ref()` and `source()`

**Answer:**

* `ref()` → references **models created by dbt**.
* `source()` → references **external raw tables**.
  👉 `ref()` builds dependencies; `source()` defines data origin.

---

### Q3. What are dbt materialisations?

**Answer:**
Ways to persist data models:

* **view:** default; lightweight
* **table:** full table rebuild
* **incremental:** only new/changed rows
* **ephemeral:** temporary CTE; not persisted

---

### Q4. How does dbt ensure data quality?

**Answer:**
Through **tests** defined in YAML:

* Built-in: `not_null`, `unique`, `accepted_values`
* Custom SQL tests
* Run via `dbt test`
  👉 Ensures trust in data.

---

### Q5. How does dbt handle dependencies?

**Answer:**
By analysing `ref()` links → builds a DAG → runs transformations in correct order.

---

### Q6. How would you manage environments (dev, stage, prod)?

**Answer:**

* Use separate schemas/databases via `target.name`
* Conditional logic in Jinja:

  ```jinja
  {% if target.name == 'prod' %}schema='analytics'{% else %}schema='staging'{% endif %}
  ```
* Integrate with CI/CD (GitHub Actions, Airflow, dbt Cloud).

---

### Q7. When to use incremental models?

**Answer:**
For large datasets that only need **delta updates**.
Use logic like:

```jinja
{% if is_incremental() %}
  where updated_at > (select max(updated_at) from {{ this }})
{% endif %}
```

---

### Q8. Common challenges in dbt projects?

**Answer:**

* Long DAGs cause performance issues
* Managing schema drift
* Ensuring consistent testing
* Incremental logic mistakes → duplicates
* Cost optimisation on warehouse compute

---

## 💡 5. Best Practices

✅ Use **version control (Git)** for every dbt project.
✅ Keep models **modular and layered**:

* `staging/` (clean raw data)
* `intermediate/` (join and enrich)
* `marts/` (business-ready tables)
  ✅ Prefer `ref()` over hardcoded names.
  ✅ Write **tests for critical columns** (unique keys, null checks).
  ✅ Add **model descriptions** in `schema.yml`.
  ✅ Use **macros** to eliminate SQL repetition.
  ✅ Maintain **environment isolation** with schemas/databases.
  ✅ Automate **docs and CI/CD** for quality assurance.
  ✅ Monitor **performance and cost** of warehouse queries.

---

## ⚠️ 6. Challenges & How to Handle Them

| Challenge                          | How to Handle                                                |
| ---------------------------------- | ------------------------------------------------------------ |
| **Slow builds**                    | Optimise queries; use incremental models; limit CTE nesting. |
| **Schema drift (column mismatch)** | Version models; add schema tests; document changes.          |
| **Data quality issues**            | Add `not_null`, `unique`, and `accepted_values` tests.       |
| **Dependency confusion**           | Use `ref()` consistently; visualise DAG.                     |
| **Large project structure**        | Organise models logically (staging → mart).                  |
| **Warehouse costs**                | Use incremental loads; schedule smartly.                     |

---

## 🚀 7. My Hands-on Experience / Use Case (example for you)

> *At Freeletics, I integrated dbt into a Databricks + S3 pipeline to build clean analytics models for marketing and user engagement data.*

* Built staging models for Braze webhook and payment data.
* Used `ref()` to connect user enrichment models with transaction tables.
* Added tests for nulls, duplicates, and relationships.
* Materialised summary tables as **incremental models** to reduce cost.
* Integrated dbt runs with Airflow DAGs and CI/CD in GitHub.
* Generated documentation for team-wide data transparency.

(👉 You can modify this example based on your actual Databricks project.)

---

## 📚 8. Further Learning Resources

| Resource          | Type                 | Link                                                                         |
| ----------------- | -------------------- | ---------------------------------------------------------------------------- |
| dbt Documentation | Official             | [https://docs.getdbt.com](https://docs.getdbt.com)                           |
| dbt Learn         | Free official course | [https://learn.getdbt.com](https://learn.getdbt.com)                         |
| dbt Discourse     | Community Q&A        | [https://discourse.getdbt.com](https://discourse.getdbt.com)                 |
| YouTube Channel   | Tutorials            | [dbt Labs YouTube](https://www.youtube.com/@dbtlabs)                         |
| GitHub            | Open source          | [https://github.com/dbt-labs/dbt-core](https://github.com/dbt-labs/dbt-core) |

---



---

If you like, I can **generate a downloadable PDF/one-pager** of this summary (formatted nicely) which you can print/update for your interview prep. Would you like me to do that?

[1]: https://www.datacamp.com/blog/dbt-interview-questions?utm_source=chatgpt.com "Top 26 dbt Interview Questions and Answers for 2025"
[2]: https://www.projectpro.io/article/dbt-interview-questions-and-answers/1062?utm_source=chatgpt.com "Top 25 DBT Interview Questions and Answers for 2025"
[3]: https://medium.com/%40nishadpatkar7/data-build-tool-dbt-interview-questions-and-answers-107f6799c7a3?utm_source=chatgpt.com "Data Build Tool (DBT) Interview Questions and Answers"
