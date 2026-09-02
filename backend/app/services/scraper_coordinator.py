"""
Scraper Coordinator Service
Coordinates homepage scraping across all platforms and logs results to MongoDB
"""
import asyncio
import sys
import os
from datetime import datetime, timezone
from typing import List, Dict, Any

# Add the root FYP directory to sys.path so we can import the scrapers module
root_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), "../../../"))
if root_dir not in sys.path:
    sys.path.append(root_dir)

# Import individual scraper functions
from scrapers.daraz.daraz_scraper import async_scrape_daraz
from scrapers.oliz.oliz_scraper import async_scrape_oliz
from scrapers.hukut.hukut_scraper import async_scrape_hukut
from scrapers.neostore.neostore_scraper import async_scrape_neostore
from scrapers.cgdigital.cgdigital_scraper import async_scrape_cgdigital
from scrapers.better.better_scraper import async_scrape_better
from scrapers.hardwarepasal.hardwarepasal_scraper import async_scrape_hardwarepasal
from scrapers.ufonepal.ufonepal_scraper import async_scrape_ufonepal
from scrapers.jeevee.jeevee_scraper import async_scrape_jeevee

# Removed MongoDB connection

# Import PostgreSQL connection
import asyncpg


# Platform configurations
# Each platform has a scraper function and homepage search term
# For homepage scraping, we use generic popular terms to get featured/trending products
# This simulates scraping the homepage by getting broadly popular product categories
PLATFORM_CONFIGS = [
    {
        "name": "Daraz",
        "scraper": async_scrape_daraz,
        "homepage_query": "electronics",  # Popular category to get featured products
        "tier": 1,  # Tier 1 = Priority platforms (fast)
    },
    {
        "name": "Sastodeal",
        "scraper": None,  # TODO: Add when scraper available
        "homepage_query": "electronics",
        "tier": 1,  # Tier 1
    },
    {
        "name": "Oliz",
        "scraper": async_scrape_oliz,
        "homepage_query": "laptop",  # Tech-focused store
        "tier": 1,  # Tier 1
    },
    {
        "name": "Better",
        "scraper": async_scrape_better,
        "homepage_query": "electronics",
        "tier": 2,  # Tier 2 = Background platforms
    },
    {
        "name": "CGDigital",
        "scraper": async_scrape_cgdigital,
        "homepage_query": "laptop",  # Hardware/tech store
        "tier": 2,
    },
    {
        "name": "HardwarePasal",
        "scraper": async_scrape_hardwarepasal,
        "homepage_query": "computer",  # Hardware-focused store
        "tier": 2,
    },
    {
        "name": "Hukut",
        "scraper": async_scrape_hukut,
        "homepage_query": "phone",
        "tier": 2,
    },
    {
        "name": "Jeevee",
        "scraper": async_scrape_jeevee,
        "homepage_query": "electronics",
        "tier": 2,
    },
    {
        "name": "NeoStore",
        "scraper": async_scrape_neostore,
        "homepage_query": "electronics",
        "tier": 2,
    },
    {
        "name": "UfoNepal",
        "scraper": async_scrape_ufonepal,
        "homepage_query": "electronics",
        "tier": 2,
    },
    {
        "name": "Hamrobazar",
        "scraper": None,  # TODO: Add when scraper available
        "homepage_query": "electronics",
        "tier": 2,
    },
]

# Tier definitions
TIER1_PLATFORMS = [p for p in PLATFORM_CONFIGS if p.get('tier') == 1 and p['scraper'] is not None]
TIER2_PLATFORMS = [p for p in PLATFORM_CONFIGS if p.get('tier') == 2 and p['scraper'] is not None]


async def scrape_single_platform(
    platform_name: str,
    scraper_func: callable,
    query: str,
    max_pages: int = 1
) -> Dict[str, Any]:
    """
    Scrape a single platform and handle failures gracefully.
    
    Args:
        platform_name: Name of the platform (e.g., "Daraz")
        scraper_func: Async scraper function to call
        query: Search query (empty for homepage)
        max_pages: Number of pages to scrape (default: 1 for homepage)
    
    Returns:
        Dict containing:
            - platform: Platform name
            - status: "success" or "failed"
            - products: List of scraped products (empty if failed)
            - products_count: Number of products scraped
            - error_message: Error message if failed (None if success)
            - duration_ms: Time taken to scrape in milliseconds
    """
    start_time = datetime.now(timezone.utc)
    
    try:
        print(f"[COORDINATOR] Scraping {platform_name}...")
        
        # Check if scraper function accepts max_pages parameter
        import inspect
        sig = inspect.signature(scraper_func)
        params = sig.parameters
        
        # Call the scraper function with appropriate arguments and a 15-second timeout guard
        if 'max_pages' in params:
            products = await asyncio.wait_for(scraper_func(query, max_pages), timeout=15.0)
        else:
            # Scraper only accepts query parameter
            products = await asyncio.wait_for(scraper_func(query), timeout=15.0)
            
        # Normalize product keys to match Pydantic Product model
        # Scrapers use varied key names (product_name vs title, source vs store_name, etc.)
        normalized_products = []
        for p in products:
            title = p.get("product_name") or p.get("title") or p.get("name")
            raw_price = p.get("price")
            
            # Skip products missing essential data
            if not title or raw_price is None:
                continue
            
            try:
                price = float(raw_price)
            except (ValueError, TypeError):
                continue
            
            # Determine store name from various scraper fields
            store_name = platform_name  # default fallback
            if p.get("store_name"):
                store_name = p["store_name"]
            elif p.get("source"):
                store_name = p["source"].replace("_scraper", "").replace("_", " ").title()
            elif p.get("platform"):
                store_name = p["platform"].replace("_", " ").title()
            
            # Parse original_price safely
            orig_price = None
            if p.get("original_price") is not None:
                try:
                    orig_price = float(p["original_price"])
                except (ValueError, TypeError):
                    pass
            
            # Parse discount safely
            disc = p.get("discount_percentage") or p.get("discount_percent")
            discount_percent = None
            if disc is not None:
                try:
                    discount_percent = int(disc)
                except (ValueError, TypeError):
                    pass
            
            # Normalize product_url to absolute URL
            raw_url = p.get("product_url") or ""
            if raw_url:
                if raw_url.startswith("http://") or raw_url.startswith("https://"):
                    product_url = raw_url
                elif raw_url.startswith("//"):
                    product_url = "https:" + raw_url
                elif raw_url.startswith("/"):
                    # Resolve relative URL using platform-specific base URL
                    base_urls = {
                        "Daraz": "https://www.daraz.com.np",
                        "Oliz": "https://www.olizstore.com",
                        "Jeevee": "https://www.jeevee.com",
                        "Hukut": "https://hukut.com",
                        "CGDigital": "https://cgdigital.com.np",
                        "Better": "https://www.thebetterappliances.com",
                        "HardwarePasal": "https://hardwarepasal.com",
                        "NeoStore": "https://www.neostore.com.np",
                        "UfoNepal": "https://www.ufonepal.com",
                        "Sastodeal": "https://www.sastodeal.com",
                    }
                    base = base_urls.get(platform_name, "")
                    product_url = f"{base}{raw_url}" if base else raw_url
                else:
                    product_url = raw_url
            else:
                product_url = ""
            
            normalized_products.append({
                "title": title,
                "price": price,
                "original_price": orig_price,
                "discount_percent": discount_percent,
                "image_url": p.get("image_url") or "",
                "store_name": store_name,
                "product_url": product_url,
                "category": p.get("category"),
            })
        products = normalized_products
        
        end_time = datetime.now(timezone.utc)
        duration_ms = int((end_time - start_time).total_seconds() * 1000)
        
        print(f"[COORDINATOR] {platform_name}: OK {len(products)} products in {duration_ms}ms")
        
        return {
            "platform": platform_name,
            "status": "success",
            "products": products,
            "products_count": len(products),
            "error_message": None,
            "duration_ms": duration_ms,
            "scraped_at": end_time.isoformat(),
        }
        
    except Exception as e:
        end_time = datetime.now(timezone.utc)
        duration_ms = int((end_time - start_time).total_seconds() * 1000)
        
        error_message = str(e)
        print(f"[COORDINATOR] {platform_name}: FAIL - {error_message}")
        
        return {
            "platform": platform_name,
            "status": "failed",
            "products": [],
            "products_count": 0,
            "error_message": error_message,
            "duration_ms": duration_ms,
            "scraped_at": end_time.isoformat(),
        }





