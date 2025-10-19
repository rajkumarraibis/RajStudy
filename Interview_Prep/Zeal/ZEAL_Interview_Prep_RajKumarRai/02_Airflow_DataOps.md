# Airflow & DataOps

We use databricks as our Orchstrator.
I am equally comfortable in airfloe as well. 
we use it for some of our workloads\jobs I’ve implemented DAGs that ensure reliability, modularity, and traceability — following DataOps principles.

## Key Practices

- **DAG Design:** Modular, parameterized DAGs with well-defined dependencies and retries. 
- **Monitoring:** Integrated Slack alerts, Airflow callbacks, and CloudWatch logs for proactive failure detection.
- **Testing & CI/CD:** All DAGs and Spark jobs are version-controlled in Git, validated via pre-merge tests, and deployed through CI pipelines.
- **Data Quality:** Added validation tasks (using Great Expectations or PyDeequ) directly in the DAGs.
- **Automation:** Dynamic task generation for daily partition runs, eliminating manual triggers.

## Takeaway

I would emphasize how these practices reduce failure rates and enable end-to-end visibility. ZEAL’s focus on DataOps and GitOps resonates strongly with how I’ve standardized orchestration and automation at scale.
