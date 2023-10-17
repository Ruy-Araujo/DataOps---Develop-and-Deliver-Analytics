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

    @retry()
    async def extract(self, url):
        """
        Extracts data from a given URL using HTTP requests.

        Args:
            url (str): The URL to extract data from.

        Returns:
            list: A list of results obtained by making HTTP GET requests to the URL and parsing the JSON responses.

        Raises:
            Exception: If the HTTP GET request fails or the response status code is not 200.
        """
        results = []
        page = 1

        async with httpx.AsyncClient(timeout=60) as client:
            logging.info(f"Starting data extraction from {url}...")
            while True:
                url = url.format(page=page)
                response = await client.get(url=url)
                if response.status_code == 200:
                    data = response.json()
                    results.extend(data.get("results", []))
                    next_page = data.get("next")
                    if not next_page:
                        break
                    else:
                        page += 1
                else:
                    raise Exception(f"Failed to fetch data from {url}")
        logging.info(f"Data extracted with success...")
        return results
