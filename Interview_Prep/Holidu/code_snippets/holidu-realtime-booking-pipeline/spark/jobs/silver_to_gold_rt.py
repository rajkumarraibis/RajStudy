"""
Silver → Gold Streaming Job
- Aggregates Silver data into Gold table
- Windowed aggregates: bookings per property, GMV per minute
"""

from pyspark.sql import SparkSession
from pyspark.sql.functions import col, window, sum as _sum, count

spark = SparkSession.builder     .appName("silver_to_gold_rt")     .getOrCreate()

# Source: Silver Iceberg
df = spark.readStream.format("iceberg").load("s3://silver-bucket/holidu/events/")

agg = df.groupBy(
    window(col("timestamp"), "1 minute"),
    col("property_id")
).agg(
    count("*").alias("bookings"),
    _sum("price").alias("gmv")
)

# Write to Gold (Iceberg)
agg.writeStream     .format("iceberg")     .option("path", "s3://gold-bucket/holidu/aggregates/")     .option("checkpointLocation", "s3://chk-bucket/silver_to_gold/")     .start()
