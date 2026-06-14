import asyncio
from playwright.async_api import async_playwright

async def intercept_better():
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        context = await browser.new_context(
            user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
        )
        page = await context.new_page()

        def log_request(request):
            url = request.url.lower()
            if 'betterappliances' in url or 'wix' in url:
                if 'query' in url or 'search' in url or 'graphql' in url or 'v1' in url:
                    print(f"XHR/FETCH: {request.url}")

        page.on("request", log_request)

        print("Navigating to search page...")
        try:
            await page.goto("https://www.thebetterappliances.com/search?q=tv", wait_until="networkidle", timeout=20000)
            await asyncio.sleep(5)
        except Exception as e:
            print(f"Error/Timeout: {e}")
            
        print("Done.")
        await browser.close()

if __name__ == "__main__":
    asyncio.run(intercept_better())
