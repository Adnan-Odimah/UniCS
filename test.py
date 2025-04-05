import requests

#url = "https://scrapemequickly.com/assets/entry.client-DX8GoJ3y.js"
url2 = "https://api.scrapemequickly.com/cars/test?scraping_run_id=b6bcf7b7-120c-11f0-9ce5-0242ac120003&per_page=25&start=0"

#response = requests.get(url2, headers={"referer": "https://scrapemequickly.com/all_cars?scraping_run_id=b6bcf7b7-120c-11f0-9ce5-0242ac120003", "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/113.0.0.0 Safari/537.36"})
response = requests.get(url2)

with open("test.js", "w") as f:
    f.write(response.text)
