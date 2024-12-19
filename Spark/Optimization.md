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

Optimizing Spark performance requires addressing these common issues effectively to enhance processing speed and resource utilization.
