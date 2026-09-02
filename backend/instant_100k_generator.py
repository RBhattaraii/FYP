#!/usr/bin/env python3
"""
CONTINUOUS 100K SCRAPER - REAL DATA
Focus on available non-Daraz scrapers and keep collecting until 100k unique products.
"""

import asyncio
import random
import sqlite3
import sys
import os
import time
from datetime import datetime, timezone

# Ensure scrapers can be imported from backend
ROOT_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.append(ROOT_DIR)
sys.path.append(os.path.join(ROOT_DIR, 'scrapers'))

from scrapers.jeevee.jeevee_scraper import async_scrape_jeevee
from scrapers.oliz.oliz_scraper import async_scrape_oliz
from scrapers.hukut.hukut_scraper import async_scrape_hukut
from scrapers.cgdigital.cgdigital_scraper import async_scrape_cgdigital
from scrapers.neostore.neostore_scraper import async_scrape_neostore
from scrapers.ufonepal.ufonepal_scraper import async_scrape_ufonepal
from scrapers.hardwarepasal.hardwarepasal_scraper import async_scrape_hardwarepasal
from scrapers.better.better_scraper import async_scrape_better

DATABASE_PATH = 'master_products.db'
TARGET_COUNT = 100000
SEARCH_TERMS = []

APP_CATEGORIES = [
    'Electronics', 'Home', 'Beauty', 'Sports', 'Auto', 'Toys', 'Fashion', 'Grocery', 'Books', 'Health'
]

SEARCH_TERMS_BY_CATEGORY = {
    'Electronics': [
        'laptop', 'mobile', 'smartphone', 'computer', 'tablet', 'headphone', 'earphone', 'speaker',
        'monitor', 'keyboard', 'mouse', 'printer', 'camera', 'smartwatch', 'router', 'ssd', 'hard drive'
    ],
    'Home': [
        'sofa', 'bed', 'mattress', 'chair', 'table', 'lamp', 'fan', 'vacuum', 'refrigerator', 'microwave',
        'air conditioner', 'cooler', 'heater', 'rice cooker', 'blender', 'kettle', 'toaster', 'dishwasher',
        'kitchen appliance', 'home appliance', 'storage container'
    ],
    'Beauty': [
        'shampoo', 'conditioner', 'soap', 'cream', 'lotion', 'perfume', 'makeup', 'lipstick', 'foundation',
        'mascara', 'skincare', 'haircare', 'body wash', 'deodorant', 'face wash', 'serum'
    ],
    'Sports': [
        'sports shoes', 'football', 'cricket bat', 'badminton racket', 'yoga mat', 'gym equipment',
        'dumbbell', 'resistance band', 'exercise bike', 'treadmill', 'fitness tracker', 'sports wear'
    ],
    'Auto': [
        'car accessories', 'bike accessories', 'helmet', 'car charger', 'car cover', 'seat cover',
        'air freshener', 'car vacuum', 'dash cam', 'car mat', 'bike lock', 'car cleaner', 'tool kit'
    ],
    'Toys': [
        'toy', 'soft toy', 'teddy bear', 'doll', 'board game', 'puzzle', 'remote control car', 'lego',
        'building blocks', 'educational toy', 'baby toy', 'rc car', 'drone', 'game controller'
    ],
    'Fashion': [
        'shirt', 't-shirt', 'jeans', 'dress', 'jacket', 'shoes', 'sneakers', 'sandals', 'bag', 'backpack',
        'handbag', 'wallet', 'watch', 'sunglasses', 'belt', 'hoodie', 'coat', 'boots'
    ],
    'Grocery': [
        'water bottle', 'thermos', 'storage container', 'spice box', 'lunch box', 'tiffin box',
        'glass set', 'cup set', 'plate set', 'snacks', 'tea', 'coffee', 'cooking oil', 'rice', 'pasta'
    ],
    'Books': [
        'book', 'novel', 'textbook', 'story book', 'children book', 'reference book', 'notebook',
        'diary', 'pen', 'pencil', 'stationery', 'calculator', 'drawing book'
    ],
    'Health': [
        'vitamin', 'supplement', 'first aid kit', 'thermometer', 'massager', 'sleep mask', 'bandage',
        'toothpaste', 'toothbrush', 'mouthwash', 'hand sanitizer', 'personal care', 'medical supplies'
    ]
}

