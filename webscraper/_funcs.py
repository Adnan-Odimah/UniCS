import requests
from bs4 import BeautifulSoup
import sys
import json
import threading as th
BASE_URL = "https://scrapemequickly.com/cars/static/"
RUN_ID = f"?scarping_run_id="
TEAM_ID = "3dcee599-120c-11f0-b749-0242ac120003"

data = {"year": [], "price": [], "make": []}

def scrape_page(page_url: str, session: requests.Session):
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
        response = session.get(page_url)
        response.raise_for_status()  # Raise an exception for 4xx/5xx responses
    except requests.exceptions.RequestException as e:
        print(f"Failed to fetch {page_url}: {e}")

    soup = BeautifulSoup(response.text, 'html.parser')

    # --- Extract the Year ---
    # Example: if the page has  <p>Year: 1997</p>
    year_text = soup.find(text=lambda t: "Year:" in t)
    if year_text:
        # year_text might be "Year: 1997", so split on ':'
        # Then strip() and convert to int.
        year_str = year_text.split(":")[-1].strip()


    # --- Extract the Price ---
    # Example: <p>Price: $12573</p>
    price_text = soup.find(text=lambda t: "Price:" in t)
    if price_text:
        # Might be something like "Price: $12573"
        price_str = price_text.split(":")[-1].strip().lstrip('$')


    # --- Extract the Make ---
    # Example: <h2>Ford, Aerostar</h2> or <p>Make: Ford</p>
    # For demonstration, let's assume there's a line "Ford, Aerostar"
    # and you only want the brand name "Ford".
    make_text = soup.find(text=lambda t: "," in t)  # e.g. "Ford, Aerostar"
    if make_text:
        brand_part = make_text.split(",")[0].strip()



    return year_str, price_str, brand_part

def start_scraping_run():
    r = requests.post(f"https://api.scrapemequickly.com/scraping-run?team_id={TEAM_ID}")

    if r.status_code != 200:
        print(r.json())
        print("Failed to start scraping run")
        sys.exit(1)

    return r.json()["data"]["scraping_run_id"]

def submit(answers: dict, scraping_run_id: str) -> bool:
    r = requests.post(
        f"https://api.scrapemequickly.com/cars/solve?scraping_run_id={scraping_run_id}",
        data=json.dumps(answers),
        headers={"Content-Type": "application/json"}
    )

    if r.status_code != 200:
        print(r.json())
        print("Failed to submit answers")
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
            print(f"No data found for {url}")

def thread_gen(thread_count, end_idx, proxies, scraping_run_id):
    threads = []
    split_idx = end_idx // thread_count
    for i in range(thread_count):
        if i == 6:
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
    return {}

# data = {
#     "year": [ "1999", "2004", ... ],
#     "price": [ "12500", "13999", ... ],
#     "make": [ "ford", "toyota", ... ]
# }
