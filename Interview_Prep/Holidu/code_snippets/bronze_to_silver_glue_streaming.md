# Glue Streaming Job Walkthrough (Bronze → Silver → Gold)

This document explains how **AWS Glue Streaming** (Spark Structured Streaming under the hood) processes
events from **Kafka/MSK** into **Silver (Iceberg)** and how **Silver → Gold** is produced using **Iceberg tables**
that remain physically stored as **Parquet** in Amazon S3.

> **Key idea:** *Iceberg is a **table** format (metadata + manifests) layered on top of Parquet files.*  
> You get ACID transactions, schema/partition evolution, and time travel. Athena and Redshift Spectrum can query Iceberg directly via the **Glue Data Catalog**.

---

## 🔹 Why Glue Streaming == Spark Structured Streaming

- Glue Streaming is **built on Spark Structured Streaming**. Your code uses `.readStream` and `.writeStream`.
- Glue adds: managed provisioning (DPUs), IAM integration, logging (CloudWatch), built‑in connectors (Kafka/MSK, Kinesis).
- You still control schemas, checkpoints, and sinks exactly like Spark Streaming.

---

## 🔹 Typical Flow

1. **Raw events** → Kafka/MSK topic(s). (Firehose may also persist raw to **S3 Bronze** for archive/replay.)  
2. **Glue Streaming job** consumes **Kafka** → validates schema, filters by consent, dedupes → writes to **Silver (Iceberg)**.  
3. **Silver → Gold**: a **Glue Batch job** (or a second streaming job) reads **Silver (Iceberg)**, enriches/aggregates, and writes **Gold (Iceberg)**.  
4. **BI**: Athena / Redshift Spectrum / QuickSight query **Iceberg** tables via **Glue Catalog**.

---

## 🔹 Streaming Source: Kafka/MSK 

```python
# Create Spark + Glue contexts
from awsglue.context import GlueContext
from pyspark.context import SparkContext
from pyspark.sql import functions as F, types as T

sc = SparkContext()
glueContext = GlueContext(sc)
spark = glueContext.spark_session

# ✅ Define the canonical event schema (versioned in Git/Registry)
schema = T.StructType([
    T.StructField("event_id", T.StringType(), True),
    T.StructField("user_id", T.StringType(), True),
    T.StructField("occurred_at", T.TimestampType(), True),  # business time
    T.StructField("gdpr_consent", T.BooleanType(), True),
    T.StructField("listing_id", T.StringType(), True),
    T.StructField("price", T.DoubleType(), True),
    T.StructField("currency", T.StringType(), True),
    T.StructField("event_type", T.StringType(), True),
    T.StructField("payload", T.StringType(), True)          # nested JSON as string (optional)
])


# -----------------------------------------------------------------------------
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


# Convert kafka stream to dataframe
from pyspark.sql.functions import col, from_json

# 🔹 STEP 1: Kafka delivers messages in binary format
# - Columns: key (binary), value (binary), topic, partition, offset, timestamp...
# - The actual event payload is inside the `value` column (binary).
# - Producers (e.g., Holidu frontend/backend) usually publish JSON payloads.

df_parsed = (
    raw_stream
        # 🔹 STEP 2: Convert binary Kafka "value" → string (assume JSON payload)
        # Kafka sends raw bytes → we CAST to STRING so Spark can interpret it as JSON text.
        .selectExpr("CAST(value AS STRING) AS raw")

        # 🔹 STEP 3: Parse JSON string into structured fields
        # - from_json() takes JSON text + schema (no inference allowed in streaming).
        # - The schema usually comes from AWS Glue Catalog (keeps it consistent).
        # - Returns a STRUCT column called `e` with typed fields.
        .select(from_json(col("raw"), schema).alias("e"))

        # 🔹 STEP 4: Flatten struct into top-level columns
        # - e.* expands all fields inside the struct into normal DataFrame columns.
        # - Example: booking_id, user_id, amount, timestamp
        .select("e.*")
)

# ✅ df_parsed is now a Streaming DataFrame with schema-enforced, tabular columns:
# booking_id | user_id | amount | created_at | ...
# This is the clean Bronze → Silver ingestion step.

```

---

## 🔹 Transform: consent, DQ, idempotency (dedupe)

```python
# Consent gate first (drop non-consenting users)
consented = parsed.filter(F.col("gdpr_consent") == F.lit(True))

# Basic DQ (examples): mandatory fields, price ≥ 0
dq_pass = consented.filter("event_id IS NOT NULL AND occurred_at IS NOT NULL AND price >= 0")

# Idempotency: drop duplicates by event_id with a watermark for late events
deduped = (dq_pass
    .withWatermark("occurred_at", "24 hours")   # bounded state for late data
    .dropDuplicates(["event_id"])               # exactly-once-ish semantics
)
```

