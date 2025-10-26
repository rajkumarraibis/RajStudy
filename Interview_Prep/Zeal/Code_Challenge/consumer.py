import os, json, time, signal, threading
from flask import Flask, Response
from confluent_kafka import Consumer, KafkaException
import psycopg2

BOOTSTRAP = os.getenv("KAFKA_BOOTSTRAP", "redpanda:9092")
INPUT_TOPIC = os.getenv("INPUT_TOPIC", "events.raw")
POSTGRES_DSN = os.getenv("POSTGRES_DSN", "postgresql://zeal:zeal@postgres:5432/events")

stop = False
message_count = 0

def _stop(*_):
    global stop
    stop = True

signal.signal(signal.SIGINT, _stop)
signal.signal(signal.SIGTERM, _stop)

# Simple Flask app for Prometheus metrics
app = Flask(__name__)

@app.route("/metrics")
def metrics():
    return Response(f"consumer_messages_total {message_count}\n", mimetype="text/plain")

def start_metrics_server():
    app.run(host="0.0.0.0", port=8000)

def ensure_table_and_view(conn):
    with conn.cursor() as cur:
        cur.execute("""
            CREATE TABLE IF NOT EXISTS events (
                id BIGINT GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
                user_id INT,
                event_type TEXT,
                ts_ms BIGINT,
                payload JSONB,
                received_at TIMESTAMPTZ DEFAULT NOW()
            );
        """)
        conn.commit()

        cur.execute("""
            CREATE OR REPLACE VIEW events_hourly_view AS
            SELECT
                date_trunc('hour', to_timestamp(ts_ms / 1000.0)) AS event_hour,
                event_type,
                COUNT(*) AS event_count,
                COUNT(DISTINCT user_id) AS unique_users
            FROM events
            GROUP BY 1, 2
            ORDER BY 1 DESC, 2;
        """)
        conn.commit()
        print("🧮 Created or replaced view 'events_hourly_view'")

def main():
    global message_count

    # Start metrics server in background
    threading.Thread(target=start_metrics_server, daemon=True).start()
    print("📊 Metrics endpoint started on :8000")

    # Kafka consumer
    c = Consumer({
        "bootstrap.servers": BOOTSTRAP,
        "group.id": "zeal-consumer",
        "auto.offset.reset": "earliest",
        "enable.auto.commit": True,

        # 🔧 Important Redpanda/Kafka network stability settings
        "security.protocol": "PLAINTEXT",
        "broker.address.family": "v4",
        "socket.keepalive.enable": True,
        "connections.max.idle.ms": 0,   # keep connection alive
        "session.timeout.ms": 45000,
    })

    c.subscribe([INPUT_TOPIC])

    # Connect to Postgres
    conn = None
    for attempt in range(30):
        try:
            conn = psycopg2.connect(POSTGRES_DSN)
            break
        except Exception as e:
            print(f"⏳ Waiting for Postgres... ({e})")
            time.sleep(2)
    if conn is None:
        raise RuntimeError("Postgres not reachable")

    ensure_table_and_view(conn)
    print("🎧 Consumer listening... Ctrl+C to stop.")

    try:
        while not stop:
            msg = c.poll(1.0)
            if msg is None:
                continue
            if msg.error():
                raise KafkaException(msg.error())
            try:
                evt = json.loads(msg.value())
                with conn.cursor() as cur:
                    cur.execute(
                        "INSERT INTO events (user_id, event_type, ts_ms, payload) VALUES (%s, %s, %s, %s::jsonb)",
                        (evt.get("user_id"), evt.get("event_type"), evt.get("ts"), json.dumps(evt)),
                    )
                conn.commit()
                message_count += 1
                print(f"📥 stored event user={evt.get('user_id')} type={evt.get('event_type')} total={message_count}")
            except Exception as e:
                print(f"❌ processing error: {e}")
                conn.rollback()
    finally:
        print("🛑 Closing consumer...")
        c.close()
        conn.close()
        print("✅ Consumer exited.")

if __name__ == "__main__":
    main()
