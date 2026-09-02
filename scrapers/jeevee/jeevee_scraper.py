import asyncio
import urllib.parse
from datetime import datetime, timezone
import re
import requests

from scrapers.utils import clean_price, calculate_discount, USER_AGENT

def _fetch_jeevee_page(search_query: str, page: int, headers: dict) -> list:
    """Fetch a single page from Jeevee search API."""
    url = "https://search.jeevee.com/search-test-updated"
    params = {
        "search": search_query,
        "item_per_page": 100,
        "page": page,
        "pagination": "true",
        "query": search_query
    }
    try:
        response = requests.get(url, params=params, headers=headers, timeout=15)
        if response.status_code != 200:
            return []
        data = response.json()
        if 'data' not in data or not isinstance(data['data'], list):
            return []
        return data['data']
    except Exception:
        return []


def _resolve_jeevee_url(slug: str, template_id, product_id) -> str:
    """
    Jeevee's URL routing is inconsistent, but for speed we avoid extra HEAD requests.
    We prefer the template_id URL and fall back to the product_id URL when template_id is missing.
    """
    url_tmpl = f"https://www.jeevee.com/products/{slug}-{template_id}"
    url_pid = f"https://www.jeevee.com/products/{slug}-{product_id}"

    if not template_id or str(template_id) == str(product_id):
        return url_pid

    return url_tmpl


async def async_scrape_jeevee(search_query: str, max_pages: int = 999):
    """
    Asynchronous scraper for Jeevee.
    Uses their internal search API at search.jeevee.com.
    Paginates through ALL pages to get every product.
    """
    encoded_query = urllib.parse.quote(search_query)
    headers = {
        "User-Agent": USER_AGENT,
        "Accept": "application/json, text/plain, */*",
        "Origin": "https://www.jeevee.com",
        "Referer": f"https://www.jeevee.com/products/search?query={encoded_query}"
    }

    products = []
    try:
        loop = asyncio.get_event_loop()
        page = 1
        while page <= max_pages:
            items = await loop.run_in_executor(
                None,
                lambda p=page: _fetch_jeevee_page(search_query, p, headers)
            )
            if not items:
                break  # No more results

            for item in items:
                try:
                    product_name = item.get('label')
                    product_id = item.get('product_id')

                    if not product_name or not product_id:
                        continue

                    template_id = item.get('product_template_id', product_id)

                    # Build slug from product name
                    slug_from_name = re.sub(r'[^a-z0-9]+', '-', product_name.lower()).strip('-')

                    # Resolve the correct URL (tries template_id first, then product_id)
                    product_url = _resolve_jeevee_url(slug_from_name, template_id, product_id)

                    selling_price = item.get('price')
                    discount_percentage = item.get('discount', 0)
                    original_price = None

                    if discount_percentage and discount_percentage > 0 and selling_price:
                        original_price = round(selling_price / (1 - discount_percentage / 100), 2)
                    else:
                        discount_percentage = None

                    image_url = None
                    images = item.get('image', [])
                    if images and isinstance(images, list) and len(images) > 0:
                        first_img = images[0]
                        if isinstance(first_img, dict):
                            image_url = first_img.get('512') or first_img.get('256') or first_img.get('1024')

                    product = {
                        "product_name": product_name,
                        "price": selling_price,
                        "original_price": original_price,
                        "discount_percentage": discount_percentage,
                        "product_url": product_url,
                        "image_url": image_url,
                        "platform": "jeevee",
                        "rating": None,
                        "review_count": None,
                        "search_term": search_query.lower(),
                        "scraped_at": datetime.now(timezone.utc).isoformat(),
                        "source": "jeevee_scraper",
                    }
                    products.append(product)
                except Exception as e:
                    print(f"  JEEVEE SCRAPER: Error parsing product: {e}")

            # If less than 100 results returned, this is the last page
            if len(items) < 100:
                break
            page += 1

        print(f"  JEEVEE SCRAPER: Parsed {len(products)} valid products")
        return products

    except Exception as e:
        print(f"  JEEVEE SCRAPER: Error scraping: {e}")
        return []
