import asyncio
import urllib.parse
from datetime import datetime, timezone
import requests

from scrapers.utils import clean_price, calculate_discount, USER_AGENT
from scrapers.daraz.daraz_scraper import _executor

async def async_scrape_cgdigital(search_query: str):
    """
    Asynchronous scraper for CG Digital.
    Uses their internal web-search API.
    """
    encoded_query = urllib.parse.quote(search_query)
    url = f"https://www.cgdigital.com.np/api/web-search?keywords={encoded_query}"
    
    headers = {
        "User-Agent": USER_AGENT,
        "Accept": "application/json, text/plain, */*",
        "Origin": "https://cgdigital.com.np",
        "Referer": f"https://cgdigital.com.np/search/{encoded_query}"
    }
    
    products = []
    try:
        loop = asyncio.get_event_loop()
        response = await loop.run_in_executor(
            _executor, 
            lambda: requests.get(url, headers=headers, timeout=15)
        )
        
        if response.status_code != 200:
            print(f"  CGDIGITAL SCRAPER: Failed to fetch. Status code: {response.status_code}")
            return []
            
        data = response.json()
        
        # Check if the expected structure is there
        if 'data' not in data or 'products' not in data['data']:
            print("  CGDIGITAL SCRAPER: Unexpected JSON structure.")
            return []
            
        items = data['data']['products']
        
        for item in items:
            try:
                product_id = item.get('id')
                product_name = item.get('name')
                
                if not product_name or not product_id:
                    continue
                    
                # URL is constructed using product ID
                product_url = f"https://cgdigital.com.np/product/{product_id}"
                
                # Prices are returned as raw numbers or strings like "458090"
                raw_price = item.get('price')
                raw_discount_price = item.get('discount_price')
                
                # 'discount_price' is usually the selling price if available and lower
                # Wait, "discount_price: 346590" and "price: 458090". 
                # So original_price = price, price = discount_price
                original_price = clean_price(str(raw_price)) if raw_price else None
                selling_price = clean_price(str(raw_discount_price)) if raw_discount_price else None
                
                # If there's no discount_price or it's 0, the selling price is the original price
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
                print(f"  CGDIGITAL SCRAPER: Error parsing product: {e}")
                
        print(f"  CGDIGITAL SCRAPER: Parsed {len(products)} valid products")
        return products
        
    except Exception as e:
        print(f"  CGDIGITAL SCRAPER: Error scraping: {e}")
        return []