async def scrape_homepage_daily() -> Dict[str, Any]:
    """
    Scrape homepage/featured products from all platforms concurrently.
    
    This function:
    1. Scrapes all 9 available platforms concurrently using asyncio.gather
    2. Extracts featured products from homepage (20-50 per platform)
    3. Handles individual scraper failures gracefully (return_exceptions=True)
    4. Logs results to MongoDB scraping_logs collection
    5. Returns all products for curation algorithm (task 3.2)
    
    Returns:
        Dict containing:
            - status: "completed" or "partial" (if some scrapers failed)
            - total_products: Total number of products scraped
            - platforms_scraped: Number of platforms successfully scraped
            - platforms_failed: Number of platforms that failed
            - results: List of platform scraping results
            - all_products: Combined list of all scraped products
    """
    print("[COORDINATOR] Starting daily homepage scraping...")
    start_time = datetime.now(timezone.utc)
    
    # Create scraping tasks for all platforms
    scraping_tasks = [
        scrape_single_platform(
            platform_name=config["name"],
            scraper_func=config["scraper"],
            query=config["homepage_query"],
            max_pages=1  # Only scrape first page for homepage
        )
        for config in PLATFORM_CONFIGS
    ]
    
    # Scrape all platforms concurrently
    # return_exceptions=True ensures one failure doesn't break everything
    print(f"[COORDINATOR] Scraping {len(scraping_tasks)} platforms concurrently...")
    results = await asyncio.gather(*scraping_tasks, return_exceptions=True)
    
    # Process results
    all_products = []
    platforms_scraped = 0
    platforms_failed = 0
    processed_results = []
    
    for result in results:
        # Handle exceptions from asyncio.gather
        if isinstance(result, Exception):
            platforms_failed += 1
            error_result = {
                "platform": "Unknown",
                "status": "failed",
                "products": [],
                "products_count": 0,
                "error_message": str(result),
                "duration_ms": 0,
            }
            processed_results.append(error_result)
            print(f"[COORDINATOR] Exception in scraping: {result}")
            continue
        
        # Add to results
        processed_results.append(result)
        
        # Track success/failure
        if result["status"] == "success":
            platforms_scraped += 1
            
            # Normalize product data format before adding to all_products
            for product in result["products"]:
                # Rename fields to match database schema
                if 'product_name' in product and 'title' not in product:
                    product['title'] = product['product_name']
                if 'platform' in product and 'store_name' not in product:
                    product['store_name'] = product['platform']
                    
            all_products.extend(result["products"])
        else:
            platforms_failed += 1
        
        # MongoDB logging removed
    
    end_time = datetime.now(timezone.utc)
    total_duration_ms = int((end_time - start_time).total_seconds() * 1000)
    
    # Determine overall status
    overall_status = "completed" if platforms_failed == 0 else "partial"
    
    summary = {
        "status": overall_status,
        "total_products": len(all_products),
        "platforms_scraped": platforms_scraped,
        "platforms_failed": platforms_failed,
        "total_platforms": len(PLATFORM_CONFIGS),
        "total_duration_ms": total_duration_ms,
        "results": processed_results,
        "all_products": all_products,
        "scraped_at": end_time.isoformat(),
    }
    
    print(f"[COORDINATOR] Scraping complete: {platforms_scraped}/{len(PLATFORM_CONFIGS)} platforms succeeded")
    print(f"[COORDINATOR] Total products scraped: {len(all_products)}")
    print(f"[COORDINATOR] Total time: {total_duration_ms}ms")
    
    return summary


