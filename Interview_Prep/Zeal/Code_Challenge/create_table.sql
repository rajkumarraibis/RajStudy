CREATE TABLE IF NOT EXISTS hourly_user_events (
  window_start   TIMESTAMP NOT NULL,
  user_id        TEXT NOT NULL,
  event_type     TEXT NOT NULL,
  event_count    INTEGER NOT NULL,
  PRIMARY KEY (window_start, user_id, event_type)
);
