import json
import requests
import asyncio
import urllib.parse
from bs4 import BeautifulSoup
from datetime import datetime, timezone
from scrapers.utils import calculate_discount, USER_AGENT
# Uses default asyncio thread pool executor (None) - no Playwright needed for Oliz

async def async_scrape_oliz(search_query: str, max_pages: int = 1):
    """
    Asynchronous scraper for Oliz Store.
    Oliz Store is a Next.js SPA. We can extract product data from the
    embedded __NEXT_DATA__ JSON script tag using requests and BeautifulSoup.
    """
    encoded_query = urllib.parse.quote(search_query)
    base_urls = [
        f"https://www.olizstore.com/search?q={encoded_query}",
        f"https://www.olizstore.com/products?search={encoded_query}",
        f"https://www.olizstore.com/shop?query={encoded_query}"
    ]

    headers = {
        "User-Agent": USER_AGENT,
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8",
        "Accept-Language": "en-US,en;q=0.5",
        "Referer": "https://www.google.com/",
        "Connection": "keep-alive",
    }

    products = []
    seen_urls = set()
    try:
        loop = asyncio.get_event_loop()
        session = requests.Session()
        session.headers.update(headers)

        for base_url in base_urls:
            for page in range(1, max_pages + 1):
                url = f"{base_url}&page={page}"
                response = await loop.run_in_executor(
                    None,
                    lambda u=url: session.get(u, timeout=15)
                )

                if response.status_code != 200:
                    continue

                soup = BeautifulSoup(response.text, 'html.parser')
                next_data_script = soup.find('script', id='__NEXT_DATA__')
                if not next_data_script:
                    continue

                data = json.loads(next_data_script.string)
                results = data.get('props', {}).get('pageProps', {}).get('response', [])
                if not results:
                    continue

                for item in results:
                    product_name = item.get('name')
                    slug = item.get('slug')
                    if not product_name or not slug:
                        continue

                    product_url = f"https://www.olizstore.com/product/{slug}"
                    if product_url in seen_urls:
                        continue
                    seen_urls.add(product_url)

                    price = item.get('price') or item.get('min_price')
                    if price:
                        try:
                            price = float(price)
                        except ValueError:
                            price = None

                    original_price = item.get('compare_at_price')
                    if original_price:
                        try:
                            original_price = float(original_price)
                            if original_price <= 0 or (price is not None and original_price <= price):
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
                        "rating": None,
                        "review_count": None,
                        "search_term": search_query.lower(),
                        "scraped_at": datetime.now(timezone.utc).isoformat(),
                        "source": "oliz_scraper",
                    }
                    products.append(product)

                if not results:
                    break

        print(f"  OLIZ SCRAPER: Parsed {len(products)} valid products")
        return products

    except Exception as e:
        print(f"  OLIZ SCRAPER: Error scraping: {e}")
        return []