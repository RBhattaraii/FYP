import asyncio
import json
from playwright.async_api import async_playwright

async def main():
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        page = await browser.new_page()
        
        async def handle_response(response):
            if "web-search" in response.url:
                print(f"Intercepted web-search response: {response.url}")
                try:
                    data = await response.json()
                    print(f"Found products: {len(data['data']['products'])}")
                except Exception as e:
                    print("Error reading json:", e)
                    
        page.on("response", handle_response)
        
        print("Navigating to CGDigital...")
        await page.goto("https://cgdigital.com.np/search/laptop")
        await page.wait_for_timeout(5000)
        
        await browser.close()

if __name__ == "__main__":
    asyncio.run(main())
