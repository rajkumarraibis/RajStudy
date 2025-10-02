"""
Bronze → Silver Streaming Job
- Reads raw events from Bronze (S3/Kafka)
- Deduplicates by event_id
- Filters out users without GDPR consent
- Simple data quality checks
- Writes cleaned stream to Silver Iceberg table
"""

from pyspark.sql import SparkSession
from pyspark.sql.functions import col

spark = SparkSession.builder     .appName("bronze_to_silver_rt")     .getOrCreate()

# Source: Bronze (S3 JSON or Kafka)
df = spark.readStream.format("json").schema("event_id STRING, event_type STRING, timestamp STRING, user_id STRING, property_id STRING, nights INT, price DOUBLE, currency STRING, gdpr_consent BOOLEAN").load("s3://bronze-bucket/holidu/events/")

# Deduplicate
deduped = df.dropDuplicates(["event_id"])

# GDPR consent filter
consented = deduped.filter(col("gdpr_consent") == True)

# Simple DQ check: price > 0
cleaned = consented.filter(col("price") > 0)

# Write to Silver (Iceberg)
cleaned.writeStream     .format("iceberg")     .option("path", "s3://silver-bucket/holidu/events/")     .option("checkpointLocation", "s3://chk-bucket/bronze_to_silver/")     .start()
