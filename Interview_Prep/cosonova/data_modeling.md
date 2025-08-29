# 📌 Data Vault 2.0

### 🔹 Core Idea

A **modeling methodology (not a product)** for building an **auditable, historized, and scalable raw data warehouse layer**.

It’s designed for:

* **Agility** → schema changes don’t break the model.
* **History** → keeps track of changes over time.
* **Auditability** → every record can be traced to its source.
* **Scalability** → modular, extensible with new hubs/links/sats.

---

### 🔹 Components (Freeletics-specific)

**1. Hub (Business Keys)**

* Represents the *core business entity* (immutable ID).
* Freeletics Examples: `User_ID`, `Subscription_ID`, `Campaign_ID`.
* Columns:
  * Business key (natural ID)
  * Surrogate hash key (HK)
  * Load date
  * Record source

👉 *Example:*
```sql
Hub_User
+---------+----------+-----------+--------------+
| User_HK | User_ID  | LoadDate  | RecordSource |
+---------+----------+-----------+--------------+
```

---

**2. Link (Relationships)**

* Connects **two or more hubs** (many-to-many relationships).
* Represents **transactions, events, or associations**.
* Freeletics Examples: *User subscribes to a plan*, *Campaign targets User*.
* Columns:
  * Surrogate hash key
  * Foreign keys to hubs
  * Load date
  * Record source

👉 *Example:*
```sql
Link_Subscription
+-----------------+---------+------------------+-----------+--------------+
| Subscription_HK | User_HK | Subscription_ID  | StartDate | RecordSource |
+-----------------+---------+------------------+-----------+--------------+
```

---

**3. Satellite (Attributes & History)**

* Stores **descriptive attributes** about hubs or links.
* Keeps **history** (effective date, expiry, load date).
* Freeletics Examples: User profile details, subscription plan attributes, campaign metadata.
* Columns:
  * Parent hub/link key
  * Attribute(s)
  * Effective date, Load date
  * Record source

👉 *Example:*
```sql
Sat_UserDetails
+---------+-------------+----------+-----------+--------------+
| User_HK | Country     | Language | LoadDate  | RecordSource |
+---------+-------------+----------+-----------+--------------+
```

```sql
Sat_SubscriptionPlan
+-----------------+----------+--------------+-----------+--------------+
| Subscription_HK | PlanType | Price        | LoadDate  | RecordSource |
+-----------------+----------+--------------+-----------+--------------+
```

---

### 🔹 Freeletics Implementation Example (DV2 on Databricks)

At Freeletics, I implemented a **DV 2.0 style architecture on Databricks with Delta Lake**, focusing on **CDC (Change Data Capture), history tracking, and governance**:

* **Hub_User** stored immutable user IDs.
* **Hub_Subscription** stored subscription IDs.
* **Link_Subscription** connected users with their subscriptions over time.
* **Sat_UserDetails** tracked changing user attributes like email, language, or country.
* **Sat_SubscriptionPlan** historized subscription tier changes (Free, Premium, Family) and price changes.
* **Hub_Campaign** represented marketing campaigns, with a **Link_UserCampaign** capturing which users were targeted.
* Implemented **CDC using Delta Lake MERGE** to capture user profile and subscription updates.
* Used **Delta Time Travel** for historization and audit.
* Embedded **data quality checks** with **Great Expectations** (e.g., User_ID not null, subscription price within expected range).
* Integrated **Unity Catalog** for schema/catalog management (Bronze, Silver, Gold), fine-grained access, and lineage tracking.
* Built **CI/CD pipelines with GitHub Actions** for automated validation and deployment.

👉 *Result:* Finance could accurately report on subscription revenue by date, Product teams could track plan migrations, and Marketing could analyze campaign performance historically.

---

### 🔹 Medallion Architecture (Databricks)

We followed the **Medallion Architecture** (Bronze → Silver → Gold) as the layering principle:

* **Bronze (Raw Ingest):** Landing raw user events, campaign logs, subscription transactions.
* **Silver (Cleansed / Modeled):** Applied DV 2.0 modeling with Hubs (User, Subscription, Campaign), Links (User-Subscription, User-Campaign), Satellites (UserDetails, SubscriptionPlan, CampaignMetadata).
* **Gold (Curated / Marts):** Exposed Star Schema facts/dimensions for KPIs: subscription funnel, churn rates, campaign ROI.

👉 This layering ensured clear separation of concerns: raw data preserved in Bronze, governed enterprise model in Silver, and business-friendly marts in Gold.

![Medallion Architecture](https://databricks.com/wp-content/uploads/2023/06/medallion-architecture.png)

---

### 🔹 Why It’s Valuable (for cosnova)

1. **Audit Trail** → e.g., track historical campaign targeting or subscription changes.
2. **Schema Evolution** → add new campaign types or user attributes without redesign.
3. **Traceability** → full lineage from raw user events → DV layer → KPI dashboards.
4. **Data Quality** → validated via Great Expectations before business consumption.
5. **Governance** → Unity Catalog controlled access and provided lineage.

👉 **Interview Soundbite:**
*"At Freeletics, we applied DV 2.0 in the Silver layer with Unity Catalog for governance and Great Expectations for quality checks. On top, we exposed Gold layer Star Schema marts — e.g., Fact_SubscriptionEvents with Dim_User and Dim_Subscription — which powered churn prediction and campaign ROI dashboards. This balance of auditability and simplicity is exactly what I see cosnova needing for products, prices, and campaigns."*

---

# 📌 Star Schema (on top of DV 2.0)

### 🔹 Core Idea

* Analysts don’t want to query Hubs/Links/Satellites directly.
* So we **transform Data Vault → Star Schema marts** (Facts + Dimensions).
* This is the **semantic layer** used for BI & reporting.

---

### 🔹 Example Transformation (Freeletics-specific)

From DV 2.0:

* **Hub_User + Sat_UserDetails** → becomes **Dim_User**
* **Hub_Subscription + Sat_SubscriptionPlan** → becomes **Dim_Subscription**
* **Link_Subscription + Sat_SubscriptionEvents** → becomes **Fact_SubscriptionEvents**
* **Hub_Campaign + Sat_CampaignMetadata** → becomes **Dim_Campaign**
* **Link_UserCampaign** → part of **Fact_CampaignEngagement**

---

**Fact_SubscriptionEvents**
| Event_ID | Date_Key | User_Key | Subscription_Key | EventType | Revenue |

**Dim_User**
| User_Key | Country | Language | SignupDate |

**Dim_Subscription**
| Subscription_Key | PlanType | Price | ValidFrom | ValidTo |

**Fact_CampaignEngagement**
| Engagement_ID | User_Key | Campaign_Key | Clicks | Conversions |

---

### 🔹 Why It’s Valuable (Freeletics)

* BI teams tracked **subscription funnel metrics** (trial → paid → churn) via Fact_SubscriptionEvents.
* Finance validated **historical revenue** by joining Dim_Subscription with Fact_SubscriptionEvents.
* Marketing analyzed **campaign ROI** by combining Fact_CampaignEngagement with Dim_Campaign.
* Data Science built **churn models** using Dim_User + Fact_SubscriptionEvents features.

---

### 🔹 Why It’s Valuable (for cosnova)

1. **Ease of Use** → Analysts see simple facts/dims, not complex DV tables.
2. **Performance** → Optimized joins for BI dashboards.
3. **Business Alignment** → KPIs directly exposed (e.g., sales by campaign, pricing changes over time).
4. **Flexibility** → Backed by DV 2.0 for audit/history.

👉 **Interview Soundbite:**
*"At Freeletics, I transformed DV 2.0 into Star Schema marts like Fact_SubscriptionEvents, Dim_User, and Dim_Campaign, enabling finance, marketing, and product teams to access reliable KPIs. I see cosnova following the same pattern — DV for governance and history, Star Schema for fast business insights."*

---

✅ With Freeletics-specific examples (users, subscriptions, campaigns), your story is **authentic, easy to remember, and perfectly transferable** to cosnova’s domain.