async def save_curated_products_to_postgres(
    db: asyncpg.Connection,
    curated_products: Dict[str, List[Dict[str, Any]]]
) -> int:
    """
    Save curated products to PostgreSQL home_screen_products table.
    
    This function:
    1. Deletes old products from home_screen_products table
    2. Inserts new curated products (25 best_deals + 25 top_price_drops)
    3. Updates scrape_metadata table with scraping status
    4. Uses a transaction to ensure all operations succeed or fail together
    
    Args:
        db: PostgreSQL database connection
        curated_products: Dict with 'best_deals' and 'top_price_drops' arrays
    
    Returns:
        Total number of products inserted
    """
    best_deals = curated_products.get('best_deals', [])
    top_price_drops = curated_products.get('top_price_drops', [])
    tech_gadgets = curated_products.get('tech_gadgets', [])
    audio_essentials = curated_products.get('audio_essentials', [])
    home_appliances = curated_products.get('home_appliances', [])
    
    total_products = len(best_deals) + len(top_price_drops) + len(tech_gadgets) + len(audio_essentials) + len(home_appliances)
    
    print(f"[POSTGRES] Saving {total_products} curated products...")
    
    async with db.transaction():
        # Step 1: Delete old products
        await db.execute("DELETE FROM home_screen_products")
        print("[POSTGRES] Old products deleted")
        
        # Step 1.5: Ensure all curated products exist in the global products table
        global_products = []
        for items in [best_deals, top_price_drops, tech_gadgets, audio_essentials, home_appliances]:
            for product in items:
                global_products.append((
                    product.get('title', 'Unknown'),
                    float(product.get('price', 0)),
                    float(product.get('original_price', 0)) if product.get('original_price') else None,
                    int(product.get('discount_percent', 0)) if product.get('discount_percent') else None,
                    product.get('image_url', ''),
                    product.get('store_name', 'Unknown'),
                    product.get('product_url', ''),
                    product.get('category')
                ))

        if global_products:
            await db.executemany("""
                INSERT INTO products 
                (title, price, original_price, discount_percent, image_url, store_name, product_url, category)
                VALUES ($1, $2, $3, $4, $5, $6, $7, $8)
                ON CONFLICT (product_url) DO UPDATE 
                SET price = EXCLUDED.price, 
                    original_price = EXCLUDED.original_price, 
                    discount_percent = EXCLUDED.discount_percent,
                    image_url = EXCLUDED.image_url,
                    title = EXCLUDED.title
            """, global_products)
            print(f"[POSTGRES] Synced {len(global_products)} curated products to global products table")

        # Step 2: Prepare data for bulk insert
        products_to_insert = []
        
        # Add best deals
        for product in best_deals:
            products_to_insert.append((
                'best_deals',
                product.get('title', 'Unknown'),
                float(product.get('price', 0)),
                float(product.get('original_price', 0)) if product.get('original_price') else None,
                int(product.get('discount_percent', 0)) if product.get('discount_percent') else None,
                product.get('image_url', ''),
                product.get('store_name', 'Unknown'),
                product.get('product_url', ''),
                product.get('category')
            ))
        
        # Add top price drops
        for product in top_price_drops:
            products_to_insert.append((
                'top_price_drops',
                product.get('title', 'Unknown'),
                float(product.get('price', 0)),
                float(product.get('original_price', 0)) if product.get('original_price') else None,
                int(product.get('discount_percent', 0)) if product.get('discount_percent') else None,
                product.get('image_url', ''),
                product.get('store_name', 'Unknown'),
                product.get('product_url', ''),
                product.get('category')
            ))
            
        # Add tech gadgets
        for product in tech_gadgets:
            products_to_insert.append((
                'tech_gadgets',
                product.get('title', 'Unknown'),
                float(product.get('price', 0)),
                float(product.get('original_price', 0)) if product.get('original_price') else None,
                int(product.get('discount_percent', 0)) if product.get('discount_percent') else None,
                product.get('image_url', ''),
                product.get('store_name', 'Unknown'),
                product.get('product_url', ''),
                product.get('category')
            ))
            
        # Add audio essentials
        for product in audio_essentials:
            products_to_insert.append((
                'audio_essentials',
                product.get('title', 'Unknown'),
                float(product.get('price', 0)),
                float(product.get('original_price', 0)) if product.get('original_price') else None,
                int(product.get('discount_percent', 0)) if product.get('discount_percent') else None,
                product.get('image_url', ''),
                product.get('store_name', 'Unknown'),
                product.get('product_url', ''),
                product.get('category')
            ))
            
        # Add home appliances
        for product in home_appliances:
            products_to_insert.append((
                'home_appliances',
                product.get('title', 'Unknown'),
                float(product.get('price', 0)),
                float(product.get('original_price', 0)) if product.get('original_price') else None,
                int(product.get('discount_percent', 0)) if product.get('discount_percent') else None,
                product.get('image_url', ''),
                product.get('store_name', 'Unknown'),
                product.get('product_url', ''),
                product.get('category')
            ))
        
        # Step 3: Bulk insert products
        if products_to_insert:
            await db.executemany("""
                INSERT INTO home_screen_products 
                (section, title, price, original_price, discount_percent,
                 image_url, store_name, product_url, category)
                VALUES ($1, $2, $3, $4, $5, $6, $7, $8, $9)
            """, products_to_insert)
            print(f"[POSTGRES] Inserted {len(products_to_insert)} products")
        
        # Step 4: Update scrape_metadata
        from datetime import timedelta
        next_scrape = datetime.now(timezone.utc) + timedelta(hours=24)
        
        await db.execute("""
            INSERT INTO scrape_metadata
            (scrape_type, last_scrape_time, next_scrape_time, status, products_found)
            VALUES ($1, $2, $3, $4, $5)
        """, 'daily_homepage', datetime.now(timezone.utc), next_scrape, 'completed', total_products)
        print("[POSTGRES] Scrape metadata updated")
    
    return total_products


async def execute_daily_homepage_scraping(db: asyncpg.Connection) -> Dict[str, Any]:
    """
    Complete daily homepage scraping workflow.
    
    This is the main entry point for daily scraping that:
    1. Scrapes all platforms
    2. Curates products
    3. Saves to PostgreSQL
    
    Args:
        db: PostgreSQL database connection
    
    Returns:
        Summary dict with scraping results and curation stats
    """
    # Step 1: Scrape all platforms
    scraping_result = await scrape_homepage_daily()
    
    # Step 2: Curate products
    if scraping_result['all_products']:
        curated = curate_products(scraping_result['all_products'])
        
        # Step 3: Save to PostgreSQL
        saved_count = await save_curated_products_to_postgres(db, curated)
        
        return {
            'status': scraping_result['status'],
            'total_scraped': scraping_result['total_products'],
            'platforms_scraped': scraping_result['platforms_scraped'],
            'platforms_failed': scraping_result['platforms_failed'],
            'best_deals_count': len(curated['best_deals']),
            'top_price_drops_count': len(curated['top_price_drops']),
            'saved_to_db': saved_count,
            'scraped_at': scraping_result['scraped_at']
        }
    else:
        return {
            'status': 'failed',
            'error': 'No products scraped from any platform'
        }


# Additional utility functions for future tasks

async def scrape_search_query(query: str, tier: int = None) -> List[Dict[str, Any]]:
    """
    Scrape search results for a given query across platforms.
    
    This function will be used for tiered search implementation.
    
    Args:
        query: Search query string
        tier: Optional tier number (1 or 2) to scrape specific platforms
              If None, scrapes all platforms
    
    Returns:
        List of all scraped products
    """
    # Determine which platforms to scrape
    if tier == 1:
        platforms_to_scrape = TIER1_PLATFORMS
    elif tier == 2:
        platforms_to_scrape = TIER2_PLATFORMS
    else:
        # Scrape all platforms
        platforms_to_scrape = [p for p in PLATFORM_CONFIGS if p['scraper'] is not None]
    
    print(f"[SEARCH] Scraping {len(platforms_to_scrape)} platforms for query: '{query}'")
    
    # Create scraping tasks
    scraping_tasks = [
        scrape_single_platform(
            platform_name=config["name"],
            scraper_func=config["scraper"],
            query=query,
            max_pages=2  # Scrape first 2 pages for search
        )
        for config in platforms_to_scrape
    ]
    
    # Scrape concurrently
    results = await asyncio.gather(*scraping_tasks, return_exceptions=True)
    
    # Collect all products
    all_products = []
    for result in results:
        if isinstance(result, Exception):
            print(f"[SEARCH] Exception: {result}")
            continue
        
        if result["status"] == "success":
            all_products.extend(result["products"])
        
        # MongoDB logging removed
    
    return all_products


