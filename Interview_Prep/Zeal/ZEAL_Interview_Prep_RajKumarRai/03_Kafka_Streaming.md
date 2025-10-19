# Kafka & Streaming Pipelines

kafka tech details : https://github.com/rajkumarraibis/RajStudy/blob/main/Data_Topics_Misc/Kafka.md

Although Freeletics uses Kinesis for streaming, I’ve designed ingestion and enrichment flows conceptually identical to Kafka-based systems — event-driven, schema-managed, and idempotent.

## Experience Overview

- **Event Schema Management:** Defined clear JSON schemas for user transactions and webhook events to ensure consistent downstream processing.
- **Parallel Enrichment:** Used Spark RDD-based parallel fetches (similar to Kafka consumer groups) for DynamoDB lookups.
- **Idempotency:** All enrichment logic writes deterministic outputs (keyed by `event_id`) to avoid duplicates.
- **Replay Mechanisms:** Reprocessing capabilities built by date-based partition reruns.
- **Monitoring:** End-to-end S3 and log-based metrics for latency, record counts, and error tracking.

## Alignment with ZEAL

I can directly apply this experience to Kafka topics — partitioning strategies, offset management, and schema evolution — essential for ZEAL’s real-time transaction processing and analytics pipelines.
