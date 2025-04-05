import threading as th
from _funcs import start_scraping_run, submit, handle_data, thread_gen
import requests
import time

END_IDX = 100_000
THREAED_COUNT = 6

with open("proxies.txt", "r") as f:
    PROXIES = f.read().splitlines()


def main():
    SCRAPING_RUN_ID = start_scraping_run()
    thread_gen(THREAED_COUNT, END_IDX, PROXIES, SCRAPING_RUN_ID)
    data = handle_data()
    print(data)

    #submit(data, SCRAPING_RUN_ID)



if __name__ == "__main__":
    # timer for speed
    start_time = time.time()
    main()
    end_time = time.time()
    print(f"Time taken: {end_time - start_time} seconds")