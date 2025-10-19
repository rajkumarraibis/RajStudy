
# Kafka: Architect’s Pocket Guide (Python-only)

## 1) Mental model (2025+)

* **KRaft (no ZooKeeper):** metadata via Raft quorum (controllers), brokers move data → simpler ops, faster failover.
* **Partitions = parallelism:** more partitions ⇒ more consumer concurrency (but more overhead).
* **RF=3 + rack awareness:** survives 1 node/AZ loss while staying writable.
* **Retention vs. compaction:** time/size for event logs; **compact** for “latest state” (upsert-like).

---

## 2) Golden flags (with one-liners)

### Producer (throughput + safety)

* `acks=all` → wait for quorum; strongest durability.
* `enable.idempotence=true` → server de-dupes retries; no dupes.
* `compression=zstd|lz4` → higher throughput, lower network/disk.
* `linger.ms=5–20` → micro-buffering to fill batches (lower latency sensitivity).
* `batch.size=32–128 KiB` → bigger batches = better throughput (watch memory).
* `max.in.flight.requests.per.connection=5` → keeps idempotence safe at high throughput.
* `retries` (high) + `retry.backoff.ms` → resilient to blips without storming the broker.

### Consumer (control lag & rebalance)

* `enable.auto.commit=false` → **you** commit **after** processing; prevents lost/dup work.
* `max.poll.records` → smaller = smoother latency; larger = better throughput.
* `max.poll.interval.ms` → raise if processing per batch takes longer to avoid rebalances.
* `isolation.level=read_committed` → only see committed (transactional) messages.

### Streams-style guarantees (if using Kafka Streams or EOS pipelines)

* `processing.guarantee=exactly_once_v2` → end-to-end EOS (or, for plain consumers, use transactions + `read_committed`).

---

## 3) Python producer — high-throughput, safe writes (idempotent)

```python
# pip install confluent-kafka
from confluent_kafka import Producer
p = Producer({
    "bootstrap.servers": "kafka:9092",
    "acks": "all",                     # quorum durability
    "enable.idempotence": True,        # de-duplicate retries
    "compression.type": "zstd",        # or "lz4"
    "linger.ms": 10,                   # batch for ~10ms
    "batch.size": 65536,               # ~64 KiB
    "max.in.flight.requests.per.connection": 5,
    "retries": 1000000
})

def dr(err, msg):
    if err:
        print("Delivery failed:", err)

for i in range(1000):
    p.produce("orders", key=f"user-{i%100}", value=f'{{"id":{i}}}', callback=dr)

p.flush()  # ensure delivery before exit
```

**Why this works:** batches + compression ⇒ throughput; `acks=all` + idempotence ⇒ no data loss/dupes under retries.

---

## 4) Python producer — **transactions (EOS)**

```python
from confluent_kafka import Producer

p = Producer({
    "bootstrap.servers": "kafka:9092",
    "enable.idempotence": True,
    "acks": "all",
    "transactional.id": "orders-tx-1"  # unique per producer instance
})

p.init_transactions()
try:
    p.begin_transaction()
    for i in range(10):
        p.produce("orders", key="cust-42", value=str(i).encode("utf-8"))
    # include offset commits to a txn (read-process-write patterns) by using a consumer with txn API
    p.commit_transaction()    # atomic publish or nothing
except Exception:
    p.abort_transaction()
finally:
    p.flush()
```

**When to use:** you **must** avoid duplicates across multi-record writes or read-process-write pipelines.

---

## 5) Python consumer — process, then commit

```python
from confluent_kafka import Consumer, KafkaException

c = Consumer({
    "bootstrap.servers": "kafka:9092",
    "group.id": "billing",
    "enable.auto.commit": False,       # we commit after successful processing
    "auto.offset.reset": "earliest",
    "isolation.level": "read_committed"  # see only committed txns
})

c.subscribe(["orders"])

try:
    while True:
        msg = c.poll(0.5)
        if not msg:
            continue
        if msg.error():
            raise KafkaException(msg.error())
        # 1) do the work (idempotent sinks help: upsert by key, use DB transactions)
        # 2) commit only after success
        c.commit(msg)  # per-message; or commit() periodically for batches
finally:
    c.close()
```

**Why:** avoids acknowledging work you didn’t finish; `read_committed` hides aborted txn writes.

---

## 6) Topic design (quick rules + “why”)

* **One event type per topic** → clean contracts, simpler evolution.
* **Pick a key that spreads** (e.g., userId) → avoids partition hotspots.
* **RF=3, min.insync.replicas=2** → tolerate a broker down and still write.
* **Compaction for latest-state streams** (profiles, inventory) → small, always-current topics.

---

## 7) Ops & SLO signals (what to alert on)

* `OfflinePartitionsCount > 0` → data unavailable; investigate broker/controller.
* `UnderReplicatedPartitions > 0` → durability risk or overloaded broker.
* **Consumer lag** rising persistently → add consumers/partitions or speed processing.
* **Request latencies** (produce/fetch) up → check network/disk, batch sizes, ISR health.

---

## 8) Security (minimum viable)

* **TLS everywhere** (brokers, clients, Connect).
* **SASL** (SCRAM/PLAIN/Kerberos/OAuth) for auth.
* **ACLs**: producers→`WRITE` on topic; consumers→`READ` on topic + `READ` on group.

---

## 9) Defaults to memorize

* **Producer:** `acks=all`, `enable.idempotence=true`, `compression=zstd|lz4`, `linger.ms≈10`, `batch.size≈64KiB`.
* **Consumer:** manual commits after work; tune `max.poll.records` & `max.poll.interval.ms`; use `read_committed` with EOS.
* **Cluster:** RF=3, rack awareness on; compaction only for latest-state topics.

---

Want me to tailor these **defaults and code** for your stack (e.g., **AWS MSK + Databricks** networking/IAM and a **DLQ pattern**)?
