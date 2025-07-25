import requests
from bs4 import BeautifulSoup
from collections import Counter
import re
import sys
import json
import threading as th
from more_itertools import minmax

BASE_URL = "https://scrapemequickly.com/cars/static/"
RUN_ID = f"?scraping_run_id="
TEAM_ID = "3dcee599-120c-11f0-b749-0242ac120003"

data = {"year": [], "price": [], "make": []}

async def scrape_page(page_url: str, session: requests.Session):
    """
    Scrapes pages with IDs in [start_idx, end_idx] from base_url
    and computes the min year, max year, average price, and mode make.

    :param base_url: The URL pattern where pages can be fetched.
                     For example, 'http://example.com/car?id='
    :param start_idx: The starting ID to scrape.
    :param end_idx:   The ending ID to scrape.
    :return: A dictionary with min_year, max_year, avg_price, mode_make
    """

    # year, price, make

    # Loop through the specified range of IDs
    try:
        async with session.get(page_url) as response:
            html = await response.text()
    except Exception as e:
        # print(f"Failed to fetch {page_url}: {e}")
        return None, None, None

    # -- REGEX PATTERNS --
    # 1) Year pattern (example: "Year: 1997")
    #    We'll capture the 4-digit year in a group.
    year_pattern = r"Year:</strong>\s*(\d{4})"

    # 2) Price pattern (example: "Price: $12573")
    #    We'll capture digits, ignoring the "$" sign.
    price_pattern = r"Price:</strong>\s*\$?(\d+)"

    # 3) Make pattern (example: "Audi, A4" => we want "Audi")
    #    We'll capture the brand name before the comma.
    make_pattern = r">([A-Za-z]+), ([A-Za-z]+)</h2>"

    # -- EXTRACT YEAR --
    year_str = None
    match_year = re.search(year_pattern, html)
    ## print(match_year)
    if match_year:
        year = int(match_year.group(1))  # e.g., "1997"
      #  # print("year", year_str)

    # -- EXTRACT PRICE --
    price_str = None
    match_price = re.search(price_pattern, html)
    ## print(match_price)
    if match_price:
        price = int(match_price.group(1))  # e.g., "12573"

    # -- EXTRACT MAKE --
    brand_part = None
    match_make = re.search(make_pattern, html)
    if match_make:
        make = match_make.group(1)  # e.g., "Audi"

    return year, price, make

def start_scraping_run():
    r = requests.post(f"https://api.scrapemequickly.com/scraping-run?team_id={TEAM_ID}")

    if r.status_code != 200:
        # print(r.json())
        # print("Failed to start scraping run")
        sys.exit(1)

    return r.json()["data"]["scraping_run_id"]

def submit(answers: dict, scraping_run_id: str) -> bool:
    r = requests.post(
        f"https://api.scrapemequickly.com/cars/solve?scraping_run_id={scraping_run_id}",
        data=json.dumps(answers),
        headers={"Content-Type": "application/json"}
    )

    if r.status_code != 200:
        # print(r.json())
        # print("Failed to submit answers")
        return False

    return True

def page_finder(start_idx: int, end_idx: int, _session, scraping_run_id):
    for i in range(start_idx, end_idx):
        url = f"{BASE_URL}{i}{RUN_ID}{scraping_run_id}"
        year, price, make = scrape_page(url, _session)
        if year and price and make:
            data["year"].append(year)
            data["price"].append(price)
            data["make"].append(make)
        else:
           # # print(year, price, make)
            ## print(f"No data found for {url}")
            pass

def thread_gen(thread_count, end_idx, proxies, scraping_run_id):
    threads = []
    split_idx = end_idx // thread_count
    for i in range(thread_count):
        if i > 4:
            session = requests.Session()
        else:
            proxy = proxies[i]
            session = requests.Session()
            session.proxies.update({"http": proxy, "https": proxy})
        start_idx = i * split_idx
        end_idx = start_idx + split_idx
        thread = th.Thread(target=page_finder, args=(start_idx, end_idx, session, scraping_run_id))
        threads.append(thread)
        thread.start()

    for thread in threads:
        thread.join()

def handle_data():
    """
    get the data that they need and send it to their server
    """
    # print(data)
    years, prices = data["year"], data["price"]
    makes = data["make"]

    min_year, max_year = minmax(years)
    total = 0
    count = 0
    for price in prices:
        total += price
        count += 1
    avg_price = total / count
    mode_make = Counter(makes).most_common(1)[0][0]

    answers = {
        "min_year": min_year,
        "max_year": max_year,
        "avg_price": avg_price,
        "mode_make": mode_make
    }

    return answers