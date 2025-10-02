"""
Airflow DAG for Iceberg maintenance & DQ checks
Runs daily
"""

from airflow import DAG
from airflow.operators.bash import BashOperator
from datetime import datetime

with DAG("iceberg_maintenance", start_date=datetime(2025,1,1), schedule_interval="@daily", catchup=False) as dag:
    compaction = BashOperator(
        task_id="compact_iceberg",
        bash_command="spark-submit --class org.apache.iceberg.actions.CompactTable s3://scripts/compact.py"
    )

    dq = BashOperator(
        task_id="data_quality_check",
        bash_command="python3 dq_check.py"
    )

    compaction >> dq
