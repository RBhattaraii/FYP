#!/usr/bin/env python3
"""
SMART CONSOLIDATED SCRAPER
Prevents duplicates and maintains one master database
TARGET: Build to 50k+ unique products efficiently
"""

import asyncio
import sqlite3
import sys
import os
import time
import random
from datetime import datetime, timezone
from urllib.parse import urlparse

# Add paths for imports
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))
sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'scrapers'))

# Import working scrapers
from scrapers.daraz.daraz_scraper import sync_scrape_daraz
from scrapers.better.better_scraper import async_scrape_better
from scrapers.hardwarepasal.hardwarepasal_scraper import async_scrape_hardwarepasal
from scrapers.hukut.hukut_scraper import async_scrape_hukut
from scrapers.jeevee.jeevee_scraper import async_scrape_jeevee
from scrapers.neostore.neostore_scraper import async_scrape_neostore
from scrapers.oliz.oliz_scraper import async_scrape_oliz

# Comprehensive search terms for maximum coverage
SEARCH_TERMS = [
    # High-yield electronics
    "laptop", "mobile", "phone", "smartphone", "computer", "tablet", "headphone", "earphone", 
    "speaker", "mouse", "keyboard", "charger", "cable", "power bank", "bluetooth", "wireless",
    
    # Popular brands
    "samsung", "apple", "xiaomi", "oppo", "vivo", "realme", "oneplus", "huawei", "nokia",
    "dell", "hp", "lenovo", "acer", "asus", "msi", "macbook", "iphone", "ipad",
    
    # Fashion essentials
    "shirt", "t-shirt", "jeans", "pants", "dress", "jacket", "coat", "shoes", "sneakers", 
    "sandals", "slippers", "bag", "backpack", "handbag", "wallet", "watch", "sunglasses",
    
    # Home & kitchen
    "kitchen", "home", "chair", "table", "sofa", "bed", "mattress", "pillow", "lamp", 
    "mirror", "clock", "fan", "cooler", "heater", "rice cooker", "blender", "kettle",
    
    # Beauty & health
    "cream", "lotion", "shampoo", "conditioner", "soap", "perfume", "makeup", "lipstick", 
    "foundation", "skincare", "haircare", "toothbrush", "toothpaste", "deodorant",
    
    # Sports & fitness
    "sports", "fitness", "gym", "exercise", "yoga", "running", "cricket", "football",
    "badminton", "tennis", "swimming", "cycling", "dumbbell", "weights", "treadmill",
    
    # Electronics accessories
    "case", "cover", "screen protector", "adapter", "converter", "extension", "stand", 
    "holder", "mount", "storage", "memory card", "usb", "hdmi", "audio", "video",
    
    # Categories for broader coverage
    "electronics", "fashion", "home", "beauty", "sports", "books", "toys", "games",
    "automobile", "medical", "tools", "office", "stationery", "jewelry", "appliances"
]

