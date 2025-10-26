import json
import time
import random
from datetime import datetime
from confluent_kafka import Producer

BROKER = "localhost:9094"
TOPIC = "events.raw"

producer_config = {
    "bootstrap.servers": BROKER,
    "client.id": "zeal-producer",
    "linger.ms": 10
}

producer = Producer(producer_config)
EVENT_TYPES = ["page_view", "login", "purchase", "logout"]


def generate_event():
    """Generate a mock user event"""
    return {
        "user_id": random.randint(1000, 1020),
        "event_type": random.choice(EVENT_TYPES),
        "timestamp": datetime.utcnow().isoformat()
    }


def delivery_report(err, msg):
    if err is not None:
        print(f"❌ Delivery failed for record {msg.key()}: {err}")
    else:
        print(f"✅ Sent → {msg.value()} @ offset {msg.offset()}")


if __name__ == "__main__":
    print("🚀 Starting producer... Press Ctrl+C to stop.")
    try:
        first = True
        while True:
            event = generate_event()
            producer.produce(
                topic=TOPIC,
                key=str(event["user_id"]),
                value=json.dumps(event),
                callback=delivery_report
            )
            producer.poll(0)

            # first event immediately, then random 1–50 s
            if first:
                first = False
            else:
                wait_time = random.randint(1, 50)
                print(f"⏱️ Waiting {wait_time}s before next event...")
                time.sleep(wait_time)

    except KeyboardInterrupt:
        print("🛑 Stopping producer...")
    finally:
        producer.flush()
