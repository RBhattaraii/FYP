import asyncio
import urllib.parse
from datetime import datetime, timezone
import requests

from scrapers.utils import clean_price, calculate_discount, USER_AGENT
from scrapers.daraz.daraz_scraper import _executor

async def async_scrape_jeevee(search_query: str):
    """
    Asynchronous scraper for Jeevee.
    Uses their internal search API at search.jeevee.com.
    """
    encoded_query = urllib.parse.quote(search_query)
    url = "https://search.jeevee.com/search-test-updated"
    params = {
        "search": search_query,
        "item_per_page": 24,
        "page": 1,
        "pagination": "true",
        "query": search_query
    }
    
    headers = {
        "User-Agent": USER_AGENT,
        "Accept": "application/json, text/plain, */*",
        "Origin": "https://www.jeevee.com",
        "Referer": f"https://www.jeevee.com/products/search?query={encoded_query}"
    }
    
    products = []
    try:
        loop = asyncio.get_event_loop()
        response = await loop.run_in_executor(
            _executor, 
            lambda: requests.get(url, params=params, headers=headers, timeout=15)
        )
        
        if response.status_code != 200:
            print(f"  JEEVEE SCRAPER: Failed to fetch. Status code: {response.status_code}")
            return []
            
        data = response.json()
        
        if 'data' not in data or not isinstance(data['data'], list):
            print("  JEEVEE SCRAPER: Unexpected JSON structure.")
            return []
            
        items = data['data']
        
        for item in items:
            try:
                product_name = item.get('label')
                product_id = item.get('product_id')
                
                if not product_name or not product_id:
                    continue
                
                # Build slug from seo_details or label
                seo = item.get('seo_details', {})
                slug = seo.get('slug', '')
                if not slug:
                    # Build slug from label + product_id
                    slug = product_name.lower().replace(' ', '-').replace('/', '-')
                    slug = f"{slug}-{product_id}"
                else:
                    slug = f"{slug}-{product_id}"
                    
                product_url = f"https://www.jeevee.com/products/{slug}"
                
                # Price is the selling price (includes VAT)
                selling_price = item.get('price')
                
                # Discount info
                discount_obj = item.get('discount_object')
                discount_percentage = item.get('discount', 0)
                original_price = None
                
                if discount_percentage and discount_percentage > 0 and selling_price:
                    # Calculate original price from discount percentage
                    original_price = round(selling_price / (1 - discount_percentage / 100), 2)
                else:
                    discount_percentage = None
                    
                # Image - get the 512px version from first image
                image_url = None
                images = item.get('image', [])
                if images and isinstance(images, list) and len(images) > 0:
                    first_img = images[0]
                    if isinstance(first_img, dict):
                        image_url = first_img.get('512') or first_img.get('256') or first_img.get('1024')
                
                # Rating
                rating = None
                review_count = None
                review_data = item.get('review_and_rating', {})
                if review_data:
                    rating = review_data.get('avg_rating')
                    review_count = review_data.get('review_count')
                
                product = {
                    "product_name": product_name,
                    "price": selling_price,
                    "original_price": original_price,
                    "discount_percentage": discount_percentage,
                    "product_url": product_url,
                    "image_url": image_url,
                    "platform": "jeevee",
                    "rating": rating,
                    "review_count": review_count,
                    "search_term": search_query.lower(),
                    "scraped_at": datetime.now(timezone.utc).isoformat(),
                    "source": "jeevee_scraper",
                }
                
                products.append(product)
            except Exception as e:
                print(f"  JEEVEE SCRAPER: Error parsing product: {e}")
                
        print(f"  JEEVEE SCRAPER: Parsed {len(products)} valid products")
        return products
        
    except Exception as e:
        print(f"  JEEVEE SCRAPER: Error scraping: {e}")
        return []
