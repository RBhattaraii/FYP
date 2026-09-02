#!/usr/bin/env python3
"""
Sitewide scraper for supported platforms.
Uses each platform's scraper with an empty or generic query to collect full catalog data,
then stores results into a local SQLite DB with unique product URLs.
"""

import asyncio
import os
import sqlite3
import sys
import time
from datetime import datetime, timezone

ROOT_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
if ROOT_DIR not in sys.path:
    sys.path.insert(0, ROOT_DIR)

from scrapers.jeevee.jeevee_scraper import async_scrape_jeevee
from scrapers.oliz.oliz_scraper import async_scrape_oliz
from scrapers.hukut.hukut_scraper import async_scrape_hukut
from scrapers.cgdigital.cgdigital_scraper import async_scrape_cgdigital
from scrapers.neostore.neostore_scraper import async_scrape_neostore
from scrapers.ufonepal.ufonepal_scraper import async_scrape_ufonepal
from scrapers.hardwarepasal.hardwarepasal_scraper import async_scrape_hardwarepasal
from scrapers.better.better_scraper import async_scrape_better

DB_PATH = os.path.join(os.path.dirname(__file__), 'sitewide_products.db')

PLATFORM_CONFIGS = [
    {
        'name': 'Jeevee',
        'func': async_scrape_jeevee,
        'queries': [''],
        'max_pages': 999,
        'delay': 2.5,
    },
    {
        'name': 'Hukut',
        'func': async_scrape_hukut,
        'queries': [''],
        'max_pages': 999,
        'delay': 2.5,
    },
    {
        'name': 'Oliz',
        'func': async_scrape_oliz,
        'queries': [''],
        'max_pages': 50,
        'delay': 2.5,
    },
    {
        'name': 'CGDigital',
        'func': async_scrape_cgdigital,
        'queries': [''],
        'max_pages': None,
        'delay': 2.5,
    },
    {
        'name': 'NeoStore',
        'func': async_scrape_neostore,
        'queries': [''],
        'max_pages': None,
        'delay': 2.0,
    },
    {
        'name': 'UfoNepal',
        'func': async_scrape_ufonepal,
        'queries': [''],
        'max_pages': None,
        'delay': 2.5,
    },
    {
        'name': 'HardwarePasal',
        'func': async_scrape_hardwarepasal,
        'queries': [''],
        'max_pages': None,
        'delay': 3.0,
    },
    {
        'name': 'Better',
        'func': async_scrape_better,
        'queries': ['', 'all', 'products', 'shop'],
        'max_pages': None,
        'delay': 3.5,
    },
]

GENERIC_FALLBACK_QUERIES = ['all', 'products', 'shop', 'shop now', 'latest']


