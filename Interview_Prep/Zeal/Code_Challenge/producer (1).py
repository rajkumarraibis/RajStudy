import os, json, time, random, signal
from datetime import datetime
from confluent_kafka import Producer

BOOTSTRAP = os.getenv("KAFKA_BOOTSTRAP", "redpanda:9092")
TOPIC = os.getenv("TOPIC", "events.raw")

stop = False
def _stop(*_):
    global stop; stop = True
signal.signal(signal.SIGINT, _stop)
signal.signal(signal.SIGTERM, _stop)

p = Producer({
    "bootstrap.servers": BOOTSTRAP,
    "client.id": "zeal-producer",
})

def on_delivery(err, msg):
    if err:
        print(f"❌ delivery failed: {err}")
    else:
        print(f"✅ delivered to {msg.topic()}[{msg.partition()}]@{msg.offset()}")

print("🚀 Starting producer... Ctrl+C to stop.")
i = 0
try:
    while not stop:
        evt = {
            "id": i,
            "user_id": i % 5,
            "event_type": random.choice([\"click\",\"view\",\"purchase\"]),
            "ts": int(time.time()*1000),
            "iso": datetime.utcnow().isoformat(timespec=\"seconds\") + \"Z\",
        }
        p.produce(TOPIC, json.dumps(evt).encode(), callback=on_delivery)
        p.poll(0)
        # short, responsive sleep
        for _ in range(random.randint(3,8)):
            if stop: break
            time.sleep(1)
        i += 1
finally:
    print(\"🛑 Stopping producer... flushing...\")
    p.flush(5)
    print(\"✅ Producer exited.\")
