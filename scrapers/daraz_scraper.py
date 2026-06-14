"""
==============================================================
  DARAZ NEPAL WEB SCRAPER
  -----------------------
  Scrapes product listings from daraz.com.np using Playwright.
  Saves results to MongoDB Atlas (pricepilot_raw.raw_products).
  
  Author : PricePilot Team
  Date   : 2026-06-03
==============================================================
"""

import os
import re
import time
import random
import logging
import certifi
from datetime import datetime, timezone
from pathlib import Path

from dotenv import load_dotenv
from playwright.sync_api import sync_playwright, TimeoutError as PWTimeoutError
from pymongo import MongoClient
from pymongo.errors import ConnectionFailure, ServerSelectionTimeoutError


# ──────────────────────────────────────────────
#  CONFIGURATION
# ──────────────────────────────────────────────

# Load environment variables from the backend .env file (already has MONGODB_URI)
env_path = Path(__file__).parent.parent / "backend" / ".env"
load_dotenv(env_path)

# MongoDB settings
MONGODB_URI = os.getenv("MONGODB_URI")
DB_NAME = "pricepilot_raw"
COLLECTION_NAME = "raw_products"

# Scraping settings
BASE_URL = "https://www.daraz.com.np"
SEARCH_URL = f"{BASE_URL}/catalog/?page={{page}}"          # All products listing
MAX_PAGES = 5                                               # Scrape at least 5 pages
MIN_DELAY = 2                                               # Min delay between pages (seconds)
MAX_DELAY = 5                                               # Max delay between pages (seconds)
MAX_RETRIES = 3                                             # Retry failed pages up to 3 times

# Realistic browser user-agent
USER_AGENT = (
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
    "AppleWebKit/537.36 (KHTML, like Gecko) "
    "Chrome/125.0.0.0 Safari/537.36"
)

# ──────────────────────────────────────────────
#  LOGGING SETUP
# ──────────────────────────────────────────────

# Create logs directory if it doesn't exist
log_dir = Path(__file__).parent / "logs"
log_dir.mkdir(exist_ok=True)

# Configure file logger for errors
file_handler = logging.FileHandler(log_dir / "scraper_errors.log", encoding="utf-8")
file_handler.setLevel(logging.ERROR)
file_handler.setFormatter(logging.Formatter(
    "%(asctime)s | %(levelname)s | %(message)s"
))

# Configure console logger for progress
console_handler = logging.StreamHandler()
console_handler.setLevel(logging.INFO)
console_handler.setFormatter(logging.Formatter(
    "%(asctime)s | %(message)s", datefmt="%H:%M:%S"
))

logger = logging.getLogger("daraz_scraper")
logger.setLevel(logging.DEBUG)
logger.addHandler(file_handler)
logger.addHandler(console_handler)


# ──────────────────────────────────────────────
#  MONGODB CONNECTION
# ──────────────────────────────────────────────

def connect_to_mongodb():
    """
    Connect to MongoDB Atlas using the URI from .env file.
    Returns the collection object for raw_products.
    """
    if not MONGODB_URI:
        raise ValueError(
            "MONGODB_URI not found in .env file! "
            "Add it like: MONGODB_URI=mongodb+srv://user:pass@cluster.mongodb.net/"
        )

    logger.info("Connecting to MongoDB Atlas...")
    
    client = MongoClient(
        MONGODB_URI,
        tlsCAFile=certifi.where(),           # Fix SSL certificate issues
        serverSelectionTimeoutMS=10000        # 10 second timeout
    )

    # Test the connection
    try:
        client.admin.command("ping")
        logger.info("Connected to MongoDB Atlas successfully!")
    except (ConnectionFailure, ServerSelectionTimeoutError) as e:
        logger.error(f"MongoDB connection failed: {e}")
        raise

    db = client[DB_NAME]
    collection = db[COLLECTION_NAME]
    return client, collection


# ──────────────────────────────────────────────
#  HELPER FUNCTIONS
# ──────────────────────────────────────────────

