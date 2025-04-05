import requests
from bs4 import BeautifulSoup
from collections import Counter

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

def handle_data():
    """
    get the data that they need and send it to their server
    """
    years = data["year"]
    price = data["price"]
    make = data["make"]
    pass

# data = {
#     "year": [ "1999", "2004", ... ],
#     "price": [ "12500", "13999", ... ],
#     "make": [ "ford", "toyota", ... ]
# }

# data = {"year": [], "price": [], "make": []}