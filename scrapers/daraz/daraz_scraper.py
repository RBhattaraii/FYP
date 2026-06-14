import time
import asyncio
import re
import urllib.parse
from datetime import datetime, timezone
from concurrent.futures import ThreadPoolExecutor
from playwright.sync_api import sync_playwright, TimeoutError as PWTimeoutError
from scrapers.utils import clean_price, calculate_discount, BASE_URL, USER_AGENT

_executor = ThreadPoolExecutor(max_workers=2)
def _parse_products_from_page(page, search_term):
    """
    Parse product data from a Daraz search results page.
    Uses multiple selector strategies to handle different page layouts.
    """
    products = []

    # Strategy 1: Search results page uses div[data-aplus-ae] containers
    # Strategy 2: Homepage/catalog uses a.jfy-item links
    # Strategy 3: Fallback selectors for older layouts
    card_selectors = [
        "div[data-qa-locator='product-item']", # Search results grid items
        "a.jfy-item",                       # "Just For You" items
        "a.card-fs-content-body-unit",      # Flash sale items
        ".gridItem--Yd0sa",
        "div.box--ujueT",
    ]

    product_cards = []
    used_selector = None
    for selector in card_selectors:
        product_cards = page.query_selector_all(selector)
        if product_cards and len(product_cards) > 0:
            used_selector = selector
            break

    print(f"  SCRAPER: Found {len(product_cards)} cards using '{used_selector}'")

    for i, card in enumerate(product_cards):
        try:
            product_name = None
            product_url = None

            # ── Get product name and URL ──
            # Check if the card itself is an <a> tag
            tag_name = card.evaluate("el => el.tagName").lower()

            if tag_name == "a":
                product_url = card.get_attribute("href")
                product_name = (
                    card.get_attribute("title")
                    or card.get_attribute("name")
                )
                if not product_name:
                    title_el = card.query_selector(
                        ".card-jfy-title, .fs-card-title, .title--wFj93"
                    )
                    if title_el:
                        product_name = title_el.inner_text().strip()
            else:
                # For div-based cards, prioritize the link with the title
                link_el = card.query_selector("a[title]")
                if not link_el:
                    link_el = card.query_selector(".RfADt a, .title--wFj93 a, a[href*='/products/']")
                if link_el:
                    product_name = (
                        link_el.get_attribute("title")
                        or link_el.inner_text().strip()
                    )
                    product_url = link_el.get_attribute("href")

            # Fix URL format
            if product_url:
                if product_url.startswith("//"):
                    product_url = "https:" + product_url
                elif not product_url.startswith("http"):
                    product_url = BASE_URL + product_url

            # ── Price ──
            price_el = card.query_selector(
                "span.ooOxS, span.price, .price--NVB62 span, "
                ".currency--GVKjl, [data-price]"
            )
            price_text = price_el.inner_text().strip() if price_el else None
            price = clean_price(price_text)

            # ── Original Price (crossed out) ──
            orig_el = card.query_selector(
                "del, .fs-origin-price .price, "
                ".origPrice--AJxKE del, .price--original"
                ".origPrice--AJxKE del, .price--original, .price-orig--jK02r"
            )
            orig_text = orig_el.inner_text().strip() if orig_el else None
            original_price = clean_price(orig_text)

            # ── Discount Percentage ──
            disc_el = card.query_selector(
                "span.IcOsH, .hp-mod-discount, .itemDiscount, "
                ".discount--HADo4, [class*='discount']"
            )
            discount_percentage = None
            if disc_el:
                disc_text = disc_el.inner_text().strip()
                disc_match = re.search(r"(\d+)", disc_text)
                if disc_match:
                    discount_percentage = int(disc_match.group(1))

            if discount_percentage is None:
                discount_percentage = calculate_discount(original_price, price)

            # ── Image URL ──
            img_el = card.query_selector("img")
            image_url = None
            if img_el:
                image_url = (
                    img_el.get_attribute("src")
                    or img_el.get_attribute("data-src")
                )

            # ── Rating ──
            rating = None
            rating_el = card.query_selector(
                ".rating--ZI3Ol .star-score, "
                "[class*='rating'] [class*='score']"
            )
            if rating_el:
                style = rating_el.get_attribute("style")
                if style:
                    width_match = re.search(r"width:\s*([\d.]+)%", style)
                    if width_match:
                        rating = round(float(width_match.group(1)) / 20, 1)
                if rating is None:
                    try:
                        rating = float(rating_el.inner_text().strip())
                    except (ValueError, TypeError):
                        pass

            # ── Review Count ──
            review_count = None
            review_el = card.query_selector(
                "span.qzqFw, .rating--ZI3Ol .rating__review, [class*='review']"
            )
            if review_el:
                review_text = review_el.inner_text().strip()
                review_match = re.search(r"(\d+)", review_text)
                if review_match:
                    review_count = int(review_match.group(1))

            # ── Build product document ──
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
                "search_term": search_term,
                "scraped_at": datetime.now(timezone.utc).isoformat(),
                "source": "daraz_scraper",
            }

            if product_name or price:
                products.append(product)

        except Exception as e:
            print(f"  SCRAPER: Error parsing card #{i+1}: {e}")
            continue

    print(f"  SCRAPER: Parsed {len(products)} valid products")
    return products


def sync_scrape_daraz(search_query: str, max_pages: int = 1):
    """
    Synchronous scraper function — runs Playwright in the current thread.
    Called by async_scrape_daraz via ThreadPoolExecutor.
    """
    encoded_query = urllib.parse.quote(search_query)
    all_products = []

    with sync_playwright() as pw:
        browser = pw.chromium.launch(headless=True)
        context = browser.new_context(
            user_agent=USER_AGENT,
            viewport={"width": 1366, "height": 768},
            locale="en-US",
        )
        page = context.new_page()

        for page_num in range(1, max_pages + 1):
            url = f"{BASE_URL}/catalog/?q={encoded_query}&page={page_num}"
            print(f"  SCRAPER: Loading {url}")

            try:
                page.goto(url, wait_until="domcontentloaded", timeout=30000)
                time.sleep(3)  # Wait for JS rendering

                # Scroll to trigger lazy loading
                total_height = page.evaluate("document.body.scrollHeight")
                current_position = 0
                while current_position < total_height:
                    current_position += 500
                    page.evaluate(f"window.scrollTo(0, {current_position})")
                    time.sleep(0.3)
                    total_height = page.evaluate("document.body.scrollHeight")

                time.sleep(1)

                products = _parse_products_from_page(page, search_query.lower())

                if not products:
                    print(f"  SCRAPER: No products found on page {page_num}, stopping.")
                    break

                all_products.extend(products)
                print(f"  SCRAPER: Total so far: {len(all_products)}")

            except PWTimeoutError:
                print(f"  SCRAPER: Timeout on page {page_num}")
            except Exception as e:
                print(f"  SCRAPER: Error on page {page_num}: {e}")

        browser.close()

    print(f"  SCRAPER: Done. Returning {len(all_products)} products.")
    return all_products


async def async_scrape_daraz(search_query: str, max_pages: int = 1):
    """
    Async wrapper that runs the sync scraper in a thread pool.
    This is the function FastAPI endpoints should call.
    """
    loop = asyncio.get_event_loop()
    products = await loop.run_in_executor(
        _executor, sync_scrape_daraz, search_query, max_pages
    )
    return products