# ⚡ Cosnova – Senior Data Engineer (Flashcard Prep)

## 🎯 Core Topics
- **DV2.0**: Hubs (keys), Links (relationships), Satellites (history).  
- **Star Schema**: Facts = events (subscriptions/products), Dims = users/customers.  
- **Governance**: Unity Catalog (schemas, ACLs, lineage).  
- **Quality**: Great Expectations → block bad data at Silver.  
- **Azure Stack**: ADLS = S3, ADF = Glue/StepFunctions, Event Hubs = Kinesis, DynamoDB = CosmosDB,Key Vault = Secrets Manager.  
- **Optimization**: Partition pruning, Z-Ordering, broadcast joins, AQE, OPTIMIZE.  
- **CDC**: Auto Loader + MERGE INTO (row-level CDC in Satellites).  
- **CI/CD**: GitHub Actions + Docker containers + GE tests + Databricks deploys.  
- **IaC**: CloudFormation (AWS) → Terraform (Azure).  
- **Observability**: SLAs, freshness dashboards, Spark UI, cost control (autoscale, spot, OPTIMIZE).  
- **Security**: PII masking (UC), Key Vault secrets, least-privilege.  

---

## 🎤 Soundbites (Drop Naturally)
- *“Unity Catalog gave us schema consistency, ACLs for PII, and lineage from raw to dashboard.”*  
- *“Partition pruning + Z-Ordering kept TB-scale Delta queries performant.”*  
- *“CDC modeled row-level in DV2 Satellites; MERGE INTO + checkpoints gave us idempotency.”*  
- *“We packaged ETL jobs in Docker, tested with GitHub Actions, then deployed to Databricks — same image everywhere.”*  
- *“In AWS I used CloudFormation; in Azure Terraform plays the same role — declarative infra in Git, deployed via CI/CD.”*  
- *“To prevent a swamp: Bronze/Silver/Gold layering, Unity Catalog governance, GE quality gates, and SLAs.”*  

---

## 🧩 Domain Mapping (Freeletics → Cosnova)
- Users → Customers.  
- Subscriptions → Products.  
- Campaigns → Promotions.  
- Fact_SubscriptionEvents → Fact_PromotionEvents.  

---

## ⚖️ Common Prompts
- **“How do you prevent a swamp?”** → Governance, GE, Medallion, SLAs.  
- **“Onboard new source?”** → Auto Loader → GE → DV2 Silver → Gold mart.  
- **“Numbers look off?”** → UC lineage trace + GE checks + CDC merge validation.  

---

## ✅ Closing Questions to Ask
- “How does Cosnova see DV2 evolving — do you already run PIT/Bridge tables?”  
- “What’s your approach to balancing self-service for analysts vs governed data access?”  
- “Where do you see the biggest opportunity for automation in your current stack?”  
