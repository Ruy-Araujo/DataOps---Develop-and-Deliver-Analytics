import logging
import httpx
import asyncio
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

