
#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Job A: Bronze -> Silver (Real-time) on EMR Serverless with Spark Structured Streaming

Purpose
-------
Continuously ingest new JSON/JSON.GZ files that Kinesis Firehose lands in S3 "Bronze",
apply GDPR consent checks and basic DQ, deduplicate by event_id (idempotency),
and write clean rows into an Iceberg "Silver" table registered in Glue.

Key points
----------
- S3 FILE STREAM source: Spark lists S3, ingests only new files each trigger.
- Checkpointing: records processed files, enables exactly-once-ish on restart.
- Iceberg sink: transactional writes, schema evolution, time travel.
"""
import os
from pyspark.sql import SparkSession, functions as F, types as T

BRONZE_BASE   = os.getenv("BRONZE_BASE",   "s3://<YOUR_BUCKET>/bronze/events/booking_confirmed")
BRONZE_PATH   = os.getenv("BRONZE_PATH",   f"{BRONZE_BASE}/dt=*/hour=*/")  # partitioned bronze
DLQ_PATH      = os.getenv("DLQ_PATH",      "s3://<YOUR_BUCKET>/dlq/booking_confirmed/")
CHK_BASE      = os.getenv("CHK_BASE",      "s3://<YOUR_BUCKET>/_chk")
CHECKPOINT    = f"{CHK_BASE}/bronze_to_silver_rt"
SILVER_TABLE  = os.getenv("SILVER_TABLE",  "glue_catalog.analytics.silver_booking_confirmed")
FILES_PER_TRG = int(os.getenv("MAX_FILES_PER_TRIGGER", "500"))
TRIGGER_EVERY = os.getenv("TRIGGER_EVERY", "1 minute")

spark = (SparkSession.builder
         .appName("bronze_to_silver_rt")
         .config("spark.sql.shuffle.partitions", os.getenv("SPARK_SHUFFLE_PARTS", "200"))
         .getOrCreate())

schema = T.StructType([
    T.StructField("event", T.StringType()),
    T.StructField("event_id", T.StringType()),
    T.StructField("occurred_at", T.TimestampType()),
    T.StructField("received_at", T.TimestampType()),
    T.StructField("user_id", T.StringType()),
    T.StructField("session_id", T.StringType()),
    T.StructField("consent_state", T.StringType()),
    T.StructField("listing_id", T.StringType()),
    T.StructField("booking", T.StructType([
        T.StructField("reference", T.StringType()),
        T.StructField("check_in", T.DateType()),
        T.StructField("check_out", T.DateType()),
        T.StructField("guests", T.IntegerType()),
        T.StructField("currency", T.StringType()),
        T.StructField("amount_total", T.DoubleType())
    ])),
])

# 🔹 S3 FILE STREAM SOURCE
raw = (spark.readStream
       .format("json")                         # supports .json and .json.gz
       .schema(schema)                         # streaming requires explicit schema
       .option("pathGlobFilter", "*.json*")    # pick only JSON-ish files
       .option("maxFilesPerTrigger", FILES_PER_TRG)  # throughput control
       .load(BRONZE_PATH))                     # e.g., s3://.../dt=*/hour=*/

clean = (raw
    .filter(F.col("event") == "booking_confirmed")
    .filter(F.col("consent_state") == "analytics_allowed")
    .withColumn("event_date", F.to_date("occurred_at"))
    .withColumn("booking_reference", F.col("booking.reference"))
    .withColumn("amount_total", F.col("booking.amount_total"))
    .withColumn("currency", F.col("booking.currency"))
    .drop("booking"))

dedup = (clean
    .withWatermark("occurred_at", "24 hours")
    .dropDuplicates(["event_id"]))

valid   = dedup.filter("event_id IS NOT NULL AND amount_total >= 0")
invalid = dedup.exceptAll(valid)

(invalid.writeStream
   .format("json")
   .option("checkpointLocation", f"{CHECKPOINT}/dlq")
   .option("path", DLQ_PATH)
   .outputMode("append")
   .trigger(processingTime=TRIGGER_EVERY)
   .start())

(valid.writeStream
   .format("iceberg")
   .option("checkpointLocation", f"{CHECKPOINT}/silver")
   .outputMode("append")
   .trigger(processingTime=TRIGGER_EVERY)
   .toTable(SILVER_TABLE))

spark.streams.awaitAnyTermination()
