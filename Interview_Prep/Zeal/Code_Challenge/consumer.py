import os, json, time, signal
from confluent_kafka import Consumer, KafkaException
import psycopg2

BOOTSTRAP = os.getenv(\"KAFKA_BOOTSTRAP\", \"redpanda:9092\")
INPUT_TOPIC = os.getenv(\"INPUT_TOPIC\", \"events.raw\")
POSTGRES_DSN = os.getenv(\"POSTGRES_DSN\", \"postgresql://zeal:zeal@postgres:5432/events\")

stop = False
def _stop(*_):
    global stop; stop = True
signal.signal(signal.SIGINT, _stop)
signal.signal(signal.SIGTERM, _stop)

def ensure_table(conn):
    with conn.cursor() as cur:
        cur.execute(
            \"\"\"CREATE TABLE IF NOT EXISTS events (
              id BIGINT GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
              user_id INT,
              event_type TEXT,
              ts_ms BIGINT,
              payload JSONB,
              received_at TIMESTAMPTZ DEFAULT NOW()
            );\"\"\"
        )
        conn.commit()

def main():
    # Kafka
    c = Consumer({
        \"bootstrap.servers\": BOOTSTRAP,
        \"group.id\": \"zeal-consumer\",
        \"auto.offset.reset\": \"earliest\",
        \"enable.auto.commit\": True,
    })
    c.subscribe([INPUT_TOPIC])

    # DB (retry until ready)
    conn = None
    for attempt in range(30):
        try:
            conn = psycopg2.connect(POSTGRES_DSN)
            break
        except Exception as e:
            print(f\"⏳ Waiting for Postgres... ({e})\")
            time.sleep(2)
    if conn is None:
        raise RuntimeError(\"Postgres not reachable\")
    ensure_table(conn)

    print(\"🎧 Consumer listening... Ctrl+C to stop.\")
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
                        \"INSERT INTO events (user_id, event_type, ts_ms, payload) VALUES (%s,%s,%s,%s::jsonb)\",
                        (evt.get(\"user_id\"), evt.get(\"event_type\"), evt.get(\"ts\"), json.dumps(evt))
                    )
                conn.commit()
                print(f\"📥 stored event user={evt.get('user_id')} type={evt.get('event_type')}\")
            except Exception as e:
                print(f\"❌ processing error: {e}\")
                conn.rollback()
    finally:
        print(\"🛑 Closing consumer...\")
        try:
            c.close()
        finally:
            if conn:
                conn.close()
        print(\"✅ Consumer exited.\")

if __name__ == '__main__':
    main()
