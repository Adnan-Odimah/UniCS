import aiohttp
import asyncio
import json
from collections import Counter
from _func_aysnc import scrape_page
import time

BASE_URL = "https://scrapemequickly.com/all_cars?"
RUN_ID = f"scraping_run_id="
TEAM_ID = "3dcee599-120c-11f0-b749-0242ac120003"

CONCURRENT_PER_PROXY = 200

with open("proxies.txt", "r") as f:
    PROXIES = [line.strip() for line in f.readlines()]

END_IDX = 10000

async def get_token(scraping_run_id: str):
    async with aiohttp.ClientSession() as session:
        async with session.get(f"https://api.scrapemequickly.com/get-token?scraping_run_id={scraping_run_id}") as response:
            return (await response.json())["token"]

async def start_scraping_run():
    async with aiohttp.ClientSession() as session:
        async with session.post(f"https://api.scrapemequickly.com/scraping-run?team_id={TEAM_ID}") as response:
            start = time.perf_counter()
            if response.status != 200:
                raise Exception("Failed to start scraping run")
            return (await response.json())["data"]["scraping_run_id"], start

async def submit(answers: dict, scraping_run_id: str, session: aiohttp.ClientSession):
    async with session.post(f"https://api.scrapemequickly.com/cars/solve?scraping_run_id={scraping_run_id}",
                            data=json.dumps(answers),
                            headers={"Content-Type": "application/json"}) as response:
        if response.status != 200:
            raise Exception("Failed to submit answers")
        return await response.json()

def handle_data(data: dict):
    """
    get the data that they need and send it to their server
    """
    years, prices, makes = [], [], []
    for el in data:
        for el2 in el:
            years.append(el2["year"])
            prices.append(el2["price"])
            makes.append(el2["make"])

    min_year = min(years)
    max_year = max(years)
    avg_price = sum(prices) // len(prices)
    mode_make = Counter(makes).most_common(1)[0][0]

    answers = {
        "min_year": min_year,
        "max_year": max_year,
        "avg_price": avg_price,
        "mode_make": mode_make
    }
    return answers

async def worker(proxy, indices, scraping_run_id, token):
    semaphore = asyncio.Semaphore(CONCURRENT_PER_PROXY)
    async with aiohttp.ClientSession() as session:
        tasks = [scrape_page(index, session, proxy, scraping_run_id, token, semaphore) for index in indices]
        results = await asyncio.gather(*tasks, return_exceptions=True)
        # Filter out errors and return only successful responses
        return [r for r in results if not isinstance(r, Exception)]

async def main():
    idx_split = END_IDX // 25

    starts_per = []
    # each proxy needs to pic
    # [1, 2, 3, 4, 5]
    # 1 -> [0-24, 25-49, ..., idx_split]
    # 2 -> [idx_split+1, idx_split+2, ..., idx_split*2]
    # ...
    # 5 -> [idx_split*4+1, idx_split*4+2, ..., END_IDX]

    # code for it:
    for i in range(5):
        starts_per.append([])
        for j in range(i*idx_split, (i+1)*idx_split, 25):
            starts_per[i].append(j)

    y = END_IDX
    for i in range(5):
        x = sum(starts_per[i])
        y -= x
    print(y)

    return


    scraping_run_id, start = await start_scraping_run()
    token = await get_token(scraping_run_id)

    tasks = [worker(PROXIES[i], starts_per[i], scraping_run_id, token) for i in range(len(PROXIES))]
    data = await asyncio.gather(*tasks)

    # Flatten the data and filter out any remaining errors
    flat_data = []
    for proxy_data in data:
        for item in proxy_data:
            if not isinstance(item, Exception):
                flat_data.append(item)

    with open("data2.json", "w") as f:
        json.dump(flat_data, f)

    end = time.perf_counter()
    print(f"Time taken: {end - start}")

    print(handle_data(flat_data))
    #await submit(data, scraping_run_id, SESSIONS.get())



if __name__ == "__main__":
    asyncio.run(main())