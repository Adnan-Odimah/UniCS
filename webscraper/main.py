import threading as th
from _funcs import scrape_page

END_IDX = 100000
THREAED_COUNT = 10
BASE_URL = "https://scrapemequickly.com/cars/static/"
RUN_ID = "?scarping_run_id=89d5dca4-0a34-11f0-b686-4a33b21d14f6"

def main():
    threads = []
    split_idx = END_IDX // THREAED_COUNT
    for i in range(THREAED_COUNT):
        start_idx = i * split_idx
        end_idx = start_idx + split_idx
        thread = th.Thread(target=page_finder, args=(start_idx, end_idx))
        threads.append(thread)
        thread.start()

    for thread in threads:
        thread.join()

def page_finder(start_idx: int, end_idx: int):
    for i in range(start_idx, end_idx):
        url = f"{BASE_URL}{i}{RUN_ID}"
        data = scrape_page(url)
        if data:

        else:
            print(f"No data found for {url}")



if __name__ == "__main__":
    main()
