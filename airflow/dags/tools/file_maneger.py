import os
import json


def write(data, path):
    try:
        os.makedirs(os.path.dirname(path), exist_ok=True)
        with open(path, 'w') as f:
            json.dump(data, f, indent=4, ensure_ascii=False)
    except FileNotFoundError as e:
        print(f"Error: {e}. Path: {path}")


def read(path):
    pass


def load_config(file):
    try:
        with open(f"/opt/airflow/dags/configs/{file}", 'r') as f:
            data = json.load(f)
        return data
    except FileNotFoundError as e:
        print(f"Error: {e}. File: {file}")
