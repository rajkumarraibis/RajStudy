# Quick Start (All-in-Docker, minimal & interview-friendly)

## What this runs
- **Redpanda** (Kafka-compatible broker) + **Console UI**
- **Postgres** + **pgAdmin**
- **Producer** (simulated events at irregular intervals)
- **Consumer** (ingests to Postgres, builds hourly view, prints stall alerts)

## Run
```bash
docker compose up -d --build
```
- Redpanda Console: http://localhost:8080
- pgAdmin: http://localhost:5050 (admin@zeal.com / zeal123)
- Postgres: `postgresql://zeal:zeal@localhost:5432/events`

## Stop
```bash
docker compose down -v
```

## What to demo
1. **Flow**: Producer → Redpanda → Consumer → Postgres
2. **Transformation**: `events_hourly_view` (hourly count + unique users)
3. **Observability (lite)**:
   - Redpanda Console shows topic health & throughput
   - Consumer logs print an **ALERT** if no messages processed for 60s
   - Query KPIs in pgAdmin

## Useful SQL
```sql
-- Hourly KPIs
SELECT * FROM events_hourly_view ORDER BY event_hour DESC, event_type;

-- Total processed
SELECT COUNT(*) AS total_events FROM events;

-- Recent events
SELECT id, user_id, event_type, to_timestamp(ts_ms/1000.0) AS ts
FROM events ORDER BY id DESC LIMIT 10;
```
