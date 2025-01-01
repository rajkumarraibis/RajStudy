
# Spark SQL Guide

## Introduction
Spark SQL is a module for structured data processing. It provides a programming abstraction called DataFrames and a domain-specific language (DSL) for structured data manipulation.

This guide includes examples of commonly used Spark SQL functions.

---

## Setting Up Spark SQL
```python
from pyspark.sql import SparkSession

# Initialize SparkSession
spark = SparkSession.builder \
    .appName("Spark SQL Guide") \
    .getOrCreate()

# Sample Data
data = [(1, "Alice", 29), (2, "Bob", 31), (3, "Cathy", 25)]
columns = ["ID", "Name", "Age"]
df = spark.createDataFrame(data, columns)

# Show DataFrame
df.show()
```

---

## DataFrame Operations
### 1. Select Columns
```python
df.select("Name", "Age").show()
```

### 2. Filter Rows
```python
df.filter(df["Age"] > 28).show()
```

### 3. Add a New Column
```python
df.withColumn("AgeAfter5Years", df["Age"] + 5).show()
```

### 4. Rename a Column
```python
df.withColumnRenamed("Age", "CurrentAge").show()
```

---

## Aggregation Functions
### 1. Count
```python
from pyspark.sql.functions import count

df.select(count("Name")).show()
```

### 2. Average
```python
from pyspark.sql.functions import avg

df.select(avg("Age")).show()
```

### 3. Group By and Aggregate
```python
grouped_df = df.groupBy("Age").count()
grouped_df.show()
```

---

## String Functions
### 1. Upper and Lower
```python
from pyspark.sql.functions import upper, lower

df.select(upper("Name"), lower("Name")).show()
```

### 2. Length
```python
from pyspark.sql.functions import length

df.select("Name", length("Name").alias("NameLength")).show()
```

### 3. Substring
```python
from pyspark.sql.functions import substring

df.select("Name", substring("Name", 1, 3).alias("Substr")).show()
```

---

## Date and Time Functions
### 1. Current Date
```python
from pyspark.sql.functions import current_date

df.select(current_date().alias("CurrentDate")).show()
```

### 2. Date Difference
```python
from pyspark.sql.functions import datediff, to_date

sample_data = [(1, "2023-12-25"), (2, "2024-01-01")]
date_df = spark.createDataFrame(sample_data, ["ID", "EventDate"])
date_df = date_df.withColumn("EventDate", to_date("EventDate"))

# Calculate difference in days
date_df.select("ID", datediff(current_date(), "EventDate").alias("DaysDifference")).show()
```

### 3. Add Months
```python
from pyspark.sql.functions import add_months

date_df.select("ID", add_months("EventDate", 2).alias("DateAfter2Months")).show()
```

---

## Joins
### Inner Join
```python
data2 = [(1, "HR"), (2, "Finance"), (4, "Marketing")]
department_df = spark.createDataFrame(data2, ["ID", "Department"])

joined_df = df.join(department_df, "ID", "inner")
joined_df.show()
```

### Left Join
```python
left_join_df = df.join(department_df, "ID", "left")
left_join_df.show()
```

---

## Window Functions
### Row Number
```python
from pyspark.sql.window import Window
from pyspark.sql.functions import row_number

window_spec = Window.partitionBy().orderBy("Age")
df.withColumn("RowNumber", row_number().over(window_spec)).show()
```

---

## Caching and Unpersisting
### Cache DataFrame
```python
df.cache()
df.show()
```

### Unpersist DataFrame
```python
df.unpersist()
```

---

## Conclusion
This guide provides examples of commonly used functions in Spark SQL. For more advanced usage, refer to the [official Spark documentation](https://spark.apache.org/docs/latest/sql-programming-guide.html).
