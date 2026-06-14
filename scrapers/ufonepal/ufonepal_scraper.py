import asyncio
import urllib.parse
from datetime import datetime, timezone
import requests
from bs4 import BeautifulSoup
import re

from scrapers.utils import clean_price, calculate_discount, USER_AGENT
from scrapers.daraz.daraz_scraper import _executor

async def async_scrape_ufonepal(search_query: str):
    """
    Asynchronous scraper for UFO Nepal.
    Uses BeautifulSoup since the site is server-side rendered with standard WooCommerce.
    """
    encoded_query = urllib.parse.quote(search_query)
    url = f"https://www.ufonepal.com/?s={encoded_query}&post_type=product"
    
    headers = {
        "User-Agent": USER_AGENT,
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8",
        "Accept-Language": "en-US,en;q=0.5",
    }
    
    products = []
    try:
        loop = asyncio.get_event_loop()
        response = await loop.run_in_executor(
            _executor, 
            lambda: requests.get(url, headers=headers, timeout=15)
        )
        
        if response.status_code != 200:
            print(f"  UFO NEPAL SCRAPER: Failed to fetch. Status code: {response.status_code}")
            return []
            
        soup = BeautifulSoup(response.text, 'html.parser')
        
        ul = soup.find('ul', class_='products')
        if not ul:
            print("  UFO NEPAL SCRAPER: No ul.products found. Assuming 0 results.")
            return []
            
        items = ul.find_all('li', class_=lambda c: c and 'product' in c.lower())
        
        for item in items:
            try:
                title_el = item.find(class_='woocommerce-loop-product__title')
                product_name = title_el.text.strip() if title_el else None
                
                link_el = item.find('a', class_='woocommerce-LoopProduct-link')
                product_url = link_el.get('href') if link_el else None
                
                if not product_name or not product_url:
                    continue
                    
                img_el = item.find('img')
                image_url = None
                if img_el:
                    image_url = img_el.get('data-src') or img_el.get('src')
                    
                price_el = item.find(class_='price')
                
                original_price = None
                selling_price = None
                
                if price_el:
                    # Find all amounts inside bdi tags or using regex on the raw text
                    # To be safe and handle WooCommerce del/ins structure
                    # We'll extract digits from the text
                    price_text = price_el.get_text(separator=' ')
                    # Matches "1,998" or "1998.00"
                    matches = re.findall(r'[\d,]+(?:\.\d+)?', price_text)
                    if matches:
                        prices = [clean_price(m) for m in matches if clean_price(m) is not None]
                        if len(prices) >= 2:
                            original_price = max(prices)
                            selling_price = min(prices)
                        elif len(prices) == 1:
                            selling_price = prices[0]
                
                # Validation
                if original_price and selling_price and original_price <= selling_price:
                    original_price = None
                    
                discount_percentage = calculate_discount(original_price, selling_price)
                
                product = {
                    "product_name": product_name,
                    "price": selling_price,
                    "original_price": original_price,
                    "discount_percentage": discount_percentage,
                    "product_url": product_url,
                    "image_url": image_url,
                    "platform": "ufonepal",
                    "rating": None,
                    "review_count": None,
                    "search_term": search_query.lower(),
                    "scraped_at": datetime.now(timezone.utc).isoformat(),
                    "source": "ufonepal_scraper",
                }
                
                products.append(product)
            except Exception as e:
                print(f"  UFO NEPAL SCRAPER: Error parsing product: {e}")
                
        print(f"  UFO NEPAL SCRAPER: Parsed {len(products)} products")
        return products
        
    except Exception as e:
        print(f"  UFO NEPAL SCRAPER: Error scraping: {e}")
        return []
