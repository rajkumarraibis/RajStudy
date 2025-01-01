# Apache Spark Architecture

Apache Spark is an open-source, distributed computing system designed for fast and flexible data processing. It provides a unified analytics engine, supporting batch processing, streaming, machine learning, and graph processing.

## Key Components of Spark Architecture

### 1. **Driver Program**
   - Acts as the central controller of a Spark application.
   - Converts user-defined transformations and actions into a Directed Acyclic Graph (DAG) of stages.
   - Schedules and coordinates the execution of tasks across the cluster.

### 2. **Cluster Manager**
   - Responsible for resource allocation and task scheduling.
   - Supports multiple cluster managers like:
     - Standalone cluster manager (built-in)
     - Apache Mesos
     - Hadoop YARN
     - Kubernetes

### 3. **Executors**
   - Worker nodes that run individual tasks assigned by the driver program.
   - Store data in memory or disk as required.
   - Report status and results back to the driver.

### 4. **Tasks**
   - The smallest unit of execution in Spark.
   - A stage is split into multiple tasks, each of which processes a partition of the data.

### 5. **RDD (Resilient Distributed Dataset)**
   - Core data structure in Spark.
   - Immutable, fault-tolerant distributed collections of data.
   - Supports lazy transformations and actions.

## Spark Execution Flow

1. **Application Submission**:
   - A Spark application is submitted by a user through the Spark-submit script.

2. **DAG Creation**:
   - The driver program creates a DAG of stages from user-defined transformations.

3. **Job Execution**:
   - The DAG is divided into stages, each stage containing tasks that are sent to executors for execution.

4. **Task Execution**:
   - Executors process the tasks in parallel, performing operations on partitions of the data.

5. **Result Collection**:
   - The results are aggregated and returned to the driver program or saved to external storage.

## Spark Cluster Modes

1. **Standalone Mode**: Uses Spark's built-in cluster manager.
2. **YARN Mode**: Integrates with Hadoop's resource management framework.
3. **Mesos Mode**: Supports Apache Mesos for resource scheduling.
4. **Kubernetes Mode**: Leverages Kubernetes for container orchestration.

## Spark Architecture Overview
Treat Sparkcontext as SparkSession
<img src="/images/spark-architecture.png" alt="Open" style="width:100%"/>

## References

- [Apache Spark Official Documentation](https://spark.apache.org/docs/latest/)
- [Spark Architecture Explained - Databricks](https://www.databricks.com/spark/about)
- [Introduction to Spark RDD](https://spark.apache.org/docs/latest/rdd-programming-guide.html)

## Conclusion

Apache Spark's architecture is designed for scalability, fault tolerance, and flexibility. By leveraging in-memory processing and a distributed execution model, it has become a cornerstone for big data analytics and machine learning.
