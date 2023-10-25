import asyncio
from datetime import datetime
import os

from airflow import DAG
from airflow.operators.python_operator import PythonOperator

from tools.file_maneger import load_config, write
from swapi.scripts.modules import Extractor

from dotenv import load_dotenv

load_dotenv()


async def extract(endpoint, save_path):
    extractor = Extractor()
    url = os.getenv("base_url") + endpoint + "?page={page}"
    data = await extractor.extract(url)
    save_path = os.getenv("raw_path") + save_path.format(datetime=datetime.now().strftime("%Y%m%d_%H%M%S"))
    write(data, save_path)


async def main():
    config = load_config("swapi_configs.json").get("work")
    tasks = []
    for k, v in config.items():
        tasks.append(asyncio.create_task(
            extract(v["endpoint"], v['raw_path'])
        ))
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
