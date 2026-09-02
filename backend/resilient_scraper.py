#!/usr/bin/env python3
"""
RESILIENT MULTI-PLATFORM SCRAPER
Switches platforms when rate-limited, implements delays, and uses all available scrapers
"""

import asyncio
import sqlite3
import sys
import os
import time
import random
from datetime import datetime, timezone

# Add paths for imports
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))
sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'scrapers'))

# Import ALL available scrapers
from scrapers.daraz.daraz_scraper import sync_scrape_daraz, async_scrape_daraz
from scrapers.cgdigital.cgdigital_scraper import async_scrape_cgdigital

# Core search terms that work across platforms
CORE_SEARCH_TERMS = [
    # Electronics (most universal)
    "laptop", "mobile", "phone", "tablet", "computer", "headphone", "speaker", 
    "mouse", "keyboard", "monitor", "camera", "charger", "cable", "power bank",
    
    # Fashion basics
    "shirt", "shoes", "bag", "watch", "belt", "jeans", "dress", "jacket",
    
    # Home essentials  
    "kitchen", "home", "chair", "table", "lamp", "bottle", "plate", "cup",
    
    # Health & beauty basics
    "cream", "shampoo", "soap", "toothbrush", "perfume", "makeup",
    
    # General high-yield terms
    "accessories", "tools", "parts", "cover", "case", "stand", "holder"
]

