### **Topic**: "MLOps Best Practices for Scaling Machine Learning in Production"

**Why This Topic?**
- **Current Ambitions**: You're new to Machine Learning and preparing for interviews, so understanding how to operationalize ML models will provide a solid foundation.
- **Industry Trends**: As a Senior Data Engineer, expertise in MLOps bridges the gap between engineering and machine learning, making you a stronger candidate for future roles.
- **Relevance to Your Role**: Your experience in cloud technologies like AWS and GCP aligns well with MLOps practices, which often involve these platforms.
- **Interview Edge**: Knowledge of MLOps demonstrates a practical understanding of deploying and monitoring ML models, which is highly valued.

# Table of Contents:
1. **Introduction to MLOps**:
   - [What is MLOps ?](#what-is-mlops-)
   - [Key components - CI/CD pipelines, monitoring, and automation](#key-components)
   - [Difference between MLOps and DevOps](#difference-between-mlops-and-devops)
   
3. **CI/CD Pipelines for ML**:
   - [CI/CD Pipelines for ML](#ci-cd-pipelines-for-ml)
   
5. **Data Management in MLOps**:
   - [Feature Engineering](#feature-engineering)
   
## What is MLOps ?
MLOps stands for Machine Learning Operations. MLOps is a core function of Machine Learning engineering, focused on streamlining the process of taking machine learning models to production, and then maintaining and monitoring them. MLOps is a collaborative function, often comprising data scientists, Data Engineers 
, devops engineers and IT.

<img src="/images/mlops-loop-en.jpg" alt="MLOps" style="width:50%"/>



## Key Components
## CI/CD pipelines, monitoring, and automation
### **1. CI/CD Pipelines**
- **[Jenkins](https://www.jenkins.io/)**: Automation server for building and deploying ML models.
- **[GitHub Actions](https://github.com/features/actions)**: Automates workflows directly from GitHub repositories.
- **[GitLab CI/CD](https://docs.gitlab.com/ee/ci/)**: Provides integrated pipeline automation for ML.
- **[Azure DevOps](https://azure.microsoft.com/en-us/products/devops/)**: Streamlined CI/CD with integration into Azure Machine Learning.

---

### **2. Monitoring**
- **[Seldon Core](https://docs.seldon.io/projects/seldon-core/en/latest/)**: For monitoring and managing ML models in production.
- **[WhyLabs](https://whylabs.ai/)**: AI observability and data quality monitoring tool.
- **[Amazon CloudWatch](https://aws.amazon.com/cloudwatch/)**: Tracks metrics and logs for models deployed on AWS.

---

### **3. Automation**
#### **Model Training and Deployment**
- **[Kubeflow](https://www.kubeflow.org/)**: Orchestrates ML workflows on Kubernetes.
- **[MLflow](https://mlflow.org/)**: Open-source platform to manage the ML lifecycle.
- **[Amazon SageMaker Pipelines](https://aws.amazon.com/sagemaker/pipelines/)**: Automates and scales ML workflows on AWS.

#### **Data Pipelines**
- **[Databricks Workflow](https://www.databricks.com/product/workflows)**: Databricks Workflow orchestration for data and ML pipelines.
- **[Apache Airflow](https://airflow.apache.org/)**: Workflow orchestration for data and ML pipelines.

---

The key difference between **MLOps** and **DevOps** lies in the domain they serve and the challenges they address:

---
## Difference between MLOps and DevOps

### **1. Purpose**
- **DevOps**:
  - Focuses on software development and operational workflows.
  - Ensures seamless integration, testing, deployment, and monitoring of traditional software applications.

- **MLOps**:
  - Extends DevOps practices to machine learning workflows.
  - Focuses on managing the complexities of data, model training, deployment, and monitoring in ML systems.


### **2. Core Components**
| Aspect             | DevOps                                   | MLOps                                  |
|---------------------|------------------------------------------|----------------------------------------|
| **Primary Focus**  | Code and software deployment pipelines. | Data, models, and ML workflows.        |
| **Key Artifacts**  | Source code, binaries, configurations.   | Code, datasets, trained models, features. |
| **Dependencies**   | Application libraries and environments.  | Data pipelines, model training processes. |


### **3. Lifecycle**
- **DevOps**:
  - Development → Integration → Testing → Deployment → Monitoring.
  - Focuses on static artifacts like software binaries.

- **MLOps**:
  - Data collection → Model training → Validation → Deployment → Continuous Monitoring.
  - Adds dynamic elements like datasets, model versions, and retraining workflows.

### CI CD Pipelines for ML
**Continuous Integration and Versioning of Models**  
Regularly update and test models while tracking every change to ensure consistency, reproducibility, and easy rollback.  
*Example*: Every time you modify a model’s code or data, a pipeline automatically trains, tests, and stores a new, versioned model artifact.

**Automating Model Retraining and Deployment**  
Automatically re-train and deploy new model versions based on defined triggers like drops in accuracy, signs of data drift, or model atrophy.  
*Example*: If the model’s performance declines or incoming data changes significantly, a pipeline retrains the model with fresh data. Once it passes validation checks, it’s immediately put into production.

**Model CI CD helps in tackling following issues**

**Data Drift**  
Imagine you use a **Logistic Regression** model to predict whether an online shopper will make a purchase. Initially, your training data shows that most buyers are young adults using desktop computers. Over time, however, more older adults and mobile users start visiting your site. The demographic and device usage patterns shift, causing the model’s input data to differ significantly from what it was trained on. This is data drift—your model still tries to use the old pattern (young desktop users) on new, very different data (older mobile users), leading to poorer predictions.

**Model Atrophy**  
Consider a **Random Forest** model recommending specific products to users of a streaming music service. When the model was created, it learned to associate certain listening habits with particular product preferences. Over the next few months, user tastes change due to new music trends, popular culture shifts, or even seasonal events. While the actual data features (like track play count, time spent on the app) might still look similar, the underlying relationship between user behavior and product preferences no longer holds. Even though the model sees data of the same “type,” it’s now predicting based on outdated associations. This leads to model atrophy: the model’s usefulness fades, and its predictive accuracy declines because the fundamental logic it relied on no longer applies.

### Feature Engineering
Refers to the process of transforming raw data into a set of features that better represent the underlying problem to the predictive models. This often involves:

- **Creating new features:** Combining or manipulating existing data columns to generate more informative inputs (e.g., turning raw timestamps into hour-of-day or day-of-week features).
- **Selecting relevant features:** Identifying which features are most predictive of the target and removing those that add noise or complexity.
- **Normalizing and scaling:** Adjusting data ranges so that large-valued features do not overly dominate the model.
- **Encoding categorical variables:** Converting non-numeric categories into numeric formats, such as one-hot encoding or ordinal encoding.

**Handling Feature Engineering Pipelines** involves automating and systematizing the entire feature engineering process, typically using tools and frameworks that ensure consistency and reproducibility. By defining a pipeline, you can:

- **Apply transformations consistently:** Every time new data arrives, the same sequence of steps (e.g., normalization, encoding) is applied in the same way.
- **Version and track changes:** Keep track of how features are generated and modified over time.
- **Make deployment easier:** The same pipeline can be applied both during training and at inference time to ensure that the model receives data in the expected format.
- **Integrate with CI/CD systems:** If the feature engineering pipeline is part of a continuous integration workflow, any code change to feature processing triggers automated tests, validation, and updates to the deployed model environment.
