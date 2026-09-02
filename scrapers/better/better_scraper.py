import asyncio
import urllib.parse
from datetime import datetime, timezone
from concurrent.futures import ThreadPoolExecutor
from playwright.sync_api import sync_playwright

from scrapers.utils import clean_price, calculate_discount, USER_AGENT

_executor = ThreadPoolExecutor(max_workers=2)

def _scrape_better_sync(search_query: str):
    """
    Synchronous scraper for Better Appliances using Playwright.
    Wix site so dynamic rendering is required.
    """
    encoded_query = urllib.parse.quote(search_query)
    url = f"https://www.thebetterappliances.com/search?q={encoded_query}"
    
    products = []
    
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        context = browser.new_context(user_agent=USER_AGENT)
        page = context.new_page()
        
        try:
            page.goto(url, wait_until="domcontentloaded")
            
            try:
                page.wait_for_selector("[data-hook='product-list-grid-item']", timeout=10000)
            except Exception:
                print("  BETTER SCRAPER: No products found or timeout.")
                return []
                
            cards = page.query_selector_all("[data-hook='product-list-grid-item']")
            
            for card in cards:
                try:
                    root = card.query_selector("[data-hook='product-item-root']")
                    if not root:
                        continue
                        
                    link_el = root.query_selector("a[data-hook='product-item-container']")
                    product_url = link_el.get_attribute('href') if link_el else None
                    
                    name_el = root.query_selector("[data-hook='product-item-name']")
                    product_name = name_el.inner_text() if name_el else None
                    
                    if not product_name:
                        continue
                        
                    price_el = root.query_selector("[data-hook='product-item-price-to-pay']")
                    price_text = price_el.inner_text() if price_el else None
                    
                    orig_price_el = root.query_selector("[data-hook='product-item-formatted-price']")
                    orig_price_text = orig_price_el.inner_text() if orig_price_el else None
                    
                    price = clean_price(price_text)
                    original_price = clean_price(orig_price_text)
                    
                    if original_price and price and original_price <= price:
                        original_price = None
                        
                    discount_percentage = calculate_discount(original_price, price)
                    
                    img_el = root.query_selector("img")
                    image_url = img_el.get_attribute('src') if img_el else None
                    
                    if image_url and 'static.wixstatic.com' in image_url:
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
            browser.close()
            
    print(f"  BETTER SCRAPER: Parsed {len(products)} products")
    return products

async def async_scrape_better(search_query: str):
    """
    Wrapper to run synchronous playwright inside a threadpool to prevent
    NotImplementedError on Windows asyncio loops.
    """
    loop = asyncio.get_event_loop()
    return await loop.run_in_executor(_executor, lambda: _scrape_better_sync(search_query))

if __name__ == "__main__":
    print(asyncio.run(async_scrape_better("heater")))
