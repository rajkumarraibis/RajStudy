#!/usr/bin/env python3
import json
import os
import signal
import sys
import time
from typing import Optional, List
from urllib.parse import urlparse

import psycopg2
from psycopg2.extras import Json
from confluent_kafka import (
    Consumer,
    KafkaError,
    KafkaException,
    TopicPartition,
    OFFSET_BEGINNING,
)

# ---------------- Env ----------------
KAFKA_BOOTSTRAP = (
    os.getenv("KAFKA_BOOTSTRAP_SERVERS")
    or os.getenv("KAFKA_BOOTSTRAP")
    or "redpanda:9092"
)
KAFKA_GROUP_ID = os.getenv("KAFKA_GROUP_ID", "zeal-consumer-fresh")
KAFKA_TOPIC = os.getenv("KAFKA_TOPIC") or os.getenv("INPUT_TOPIC") or "events.raw"

POSTGRES_DSN = os.getenv("POSTGRES_DSN")  # e.g. postgresql://zeal:zeal@postgres:5432/events
PG_HOST = os.getenv("POSTGRES_HOST", "postgres")
PG_DB = os.getenv("POSTGRES_DB", "events")  # not used if DSN present
PG_USER = os.getenv("POSTGRES_USER", "zeal")
PG_PASS = os.getenv("POSTGRES_PASSWORD", "zeal")
PG_PORT = int(os.getenv("POSTGRES_PORT", "5432"))

POLL_TIMEOUT = float(os.getenv("POLL_TIMEOUT_SEC", "1.0"))
COMMIT_EVERY = int(os.getenv("COMMIT_EVERY", "1"))

# if set to "1", we skip group mode and assign partitions manually from earliest
FORCE_MANUAL_ASSIGN = os.getenv("FORCE_MANUAL_ASSIGN", "0") == "1"
MANUAL_ASSIGN_WAIT_SECS = float(os.getenv("MANUAL_ASSIGN_WAIT_SECS", "5.0"))

# ---------------- Graceful shutdown ----------------
_running = True
def _stop(*_):
    global _running
    _running = False
signal.signal(signal.SIGINT, _stop)
signal.signal(signal.SIGTERM, _stop)

# ---------------- DB ----------------
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
        "dbname": (u.path or "/events").lstrip("/"),
        "user": u.username or "zeal",
        "password": u.password or "zeal",
    }

def pg_connect():
    cfg = _parse_dsn(POSTGRES_DSN) if POSTGRES_DSN else dict(
        host=PG_HOST, port=PG_PORT, dbname=PG_DB, user=PG_USER, password=PG_PASS
    )
    conn = psycopg2.connect(**cfg)
    conn.autocommit = True
    with conn.cursor() as cur:
        cur.execute(DDL)
    print(f"[db] connected → {cfg['host']}:{cfg['port']}/{cfg['dbname']} as {cfg['user']}", flush=True)
    return conn

# ---------------- Kafka ----------------
def make_consumer(debug: bool = True) -> Consumer:
    def _error_cb(err):
        print(f"[kafka-error] {err}", flush=True)

    conf = {
        "bootstrap.servers": KAFKA_BOOTSTRAP,
        "group.id": KAFKA_GROUP_ID,
        "enable.auto.commit": False,
        "auto.offset.reset": "earliest",
        "session.timeout.ms": 45000,
        "max.poll.interval.ms": 300000,
        "partition.assignment.strategy": "range",
        "allow.auto.create.topics": True,
        "enable.partition.eof": True,
        "error_cb": _error_cb,
        # "debug": "cgrp,topic,broker,fetch",  # uncomment if you want verbose logs
    }

    return Consumer(conf)



assigned_once = False  # tracks whether group-mode assignment happened

def subscribe_group(consumer: Consumer):
    def on_assign(c: Consumer, partitions: List[TopicPartition]):
        global assigned_once
        print(f"[rebalance] Assigned: {partitions}", flush=True)
        # Force from earliest to avoid idle-at-end
        tps = [TopicPartition(p.topic, p.partition, OFFSET_BEGINNING) for p in partitions]
        c.assign(tps)
        assigned_once = True
        print("[rebalance] Forced seek to earliest offsets", flush=True)

    def on_revoke(c: Consumer, partitions: List[TopicPartition]):
        print(f"[rebalance] Revoked: {partitions}", flush=True)
        try:
            c.commit(asynchronous=False)
        except KafkaException as e:
            print(f"[rebalance] Commit on revoke failed: {e}", flush=True)

    consumer.subscribe([KAFKA_TOPIC], on_assign=on_assign, on_revoke=on_revoke)
    print(f"[group] subscribed to {KAFKA_TOPIC} with group.id={KAFKA_GROUP_ID}", flush=True)

