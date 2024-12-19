# [This Spark Code is Slower Than a Snail! Let’s Optimize It](https://medium.com/plumbersofdatascience/this-spark-code-is-slower-than-a-snail-lets-optimize-it-dbe6736c784d)

## The Most Common Performance Problems

Performance issues in Spark are mostly related to the following topics:

- **Skew**: Occurs when there is an imbalance in the size of data partitions.
- **Spill**: Writing of temporary files to disk due to lack of memory.
- **Shuffle**: Moving data between executors due to a wide transformation.
- **Storage**: The way data is stored on disk actually matters.
- **Serialization**: The distribution of code across the cluster (UDFs are inefficient).

---

## Mitigating Skew

To handle data skew, we can:

- **Enable AQE** (Adaptive Query Execution) if using Spark 3.
- **Use Skew Hint** (Skew Join Optimization) if on Databricks.
- **Apply Key Salting**: Salt the skewed column with a random number to create a better distribution across partitions at the cost of extra processing.

---

## Mitigating Spill

If stages are spilling, try the following:

1. **Check for Skew**: Resolve data skew first if it causes spilling.
2. **Increase Worker Memory**: Ensure partitions fit in memory to reduce disk writes.
3. **Reduce Partition Size**: Increase the number of partitions by tuning:
   - `spark.sql.shuffle.partitions`
   - `spark.sql.maxPartitionBytes`
   - Explicitly use `repartition`.

---

## Mitigating Shuffles

Shuffles are resource-intensive. Reduce their impact by:

1. **Use Fewer, Larger Workers**: This minimizes network traffic.
2. **Reduce Data Being Shuffled**:
   - Filter unnecessary rows and columns before wide transformations.
3. **Denormalize Datasets**:
   - Persist frequently queried datasets in the data lake.
4. **Broadcast Smaller Tables**:
   - Use `.broadcast(df)` for smaller tables.
   - Tune `spark.sql.autoBroadcastJoinThreshold` for larger broadcast joins (default: 10MB).
5. **Bucketed Datasets**:
   - Pre-shuffle and store data by buckets for repeated joins.
   - Ensure all tables involved are bucketed with the same number of buckets.

---

## Storage

### Tiny Files

Tiny files (smaller than 128MB) lead to performance issues due to overhead in opening/closing files.

Mitigation strategies:
- Compact small files to match block size.
- Configure ingestion tools to write larger files.
- For Spark jobs:
  - Tune `spark.sql.shuffle.partitions` (default: 200).
  - Use `repartition()` or `coalesce()`.
  - In Spark 3+, enable AQE with `spark.sql.adaptive.coalescePartitions.enabled = true`.

### Schema Problems

Avoid inferring schemas to prevent data scanning. Always provide explicit schemas.

Solutions:
- Define schemas explicitly.
- Register datasets as tables in the Hive Metastore.
- Use Delta format for schema evolution support.

---

## Serialization

Serialization issues arise with non-native API transformations (e.g., UDFs), particularly in Python.

Mitigation strategies:
- Avoid UDFs where possible; use native Spark high-order functions.
- If UDFs are unavoidable:
  - Use Pandas UDFs in Python (uses PyArrow for batch processing).
  - Avoid standard Python UDFs, which serialize records individually and cause overhead.

---

## Advanced Optimization Techniques

To further enhance Spark performance, consider the following strategies:

### 1. **Optimize Data Serialization**

Efficient serialization reduces memory overhead and speeds up data processing.

- **Use Kryo Serialization**: Kryo is a faster and more efficient serialization framework compared to Java's default serialization. Configure Spark to use Kryo by setting `spark.serializer` to `org.apache.spark.serializer.KryoSerializer`. ([Source](https://sparkbyexamples.com/spark/spark-performance-tuning/))

  ```python
  from pyspark import SparkConf
  conf = SparkConf().set("spark.serializer", "org.apache.spark.serializer.KryoSerializer")
  ```

### 2. **Tune Parallelism**

Adjusting the level of parallelism can better match the cluster’s resources, reducing the duration of shuffle operations.

- **Set Parallelism Levels**: Configure `spark.default.parallelism` and `spark.sql.shuffle.partitions` to higher values to enhance parallelism. ([Source](https://blogs.perficient.com/2024/06/18/the-quest-for-spark-performance-optimization-a-data-engineers-journey/))

  ```python
  from pyspark import SparkConf
  conf = SparkConf().set("spark.default.parallelism", "200")
  conf = conf.set("spark.sql.shuffle.partitions", "200")
  ```

### 3. **Leverage DataFrames and Datasets**

Using DataFrames and Datasets instead of RDDs can improve performance due to optimized query execution plans and the Catalyst optimizer. ([Source](https://sparkbyexamples.com/spark/spark-performance-tuning/))

  ```python
  # Using DataFrame API
  df = spark.read.json("data.json")
  ```

### 4. **Implement Caching and Persistence**

Caching frequently accessed datasets in memory can significantly speed up processing times by avoiding recomputation. ([Source](https://moldstud.com/articles/p-optimizing-spark-performance-techniques-for-speeding-up-processing-times))

  ```python
  # Cache DataFrame
  df.cache()
  ```

### 5. **Optimize Joins with Broadcast Variables**

Broadcasting small datasets to all worker nodes can minimize data shuffling during join operations, improving performance. ([Source](https://www.cloudthat.com/resources/blog/optimization-techniques-for-high-speed-big-data-processing-in-spark))

  ```python
  from pyspark.sql.functions import broadcast
  result = large_df.join(broadcast(small_df), "key")
  ```

### 6. **Configure Memory and Executors**

Properly configuring memory and executor settings is crucial for optimizing Spark performance. Allocate sufficient memory to Spark executors and adjust the memory overhead to prevent out-of-memory errors and improve processing efficiency. ([Source](https://moldstud.com/articles/p-optimizing-spark-performance-techniques-for-speeding-up-processing-times))

  ```bash
  # Example Spark submit command with memory and executor configurations
  spark-submit --executor-memory 4G --executor-cores 4 --driver-memory 2G
  ```

### 7. **Select Appropriate File Formats**

Choosing efficient file formats like Parquet or ORC can enhance performance due to their columnar storage and compression capabilities. ([Source](https://www.cloudthat.com/resources/blog/optimization-techniques-for-high-speed-big-data-processing-in-spark))

  ```python
  # Reading data in Parquet format
  df = spark.read.parquet("data.parquet")
  ```

---

Implementing these advanced optimization techniques can lead to significant improvements in Spark job performance, resource utilization, and overall efficiency. Regularly monitoring and tuning your Spark applications based on workload characteristics and cluster resources is essential for maintaining optimal performance.

