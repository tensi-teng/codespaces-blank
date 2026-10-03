from datetime import datetime,timedelta
from airflow import DAG
from airflow.operators.bash import BashOperator

with DAG(
    "argus_academic_pipeline",
    start_date=datetime(2026,1,1),
    schedule="0 2 * * *",
    catchup=False,
    default_args={"retries":1,"retry_delay":timedelta(minutes=2)},
    tags=["argus","education","data-engineering"]
) as dag:

    generate=BashOperator(
        task_id="generate_data",
        bash_command="python /opt/airflow/scripts/generate_data.py --students 1000 --semesters 4"
    )
    ingest=BashOperator(
        task_id="ingest_bronze",
        bash_command="python -m src.argus.etl.ingest",
        env={"PYTHONPATH":"/opt/airflow","DATABASE_URL":"postgresql+psycopg2://argus:argus@host.docker.internal:5432/argus"}
    )
    validate=BashOperator(
        task_id="validate",
        bash_command="python -m src.argus.quality.validate",
        env={"PYTHONPATH":"/opt/airflow","DATABASE_URL":"postgresql+psycopg2://argus:argus@host.docker.internal:5432/argus"}
    )
    dbt=BashOperator(
        task_id="dbt_build",
        bash_command="cd /opt/airflow/dbt/argus_warehouse && dbt build --profiles-dir ."
    )
    risk=BashOperator(
        task_id="risk_engine",
        bash_command="python -m src.argus.analytics.risk_engine",
        env={"PYTHONPATH":"/opt/airflow","DATABASE_URL":"postgresql+psycopg2://argus:argus@host.docker.internal:5432/argus"}
    )
    generate >> ingest >> validate >> dbt >> risk
