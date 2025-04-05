import aiohttp
import asyncio
import json
from collections import Counter
from _func_aysnc import scrape_page
import time
from more_itertools import minmax

BASE_URL = "https://scrapemequickly.com/all_cars?"
RUN_ID = f"scraping_run_id="
TEAM_ID = "3dcee599-120c-11f0-b749-0242ac120003"

with open("proxies.txt", "r") as f:
    PROXIES = [line.strip() for line in f.readlines()]

END_IDX = 25_000

async def get_token(scraping_run_id: str):
    async with aiohttp.ClientSession() as session:
        async with session.get(f"https://api.scrapemequickly.com/get-token?scraping_run_id={scraping_run_id}") as response:
            return (await response.json())["token"]

async def start_scraping_run():
    async with aiohttp.ClientSession() as session:
        start = time.perf_counter()
        async with session.post(f"https://api.scrapemequickly.com/scraping-run?team_id={TEAM_ID}") as response:
            return (await response.json())["data"]["scraping_run_id"], start

def handle_data(data):
    years, prices, makes = [], [], []
    for el in data:
        for el2 in el:
            years.append(el2["year"])
            prices.append(el2["price"])
            makes.append(el2["make"])
    return {
        "min_year": min(years),
        "max_year": max(years),
        "avg_price": sum(prices) / len(prices),
        "mode_make": Counter(makes).most_common(1)[0][0]
    }

async def worker(proxy, indices, scraping_run_id, token, semaphore):
    async with aiohttp.ClientSession() as session:
        tasks = [scrape_page(index, session, proxy, scraping_run_id, token, semaphore) for index in indices]
        results = await asyncio.gather(*tasks)
        return [r for r in results if r]

async def main(CONCURRENT_PER_PROXY):
    idx_split = END_IDX // len(PROXIES)
    starts_per = []

    for i in range(len(PROXIES)):
        starts_per.append([])
        for j in range(i*idx_split, (i+1)*idx_split, 25):
            starts_per[i].append(j)

    scraping_run_id, start = await start_scraping_run()
    token = await get_token(scraping_run_id)
    semaphore = asyncio.Semaphore(CONCURRENT_PER_PROXY)

    tasks = [worker(PROXIES[i], starts_per[i], scraping_run_id, token, semaphore) for i in range(len(PROXIES))]
    data = await asyncio.gather(*tasks)

    flat_data = [item for sublist in data for item in sublist]
    result = handle_data(flat_data)

    end = time.perf_counter()
    print(f"Time taken: {end - start} seconds")
    return result

if __name__ == "__main__":
    CONCURRENT_PER_PROXY = 3
    result = asyncio.run(main(CONCURRENT_PER_PROXY))
    print(result)