def curate_products(all_products: List[Dict[str, Any]]) -> Dict[str, List[Dict[str, Any]]]:
    """
    Curate products to identify best deals and top price drops.
    
    Algorithm:
    1. Calculate discount percentage for each product
    2. Find best deals: Top 25 products with highest discount % (>30%)
    3. Find top price drops: Top 25 products with largest absolute price reduction
    4. Handle products without original_price (skip from curation)
    5. Remove duplicates (same product from multiple platforms)
    
    Args:
        all_products: List of all scraped products from scrape_homepage_daily()
    
    Returns:
        Dict with keys:
            - best_deals: Top 25 products by discount percentage
            - top_price_drops: Top 25 products by absolute price drop
            - tech_gadgets: Top 20 tech products
            - audio_essentials: Top 20 audio products
            - home_appliances: Top 20 home products
    """
    import re
    print(f"[CURATION] Starting curation of {len(all_products)} products...")
    
    # Step 1: Calculate discount percentage and price drop for each product
    products_with_discounts = []
    
    for product in all_products:
        # Skip products without required fields
        if not product.get('price') or not product.get('original_price'):
            continue
        
        price = float(product['price'])
        original_price = float(product['original_price'])
        
        # Skip if original_price <= price (invalid discount)
        if original_price <= price:
            continue
        
        # Calculate discount percentage
        discount_percent = int(((original_price - price) / original_price) * 100)
        
        # Calculate absolute price drop
        price_drop = original_price - price
        
        # Add calculated fields to product
        product['discount_percent'] = discount_percent
        product['price_drop'] = price_drop
        
        products_with_discounts.append(product)
    
    print(f"[CURATION] {len(products_with_discounts)} products have valid discounts")
    
    # Step 2: Find best deals (highest discount percentage, minimum 30% off)
    best_deals_candidates = [p for p in products_with_discounts if p['discount_percent'] >= 30]
    best_deals_sorted = sorted(
        best_deals_candidates,
        key=lambda p: p['discount_percent'],
        reverse=True
    )
    best_deals = best_deals_sorted[:25]  # Top 25
    
    print(f"[CURATION] Found {len(best_deals)} best deals (>30% off)")
    
    # Step 3: Find top price drops (largest absolute price reduction)
    top_price_drops_sorted = sorted(
        products_with_discounts,
        key=lambda p: p['price_drop'],
        reverse=True
    )
    
    top_price_drops = []
    seen_urls = set()
    
    for product in top_price_drops_sorted:
        if len(top_price_drops) >= 25:
            break
            
        url = product.get('product_url', '')
        if url and url not in seen_urls:
            seen_urls.add(url)
            top_price_drops.append(product)
            
    # Step 4: Extract category sections
    tech_gadgets = []
    audio_essentials = []
    home_appliances = []
    
    # We want unique products across all categories
    # best_deals and top_price_drops are already added, we track them so they don't repeat
    category_seen_urls = set()
    for p in best_deals + top_price_drops:
        if p.get('product_url'):
            category_seen_urls.add(p.get('product_url'))
            
    # Regex patterns
    tech_pattern = re.compile(r'laptop|pc|monitor|macbook|asus|acer|dell|lenovo|smartphone|phone|watch', re.IGNORECASE)
    audio_pattern = re.compile(r'earbud|earphone|headphone|speaker|audio|sound|mic', re.IGNORECASE)
    home_pattern = re.compile(r'vacuum|cleaner|juicer|blender|fan|light|lamp|heater|home|cooker|iron', re.IGNORECASE)

    # Sort all products by scraped freshness or default
    for product in all_products:
        url = product.get('product_url', '')
        if not url or url in category_seen_urls:
            continue
            
        title = product.get('title', '')
        
        if len(tech_gadgets) < 20 and tech_pattern.search(title):
            tech_gadgets.append(product)
            category_seen_urls.add(url)
        elif len(audio_essentials) < 20 and audio_pattern.search(title):
            audio_essentials.append(product)
            category_seen_urls.add(url)
        elif len(home_appliances) < 20 and home_pattern.search(title):
            home_appliances.append(product)
            category_seen_urls.add(url)
            
    print(f"[CURATION] Found {len(best_deals)} best deals, {len(top_price_drops)} top price drops")
    print(f"[CURATION] Categories: {len(tech_gadgets)} tech, {len(audio_essentials)} audio, {len(home_appliances)} home")
    
    return {
        'best_deals': best_deals,
        'top_price_drops': top_price_drops,
        'tech_gadgets': tech_gadgets,
        'audio_essentials': audio_essentials,
        'home_appliances': home_appliances
    }



# ============================================================================
# TIERED SEARCH IMPLEMENTATION (Tasks 4.1-4.4)
# ============================================================================

import uuid
import json

async def check_search_cache(db: asyncpg.Connection, query: str) -> Dict[str, Any]:
    """
    Check if search results are cached and not expired.
    
    Args:
        db: PostgreSQL connection
        query: Search query string (normalized)
    
    Returns:
        Cache data dict or None if cache miss/expired
    """
    cache = await db.fetchrow("""
        SELECT query, tier1_results, tier2_results, 
               tier1_cached_at, tier2_cached_at, is_complete, request_id
        FROM search_cache
        WHERE query = $1
        AND tier1_cached_at > NOW() - INTERVAL '24 hours'
    """, query.lower().strip())
    
    if not cache:
        return None
    
    # Parse JSONB results
    tier1_results = json.loads(cache['tier1_results']) if cache['tier1_results'] else []
    tier2_results = json.loads(cache['tier2_results']) if cache['tier2_results'] else []
    
    return {
        'query': cache['query'],
        'tier1_results': tier1_results,
        'tier2_results': tier2_results,
        'is_complete': cache['is_complete'],
        'request_id': cache['request_id'],
        'cached_at': cache['tier1_cached_at']
    }


async def save_tier1_cache(
    db: asyncpg.Connection,
    query: str,
    tier1_results: List[Dict],
    request_id: str
) -> None:
    """
    Save Tier 1 search results to cache.
    
    Args:
        db: PostgreSQL connection
        query: Search query string
        tier1_results: List of products from Tier 1 platforms
        request_id: Unique request identifier
    """
    tier1_json = json.dumps(tier1_results)
    
    await db.execute("""
        INSERT INTO search_cache 
        (query, tier1_results, tier1_cached_at, is_complete, request_id)
        VALUES ($1, $2, $3, $4, $5)
        ON CONFLICT (query) DO UPDATE
        SET tier1_results = EXCLUDED.tier1_results,
            tier1_cached_at = EXCLUDED.tier1_cached_at,
            is_complete = EXCLUDED.is_complete,
            request_id = EXCLUDED.request_id
    """, query.lower().strip(), tier1_json, datetime.now(timezone.utc), False, request_id)
    
    print(f"[CACHE] Saved Tier 1 results for '{query}' (request_id: {request_id})")


async def update_tier2_cache(
    db: asyncpg.Connection,
    request_id: str,
    tier2_results: List[Dict]
) -> None:
    """
    Update cache with Tier 2 results when background scraping completes.
    
    Args:
        db: PostgreSQL connection
        request_id: Unique request identifier
        tier2_results: List of products from Tier 2 platforms
    """
    tier2_json = json.dumps(tier2_results)
    
    await db.execute("""
        UPDATE search_cache
        SET tier2_results = $1,
            tier2_cached_at = $2,
            is_complete = TRUE
        WHERE request_id = $3
    """, tier2_json, datetime.now(timezone.utc), request_id)
    
    print(f"[CACHE] Updated Tier 2 results (request_id: {request_id})")


