import aiohttp
import asyncio
import json
from collections import Counter
from _func_aysnc import scrape_page, test_rate_limit
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
            if response.status != 200:
                raise Exception("Failed to start scraping run")
            return (await response.json())["data"]["scraping_run_id"], start

async def submit(answers: dict, scraping_run_id: str):
    max_retries = 5
    base_delay = 1
    await asyncio.sleep(1)
    time.sleep(1)

    for attempt in range(max_retries):
        try:
            async with aiohttp.ClientSession() as session:
                async with session.post(
                    f"https://api.scrapemequickly.com/cars/solve?scraping_run_id={scraping_run_id}",
                    data=json.dumps(answers),
                    headers={"Content-Type": "application/json"}
                ) as response:
                    if response.status == 429:  # Rate limit
                        retry_after = int(response.headers.get('Retry-After', base_delay * (2 ** attempt)))
                        print("rate limit", retry_after)
                        await asyncio.sleep(retry_after)
                        continue

                    if response.status != 200:
                        print(response.status)
                        if attempt == max_retries - 1:
                            raise Exception(f"Failed to submit answers after {max_retries} attempts. Status: {response.status}")
                        print("rate limit 2")
                        await asyncio.sleep(base_delay * (2 ** attempt))
                        continue

                    return await response.json()

        except (aiohttp.ClientConnectionError, aiohttp.ClientError) as e:
            if attempt == max_retries - 1:
                raise Exception(f"Failed to submit answers after {max_retries} attempts: {str(e)}")
            print("rate limit error")
            await asyncio.sleep(base_delay * (2 ** attempt))
            continue

    raise Exception("Failed to submit answers after all retries")


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

    min_year, max_year = minmax(years)
    avg_price = sum(prices) / len(prices)
    mode_make = Counter(makes).most_common(1)[0][0]

    answers = {
        "min_year": min_year,
        "max_year": max_year,
        "avg_price": avg_price,
        "mode_make": mode_make
    }

    return answers

async def worker(proxy, indices, scraping_run_id, token, BASE_DELAY, CONCURRENT_PER_PROXY):
    semaphore = asyncio.Semaphore(CONCURRENT_PER_PROXY)
    async with aiohttp.ClientSession() as session:
        tasks = [scrape_page(index, session, proxy, scraping_run_id, token, semaphore, BASE_DELAY) for index in indices]

        results = await asyncio.gather(*tasks, return_exceptions=True)
        return [r for r in results if not isinstance(r, Exception)]

async def main(CONCURRENT_PER_PROXY, BASE_DELAY):
    idx_split = END_IDX // len(PROXIES)

    starts_per = []

    for i in range(5):
        starts_per.append([])
        for j in range(i*idx_split, (i+1)*idx_split, 25):
            starts_per[i].append(j)


    scraping_run_id, start = await start_scraping_run()
    #scraping_run_id = await start_scraping_run()

#    scraping_run_id = await start_scraping_run()
    token = await get_token(scraping_run_id)

    tasks = [worker(PROXIES[i], starts_per[i], scraping_run_id, token, BASE_DELAY, CONCURRENT_PER_PROXY) for i in range(len(PROXIES))]
    data = await asyncio.gather(*tasks, return_exceptions=True)

    # Flatten the data and filter out any remaining errors
    flat_data = []
    for proxy_data in data:
        for item in proxy_data:
            if not isinstance(item, Exception):
                flat_data.append(item)
            else:
                print(item)

    with open("data1.json", "w") as f:
        json.dump(flat_data, f)

    data = handle_data(flat_data)
    time_taken = time.perf_counter() - start
    print(f"Time taken: {time_taken} seconds")


    await submit(data, scraping_run_id)

if __name__ == "__main__":

#        CONCURRENT_PER_PROXY = int(sys.argv[1])
#        BASE_DELAY = float(sys.argv[2])

#   2 | 0.0097 | 21.48 - 15-20RL

#   3 |

#   1 |

    CONCURRENT_PER_PROXY =  2
    BASE_DELAY = 0

    asyncio.run(main(CONCURRENT_PER_PROXY, BASE_DELAY))
    #asyncio.run(main2(5))