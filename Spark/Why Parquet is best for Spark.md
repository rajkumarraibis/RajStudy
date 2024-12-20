
## What is Parquet?

Apache Parquet is an open-source, column-oriented data file format designed for efficient data storage and retrieval. It provides efficient data compression and encoding schemes with enhanced performance to handle complex data in bulk. Apache Parquet is designed to be a common interchange format for both batch and interactive workloads. It is similar to other columnar-storage file formats available in Hadoop, such as RCFile and ORC.

### Characteristics of Parquet
- Free and open-source file format.
- Language-agnostic.
- Column-based format: Files are organized by column, rather than by row, which saves storage space and speeds up analytics queries.
- Used for analytics (OLAP) use cases, typically in conjunction with traditional OLTP databases.
- Highly efficient data compression and decompression.
- Supports complex data types and advanced nested data structures.

### Benefits of Parquet
- Good for storing big data of any kind (structured data tables, images, videos, documents).
- Saves on cloud storage space by using highly efficient column-wise compression and flexible encoding schemes for columns with different data types.
- Increased data throughput and performance using techniques like data skipping, whereby queries that fetch specific column values need not read the entire row of data.
- Apache Parquet is implemented using the record-shredding and assembly algorithm, which accommodates complex data structures. 
- Optimized to work with complex data in bulk.
- Queries needing to read specific columns from a large table benefit greatly as only the needed columns are read, minimizing IO.

---

## What are the Benefits of Using Parquet File-Format in Apache Spark?

Parquet is a columnar format supported by many data processing systems.

### The benefits of having a columnar storage are:
1. Columnar storage limits IO operations.
2. Columnar storage can fetch specific columns that you need to access.
3. Columnar storage consumes less space.
4. Columnar storage gives better-summarized data and follows type-specific encoding.
5. Organizing by column allows for better compression, as data is more homogeneous. The space savings are very noticeable at the scale of a Hadoop cluster.
6. I/O will be reduced as we can efficiently scan only a subset of the columns while reading the data. Better compression also reduces the bandwidth required to read the input.
7. As we store data of the same type in each column, we can use encoding better suited to modern processors’ pipeline by making instruction branching more predictable.

Parquet is an open-source file format for Hadoop. Parquet stores nested data structures in a flat columnar format. Compared to a traditional row-oriented approach, Parquet is more efficient in terms of storage and performance.

If your dataset has many columns, and your use case typically involves working with a subset of those columns rather than entire records, Parquet is optimized for that kind of work.

Parquet has higher execution speed compared to other standard file formats like Avro and JSON. It also consumes less disk space compared to Avro and JSON.

---

## Advantages of Storing Data in a Columnar Format
Columnar storage like Apache Parquet is designed to bring efficiency compared to row-based files like CSV. When querying, columnar storage skips over non-relevant data very quickly. As a result, aggregation queries are less time-consuming compared to row-oriented databases, translating into hardware savings and minimized latency for accessing data.

Apache Parquet supports advanced nested data structures and is optimized for queries processing large volumes of data. It supports flexible compression options and efficient encoding schemes, leveraging the similarity of data types in each column for straightforward compression.

Apache Parquet works best with interactive and serverless technologies like AWS Athena, Amazon Redshift Spectrum, Google BigQuery, and Google Dataproc.

---

## Difference Between Parquet and CSV
CSV is a simple and common format used by many tools such as Excel and Google Sheets. However, it has several disadvantages:

- Amazon Athena and Spectrum charge based on the amount of data scanned per query.
- Google and Amazon charge according to the amount of data stored on GS/S3.
- Google Dataproc charges are time-based.

Parquet reduces storage requirements by at least one-third on large datasets and significantly improves scan and deserialization time, reducing overall costs.

| Dataset                        | Size on Amazon S3 | Query Run Time | Data Scanned | Cost       |
|--------------------------------|-------------------|----------------|--------------|------------|
| **Data stored as CSV files**   | 1 TB              | 236 seconds    | 1.15 TB      | $5.75      |
| **Data stored in Parquet**     | 130 GB            | 6.78 seconds   | 2.51 GB      | $0.01      |
| **Savings**                    | 87% less storage  | 34x faster     | 99% less     | 99.7% cost |

---

## References
- [List the Advantages of Parquet File in Apache Spark](https://data-flair.training/forums/topic/list-the-advantage-of-parquet-file-in-apache-spark/)
- [What is Parquet - Databricks Glossary](https://databricks.com/glossary/what-is-parquet)

---