async def save_complete_search_cache(
    db: asyncpg.Connection,
    query: str,
    all_results: List[Dict],
    request_id: str
) -> None:
    """
    Save complete search results (all platforms) to cache.
    
    Used when we scrape all platforms at once instead of tiered approach.
    
    Args:
        db: PostgreSQL connection
        query: Search query string
        all_results: List of all products from all platforms
        request_id: Unique request identifier
    """
    results_json = json.dumps(all_results)
    empty_json = json.dumps([])
    now = datetime.now(timezone.utc)
    
    await db.execute("""
        INSERT INTO search_cache 
        (query, tier1_results, tier1_cached_at, tier2_results, tier2_cached_at, is_complete, request_id)
        VALUES ($1, $2, $3, $4, $5, $6, $7)
        ON CONFLICT (query) DO UPDATE
        SET tier1_results = EXCLUDED.tier1_results,
            tier1_cached_at = EXCLUDED.tier1_cached_at,
            tier2_results = EXCLUDED.tier2_results,
            tier2_cached_at = EXCLUDED.tier2_cached_at,
            is_complete = EXCLUDED.is_complete,
            request_id = EXCLUDED.request_id
    """, query.lower().strip(), results_json, now, empty_json, now, True, request_id)
    
    print(f"[CACHE] Saved complete search results for '{query}' (request_id: {request_id}, {len(all_results)} products)")


def sort_search_results(query: str, products: List[Dict]) -> List[Dict]:
    """
    Sort search results by multi-signal relevance scoring.
    
    Scoring signals (lower = better, since we sort ascending):
    1. Token match score: how many query words appear in the title (most important)
    2. Exact phrase match bonus
    3. Accessory penalty: demote cases/covers/etc. unless query asks for them
    4. Price: higher price = more likely to be the actual product (descending)
    """
    import re
    query_lower = query.lower().strip()
    # Tokenize query — split on spaces and common separators
    query_tokens = [t for t in re.split(r'[\s\-_]+', query_lower) if len(t) > 1]
    query_token_set = set(query_tokens)

    accessory_keywords = {
        "cover", "case", "protector", "glass", "cable", "charger", "adapter",
        "strap", "band", "mount", "remote", "stand", "skin", "decal", "sticker",
        "hybrid", "magsafe", "magnetic", "silicone", "leather", "wallet",
        "tempered", "lens", "guard", "ring", "holder", "tripod", "pouch", "sleeve",
        "screen", "film", "back", "bumper", "grip", "clip", "dock", "hub",
        "bag", "backpack", "cooling", "pad", "cooler"
    }
    query_has_accessory = bool(query_token_set & accessory_keywords)

    valid_products = []
    for p in products:
        title = (p.get("title") or p.get("product_name") or "").lower()
        cat = (p.get("category") or "").lower()
        title_cat = title + " " + cat
        
        if len(query_tokens) > 1:
            matched = sum(1 for tok in query_tokens if tok in title_cat)
            if matched == 0:
                continue
                
        valid_products.append(p)

    def score_product(p: Dict) -> tuple:
        title = (p.get("title") or p.get("product_name") or "").lower()
        cat = (p.get("category") or "").lower()
        title_cat = title + " " + cat

        # --- Signal 1: Token match count (0 = all tokens match, bigger = fewer matches) ---
        matched_tokens = sum(1 for tok in query_tokens if tok in title_cat)
        total_tokens = max(len(query_tokens), 1)
        # Unmatched fraction: 0.0 means perfect, 1.0 means nothing matched
        unmatched_fraction = (total_tokens - matched_tokens) / total_tokens

        # --- Signal 2: Exact phrase bonus ---
        exact_phrase = 0 if query_lower in title_cat else 1  # 0=exact match (better)

        # --- Signal 3: Accessory penalty ---
        accessory_penalty = 0
        if not query_has_accessory and any(acc in title for acc in accessory_keywords):
            accessory_penalty = 1

        # --- Signal 4: Price (higher price → more likely to be the real product) ---
        price = p.get("price") or 0

        # Combined sort key (ascending — lower is better):
        # Priority: token match > exact phrase > accessory > price
        return (
            round(unmatched_fraction, 2),  # fewer matching tokens = worse
            exact_phrase,                   # no exact phrase = worse
            accessory_penalty,              # is accessory = worse
            -price,                         # lower price = worse (negative so higher sorts first)
        )

    sorted_products = sorted(valid_products, key=score_product)

    # Log relevance distribution
    if sorted_products:
        scores = [score_product(p) for p in sorted_products[:5]]
        print(f"[SORT] Top 5 relevance scores for '{query}': {scores}")

    return sorted_products


async def tiered_search(
    db: asyncpg.Connection,
    query: str
) -> Dict[str, Any]:
    """
    Execute search across ALL platforms for best results.
    
    SIMPLIFIED VERSION: Scrapes all 9 platforms simultaneously to ensure
    users get the best results from all available stores.
    
    Flow:
    1. Check cache - return if valid and complete
    2. If cache miss:
       a. Scrape ALL platforms (Tier 1 + Tier 2) simultaneously
       b. Sort and rank results by relevance
       c. Save to cache for 24 hours
       d. Return complete results
    
    Args:
        db: PostgreSQL connection
        query: Search query string
    
    Returns:
        Dict with:
            - request_id: Unique identifier for this search
            - query: Normalized query string
            - tier: "all" (always returns all platforms)
            - is_complete: True (always complete)
            - results: List of products from all platforms
            - results_count: Total number of products found
            - tier1_platforms: List of all platform names scraped
            - message: Status message
            - from_cache: Boolean indicating if results from cache
    """
    normalized_query = query.lower().strip()
    
    # Step 1: Check cache
    cached = await check_search_cache(db, normalized_query)
    
    if cached and cached['is_complete']:
        # Cache hit with complete results
        all_results = [p for p in cached['tier1_results'] + cached['tier2_results'] if p.get("product_url")]
        sorted_results = sort_search_results(normalized_query, all_results)
        return {
            'request_id': cached['request_id'],
            'query': normalized_query,
            'tier': 'all',
            'is_complete': True,
            'results': sorted_results,
            'results_count': len(sorted_results),
            'tier1_platforms': [p['name'] for p in PLATFORM_CONFIGS if p['scraper'] is not None],
            'message': f'Found {len(sorted_results)} products from cache',
            'from_cache': True
        }
    
    # Step 2: Cache miss - scrape ALL platforms simultaneously
    print(f"[SEARCH] Cache miss for '{normalized_query}', scraping ALL platforms...")
    
    all_products = await scrape_search_query(normalized_query, tier=None)  # None = all platforms
    
    # Step 3: Filter valid products and sort by relevance
    valid_products = [p for p in all_products if p.get("product_url")]
    sorted_products = sort_search_results(normalized_query, valid_products)
    
    # Step 4: Save to cache as complete results
    request_id = str(uuid.uuid4())
    await save_complete_search_cache(db, normalized_query, sorted_products, request_id)
    
    print(f"[SEARCH] Found {len(sorted_products)} products from {len([p for p in PLATFORM_CONFIGS if p['scraper']])} platforms")
    
    return {
        'request_id': request_id,
        'query': normalized_query,
        'tier': 'all',
        'is_complete': True,
        'results': sorted_products,
        'results_count': len(sorted_products),
        'tier1_platforms': [p['name'] for p in PLATFORM_CONFIGS if p['scraper'] is not None],
        'message': f'Found {len(sorted_products)} products from all platforms',
        'from_cache': False
    }


