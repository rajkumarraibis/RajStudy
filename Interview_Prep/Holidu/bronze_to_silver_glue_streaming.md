# Glue Streaming Job Walkthrough (Bronze → Silver → Gold)

This document explains how AWS Glue Streaming jobs process data in our pipeline,
and why they look very similar to Apache Spark Structured Streaming code.

---

## 🔹 Why Glue Streaming == Spark Structured Streaming

- **Glue Streaming is built on Spark Structured Streaming**.  
  - Your code looks like `spark.readStream` and `df.writeStream`.  
  - Glue wraps it inside its managed job execution environment.  
- **Differences from raw Spark**:
  - Cluster provisioning & scaling → handled by Glue (you just choose DPUs).  
  - Checkpointing → persisted in S3 (you configure path).  
  - IAM integration → native to AWS.  
  - Built-in connectors for **Kafka/MSK, Kinesis Streams**.  

---

## 🔹 Typical Flow

1. **Raw events** land in **Bronze S3** via Firehose/Kafka.  
2. **Glue Streaming job** reads from Kafka (or Firehose output in S3).  
3. Apply **schema enforcement, validation, deduplication, DQ checks**.  
4. Write curated results into **Silver S3**.  
5. Optionally enrich & aggregate → write into **Gold layer** (query-ready).  

---

## 🔹 Example Glue Streaming Job (Bronze → Silver)

```python
import sys
from awsglue.context import GlueContext
from pyspark.context import SparkContext
from pyspark.sql.types import StructType, StructField, StringType, LongType

# Create Spark + Glue contexts
sc = SparkContext()
glueContext = GlueContext(sc)
spark = glueContext.spark_session

# ✅ Define schema explicitly (Structured Streaming does not allow schema inference)
schema = StructType([
    StructField("event_id", StringType(), True),
    StructField("user_id", StringType(), True),
    StructField("timestamp", LongType(), True),
    StructField("event_type", StringType(), True),
    StructField("payload", StringType(), True)
])

# 🔹 SOURCE: Read from Kafka (preferred for real-time Bronze ingestion)
# -----------------------------------------------------------------------------
# This block configures Spark Structured Streaming to connect to Kafka.
# In Glue Streaming, this is the most common entry point for real-time pipelines.
# -----------------------------------------------------------------------------

raw_stream = (spark.readStream                 # Start a streaming DataFrame reader
    .format("kafka")                           # Use Spark's built-in Kafka source
                                               # (Glue has this connector pre-installed)

    .option("kafka.bootstrap.servers", 
            "b-1.msk-cluster:9092")            # REQUIRED: Comma-separated list of Kafka brokers
                                               # Acts as the entry point into the Kafka cluster
                                               # In AWS MSK, this will be your broker endpoints
                                               # Note: Spark will discover the rest of the cluster from here

    .option("subscribe", "booking_events")     # REQUIRED: The topic(s) to consume from
                                               # Here, "booking_events" is where app/frontend logs
                                               # all user booking-related events
                                               # Alternative: use "assign" to bind specific partitions,
                                               # or "subscribePattern" with regex for multiple topics

    .option("startingOffsets", "latest")       # Optional: Where to start reading
                                               # "latest" = only new events from now onwards
                                               # "earliest" = consume backlog from partition 0 offset
                                               # Useful for replaying history (but can overload cluster)
                                               # In prod, "latest" is safer for real-time processing

    # 🔹 Other optional tuning knobs (not shown here, but good to mention):
    # .option("maxOffsetsPerTrigger", 5000)    # Throttle ingestion to X messages per micro-batch
    # .option("failOnDataLoss", "false")       # Handle deleted segments gracefully
    # .option("kafka.security.protocol", "SSL")# For secured MSK clusters

    .load()                                    # Execute and return a streaming DataFrame
                                               # Schema returned:
                                               #  key (binary), value (binary),
                                               #  topic (string), partition (int),
                                               #  offset (long), timestamp (ts),
                                               #  timestampType (int)
)


# 🔹 PARSE: Kafka value is in bytes → cast to string and parse JSON
from pyspark.sql.functions import col, from_json
parsed = (raw_stream
    .selectExpr("CAST(value AS STRING)")
    .select(from_json(col("value"), schema).alias("data"))
    .select("data.*")
)

# 🔹 TRANSFORM: Example DQ + deduplication
# - Drop rows without mandatory fields
# - Deduplicate using event_id
cleaned = (parsed
    .filter(col("event_id").isNotNull())
    .dropDuplicates(["event_id"])
)

# 🔹 SINK: Write to Silver layer (Parquet/Delta/Iceberg)
query = (cleaned.writeStream
    .format("parquet")                 # could also be "delta" or "iceberg"
    .option("path", "s3://my-bucket/silver/booking/")
    .option("checkpointLocation", "s3://my-bucket/checkpoints/bronze_to_silver/")
    .outputMode("append")              # append-only (streaming style)
    .trigger(processingTime="1 minute") # micro-batch interval
    .start()
)

query.awaitTermination()
```

---

## 🔹 Notes

- **Checkpointing** (`checkpointLocation`) is critical:  
  - Stores offsets, progress, and metadata.  
  - Guarantees *exactly-once* semantics if sinks are idempotent.  
- **Deduplication** ensures idempotency when upstream retries (e.g., Firehose/Kafka resend).  
- **Silver output** can be Delta or Iceberg for ACID + schema evolution.  
- **Gold transformations** may run in a second job (batch or stream) to generate aggregates, dashboards, and ML features.

---

## 🔹 Gold Job (Silver → Gold)

- Same structure, but source = Silver tables (Parquet/Delta/Iceberg).  
- Transformations: joins, enrichments, rollups.  
- Sink: Gold S3 → queryable via Athena/Redshift Spectrum.  

```python
silver_df = spark.readStream.format("delta").load("s3://my-bucket/silver/booking/")

gold_df = silver_df.groupBy("user_id").count()

query = (gold_df.writeStream
    .format("delta")
    .option("path", "s3://my-bucket/gold/booking_summary/")
    .option("checkpointLocation", "s3://my-bucket/checkpoints/silver_to_gold/")
    .outputMode("complete")   # overwrite aggregates
    .start()
)
```

---

# ✅ Takeaways
- Glue Streaming jobs **are Spark Structured Streaming** jobs.  
- Difference is in **execution environment** (AWS-managed, DPUs, IAM).  
- Use **checkpointing** for consistency, **schemas** for validation, and **deduplication** for idempotency.  
- Output layers: **Silver = cleansed detail**, **Gold = enriched aggregates**.  
