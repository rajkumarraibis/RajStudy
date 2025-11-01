
#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Job B: Silver -> Gold (Real-time aggregates) on EMR Serverless with Spark Structured Streaming

Consumes the Silver stream and writes minute-level aggregates to a Gold Iceberg table.
"""
import os
from pyspark.sql import SparkSession, functions as F

SILVER_TABLE  = os.getenv("SILVER_TABLE", "glue_catalog.analytics.silver_booking_confirmed")
GOLD_TABLE    = os.getenv("GOLD_TABLE",   "glue_catalog.analytics.gold_booking_minute")
CHK_BASE      = os.getenv("CHK_BASE",     "s3://<YOUR_BUCKET>/_chk")
CHECKPOINT    = f"{CHK_BASE}/silver_to_gold_rt"
TRIGGER_EVERY = os.getenv("TRIGGER_EVERY", "1 minute")

spark = (SparkSession.builder
         .appName("silver_to_gold_rt")
         .config("spark.sql.shuffle.partitions", os.getenv("SPARK_SHUFFLE_PARTS", "200"))
         .getOrCreate())

silver = (spark.readStream
          .format("iceberg")
          .table(SILVER_TABLE))

agg = (silver
    .withWatermark("occurred_at", "24 hours")
    .groupBy(F.window("occurred_at", "1 minute").alias("w"),
             F.col("listing_id"))
    .agg(F.countDistinct("event_id").alias("bookings"),
         F.sum("amount_total").alias("gmv"))
    .select(F.col("listing_id"),
            F.col("w.start").alias("ts_minute"),
            "bookings","gmv"))

(agg.writeStream
    .format("iceberg")
    .option("checkpointLocation", CHECKPOINT)
    .outputMode("append")
    .trigger(processingTime=TRIGGER_EVERY)
    .toTable(GOLD_TABLE))

spark.streams.awaitAnyTermination()