def clean_price(price_text):
    """
    Remove 'Rs.' prefix, commas, and spaces from price string.
    Returns a float or None.
    
    Examples:
        'Rs. 1,299'  → 1299.0
        'Rs. 25,000' → 25000.0
        ''           → None
    """
    if not price_text:
        return None
    # Remove everything except digits and dots
    cleaned = re.sub(r"[^\d.]", "", price_text)
    try:
        return float(cleaned)
    except ValueError:
        return None


def calculate_discount(original_price, current_price):
    """
    Calculate discount percentage from original and current price.
    Returns an integer percentage or None.
    
    Example:
        original=1000, current=750 → 25
    """
    if original_price and current_price and original_price > current_price:
        discount = ((original_price - current_price) / original_price) * 100
        return round(discount)
    return None


# ──────────────────────────────────────────────
#  COOKIE / POPUP HANDLER
# ──────────────────────────────────────────────

def dismiss_popups(page):
    """
    Automatically handle cookie consent popups and 
    other overlay modals that Daraz may show.
    """
    popup_selectors = [
        # Cookie consent buttons
        "button:has-text('Accept')",
        "button:has-text('OK')",
        "button:has-text('Got it')",
        # Close buttons on modals / popups
        ".baxia-dialog-close",
        ".next-dialog-close",
        "[data-spm='dcoupon'] .next-dialog-close",
        ".coupon-close",                       
        "div.popup-close",
        # Generic close icon (X)
        "[class*='close'][class*='icon']",
        ".lzd-home-pop-close",
    ]
    
    for selector in popup_selectors:
        try:
            element = page.query_selector(selector)
            if element and element.is_visible():
                element.click()
                logger.info(f"  Dismissed popup: {selector}")
                time.sleep(0.5)
        except Exception:
            pass  # Ignore — popup might not exist


# ──────────────────────────────────────────────
#  SCROLL TO LOAD LAZY CONTENT
# ──────────────────────────────────────────────

def scroll_page(page):
    """
    Scroll down the page in steps to trigger lazy-loading
    of product images and cards.
    """
    logger.info("  Scrolling page to load all products...")
    
    total_height = page.evaluate("document.body.scrollHeight")
    current_position = 0
    scroll_step = 500  # pixels per scroll

    while current_position < total_height:
        current_position += scroll_step
        page.evaluate(f"window.scrollTo(0, {current_position})")
        time.sleep(0.3)  # Small pause between scrolls
        # Re-check height (page may grow as content loads)
        total_height = page.evaluate("document.body.scrollHeight")

    # Scroll back to top
    page.evaluate("window.scrollTo(0, 0)")
    time.sleep(0.5)


# ──────────────────────────────────────────────
#  PARSE PRODUCTS FROM PAGE
# ──────────────────────────────────────────────

