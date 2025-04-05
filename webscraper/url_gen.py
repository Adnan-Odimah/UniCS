import aiohttp
import asyncio
import json
from collections import Counter
from _func_aysnc import scrape_page
import time

BASE_URL = "https://scrapemequickly.com/all_cars?"
RUN_ID = f"scraping_run_id="
TEAM_ID = "3dcee599-120c-11f0-b749-0242ac120003"

with open("proxies.txt", "r") as f:
    PROXIES = [line.strip() for line in f.readlines()]

SESSIONS = asyncio.Queue()

CONCURRENT_PER_PROXY = 200
END_IDX = 1000

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



async def setup_sessions():
    for _ in PROXIES:
        session = aiohttp.ClientSession()
        await SESSIONS.put(session)


def handle_data(data: dict):
    """
    get the data that they need and send it to their server
    """
    years = data["year"]
    prices = data["price"]
    makes = [m.lower().strip() for m in data["make"]]

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

async def fetch(start_idx: int, session: aiohttp.ClientSession, proxy: str, scraping_run_id: str, token):
    data = await scrape_page(start_idx, session, proxy, scraping_run_id, token)
    return data

async def main():
    await setup_sessions()

    idx_per_session = END_IDX // 25

    idx_per_proxy = idx_per_session // len(PROXIES)
    start_offset = 0

    idxs = []

    for i in range(len(PROXIES)):
        start_idx = i * idx_per_session
        idxs.append(start_idx)

    scraping_run_id, start = await start_scraping_run()
    tasks = []
    sessions = []

    for i, proxy in enumerate(PROXIES):
        session = await SESSIONS.get()
        sessions.append(session)
        tasks.append([fetch(index, session, proxy, scraping_run_id, await get_token(scraping_run_id)) for index in range(start_offset, start_offset + idx_per_proxy)])
        start_offset += idx_per_proxy

    data = await asyncio.gather(*tasks)

    # Close all sessions after we're done
    for session in sessions:
        await session.close()

    with open("data2.json", "w") as f:
        json.dump(data, f)

    end = time.perf_counter()
    print(f"Time taken: {end - start}")

    print(handle_data(data))
    #await submit(data, scraping_run_id, SESSIONS.get())



if __name__ == "__main__":
    asyncio.run(main())