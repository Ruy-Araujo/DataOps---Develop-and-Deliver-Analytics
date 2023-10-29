import os
import json
import pandas as pd
from dotenv import load_dotenv
load_dotenv()


def write(data, path):
    try:
        os.makedirs(os.path.dirname(path), exist_ok=True)
        if isinstance(data, list):
            with open(path, 'w') as f:
                json.dump(data, f, indent=4, ensure_ascii=False)
        elif isinstance(data, pd.DataFrame):
            data.to_csv(path, index=False, sep=";")
        else:
            print("Data is neither a dictionary nor a DataFrame.")
            return

        return path
    except FileNotFoundError as e:
        print(f"Error: {e}. Path: {path}")


def read(path):
    pass


def load_config(file):
    try:
        with open(f'{os.getenv("config_path")}/{file}', 'r') as f:
            data = json.load(f)
        return data
    except FileNotFoundError as e:
        print(f"Error: {e}. File: {file}")
