#!/usr/bin/env python3
"""
SIMPLE MASTER BUILDER
Fast and reliable addition of products to master database
"""

import asyncio
import sqlite3
import sys
import os
import time
import random
from datetime import datetime, timezone

sys.path.append(os.path.join(os.path.dirname(__file__), '..'))
sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'scrapers'))

from scrapers.daraz.daraz_scraper import sync_scrape_daraz
from scrapers.jeevee.jeevee_scraper import async_scrape_jeevee
from scrapers.neostore.neostore_scraper import async_scrape_neostore

# High-yield search terms
SEARCH_TERMS = [
    "smartphone", "android", "iphone", "samsung", "xiaomi", "oppo", "vivo", "realme",
    "laptop", "notebook", "gaming laptop", "ultrabook", "macbook", "dell", "hp", "lenovo",
    "headphones", "earbuds", "bluetooth", "wireless", "gaming headset", "airpods",
    "smartwatch", "fitness tracker", "apple watch", "garmin", "fitbit", "amazfit",
    "tablet", "ipad", "android tablet", "kindle", "e-reader", "drawing tablet",
    "speaker", "bluetooth speaker", "home theater", "sound system", "jbl", "bose",
    "camera", "dslr", "mirrorless", "action camera", "gopro", "canon", "nikon", "sony",
    "gaming", "playstation", "xbox", "nintendo", "controller", "gaming chair",
    "fashion", "clothing", "shoes", "sneakers", "formal wear", "casual wear",
    "bags", "backpack", "laptop bag", "travel bag", "handbag", "wallet",
    "home", "furniture", "decor", "kitchen", "appliances", "electronics",
    "health", "fitness", "sports", "outdoor", "camping", "hiking"
]

class SimpleMasterBuilder:
    def __init__(self):
        self.db_path = 'master_products.db'
        self.conn = sqlite3.connect(self.db_path)
        self.setup_database()
        
        # Get current stats
        cursor = self.conn.cursor()
        cursor.execute('SELECT COUNT(*) FROM products')
        self.starting_count = cursor.fetchone()[0]
        
        self.new_products = 0
        self.duplicates_prevented = 0
        
    def setup_database(self):
        """Ensure database has proper schema"""
        self.conn.execute('''
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
        self.conn.execute('CREATE INDEX IF NOT EXISTS idx_product_url ON products(product_url)')
        self.conn.commit()
        
    def add_products(self, products, platform_name, search_term):
        """Add products with duplicate checking"""
        if not products:
            return 0, 0
            
        new_count = 0
        duplicate_count = 0
        cursor = self.conn.cursor()
        
        for product in products:
            url = product.get('product_url', '')
            if not url:
                continue
                
            # Check for duplicate
            cursor.execute('SELECT 1 FROM products WHERE product_url = ? LIMIT 1', (url,))
            if cursor.fetchone():
                duplicate_count += 1
                continue
                
            try:
                cursor.execute('''
                    INSERT INTO products 
                    (title, price, original_price, discount_percent, image_url, 
                     store_name, product_url, category, scraped_at, platform, search_term, last_updated)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                ''', (
                    product.get('product_name', 'Unknown'),
                    float(product.get('price', 0)),
                    float(product.get('original_price', 0)) if product.get('original_price') else None,
                    float(product.get('discount_percentage', 0)) if product.get('discount_percentage') else None,
                    product.get('image_url', ''),
                    platform_name,
                    url,
                    search_term,
                    datetime.now(timezone.utc).isoformat(),
                    platform_name,
                    search_term,
                    datetime.now(timezone.utc).isoformat()
                ))
                new_count += 1
                
            except sqlite3.IntegrityError:
                duplicate_count += 1
            except Exception:
                continue
                
        self.conn.commit()
        self.new_products += new_count
        self.duplicates_prevented += duplicate_count
        
        return new_count, duplicate_count
        
    def scrape_daraz(self, term):
        """Daraz scraper wrapper"""
        return sync_scrape_daraz(term, max_pages=3)
        
    async def scrape_platform(self, platform_name, scraper_func, search_term, is_async=True):
        """Generic platform scraper"""
        print(f"🏪 {platform_name}: '{search_term}'")
        
        try:
            if is_async:
                products = await scraper_func(search_term)
            else:
                products = scraper_func(search_term)
                
            if products:
                new_count, duplicates = self.add_products(products, platform_name, search_term)
                print(f"   ✅ {len(products)} found → {new_count} new, {duplicates} duplicates")
                return new_count
            else:
                print(f"   ❌ No products")
                return 0
                
        except Exception as e:
            print(f"   ❌ Error: {str(e)[:50]}...")
            return 0
            
    async def run_building(self):
        """Run the building process"""
        print("🔨 SIMPLE MASTER BUILDER")
        print("=" * 35)
        print(f"📊 Starting products: {self.starting_count:,}")
        print(f"🎯 Adding more unique products...")
        print("=" * 35)
        
        # Platform scrapers
        scrapers = [
            ("Daraz", self.scrape_daraz, False),
            ("Jeevee", async_scrape_jeevee, True),
            ("Neostore", async_scrape_neostore, True)
        ]
        
        for round_num in range(1, 15):  # 15 rounds
            print(f"\\n🔄 ROUND {round_num}")
            
            round_new = 0
            
            # 3 terms per round, rotate through platforms
            for i in range(3):
                term_index = (round_num * 3 + i) % len(SEARCH_TERMS)
                search_term = SEARCH_TERMS[term_index]
                
                platform_name, scraper_func, is_async = scrapers[i % len(scrapers)]
                
                new_count = await self.scrape_platform(platform_name, scraper_func, search_term, is_async)
                round_new += new_count
                
                # Delay between requests
                await asyncio.sleep(random.uniform(1, 2))
            
            # Round summary
            cursor = self.conn.cursor()
            cursor.execute('SELECT COUNT(*) FROM products')
            current_total = cursor.fetchone()[0]
            
            print(f"📊 Round {round_num}: {round_new} new products | Total: {current_total:,}")
            print(f"🎯 50k progress: {(current_total/50000)*100:.1f}%")
            
            if current_total >= 50000:
                print("🎉 50K REACHED!")
                break
                
            if round_new == 0:
                print("⚠️ No new products this round")
        
        # Final stats
        cursor = self.conn.cursor()
        cursor.execute('SELECT COUNT(*) FROM products')
        final_count = cursor.fetchone()[0]
        
        cursor.execute('SELECT platform, COUNT(*) FROM products GROUP BY platform ORDER BY COUNT(*) DESC')
        platforms = cursor.fetchall()
        
        print(f"\\n✅ BUILDING COMPLETE!")
        print(f"📊 Final count: {final_count:,} products")
        print(f"📈 Added: {self.new_products:,} new products")
        print(f"🔒 Prevented: {self.duplicates_prevented:,} duplicates")
        
        print(f"\\n🏪 Platform distribution:")
        for platform, count in platforms:
            percentage = (count / final_count * 100) if final_count > 0 else 0
            print(f"   {platform}: {count:,} ({percentage:.1f}%)")
        
        self.conn.close()

async def main():
    builder = SimpleMasterBuilder()
    try:
        await builder.run_building()
    except KeyboardInterrupt:
        print("\\n⚠️ Building interrupted")
    except Exception as e:
        print(f"\\n❌ Error: {e}")

if __name__ == "__main__":
    asyncio.run(main())