async def scrape_tier2_background(
    db: asyncpg.Connection,
    query: str,
    request_id: str
) -> None:
    """
    Scrape Tier 2 platforms in background and update cache.
    
    This function is meant to be called as a background task.
    
    Args:
        db: PostgreSQL connection
        query: Search query string
        request_id: Request ID from Tier 1 response
    """
    print(f"[TIER2_BACKGROUND] Starting Tier 2 scraping for '{query}'...")
    
    try:
        # Scrape Tier 2 platforms
        tier2_products = await scrape_search_query(query, tier=2)
        
        # Update cache with Tier 2 results
        valid_tier2 = [p for p in tier2_products if p.get("product_url")]
        await update_tier2_cache(db, request_id, valid_tier2)
        
        print(f"[TIER2_BACKGROUND] Completed: {len(tier2_products)} products from Tier 2")
        
    except Exception as e:
        print(f"[TIER2_BACKGROUND] Error: {e}")
        # Don't update cache on error - Tier 1 results still available


async def scrape_daraz_background(
    db_pool: asyncpg.Pool,
    query: str,
    request_id: str
) -> None:
    """
    Scrape Daraz in background and update cache.
    """
    print(f"[DARAZ_BACKGROUND] Starting Daraz scraping for '{query}'...")
    
    try:
        # Scrape Daraz
        daraz_config = next((p for p in PLATFORM_CONFIGS if p['name'] == 'Daraz'), None)
        if not daraz_config or not daraz_config['scraper']:
            return
            
        result = await scrape_single_platform(
            platform_name="Daraz",
            scraper_func=daraz_config["scraper"],
            query=query,
            max_pages=1
        )
        
        daraz_products = result.get('products', []) if result.get('status') == 'success' else []
        
        # Update cache with Daraz results
        valid_daraz = [p for p in daraz_products if p.get("product_url")]
        async with db_pool.acquire() as db:
            await update_tier2_cache(db, request_id, valid_daraz)
            
            # Save products to the main database for future offline searches
            for p in valid_daraz:
                try:
                    await db.execute("""
                        INSERT INTO products (title, price, original_price, discount_percent, image_url, store_name, product_url, category)
                        VALUES ($1, $2, $3, $4, $5, $6, $7, $8)
                        ON CONFLICT (product_url) DO UPDATE
                        SET title = EXCLUDED.title,
                            price = EXCLUDED.price,
                            original_price = EXCLUDED.original_price,
                            discount_percent = EXCLUDED.discount_percent,
                            image_url = EXCLUDED.image_url,
                            category = EXCLUDED.category,
                            scraped_at = CURRENT_TIMESTAMP
                    """, p['title'], p['price'], p.get('original_price'), p.get('discount_percent'), p.get('image_url'), p['store_name'], p['product_url'], p.get('category'))
                except Exception as db_err:
                    print(f"[DARAZ_BACKGROUND] Error saving product to DB: {db_err}")
        
        print(f"[DARAZ_BACKGROUND] Completed: {len(valid_daraz)} products from Daraz")
        
    except Exception as e:
        print(f"[DARAZ_BACKGROUND] Error: {e}")
        # Mark as complete even on error so frontend stops polling
        async with db_pool.acquire() as db:
            await update_tier2_cache(db, request_id, [])


async def get_search_status(
    db: asyncpg.Connection,
    request_id: str
) -> Dict[str, Any]:
    """
    Get search status for polling endpoint.
    
    Args:
        db: PostgreSQL connection
        request_id: Request ID from initial search
    
    Returns:
        Dict with:
            - request_id: The request ID
            - is_complete: Boolean
            - new_results: List of Tier 2 products
            - new_results_count: Count of Tier 2 products
            - message: Status message
    """
    cache = await db.fetchrow("""
        SELECT query, tier2_results, is_complete
        FROM search_cache
        WHERE request_id = $1
    """, request_id)
    
    if not cache:
        return {
            'request_id': request_id,
            'is_complete': False,
            'new_results': [],
            'new_results_count': 0,
            'message': 'Request not found or expired'
        }
    
    tier2_results = json.loads(cache['tier2_results']) if cache['tier2_results'] else []
    tier2_results = [p for p in tier2_results if p.get("product_url")]
    
    query = cache['query']
    
    sorted_tier2 = sort_search_results(query, tier2_results) if tier2_results else []
    
    return {
        'request_id': request_id,
        'is_complete': cache['is_complete'],
        'new_results': sorted_tier2,
        'new_results_count': len(sorted_tier2),
        'message': 'Tier 2 scraping complete' if cache['is_complete'] else 'Tier 2 scraping in progress...'
    }


async def cleanup_expired_cache(db: asyncpg.Connection) -> int:
    """
    Delete expired cache entries (older than 24 hours).
    
    Args:
        db: PostgreSQL connection
    
    Returns:
        Number of entries deleted
    """
    result = await db.execute("""
        DELETE FROM search_cache
        WHERE tier1_cached_at < NOW() - INTERVAL '24 hours'
    """)
    
    # Extract count from result string like "DELETE 5"
    deleted_count = int(result.split()[-1]) if result else 0
    print(f"[CLEANUP] Deleted {deleted_count} expired cache entries")
    
    return deleted_count

# ============================================================================
# GLOBAL SCRAPING FOR DATABASE SEARCH (Tasks 3)
# ============================================================================