class SmartConsolidatedScraper:
    def __init__(self):
        self.db_path = 'master_products.db'
        self.setup_master_database()
        self.platform_stats = {}
        self.total_products = 0
        self.duplicates_prevented = 0
        
        # Working platforms with balanced targeting
        self.platforms = {
            'Daraz': {'scraper': self.scrape_daraz, 'async': False, 'target': 20000},
            'Jeevee': {'scraper': async_scrape_jeevee, 'async': True, 'target': 10000},
            'Oliz': {'scraper': async_scrape_oliz, 'async': True, 'target': 8000},
            'Hukut': {'scraper': async_scrape_hukut, 'async': True, 'target': 5000},
            'HardwarePasal': {'scraper': async_scrape_hardwarepasal, 'async': True, 'target': 4000},
            'Neostore': {'scraper': async_scrape_neostore, 'async': True, 'target': 2000},
            'Better': {'scraper': async_scrape_better, 'async': True, 'target': 1000}
        }
        
        # Initialize stats
        for platform in self.platforms.keys():
            self.platform_stats[platform] = 0
            
    def setup_master_database(self):
        """Setup master database with duplicate prevention"""
        self.conn = sqlite3.connect(self.db_path)
        self.conn.execute('''
            CREATE TABLE IF NOT EXISTS products (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                title TEXT NOT NULL,
                price REAL,
                original_price REAL,
                discount_percent REAL,
                image_url TEXT,
                store_name TEXT,
                product_url TEXT UNIQUE,  -- UNIQUE constraint prevents URL duplicates
                category TEXT,
                scraped_at TEXT,
                platform TEXT,
                search_term TEXT,
                last_updated TEXT
            )
        ''')
        
        # Create index for fast duplicate checking
        self.conn.execute('''
            CREATE INDEX IF NOT EXISTS idx_product_url ON products(product_url)
        ''')
        
        self.conn.commit()
        print(f"✅ Master database ready: {self.db_path}")
        print(f"🔒 Duplicate prevention: ACTIVE (unique URLs)")

    def scrape_daraz(self, search_term):
        """Wrapper for Daraz scraper with more pages"""
        return sync_scrape_daraz(search_term, max_pages=3)

    def is_duplicate(self, product_url):
        """Check if product URL already exists"""
        if not product_url:
            return True  # Skip products without URLs
            
        cursor = self.conn.cursor()
        cursor.execute("SELECT id FROM products WHERE product_url = ?", (product_url,))
        return cursor.fetchone() is not None

    def store_products_smart(self, products, platform_name, search_term):
        """Store products with intelligent duplicate prevention"""
        if not products:
            return 0, 0
            
        stored = 0
        skipped_duplicates = 0
        cursor = self.conn.cursor()
        
        for product in products:
            product_url = product.get('product_url', '')
            
            # Skip if no URL or already exists
            if not product_url or self.is_duplicate(product_url):
                skipped_duplicates += 1
                continue
            
            try:
                cursor.execute('''
                    INSERT INTO products 
                    (title, price, original_price, discount_percent, image_url, 
                     store_name, product_url, category, scraped_at, platform, search_term, last_updated)
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
                    datetime.now(timezone.utc).isoformat()
                ))
                stored += 1
                
            except sqlite3.IntegrityError:
                # URL constraint violation (shouldn't happen due to pre-check, but safety net)
                skipped_duplicates += 1
            except Exception as e:
                # Other errors - skip product
                continue
                
        self.conn.commit()
        
        # Update stats
        self.platform_stats[platform_name] += stored
        self.total_products += stored
        self.duplicates_prevented += skipped_duplicates
        
        return stored, skipped_duplicates

    async def scrape_platform_smart(self, platform_name, search_term):
        """Smart scraping with duplicate prevention"""
        platform_info = self.platforms[platform_name]
        
        # Check if platform has reached its target
        if self.platform_stats[platform_name] >= platform_info['target']:
            return 0, 0
            
        print(f"🏪 {platform_name}: '{search_term}'")
        
        try:
            if platform_info['async']:
                products = await platform_info['scraper'](search_term)
            else:
                products = platform_info['scraper'](search_term)
            
            if products and len(products) > 0:
                stored, skipped = self.store_products_smart(products, platform_name, search_term)
                
                if stored > 0 or skipped > 0:
                    status = f"✅ {len(products)} found → {stored} new, {skipped} duplicates"
                    print(f"   {status} | Total: {self.platform_stats[platform_name]:,}")
                else:
                    print(f"   ❌ No valid products")
                
                return stored, skipped
            else:
                print(f"   ❌ No products found")
                return 0, 0
                
        except Exception as e:
            print(f"   ❌ Error: {str(e)[:50]}...")
            return 0, 0

    async def run_smart_scraping(self):
        """Execute smart consolidated scraping"""
        print("🧠 SMART CONSOLIDATED SCRAPER")
        print("=" * 50)
        print("🎯 TARGET: 50k+ unique products (no duplicates)")
        print("🔒 DUPLICATE PREVENTION: Active")
        print("⚖️ BALANCED DISTRIBUTION: Enforced")
        print("🏪 PLATFORMS: All working scrapers")
        print("=" * 50)
        
        start_time = time.time()
        
        # Load existing data if any
        cursor = self.conn.cursor()
        cursor.execute("SELECT COUNT(*) FROM products")
        existing_count = cursor.fetchone()[0]
        
        if existing_count > 0:
            print(f"📊 Found {existing_count:,} existing products in master database")
            
            # Update platform stats from existing data
            cursor.execute("SELECT platform, COUNT(*) FROM products GROUP BY platform")
            for platform, count in cursor.fetchall():
                if platform in self.platform_stats:
                    self.platform_stats[platform] = count
            
            self.total_products = existing_count
        
        # Continue scraping until targets are met
        for round_num in range(1, 100):  # Up to 100 rounds
            print(f"\n🔄 ROUND {round_num}: Smart scraping with duplicate prevention")
            
            # Get platforms that need more products (ordered by deficit)
            platforms_needing_products = []
            for platform, info in self.platforms.items():
                current = self.platform_stats[platform]
                target = info['target']
                if current < target:
                    deficit = target - current
                    platforms_needing_products.append((platform, deficit))
            
            # Sort by deficit (highest first) to prioritize underperforming platforms
            platforms_needing_products.sort(key=lambda x: x[1], reverse=True)
            
            if not platforms_needing_products:
                print("🎉 All platform targets achieved!")
                break
            
            if self.total_products >= 50000:
                print("🎉 50k target reached!")
                break
            
            # Scrape from platforms in priority order
            round_new = 0
            round_duplicates = 0
            
            for i, search_term in enumerate(SEARCH_TERMS):
                if i >= len(platforms_needing_products) * 3:  # Limit terms per round
                    break
                
                # Rotate through platforms needing products
                platform_name, deficit = platforms_needing_products[i % len(platforms_needing_products)]
                
                stored, skipped = await self.scrape_platform_smart(platform_name, search_term)
                round_new += stored
                round_duplicates += skipped
                
                # Small delay between requests
                await asyncio.sleep(random.uniform(1, 3))
            
            # Progress update
            print(f"\n📊 ROUND {round_num} SUMMARY:")
            print(f"   New products: {round_new}")
            print(f"   Duplicates prevented: {round_duplicates}")
            print(f"   Total unique products: {self.total_products:,}")
            print(f"   50k progress: {(self.total_products/50000)*100:.1f}%")
            
            # Platform balance check
            if round_num % 5 == 0:
                print(f"\n⚖️ PLATFORM BALANCE:")
                for platform, count in sorted(self.platform_stats.items(), key=lambda x: x[1]):
                    target = self.platforms[platform]['target']
                    progress = (count / target) * 100 if target > 0 else 0
                    print(f"   {platform}: {count:,}/{target:,} ({progress:.1f}%)")
            
            # Break if no progress
            if round_new == 0:
                print("⚠️ No new products this round - may have reached available inventory")
                break
        
        # Final statistics
        elapsed_time = time.time() - start_time
        
        print("\n" + "=" * 50)
        print("🧠 SMART SCRAPING COMPLETE!")
        print("=" * 50)
        print(f"⏱️ Total time: {elapsed_time/60:.1f} minutes")
        print(f"📊 Unique products: {self.total_products:,}")
        print(f"🔒 Duplicates prevented: {self.duplicates_prevented:,}")
        print(f"🎯 50k progress: {(self.total_products/50000)*100:.1f}%")
        
        # Final platform distribution
        print(f"\n🏪 FINAL PLATFORM DISTRIBUTION:")
        for platform, count in sorted(self.platform_stats.items(), key=lambda x: x[1], reverse=True):
            target = self.platforms[platform]['target']
            percentage = (count / self.total_products) * 100 if self.total_products > 0 else 0
            progress = (count / target) * 100 if target > 0 else 0
            print(f"  • {platform}: {count:,} products ({percentage:.1f}% of total, {progress:.1f}% of target)")
        
        # Database info
        file_size = os.path.getsize(self.db_path) / (1024 * 1024)
        print(f"\n💾 MASTER DATABASE:")
        print(f"  • File: {self.db_path}")
        print(f"  • Size: {file_size:.1f} MB")
        print(f"  • Products: {self.total_products:,} unique")
        print(f"  • Duplicates prevented: {self.duplicates_prevented:,}")
        
        self.conn.close()
        print(f"\n✅ Smart scraping completed - NO DUPLICATES!")

async def main():
    """Run smart consolidated scraping"""
    scraper = SmartConsolidatedScraper()
    
    try:
        await scraper.run_smart_scraping()
    except KeyboardInterrupt:
        print("\n⚠️ Smart scraping interrupted")
    except Exception as e:
        print(f"\n❌ Error: {e}")

if __name__ == "__main__":
    asyncio.run(main())