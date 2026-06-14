import asyncio
from playwright.async_api import async_playwright

async def intercept_jeevee():
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        context = await browser.new_context(
            user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
        )
        page = await context.new_page()

        def log_request(request):
            url = request.url.lower()
            if 'jeevee' in url or 'api' in url or 'search' in url:
                print(f"XHR/FETCH: {request.url}")

        page.on("request", log_request)

        print("Navigating to https://www.jeevee.com/")
        try:
            await page.goto("https://www.jeevee.com/", wait_until="networkidle", timeout=30000)
            
            # Let's see if there is an input we can type into
            search_input = await page.query_selector('input[type="text"]')
            if search_input:
                print("Found input, typing 'facewash'...")
                await search_input.fill("facewash")
                await search_input.press("Enter")
                await asyncio.sleep(5)
            else:
                print("No text input found")
        except Exception as e:
            print(f"Error/Timeout: {e}")
            
        print("Done.")
        await browser.close()

if __name__ == "__main__":
    asyncio.run(intercept_jeevee())