async def execute_global_scraping(db: asyncpg.Connection) -> Dict[str, Any]:
    """
    Two-phase scraping strategy for maximum product coverage:
    
    Phase 1 — Full Catalog Scrape:
        - Hukut: empty search query returns ALL ~3,000+ products via offset pagination
    
    Phase 2 — Keyword Scrape (100+ terms):
        - Jeevee: full pagination per term
        - Oliz, CGDigital, Daraz (rate-limited): key terms
    
    Target: 30,000–50,000 unique products
    """
    start_time = datetime.now(timezone.utc)
    print("[GLOBAL SCRAPER] Starting full-coverage scraping...")

    all_products = []

    # ─────────────────────────────────────────────────────
    # PHASE 1: Full Catalog — Hukut (empty search = all products)
    # ─────────────────────────────────────────────────────
    print("\n[PHASE 1] Scraping Hukut full catalog (all products)...")
    hukut_config = next((c for c in PLATFORM_CONFIGS if c["name"] == "Hukut"), None)
    if hukut_config and hukut_config["scraper"]:
        hukut_result = await scrape_single_platform(
            platform_name="Hukut",
            scraper_func=hukut_config["scraper"],
            query="",        # empty = return entire catalog
            max_pages=999
        )
        if hukut_result["status"] == "success":
            for p in hukut_result["products"]:
                p["category"] = "general"
            all_products.extend(hukut_result["products"])
            print(f"[PHASE 1] Hukut: {hukut_result['products_count']} products collected.")

    # ─────────────────────────────────────────────────────
    # PHASE 2: Comprehensive keyword scraping
    # 100+ terms to maximize Jeevee, Oliz, CGDigital, Daraz coverage
    # ─────────────────────────────────────────────────────

    # Platforms for keyword scraping (excluding Hukut which was done in Phase 1)
    keyword_platforms = [c for c in PLATFORM_CONFIGS if c["scraper"] is not None and c["name"] != "Hukut"]

    # 100+ search terms organized by category for maximum unique coverage
    search_terms = [
        # ── Phones ──
        ("phone", "phone"), ("smartphone", "phone"), ("iphone", "phone"),
        ("samsung", "phone"), ("xiaomi", "phone"), ("realme", "phone"),
        ("oppo", "phone"), ("vivo", "phone"), ("oneplus", "phone"),
        ("motorola", "phone"), ("nokia", "phone"), ("huawei", "phone"),

        # ── Laptops ──
        ("laptop", "laptop"), ("gaming laptop", "laptop"),
        ("hp laptop", "laptop"), ("dell laptop", "laptop"),
        ("lenovo laptop", "laptop"), ("asus laptop", "laptop"),
        ("acer laptop", "laptop"), ("macbook", "laptop"),
        ("chromebook", "laptop"), ("notebook", "laptop"),

        # ── Tablets ──
        ("tablet", "tablet"), ("ipad", "tablet"), ("samsung tab", "tablet"),

        # ── Monitors ──
        ("monitor", "monitor"), ("gaming monitor", "monitor"),
        ("4k monitor", "monitor"), ("curved monitor", "monitor"),
        ("ips monitor", "monitor"), ("144hz monitor", "monitor"),

        # ── TVs ──
        ("tv", "tv"), ("smart tv", "tv"), ("led tv", "tv"),
        ("4k tv", "tv"), ("oled tv", "tv"), ("samsung tv", "tv"),
        ("lg tv", "tv"), ("sony tv", "tv"),

        # ── Audio ──
        ("earbuds", "audio"), ("wireless earbuds", "audio"),
        ("headphones", "audio"), ("headset", "audio"),
        ("bluetooth speaker", "audio"), ("soundbar", "audio"),
        ("neckband", "audio"), ("tws", "audio"),

        # ── Cameras ──
        ("camera", "camera"), ("dslr", "camera"),
        ("mirrorless camera", "camera"), ("action camera", "camera"),
        ("gopro", "camera"), ("webcam", "camera"),
        ("security camera", "camera"), ("cctv", "camera"),

        # ── Watches & Wearables ──
        ("smartwatch", "smartwatch"), ("apple watch", "smartwatch"),
        ("fitness band", "smartwatch"), ("smart band", "smartwatch"),
        ("galaxy watch", "smartwatch"),

        # ── Computer Components ──
        ("ssd", "computer-parts"), ("nvme ssd", "computer-parts"),
        ("hard disk", "computer-parts"), ("external hard drive", "computer-parts"),
        ("ram", "computer-parts"), ("graphics card", "computer-parts"),
        ("gpu", "computer-parts"), ("processor", "computer-parts"),
        ("motherboard", "computer-parts"), ("power supply", "computer-parts"),
        ("cpu cooler", "computer-parts"), ("pc case", "computer-parts"),
        ("computer", "computer-parts"),

        # ── Peripherals ──
        ("keyboard", "peripherals"), ("mechanical keyboard", "peripherals"),
        ("gaming keyboard", "peripherals"), ("mouse", "peripherals"),
        ("gaming mouse", "peripherals"), ("mousepad", "peripherals"),
        ("webcam", "peripherals"), ("microphone", "peripherals"),

        # ── Networking ──
        ("router", "networking"), ("wifi router", "networking"),
        ("mesh router", "networking"), ("network switch", "networking"),
        ("access point", "networking"),

        # ── Storage ──
        ("usb flash drive", "storage"), ("memory card", "storage"),
        ("sd card", "storage"), ("pen drive", "storage"),

        # ── Mobile Accessories ──
        ("power bank", "accessories"), ("charger", "accessories"),
        ("wireless charger", "accessories"), ("phone case", "accessories"),
        ("screen protector", "accessories"), ("cable", "accessories"),
        ("usb c cable", "accessories"), ("lightning cable", "accessories"),

        # ── Home Appliances ──
        ("refrigerator", "appliances"), ("washing machine", "appliances"),
        ("air conditioner", "appliances"), ("microwave", "appliances"),
        ("air purifier", "appliances"), ("vacuum cleaner", "appliances"),
        ("electric kettle", "appliances"), ("rice cooker", "appliances"),
        ("water purifier", "appliances"), ("room heater", "appliances"),

        # ── Kitchen ──
        ("blender", "kitchen"), ("mixer", "kitchen"),
        ("induction cooker", "kitchen"), ("electric oven", "kitchen"),
        ("sandwich maker", "kitchen"), ("juicer", "kitchen"),

        # ── Gaming ──
        ("gaming console", "gaming"), ("ps5", "gaming"),
        ("xbox", "gaming"), ("nintendo switch", "gaming"),
        ("gaming controller", "gaming"), ("gaming chair", "gaming"),
        ("gaming headset", "gaming"),

        # ── Printers & Office ──
        ("printer", "office"), ("projector", "office"),
        ("scanner", "office"), ("ups", "office"),
        ("stabilizer", "office"),

        # ── Personal Care ──
        ("trimmer", "personal-care"), ("hair dryer", "personal-care"),
        ("electric shaver", "personal-care"),
    ]

    print(f"\n[PHASE 2] Keyword scraping: {len(search_terms)} terms × {len(keyword_platforms)} platforms...")

    # Process in batches of 8 terms at a time (all platforms concurrently per batch)
    batch_size = 8
    for batch_start in range(0, len(search_terms), batch_size):
        batch = search_terms[batch_start:batch_start + batch_size]
        batch_num = batch_start // batch_size + 1
        total_batches = (len(search_terms) + batch_size - 1) // batch_size
        print(f"[PHASE 2] Batch {batch_num}/{total_batches}: {[t[0] for t in batch]}")

        # Build tasks: each term × each platform
        tasks = []
        task_meta = []
        for term, category in batch:
            for config in keyword_platforms:
                tasks.append(scrape_single_platform(
                    platform_name=config["name"],
                    scraper_func=config["scraper"],
                    query=term,
                    max_pages=999
                ))
                task_meta.append((term, category, config["name"]))

        results = await asyncio.gather(*tasks, return_exceptions=True)

        batch_count = 0
        for (term, category, platform), result in zip(task_meta, results):
            if isinstance(result, Exception):
                continue
            if result["status"] == "success" and result["products"]:
                for p in result["products"]:
                    p["category"] = category
                all_products.extend(result["products"])
                batch_count += result["products_count"]

        print(f"[PHASE 2] Batch {batch_num} done — {batch_count} products. Running total: {len(all_products)}")

    print(f"\n[GLOBAL SCRAPER] All scraping complete. Total raw: {len(all_products)}")

    # ─────────────────────────────────────────────────────
    # Deduplicate by URL
    # ─────────────────────────────────────────────────────
    unique_products = {}
    for p in all_products:
        url = p.get("product_url")
        if url and url not in unique_products:
            unique_products[url] = p

    products_to_save = list(unique_products.values())
    print(f"[GLOBAL SCRAPER] Deduped to {len(products_to_save)} unique products.")

    # ─────────────────────────────────────────────────────
    # Save to PostgreSQL
    # ─────────────────────────────────────────────────────
    print(f"[GLOBAL SCRAPER] Inserting {len(products_to_save)} products into PostgreSQL...")

    # PostgreSQL bulk insert
    pg_records = []
    for product in products_to_save:
        # Get title from either key
        title = (product.get("title") or product.get("product_name") or "Unknown")[:255]

        price_val = float(product.get("price", 0) or 0)
        if price_val > 99999999:
            price_val = 99999999

        orig_price_val = product.get("original_price")
        if orig_price_val:
            try:
                orig_price_val = float(orig_price_val)
                if orig_price_val > 99999999:
                    orig_price_val = 99999999
            except (TypeError, ValueError):
                orig_price_val = None
        else:
            orig_price_val = None

        disc = product.get("discount_percent") or product.get("discount_percentage")
        try:
            disc_val = int(disc) if disc is not None else None
        except (TypeError, ValueError):
            disc_val = None

        pg_records.append((
            title,
            price_val,
            orig_price_val,
            disc_val,
            product.get("image_url"),
            product.get("store_name", "Unknown"),
            product.get("product_url"),
            product.get("category"),
            None  # mongo_id
        ))

    saved_count = 0
    if pg_records:
        try:
            await db.executemany("""
                INSERT INTO products
                (title, price, original_price, discount_percent, image_url, store_name, product_url, category, mongo_id)
                VALUES ($1, $2, $3, $4, $5, $6, $7, $8, $9)
                ON CONFLICT (product_url) DO UPDATE
                SET title = EXCLUDED.title,
                    price = EXCLUDED.price,
                    original_price = EXCLUDED.original_price,
                    discount_percent = EXCLUDED.discount_percent,
                    image_url = EXCLUDED.image_url,
                    category = EXCLUDED.category,
                    scraped_at = NOW()
            """, pg_records)
            saved_count = len(pg_records)
            print(f"[GLOBAL SCRAPER] PostgreSQL: {saved_count} records inserted/updated.")
        except Exception as e:
            print(f"[GLOBAL SCRAPER] PostgreSQL bulk error: {e}")

    end_time = datetime.now(timezone.utc)
    duration_ms = int((end_time - start_time).total_seconds() * 1000)
    print(f"\n[GLOBAL SCRAPER] Done in {duration_ms/1000:.1f}s — saved {saved_count} products.")

    return {
        "status": "completed",
        "total_scraped": len(all_products),
        "unique_products": len(products_to_save),
        "saved_to_db": saved_count,
        "duration_ms": duration_ms
    }

