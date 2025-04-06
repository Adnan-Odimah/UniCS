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
    # thread_gen(THREAED_COUNT, END_IDX, PROXIES, SCRAPING_RUN_ID)
    # data = handle_data()

    token_url = f"https://api.scrapemequickly.com/get-token?scraping_run_id={SCRAPING_RUN_ID}"
    res = requests.get(token_url)
    token = res.json().get("token")


    # print(res.status_code)
    # print(res.text)
    # print(token)




    api_url = f"https://api.scrapemequickly.com/cars/test?scraping_run_id={SCRAPING_RUN_ID}&per_page=100000&start=0"
    res2 = requests.get(api_url, headers=headers)

    # print(res2.status_code)
    # print(res2.json())


    #submit(data, SCRAPING_RUN_ID)



if __name__ == "__main__":
    # timer for speed
    start_time = time.time()
    main()
    end_time = time.time()
    # print(f"Time taken: {end_time - start_time} seconds")