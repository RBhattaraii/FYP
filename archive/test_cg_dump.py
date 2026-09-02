import asyncio
from playwright.async_api import async_playwright

async def main():
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        page = await browser.new_page()
        
        print("Navigating to CGDigital search laptop...")
        await page.goto("https://cgdigital.com.np/search/laptop")
        await page.wait_for_timeout(5000)
        
        # Save HTML
        html = await page.content()
        with open("cg_laptop.html", "w", encoding="utf-8") as f:
            f.write(html)
        print("Saved to cg_laptop.html")
        
        await browser.close()

if __name__ == "__main__":
    asyncio.run(main())
