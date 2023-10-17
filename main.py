import os
import yaml
import json
import asyncio
from datetime import datetime

from app.extractor import Extractor


def load_config():
    with open('app/config.yaml', 'r') as f:
        config = yaml.safe_load(f)
    return config


def save_data(data, path):
    try:
        os.makedirs(os.path.dirname(path), exist_ok=True)
        with open(path, 'w') as f:
            json.dump(data, f, indent=4, ensure_ascii=False)
    except FileNotFoundError as e:
        print(f"Error: {e}. Path: {path}")


async def extract_table(url, path):
    extractor = Extractor()
    data = await extractor.extract(url)
    path = path.format(datetime=datetime.now().strftime("%Y%m%d_%H%M%S"))
    save_data(data, path)


async def main():
    config = load_config()
    tasks = []

    for tabela in config['tabelas']:
        tasks.append(asyncio.create_task(extract_table(tabela['url'], tabela['path'])))

    await asyncio.gather(*tasks)


if __name__ == "__main__":
    asyncio.run(main())
