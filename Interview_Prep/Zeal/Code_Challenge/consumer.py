import json
import time
from confluent_kafka import Consumer, KafkaException
import psycopg2

# 🔹 Kafka / Redpanda connection
BROKER = "localhost:9094"
TOPIC = "events.raw"

# 🔹 Postgres connection
DB_CONFIG = {
    "dbname": "events",
    "user": "zeal",
    "password": "zeal",
    "host": "localhost",
    "port": "5432",
}


def save_to_postgres(event):
    """Insert event into Postgres safely."""
    with psycopg2.connect(**DB_CONFIG) as conn:
        with conn.cursor() as cur:
            cur.execute(
                """
                INSERT INTO events (user_id, event_type, event_timestamp)
                VALUES (%s, %s, %s)
                """,
                (event["user_id"], event["event_type"], event["timestamp"]),
            )
        conn.commit()


def main():
    consumer_conf = {
        "bootstrap.servers": "127.0.0.1:9092",   # force IPv4 instead of 'localhost'
        "group.id": "zeal-consumer-1",
        "security.protocol": "PLAINTEXT",
        "broker.address.family": "v4",           # <-- avoid IPv6/::1 edge cases
        "session.timeout.ms": 45000,
        "socket.keepalive.enable": True,
        "enable.auto.commit": False,
        "auto.offset.reset": "earliest",
        # "debug": "broker"  # uncomment if you want verbose connection logs
    }



    consumer = Consumer(consumer_conf)
    consumer.subscribe([TOPIC])

    print("🚀 Consumer started. Listening for events... (Ctrl+C to stop)")

    try:
        while True:
            msg = consumer.poll(1.0)

            if msg is None:
                continue
            if msg.error():
                raise KafkaException(msg.error())

            try:
                event = json.loads(msg.value().decode("utf-8"))
                save_to_postgres(event)
                consumer.commit(msg, asynchronous=False)
                print(f"✅ Saved event and committed offset {msg.offset()}: {event}")

            except json.JSONDecodeError:
                print(f"⚠️ Skipping invalid JSON message: {msg.value()}")
            except Exception as e:
                print(f"❌ Error processing message: {e}")
                time.sleep(1)  # small pause to avoid tight loop on DB errors

    except KeyboardInterrupt:
        print("\n🛑 Consumer stopped manually.")
    finally:
        consumer.close()


if __name__ == "__main__":
    main()
