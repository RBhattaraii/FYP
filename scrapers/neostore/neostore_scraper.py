import asyncio
import urllib.parse
from datetime import datetime, timezone
import requests
from bs4 import BeautifulSoup

from scrapers.utils import clean_price, calculate_discount, USER_AGENT
from scrapers.daraz.daraz_scraper import _executor

async def async_scrape_neostore(search_query: str):
    """
    Asynchronous scraper for NeoStore.
    NeoStore is a standard server-rendered HTML website. We use requests and BeautifulSoup.
    """
    encoded_query = urllib.parse.quote(search_query)
    url = f"https://www.neostore.com.np/?s={encoded_query}"
    
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
            print(f"  NEOSTORE SCRAPER: Failed to fetch. Status code: {response.status_code}")
            return []
            
        soup = BeautifulSoup(response.text, 'html.parser')
        
        # Product items have a 'product-item-box' wrapper, usually inside a 'product-item' container
        cards = soup.find_all(class_=lambda c: c and 'product-item' in c)
        
        # Avoid duplicate parsing if 'product-item' and 'product-item-box' are nested
        # Let's just iterate over product-item-box
        boxes = soup.find_all(class_='product-item-box')
        if not boxes:
            boxes = cards

        for box in boxes:
            try:
                # ── Product Name and URL ──
                link_el = box.find('a', class_='product-thumbnail')
                if not link_el:
                    # Fallback find any link with /product/
                    link_el = box.find('a', href=lambda h: h and '/product/' in h)
                
                if not link_el:
                    continue
                    
                product_url = link_el.get('href')
                
                # The name is often in a specific element inside description
                desc = box.find(class_='product-description')
                product_name = None
                if desc:
                    # Usually h5 or a inside the description
                    name_a = desc.find('a')
                    if name_a and name_a.text.strip():
                        product_name = name_a.text.strip()
                        
                if not product_name:
                    # Fallback to grabbing text from link or image alt
                    img = link_el.find('img')
                    if img and img.get('alt'):
                        product_name = img.get('alt').strip()
                        
                if not product_name:
                    continue

                # ── Price ──
                price_el = box.find(class_=lambda c: c and 'price' in str(c).lower())
                price_text = price_el.text.strip() if price_el else None
                
                # Check for original price (usually inside a <del> or <strike>)
                orig_el = box.find(['del', 'strike'])
                orig_text = orig_el.text.strip() if orig_el else None
                
                price = clean_price(price_text)
                original_price = clean_price(orig_text)
                
                # If both are same or original is less, ignore original
                if original_price and price and original_price <= price:
                    original_price = None

                discount_percentage = calculate_discount(original_price, price)

                # ── Image URL ──
                img_el = link_el.find('img') or box.find('img')
                image_url = None
                if img_el:
                    image_url = img_el.get('src') or img_el.get('data-src')

                # ── Rating ──
                # Let's look for star icons for rating if possible
                rating = None
                stars = box.find_all('i', class_=lambda c: c and 'fa-star' in c and 'color: #fed700' in box.get('style', ''))
                # Or just check simple star count
                stars = box.find_all('i', class_=lambda c: c and 'fa-star' in c and 'far' not in c and 'fas' in c)
                # It's hard to get exact rating from icons without a specific structure, so leave as None if complex

                product = {
                    "product_name": product_name,
                    "price": price,
                    "original_price": original_price,
                    "discount_percentage": discount_percentage,
                    "product_url": product_url,
                    "image_url": image_url,
                    "platform": "neostore",
                    "rating": rating,
                    "review_count": None,
                    "search_term": search_query.lower(),
                    "scraped_at": datetime.now(timezone.utc).isoformat(),
                    "source": "neostore_scraper",
                }
                
                products.append(product)
            except Exception as e:
                print(f"  NEOSTORE SCRAPER: Error parsing product: {e}")
                
        print(f"  NEOSTORE SCRAPER: Parsed {len(products)} valid products")
        return products
        
    except Exception as e:
        print(f"  NEOSTORE SCRAPER: Error scraping: {e}")
        return []
