import aiohttp
import asyncio
import json
from collections import Counter
from _func_aysnc import scrape_page
import time
from more_itertools import minmax
from typing import List, Dict, Any
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

BASE_URL = "https://scrapemequickly.com/all_cars?"
RUN_ID = f"scraping_run_id="
TEAM_ID = "3dcee599-120c-11f0-b749-0242ac120003"

with open("proxies.txt", "r") as f:
    PROXIES = [line.strip() for line in f.readlines()]

END_IDX = 25_000
BATCH_SIZE = 40  # Adjust based on API limits and performance testing

class Scraper:
    def __init__(self, concurrent_per_proxy: int, base_delay: float):
        self.concurrent_per_proxy = concurrent_per_proxy
        self.base_delay = base_delay
        self.session = None
        self.scraping_run_id = None
        self.token = None
        self.start_time = None

    async def __aenter__(self):
        self.session = aiohttp.ClientSession()
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        if self.session:
            await self.session.close()

    async def get_token(self) -> str:
        async with self.session.get(f"https://api.scrapemequickly.com/get-token?scraping_run_id={self.scraping_run_id}") as response:
            return (await response.json())["token"]

    async def start_scraping_run(self):
        self.start_time = time.perf_counter()
        async with self.session.post(f"https://api.scrapemequickly.com/scraping-run?team_id={TEAM_ID}") as response:
            if response.status != 200:
                raise Exception("Failed to start scraping run")
            self.scraping_run_id = (await response.json())["data"]["scraping_run_id"]
            self.token = await self.get_token()

    async def submit(self, answers: Dict[str, Any]) -> Dict[str, Any]:
        max_retries = 3  # Reduced from 5
        base_delay = 0.00888

        #answers = {"min_year": 1990, "max_year": 2024, "avg_price": 10000, "mode_make": "Toyota"}

        for attempt in range(max_retries):
            try:
                async with self.session.post(
                    f"https://api.scrapemequickly.com/cars/solve?scraping_run_id={self.scraping_run_id}",
                    data=json.dumps(answers),
                    headers={"Content-Type": "application/json"}
                ) as response:
                    if response.status == 429:
                        await asyncio.sleep(base_delay)
                        continue

                    if response.status != 200:
                        if attempt == max_retries - 1:
                            with open("error.txt", "w") as f:
                                f.write(await response.text())
                            raise Exception(f"Failed to submit answers after {max_retries} attempts, {await response.text()}")
                        await asyncio.sleep(base_delay)
                        continue

                    return await response.json()

            except Exception:
                if attempt == max_retries - 1:
                    raise
                await asyncio.sleep(base_delay)
                continue

        raise Exception("Failed to submit answers after all retries")

    def process_batch(self, batch: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Process a batch of data efficiently"""
        if not batch:
            raise Exception("No valid data found in batch")

        try:
            # Fast single pass processing
            years = []
            prices = []
            makes = []

            for item in batch:
                if isinstance(item, Exception):
                    print(item)
                for car in item:
                            years.append(car["year"])
                            prices.append(car["price"])
                            makes.append(car["make"])


            if not years:
                raise Exception("No valid data points found")

            return {
                "min_year": min(years),
                "max_year": max(years),
                "avg_price": sum(prices) // len(prices),
                "mode_make": Counter(makes).most_common(1)[0][0]
            }
        except Exception as e:
            logger.error(f"Error processing batch: {e}")
            raise

    async def worker(self, proxy: str, indices: List[int]) -> List[Dict[str, Any]]:
        semaphore = asyncio.Semaphore(self.concurrent_per_proxy)
        tasks = [
            scrape_page(
                index,
                self.session,
                proxy,
                self.scraping_run_id,
                self.token,
                semaphore,
                self.base_delay
            ) for index in indices
        ]
        return await asyncio.gather(*tasks, return_exceptions=True)

    async def run(self):
        idx_split = END_IDX // len(PROXIES)

        # Generate indices more efficiently
        starts_per = [
            list(range(i * idx_split, (i + 1) * idx_split, BATCH_SIZE))
            for i in range(len(PROXIES))
        ]

        await self.start_scraping_run()

        # Single chunk per proxy for maximum speed
        tasks = [
            self.worker(PROXIES[i], starts_per[i])
            for i in range(len(PROXIES))
        ]

        # Process results efficiently
        results = await asyncio.gather(*tasks, return_exceptions=True)

        # Fast data processing
        processed_data = []
        for proxy_results in results:
            if not isinstance(proxy_results, Exception) and proxy_results:
                processed_data.extend(proxy_results)

        if not processed_data:
            raise Exception("No data collected")

        final_results = self.process_batch(processed_data)
        await self.submit(final_results)  # Submit immediately after processing
        return final_results

async def main(concurrent_per_proxy: int = 2, base_delay: float = 0):
    async with Scraper(concurrent_per_proxy, base_delay) as scraper:
        results = await scraper.run()
        print(results)
        # Uncomment to submit results
        await scraper.submit(results)

if __name__ == "__main__":
    asyncio.run(main())