from datetime import datetime, timedelta

from airflow import DAG
from airflow.operators.python_operator import PythonOperator

from swapi.dags import d01_extract

default_args = {
    'owner': 'Data Engineer',
    'depends_on_past': False,
    'start_date': datetime(2023, 10, 19),
    'retries': 0,
}


with DAG('swapi', default_args=default_args, schedule_interval=None) as dag:

    tsk1 = d01_extract.generate_dag(dag)