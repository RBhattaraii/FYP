#!/usr/bin/env python3
"""
MASTER DEDUPLICATED SCRAPER
Single source of truth - no duplicate products
Targets 50k+ unique products across all platforms
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

# Import ALL working scrapers
from scrapers.daraz.daraz_scraper import sync_scrape_daraz
from scrapers.better.better_scraper import async_scrape_better
from scrapers.hardwarepasal.hardwarepasal_scraper import async_scrape_hardwarepasal
from scrapers.hukut.hukut_scraper import async_scrape_hukut
from scrapers.jeevee.jeevee_scraper import async_scrape_jeevee
from scrapers.neostore.neostore_scraper import async_scrape_neostore
from scrapers.oliz.oliz_scraper import async_scrape_oliz

# COMPREHENSIVE SEARCH TERMS - optimized for maximum coverage
SEARCH_TERMS = [
    # Electronics - High yield terms
    "laptop", "phone", "mobile", "smartphone", "computer", "tablet", "headphone", "earphone", 
    "speaker", "bluetooth", "wireless", "charger", "cable", "power bank", "mouse", "keyboard",
    "samsung", "apple", "xiaomi", "oppo", "vivo", "realme", "oneplus", "huawei", "nokia",
    "dell", "hp", "lenovo", "acer", "asus", "msi", "macbook", "iphone", "android",
    
    # Fashion & Accessories
    "shirt", "t-shirt", "jeans", "pants", "dress", "jacket", "hoodie", "sweater", "shoes", 
    "sneakers", "sandals", "boot", "bag", "backpack", "handbag", "purse", "wallet", "belt",
    "watch", "smartwatch", "sunglasses", "glasses", "cap", "hat", "ring", "necklace",
    
    # Home & Kitchen
    "kitchen", "home", "chair", "table", "sofa", "bed", "mattress", "pillow", "blanket",
    "lamp", "light", "mirror", "clock", "fan", "heater", "ac", "air conditioner",
    "refrigerator", "fridge", "microwave", "oven", "blender", "mixer", "rice cooker",
    "pressure cooker", "kettle", "toaster", "iron", "vacuum", "washing machine",
    
    # Health & Beauty
    "cream", "lotion", "moisturizer", "serum", "facewash", "cleanser", "toner", "mask",
    "shampoo", "conditioner", "hair oil", "soap", "bodywash", "perfume", "deodorant",
    "makeup", "lipstick", "foundation", "concealer", "mascara", "eyeliner", "eyeshadow",
    "toothbrush", "toothpaste", "mouthwash", "vitamins", "supplements",
    
    # Sports & Fitness
    "sports", "fitness", "gym", "exercise", "yoga", "workout", "running", "jogging",
    "cricket", "football", "soccer", "basketball", "badminton", "tennis", "cycling",
    "swimming", "dumbbell", "weights", "treadmill", "bike", "bicycle",
    
    # Books & Stationery
    "book", "novel", "textbook", "guide", "dictionary", "notebook", "diary", "journal",
    "pen", "pencil", "marker", "highlighter", "eraser", "ruler", "calculator", "stapler",
    
    # Baby & Kids
    "baby", "infant", "toddler", "kids", "children", "toy", "game", "puzzle", "doll",
    "teddy", "stroller", "pram", "car seat", "high chair", "baby food", "diaper",
    
    # Automotive
    "car", "bike", "motorcycle", "scooter", "helmet", "gloves", "jacket", "cover",
    "accessories", "parts", "tools", "battery", "tire", "oil", "polish",
    
    # General high-yield terms
    "accessories", "case", "cover", "stand", "holder", "mount", "adapter", "converter",
    "storage", "organizer", "box", "container", "set", "kit", "pack", "bundle"
]

class MasterDeduplicatedScraper:
    def __init__(self):
        self.db_path = 'master_products.db'
        self.setup_database()
        self.platform_stats = {}
        self.total_products = 0
        self.target_total = 50000
        
        # Working scrapers with their async status
        self.platforms = {
            'Daraz': {'scraper': self.scrape_daraz, 'async': False, 'priority': 1},
            'Better': {'scraper': async_scrape_better, 'async': True, 'priority': 3}, 
            'HardwarePasal': {'scraper': async_scrape_hardwarepasal, 'async': True, 'priority': 2},
            'Hukut': {'scraper': async_scrape_hukut, 'async': True, 'priority': 2},
            'Jeevee': {'scraper': async_scrape_jeevee, 'async': True, 'priority': 2},
            'Neostore': {'scraper': async_scrape_neostore, 'async': True, 'priority': 3},
            'Oliz': {'scraper': async_scrape_oliz, 'async': True, 'priority': 2}
        }
        
        # Initialize platform stats
        for platform in self.platforms.keys():
            self.platform_stats[platform] = 0
            
    def setup_database(self):
        """Setup master database with UNIQUE constraint on URLs"""
        self.conn = sqlite3.connect(self.db_path)
        self.conn.execute('''
            CREATE TABLE IF NOT EXISTS products (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                title TEXT NOT NULL,
                price REAL,
                original_price REAL,
                discount_percent REAL,
                image_url TEXT,
                store_name TEXT NOT NULL,
                product_url TEXT UNIQUE NOT NULL,  -- UNIQUE prevents duplicates
                category TEXT,
                scraped_at TEXT,
                platform TEXT NOT NULL,
                search_term TEXT,
                master_batch TEXT
            )
        ''')
        
        # Create index for faster duplicate checking
        self.conn.execute('''
            CREATE INDEX IF NOT EXISTS idx_product_url ON products(product_url)
        ''')
        
        self.conn.commit()
        
        # Get current counts
        cursor = self.conn.cursor()
        cursor.execute('SELECT COUNT(*) FROM products')
        self.total_products = cursor.fetchone()[0]
        
        # Get platform breakdown
        cursor.execute('SELECT platform, COUNT(*) FROM products GROUP BY platform')
        for platform, count in cursor.fetchall():
            if platform in self.platform_stats:
                self.platform_stats[platform] = count
        
        print(f"✅ Master database ready: {self.db_path}")
        print(f"📊 Current products: {self.total_products:,}")
        
        if self.total_products > 0:
            print("🏪 Current platform distribution:")
            for platform, count in self.platform_stats.items():
                if count > 0:
                    percentage = (count / self.total_products) * 100
                    print(f"   • {platform}: {count:,} ({percentage:.1f}%)")

    def scrape_daraz(self, search_term):
        """Wrapper for Daraz sync scraper"""
        return sync_scrape_daraz(search_term, max_pages=3)

    def store_products_deduplicated(self, products, platform_name, search_term, batch_id):
        """Store products with automatic deduplication"""
        if not products:
            return 0, 0
            
        stored = 0
        duplicates = 0
        cursor = self.conn.cursor()
        
        for product in products:
            try:
                product_url = product.get('product_url', '')
                if not product_url:
                    continue  # Skip products without URLs
                    
                # Try to insert - will fail if URL already exists (UNIQUE constraint)
                cursor.execute('''
                    INSERT INTO products 
                    (title, price, original_price, discount_percent, image_url, 
                     store_name, product_url, category, scraped_at, platform, search_term, master_batch)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                ''', (
                    product.get('product_name', 'Unknown Product'),
                    float(product.get('price', 0)),
                    float(product.get('original_price', 0)) if product.get('original_price') else None,
                    float(product.get('discount_percentage', 0)) if product.get('discount_percentage') else None,
                    product.get('image_url', ''),
                    platform_name,
                    product_url,
                    search_term,
                    datetime.now(timezone.utc).isoformat(),
                    platform_name,
                    search_term,
                    batch_id
                ))
                stored += 1
                
            except sqlite3.IntegrityError:
                # This product URL already exists - it's a duplicate
                duplicates += 1
            except Exception as e:
                # Other errors (invalid data, etc.)
                continue
                
        self.conn.commit()
        
        # Update stats
        self.platform_stats[platform_name] += stored
        self.total_products += stored
        
        return stored, duplicates

    async def scrape_platform_deduplicated(self, platform_name, search_term, batch_id):
        """Scrape from platform with deduplication"""
        platform_info = self.platforms[platform_name]
        
        print(f"🏪 {platform_name}: {search_term}")
        
        try:
            if platform_info['async']:
                products = await platform_info['scraper'](search_term)
            else:
                products = platform_info['scraper'](search_term)
            
            if products and len(products) > 0:
                stored, duplicates = self.store_products_deduplicated(products, platform_name, search_term, batch_id)
                
                if stored > 0 or duplicates > 0:
                    print(f"  ✅ {len(products)} found → {stored} NEW, {duplicates} duplicates")
                    print(f"  📊 Platform total: {self.platform_stats[platform_name]:,} | Grand total: {self.total_products:,}")
                else:
                    print(f"  ⚠️  {len(products)} found but no valid URLs")
                
                return stored
            else:
                print(f"  ❌ No products found")
                return 0
                
        except Exception as e:
            print(f"  ❌ Error: {str(e)[:60]}...")
            return 0

    async def run_master_scraping(self):
        """Execute master scraping with deduplication"""
        print("🎯 MASTER DEDUPLICATED SCRAPER")
        print("=" * 60)
        print("✅ DUPLICATE PREVENTION: URLs are unique")
        print("🎯 TARGET: 50,000+ unique products")
        print("🏪 PLATFORMS: 7 working Nepali e-commerce sites")
        print("=" * 60)
        
        start_time = time.time()
        batch_id = f"master_{int(time.time())}"
        
        # Continue until we reach target
        round_num = 1
        
        while self.total_products < self.target_total:
            print(f"\n🔄 ROUND {round_num}: Master scraping")
            print(f"📊 Current progress: {self.total_products:,}/{self.target_total:,} ({(self.total_products/self.target_total)*100:.1f}%)")
            
            round_stored = 0
            
            # Cycle through platforms by priority and need
            platform_order = sorted(self.platforms.keys(), 
                                  key=lambda p: (self.platform_stats[p], self.platforms[p]['priority']))
            
            # Use different search terms each round
            term_start = (round_num - 1) * len(platform_order)
            
            for i, platform_name in enumerate(platform_order):
                term_index = (term_start + i) % len(SEARCH_TERMS)
                search_term = SEARCH_TERMS[term_index]
                
                stored = await self.scrape_platform_deduplicated(platform_name, search_term, batch_id)
                round_stored += stored
                
                # Small delay between platforms
                await asyncio.sleep(random.uniform(2, 5))
                
                # Check if we've reached target
                if self.total_products >= self.target_total:
                    print(f"\n🎉 TARGET REACHED: {self.total_products:,} products!")
                    break
            
            # Progress update
            print(f"\n📊 ROUND {round_num} SUMMARY:")
            print(f"   New products this round: {round_stored}")
            print(f"   Total products: {self.total_products:,}")
            print(f"   Progress: {(self.total_products/self.target_total)*100:.1f}%")
            
            # Platform balance update every 3 rounds
            if round_num % 3 == 0:
                print(f"\n🏪 PLATFORM BALANCE:")
                for platform, count in sorted(self.platform_stats.items(), key=lambda x: x[1], reverse=True):
                    if count > 0:
                        percentage = (count / self.total_products) * 100
                        print(f"   • {platform}: {count:,} ({percentage:.1f}%)")
            
            round_num += 1
            
            # Safety break if no progress for multiple rounds
            if round_stored == 0:
                print("⚠️  No new products this round")
                if round_num > 20:  # Allow some rounds without progress
                    print("🔄 Switching to different search terms...")
                    # Randomize search terms to find new products
                    random.shuffle(SEARCH_TERMS)
            
        # Final comprehensive statistics
        elapsed_time = time.time() - start_time
        
        print("\n" + "=" * 60)
        print("🎉 MASTER SCRAPING COMPLETE!")
        print("=" * 60)
        print(f"⏱️  Total time: {elapsed_time/60:.1f} minutes")
        print(f"📊 Total unique products: {self.total_products:,}")
        print(f"🎯 Target achievement: {(self.total_products/self.target_total)*100:.1f}%")
        
        # Final platform distribution
        print(f"\n🏪 FINAL PLATFORM DISTRIBUTION:")
        for platform, count in sorted(self.platform_stats.items(), key=lambda x: x[1], reverse=True):
            if count > 0:
                percentage = (count / self.total_products) * 100
                print(f"  • {platform}: {count:,} products ({percentage:.1f}%)")
        
        # Database final stats
        cursor = self.conn.cursor()
        cursor.execute("SELECT COUNT(DISTINCT product_url) FROM products")
        unique_urls = cursor.fetchone()[0]
        
        file_size = os.path.getsize(self.db_path) / (1024 * 1024)
        
        print(f"\n💾 DATABASE STATS:")
        print(f"  • Total products: {self.total_products:,}")
        print(f"  • Unique URLs: {unique_urls:,}")
        print(f"  • File size: {file_size:.1f} MB")
        print(f"  • Duplicate prevention: ✅ ACTIVE")
        
        # Categories breakdown
        cursor.execute("SELECT category, COUNT(*) FROM products GROUP BY category ORDER BY COUNT(*) DESC LIMIT 10")
        categories = cursor.fetchall()
        
        if categories:
            print(f"\n📂 TOP CATEGORIES:")
            for category, count in categories:
                percentage = (count / self.total_products) * 100
                print(f"  • {category}: {count:,} ({percentage:.1f}%)")
        
        self.conn.close()
        
        print(f"\n✅ Master database ready for PricePilot!")
        print(f"🚀 Zero duplicates, maximum coverage, balanced platforms!")

async def main():
    """Run master deduplicated scraping"""
    scraper = MasterDeduplicatedScraper()
    
    try:
        await scraper.run_master_scraping()
    except KeyboardInterrupt:
        print("\n⚠️  Master scraping interrupted")
    except Exception as e:
        print(f"\n❌ Error: {e}")

if __name__ == "__main__":
    asyncio.run(main())