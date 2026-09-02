"""
bulk_scrape_all.py
==================
Exhaustively scrapes all categories from all 9 platforms across many pages.
Run this standalone: python bulk_scrape_all.py
It saves products directly to PostgreSQL as it goes.
"""

import asyncio
import asyncpg
import os
import sys
import time
from datetime import datetime, timezone
from dotenv import load_dotenv

# Add parent path so scrapers module is found
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
load_dotenv()

# ─────────────────────────────────────────────────────────────────────────────
# SEARCH TERMS BY CATEGORY (broad terms to maximise unique products from Daraz)
# ─────────────────────────────────────────────────────────────────────────────
CATEGORIES = {
    "Electronics": [
        "laptop", "gaming laptop", "macbook", "dell laptop", "hp laptop",
        "smartphone", "iphone", "samsung phone", "xiaomi", "realme phone",
        "tablet", "ipad", "android tablet",
        "tv", "smart tv", "led tv", "4k tv",
        "headphone", "earphone", "bluetooth earphone", "airpods",
        "camera", "dslr camera", "mirrorless camera", "action camera",
        "power bank", "charger", "usb hub", "keyboard", "mouse",
        "monitor", "gaming monitor", "printer", "scanner", "projector",
    ],
    "Mobile Accessories": [
        "phone case", "screen protector", "mobile cover",
        "phone stand", "selfie stick", "phone holder", "car mount",
        "wireless charger", "fast charger cable", "type c cable",
    ],
    "Home Appliances": [
        "refrigerator", "washing machine", "air conditioner", "microwave",
        "vacuum cleaner", "iron", "rice cooker", "blender", "mixer",
        "water heater", "fan", "air purifier", "dishwasher",
    ],
    "Kitchen": [
        "cookware set", "frying pan", "pressure cooker", "knife set",
        "cutting board", "storage container", "thermos", "lunch box",
        "coffee maker", "electric kettle", "toaster", "juicer",
    ],
    "Fashion": [
        "men shirt", "men trouser", "men jacket", "men suit",
        "women dress", "women top", "women jeans", "women kurta",
        "sneakers", "running shoes", "formal shoes", "sandals",
        "handbag", "backpack", "wallet", "belt",
        "sunglasses", "watch", "bracelet", "necklace",
    ],
    "Beauty & Health": [
        "face wash", "moisturizer", "sunscreen", "foundation", "lipstick",
        "shampoo", "conditioner", "hair oil", "body lotion",
        "vitamin c", "protein powder", "multivitamin", "face mask",
        "perfume", "deodorant", "nail polish", "hair dryer",
    ],
    "Sports": [
        "yoga mat", "dumbbell", "resistance band", "jump rope",
        "cricket bat", "football", "badminton racket", "cycling helmet",
        "running shoes", "gym gloves", "treadmill", "cycling",
    ],
    "Baby & Kids": [
        "baby clothes", "baby shoes", "diaper", "baby food",
        "toys", "lego", "puzzle", "baby stroller", "school bag",
    ],
    "Books & Stationery": [
        "notebook", "pen", "pencil", "marker", "stationery set",
        "file folder", "sticky notes", "calculator",
    ],
    "Gaming": [
        "gaming mouse", "gaming keyboard", "gaming headset",
        "gaming chair", "ps5", "xbox", "nintendo switch",
        "gaming controller", "graphics card", "ram memory",
    ],
}

# ALL scrapers and their names
SCRAPERS = [
    ("Daraz",        "scrapers.daraz.daraz_scraper",        "async_scrape_daraz",        {"max_pages": 40}),
    ("Oliz",         "scrapers.oliz.oliz_scraper",          "async_scrape_oliz",         {}),
    ("CgDigital",    "scrapers.cgdigital.cgdigital_scraper","async_scrape_cgdigital",    {}),
    ("HardwarePasal","scrapers.hardwarepasal.hardwarepasal_scraper","async_scrape_hardwarepasal",{}),
    ("NeoStore",     "scrapers.neostore.neostore_scraper",  "async_scrape_neostore",     {}),
    ("Better",       "scrapers.better.better_scraper",      "async_scrape_better",       {}),
    ("UfoNepal",     "scrapers.ufonepal.ufonepal_scraper",  "async_scrape_ufonepal",     {}),
]