def manual_assign_beginning(consumer: Consumer):
    # list topic metadata, assign all partitions from earliest
    md = consumer.list_topics(KAFKA_TOPIC, timeout=10.0)
    if md.topics.get(KAFKA_TOPIC) is None or md.topics[KAFKA_TOPIC].error is not None:
        raise RuntimeError(f"Topic {KAFKA_TOPIC} not found or error in metadata")
    parts = sorted(md.topics[KAFKA_TOPIC].partitions.keys())
    tps = [TopicPartition(KAFKA_TOPIC, p, OFFSET_BEGINNING) for p in parts]
    consumer.assign(tps)
    print(f"[manual] assigned partitions (earliest): {tps}", flush=True)

# ---------------- Main ----------------
def main():
    print(f"[cfg] kafka bootstrap   = {KAFKA_BOOTSTRAP}", flush=True)
    print(f"[cfg] kafka group.id    = {KAFKA_GROUP_ID}", flush=True)
    print(f"[cfg] kafka topic       = {KAFKA_TOPIC}", flush=True)
    print(f"[cfg] postgres dsn set  = {'yes' if POSTGRES_DSN else 'no'}", flush=True)
    print(f"[cfg] force manual assign = {FORCE_MANUAL_ASSIGN}", flush=True)

    conn = pg_connect()
    consumer = make_consumer()

    # try group subscribe unless forced manual
    if not FORCE_MANUAL_ASSIGN:
        subscribe_group(consumer)
        wait_until = time.time() + MANUAL_ASSIGN_WAIT_SECS
        while time.time() < wait_until and not assigned_once and _running:
            # poll to allow callbacks to fire
            m = consumer.poll(0.2)
            if m and m.error() and m.error().code() not in (KafkaError._PARTITION_EOF,):
                print(f"[pre-assign] poll error: {m.error()}", flush=True)
        if not assigned_once:
            print(f"[group] no assignment within {MANUAL_ASSIGN_WAIT_SECS}s → falling back to manual assign", flush=True)
            manual_assign_beginning(consumer)
    else:
        manual_assign_beginning(consumer)

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
                        # reached end of a partition; normal
                        continue
                    print(f"[poll-error] {msg.error()}", flush=True)
                    continue  # keep running; don't die on transient errors

                try:
                    key: Optional[str] = msg.key().decode("utf-8") if msg.key() else None
                    raw_value = msg.value()

                    try:
                        value_obj = json.loads(raw_value)
                    except Exception:
                        value_obj = {"raw": raw_value.decode("utf-8") if isinstance(raw_value, (bytes, bytearray)) else str(raw_value)}

                    cur.execute(INSERT_SQL, (key, Json(value_obj)))

                    # only commit offsets in group mode (manual mode has no group semantics)
                    if assigned_once and KAFKA_GROUP_ID:
                        consumer.commit(message=msg, asynchronous=False)
                        commit_counter += 1
                        if commit_counter % COMMIT_EVERY == 0:
                            print(f"[ok] inserted + committed {msg.topic()}[{msg.partition()}]@{msg.offset()} key={key}", flush=True)
                    else:
                        # manual mode
                        print(f"[ok] inserted (manual) {msg.topic()}[{msg.partition()}]@{msg.offset()} key={key}", flush=True)

                except (psycopg2.Error, Exception) as e:
                    print(f"[error] DB insert failed; leaving offset uncommitted. Reason: {e}", flush=True)
                    time.sleep(0.5)

    except KeyboardInterrupt:
        pass
    finally:
        try:
            print("[shutdown] final synchronous commit (group mode only)...", flush=True)
            if assigned_once and KAFKA_GROUP_ID:
                consumer.commit(asynchronous=False)
        except Exception as e:
            print(f"[shutdown] final commit failed: {e}", flush=True)
        consumer.close()
        conn.close()
        print("[shutdown] consumer closed, DB connection closed.", flush=True)

if __name__ == "__main__":
    sys.exit(main())
