import re
import asyncio
import aiohttp


async def fetch_car_data(car_url: str, session: aiohttp.ClientSession, semaphore: asyncio.Semaphore):
    """
    Fetch a single car page and extract year, price, and make using regex.
    """

    year_pattern = r"Year:</strong>\s*(\d{4})"
    price_pattern = r"Price:</strong>\s*\$?(\d+)"
    make_pattern = r">([A-Za-z]+),\s*[A-Za-z]+</h2>"

    async with semaphore:
        try:
            async with session.get(car_url, timeout=10) as response:
                html = await response.text()
        except Exception as e:
            print(f"Error fetching {car_url}: {e}")
            return None  # Could not fetch page

    # Extract Year
    match_year = re.search(year_pattern, html)
    year = int(match_year.group(1)) if match_year else None

    # Extract Price
    match_price = re.search(price_pattern, html)
    price = int(match_price.group(1)) if match_price else None

    # Extract Make
    match_make = re.search(make_pattern, html)
    make = match_make.group(1) if match_make else None

    # Only return data if all values were found; adjust as needed if partial data is acceptable.
    if year is None or price is None or make is None:
        return None

    return {"year": year, "price": price, "make": make}

async def scrape_page(page_url: str, start_indx: int, end_index: int, session: aiohttp.ClientSession, semaphore: asyncio.Semaphore):
    """
    Scrapes car pages using the URL pattern provided (with a {car_id} placeholder) 
    for car IDs between start_indx and end_index. Returns a dictionary where the keys 
    'years', 'prices', and 'makes' map to arrays of the corresponding scraped data.
    
    :param page_url: URL pattern, e.g., "https://scrapemequickly.com/cars/static/{car_id}"
    :param start_indx: Starting car ID.
    :param end_index: Ending car ID.
    :param session: An aiohttp.ClientSession for making HTTP requests.
    :param semaphore: An asyncio.Semaphore for limiting concurrent requests.
    :return: A dictionary with keys "years", "prices", and "makes".
    """
    tasks = []
    for car_id in range(start_indx, end_index + 1):
        # Replace the placeholder with the actual car ID.
        car_url = page_url.replace("{car_id}", str(car_id))
        tasks.append(fetch_car_data(car_url, session, semaphore))
    
    # Run all tasks concurrently.
    results = await asyncio.gather(*tasks)
    
    # Filter out any failed results.
    valid_results = [res for res in results if res is not None]
    
    # Unzip the results into separate lists.
    years = [res["year"] for res in valid_results]
    prices = [res["price"] for res in valid_results]
    makes = [res["make"] for res in valid_results]
    
    return {"years": years, "prices": prices, "makes": makes}

