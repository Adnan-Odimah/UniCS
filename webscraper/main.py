import threading as th
from _funcs import scrape_page
import requests

END_IDX = 100
THREAED_COUNT = 5
BASE_URL = "https://scrapemequickly.com/cars/static/"
SCRAPING_RUN_ID = "b6bcf7b7-120c-11f0-9ce5-0242ac120003"
RUN_ID = f"?scarping_run_id={SCRAPING_RUN_ID}"
with open("proxies.txt", "r") as f:
    PROXIES = f.read().splitlines()

sessions = []
data = {"year": [], "price": [], "make": []}

def main():
    threads = []
    split_idx = END_IDX // THREAED_COUNT
    for i in range(THREAED_COUNT):
        proxy = PROXIES[i]
        session = requests.Session()
        session.proxies.update({"http": proxy, "https": proxy})
        sessions.append(session)
        start_idx = i * split_idx
        end_idx = start_idx + split_idx
        thread = th.Thread(target=page_finder, args=(start_idx, end_idx, session))
        threads.append(thread)
        thread.start()

    for thread in threads:
        thread.join()

def page_finder(start_idx: int, end_idx: int, _session):
    for i in range(start_idx, end_idx):
        url = f"{BASE_URL}{i}{RUN_ID}"
        year, price, make = scrape_page(url, _session)
        if year and price and make:
            data["year"].append(year)
            data["price"].append(price)
            data["make"].append(make)
        else:
            print(f"No data found for {url}")

def handle_data(year: int, price: int, make: str):
    pass

if __name__ == "__main__":
    main()
    print(data)
