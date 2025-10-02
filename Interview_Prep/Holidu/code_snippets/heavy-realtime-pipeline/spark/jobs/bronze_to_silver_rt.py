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

# Source: Bronze (S3 JSON)
# 🔹 S3 FILE STREAM SOURCE
# This tells Spark Structured Streaming to "watch" the Bronze S3 folder where
# Amazon Kinesis Firehose continuously drops new JSON (or JSON.GZ) files.
# Spark treats every new file that lands as part of a micro-batch stream.
raw = (spark.readStream
       .format("json")                  
       # Firehose typically writes files in JSON or compressed JSON.GZ.
       # Spark can automatically read gzip-compressed files, so both work.
       
       .schema(schema)                  
       # IMPORTANT: In Structured Streaming, schema inference is not allowed.
       # We must define the JSON schema upfront (see schema above).
       # This ensures consistent parsing and avoids runtime surprises.
       
       .option("pathGlobFilter", "*.json*")  
       # Optional safety filter: ensures Spark only picks up files ending
       # with .json or .json.gz. Prevents it from accidentally reading
       # checkpoint files, metadata, or any other junk files in the folder.
       
       .option("maxFilesPerTrigger", 500)    
       # Key performance knob: controls how many *new files* Spark reads
       # in each micro-batch trigger. 
       # - If Firehose is writing 1000 small files per minute, Spark will pick 500,
       #   then pick the next 500 in the following micro-batch.
       # - Prevents overloading executors if there’s a sudden file dump.
       # Tuning depends on event volume and cluster size.
       
       .load(BRONZE_PATH))
       # Finally, tell Spark which S3 folder to watch.
       # Example: s3://lake/bronze/events/booking_confirmed/dt=*/hour=*/
       # Partitioning the path by dt/hour makes listing efficient.


# Deduplicate
deduped = df.dropDuplicates(["event_id"])

# GDPR consent filter
consented = deduped.filter(col("gdpr_consent") == True)

# Simple DQ check: price > 0
cleaned = consented.filter(col("price") > 0)

# Write to Silver (Iceberg)
cleaned.writeStream     .format("iceberg")     .option("path", "s3://silver-bucket/holidu/events/")     .option("checkpointLocation", "s3://chk-bucket/bronze_to_silver/")     .start()
