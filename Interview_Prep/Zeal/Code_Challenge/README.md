# Quick Start (All-in-Docker)

## Files
- `docker-compose.yml` — runs Redpanda, Console UI, Postgres, pgAdmin, topics init, Producer, and Consumer.
- `producer.py` — simple JSON event producer.
- `consumer.py` — consumes events and writes to Postgres table `events`.

## Run
```bash
docker compose up --build
```
- Redpanda Console: http://localhost:8080
- Postgres: `postgresql://zeal:zeal@localhost:5432/events` (pgAdmin at http://localhost:5050)

## Stop
```bash
docker compose down
```

## Notes
- Everything talks to Kafka at `redpanda:9092` inside Docker (no host networking issues).
- Change event rate by adjusting the small sleep loop in `producer.py`.