class ResilientScraper:
    def __init__(self):
        self.db_path = 'resilient_products.db'
        self.setup_database()
        self.failed_attempts = {}
        
    def setup_database(self):
        """Setup resilient scraper database"""
        self.conn = sqlite3.connect(self.db_path)
        self.conn.execute('''
            CREATE TABLE IF NOT EXISTS products (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                title TEXT,
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
                scraper_source TEXT
            )
        ''')
        self.conn.commit()
        print(f"✅ Resilient database ready: {self.db_path}")

    def store_products_batch(self, products, store_name, search_term, scraper_name):
        """Store products with source tracking"""
        if not products:
            return 0
            
        stored = 0
        cursor = self.conn.cursor()
        
        for product in products:
            try:
                cursor.execute('''
                    INSERT OR REPLACE INTO products 
                    (title, price, original_price, discount_percent, image_url, 
                     store_name, product_url, category, scraped_at, platform, search_term, scraper_source)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                ''', (
                    product.get('product_name', 'Unknown Product'),
                    float(product.get('price', 0)),
                    float(product.get('original_price', 0)) if product.get('original_price') else None,
                    float(product.get('discount_percentage', 0)) if product.get('discount_percentage') else None,
                    product.get('image_url', ''),
                    store_name,
                    product.get('product_url', ''),
                    search_term,
                    datetime.now(timezone.utc).isoformat(),
                    product.get('platform', store_name.lower()),
                    search_term,
                    scraper_name
                ))
                stored += 1
            except Exception as e:
                continue
                
        self.conn.commit()
        return stored

    async def try_daraz_careful(self, search_term):
        """Try Daraz with careful rate limiting"""
        print(f"📱 DARAZ: {search_term}")
        
        try:
            # Use fewer pages to avoid rate limiting
            products = sync_scrape_daraz(search_term, max_pages=3)
            
            if products and len(products) > 0:
                stored = self.store_products_batch(products, "Daraz", search_term, "daraz_careful")
                print(f"  ✅ {len(products)} found → {stored} stored")
                # Add success delay
                await asyncio.sleep(2)
                return stored
            else:
                print(f"  ⚠️  No products or rate limited")
                self.failed_attempts['daraz'] = self.failed_attempts.get('daraz', 0) + 1
                return 0
                
        except Exception as e:
            print(f"  ❌ Daraz failed: {e}")
            self.failed_attempts['daraz'] = self.failed_attempts.get('daraz', 0) + 1
            return 0

    async def try_cgdigital(self, search_term):
        """Try CGDigital scraper"""
        print(f"💻 CGDIGITAL: {search_term}")
        
        try:
            products = await async_scrape_cgdigital(search_term)
            
            if products and len(products) > 0:
                stored = self.store_products_batch(products, "CGDigital", search_term, "cgdigital")
                print(f"  ✅ {len(products)} found → {stored} stored")
                await asyncio.sleep(1)
                return stored
            else:
                print(f"  ⚠️  No products")
                return 0
                
        except Exception as e:
            print(f"  ❌ CGDigital failed: {e}")
            return 0

    async def scrape_term_resilient(self, search_term, attempt=1):
        """Scrape a term using multiple platforms as fallbacks"""
        max_attempts = 2
        total_stored = 0
        
        # Try different platforms based on their success rate
        platforms_to_try = []
        
        # Prioritize based on failure count
        daraz_failures = self.failed_attempts.get('daraz', 0)
        
        if daraz_failures < 5:  # Still try Daraz if not too many failures
            platforms_to_try.append(self.try_daraz_careful)
        
        # Always try CGDigital as backup
        platforms_to_try.append(self.try_cgdigital)
        
        # Try platforms until we get products or exhaust options
        for platform_func in platforms_to_try:
            stored = await platform_func(search_term)
            total_stored += stored
            
            if stored > 0:
                break  # Success, move to next term
                
            # Random delay between platform attempts
            await asyncio.sleep(random.uniform(1, 3))
        
        return total_stored

    async def run_resilient_scraping(self):
        """Run resilient scraping across platforms"""
        print("🛡️ RESILIENT MULTI-PLATFORM SCRAPER STARTING")
        print("=" * 60)
        print("🔄 Auto-switches platforms when rate-limited")
        print("💪 Uses Daraz, CGDigital, and intelligent delays")
        print("=" * 60)
        
        start_time = time.time()
        total_products = 0
        
        # Process terms with intelligent delays
        for i, search_term in enumerate(CORE_SEARCH_TERMS, 1):
            print(f"\n🔍 [{i}/{len(CORE_SEARCH_TERMS)}] Searching: {search_term}")
            
            stored = await self.scrape_term_resilient(search_term)
            total_products += stored
            
            print(f"  📊 Term result: {stored} products | Running total: {total_products:,}")
            
            # Adaptive delays based on failures
            if self.failed_attempts.get('daraz', 0) > 3:
                delay = random.uniform(5, 10)  # Longer delays if many failures
            else:
                delay = random.uniform(2, 4)   # Normal delays
                
            print(f"  ⏸️  Waiting {delay:.1f}s before next term...")
            await asyncio.sleep(delay)
            
            # Progress update every 5 terms
            if i % 5 == 0:
                print(f"\n📈 PROGRESS UPDATE: {total_products:,} products after {i} terms")
                
        # Final statistics
        elapsed_time = time.time() - start_time
        
        print("\n" + "=" * 60)
        print("🛡️ RESILIENT SCRAPING COMPLETE!")
        print(f"⏱️  Time: {elapsed_time/60:.1f} minutes")
        print(f"📊 Total products: {total_products:,}")
        print(f"🚀 Rate: {total_products/(elapsed_time/60):.0f} products/minute")
        
        # Show failure stats
        print(f"\n📈 PLATFORM PERFORMANCE:")
        print(f"  • Daraz failures: {self.failed_attempts.get('daraz', 0)}")
        print(f"  • Total terms processed: {len(CORE_SEARCH_TERMS)}")
        
        # Database stats
        cursor = self.conn.cursor()
        cursor.execute("SELECT COUNT(*) FROM products")
        db_total = cursor.fetchone()[0]
        
        # Get platform breakdown
        cursor.execute("SELECT scraper_source, COUNT(*) FROM products GROUP BY scraper_source")
        platform_stats = cursor.fetchall()
        
        print(f"\n💾 DATABASE STATS:")
        print(f"  • Total stored: {db_total:,} products")
        for platform, count in platform_stats:
            print(f"  • {platform}: {count:,} products")
        
        file_size = os.path.getsize(self.db_path) / (1024 * 1024)
        print(f"  • File size: {file_size:.1f} MB")
        
        print("\n✅ Resilient scraper completed successfully!")

    def cleanup(self):
        """Close database connection"""
        if hasattr(self, 'conn'):
            self.conn.close()

async def main():
    """Main resilient scraper execution"""
    scraper = ResilientScraper()
    
    try:
        await scraper.run_resilient_scraping()
    except KeyboardInterrupt:
        print("\n⚠️  Resilient scraping interrupted")
    except Exception as e:
        print(f"\n❌ Resilient scraper error: {e}")
    finally:
        scraper.cleanup()

if __name__ == "__main__":
    asyncio.run(main())