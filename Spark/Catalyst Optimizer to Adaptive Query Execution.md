# Catalyst Optimizer to Adaptive Query Execution (AQE)

## Apache Spark 3.0 Adaptive Query Execution

Spark SQL is one of the most valuable components of Apache Spark, powering both SQL queries and the DataFrame API. At its core is the Catalyst optimizer, a powerful and extensible query optimizer leveraging advanced Scala features. With the release of Apache Spark 3.0, Adaptive Query Execution (AQE) introduces runtime query optimization, addressing some of the limitations of rule-based optimization.

---

## Relationship Between Catalyst Optimizer and AQE:
Catalyst Optimizer: A foundational query optimization framework in Spark that operates before the query execution begins. It applies rule-based and cost-based optimizations during query planning to generate the best initial query execution plan.

AQE: Introduced in Spark 3.0, AQE enhances the Catalyst Optimizer by enabling runtime query optimization. While the Catalyst Optimizer creates the initial plan, AQE modifies and improves it dynamically as the query runs based on real-time statistics.

---

## Catalyst Optimizer: Workflow Overview

The Catalyst optimizer applies optimizations during both logical and physical planning stages, aiming to execute queries efficiently. Below is an overview of its workflow:

1. **Unresolved Logical Plan**: The optimizer accepts an unresolved logical plan and checks for syntax errors.
2. **Logical Plan**: Names in the unresolved logical plan are resolved using the catalog.
3. **Optimized Logical Plan**: The query order is reorganized for maximum efficiency.
4. **Physical Plans**: Multiple physical plans are generated, outlining execution strategies.
5. **Selected Physical Plan**: The best physical plan is chosen based on a cost model.
6. **RDDs**: The selected physical plan is converted into RDDs, and bytecode for the JVM is generated.

### Catalyst Optimizer Workflow
<img src="/images/CatalystOptimizer.png" alt="Open" style="width:100%"/>

### Limitations of Rule-Based Optimization in Spark 2.X

In Spark 2.X, all optimizations were based on static estimations made before runtime. This could lead to suboptimal plans due to inaccuracies in these estimations or unforeseen runtime conditions.

---

## Adaptive Query Execution (AQE)

AQE enhances query optimization by dynamically adjusting query plans based on runtime statistics collected during query execution. This eliminates the need for static estimations and allows Spark to re-optimize queries for better performance.

###  Adaptive Query Execution Workflow
<img src="/images/AQE.png" alt="Open" style="width:100%"/>

### Key Features of AQE

1. **Dynamically Switching Join Strategies**
   - In Spark 2.X, join strategies relied on size estimations that could be inaccurate.
   - AQE replans join strategies at runtime, enabling optimal selection such as converting sort-merge joins to broadcast hash joins based on actual data sizes.

2. **Dynamically Coalescing Shuffle Partitions**
   - Determining the optimal number of shuffle partitions is challenging.
   - AQE combines adjacent small partitions into larger ones at runtime, improving efficiency by reducing disk spills and network fetches.

3. **Dynamically Optimizing Skew Joins**
   - Data skew leads to performance degradation due to uneven partition sizes.
   - AQE splits skewed partitions into smaller subpartitions, distributing the workload evenly and enhancing performance.

---

## Why AQE is Disabled by Default

Despite its potential to improve query performance, AQE is disabled by default in Spark 3.0 for several reasons:

1. **Backward Compatibility**:
   - Many Spark users and organizations have production pipelines configured to work with the traditional Catalyst Optimizer.
   - Enabling AQE by default could introduce unexpected behavior in existing workflows.

2. **Runtime Overhead**:
   - AQE requires Spark to collect runtime statistics, which adds some overhead, especially for small or simple queries where the performance benefit might not outweigh the cost.

3. **Stability and Maturity**:
   - When Spark 3.0 was released, AQE was a relatively new feature, and developers may have been cautious about enabling it by default until it proved stable and effective across diverse workloads.

4. **Use Case Specific**:
   - AQE is most beneficial for complex, large-scale queries involving joins, aggregations, and skewed data. For simpler workloads, traditional query optimization might be sufficient, and AQE might not provide noticeable gains.

5. **User Control**:
   - Spark developers opted to give users the flexibility to enable AQE when they see fit. This allows advanced users to evaluate its benefits in their specific scenarios without forcing it on everyone.

### When Should You Enable AQE?

You should enable AQE (`spark.sql.adaptive.enabled = true`) if:
- Your workload involves large datasets, complex joins, or skewed data distributions.
- You need to optimize shuffle operations dynamically.
- Your queries are suffering from performance issues due to suboptimal plans generated by static estimations.

---

## Detailed Example: AQE Features

### Dynamically Coalescing Shuffle Partitions

When running queries with large datasets, shuffle operations redistribute data across the cluster. Incorrect partition numbers can lead to inefficiencies. AQE resolves this by:

- Starting with a large number of shuffle partitions.
- Combining adjacent small partitions at runtime based on shuffle file statistics.

Example: If a query initially generates five shuffle partitions but three are very small, AQE combines them into one, reducing the number of tasks required.

### Dynamically Switching Join Strategies

Broadcast hash joins are efficient when one side of the join fits in memory. AQE dynamically converts sort-merge joins to broadcast hash joins if runtime statistics reveal a smaller-than-estimated dataset size.

### Dynamically Optimizing Skew Joins

In cases of data skew, AQE:

- Detects skewed partitions based on shuffle statistics.
- Splits large partitions into smaller subpartitions.
- Joins subpartitions with corresponding partitions from the other side, balancing workload and improving performance.

---

## Enabling AQE

AQE is disabled by default in Spark 3.0. To enable it, set the following configuration:

```bash
spark.sql.adaptive.enabled = true
```

### Criteria for AQE Application

- Queries must not be streaming queries.
- Queries must contain at least one exchange (e.g., joins, aggregates, or window operators) or subquery.

---

## Advantages of AQE

1. **Improved Query Performance**
   - Plans are optimized as the query runs, adapting to actual runtime conditions.

2. **Reduced Manual Effort**
   - AQE eliminates the need for extensive statistics collection or manual Spark configuration tuning.

3. **Resilience to Data Variability**
   - AQE adapts to changes in data distribution, size, and complexity, ensuring robust query optimization.

---

## Conclusion

Adaptive Query Execution is a transformative feature in Apache Spark 3.0, enhancing query optimization by making it dynamic and data-driven. By addressing the limitations of static optimization, AQE simplifies configuration and delivers superior performance for a wide range of workloads. 

---

## References

1. [Apache Spark 3.0 Adaptive Query Execution](https://towardsdatascience.com/apache-spark-3-0-adaptive-query-execution-2359e87ae31f)
2. [Databricks Blog on AQE](https://www.databricks.com/blog/2020/05/29/adaptive-query-execution-speeding-up-spark-sql-at-runtime.html)

![AQE Workflow Image](image-by-author-tag)

