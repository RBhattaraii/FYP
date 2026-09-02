import asyncio
import urllib.parse
from datetime import datetime, timezone
import requests

from scrapers.utils import clean_price, calculate_discount, USER_AGENT

async def fetch_cgdigital_page(search_query: str, encoded_query: str, page: int, headers: dict) -> list:
    url = f"https://www.cgdigital.com.np/api/web-search?keywords={encoded_query}&page={page}"
    products = []
    
    try:
        loop = asyncio.get_event_loop()
        response = await loop.run_in_executor(
            None, 
            lambda: requests.get(url, headers=headers, timeout=15)
        )
        
        if response.status_code != 200:
            return []
            
        data = response.json()
        
        if 'data' not in data or 'products' not in data['data']:
            return []
            
        items = data['data']['products']
        
        for item in items:
            try:
                product_id = item.get('id')
                product_name = item.get('name')
                
                if not product_name or not product_id:
                    continue
                    
                product_url = f"https://cgdigital.com.np/product/{product_id}"
                
                raw_price = item.get('price')
                raw_discount_price = item.get('discount_price')
                
                original_price = clean_price(str(raw_price)) if raw_price else None
                selling_price = clean_price(str(raw_discount_price)) if raw_discount_price else None
                
                if not selling_price or selling_price <= 0:
                    selling_price = original_price
                    original_price = None
                elif original_price and selling_price >= original_price:
                    original_price = None

                discount_percentage = calculate_discount(original_price, selling_price)
                
                image_url = item.get('featured_image')
                
                rating = None
                raw_ratings = item.get('ratings')
                if raw_ratings:
                    try:
                        rating = float(raw_ratings)
                    except ValueError:
                        pass
                
                product = {
                    "product_name": product_name,
                    "price": selling_price,
                    "original_price": original_price,
                    "discount_percentage": discount_percentage,
                    "product_url": product_url,
                    "image_url": image_url,
                    "platform": "cgdigital",
                    "rating": rating,
                    "review_count": None,
                    "search_term": search_query.lower(),
                    "scraped_at": datetime.now(timezone.utc).isoformat(),
                    "source": "cgdigital_scraper",
                }
                products.append(product)
            except Exception as e:
                pass
                
        return products
    except Exception as e:
        return []

async def async_scrape_cgdigital(search_query: str):
    """
    Asynchronous scraper for CG Digital.
    Fetches up to 3 pages concurrently to get more products.
    """
    encoded_query = urllib.parse.quote(search_query)
    
    headers = {
        "User-Agent": USER_AGENT,
        "Accept": "application/json, text/plain, */*",
        "Origin": "https://cgdigital.com.np",
        "Referer": f"https://cgdigital.com.np/search/{encoded_query}"
    }
    
    products = []
    try:
        # Fetch first 3 pages concurrently
        tasks = [
            fetch_cgdigital_page(search_query, encoded_query, page, headers)
            for page in range(1, 4)
        ]
        results = await asyncio.gather(*tasks)
        
        for page_products in results:
            products.extend(page_products)
            
        # Optional: remove duplicates if API returns same items across pages incorrectly
        seen = set()
        unique_products = []
        for p in products:
            if p["product_url"] not in seen:
                seen.add(p["product_url"])
                unique_products.append(p)
                
        print(f"  CGDIGITAL SCRAPER: Parsed {len(unique_products)} valid products")
        return unique_products
        
    except Exception as e:
        print(f"  CGDIGITAL SCRAPER: Error scraping: {e}")
        return []
