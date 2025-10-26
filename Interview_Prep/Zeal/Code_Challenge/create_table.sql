-- Optional: run manually if you want to pre-provision
CREATE TABLE IF NOT EXISTS events (
  id BIGINT GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
  user_id INT,
  event_type TEXT,
  ts_ms BIGINT,
  payload JSONB,
  received_at TIMESTAMPTZ DEFAULT NOW()
);

CREATE OR REPLACE VIEW events_hourly_view AS
SELECT
  date_trunc('hour', to_timestamp(ts_ms / 1000.0)) AS event_hour,
  event_type,
  COUNT(*) AS event_count,
  COUNT(DISTINCT user_id) AS unique_users
FROM events
GROUP BY 1, 2
ORDER BY 1 DESC, 2;
