import asyncio
import urllib.parse
from datetime import datetime, timezone
from playwright.async_api import async_playwright

from scrapers.utils import clean_price, calculate_discount, USER_AGENT

async def async_scrape_better(search_query: str):
    """
    Asynchronous scraper for Better Appliances using Playwright.
    Wix site so dynamic rendering is required.
    """
    encoded_query = urllib.parse.quote(search_query)
    url = f"https://www.thebetterappliances.com/search?q={encoded_query}"
    
    products = []
    
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        context = await browser.new_context(
            user_agent=USER_AGENT
        )
        page = await context.new_page()
        
        try:
            await page.goto(url, wait_until="domcontentloaded")
            
            # Wait for products to load, or timeout gracefully if no products
            try:
                await page.wait_for_selector("[data-hook='product-list-grid-item']", timeout=10000)
            except Exception:
                # Timeout means no products found or site didn't load properly
                print("  BETTER SCRAPER: No products found or timeout.")
                return []
                
            cards = await page.query_selector_all("[data-hook='product-list-grid-item']")
            
            for card in cards:
                try:
                    root = await card.query_selector("[data-hook='product-item-root']")
                    if not root:
                        continue
                        
                    link_el = await root.query_selector("a[data-hook='product-item-container']")
                    product_url = await link_el.get_attribute('href') if link_el else None
                    
                    name_el = await root.query_selector("[data-hook='product-item-name']")
                    product_name = await name_el.inner_text() if name_el else None
                    
                    if not product_name:
                        continue
                        
                    price_el = await root.query_selector("[data-hook='product-item-price-to-pay']")
                    price_text = await price_el.inner_text() if price_el else None
                    
                    orig_price_el = await root.query_selector("[data-hook='product-item-formatted-price']")
                    orig_price_text = await orig_price_el.inner_text() if orig_price_el else None
                    
                    price = clean_price(price_text)
                    original_price = clean_price(orig_price_text)
                    
                    # Ensure price isn't actually original price if no discount
                    if original_price and price and original_price <= price:
                        original_price = None
                        
                    discount_percentage = calculate_discount(original_price, price)
                    
                    img_el = await root.query_selector("img")
                    image_url = await img_el.get_attribute('src') if img_el else None
                    
                    if image_url and 'static.wixstatic.com' in image_url:
                        # Clean up wix image url
                        image_url = image_url.split('/v1/')[0]
                        
                    product = {
                        "product_name": product_name.strip(),
                        "price": price,
                        "original_price": original_price,
                        "discount_percentage": discount_percentage,
                        "product_url": product_url,
                        "image_url": image_url,
                        "platform": "better",
                        "rating": None,
                        "review_count": None,
                        "search_term": search_query.lower(),
                        "scraped_at": datetime.now(timezone.utc).isoformat(),
                        "source": "better_scraper",
                    }
                    products.append(product)
                except Exception as e:
                    print(f"  BETTER SCRAPER: Error parsing product: {e}")
                    
        except Exception as e:
            print(f"  BETTER SCRAPER: Error navigating: {e}")
        finally:
            await browser.close()
            
    print(f"  BETTER SCRAPER: Parsed {len(products)} products")
    return products

if __name__ == "__main__":
    asyncio.run(async_scrape_better("heater"))
