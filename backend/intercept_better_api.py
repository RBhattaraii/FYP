import asyncio
import json
from playwright.async_api import async_playwright

async def get_wix_search_api():
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        context = await browser.new_context(
            user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
        )
        page = await context.new_page()

        def log_request(request):
            url = request.url.lower()
            if 'search-services' in url:
                print(f"API CALL: {request.url}")
                if request.post_data:
                    print(f"PAYLOAD: {request.post_data}")
                    
        page.on("request", log_request)

        print("Navigating to https://www.thebetterappliances.com/search?q=tv")
        try:
            await page.goto("https://www.thebetterappliances.com/search?q=tv", wait_until="networkidle", timeout=25000)
            await asyncio.sleep(5)
        except Exception as e:
            print(f"Error/Timeout: {e}")
            
        await browser.close()

if __name__ == "__main__":
    asyncio.run(get_wix_search_api())
