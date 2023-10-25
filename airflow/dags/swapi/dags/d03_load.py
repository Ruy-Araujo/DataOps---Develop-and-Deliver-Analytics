import os
import logging
import pandas as pd

from airflow.operators.python_operator import PythonOperator

from tools.file_maneger import load_config
from dotenv import load_dotenv

load_dotenv()


def split_string_list(data, col, qtd):
    df = data.copy()
    df['col_temp'] = df[col].map(lambda x: x.strip('][').split(', '))
    if qtd:
        df[col] = df['col_temp'].apply(lambda x: 0 if x == [''] else len([y.replace("'", "") for y in x]))
    else:
        df[col] = df['col_temp'].apply(lambda x: 0 if x == [''] else [y.replace("'", "") for y in x])

    return df[col]


def sw_work_to_dw():
    logging.info("Starting transform data to DW")
    work_path = os.getenv("work_path")
    dw_path = os.getenv("dw_path")
    dw_meta_path = os.getenv("dw_meta_path")
    configs = load_config("swapi_configs.json")

    people = pd.read_csv(work_path + configs['work']['people']['work_path'], sep=";")
    planets = pd.read_csv(work_path + configs['work']['planets']['work_path'], sep=";")
    films = pd.read_csv(work_path + configs['work']['films']['work_path'], sep=";")

    people['qtd_veiculos'] = split_string_list(people, 'url_vehicles', True)
    people['qtd_naves'] = split_string_list(people, 'url_starships', True)
    people['url_films'] = split_string_list(people, 'url_films', False)

    films['titulo_filme2'] = films['titulo_filme'].map(lambda x: x.lower().replace(" ", "_"))
    film_dict = films[['titulo_filme2', 'url_origem']].set_index('titulo_filme2').to_dict()['url_origem']

    for key in film_dict:
        people[key] = people['url_films'].apply(lambda x: 1 if film_dict[key] in x else 0)

    df = people.merge(
        planets[['nome_planeta', 'url_origem']], left_on='url_homeworld', right_on='url_origem'
    ).rename(columns={"nome_planeta": 'planeta_natal'})

    sw = df[list(pd.read_csv(f"{dw_meta_path}{configs['dw']['meta_path']}")['nome'])]
    sw.to_csv(f"{dw_path}{configs['dw']['dw_path']}", index=False)

    logging.info("Transform data to DW finished")
    return True


def generate_dag(dag):
    task = PythonOperator(
        task_id='load',
        python_callable=sw_work_to_dw,
        provide_context=True,
        dag=dag
    )

    return task