async def live_search_and_save(query: str, platform_filter: str = None):
    """
    Executes a live search across all scrapers for a specific query and saves the results to the database.
    This is triggered asynchronously by the /search API endpoint.
    """
    from app.database.postgres import pool
    
    print(f"[LIVE SEARCH] Triggered live search for query: {query}" + (f" on {platform_filter}" if platform_filter else ""))
    start_time = datetime.now(timezone.utc)
    
    scraping_tasks = [
        scrape_single_platform(
            platform_name=config["name"],
            scraper_func=config["scraper"],
            query=query,
            max_pages=1  # Only scrape 1 page for live search speed
        )
        for config in PLATFORM_CONFIGS if config["scraper"] is not None and (platform_filter is None or config["name"].lower() == platform_filter.lower())
    ]
    
    results = await asyncio.gather(*scraping_tasks, return_exceptions=True)
    
    all_products = []
    for result in results:
        if isinstance(result, Exception):
            continue
        if result["status"] == "success":
            for p in result["products"]:
                p["category"] = query
            all_products.extend(result["products"])
            
    if not all_products:
        print(f"[LIVE SEARCH] No products found for query: {query}")
        return
        
    print(f"[LIVE SEARCH] Scraping complete. Found {len(all_products)} total raw products.")
    
    # Deduplicate
    unique_products = {}
    for p in all_products:
        url = p.get("product_url")
        if url and url not in unique_products:
            unique_products[url] = p
            
    products_to_save = list(unique_products.values())
    print(f"[LIVE SEARCH] Deduped to {len(products_to_save)} unique products. Preparing DB insert...")
    
    pg_records = []
    for product in products_to_save:
        price_val = float(product.get("price", 0))
        if price_val > 99999999: price_val = 99999999
        
        orig_price_val = product.get("original_price")
        if orig_price_val:
            orig_price_val = float(orig_price_val)
            if orig_price_val > 99999999: orig_price_val = 99999999
        else:
            orig_price_val = None
            
        pg_records.append((
            product.get("title", "Unknown")[:255],
            price_val,
            orig_price_val,
            int(product.get("discount_percent")) if product.get("discount_percent") else None,
            product.get("image_url"),
            product.get("store_name", "Unknown"),
            product.get("product_url"),
            product.get("category"),
            None
        ))
        
    saved_count = 0
    if pg_records and pool:
        try:
            async with pool.acquire() as db_conn:
                await db_conn.executemany("""
                    INSERT INTO products 
                    (title, price, original_price, discount_percent, image_url, store_name, product_url, category, mongo_id)
                    VALUES ($1, $2, $3, $4, $5, $6, $7, $8, $9)
                    ON CONFLICT (product_url) DO UPDATE
                    SET title = EXCLUDED.title,
                        price = EXCLUDED.price,
                        original_price = EXCLUDED.original_price,
                        discount_percent = EXCLUDED.discount_percent,
                        image_url = EXCLUDED.image_url,
                        scraped_at = NOW()
                """, pg_records)
                saved_count = len(pg_records)
        except Exception as e:
            print(f"[LIVE SEARCH] Postgres bulk save error: {e}")
            
    end_time = datetime.now(timezone.utc)
    duration_ms = int((end_time - start_time).total_seconds() * 1000)
    print(f"[LIVE SEARCH] Successfully saved {saved_count} new products in {duration_ms}ms")
