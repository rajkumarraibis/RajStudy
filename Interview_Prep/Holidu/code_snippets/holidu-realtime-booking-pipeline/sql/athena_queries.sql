-- Athena query example: Get booking counts per property per day
SELECT property_id, date_trunc('day', timestamp) as day, count(*) as bookings, sum(price) as gmv
FROM iceberg.holidu.silver_events
GROUP BY property_id, day
ORDER BY day DESC;