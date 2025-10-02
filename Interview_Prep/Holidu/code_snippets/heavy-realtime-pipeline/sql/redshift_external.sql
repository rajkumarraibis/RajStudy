-- Redshift Spectrum external table on Iceberg
CREATE EXTERNAL SCHEMA spectrum_iceberg
FROM DATA CATALOG
DATABASE 'holidu_db'
IAM_ROLE 'arn:aws:iam::123456789012:role/RedshiftSpectrumRole'
CREATE EXTERNAL DATABASE IF NOT EXISTS;

-- Query Iceberg table
SELECT property_id, count(*) as bookings, sum(price) as gmv
FROM spectrum_iceberg.silver_events
GROUP BY property_id;