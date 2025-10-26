#!/usr/bin/env python3
import json
import os
import signal
import sys
import time
from typing import Optional

import psycopg2
from psycopg2.extras import Json
from urllib.parse import urlparse
from confluent_kafka import Consumer, KafkaError, KafkaException

# -------- Read env (support both your compose & prior code) --------
KAFKA_BOOTSTRAP = (
    os.getenv("KAFKA_BOOTSTRAP_SERVERS")
    or os.getenv("KAFKA_BOOTSTRAP")
    or "redpanda:9092"
)
KAFKA_GROUP_ID = os.getenv("KAFKA_GROUP_ID", "zeal-consumer-fresh")
KAFKA_TOPIC = os.getenv("KAFKA_TOPIC") or os.getenv("INPUT_TOPIC") or "events.raw"

POSTGRES_DSN = os.getenv("POSTGRES_DSN")  # e.g. postgresql://zeal:zeal@postgres:5432/events

PG_HOST = os.getenv("POSTGRES_HOST", "postgres")
PG_DB = os.getenv("POSTGRES_DB", "postgres")
PG_USER = os.getenv("POSTGRES_USER", "zeal")
PG_PASS = os.getenv("POSTGRES_PASSWORD", "zeal")
PG_PORT = int(os.getenv("POSTGRES_PORT", "5432"))

POLL_TIMEOUT = float(os.getenv("POLL_TIMEOUT_SEC", "1.0"))  # seconds
COMMIT_EVERY = int(os.getenv("COMMIT_EVERY", "1"))          # commit after N successful inserts

# -------- Graceful shutdown flag --------
_running = True
def _stop(*_):
    global _running
    _running = False
signal.signal(signal.SIGINT, _stop)
signal.signal(signal.SIGTERM, _stop)

# -------- Postgres helpers --------
DDL = """
CREATE TABLE IF NOT EXISTS events_raw (
  id          BIGSERIAL PRIMARY KEY,
  msg_key     TEXT,
  payload     JSONB NOT NULL,
  received_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);
"""
INSERT_SQL = "INSERT INTO events_raw (msg_key, payload) VALUES (%s, %s);"

def _parse_dsn(dsn: str):
    u = urlparse(dsn)
    return {
        "host": u.hostname or "postgres",
        "port": u.port or 5432,
        "dbname": (u.path or "/postgres").lstrip("/"),
        "user": u.username or "zeal",
        "password": u.password or "zeal",
    }

def pg_connect():
    if POSTGRES_DSN:
        cfg = _parse_dsn(POSTGRES_DSN)
    else:
        cfg = dict(host=PG_HOST, port=PG_PORT, dbname=PG_DB, user=PG_USER, password=PG_PASS)

    conn = psycopg2.connect(**cfg)
    conn.autocommit = True
    with conn.cursor() as cur:
        cur.execute(DDL)
    # helpful startup log
    print(f"[db] connected → {cfg['host']}:{cfg['port']}/{cfg['dbname']} as {cfg['user']}", flush=True)
    return conn

# -------- Kafka consumer setup --------
def make_consumer() -> Consumer:
    conf = {
        "bootstrap.servers": KAFKA_BOOTSTRAP,
        "group.id": KAFKA_GROUP_ID,
        "enable.auto.commit": False,      # commit only after DB success
        "auto.offset.reset": "earliest",  # safe for fresh groups
        "session.timeout.ms": 45000,
        "max.poll.interval.ms": 300000,
        # simpler strategy to avoid incremental assign API requirements
        "partition.assignment.strategy": "range",
        "allow.auto.create.topics": True,
    }

    c = Consumer(conf)

    def on_assign(consumer, partitions):
        print(f"[rebalance] Assigned: {partitions}", flush=True)
        # Force the consumer to start reading from the earliest offset
        tps = [TopicPartition(p.topic, p.partition, OFFSET_BEGINNING) for p in partitions]
        consumer.assign(tps)
        print("[rebalance] Forced seek to earliest offsets", flush=True)


    def on_revoke(consumer, partitions):
        print(f"[rebalance] Revoked: {partitions}", flush=True)
        try:
            consumer.commit(asynchronous=False)
        except KafkaException as e:
            print(f"[rebalance] Commit on revoke failed: {e}", flush=True)

    c.subscribe([KAFKA_TOPIC], on_assign=on_assign, on_revoke=on_revoke)
    return c

def main():
    print(f"[cfg] kafka bootstrap   = {KAFKA_BOOTSTRAP}", flush=True)
    print(f"[cfg] kafka group.id    = {KAFKA_GROUP_ID}", flush=True)
    print(f"[cfg] kafka topic       = {KAFKA_TOPIC}", flush=True)
    print(f"[cfg] postgres dsn set  = {'yes' if POSTGRES_DSN else 'no'}", flush=True)

    conn = pg_connect()
    consumer = make_consumer()

    commit_counter = 0
    last_log = time.time()

    try:
        with conn.cursor() as cur:
            while _running:
                msg = consumer.poll(POLL_TIMEOUT)
                if msg is None:
                    if time.time() - last_log > 15:
                        print("[loop] idle...", flush=True)
                        last_log = time.time()
                    continue

                if msg.error():
                    if msg.error().code() == KafkaError._PARTITION_EOF:
                        continue
                    raise KafkaException(msg.error())

                try:
                    key: Optional[str] = msg.key().decode("utf-8") if msg.key() else None
                    raw_value = msg.value()
                    try:
                        value_obj = json.loads(raw_value)
                    except Exception:
                        value_obj = {"raw": raw_value.decode("utf-8") if isinstance(raw_value, (bytes, bytearray)) else str(raw_value)}

                    cur.execute(INSERT_SQL, (key, Json(value_obj)))
                    consumer.commit(message=msg, asynchronous=False)
                    commit_counter += 1

                    if commit_counter % COMMIT_EVERY == 0:
                        print(f"[ok] inserted + committed {msg.topic()}[{msg.partition()}]@{msg.offset()} key={key}", flush=True)

                except (psycopg2.Error, Exception) as e:
                    print(f"[error] DB insert failed; leaving offset uncommitted. Reason: {e}", flush=True)
                    time.sleep(0.5)

    except KeyboardInterrupt:
        pass
    finally:
        try:
            print("[shutdown] final synchronous commit...", flush=True)
            consumer.commit(asynchronous=False)
        except Exception as e:
            print(f"[shutdown] final commit failed: {e}", flush=True)
        consumer.close()
        conn.close()
        print("[shutdown] consumer closed, DB connection closed.", flush=True)

if __name__ == "__main__":
    sys.exit(main())
