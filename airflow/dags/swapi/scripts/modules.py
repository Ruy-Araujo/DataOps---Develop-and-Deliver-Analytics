import re
import os
import json
import logging
import httpx
import asyncio
import pandas as pd
from datetime import date
from functools import wraps


class Extractor:
    """
    A class that extracts data from a given URL using HTTP requests.

    This class provides a method called `extract` that takes a URL as input and returns a list of results
    obtained by making HTTP GET requests to the URL and parsing the JSON responses. The method uses an
    `httpx.AsyncClient` object to make the requests asynchronously, and implements a retry mechanism that
    allows for a configurable number of retries and delay between retries in case of failures.

    Example usage:
    ```
    extractor = Extractor()
    results = await extractor.extract("https://example.com/api/data?page={page}")
    ```
    """
    logging.basicConfig(level=logging.INFO)

    def __init__(self):
        pass

    def retry(retries=3, delay=1):
        """
        A decorator that implements a retry mechanism for a given async function.

        The decorator takes two optional arguments: `retries` (default 3) and `delay` (default 1). The `retries`
        argument specifies the maximum number of retries to attempt in case of failures, while the `delay` argument
        specifies the delay (in seconds) between retries, which increases exponentially with each retry.

        Example usage:
        ```
        @retry(retries=5, delay=2)
        async def my_async_function():
            ...
        ```
        """
        def decorator(func):
            @wraps(func)
            async def wrapper(*args, **kwargs):
                retry_count = 0
                while retry_count < retries:
                    try:
                        result = await func(*args, **kwargs)
                        return result
                    except Exception as e:
                        retry_count += 1
                        logging.error(f"Tentativa {retry_count} falhou: {e}")
                        await asyncio.sleep(delay * (2 ** retry_count))

                logging.error(f"Todas as {retry_count} tentativas falharam.")
                return False

            return wrapper
        return decorator

    async def extract(self, url):
        """
        Asynchronously extracts data from a given URL using HTTP requests.

        Args:
            url (str): The URL to extract data from.

        Returns:
            list: A list of results obtained by making HTTP GET requests to the URL and parsing the JSON responses.

        Raises:
            Exception: If the HTTP GET request fails or the response status code is not 200.

        Example:
            extractor = Extractor()
            results = await extractor.extract('https://example.com/api/data?page={page}')
        """
        logging.info(f"Starting data extraction from {url}...")
        results = []
        page = 1
        tasks = []

        async with httpx.AsyncClient(timeout=60) as client:
            first_page = await self.extract_page(client, url.format(page=page))
            results.extend(first_page.get("results", []))

            if not first_page.get("next"):
                return results

            total_pages = first_page["count"] // len(first_page["results"])
            for page in range(2, total_pages + 1):
                tasks.append(self.extract_page(client, url.format(page=page)))
            tasks_results = await asyncio.gather(*tasks)
            results.extend([result for task_result in tasks_results for result in task_result.get("results", [])])

        logging.info(f"Data from {url} extracted with success...")
        return results

    @retry()
    async def extract_page(self, client, url):
        """
        Asynchronously extracts data from a given URL using HTTP GET requests.

        Args:
            client (aiohttp.ClientSession): The client session to use for making HTTP requests.
            url (str): The URL to extract data from.

        Returns:
            dict: A dictionary containing the JSON response obtained by making an HTTP GET request to the URL.

        Raises:
            Exception: If the HTTP GET request fails or the response status code is not 200.

        Example:
            extractor = Extractor()
            async with aiohttp.ClientSession() as client:
                data = await extractor.extract_page(client, 'https://example.com/api/data?page=1')
        """
        response = await client.get(url=url)
        if response.status_code == 200:
            data = response.json()
            return data
        else:
            raise Exception(f"Failed to fetch data from {url}")


class Saneamento:

    def __init__(self, data, configs, tabela):
        self.data = data
        self.metadado = pd.read_csv(os.getenv("meta_path") + configs[tabela]["meta_path"])
        self.len_cols = max(list(self.metadado["id"]))
        self.colunas = list(self.metadado['campo_original'])
        self.colunas_new = list(self.metadado['campo_final'])
        self.path_work = os.getenv("work_path") + configs[tabela]["work_path"]
        self.dest_data = self.load_data(configs, tabela)

    def load_data(self, configs, tabela):
        try:
            return pd.read_csv(f"{os.getenv('work_path')}{configs[tabela]['work_path']}", sep=";")
        except FileNotFoundError:
            return pd.DataFrame()

    def rename(self):
        for i in range(self.len_cols):
            self.data.rename(columns={self.colunas[i].strip(): self.colunas_new[i].strip()}, inplace=True)

    def normalize_dtype(self):
        for col in self.colunas_new:
            self.data[col] = self.data[col].astype(str)

    def normalize_null(self):
        for col in self.colunas_new:
            self.data[col].replace("unknown", None, regex=True, inplace=True)
            self.data[col].replace("n/a", None, regex=True, inplace=True)

    def tipagem(self):
        for col in self.colunas_new:
            tipo = self.metadado.loc[self.metadado['campo_final'] == col]['tipo'].item()
            if tipo == "int":
                tipo = self.data[col].astype(int)
            elif tipo == "float":
                self.data[col].replace(",", ".", regex=True, inplace=True)
                self.data[col] = self.data[col].astype(float)
            elif tipo == "date":
                self.data[col] = pd.to_datetime(self.data[col])

    def normalize_str(self):
        for col in self.colunas_new:
            tipo = self.metadado.loc[self.metadado['campo_final'] == col]['tipo'].item()
            if tipo == "string":
                self.data[col] = self.data[col].apply(
                    lambda x: x.encode('ASCII', 'ignore')
                    .decode("utf-8").lower() if x != None else None)

    def null_tolerance(self):
        for col in self.colunas_new:
            nul = self.metadado.loc[self.metadado['campo_final'] == col]['permite_nulo'].item()
            if int(nul) == 0:
                if len(self.data[self.data[col].isna()]) > 0:
                    raise Exception(f"{self.tabela} possui nulos acima do permitido")

    def check_key(self):
        for col in self.colunas_new:
            nul = self.metadado.loc[self.metadado['campo_final'] == col]['chave'].item()
            if int(nul) == 1:
                if len(self.data) != self.data[col].nunique():
                    raise Exception(f"{self.tabela} chaves duplicadas")

    def duplicate_tolerance(self):
        key_col = self.metadado['campo_final'].where(self.metadado['chave'] == 1).dropna().item()

        self.data = pd.concat([self.dest_data, self.data]) \
            .drop_duplicates(subset=key_col) \
            .dropna(subset=[key_col])

        if self.data[key_col].duplicated().any():
            raise Exception(f"{self.tabela} possui chaves duplicadas")

    def save_work(self):
        self.data["load_date"] = date.today()
        if not os.path.exists(self.path_work):
            os.makedirs(os.path.dirname(self.path_work), exist_ok=True)
            self.data.to_csv(self.path_work, index=False, sep=";")
        else:
            self.data.to_csv(self.path_work, index=False, mode='a', header=False, sep=";")
