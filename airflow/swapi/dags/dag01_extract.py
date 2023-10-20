import os
import json
import asyncio
from datetime import datetime, timedelta

from airflow import DAG
from airflow.operators.python_operator import PythonOperator

from swpi.common_package.extractor import Extractor


def load_config():
    with open('configs/extractor.json', 'r') as f:
        default_args = json.load(f)
    return default_args


def save_data(data, path):
    try:
        os.makedirs(os.path.dirname(path), exist_ok=True)
        with open(path, 'w') as f:
            json.dump(data, f, indent=4, ensure_ascii=False)
    except FileNotFoundError as e:
        print(f"Error: {e}. Path: {path}")


async def extract(url, path):
    extractor = Extractor()
    data = await extractor.extract(url)
    path = path.format(datetime=datetime.now().strftime("%Y%m%d_%H%M%S"))
    save_data(data, path)


default_args = {
    'owner': 'Ruy',
    'depends_on_past': False,
    'start_date': datetime(2023, 10, 19),
    'retries': 1,
}

# dag = DAG('dag_extract_data', default_args=default_args, schedule_interval=None)


async def main():
    config = load_config()
    tasks = []
    for route in config['routes']:
        tasks.append(asyncio.create_task(extract(route['url'], route['path'])))
    await asyncio.gather(*tasks)


def extract_data():
    asyncio.run(main())


with DAG('dag_extract_data', default_args=default_args, schedule_interval=timedelta(hours=1)) as dag:

    task = PythonOperator(
        task_id='extract_data',
        python_callable=extract_data,
        provide_context=True,
        dag=dag
    )
