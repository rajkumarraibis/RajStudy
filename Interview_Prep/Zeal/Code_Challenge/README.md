# Zeal Code Challenge — E2E Streaming (Python Producer  →  Redpanda(Kafka) → Python Consumer → Postgres (pgAdmin))

A minimal, production-ish pipeline:

```
[ Python Producer ]  →  [ Redpanda (Kafka API) ]  →  [ Python Consumer ]  →  [ Postgres ]
                                                                ↓
                                                       [ hourly_aggregate VIEW ]
```

---

## 1) What you’ll run (components)

* **Redpanda** — Kafka-compatible broker (single binary, easy in Docker)
* **Redpanda cosole** — Monitor kafka redpanda visually
* **Producer (Python)** — simulates clickstream events into topic `events.raw`
* **Consumer (Python)** — reads `events.raw`, writes rows into Postgres table `events_raw`, creates view `hourly_aggregate`
* **Postgres** — stores raw JSON and powers the aggregate view
* **pgAdmin** — browse tables, run SQL.

---

## 2) Prereqs

* Docker Desktop (fresh install is fine)
* `docker compose` available on PATH

---

## 3) One-liner to build and start everything

```bash
docker compose build && docker compose up -d
```

To rebuild from scratch later:

```bash
docker compose down -v && docker compose build --no-cache && docker compose up -d
```

Check that all containers are healthy:

```bash
docker compose ps
```

---

## 4) Service endpoints & logins

