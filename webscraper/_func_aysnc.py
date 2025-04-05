import re
import asyncio
import aiohttp


async def scrape_page(page_url: str, session: aiohttp.ClientSession, proxy: str, semaphore: asyncio.Semaphore):
    """
    Scrapes a single page using asynchronous HTTP requests with a given proxy and semaphore.
    Extracts year, price, and make using regex.
    """

    # Regex patterns for extraction
    year_pattern = r"Year:</strong>\s*(\d{4})"
    price_pattern = r"Price:</strong>\s*\$?(\d+)"
    make_pattern = r">([A-Za-z]+), ([A-Za-z]+)</h2>"

    async with semaphore:  # Limit concurrency
        try:
            async with session.get(page_url, proxy=proxy, timeout=10) as response:
                html = await response.text()
        except Exception as e:
            print(f"Error with {proxy} for {page_url}: {e}")
            return None, None, None

        # Extract Year
        match_year = re.search(year_pattern, html)
        year = int(match_year.group(1)) if match_year else None

        # Extract Price
        match_price = re.search(price_pattern, html)
        price = int(match_price.group(1)) if match_price else None

        # Extract Make
        match_make = re.search(make_pattern, html)
        make = match_make.group(1) if match_make else None

        return year, price, make
