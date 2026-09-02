#!/usr/bin/env python3
"""
Standalone Jeevee scraper that collects products and stores them in a local SQLite DB.
"""

import asyncio
import sqlite3
import sys
import os
import time
from datetime import datetime, timezone

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
if ROOT not in sys.path:
    sys.path.insert(0, ROOT)

from scrapers.jeevee.jeevee_scraper import async_scrape_jeevee

DB_PATH = 'jeevee_products.db'
SEARCH_TERMS = [
    'laptop',
    'mobile phone',
    'smartphone',
    'tablet',
    'headphones',
    'speaker',
    'smartwatch',
    'charger',
    'power bank',
    'gaming laptop'
]


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
            scraped_at TEXT
        )
    ''')
    cursor.execute('CREATE UNIQUE INDEX IF NOT EXISTS idx_product_url ON products(product_url)')
    conn.commit()
    conn.close()


def save_products(products, search_term):
    conn = sqlite3.connect(DB_PATH, timeout=30)
    cursor = conn.cursor()
    inserted = 0
    skipped = 0
    now = datetime.now(timezone.utc).isoformat()

    for product in products:
        try:
            cursor.execute('''
                INSERT OR IGNORE INTO products
                (title, price, original_price, discount_percent, image_url, product_url, category, platform, search_term, scraped_at)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            ''', (
                product.get('product_name') or '',
                float(product.get('price')) if product.get('price') is not None else None,
                float(product.get('original_price')) if product.get('original_price') is not None else None,
                float(product.get('discount_percentage')) if product.get('discount_percentage') is not None else None,
                product.get('image_url'),
                product.get('product_url'),
                product.get('platform'),
                product.get('platform'),
                search_term,
                now,
            ))
            if cursor.rowcount > 0:
                inserted += 1
            else:
                skipped += 1
        except Exception:
            skipped += 1
    conn.commit()
    conn.close()
    return inserted, skipped


async def run_scraper():
    setup_database()
    total_inserted = 0
    total_skipped = 0
    start_time = time.time()

    for term in SEARCH_TERMS:
        print(f"\n=== Searching Jeevee for: '{term}' ===")
        products = await async_scrape_jeevee(term, max_pages=2)
        print(f"Found {len(products)} products for term '{term}'")
        inserted, skipped = save_products(products, term)
        total_inserted += inserted
        total_skipped += skipped
        print(f"Inserted: {inserted}, Skipped (duplicates/errors): {skipped}")
        time.sleep(2)

    elapsed = time.time() - start_time
    print('\n=== Scraping complete ===')
    print(f'Total inserted: {total_inserted}')
    print(f'Total skipped: {total_skipped}')
    print(f'Elapsed time: {elapsed:.1f}s')


if __name__ == '__main__':
    asyncio.run(run_scraper())
