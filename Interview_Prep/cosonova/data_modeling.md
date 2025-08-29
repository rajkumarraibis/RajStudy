

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

### 🔹 Why It’s Valuable (for cosnova)

1. **Audit Trail** → full history of product, pricing, campaigns (important in retail).
2. **Schema Evolution** → new attributes can be added without disrupting existing model.
3. **Traceability** → easy to trace any KPI back to raw source.
4. **Modularity** → new hubs/links/sats can be added as business grows.
5. **Business Alignment** → provides a governed foundation, then transformed for BI/AI use.

👉 **Interview Soundbite:**
*"I see Data Vault 2.0 as cosnova’s governed raw data backbone — hubs capture keys like Product or Customer, links capture relationships like Sales, and satellites capture changing attributes like prices or categories. It ensures history and compliance, while still enabling agile growth."*

---

# 📌 Star Schema (on top of DV 2.0)

### 🔹 Core Idea

* Analysts don’t want to query Hubs/Links/Satellites directly.
* So we **transform Data Vault → Star Schema marts** (Facts + Dimensions).
* This is the **semantic layer** used for BI & reporting.

---

### 🔹 Example Transformation

From DV 2.0:

* **Hub\_Customer** → becomes **Dim\_Customer**
* **Hub\_Product + Sat\_Product** → becomes **Dim\_Product**
* **Link\_Sales + Sat\_Sales** → becomes **Fact\_Sales**

---

**Fact\_Sales (from Link\_Sales + Sat\_Sales)**
\| Sale\_ID | Date\_Key | Customer\_Key | Product\_Key | Quantity | Sales\_Amount |

**Dim\_Customer (from Hub\_Customer + Sat\_Customer)**
\| Customer\_Key | Customer\_Name | Gender | City | Country |

**Dim\_Product (from Hub\_Product + Sat\_Product)**
\| Product\_Key | Product\_Name | Category | Brand |

---

### 🔹 Why It’s Valuable (for cosnova)

1. **Ease of Use** → Analysts, BI tools (Power BI, Tableau) prefer facts/dims.
2. **Performance** → Queries run faster (optimized for aggregations).
3. **Business Alignment** → Exposes KPIs directly.
4. **Flexibility** → Still backed by DV → full history and governance.

👉 **Interview Soundbite:**
*"In practice, I’d use Data Vault 2.0 as the enterprise raw layer for audit/history, and then transform into Star Schema marts for BI. For example, a Link\_Sales and Sat\_Sales in DV would transform into a Fact\_Sales table, with Dim\_Customer and Dim\_Product from their hubs and satellites. This way, analysts get simplicity, and IT retains auditability."*

---

✅ If you can explain **DV = raw, auditable foundation** and **Star = consumable marts**, you’ll hit Yannick’s sweet spot.

---