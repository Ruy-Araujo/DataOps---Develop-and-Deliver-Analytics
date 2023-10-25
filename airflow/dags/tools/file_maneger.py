import os
import json
from dotenv import load_dotenv
load_dotenv()


def write(data, path):
    try:
        os.makedirs(os.path.dirname(path), exist_ok=True)
        with open(path, 'w') as f:
            json.dump(data, f, indent=4, ensure_ascii=False)
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
