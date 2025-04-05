import requests
from bs4 import BeautifulSoup
from collections import Counter
import re 

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
        response.raise_for_status()
    except requests.exceptions.RequestException as e:
        print(f"Failed to fetch {page_url}: {e}")
        return None, None, None

    html = response.text

    # -- REGEX PATTERNS --
    # 1) Year pattern (example: "Year: 1997")
    #    We'll capture the 4-digit year in a group.
    year_pattern = r"Year:\s*(\d{4})"

    # 2) Price pattern (example: "Price: $12573")
    #    We'll capture digits, ignoring the "$" sign.
    price_pattern = r"Price:\s*\$?(\d+)"

    # 3) Make pattern (example: "Audi, A4" => we want "Audi")
    #    We'll capture the brand name before the comma.
    make_pattern = r"([A-Za-z]+)\s*,\s*\S+"

    # -- EXTRACT YEAR --
    year_str = None
    match_year = re.search(year_pattern, html)
    if match_year:
        year_str = int(match_year.group(1))  # e.g., "1997"

    # -- EXTRACT PRICE --
    price_str = None
    match_price = re.search(price_pattern, html)
    if match_price:
        price_str = int(match_price.group(1))  # e.g., "12573"

    # -- EXTRACT MAKE --
    brand_part = None
    match_make = re.search(make_pattern, html)
    if match_make:
        brand_part = match_make.group(1)  # e.g., "Audi"

    return year_str, price_str, brand_part



