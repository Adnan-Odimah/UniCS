import aiohttp
import aiofiles
import asyncio

async def write_html_to_file(page_url: str, session: aiohttp.ClientSession, filename: str):
    """
    Fetches the raw HTML from the given page_url using the provided aiohttp session
    and writes the HTML content to a file specified by filename.

    :param page_url: URL of the webpage to fetch.
    :param session: An aiohttp.ClientSession() instance.
    :param filename: The file path where the HTML will be saved.
    """
    try:
        async with session.get(page_url, timeout=10) as response:
            response.raise_for_status()  # Raise exception for HTTP errors
            html = await response.text()
    except Exception as e:
        # print(f"Failed to fetch {page_url}: {e}")
        return

    try:
        async with aiofiles.open(filename, 'w', encoding='utf-8') as f:
            await f.write(html)
        # print(f"Successfully wrote HTML to {filename}")
    except Exception as e:
        # print(f"Failed to write HTML to {filename}: {e}")

# Example usage
async def main():
    url = "https://scrapemequickly.com/cars/static/0?scraping_run_id=89d5dca4-0a34-11f0-b686-4a33b21d14f6"
    filename = "webpage.html"
    async with aiohttp.ClientSession() as session:
        await write_html_to_file(url, session, filename)

if __name__ == "__main__":
    asyncio.run(main())