def setup_database():
    conn = sqlite3.connect(DB_PATH, timeout=30)
    cursor = conn.cursor()
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS products (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            title TEXT NOT NULL,
            price REAL,
            original_price REAL,
            discount_percent REAL,
            image_url TEXT,
            product_url TEXT UNIQUE,
            category TEXT,
            platform TEXT,
            search_term TEXT,
            scraped_at TEXT,
            source TEXT
        )
    ''')
    cursor.execute('CREATE INDEX IF NOT EXISTS idx_product_url ON products(product_url)')
    conn.commit()
    conn.close()


def save_products(products, platform_name, search_term):
    conn = sqlite3.connect(DB_PATH, timeout=30)
    cursor = conn.cursor()
    added = 0
    skipped = 0
    now = datetime.now(timezone.utc).isoformat()

    for raw in products:
        product_url = raw.get('product_url') or raw.get('url') or raw.get('link') or ''
        if not product_url or not isinstance(product_url, str) or len(product_url.strip()) == 0:
            skipped += 1
            continue

        title = raw.get('product_name') or raw.get('title') or raw.get('name') or 'Unknown Product'
        price = raw.get('price')
        original_price = raw.get('original_price')
        discount_percent = raw.get('discount_percentage') or raw.get('discount_percent')
        image_url = raw.get('image_url') or raw.get('image')
        category = raw.get('category') or raw.get('search_term') or None
        source = raw.get('source') or platform_name.lower()

        try:
            cursor.execute('''
                INSERT OR IGNORE INTO products
                (title, price, original_price, discount_percent, image_url, product_url,
                 category, platform, search_term, scraped_at, source)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            ''', (
                title[:250],
                float(price) if price is not None else None,
                float(original_price) if original_price is not None else None,
                float(discount_percent) if discount_percent is not None else None,
                image_url,
                product_url,
                category,
                platform_name,
                search_term,
                now,
                source,
            ))
            if cursor.rowcount > 0:
                added += 1
            else:
                skipped += 1
        except Exception:
            skipped += 1

    conn.commit()
    conn.close()
    return added, skipped


def clean_duplicates():
    conn = sqlite3.connect(DB_PATH, timeout=30)
    cursor = conn.cursor()

    cursor.execute('SELECT COUNT(*) FROM products')
    total_before = cursor.fetchone()[0]

    cursor.execute('''
        DELETE FROM products
        WHERE id NOT IN (
            SELECT MIN(id)
            FROM products
            WHERE product_url IS NOT NULL AND product_url != ''
            GROUP BY product_url
        )
        AND product_url IS NOT NULL AND product_url != ''
    ''')
    deleted_duplicates = cursor.rowcount
    conn.commit()

    cursor.execute("DELETE FROM products WHERE product_url IS NULL OR product_url = ''")
    deleted_invalid = cursor.rowcount
    conn.commit()

    cursor.execute('SELECT COUNT(*) FROM products')
    total_after = cursor.fetchone()[0]
    conn.close()

    print(f"✅ Duplication cleanup complete: {deleted_duplicates} duplicates removed, {deleted_invalid} invalid rows removed")
    print(f"   Total before: {total_before}, total after: {total_after}")
    return total_after


def safe_call_scraper(scraper, query, max_pages=None):
    if max_pages is None:
        return scraper(query)
    try:
        return scraper(query, max_pages=max_pages)
    except TypeError:
        return scraper(query)


async def scrape_platform(config):
    name = config['name']
    scraper = config['func']
    queries = config.get('queries', [''])
    max_pages = config.get('max_pages')
    delay = config.get('delay', 2.0)

    print(f"\n=== {name} sitewide scraping ===")
    print(f"Using queries: {queries}")

    if delay:
        print(f"Waiting {delay:.1f}s before scraping {name}")
        await asyncio.sleep(delay)

    for query in queries:
        if query:
            print(f"  → Trying generic query '{query}'")
        else:
            print(f"  → Trying empty query to fetch full catalog")

        products = await safe_call_scraper(scraper, query, max_pages)
        if products:
            print(f"  {name}: scraped {len(products)} products for query '{query}'")
            added, skipped = save_products(products, name, query or 'sitewide')
            print(f"  {name}: added {added}, skipped {skipped}")
            return added, skipped
        print(f"  {name}: no results for query '{query}'")

    print(f"  {name}: empty query failed; trying generic fallbacks")
    for fallback in GENERIC_FALLBACK_QUERIES:
        products = await safe_call_scraper(scraper, fallback, max_pages)
        if products:
            print(f"  {name}: scraped {len(products)} products for fallback '{fallback}'")
            added, skipped = save_products(products, name, fallback)
            print(f"  {name}: added {added}, skipped {skipped}")
            return added, skipped
        print(f"  {name}: no results for fallback '{fallback}'")

    print(f"  {name}: failed to scrape sitewide data")
    return 0, 0


async def main():
    setup_database()
    start = time.time()
    total_added = 0
    total_skipped = 0

    for config in PLATFORM_CONFIGS:
        added, skipped = await scrape_platform(config)
        total_added += added
        total_skipped += skipped

    print("\n=== Sitewide scraping complete ===")
    print(f"Total added: {total_added}")
    print(f"Total skipped: {total_skipped}")
    print("Cleaning duplicates in the sitewide DB...")
    total_after = clean_duplicates()
    print(f"Final unique products in DB: {total_after}")
    elapsed = time.time() - start
    print(f"Elapsed time: {elapsed/60:.1f} minutes")


if __name__ == '__main__':
    asyncio.run(main())
