import asyncio
from datetime import datetime
import os

from airflow import DAG
from airflow.operators.python_operator import PythonOperator

from tools.file_maneger import load_config, write
from swapi.scripts.modules import Extractor

from dotenv import load_dotenv

load_dotenv()


async def extract(name, endpoint, save_path):
    extractor = Extractor()
    url = os.getenv("base_url") + endpoint + "?page={page}"
    data = await extractor.extract(url)
    save_path = os.getenv("raw_path") + save_path.format(datetime=datetime.now().strftime("%Y%m%d_%H%M%S"))
    file_name = write(data, save_path)
    return {"table": name, "file": file_name}


async def main():
    config = load_config("swapi_configs.json").get("work")
    tasks = []
    for k, v in config.items():
        tasks.append(asyncio.create_task(
            extract(v["name"], v["endpoint"], v['raw_path'])
        ))

    files = await asyncio.gather(*tasks)
    return files


def run(**kwargs):
    files = asyncio.run(main())
    kwargs['ti'].xcom_push(key='files', value=files)


def generate_dag(dag):
    task = PythonOperator(
        task_id='extract',
        python_callable=run,
        provide_context=True,
        dag=dag
    )

    return task
