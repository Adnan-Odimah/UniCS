import asyncio
import aiohttp

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

async def scrape_page(start_indx: int, session: aiohttp.ClientSession, proxy: str, scraping_run_id: str, token, semaphore):

    async with semaphore:
        url = f"https://api.scrapemequickly.com/cars/test?scraping_run_id={scraping_run_id}&per_page=25&start={start_indx}"

        async with session.get(url, proxy=proxy, headers=await get_headers(token, scraping_run_id)) as response:
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
