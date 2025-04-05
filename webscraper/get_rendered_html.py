import asyncio
import aiofiles
from pyppeteer import launch

async def write_rendered_html_to_file(page_url: str, filename: str):
    """
    Uses Pyppeteer to launch a headless browser, navigate to the page URL,
    wait for the JavaScript to render, and then write the fully rendered HTML to a file.
    
    :param page_url: URL of the webpage to fetch.
    :param filename: The file path where the HTML will be saved.
    """
    try:
        # Launch a headless browser.
        browser = await launch(headless=True)
        page = await browser.newPage()
        
        # Navigate to the page and wait until network is idle (i.e., JS has rendered).
        await page.goto(page_url, {'waitUntil': 'networkidle0'})
        
        # Get the full rendered HTML content.
        html = await page.content()
        
        # Write the HTML to a file.
        async with aiofiles.open(filename, 'w', encoding='utf-8') as f:
            await f.write(html)
        print(f"Successfully wrote rendered HTML to {filename}")
        
        # Close the browser.
        await browser.close()
    except Exception as e:
        print(f"Error: {e}")

# Example usage:
async def main():
    url = "https://scrapemequickly.com/all_cars?scraping_run_id=b6bcf7b7-120c-11f0-9ce5-0242ac120003"
    filename = "rendered_webpage.html"
    await write_rendered_html_to_file(url, filename)

if __name__ == "__main__":
    asyncio.run(main())
