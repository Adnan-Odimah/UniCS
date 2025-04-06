import asyncio
import aiohttp
from aiohttp import ClientResponseError
import time
import sys

async def get_headers(token: str, scraping_run_id: str):
    return {
    "Authorization": f"Bearer {token}",
    "User-Agent": (
        "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) "
        "AppleWebKit/537.36 (KHTML, like Gecko) "
        "Chrome/123.0.0.0 Safari/537.36"
    ),
    "Referer": f"https://scrapemequickly.com/all_cars?scraping_run_id={scraping_run_id}",
    "Accept": "application/json, text/plain, */*",
    "Accept-Encoding": "gzip, deflate, br",
    "Accept-Language": "en-GB,en-US;q=0.9,en;q=0.8",
    "Connection": "keep-alive",
    "DNT": "1",
    }

async def scrape_page2(start_indx: int, session: aiohttp.ClientSession, proxy: str, scraping_run_id: str, token, semaphore, base_delay: float):
    max_retries = 15

    for attempt in range(max_retries):
        try:
            async with semaphore:
                url = f"https://api.scrapemequickly.com/cars/test?scraping_run_id={scraping_run_id}&per_page=25&start={start_indx}"

                async with session.get(url, proxy=proxy, headers=await get_headers(token, scraping_run_id)) as response:
                    if response.status == 429:  # Rate limit
                        retry_after = int(response.headers.get('Retry-After', base_delay * (2 ** attempt)))
                        ## print(f"Rate limited. Waiting {retry_after} seconds before retry...")
                        await asyncio.sleep(retry_after)
                        continue

                    response.raise_for_status()
                    data = await response.json()

                # Extract the required fields (price, year, make) from each car in the data
                results = []
                for car in data.get("data", []):
                    # Only add the car if the necessary keys exist
                    if "price" in car and "year" in car and "make" in car:
                        results.append({
                            "price": car["price"],
                            "year": car["year"],
                            "make": car["make"]
                        })
                return results

        except ClientResponseError as e:
            if e.status == 429:  # Rate limit
                retry_after = base_delay * (2 ** attempt)
                # print(f"Rate limited. Waiting {retry_after} seconds before retry...")
                await asyncio.sleep(retry_after)
                continue
            raise  # Re-raise if it's not a rate limit error

        except Exception as e:
            if attempt == max_retries - 1:  # Last attempt
                # print(f"Failed after {max_retries} attempts: {str(e)}")
                sys.exit(1)
                raise e

            delay = base_delay * (2 ** attempt)
            # print(f"Error occurred, retrying in {delay} seconds...")
            await asyncio.sleep(delay)

async def scrape_page(start_indx: int, session: aiohttp.ClientSession, proxy: str, scraping_run_id: str, token, semaphore, base_delay: float):
    max_retries = 200
    for attempt in range(max_retries):
        try:
            async with semaphore:
                url = f"https://api.scrapemequickly.com/cars/test?scraping_run_id={scraping_run_id}&per_page=25&start={start_indx}"

                async with session.get(url, proxy=proxy, headers=await get_headers(token, scraping_run_id)) as response:
                    if response.status == 429:  # Rate limit
                        # print(f"Rate limited. Waiting {base_delay} seconds before retry...")
                        await asyncio.sleep(base_delay)
                        continue

                    # print(response.status)
                    response.raise_for_status()
                    data = await response.json()

                # Extract the required fields (price, year, make) from each car in the data
                results = []
                for car in data.get("data", []):
                    # Only add the car if the necessary keys exist
                    if "price" in car and "year" in car and "make" in car:
                        results.append({
                            "price": car["price"],
                            "year": car["year"],
                            "make": car["make"]
                        })
                    # print(results)
                return results

        except ClientResponseError as e:
            if e.status == 429:  # Rate limit
                # print(f"Rate limited. Waiting {base_delay} seconds before retry...")
                await asyncio.sleep(retry_after)
                continue
            raise  # Re-raise if it's not a rate limit error

        except Exception as e:
            if attempt == max_retries - 1:  # Last attempt
                # print(f"Failed after {max_retries} attempts: {str(e)}")
                sys.exit(1)
                raise e

            delay = base_delay
            # print(f"Error occurred, retrying in {delay} seconds...")
            await asyncio.sleep(delay)

async def test_rate_limit(start_indx, session, proxy, scraping_run_id, token, semaphore):
    attempts = 0
    url = f"https://api.scrapemequickly.com/cars/test?scraping_run_id={scraping_run_id}&per_page=25&start={start_indx}"
    # get the exact second the test starts
    start_second = int(time.strftime("%S"))
    while start_second == int(time.strftime("%S")):
        pass
    while True:
        try:
            async with semaphore:
                async with session.get(url, proxy=proxy, headers=await get_headers(token, scraping_run_id)) as response:
                    attempts +=1
                    if response.status == 429:  # Rate limit
                        end = int(time.strftime("%S"))
                        # print(f"Rate limit hit at {attempts} attempts. Time taken: {end - start_second} seconds")
                        return attempts/(end - start_second)

        except ClientResponseError as e:
            if e.status == 429:  # Rate limit
                end = int(time.strftime("%S"))
                return attempts/(end-start_second)
            raise  # Re-raise if it's not a rate limit error


# Example usage in main or another async function:
# rate_limit = await test_rate_limit(scraping_run_id, token, PROXIES[0])