SEARCH_TERMS_BY_PLATFORM = {
    # Jeevee: general marketplace — keep broad but focused on common categories
    'Jeevee': SEARCH_TERMS_BY_CATEGORY['Electronics'] + SEARCH_TERMS_BY_CATEGORY['Home'] + SEARCH_TERMS_BY_CATEGORY['Fashion'] + SEARCH_TERMS_BY_CATEGORY['Toys'] + SEARCH_TERMS_BY_CATEGORY['Books'] + SEARCH_TERMS_BY_CATEGORY['Health'],
    # Oliz: primarily electronics / mobile store
    'Oliz': SEARCH_TERMS_BY_CATEGORY['Electronics'],
    # Hukut: electronics and appliances
    'Hukut': SEARCH_TERMS_BY_CATEGORY['Electronics'] + SEARCH_TERMS_BY_CATEGORY['Home'] + SEARCH_TERMS_BY_CATEGORY['Auto'],
    # CGDigital: consumer electronics and accessories
    'CGDigital': SEARCH_TERMS_BY_CATEGORY['Electronics'] + SEARCH_TERMS_BY_CATEGORY['Home'],
    # NeoStore: electronics and home appliances
    'NeoStore': SEARCH_TERMS_BY_CATEGORY['Electronics'] + SEARCH_TERMS_BY_CATEGORY['Home'],
    # UfoNepal: telecom/mobile focused — phones, accessories, cases
    'UfoNepal': SEARCH_TERMS_BY_CATEGORY['Electronics'] + SEARCH_TERMS_BY_CATEGORY['Fashion'],
    # HardwarePasal: hardware, tools, auto accessories
    'HardwarePasal': SEARCH_TERMS_BY_CATEGORY['Auto'] + SEARCH_TERMS_BY_CATEGORY['Home'] + SEARCH_TERMS_BY_CATEGORY['Electronics'],
    # Better Appliances: home appliances and electronics
    'Better': SEARCH_TERMS_BY_CATEGORY['Home'] + SEARCH_TERMS_BY_CATEGORY['Electronics']
}

PLATFORM_CATEGORY_MAP = {
    'Jeevee': ['Electronics', 'Home', 'Beauty', 'Sports', 'Auto', 'Toys', 'Fashion', 'Books', 'Health'],
    'Oliz': ['Electronics', 'Home', 'Beauty', 'Fashion', 'Toys', 'Books', 'Health'],
    'Hukut': ['Electronics', 'Home', 'Auto', 'Books', 'Health'],
    'CGDigital': ['Electronics', 'Home', 'Books', 'Health'],
    'NeoStore': ['Electronics', 'Home', 'Books', 'Health'],
    'UfoNepal': ['Electronics', 'Home', 'Beauty', 'Fashion', 'Toys', 'Health', 'Grocery'],
    'HardwarePasal': ['Electronics', 'Home', 'Auto', 'Books', 'Health'],
    'Better': ['Home', 'Electronics', 'Health']
}

PLATFORM_CONFIGS = [
    {
        'name': 'Jeevee',
        'scraper': async_scrape_jeevee,
        'max_pages': 6,
        'priority': 1,
        'platform_label': 'jeevee',
        'delay': 2.5
    },
    {
        'name': 'Oliz',
        'scraper': async_scrape_oliz,
        'max_pages': 1,
        'priority': 1,
        'platform_label': 'oliz_store',
        'delay': 2.0
    },
    {
        'name': 'Hukut',
        'scraper': async_scrape_hukut,
        'max_pages': 10,
        'priority': 1,
        'platform_label': 'hukut_store',
        'delay': 3.0
    },
    {
        'name': 'CGDigital',
        'scraper': async_scrape_cgdigital,
        'max_pages': 1,
        'priority': 1,
        'platform_label': 'cgdigital',
        'delay': 2.5
    },
    {
        'name': 'NeoStore',
        'scraper': async_scrape_neostore,
        'max_pages': 1,
        'priority': 2,
        'platform_label': 'neostore',
        'delay': 2.0
    },
    {
        'name': 'UfoNepal',
        'scraper': async_scrape_ufonepal,
        'max_pages': 1,
        'priority': 2,
        'platform_label': 'ufonepal',
        'delay': 2.5
    },
    {
        'name': 'HardwarePasal',
        'scraper': async_scrape_hardwarepasal,
        'max_pages': 1,
        'priority': 2,
        'platform_label': 'hardwarepasal',
        'delay': 3.0
    },
    {
        'name': 'Better',
        'scraper': async_scrape_better,
        'max_pages': 1,
        'priority': 3,
        'platform_label': 'better',
        'delay': 2.0
    }
]

