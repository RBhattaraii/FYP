import asyncio
from playwright.async_api import async_playwright

async def intercept_hukut():
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        context = await browser.new_context(
            user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
        )
        page = await context.new_page()

        def log_request(request):
            if "api-server" in request.url and "list" in request.url:
                print(f"API CALL: {request.url}")
                print(f"PAYLOAD: {request.post_data}")

        # Listen to all requests
        page.on("request", log_request)

        print("Navigating to Hukut search...")
        await page.goto("https://hukut.com/search?q=macbook", wait_until="networkidle")
        
        await asyncio.sleep(2)
        await browser.close()

if __name__ == "__main__":
    asyncio.run(intercept_hukut())
