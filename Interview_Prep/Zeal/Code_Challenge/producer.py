import os, json, time, random, signal
from datetime import datetime
from confluent_kafka import Producer

BOOTSTRAP = os.getenv("KAFKA_BOOTSTRAP", "redpanda:9092")
TOPIC = os.getenv("TOPIC", "events.raw")

stop = False
def _stop(*_):
    global stop
    stop = True
signal.signal(signal.SIGINT, _stop)
signal.signal(signal.SIGTERM, _stop)

p = Producer({
    "bootstrap.servers": BOOTSTRAP,
    "client.id": "zeal-producer",
    "security.protocol": "PLAINTEXT",
    "broker.address.family": "v4",
})

EVENT_TYPES = ["page_view", "login", "purchase", "logout"]

def make_event(i: int) -> dict:
    return {
        "id": i,
        "user_id": random.randint(1000, 1020),
        "event_type": random.choice(EVENT_TYPES),
        "ts": int(time.time() * 1000),
        "iso": datetime.utcnow().isoformat(timespec="seconds") + "Z",
    }

def dr(err, msg):
    if err:
        print(f"❌ delivery failed: {err}")
    else:
        print(f"✅ delivered to {msg.topic()}[{msg.partition()}]@{msg.offset()}")

print("🚀 Starting producer... Ctrl+C to stop.")
i = 0
try:
    while not stop:
        evt = make_event(i)
        p.produce(TOPIC, json.dumps(evt).encode(), callback=dr)
        p.poll(0)
        sleep_total = random.randint(2, 6)
        for _ in range(sleep_total):
            if stop:
                break
            time.sleep(1)
        i += 1
finally:
    print("🛑 Stopping producer... flushing...")
    p.flush(5)
    print("✅ Producer exited.")
