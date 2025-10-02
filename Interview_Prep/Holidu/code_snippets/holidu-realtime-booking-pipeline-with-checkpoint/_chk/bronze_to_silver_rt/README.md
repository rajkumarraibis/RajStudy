
# Spark Structured Streaming Checkpoint (Illustrative)

This is a **mocked** checkpoint tree to help explain how Spark tracks progress
for the S3 file stream source. Real Spark creates similar folders/files here.

Key ideas:
- `sources/0/*`  : source offsets — lists the files Spark has already processed.
- `commits/*`    : per‑batch commit metadata (batchId, timestamp).
- `offsets/*`    : global offsets per batch (used for recovery on restart).

⚠️ These files are **simplified**; contents are for demo only.