VALID_PLATFORM_NAMES = [config['name'] for config in PLATFORM_CONFIGS]

SELECTED_PLATFORM = None
if len(sys.argv) > 1:
    SELECTED_PLATFORM = sys.argv[1].strip()
    if SELECTED_PLATFORM.lower() == 'daraz':
        print("⚠️ Daraz is excluded by default. Use a non-Daraz platform.")
        sys.exit(1)

if SELECTED_PLATFORM:
    PLATFORM_CONFIGS = [config for config in PLATFORM_CONFIGS if config['name'].lower() == SELECTED_PLATFORM.lower()]
    if not PLATFORM_CONFIGS:
        print(f"⚠️ Unknown platform '{SELECTED_PLATFORM}'. Valid choices:")
        print(', '.join(VALID_PLATFORM_NAMES))
        sys.exit(1)


class Continuous100kScraper:
    def __init__(self):
        self.conn = None
        self.cursor = None
        self.round = 0
        self.term_queues = {}
        self._setup_database()
        self._initialize_term_queues()

    def _setup_database(self):
        self.conn = sqlite3.connect(DATABASE_PATH, timeout=30)
        self.cursor = self.conn.cursor()
        self.cursor.execute('''
            CREATE TABLE IF NOT EXISTS products (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                title TEXT NOT NULL,
                price REAL,
                original_price REAL,
                discount_percent REAL,
                image_url TEXT,
                store_name TEXT,
                product_url TEXT UNIQUE,
                category TEXT,
                scraped_at TEXT,
                platform TEXT,
                search_term TEXT,
                last_updated TEXT
            )
        ''')
        self.cursor.execute('CREATE INDEX IF NOT EXISTS idx_product_url ON products(product_url)')
        self.conn.commit()

    def get_current_count(self):
        self.cursor.execute('SELECT COUNT(*) FROM products')
        return self.cursor.fetchone()[0]

    def _build_term_pool(self, platform_name):
        term_pool = SEARCH_TERMS_BY_PLATFORM.get(platform_name, [])
        if term_pool:
            return list(dict.fromkeys(term_pool))

        pool = []
        for category in PLATFORM_CATEGORY_MAP.get(platform_name, []):
            pool.extend(SEARCH_TERMS_BY_CATEGORY.get(category, []))
        return list(dict.fromkeys(pool))

    def _initialize_term_queues(self):
        for config in PLATFORM_CONFIGS:
            name = config['name']
            term_pool = self._build_term_pool(name)
            random.shuffle(term_pool)
            self.term_queues[name] = term_pool

    def _next_search_term(self, platform_name):
        queue = self.term_queues.get(platform_name, [])
        if not queue:
            queue = self._build_term_pool(platform_name)
            random.shuffle(queue)
            self.term_queues[platform_name] = queue

        if not queue:
            return random.choice([
                'laptop', 'mobile', 'phone', 'smartphone', 'camera', 'tv', 'speaker',
                'headphone', 'tablet', 'printer', 'refrigerator', 'fan', 'watch', 'shoes'
            ])

        return queue.pop()

    def save_products(self, products, platform_name, search_term):
        if not products:
            return 0, 0

        added = 0
        skipped = 0
        now = datetime.now(timezone.utc).isoformat()

        def normalize_category(raw_category, search_term):
            if not raw_category:
                return None
            cat = raw_category.strip().lower()
            if 'elect' in cat or 'phone' in cat or 'tablet' in cat or 'camera' in cat or 'watch' in cat or 'headphone' in cat or 'speaker' in cat:
                return 'Electronics'
            if 'home' in cat or 'kitchen' in cat or 'sofa' in cat or 'mattress' in cat or 'refrigerator' in cat or 'microwave' in cat or 'vacuum' in cat or 'blender' in cat or 'heater' in cat or 'fan' in cat:
                return 'Home'
            if 'beauty' in cat or 'makeup' in cat or 'skincare' in cat or 'hair' in cat or 'lotion' in cat or 'perfume' in cat or 'cosmetic' in cat or 'soap' in cat or 'shampoo' in cat:
                return 'Beauty'
            if 'sport' in cat or 'fitness' in cat or 'gym' in cat or 'yoga' in cat or 'ball' in cat or 'cricket' in cat or 'badminton' in cat or 'football' in cat or 'running' in cat:
                return 'Sports'
            if 'auto' in cat or 'car' in cat or 'bike' in cat or 'motor' in cat or 'helmet' in cat or 'seat' in cat or 'dashboard' in cat or 'tire' in cat or 'vehicle' in cat:
                return 'Auto'
            if 'toy' in cat or 'game' in cat or 'lego' in cat or 'doll' in cat or 'puzzle' in cat or 'board' in cat:
                return 'Toys'
            if 'fashion' in cat or 'clothing' in cat or 'shirt' in cat or 'jeans' in cat or 'dress' in cat or 'shoes' in cat or 'bag' in cat or 'wallet' in cat or 'sunglass' in cat:
                return 'Fashion'
            if 'book' in cat or 'stationery' in cat or 'pen' in cat or 'notebook' in cat or 'diary' in cat or 'paper' in cat:
                return 'Books'
            if 'health' in cat or 'medicine' in cat or 'supplement' in cat or 'vitamin' in cat or 'dental' in cat or 'first aid' in cat or 'thermometer' in cat:
                return 'Health'
            if 'grocery' in cat or 'tea' in cat or 'coffee' in cat or 'rice' in cat or 'oil' in cat or 'snack' in cat or 'food' in cat or 'bottle' in cat or 'kitchen' in cat:
                return 'Grocery'
            # fallback based on search_term category mappings
            for category, terms in SEARCH_TERMS_BY_CATEGORY.items():
                normalized_search = search_term.strip().lower()
                if normalized_search in [t.lower() for t in terms]:
                    return category
            return None

        for raw in products:
            product_url = raw.get('product_url') or raw.get('url') or ''
            title = raw.get('product_name') or raw.get('title') or 'Unknown Product'
            price = raw.get('price')
            original_price = raw.get('original_price')
            discount_percent = raw.get('discount_percentage') or raw.get('discount_percent')
            image_url = raw.get('image_url') or raw.get('image') or ''
            raw_category = raw.get('category') or raw.get('search_term') or ''
            category = normalize_category(raw_category, search_term) or 'Electronics'

            if not product_url or len(product_url.strip()) == 0:
                skipped += 1
                continue

            try:
                self.cursor.execute('''
                    INSERT OR IGNORE INTO products
                    (title, price, original_price, discount_percent, image_url, store_name, product_url,
                     category, scraped_at, platform, search_term, last_updated)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                ''', (
                    title[:200],
                    float(price) if price is not None else None,
                    float(original_price) if original_price is not None else None,
                    float(discount_percent) if discount_percent is not None else None,
                    image_url,
                    platform_name,
                    product_url,
                    category,
                    raw.get('scraped_at') or now,
                    platform_name,
                    search_term,
                    now
                ))
                if self.cursor.rowcount > 0:
                    added += 1
                else:
                    skipped += 1
            except Exception:
                skipped += 1

        self.conn.commit()
        return added, skipped

    async def _scrape_platform(self, config, search_term):
        platform_name = config['name']
        scraper = config['scraper']
        max_pages = config['max_pages']

        try:
            # Rate-limit non-Daraz platforms to be gentle/slow
            if platform_name != 'Daraz':
                delay = config.get('delay') if isinstance(config.get('delay'), (int, float)) else random.uniform(1.5, 3.5)
                print(f"   💤 {platform_name}: sleeping {delay:.2f}s before scraping '{search_term}'")
                await asyncio.sleep(delay)

            if platform_name in ('Daraz', 'Oliz'):
                products = await scraper(search_term, max_pages=max_pages)
            else:
                products = await scraper(search_term)

            if not products:
                print(f"   ❌ {platform_name}: no products for '{search_term}'")
                return 0, 0, platform_name

            # Filter out products that already exist in the DB by product_url
            urls = [p.get('product_url') for p in products if p.get('product_url')]
            if urls:
                placeholders = ','.join(['?'] * len(urls))
                try:
                    self.cursor.execute(f"SELECT product_url FROM products WHERE product_url IN ({placeholders})", tuple(urls))
                    existing = set(r[0] for r in self.cursor.fetchall())
                except Exception:
                    existing = set()

                if existing:
                    before = len(products)
                    products = [p for p in products if p.get('product_url') not in existing]
                    filtered = before - len(products)
                    if filtered > 0:
                        print(f"   ℹ️ {platform_name}: filtered {filtered} products already in DB")

            if not products:
                print(f"   ❌ {platform_name}: all scraped products already exist for '{search_term}'")
                return 0, 0, platform_name

            added, skipped = self.save_products(products, platform_name, search_term)
            print(f"   ✅ {platform_name}: searched '{search_term}' → found {len(products)}, added {added}, skipped {skipped}")
            return added, skipped, platform_name

        except Exception as e:
            print(f"   ❌ {platform_name}: scrape error for '{search_term}': {e}")
            return 0, 0, platform_name

    async def run(self):
        print("\n🚀 CONTINUOUS 100K SCRAPER STARTED")
        print("🔒 Using real scrapers and unique product URLs")
        print("🎯 Target: 100,000 unique products")
        print("⚠️ Prioritizing non-Daraz scrapers first")
        print("\n")

        start_time = time.time()
        prev_count = self.get_current_count()
        print(f"📊 Starting count: {prev_count:,}")

        while prev_count < TARGET_COUNT:
            self.round += 1
            tasks = []

            # Prioritize platforms by non-Daraz first
            sorted_configs = sorted(PLATFORM_CONFIGS, key=lambda c: c['priority'])
            for config in sorted_configs:
                platform_name = config['name']
                term = self._next_search_term(platform_name)
                tasks.append(self._scrape_platform(config, term))

            results = await asyncio.gather(*tasks, return_exceptions=True)
            added_total = 0
            skipped_total = 0

            for result in results:
                if isinstance(result, tuple):
                    added_total += result[0]
                    skipped_total += result[1]

            current_count = self.get_current_count()
            progress = (current_count / TARGET_COUNT) * 100
            elapsed = time.time() - start_time
            rate = current_count / elapsed if elapsed > 0 else 0

            print(f"\n🔄 ROUND {self.round} COMPLETE")
            print(f"   Added this round: {added_total:,}")
            print(f"   Skipped duplicates/invalid: {skipped_total:,}")
            print(f"   Total unique products: {current_count:,} ({progress:.2f}%)")
            print(f"   Elapsed: {int(elapsed)}s | Average rate: {rate:.2f} products/s")
            print(f"   Target remaining: {max(0, TARGET_COUNT - current_count):,}")
            print("\n")

            if current_count == prev_count:
                print("⚠️ No new unique products this round. Continuing with different terms.")
            prev_count = current_count

            if current_count >= TARGET_COUNT:
                break

            await asyncio.sleep(0.5)

        total_elapsed = time.time() - start_time
        if prev_count >= TARGET_COUNT:
            print("\n🎉 100K TARGET ACHIEVED!")
        else:
            print("\n⚠️ 100K TARGET NOT REACHED")
        print(f"📊 Final count: {prev_count:,}")
        print(f"⏱️ Total time: {total_elapsed/60:.1f} minutes")

        self._print_platform_breakdown()

    def _print_platform_breakdown(self):
        self.cursor.execute('SELECT platform, COUNT(*) FROM products GROUP BY platform ORDER BY COUNT(*) DESC')
        rows = self.cursor.fetchall()
        print("\n🏪 Platform distribution:")
        total = self.get_current_count()
        for platform, count in rows:
            pct = (count / total * 100) if total else 0
            print(f"   {platform}: {count:,} ({pct:.1f}%)")


if __name__ == '__main__':
    scraper = Continuous100kScraper()
    asyncio.run(scraper.run())
