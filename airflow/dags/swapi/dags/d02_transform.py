import pandas as pd
from tools.file_maneger import load_config
from datetime import datetime
from airflow import DAG
from airflow.operators.python_operator import PythonOperator
import logging
from swapi.scripts.modules import Saneamento
import json

# logging.basicConfig(level=logging.INFO)


def preparation_work(**kwargs):
    files = kwargs['ti'].xcom_pull(task_ids='extract', key='files')
    configs_work = load_config("swapi_configs.json").get("work")

    if len(files) > 0:
        for file in files:
            json_data = json.load(open(file["file"], "r"))
            df = pd.DataFrame.from_records(json_data)
            san = Saneamento(df, configs_work, file["table"])
            san.rename()
            san.normalize_dtype()
            san.normalize_null()
            san.tipagem()
            san.normalize_str()
            san.null_tolerance()
            san.save_work()
    else:
        print("sem dados novos")

    return True


def generate_dag(dag):
    task = PythonOperator(
        task_id='transform',
        python_callable=preparation_work,
        provide_context=True,
        dag=dag
    )

    return task