def parse_products(page):
    """
    Extract product data from the current Daraz listing page.
    """
    products = []
    
    # Daraz uses different class names for different sections (flash sale, just for you, grid)
    card_selectors = [
        "a.jfy-item",                  # "Just For You" items
        "a.card-fs-content-body-unit", # Flash sale items
        "div[data-qa-locator='product-item']", # Old catalog grid
        ".gridItem--Yd0sa",
        "div.box--ujueT",
        "[data-item-id]"
    ]
    
    product_cards = []
    used_selector = None
    for selector in card_selectors:
        product_cards = page.query_selector_all(selector)
        if product_cards and len(product_cards) > 0:
            used_selector = selector
            break
            
    logger.info(f"  Found {len(product_cards)} products using selector: {used_selector}")

    for i, card in enumerate(product_cards):
        try:
            # ── Product Name & URL ──
            product_name = None
            product_url = None
            
            # If the card itself is an <a> tag
            tag_name = card.evaluate("el => el.tagName").lower()
            if tag_name == 'a':
                product_url = card.get_attribute("href")
                # Try to get name from attribute or child title element
                product_name = card.get_attribute("title") or card.get_attribute("name")
                if not product_name:
                    title_el = card.query_selector(".card-jfy-title, .fs-card-title, .title--wFj93")
                    if title_el:
                        product_name = title_el.inner_text().strip()
            else:
                name_el = card.query_selector(".info--ifj7U a, .title--wFj93 a, a[title], a")
                if name_el:
                    product_name = name_el.get_attribute("title") or name_el.inner_text().strip()
                    product_url = name_el.get_attribute("href")
            
            if product_url:
                if product_url.startswith("//"):
                    product_url = "https:" + product_url
                elif not product_url.startswith("http"):
                    product_url = BASE_URL + product_url

            # ── Price ──
            price_el = card.query_selector("span.price, .price--NVB62 span, .currency--GVKjl, [data-price]")
            price_text = price_el.inner_text().strip() if price_el else None
            price = clean_price(price_text)

            # ── Original Price (crossed out) ──
            orig_el = card.query_selector("del, .fs-origin-price .price, .origPrice--AJxKE del, .price--original")
            orig_text = orig_el.inner_text().strip() if orig_el else None
            original_price = clean_price(orig_text)

            # ── Discount Percentage ──
            disc_el = card.query_selector(".hp-mod-discount, .itemDiscount, .discount--HADo4, [class*='discount']")
            discount_percentage = None
            if disc_el:
                disc_text = disc_el.inner_text().strip()
                disc_match = re.search(r"(\d+)", disc_text)
                if disc_match:
                    discount_percentage = int(disc_match.group(1))
            
            # If discount not shown, calculate it
            if discount_percentage is None:
                discount_percentage = calculate_discount(original_price, price)

            # ── Image URL ──
            img_el = card.query_selector("img")
            image_url = None
            if img_el:
                image_url = (
                    img_el.get_attribute("src") or
                    img_el.get_attribute("data-src")
                )

            # ── Rating ──
            rating = None
            rating_el = card.query_selector(".rating--ZI3Ol .star-score")
            if rating_el:
                style = rating_el.get_attribute("style")
                if style:
                    width_match = re.search(r"width:\s*([\d.]+)%", style)
                    if width_match:
                        rating = round(float(width_match.group(1)) / 20, 1)
            
            if rating is None:
                alt_rating = card.query_selector("[class*='rating'] [class*='score']")
                if alt_rating:
                    try:
                        rating = float(alt_rating.inner_text().strip())
                    except ValueError:
                        pass

            # ── Review Count ──
            review_count = None
            review_el = card.query_selector(".rating--ZI3Ol .rating__review, [class*='review']")
            if review_el:
                review_text = review_el.inner_text().strip()
                review_match = re.search(r"(\d+)", review_text)
                if review_match:
                    review_count = int(review_match.group(1))

            # ── Build Product Document ──
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
                "scraped_at": datetime.now(timezone.utc).isoformat(),
                "source": "daraz_scraper",
            }

            # Only add product if it has at least a name or price
            if product_name or price:
                products.append(product)
            
        except Exception as e:
            logger.error(f"Error parsing product #{i+1}: {e}")
            continue  # Never stop for one bad product

    return products


# ──────────────────────────────────────────────
#  SCRAPE A SINGLE PAGE (WITH RETRIES)
# ──────────────────────────────────────────────