# ─────────────────────────────────────────────────────────────────────────────
# DB helpers
# ─────────────────────────────────────────────────────────────────────────────
async def get_conn():
    return await asyncpg.connect(os.getenv("DATABASE_URL"), statement_cache_size=0)


async def bulk_insert(conn, records: list):
    """Insert a batch of scraped products, ignoring duplicates."""
    if not records:
        return 0

    pg_records = []
    for r in records:
        title = r.get("product_name") or r.get("title", "")
        price = r.get("price")
        if not title or not price:
            continue
        try:
            price = float(price)
        except (TypeError, ValueError):
            continue

        original_price = r.get("original_price")
        try:
            original_price = float(original_price) if original_price else None
        except (TypeError, ValueError):
            original_price = None

        discount = r.get("discount_percentage") or r.get("discount_percent")
        try:
            discount = int(discount) if discount else None
        except (TypeError, ValueError):
            discount = None

        image_url   = r.get("image_url", "")
        store_name  = r.get("platform") or r.get("store_name", "")
        product_url = r.get("product_url", "")
        category    = r.get("category", "")

        pg_records.append((title, price, original_price, discount,
                           image_url, store_name, product_url, category))

    if not pg_records:
        return 0

    try:
        await conn.executemany("""
            INSERT INTO products
              (title, price, original_price, discount_percent,
               image_url, store_name, product_url, category)
            VALUES ($1, $2, $3, $4, $5, $6, $7, $8)
            ON CONFLICT (product_url) DO UPDATE
              SET title          = EXCLUDED.title,
                  price          = EXCLUDED.price,
                  original_price = EXCLUDED.original_price,
                  discount_percent = EXCLUDED.discount_percent,
                  image_url      = EXCLUDED.image_url,
                  scraped_at     = NOW()
        """, pg_records)
        return len(pg_records)
    except Exception as e:
        print(f"    [DB ERROR] {e}")
        return 0


# ─────────────────────────────────────────────────────────────────────────────
# Scrape one term on one scraper
# ─────────────────────────────────────────────────────────────────────────────
async def scrape_term(scraper_info, term, category):
    store_name, module_path, func_name, kwargs = scraper_info
    try:
        import importlib
        mod  = importlib.import_module(module_path)
        func = getattr(mod, func_name)
        products = await func(term, **kwargs)
        # Tag with category
        for p in products:
            p["category"] = category
        return products
    except Exception as e:
        print(f"    [{store_name}] Error scraping '{term}': {e}")
        return []


# ─────────────────────────────────────────────────────────────────────────────
# Main
# ─────────────────────────────────────────────────────────────────────────────
async def main():
    conn = await get_conn()
    start = time.time()

    # Count before
    before = await conn.fetchval("SELECT COUNT(*) FROM products")
    print(f"\n{'='*60}")
    print(f"  BULK SCRAPER — starting with {before:,} products in DB")
    print(f"{'='*60}\n")

    total_saved = 0
    total_terms = sum(len(v) for v in CATEGORIES.values())
    done_terms  = 0

    for category, terms in CATEGORIES.items():
        print(f"\n>>  Category: {category}  ({len(terms)} terms)")

        for term in terms:
            done_terms += 1
            elapsed = time.time() - start
            eta_per_term = elapsed / done_terms if done_terms else 0
            remaining = (total_terms - done_terms) * eta_per_term
            print(f"  [{done_terms}/{total_terms}] '{term}'  |  "
                  f"elapsed={elapsed/60:.1f}m  eta={remaining/60:.1f}m")

            # Run all scrapers in parallel for this term
            tasks = [scrape_term(s, term, category) for s in SCRAPERS]
            results = await asyncio.gather(*tasks, return_exceptions=True)

            batch = []
            for res in results:
                if isinstance(res, list):
                    batch.extend(res)

            saved = await bulk_insert(conn, batch)
            total_saved += saved
            print(f"    → {len(batch)} scraped, {saved} saved to DB")

    # Final count
    after = await conn.fetchval("SELECT COUNT(*) FROM products")
    print(f"\n{'='*60}")
    print(f"  DONE!  Added {after - before:,} new products.")
    print(f"  Total in DB: {after:,}")
    print(f"  Time taken:  {(time.time()-start)/60:.1f} minutes")
    print(f"{'='*60}\n")

    await conn.close()


if __name__ == "__main__":
    asyncio.run(main())
