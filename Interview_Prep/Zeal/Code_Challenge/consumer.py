import os, json, time
import psycopg2
from psycopg2.extras import Json
from confluent_kafka import Consumer, KafkaException, KafkaError

TOPIC = os.getenv("KAFKA_TOPIC", "events.raw")
GROUP = os.getenv("KAFKA_GROUP_ID", "zeal-consumer")
BOOT  = os.getenv("KAFKA_BOOTSTRAP_SERVERS", "redpanda:9092")

PGHOST = os.getenv("PGHOST", "postgres")
PGUSER = os.getenv("PGUSER", "zeal")
PGPASSWORD = os.getenv("PGPASSWORD", "zeal")
PGDATABASE = os.getenv("PGDATABASE", "events")
PGPORT = int(os.getenv("PGPORT", "5432"))

def pg_connect():
    for i in range(1, 31):
        try:
            conn = psycopg2.connect(host=PGHOST, user=PGUSER, password=PGPASSWORD, dbname=PGDATABASE, port=PGPORT, connect_timeout=5)
            conn.autocommit = False
            print(f"[pg] connected")
            return conn
        except Exception as e:
            print(f"[pg] connect failed ({i}): {e}")
            time.sleep(min(2*i, 5))
    raise SystemExit("pg connect failed")

def ensure_schema(conn):
    with conn.cursor() as cur:
        cur.execute("""
        CREATE TABLE IF NOT EXISTS events_raw (
            id BIGSERIAL PRIMARY KEY,
            key TEXT,
            payload JSONB NOT NULL,
            ts TIMESTAMPTZ DEFAULT NOW()
        );
        """)
    conn.commit()
    print("[pg] ensured table events_raw")

def main():
    print(f"[boot] BOOTSTRAP={BOOT} TOPIC={TOPIC} GROUP={GROUP}", flush=True)
    conf = {
        "bootstrap.servers": BOOT,
        "group.id": GROUP,
        "auto.offset.reset": "latest",
        "enable.auto.commit": False,
        "security.protocol": "PLAINTEXT",
        "broker.address.family": "v4",
        "socket.keepalive.enable": True,
        "connections.max.idle.ms": 0,
        "session.timeout.ms": 45000,
        "socket.timeout.ms": 60000,
        "reconnect.backoff.ms": 500,
        "reconnect.backoff.max.ms": 10000,
        "log.connection.close": False,
    }
    c = Consumer(conf)
    c.subscribe([TOPIC])
    print("[kafka] subscribed", flush=True)

    pg = pg_connect()
    ensure_schema(pg)
    cur = pg.cursor()

    try:
        while True:
            m = c.poll(2.0)
            if m is None:
                continue
            if m.error():
                if m.error().code() == KafkaError._PARTITION_EOF:
                    continue
                print("[kafka][error]", m.error(), flush=True)
                raise KafkaException(m.error())

            key = m.key().decode() if m.key() else None
            try:
                payload = json.loads(m.value().decode("utf-8"))
            except Exception as e:
                print(f"[consumer][warn] bad JSON at offset {m.offset()}: {e}", flush=True)
                payload = {"raw": m.value().decode("utf-8", "replace")}

            cur.execute("INSERT INTO events_raw (key, payload) VALUES (%s, %s)", (key, Json(payload)))
            pg.commit()
            c.commit(message=m)
            print(f"[consumer] stored key={key} offset={m.offset()}", flush=True)

    except KeyboardInterrupt:
        print("[consumer] shutting down…", flush=True)
    finally:
        try:
            cur.close(); pg.close()
        except Exception:
            pass
        c.close()

if __name__ == "__main__":
    main()
