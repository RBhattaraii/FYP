import json
import requests
import asyncio
import urllib.parse
from datetime import datetime, timezone
from scrapers.utils import calculate_discount, USER_AGENT
from scrapers.daraz.daraz_scraper import _executor

async def async_scrape_hukut(search_query: str):
    """
    Asynchronous scraper for Hukut Store.
    Hukut uses Next.js with a hidden backend API. We can directly POST to their
    ElasticSearch endpoint for lightning-fast results without a browser.
    """
    url = "https://hukut.com/api-server/v1/product/list-elastic"
    headers = {
        "User-Agent": USER_AGENT,
        "Content-Type": "application/json",
        "Origin": "https://hukut.com",
        "Referer": f"https://hukut.com/search?q={urllib.parse.quote(search_query)}"
    }
    
    payload = {
        "searchText": search_query,
        "pagination": {"limit": 40, "offset": 0}
    }
    
    products = []
    try:
        loop = asyncio.get_event_loop()
        response = await loop.run_in_executor(
            _executor, 
            lambda: requests.post(url, headers=headers, json=payload, timeout=15)
        )
        
        if response.status_code != 200:
            print(f"  HUKUT SCRAPER: Failed to fetch. Status code: {response.status_code}")
            return []
            
        data = response.json()
        rows = data.get('data', {}).get('rows', [])
        
        for item in rows:
            product_name = item.get('name')
            slug = item.get('slug')
            if not product_name or not slug:
                continue
                
            product_url = f"https://hukut.com/product/{slug}"
            
            variant = item.get('defaultVariant', {})
            base_price = variant.get('price')
            sale_price = variant.get('salePrice')
            
            if sale_price and sale_price < base_price:
                price = float(sale_price)
                original_price = float(base_price)
            else:
                price = float(base_price) if base_price else None
                original_price = None
                
            # Fallback to sortablePrice if variant is empty
            if not price and item.get('sortablePrice'):
                price = float(item.get('sortablePrice'))
                
            discount_percentage = calculate_discount(original_price, price)
            
            image_obj = item.get('image', {})
            image_url = image_obj.get('cdn') or image_obj.get('url')
            
            rating = item.get('averageRating')
            if rating:
                try:
                    rating = float(rating)
                except ValueError:
                    rating = None
            
            product = {
                "product_name": product_name,
                "price": price,
                "original_price": original_price,
                "discount_percentage": discount_percentage,
                "product_url": product_url,
                "image_url": image_url,
                "platform": "hukut_store",
                "rating": rating,
                "review_count": None,
                "search_term": search_query.lower(),
                "scraped_at": datetime.now(timezone.utc).isoformat(),
                "source": "hukut_scraper",
            }
            products.append(product)
            
        print(f"  HUKUT SCRAPER: Parsed {len(products)} valid products")
        return products
        
    except Exception as e:
        print(f"  HUKUT SCRAPER: Error scraping: {e}")
        return []