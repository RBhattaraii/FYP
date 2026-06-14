import asyncio
import urllib.parse
from playwright.async_api import async_playwright

async def scrape_better_playwright(search_query: str):
    encoded_query = urllib.parse.quote(search_query)
    url = f"https://www.thebetterappliances.com/search?q={encoded_query}"
    
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        context = await browser.new_context(
            user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
        )
        page = await context.new_page()
        
        try:
            print(f"Navigating to {url}")
            await page.goto(url, wait_until="domcontentloaded")
            
            # Wait for at least one product card to be visible
            print("Waiting for products...")
            await page.wait_for_selector("[data-hook='product-list-grid-item']", timeout=15000)
            
            # Now let's scrape the DOM
            products = []
            
            cards = await page.query_selector_all("[data-hook='product-list-grid-item']")
            print(f"Found {len(cards)} products via Playwright")
            
            for card in cards:
                root = await card.query_selector("[data-hook='product-item-root']")
                if not root:
                    continue
                    
                link_el = await root.query_selector("a[data-hook='product-item-container']")
                product_url = await link_el.get_attribute('href') if link_el else None
                
                name_el = await root.query_selector("[data-hook='product-item-name']")
                product_name = await name_el.inner_text() if name_el else None
                
                price_el = await root.query_selector("[data-hook='product-item-price-to-pay']")
                price = await price_el.inner_text() if price_el else None
                
                print(f"Name: {product_name}, Price: {price}")
                
        except Exception as e:
            print(f"Error: {e}")
            print(f"Content: {await page.content()}")
        finally:
            await browser.close()

if __name__ == "__main__":
    asyncio.run(scrape_better_playwright("tv"))
