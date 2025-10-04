# Glue Streaming Job Walkthrough (Bronze → Silver → Gold) — **Iceberg Edition**

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

## 🔹 Streaming Source: Kafka/MSK (super‑annotated)

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


# Kafka message schema: key (binary), value (binary), topic, partition, offset, timestamp...
from pyspark.sql.functions import col, from_json
parsed = (raw_stream
    .selectExpr("CAST(value AS STRING) AS raw")
    .select(from_json(col("raw"), schema).alias("e"))
    .select("e.*")  # flatten to columns
)
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

```python
# Iceberg config is typically provided via spark-submit confs, e.g.:
# --conf spark.sql.catalog.glue_catalog=org.apache.iceberg.spark.SparkCatalog
# --conf spark.sql.catalog.glue_catalog.warehouse=s3://<WAREHOUSE_BUCKET>/warehouse/
# --conf spark.sql.catalog.glue_catalog.catalog-impl=org.apache.iceberg.aws.glue.GlueCatalog
# --conf spark.sql.catalog.glue_catalog.io-impl=org.apache.iceberg.aws.s3.S3FileIO

SILVER_TABLE = "glue_catalog.analytics.silver_booking"     # <catalog>.<db>.<table>
SILVER_CHECKPOINT = "s3://my-bucket/checkpoints/bronze_to_silver/"

silver_query = (deduped.writeStream
    .format("iceberg")                           # Iceberg table sink (physical files = Parquet)
    .outputMode("append")                        # append rows as they arrive
    .option("checkpointLocation", SILVER_CHECKPOINT)
    # NOTE: With Iceberg, table location is managed by the catalog;
    # you reference the table by name rather than a raw S3 'path'.
    .toTable(SILVER_TABLE)                       # creates table if missing (with proper perms)
)
```

> **Why Iceberg here?** ACID appends, schema evolution, partition evolution, and direct query support from Athena/Redshift via Glue Catalog.  
> **Yes:** the data files landing in S3 are **Parquet** under the hood.

---

## 🔹 Silver → Gold (Iceberg) — Batch job (recommended)

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

## 🔹 Alternative: Silver → Gold as a second **Streaming** job

If you truly need near real-time Gold (< 2–5 min), you can read Silver as a stream and write Gold as a stream too:

```python
from awsglue.context import GlueContext
from pyspark.context import SparkContext
from pyspark.sql import functions as F

sc = SparkContext()
glueContext = GlueContext(sc)
spark = glueContext.spark_session

SILVER_TABLE = "glue_catalog.analytics.silver_booking"
GOLD_TABLE   = "glue_catalog.analytics.gold_booking_minute"
CHECKPOINT   = "s3://my-bucket/checkpoints/silver_to_gold_stream/"

silver_stream = (spark.readStream
                 .format("iceberg")
                 .table(SILVER_TABLE))

agg_stream = (silver_stream
    .withWatermark("occurred_at", "24 hours")
    .groupBy(F.window("occurred_at", "1 minute").alias("w"),
             F.col("listing_id"))
    .agg(F.countDistinct("event_id").alias("bookings"),
         F.sum("price").alias("gmv"))
    .select(F.col("listing_id"),
            F.col("w.start").alias("ts_minute"),
            "bookings","gmv"))

gold_query = (agg_stream.writeStream
    .format("iceberg")
    .option("checkpointLocation", CHECKPOINT)
    .outputMode("append")
    .toTable(GOLD_TABLE))
```

**Trade‑off:** lower latency, higher cost/ops. Batch is usually enough for BI (QuickSight SPICE ≈ 15 min).

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
