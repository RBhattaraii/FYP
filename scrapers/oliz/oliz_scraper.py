import json
import requests
import asyncio
import urllib.parse
from bs4 import BeautifulSoup
from datetime import datetime, timezone
from scrapers.utils import calculate_discount, USER_AGENT
from scrapers.daraz.daraz_scraper import _executor

async def async_scrape_oliz(search_query: str):
    """
    Asynchronous scraper for Oliz Store.
    Oliz Store is a Next.js SPA. We can extract the product data directly
    from the embedded __NEXT_DATA__ JSON script tag using requests and BeautifulSoup.
    This is extremely fast and lightweight (no Playwright needed).
    """
    encoded_query = urllib.parse.quote(search_query)
    url = f"https://www.olizstore.com/search?q={encoded_query}"
    
    headers = {
        "User-Agent": USER_AGENT,
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8",
        "Accept-Language": "en-US,en;q=0.5",
    }
    
    products = []
    try:
        # Run the blocking requests call in the thread pool
        loop = asyncio.get_event_loop()
        response = await loop.run_in_executor(
            _executor, 
            lambda: requests.get(url, headers=headers, timeout=15)
        )
        
        if response.status_code != 200:
            print(f"  OLIZ SCRAPER: Failed to fetch. Status code: {response.status_code}")
            return []
            
        soup = BeautifulSoup(response.text, 'html.parser')
        next_data_script = soup.find('script', id='__NEXT_DATA__')
        
        if not next_data_script:
            print("  OLIZ SCRAPER: Could not find __NEXT_DATA__ script.")
            return []
            
        data = json.loads(next_data_script.string)
        
        # Navigate the Next.js JSON structure to find the search results
        # Usually: data -> props -> pageProps -> response (which is a list of products)
        results = data.get('props', {}).get('pageProps', {}).get('response', [])
        
        for item in results:
            product_name = item.get('name')
            slug = item.get('slug')
            if not product_name or not slug:
                continue
                
            product_url = f"https://www.olizstore.com/product/{slug}"
            
            # Prices in the JSON are usually raw numbers
            price = item.get('price')
            if not price:
                price = item.get('min_price')
                
            if price:
                try:
                    price = float(price)
                except ValueError:
                    price = None
                    
            original_price = item.get('compare_at_price')
            if original_price:
                try:
                    original_price = float(original_price)
                    if original_price <= 0 or original_price <= price:
                        original_price = None
                except ValueError:
                    original_price = None
                    
            discount_percentage = calculate_discount(original_price, price)
            
            image_urls = item.get('image_urls', [])
            image_url = image_urls[0] if image_urls else None
            
            product = {
                "product_name": product_name,
                "price": price,
                "original_price": original_price,
                "discount_percentage": discount_percentage,
                "product_url": product_url,
                "image_url": image_url,
                "platform": "oliz_store",
                "rating": None,  # Not readily available in search JSON
                "review_count": None,
                "search_term": search_query.lower(),
                "scraped_at": datetime.now(timezone.utc).isoformat(),
                "source": "oliz_scraper",
            }
            products.append(product)
            
        print(f"  OLIZ SCRAPER: Parsed {len(products)} valid products")
        return products
        
    except Exception as e:
        print(f"  OLIZ SCRAPER: Error scraping: {e}")
        return []