def scrape_page(page, page_number):
    """
    Navigate to a specific page number and extract products.
    Retries up to MAX_RETRIES times on failure.
    """
    url = SEARCH_URL.format(page=page_number)
    
    for attempt in range(1, MAX_RETRIES + 1):
        try:
            logger.info(f"Page {page_number} (attempt {attempt}/{MAX_RETRIES}) -> {url}")
            
            # Navigate to the page
            page.goto(url, wait_until="domcontentloaded", timeout=30000)
            time.sleep(2)  # Wait for dynamic content
            
            # Dismiss any popups
            dismiss_popups(page)
            
            # Scroll to trigger lazy loading
            scroll_page(page)
            
            # Wait a bit more for images to load
            time.sleep(1)
            
            # Parse products
            products = parse_products(page)
            
            if not products:
                logger.warning(f"  No products found on page {page_number}")
                # Check if we've reached the end
                no_results = page.query_selector(
                    ".ant-pagination-disabled .ant-pagination-next, "
                    "[class*='noResult'], "
                    ".next-pagination-no-more"
                )
                if no_results:
                    logger.info("  No more pages available - stopping.")
                    return None  # Signal to stop
                
                if attempt < MAX_RETRIES:
                    logger.info(f"  Retrying page {page_number}...")
                    time.sleep(3)
                    continue
            
            logger.info(f"  Scraped {len(products)} products from page {page_number}")
            return products
            
        except PWTimeoutError:
            logger.error(f"Timeout loading page {page_number} (attempt {attempt})")
            if attempt < MAX_RETRIES:
                time.sleep(3)
        except Exception as e:
            logger.error(f"Error on page {page_number} (attempt {attempt}): {e}")
            if attempt < MAX_RETRIES:
                time.sleep(3)
    
    logger.error(f"Failed to scrape page {page_number} after {MAX_RETRIES} attempts. Skipping.")
    return []


# ──────────────────────────────────────────────
#  MAIN SCRAPER FUNCTION
# ──────────────────────────────────────────────

def run_scraper():
    """
    Main function that orchestrates the entire scraping process:
    1. Connect to MongoDB
    2. Launch Playwright browser
    3. Scrape pages one by one
    4. Save products to MongoDB
    5. Print summary
    """
    print("=" * 60)
    print("  DARAZ NEPAL SCRAPER - PricePilot")
    print("=" * 60)
    print()
    
    # ── Step 1: Connect to MongoDB ──
    client, collection = connect_to_mongodb()
    
    all_products = []
    
    # ── Step 2: Launch Browser ──
    with sync_playwright() as pw:
        logger.info("Launching browser (Chromium)...")
        
        browser = pw.chromium.launch(
            headless=True,   # Set to False to watch the browser in action
        )
        
        context = browser.new_context(
            user_agent=USER_AGENT,
            viewport={"width": 1366, "height": 768},
            locale="en-US",
        )
        
        page = context.new_page()
        
        # ── Step 3: Scrape Pages ──
        for page_num in range(1, MAX_PAGES + 1):
            products = scrape_page(page, page_num)
            
            # None means no more pages exist
            if products is None:
                logger.info(f"Reached last page at page {page_num}.")
                break
            
            all_products.extend(products)
            
            # Progress update
            logger.info(
                f"  Total products so far: {len(all_products)}"
            )
            
            # Random delay between pages (2-5 seconds)
            if page_num < MAX_PAGES:
                delay = random.uniform(MIN_DELAY, MAX_DELAY)
                logger.info(f"  Waiting {delay:.1f}s before next page...")
                time.sleep(delay)
        
        browser.close()
        logger.info("Browser closed.")
    
    # ── Step 4: Save to MongoDB ──
    if all_products:
        logger.info(f"Saving {len(all_products)} products to MongoDB...")
        result = collection.insert_many(all_products)
        logger.info(
            f"Inserted {len(result.inserted_ids)} documents "
            f"into {DB_NAME}.{COLLECTION_NAME}"
        )
    else:
        logger.warning("No products scraped. Nothing saved to MongoDB.")
    
    # ── Step 5: Print Summary ──
    print()
    print("=" * 60)
    print("  SCRAPING SUMMARY")
    print("=" * 60)
    print(f"  Total products scraped : {len(all_products)}")
    print(f"  Database               : {DB_NAME}")
    print(f"  Collection             : {COLLECTION_NAME}")
    print(f"  Errors logged to       : logs/scraper_errors.log")
    print("=" * 60)
    
    # Close MongoDB connection
    client.close()
    
    return all_products


# ──────────────────────────────────────────────
#  ENTRY POINT
# ──────────────────────────────────────────────

if __name__ == "__main__":
    run_scraper()
