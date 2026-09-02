#!/usr/bin/env python3
"""
BALANCED MULTI-PLATFORM SCRAPER
Ensures equal distribution across ALL 9 e-commerce platforms
TARGET: 300k products = ~33k per platform
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

# Import ALL 9 scrapers
from scrapers.daraz.daraz_scraper import sync_scrape_daraz, async_scrape_daraz
from scrapers.cgdigital.cgdigital_scraper import async_scrape_cgdigital
from scrapers.better.better_scraper import async_scrape_better
from scrapers.hardwarepasal.hardwarepasal_scraper import async_scrape_hardwarepasal
from scrapers.hukut.hukut_scraper import async_scrape_hukut
from scrapers.jeevee.jeevee_scraper import async_scrape_jeevee
from scrapers.neostore.neostore_scraper import async_scrape_neostore
from scrapers.oliz.oliz_scraper import async_scrape_oliz
from scrapers.ufonepal.ufonepal_scraper import async_scrape_ufonepal

# BALANCED SEARCH TERMS - optimized for all platforms
BALANCED_SEARCH_TERMS = [
    # Electronics - Universal terms
    "laptop", "mobile", "phone", "computer", "tablet", "headphone", "speaker", "mouse", "keyboard", 
    "charger", "cable", "power bank", "bluetooth", "wireless", "samsung", "apple", "xiaomi",
    
    # Fashion - Common items
    "shirt", "jeans", "shoes", "bag", "watch", "belt", "dress", "jacket", "sneakers", "sandals",
    
    # Home & Kitchen - Essentials  
    "kitchen", "home", "chair", "table", "lamp", "bottle", "plate", "cup", "cookware", "utensil",
    
    # Health & Beauty - Basics
    "cream", "shampoo", "soap", "toothbrush", "perfume", "makeup", "skincare", "haircare",
    
    # Sports & Fitness
    "sports", "fitness", "gym", "exercise", "yoga", "football", "cricket", "badminton",
    
    # Books & Stationery
    "book", "notebook", "pen", "pencil", "diary", "calculator", "bag", "school",
    
    # Baby & Kids
    "baby", "kids", "toy", "game", "puzzle", "doll", "stroller", "feeding",
    
    # Automotive 
    "car", "bike", "helmet", "cover", "accessories", "parts", "tools", "battery",
    
    # General high-yield terms
    "accessories", "case", "cover", "stand", "holder", "storage", "organizer", "set"
]

class BalancedPlatformScraper:
    def __init__(self):
        self.db_path = 'balanced_products.db'
        self.setup_database()
        self.platform_stats = {}
        self.target_per_platform = 33000  # 300k / 9 platforms
        
        # Define all 9 platforms with their scrapers
        self.platforms = {
            'Daraz': {'scraper': self.scrape_daraz, 'async': False},
            'CGDigital': {'scraper': async_scrape_cgdigital, 'async': True},
            'Better': {'scraper': async_scrape_better, 'async': True}, 
            'HardwarePasal': {'scraper': async_scrape_hardwarepasal, 'async': True},
            'Hukut': {'scraper': async_scrape_hukut, 'async': True},
            'Jeevee': {'scraper': async_scrape_jeevee, 'async': True},
            'Neostore': {'scraper': async_scrape_neostore, 'async': True},
            'Oliz': {'scraper': async_scrape_oliz, 'async': True},
            'UFONepal': {'scraper': async_scrape_ufonepal, 'async': True}
        }
        
        # Initialize stats
        for platform in self.platforms.keys():
            self.platform_stats[platform] = 0
            
    def setup_database(self):
        """Setup balanced scraper database"""
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
                balanced_batch TEXT
            )
        ''')
        self.conn.commit()
        print(f"✅ Balanced database ready: {self.db_path}")

    def scrape_daraz(self, search_term):
        """Wrapper for Daraz sync scraper"""
        return sync_scrape_daraz(search_term, max_pages=5)

    def store_products_balanced(self, products, platform_name, search_term, batch_id):
        """Store products with platform tracking"""
        if not products:
            return 0
            
        stored = 0
        cursor = self.conn.cursor()
        
        for product in products:
            try:
                cursor.execute('''
                    INSERT OR REPLACE INTO products 
                    (title, price, original_price, discount_percent, image_url, 
                     store_name, product_url, category, scraped_at, platform, search_term, balanced_batch)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                ''', (
                    product.get('product_name', 'Unknown Product'),
                    float(product.get('price', 0)),
                    float(product.get('original_price', 0)) if product.get('original_price') else None,
                    float(product.get('discount_percentage', 0)) if product.get('discount_percentage') else None,
                    product.get('image_url', ''),
                    platform_name,
                    product.get('product_url', ''),
                    search_term,
                    datetime.now(timezone.utc).isoformat(),
                    platform_name,
                    search_term,
                    batch_id
                ))
                stored += 1
            except Exception as e:
                continue
                
        self.conn.commit()
        self.platform_stats[platform_name] += stored
        return stored

    async def scrape_platform_balanced(self, platform_name, search_term, batch_id):
        """Scrape from a specific platform"""
        platform_info = self.platforms[platform_name]
        
        # Skip if platform already has enough products
        if self.platform_stats[platform_name] >= self.target_per_platform:
            return 0
            
        print(f"🏪 {platform_name}: {search_term}")
        
        try:
            if platform_info['async']:
                products = await platform_info['scraper'](search_term)
            else:
                products = platform_info['scraper'](search_term)
            
            if products and len(products) > 0:
                stored = self.store_products_balanced(products, platform_name, search_term, batch_id)
                print(f"  ✅ {len(products)} found → {stored} stored | Total: {self.platform_stats[platform_name]:,}")
                return stored
            else:
                print(f"  ❌ No products")
                return 0
                
        except Exception as e:
            print(f"  ❌ Error: {str(e)[:50]}...")
            return 0

    async def run_balanced_scraping(self):
        """Execute balanced scraping across all 9 platforms"""
        print("⚖️ BALANCED MULTI-PLATFORM SCRAPER")
        print("=" * 60)
        print("🎯 TARGET: 300k products across 9 platforms (~33k each)")
        print("🏪 PLATFORMS: Daraz, CGDigital, Better, HardwarePasal, Hukut,")
        print("              Jeevee, Neostore, Oliz, UFONepal")
        print("=" * 60)
        
        start_time = time.time()
        batch_id = f"balanced_{int(time.time())}"
        
        # Continue until all platforms have enough products or we exhaust terms
        for round_num in range(1, 20):  # Up to 20 rounds
            print(f"\n🔄 ROUND {round_num}: Cycling through all platforms")
            
            # Check if any platform needs more products
            platforms_needing_products = [
                p for p in self.platforms.keys() 
                if self.platform_stats[p] < self.target_per_platform
            ]
            
            if not platforms_needing_products:
                print("🎉 All platforms have reached target!")
                break
            
            # Scrape from each platform that needs products
            for i, search_term in enumerate(BALANCED_SEARCH_TERMS):
                if not platforms_needing_products:
                    break
                    
                # Rotate through platforms needing products
                platform_name = platforms_needing_products[i % len(platforms_needing_products)]
                
                await self.scrape_platform_balanced(platform_name, search_term, batch_id)
                
                # Add delay between requests
                await asyncio.sleep(random.uniform(2, 4))
                
                # Progress update every 10 terms
                if (i + 1) % 10 == 0:
                    total_products = sum(self.platform_stats.values())
                    print(f"\n📊 PROGRESS UPDATE:")
                    print(f"   Total products: {total_products:,}")
                    for platform, count in self.platform_stats.items():
                        percentage = (count / self.target_per_platform) * 100
                        print(f"   • {platform}: {count:,} ({percentage:.1f}%)")
                    
                    # Update list of platforms needing products
                    platforms_needing_products = [
                        p for p in self.platforms.keys() 
                        if self.platform_stats[p] < self.target_per_platform
                    ]
                    
                    if not platforms_needing_products:
                        print("🎉 All targets reached!")
                        break
        
        # Final comprehensive statistics
        elapsed_time = time.time() - start_time
        total_products = sum(self.platform_stats.values())
        
        print("\n" + "=" * 60)
        print("⚖️ BALANCED SCRAPING COMPLETE!")
        print("=" * 60)
        print(f"⏱️  Total time: {elapsed_time/60:.1f} minutes")
        print(f"📊 Total products: {total_products:,}")
        print(f"🎯 Target achievement: {(total_products/300000)*100:.1f}%")
        
        print(f"\n🏪 PLATFORM DISTRIBUTION:")
        for platform, count in sorted(self.platform_stats.items(), key=lambda x: x[1], reverse=True):
            percentage = (count / total_products) * 100 if total_products > 0 else 0
            target_percentage = (count / self.target_per_platform) * 100
            print(f"  • {platform}: {count:,} products ({percentage:.1f}% of total, {target_percentage:.1f}% of target)")
        
        # Database stats
        cursor = self.conn.cursor()
        cursor.execute("SELECT COUNT(*) FROM products")
        db_total = cursor.fetchone()[0]
        
        cursor.execute("SELECT platform, COUNT(*) FROM products GROUP BY platform")
        db_platform_stats = cursor.fetchall()
        
        file_size = os.path.getsize(self.db_path) / (1024 * 1024)
        
        print(f"\n💾 DATABASE STATS:")
        print(f"  • Total stored: {db_total:,} products")
        print(f"  • File size: {file_size:.1f} MB")
        
        print(f"\n📂 STORED BY PLATFORM:")
        for platform, count in db_platform_stats:
            percentage = (count / db_total) * 100 if db_total > 0 else 0
            print(f"  • {platform}: {count:,} products ({percentage:.1f}%)")
        
        # Check balance quality
        platform_counts = [count for _, count in db_platform_stats]
        if platform_counts:
            min_count = min(platform_counts)
            max_count = max(platform_counts)
            balance_ratio = min_count / max_count if max_count > 0 else 0
            
            print(f"\n⚖️ BALANCE QUALITY:")
            print(f"  • Balance ratio: {balance_ratio:.2f} (1.0 = perfect balance)")
            if balance_ratio >= 0.8:
                print(f"  • ✅ EXCELLENT balance across platforms!")
            elif balance_ratio >= 0.5:
                print(f"  • ✅ GOOD balance across platforms")
            else:
                print(f"  • ⚠️  Imbalanced - some platforms need more products")
        
        self.conn.close()
        
        print(f"\n✅ Balanced scraping completed!")
        print(f"🎯 Your PricePilot now has products from ALL 9 platforms!")

async def main():
    """Run balanced platform scraping"""
    scraper = BalancedPlatformScraper()
    
    try:
        await scraper.run_balanced_scraping()
    except KeyboardInterrupt:
        print("\n⚠️  Balanced scraping interrupted")
    except Exception as e:
        print(f"\n❌ Error: {e}")
    finally:
        if hasattr(scraper, 'conn'):
            scraper.cleanup()

if __name__ == "__main__":
    asyncio.run(main())