* **pgAdmin**: [http://localhost:5050](http://localhost:5050)
  Login with the credentials defined in your `docker-compose.yml` (`PGADMIN_DEFAULT_EMAIL`, `PGADMIN_DEFAULT_PASSWORD`).
  Add a server:

  * Name: `local-events`
  * Host: `postgres`
  * Port: `5432`
  * DB: `events`
  * User: `zeal`
  * Password: `zeal`

* **Redpanda (CLI via rpk)**: run inside the broker container

  ```bash
  docker compose exec redpanda rpk cluster info
  docker compose exec redpanda rpk topic list --brokers redpanda:9092
  docker compose exec redpanda rpk topic describe events.raw --brokers redpanda:9092
  ```

* **(Optional) Redpanda Console**: if you enabled it in compose, open [http://localhost:8080](http://localhost:8080)

---

## 5) Verifying the end-to-end flow

Produce a smoke event with `rpk`:

```bash
docker compose exec redpanda sh -lc 'printf "{\"event\":\"smoke\",\"event_type\":\"page_view\",\"ts\":\"$(date -Iseconds)\"}\n" | rpk topic produce events.raw --brokers redpanda:9092'
```

Follow consumer logs:

```bash
docker compose logs -f consumer
```

You should see lines like:

```
[ok] inserted + committed events.raw[0]@<offset> key=None
```

Check Postgres:

```bash
docker compose exec postgres psql -U zeal -d events -c "SELECT id, msg_key, left(payload::text,80)||'...' AS payload, received_at FROM events_raw ORDER BY id DESC LIMIT 10;"
```

Query the view:

```bash
docker compose exec postgres psql -U zeal -d events -c "SELECT * FROM hourly_aggregate ORDER BY event_hour DESC, event_type LIMIT 20;"
```

---

## 6) File map & code walkthrough

### `docker-compose.yml`

Defines all services (redpanda, postgres, pgadmin, producer, consumer).
Key bits:

* **Redpanda** advertises internal Docker listener as `redpanda:9092` so other containers can fetch correctly.
* **Env** shares common settings (`KAFKA_BOOTSTRAP=redpanda:9092`, etc.)

### `producer.py`

Purpose: simulate events into `events.raw`.
Main steps:

* Build `confluent_kafka.Producer` with `bootstrap.servers=redpanda:9092`.
* Generate JSON payloads with fields like `id`, `user_id`, `event_type`, `ts`, `iso`.
* `produce(topic, key=None, value=json)`, flush on shutdown.
* Runs as a simple loop to keep data flowing.

### `consumer.py`

Purpose: consume from `events.raw` and insert into Postgres.
Highlights:

* **Config**: `bootstrap.servers=redpanda:9092`, `group.id=zeal-consumer-fresh`, `auto.offset.reset=earliest`, `enable.auto.commit=False`.
* **Subscription**: subscribes to `events.raw`. If assignment doesn’t happen quickly, it can **fallback to manual assign** from earliest so it never sits idle.
* **DB bootstrap**:

  * Creates table if missing:

    ```sql
    CREATE TABLE IF NOT EXISTS events_raw (
      id BIGSERIAL PRIMARY KEY,
      msg_key TEXT,
      payload JSONB NOT NULL,
      received_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
    );
    ```
  * Creates/updates the view:

    ```sql
    CREATE OR REPLACE VIEW hourly_aggregate AS
    SELECT
      date_trunc('hour', received_at) AS event_hour,
      COALESCE(payload->>'event_type', 'unknown') AS event_type,
      COUNT(*) AS event_count
    FROM events_raw
    GROUP BY 1, 2
    ORDER BY event_hour DESC;
    ```
* **Processing loop**:

  * `poll()` → parse JSON → `INSERT INTO events_raw(msg_key, payload) VALUES (%s, %s)`
  * **Commit offsets only after a successful insert** (at-least-once semantics).
  * Handles `_PARTITION_EOF` quietly (means “no new data yet”).

Functions you’ll see (names may vary slightly):

* `pg_connect()` — returns an autocommit connection and ensures table exists.
* `ensure_hourly_aggregate_view(conn)` — creates/refreshes the view once at startup.
* `make_consumer()` — returns a configured Kafka consumer.
* `subscribe_group()` — subscribes with `on_assign`/`on_revoke` handlers; seeks to earliest on assign.
* `manual_assign_beginning()` — list topic partitions and assign from earliest (fallback).
* `main()` — wires it all together, runs the poll → insert → commit loop.

### `requirements.txt`

Pinned deps for reproducibility, e.g.:

```
confluent-kafka==2.3.0
psycopg2-binary==2.9.9
```

(Producer and consumer both use the **same** version — this fixed earlier transport issues.)

### `create_table.sql`

DDL for `events_raw` (consumer also creates it automatically; the SQL file is a helpful reference).

### `README.md` (this document)

End-to-end instructions, architecture, and design notes.

---

## 7) Operational commands (handy)

Build + up:

```bash
docker compose build && docker compose up -d
```

Tail logs:

```bash
docker compose logs -f consumer
```

Kafka topic introspection:

```bash
docker compose exec redpanda rpk topic list --brokers redpanda:9092
docker compose exec redpanda rpk topic describe events.raw --brokers redpanda:9092
docker compose exec redpanda rpk group list --brokers redpanda:9092
```

Produce test messages:

```bash
docker compose exec redpanda sh -lc 'printf "{\"event\":\"smoke\",\"event_type\":\"page_view\",\"ts\":\"$(date -Iseconds)\"}\n" | rpk topic produce events.raw --brokers redpanda:9092'
```

Drop and recreate consumer with a fresh group:

```bash
KAFKA_GROUP_ID=zeal-consumer-$RANDOM docker compose up -d --force-recreate consumer
```

---

## 8) Assumptions

* Single partition topic (`events.raw`) is sufficient for this challenge.
* JSON payloads contain an `event_type` field; if missing we default to `'unknown'`.
* Timestamps are recorded from **ingest time** (`received_at`) to keep the view simple and robust.
* At-least-once delivery is acceptable for inserts (commits only after DB write).

---

## 9) Solution approach (short)

* Keep the **data plane** simple: Python → Redpanda → Python → Postgres.
* Make networking deterministic: advertise `redpanda:9092` for in-Docker clients.
* Ensure the consumer is resilient: earliest seek, fallback to manual assignment, commit-after-insert.
* Provide a queryable **analytic view** immediately (`hourly_aggregate`) without extra infra.

---

## 10) Design choices

**Why `confluent-kafka` (Python client)?**

* It’s the de-facto high-performance Kafka client for Python (CPython bindings over `librdkafka`), stable and widely deployed.
* Backpressure, batching, retries, and rebalance handling are well-tested.

**Why Redpanda (vs Kafka)?**

* Drop-in Kafka API with a single container, no ZooKeeper.
* Faster startup and simpler ops for a coding challenge.
* Great local DX: `rpk` tooling and easy Docker networking.

**Why Postgres for storage?**

* Universal, rock-solid, and lets us mix **raw JSONB** with **SQL views** for reporting.
* No need to introduce another store just for aggregates.

**Why not Grafana (for now)?**

* It was causing network issues with other services. For now pgadmin , redpanda-console , docker app can be used for monitoring and tracing.
* If needed later, I’d expose consumer metrics (e.g., via Prometheus client), scrape them, and build a small dashboard for lag/throughput.

---