---

## 🔹 Sink: **Silver (Iceberg on Parquet)** — Glue Catalog
 
 > Iceberg is a table format (NOT a file format). Under the hood, it stores data as Parquet files,
 > but with extra metadata/manifest layers to manage schema, partitions, and versions.
 
```
query = (cleaned.writeStream
    .format("iceberg")                           # Use Iceberg table format
                                                 # (still writes underlying Parquet files)

    .option("catalog", "glue_catalog")           # Glue Data Catalog acts as Iceberg catalog
                                                 # - Stores table metadata
                                                 # - Allows Athena/Redshift Spectrum queries
                                                 # - Enables schema evolution

    .option("database", "silver")                # Logical database in Glue
    .option("table", "booking")                  # Logical table name ("silver.booking")

    .option("checkpointLocation", "s3://my-bucket/checkpoints/bronze_to_silver/")
                                                 # Checkpointing: ensures exactly-once semantics
                                                 # Tracks Kafka offsets + processing progress

    .outputMode("append")                        # Append-only ingestion of booking events
                                                 # For aggregates → "update" or "complete"

    .trigger(processingTime="1 minute")          # Micro-batch every 1 min
                                                 # Trade-off: lower latency vs cost

    .start()                                     #Begin executing the streaming job (turns code from a plan into an active query)    
)
```

> **Why Iceberg here?** ACID appends, schema evolution, partition evolution, and direct query support from Athena/Redshift via Glue Catalog.  
> **Yes:** the data files landing in S3 are **Parquet** under the hood.

---

## 🔹 Silver → Gold (Iceberg) 

Silver→Gold is usually **batch** on AWS (e.g., every 10–15 minutes via MWAA/Airflow) for cost/perf balance.  
Below is a Glue **batch** example that reads the **Silver Iceberg** table and writes **Gold** aggregates.

```python
# Glue Batch Job: silver_to_gold_batch.py
from awsglue.context import GlueContext
from pyspark.context import SparkContext
from pyspark.sql import functions as F

sc = SparkContext()
glueContext = GlueContext(sc)
spark = glueContext.spark_session

SILVER_TABLE = "glue_catalog.analytics.silver_booking"
GOLD_TABLE   = "glue_catalog.analytics.gold_booking_minute"

# Read Silver Iceberg (snapshot)
silver = spark.read.format("iceberg").table(SILVER_TABLE)

# Example: minute-level KPIs by listing
gold = (silver
    .groupBy(F.window("occurred_at", "1 minute").alias("w"),
             F.col("listing_id"))
    .agg(F.countDistinct("event_id").alias("bookings"),
         F.sum("price").alias("gmv"))
    .select(F.col("listing_id"),
            F.col("w.start").alias("ts_minute"),
            "bookings", "gmv")
)

# Write to Iceberg Gold (append or MERGE into a partitioned table)
# Tip: Partition by date(ts_minute) for Athena/Redshift pruning
(spark.write
    .format("iceberg")
    .mode("append")
    .option("write.format.default", "parquet")   # physical file format
    .saveAsTable(GOLD_TABLE))
```

**Scheduling:** Use **Airflow (MWAA)** to run this batch job every 10–15 minutes (or hourly for cost).  
**Compaction:** Nightly compaction jobs (Spark/Iceberg actions) keep file counts healthy.

---

## 🔹 Notes & Best Practices

- **Schemas**: Version your contract in Git/Schema Registry. Do not rely on Glue Crawler inference at runtime.
- **Checkpointing**: Always set `checkpointLocation` for streaming sinks; never share paths across jobs.
- **Idempotency**: Enforce at Silver (e.g., `dropDuplicates(event_id)`), and use MERGE on business keys when needed.
- **Partitioning**: For Iceberg Gold, partition by `date(ts_minute)` (and possibly by entity) for scan pruning.
- **Governance**: Use **Glue Catalog + Lake Formation** for permissions; Great Expectations for DQ; keep DLQ for rejects.
- **Query engines**: Athena and Redshift Spectrum can both query Iceberg tables registered in Glue Catalog.

---

# ✅ Takeaways
- Glue Streaming code **looks like raw Spark** because it *is* Spark under the hood.
- Silver/Gold as **Iceberg** means Parquet files + managed metadata → ACID & evolution + Athena/Redshift compatibility.
- Prefer **batch** for Silver→Gold (cost‑efficient), keep **streaming** for truly low‑latency use cases.
