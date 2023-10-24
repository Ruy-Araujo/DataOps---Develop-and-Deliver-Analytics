import asyncio
from datetime import datetime

from airflow import DAG
from airflow.operators.python_operator import PythonOperator

from tools.file_maneger import load_config, write
from swapi.scripts.modules import Extractor


async def extract(url, path, save_path):
    extractor = Extractor()
    data = await extractor.extract(url)
    path = path.format(base=save_path, datetime=datetime.now().strftime("%Y%m%d_%H%M%S"))
    write(data, path)


async def main():
    config = load_config("swapi_configs.json")
    tasks = []
    for route in config['routes']:
        tasks.append(asyncio.create_task(extract(route['url'], route['path'], config['save_path'])))
    await asyncio.gather(*tasks)


def run():
    asyncio.run(main())


def generate_dag(dag):
    task = PythonOperator(
        task_id='extract',
        python_callable=run,
        provide_context=True,
        dag=dag
    )

    return task
