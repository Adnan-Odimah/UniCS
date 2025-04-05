import asyncio
import aiohttp

async def scrape_page(page_url: str, start_indx: int, session: aiohttp.ClientSession, semaphore: asyncio.Semaphore):
    # Build the URL by replacing the {index} placeholder with the start_indx value
    # example imput: page_url = "https://api.scrapemequickly.com/cars/test?scraping_run_id=b6bcf7b7-120c-11f0-9ce5-0242ac120003&per_page=25&start={index}"

    url = page_url.format(index=start_indx)
    
    async with semaphore:
        async with session.get(url) as response:
            response.raise_for_status()
            data = await response.json()
    
    # Extract the required fields (price, year, make) from each car in the data
    results = []
    for car in data.get("data", []):
        # Only add the car if the necessary keys exist
        if "price" in car and "year" in car and "make" in car:
            results.append({
                "price": car["price"],
                "year": car["year"],
                "make": car["make"]
            })
    return results


