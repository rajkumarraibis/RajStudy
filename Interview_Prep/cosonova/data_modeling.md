# 📌 Data Vault 2.0

### 🔹 Core Idea

A **modeling methodology (not a product)** for building an **auditable, historized, and scalable raw data warehouse layer**.

It’s designed for:

* **Agility** → schema changes don’t break the model.
* **History** → keeps track of changes over time.
* **Auditability** → every record can be traced to its source.
* **Scalability** → modular, extensible with new hubs/links/sats.

---

### 🔹 Components

**1. Hub (Business Keys)**

* Represents the *core business entity* (immutable ID).
* Examples: `Customer_ID`, `Product_ID`, `Store_ID`.
* Columns:
  * Business key (natural ID)
  * Surrogate hash key (HK)
  * Load date
  * Record source

👉 *Example:*
```sql
Hub_Customer
+------------+-------------+-----------+--------------+
| Customer_HK| Customer_ID | LoadDate  | RecordSource |
+------------+-------------+-----------+--------------+
```

---

**2. Link (Relationships)**

* Connects **two or more hubs** (many-to-many relationships).
* Represents **transactions, events, or associations**.
* Examples: *Customer buys Product*, *Product sold in Store*.
* Columns:
  * Surrogate hash key
  * Foreign keys to hubs
  * Load date
  * Record source

👉 *Example:*
```sql
Link_Sales
+---------+-------------+-----------+-----------+--------------+
| Sales_HK| Customer_HK | Product_HK| SaleDate  | RecordSource |
+---------+-------------+-----------+-----------+--------------+
```

---

**3. Satellite (Attributes & History)**

* Stores **descriptive attributes** about hubs or links.
* Keeps **history** (effective date, expiry, load date).
* Examples: Customer Name, Address, Product Price.
* Columns:
  * Parent hub/link key
  * Attribute(s)
  * Effective date, Load date
  * Record source

👉 *Example:*
```sql
Sat_Product
+-----------+-------------+----------+-----------+--------------+
| Product_HK| ProductName | Category | LoadDate  | RecordSource |
+-----------+-------------+----------+-----------+--------------+
```

---

### 🔹 Freeletics Implementation Example (DV2 on Databricks)

At Freeletics, I implemented a **DV 2.0 style architecture on Databricks with Delta Lake**, focusing on **CDC (Change Data Capture), history tracking, and governance**:

* **Hub_User** stored unique user IDs (immutable business keys).
* **Link_Subscription** captured relationships between users and subscriptions (many-to-many over time).
* **Sat_User** recorded changing user attributes (email, country, subscription tier) with full historization.
* **Sat_Subscription** captured plan details, including upgrades/downgrades over time.
* Implemented **CDC using Delta Lake MERGE** to capture new inserts/updates efficiently.
* Used **Delta Time Travel** for historization and audit.
* Embedded **data quality checks** with Great Expectations and lineage with Unity Catalog.
* Built **CI/CD pipelines with GitHub Actions** to ensure consistent deployments.

👉 *Result:* We achieved **traceable, historized user and subscription data**, which allowed finance and product teams to answer: *“What was the user’s subscription state on any given date?”* while maintaining compliance.

---

### 🔹 Why It’s Valuable (for cosnova)

1. **Audit Trail** → full history of product, pricing, campaigns (important in retail).
2. **Schema Evolution** → new attributes can be added without disrupting existing model.
3. **Traceability** → easy to trace any KPI back to raw source.
4. **Modularity** → new hubs/links/sats can be added as business grows.
5. **Business Alignment** → provides a governed foundation, then transformed for BI/AI use.

👉 **Interview Soundbite:**
*"At Freeletics, we used DV 2.0 to historize subscription and user changes with Delta Lake CDC and Time Travel. I see a similar value at cosnova for tracking product, pricing, and campaign changes with full traceability and governance."*

---

# 📌 Star Schema (on top of DV 2.0)

### 🔹 Core Idea

* Analysts don’t want to query Hubs/Links/Satellites directly.
* So we **transform Data Vault → Star Schema marts** (Facts + Dimensions).
* This is the **semantic layer** used for BI & reporting.

---

### 🔹 Example Transformation

From DV 2.0:

* **Hub_Customer** → becomes **Dim_Customer**
* **Hub_Product + Sat_Product** → becomes **Dim_Product**
* **Link_Sales + Sat_Sales** → becomes **Fact_Sales**

---

**Fact_Sales (from Link_Sales + Sat_Sales)**
| Sale_ID | Date_Key | Customer_Key | Product_Key | Quantity | Sales_Amount |

**Dim_Customer (from Hub_Customer + Sat_Customer)**
| Customer_Key | Customer_Name | Gender | City | Country |

**Dim_Product (from Hub_Product + Sat_Product)**
| Product_Key | Product_Name | Category | Brand |

---

### 🔹 Freeletics Star Schema Example

At Freeletics, after building the raw DV 2.0 layer:

* We exposed **Fact_SubscriptionEvents** from Link_Subscription + Sat_Subscription.
* Built **Dim_User** from Hub_User + Sat_User.
* Built **Dim_Product** from Hub_Product + Sat_Product.
* These star schema marts powered BI dashboards (subscription funnel, churn rates) and supported AI models for churn prediction.

👉 *Result:* BI analysts had **fast, simple marts** (facts/dims), while DV 2.0 still retained the **raw audit trail** for compliance.

---

### 🔹 Why It’s Valuable (for cosnova)

1. **Ease of Use** → Analysts, BI tools (Power BI, Tableau) prefer facts/dims.
2. **Performance** → Queries run faster (optimized for aggregations).
3. **Business Alignment** → Exposes KPIs directly.
4. **Flexibility** → Still backed by DV → full history and governance.

👉 **Interview Soundbite:**
*"At Freeletics, I transformed DV 2.0 into star schema marts, e.g., subscription facts and user/product dimensions, enabling analysts to get simple, performant access while IT still had a complete historical trail. For cosnova, I see the same pattern: DV for governance and audit, Star for reporting and analytics."*

---

✅ If you can explain **DV = raw, auditable foundation** and **Star = consumable marts**, with your Freeletics examples, you’ll hit Yannick’s sweet spot.

