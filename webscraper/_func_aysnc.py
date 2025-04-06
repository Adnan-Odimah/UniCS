import asyncio
import aiohttp
from aiohttp import ClientResponseError
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
                        ## # print(f"Rate limited. Waiting {retry_after} seconds before retry...")
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
           # # print(f"Rate limited. Waiting {retry_after} seconds before retry...")
                await asyncio.sleep(retry_after)
                continue
            raise  # Re-raise if it's not a rate limit error

        except Exception as e:
            if attempt == max_retries - 1:  # Last attempt
                # # print(f"Failed after {max_retries} attempts: {str(e)}")
                sys.exit(1)
                raise e

            delay = base_delay * (2 ** attempt)
            # # print(f"Error occurred, retrying in {delay} seconds...")
            await asyncio.sleep(delay)

async def scrape_page3(start_indx: int, session: aiohttp.ClientSession, proxy: str, scraping_run_id: str, token, semaphore, base_delay: float):
    max_retries = 10
    for _ in range(max_retries):
        try:
            async with semaphore:
                url = f"https://api.scrapemequickly.com/cars/test?scraping_run_id={scraping_run_id}&per_page=25&start={start_indx}"

                async with session.get(url, proxy=proxy, headers=await get_headers(token, scraping_run_id)) as response:
                    if response.status == 429:  # Rate limit
 #                       print("rl")
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
                   # print(results)
                return results

        except ClientResponseError as e:
            if e.status == 429:  # Rate limit
                #print("rl")
                await asyncio.sleep(base_delay)
                continue
            raise  # Re-raise if it's not a rate limit error

        except Exception as e:
            #print("rl2", e)

            # # print(f"Error occurred, retrying in {delay} seconds...")
            await asyncio.sleep(base_delay)

async def scrape_page(start_indx: int, session: aiohttp.ClientSession, proxy: str, scraping_run_id: str, token, semaphore, base_delay: float):
    max_retries = 50  # Reduced from 20 to 10
    headers = await get_headers(token, scraping_run_id)  # Cache headers

    for attempt in range(max_retries):
        try:
            async with semaphore:
                url = f"https://api.scrapemequickly.com/cars/test?scraping_run_id={scraping_run_id}&per_page=25&start={start_indx}"
                async with session.get(url, proxy=proxy, headers=headers) as response:
                    if response.status == 429:  # Rate limit
                        await asyncio.sleep(base_delay)
                        continue

                    data = await response.json()
                    if not data.get("data"):
                        continue

                    # Fast single pass data extraction
                    return [
                        {"price": car["price"], "year": car["year"], "make": car["make"]}
                        for car in data["data"]
                        if all(k in car for k in ("price", "year", "make"))
                    ]

        except Exception:
            await asyncio.sleep(base_delay)
            continue

    raise Exception(f"Failed to get data after {max_retries} attempts")

# Example usage in main or another async function:
# rate_limit = await test_rate_limit(scraping_run_id, token, PROXIES[0])
