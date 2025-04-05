import threading as th
from _funcs import scrape_page, start_scraping_run, submit, page_finder, handle_data
import requests
import time

END_IDX = 100
THREAED_COUNT = 6

with open("proxies.txt", "r") as f:
    PROXIES = f.read().splitlines()

sessions = []
data = {"year": [], "price": [], "make": []}

def main():
    threads = []
    split_idx = END_IDX // THREAED_COUNT
    for i in range(THREAED_COUNT):
        if i == 6:
            session = requests.Session()
            sessions.append(session)
        else:
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


if __name__ == "__main__":
    # timer for speed
    start_time = time.time()
    main()
    end_time = time.time()
    print(f"Time taken: {end_time - start_time} seconds")
    print(data)
