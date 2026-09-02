import json
import requests
import asyncio
import urllib.parse
from datetime import datetime, timezone
from scrapers.utils import calculate_discount, USER_AGENT


def _fetch_hukut_offset(offset: int, headers: dict, search_query: str = "") -> tuple:
    """Fetch products at a given offset with empty search (returns ALL products) or specific search."""
    url = "https://hukut.com/api-server/v1/product/list-elastic"
    payload = {
        "searchText": search_query,
        "pagination": {"limit": 100, "offset": offset}
    }
    try:
        response = requests.post(url, headers=headers, json=payload, timeout=15)
        if response.status_code != 200:
            return [], 0
        data = response.json()
        rows = data.get('data', {}).get('rows', [])
        total = data.get('data', {}).get('count', 0)
        return rows, total
    except Exception:
        return [], 0


async def async_scrape_hukut(search_query: str = "", max_pages: int = 999):
    """
    Asynchronous scraper for Hukut Store.
    When called with empty/default query, fetches ALL products from the store.
    Otherwise, searches for specific query.
    Total store catalog: ~3,187 products (as of July 2026).
    """
    headers = {
        "User-Agent": USER_AGENT,
        "Content-Type": "application/json",
        "Origin": "https://hukut.com",
        "Referer": "https://hukut.com/"
    }

    products = []
    seen_slugs = set()

    try:
        loop = asyncio.get_event_loop()

        # First request to get total count
        first_rows, total = await loop.run_in_executor(
            None,
            lambda: _fetch_hukut_offset(0, headers, search_query)
        )

        if not first_rows:
            return []

        if total == 0:
            total = 9999  # fallback — keep paginating until empty

        def parse_rows(rows, query):
            parsed = []
            for item in rows:
                product_name = item.get('name')
                slug = item.get('slug')
                if not product_name or not slug or slug in seen_slugs:
                    continue
                seen_slugs.add(slug)
                product_url = f"https://hukut.com/product/{slug}"

                variant = item.get('defaultVariant', {})
                base_price = variant.get('price')
                sale_price = variant.get('salePrice')

                if sale_price and base_price and sale_price < base_price:
                    price = float(sale_price)
                    original_price = float(base_price)
                else:
                    price = float(base_price) if base_price else None
                    original_price = None

                if not price and item.get('sortablePrice'):
                    price = float(item.get('sortablePrice'))

                discount_percentage = calculate_discount(original_price, price)
                image_obj = item.get('image', {})
                image_url = image_obj.get('cdn') or image_obj.get('url')

                parsed.append({
                    "product_name": product_name,
                    "price": price,
                    "original_price": original_price,
                    "discount_percentage": discount_percentage,
                    "product_url": product_url,
                    "image_url": image_url,
                    "platform": "hukut_store",
                    "rating": None,
                    "review_count": None,
                    "search_term": query.lower(),
                    "scraped_at": datetime.now(timezone.utc).isoformat(),
                    "source": "hukut_scraper",
                })
            return parsed

        # Parse first batch
        products.extend(parse_rows(first_rows, search_query))

        # Paginate through remaining
        offset = 100
        pages_fetched = 1
        while offset < total and pages_fetched < max_pages:
            current_offset = offset
            rows, _ = await loop.run_in_executor(
                None,
                lambda: _fetch_hukut_offset(current_offset, headers, search_query)
            )
            if not rows:
                break
            products.extend(parse_rows(rows, search_query))
            if len(rows) < 100:
                break
            offset += 100
            pages_fetched += 1

        print(f"  HUKUT SCRAPER: Parsed {len(products)} valid products (total catalog: {total})")
        return products

    except Exception as e:
        print(f"  HUKUT SCRAPER: Error scraping: {e}")
        return []