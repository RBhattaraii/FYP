import asyncio
from playwright.async_api import async_playwright

async def main():
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        page = await browser.new_page()
        
        async def log_request(route, request):
            if "api" in request.url:
                print(f"API CALL: {request.url}")
            await route.continue_()
            
        await page.route("**/*", log_request)
        
        print("Navigating to CGDigital...")
        await page.goto("https://cgdigital.com.np/search/laptop")
        await page.wait_for_timeout(5000)
        
        await browser.close()

if __name__ == "__main__":
    asyncio.run(main())
