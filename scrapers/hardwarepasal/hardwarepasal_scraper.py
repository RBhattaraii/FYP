import asyncio
import urllib.parse
from datetime import datetime, timezone
import requests
from bs4 import BeautifulSoup
import re

from scrapers.utils import clean_price, calculate_discount, USER_AGENT
from scrapers.daraz.daraz_scraper import _executor

async def async_scrape_hardwarepasal(search_query: str):
    """
    Asynchronous scraper for Hardware Pasal.
    Uses BeautifulSoup since the site is server-side rendered.
    """
    encoded_query = urllib.parse.quote(search_query)
    url = f"https://hardwarepasal.com/search?q={encoded_query}"
    
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
            print(f"  HARDWARE PASAL SCRAPER: Failed to fetch. Status code: {response.status_code}")
            return []
            
        soup = BeautifulSoup(response.text, 'html.parser')
        
        items = soup.find_all('div', class_='product__item')
        
        for item in items:
            try:
                name_el = item.find('div', class_='product__name')
                link_el = name_el.find('a') if name_el else None
                
                if not name_el or not link_el:
                    continue
                    
                product_name = link_el.get('title') or link_el.text.strip()
                product_url = link_el.get('href')
                
                if not product_name:
                    continue
                    
                img_el = item.find('img')
                # Usually it's in data-src or src
                image_url = None
                if img_el:
                    image_url = img_el.get('data-src') or img_el.get('src')
                    
                price_el = item.find('div', class_='product__price')
                
                original_price = None
                selling_price = None
                
                if price_el:
                    # Find all strings matching Rs. digits
                    # Get all text from price_el
                    price_text = price_el.get_text(separator=' ')
                    # Find all amounts
                    matches = re.findall(r'Rs\.?\s*([\d,]+)', price_text, re.IGNORECASE)
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
                    "platform": "hardwarepasal",
                    "rating": None,
                    "review_count": None,
                    "search_term": search_query.lower(),
                    "scraped_at": datetime.now(timezone.utc).isoformat(),
                    "source": "hardwarepasal_scraper",
                }
                
                products.append(product)
            except Exception as e:
                print(f"  HARDWARE PASAL SCRAPER: Error parsing product: {e}")
                
        print(f"  HARDWARE PASAL SCRAPER: Parsed {len(products)} products")
        return products
        
    except Exception as e:
        print(f"  HARDWARE PASAL SCRAPER: Error scraping: {e}")
        return []
