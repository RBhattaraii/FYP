import asyncio
from playwright.async_api import async_playwright

async def intercept_cgdigital():
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        context = await browser.new_context(
            user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
        )
        page = await context.new_page()

        def log_request(request):
            url = request.url.lower()
            if "cgdigital.com.np" in url:
                if not any(ext in url for ext in ['.jpg', '.jpeg', '.png', '.webp', '.css', '.js', '.woff', '.ico']):
                    print(f"XHR/FETCH: {request.url}")
                    if request.post_data:
                        print(f"PAYLOAD: {request.post_data}")

        page.on("request", log_request)

        print("Navigating to https://cgdigital.com.np/search/macbook")
        await page.goto("https://cgdigital.com.np/search/macbook", wait_until="networkidle")
        
        await asyncio.sleep(3)
        await browser.close()

if __name__ == "__main__":
    asyncio.run(intercept_cgdigital())
