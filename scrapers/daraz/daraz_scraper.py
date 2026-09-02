import asyncio
import urllib.parse
from datetime import datetime, timezone
import requests

from scrapers.utils import clean_price, calculate_discount, BASE_URL, USER_AGENT

def sync_scrape_daraz(search_query: str, max_pages: int = 1):
    """
    Synchronous scraper function using Daraz AJAX API directly for incredible speed.
    """
    encoded_query = urllib.parse.quote(search_query)
    all_products = []
    
    headers = {
        'User-Agent': USER_AGENT,
        'Accept': 'application/json, text/plain, */*'
    }

    for page_num in range(1, max_pages + 1):
        url = f"{BASE_URL}/catalog/?q={encoded_query}&page={page_num}&ajax=true"
        print(f"  SCRAPER: Requesting {url}")

        try:
            r = requests.get(url, headers=headers, timeout=10)
            if r.status_code != 200:
                print(f"  SCRAPER: Failed with status code {r.status_code}")
                break
                
            data = r.json()
            items = data.get('mods', {}).get('listItems', [])
            
            if not items:
                print(f"  SCRAPER: No products found on page {page_num}, stopping.")
                break
                
            for item in items:
                try:
                    product_name = item.get('name')
                    if not product_name:
                        continue
                        
                    raw_price = item.get('price')
                    raw_orig_price = item.get('originalPrice')
                    
                    price = float(raw_price) if raw_price else None
                    original_price = float(raw_orig_price) if raw_orig_price else None
                    
                    if original_price and price and original_price <= price:
                        original_price = None
                        
                    discount_percentage = calculate_discount(original_price, price)
                    
                    product_url = item.get('itemUrl', '')
                    if product_url.startswith('//'):
                        product_url = 'https:' + product_url
                        
                    image_url = item.get('image', '')
                    rating = float(item.get('ratingScore', 0)) if item.get('ratingScore') else None
                    review_count = int(item.get('review', 0)) if item.get('review') else None

                    product = {
                        "product_name": product_name,
                        "price": price,
                        "original_price": original_price,
                        "discount_percentage": discount_percentage,
                        "product_url": product_url,
                        "image_url": image_url,
                        "platform": "daraz",
                        "rating": rating,
                        "review_count": review_count,
                        "search_term": search_query.lower(),
                        "scraped_at": datetime.now(timezone.utc).isoformat(),
                        "source": "daraz_scraper",
                    }
                    all_products.append(product)
                except Exception as e:
                    print(f"  SCRAPER: Error parsing item: {e}")
                    continue
                    
            print(f"  SCRAPER: Parsed {len(items)} products from page {page_num}")
        except Exception as e:
            print(f"  SCRAPER: Error on page {page_num}: {e}")
            break

    print(f"  SCRAPER: Done. Returning {len(all_products)} products.")
    return all_products

async def async_scrape_daraz(search_query: str, max_pages: int = 1):
    """
    Async wrapper for the fast API scraper.
    """
    loop = asyncio.get_event_loop()
    products = await loop.run_in_executor(
        None, sync_scrape_daraz, search_query, max_pages
    )
    return products

if __name__ == '__main__':
    print(asyncio.run(async_scrape_daraz('iphone')))