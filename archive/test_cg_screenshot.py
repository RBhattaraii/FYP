import asyncio
from playwright.async_api import async_playwright

async def main():
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        page = await browser.new_page()
        print("Navigating to CGDigital search laptop...")
        await page.goto("https://cgdigital.com.np/search/laptop")
        await page.wait_for_timeout(5000)
        await page.screenshot(path="cg_laptop.png")
        print("Screenshot saved to cg_laptop.png")
        
        # also try 'tv'
        print("Navigating to CGDigital search tv...")
        await page.goto("https://cgdigital.com.np/search/tv")
        await page.wait_for_timeout(5000)
        await page.screenshot(path="cg_tv.png")
        print("Screenshot saved to cg_tv.png")
        
        await browser.close()

if __name__ == "__main__":
    asyncio.run(main())
