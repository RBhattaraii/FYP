#!/usr/bin/env python3
"""
AGGRESSIVE BALANCED SCRAPER
Enforces STRICT equal distribution by capping each platform
TARGET: 300k products with ~43k per working platform (7 platforms)
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

# Import working scrapers (7 confirmed working)
from scrapers.daraz.daraz_scraper import sync_scrape_daraz
from scrapers.better.better_scraper import async_scrape_better
from scrapers.hardwarepasal.hardwarepasal_scraper import async_scrape_hardwarepasal
from scrapers.hukut.hukut_scraper import async_scrape_hukut
from scrapers.jeevee.jeevee_scraper import async_scrape_jeevee
from scrapers.neostore.neostore_scraper import async_scrape_neostore
from scrapers.oliz.oliz_scraper import async_scrape_oliz

# AGGRESSIVE SEARCH TERMS - designed for maximum yield
AGGRESSIVE_SEARCH_TERMS = [
    # High-yield electronics terms
    "laptop", "phone", "mobile", "computer", "tablet", "headphone", "speaker", "charger",
    "samsung", "apple", "xiaomi", "oppo", "vivo", "realme", "oneplus", "huawei",
    "dell", "hp", "lenovo", "acer", "asus", "msi", "macbook", "iphone", "android",
    
    # Fashion & accessories  
    "shirt", "t-shirt", "jeans", "pants", "dress", "jacket", "shoes", "sneakers", 
    "sandals", "bag", "backpack", "handbag", "watch", "sunglasses", "belt", "cap",
    
    # Home & kitchen essentials
    "kitchen", "home", "chair", "table", "sofa", "bed", "lamp", "mirror", "clock",
    "plate", "cup", "glass", "bottle", "cookware", "utensil", "knife", "spoon",
    
    # Beauty & health
    "cream", "lotion", "shampoo", "soap", "perfume", "makeup", "lipstick", "foundation",
    "skincare", "haircare", "toothbrush", "toothpaste", "deodorant", "cologne",
    
    # Electronics accessories
    "case", "cover", "screen protector", "cable", "adapter", "power bank", "bluetooth",
    "wireless", "earphone", "earbuds", "mouse", "keyboard", "webcam", "microphone",
    
    # Sports & fitness
    "sports", "fitness", "gym", "exercise", "yoga", "running", "cricket", "football",
    "badminton", "tennis", "swimming", "cycling", "dumbbell", "weights", "treadmill",
    
    # Categories
    "electronics", "fashion", "home", "beauty", "sports", "books", "toys", "games",
    "automobile", "medical", "tools", "office", "stationery", "jewelry", "shoes"
]

class AggressiveBalancedScraper:
    def __init__(self):
        self.db_path = 'aggressive_balanced_products.db'
        self.setup_database()
        self.platform_stats = {}
        
        # Target 43k per platform (300k / 7 working platforms)
        self.target_per_platform = 43000
        self.max_imbalance = 1000  # Allow max 1k difference between platforms
        
        # Only working scrapers
        self.platforms = {
            'Daraz': {'scraper': self.scrape_daraz, 'async': False, 'priority': 3},
            'Better': {'scraper': async_scrape_better, 'async': True, 'priority': 1}, 
            'HardwarePasal': {'scraper': async_scrape_hardwarepasal, 'async': True, 'priority': 2},
            'Hukut': {'scraper': async_scrape_hukut, 'async': True, 'priority': 2},
            'Jeevee': {'scraper': async_scrape_jeevee, 'async': True, 'priority': 2},
            'Neostore': {'scraper': async_scrape_neostore, 'async': True, 'priority': 1},
            'Oliz': {'scraper': async_scrape_oliz, 'async': True, 'priority': 1}
        }
        
        # Initialize stats
        for platform in self.platforms.keys():
            self.platform_stats[platform] = 0
            
    def setup_database(self):
        """Setup aggressive balanced database"""
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
                aggressive_batch TEXT
            )
        ''')
        self.conn.commit()
        print(f"✅ Aggressive balanced database ready: {self.db_path}")

    def scrape_daraz(self, search_term):
        """Wrapper for Daraz sync scraper - use more pages for volume"""
        return sync_scrape_daraz(search_term, max_pages=8)

    def get_platform_priority_order(self):
        """Get platforms ordered by current deficit (least products first)"""
        platform_counts = [(platform, self.platform_stats[platform]) 
                          for platform in self.platforms.keys()]
        
        # Sort by count (ascending) then by priority (ascending = higher priority)  
        return sorted(platform_counts, key=lambda x: (x[1], self.platforms[x[0]]['priority']))

    def should_scrape_platform(self, platform_name):
        """Check if platform should be scraped based on balance"""
        current_count = self.platform_stats[platform_name]
        
        # Always scrape if under target
        if current_count < self.target_per_platform:
            return True
            
        # Check if this platform is significantly ahead of others
        other_counts = [count for p, count in self.platform_stats.items() if p != platform_name]
        if other_counts:
            min_other = min(other_counts)
            if current_count - min_other > self.max_imbalance:
                return False  # Skip this platform, it's too far ahead
                
        return True

    def store_products_aggressive(self, products, platform_name, search_term, batch_id):
        """Store products with strict balance enforcement"""
        if not products or not self.should_scrape_platform(platform_name):
            return 0
            
        stored = 0
        cursor = self.conn.cursor()
        
        # Calculate how many we can actually store to maintain balance
        current_count = self.platform_stats[platform_name]
        other_counts = [count for p, count in self.platform_stats.items() if p != platform_name]
        
        if other_counts:
            min_other = min(other_counts)
            max_storable = min_other + self.max_imbalance
            available_slots = max(0, max_storable - current_count)
            
            if available_slots < len(products):
                products = products[:available_slots]
                print(f"  ⚖️  Limited to {available_slots} products for balance")
        
        for product in products:
            try:
                cursor.execute('''
                    INSERT OR REPLACE INTO products 
                    (title, price, original_price, discount_percent, image_url, 
                     store_name, product_url, category, scraped_at, platform, search_term, aggressive_batch)
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

    async def scrape_platform_aggressive(self, platform_name, search_term, batch_id):
        """Aggressively scrape with balance enforcement"""
        if not self.should_scrape_platform(platform_name):
            return 0
            
        platform_info = self.platforms[platform_name]
        
        print(f"🏪 {platform_name}: {search_term}")
        
        try:
            if platform_info['async']:
                products = await platform_info['scraper'](search_term)
            else:
                products = platform_info['scraper'](search_term)
            
            if products and len(products) > 0:
                stored = self.store_products_aggressive(products, platform_name, search_term, batch_id)
                print(f"  ✅ {len(products)} found → {stored} stored | Total: {self.platform_stats[platform_name]:,}")
                return stored
            else:
                print(f"  ❌ No products")
                return 0
                
        except Exception as e:
            print(f"  ❌ Error: {str(e)[:50]}...")
            return 0

    async def run_aggressive_scraping(self):
        """Execute aggressive balanced scraping"""
        print("⚡ AGGRESSIVE BALANCED MULTI-PLATFORM SCRAPER")
        print("=" * 70)
        print("🎯 TARGET: 300k products across 7 platforms (~43k each)")
        print("⚖️ BALANCE: Maximum 1k difference between platforms")
        print("🏪 PLATFORMS: Daraz, Better, HardwarePasal, Hukut, Jeevee, Neostore, Oliz")
        print("=" * 70)
        
        start_time = time.time()
        batch_id = f"aggressive_{int(time.time())}"
        term_index = 0
        
        # Continue until all platforms reach target or we exhaust options
        for round_num in range(1, 50):  # Up to 50 rounds for 300k products
            print(f"\n⚡ ROUND {round_num}: Aggressive balanced scraping")
            
            # Get platforms ordered by priority (least products first)
            priority_order = self.get_platform_priority_order()
            
            # Check if we should continue
            platforms_needing_products = [p for p, count in priority_order 
                                        if count < self.target_per_platform]
            
            if not platforms_needing_products:
                print("🎉 All platforms have reached target!")
                break
                
            total_products = sum(self.platform_stats.values())
            if total_products >= 300000:
                print("🎉 300k target reached!")
                break
            
            # Scrape from platforms in priority order
            scraped_this_round = 0
            
            for platform_name, current_count in priority_order[:5]:  # Top 5 priority platforms per round
                if term_index >= len(AGGRESSIVE_SEARCH_TERMS):
                    term_index = 0  # Restart terms if exhausted
                    
                search_term = AGGRESSIVE_SEARCH_TERMS[term_index]
                
                stored = await self.scrape_platform_aggressive(platform_name, search_term, batch_id)
                scraped_this_round += stored
                
                # Small delay between platforms
                await asyncio.sleep(random.uniform(1, 3))
                
                term_index += 1
            
            # Progress update every round
            total_products = sum(self.platform_stats.values())
            print(f"\n📊 ROUND {round_num} SUMMARY:")
            print(f"   Products this round: {scraped_this_round}")
            print(f"   Total products: {total_products:,}")
            print(f"   Progress: {(total_products/300000)*100:.1f}%")
            
            # Show balance
            counts = list(self.platform_stats.values())
            if counts:
                min_count = min(counts)
                max_count = max(counts)
                balance_ratio = min_count / max_count if max_count > 0 else 0
                print(f"   Balance ratio: {balance_ratio:.3f}")
            
            # Every 5 rounds, show detailed platform stats
            if round_num % 5 == 0:
                print(f"\n🏪 PLATFORM DISTRIBUTION:")
                for platform, count in sorted(self.platform_stats.items(), key=lambda x: x[1]):
                    percentage = (count / total_products) * 100 if total_products > 0 else 0
                    target_percentage = (count / self.target_per_platform) * 100
                    print(f"   • {platform}: {count:,} ({percentage:.1f}% of total, {target_percentage:.1f}% of target)")
            
            if scraped_this_round == 0:
                print("⚠️  No products scraped this round, switching terms...")
                term_index = (term_index + 10) % len(AGGRESSIVE_SEARCH_TERMS)
        
        # Final statistics
        elapsed_time = time.time() - start_time
        total_products = sum(self.platform_stats.values())
        
        print("\n" + "=" * 70)
        print("⚡ AGGRESSIVE BALANCED SCRAPING COMPLETE!")
        print("=" * 70)
        print(f"⏱️  Total time: {elapsed_time/60:.1f} minutes")
        print(f"📊 Total products: {total_products:,}")
        print(f"🎯 Target achievement: {(total_products/300000)*100:.1f}%")
        
        # Final platform distribution
        print(f"\n🏪 FINAL PLATFORM DISTRIBUTION:")
        for platform, count in sorted(self.platform_stats.items(), key=lambda x: x[1], reverse=True):
            percentage = (count / total_products) * 100 if total_products > 0 else 0
            target_percentage = (count / self.target_per_platform) * 100
            print(f"  • {platform}: {count:,} products ({percentage:.1f}% of total, {target_percentage:.1f}% of target)")
        
        # Balance quality assessment
        platform_counts = list(self.platform_stats.values())
        if platform_counts:
            min_count = min(platform_counts)
            max_count = max(platform_counts)
            balance_ratio = min_count / max_count if max_count > 0 else 0
            imbalance = max_count - min_count
            
            print(f"\n⚖️ BALANCE QUALITY:")
            print(f"  • Balance ratio: {balance_ratio:.3f} (1.0 = perfect)")
            print(f"  • Max imbalance: {imbalance:,} products")
            
            if balance_ratio >= 0.9:
                print(f"  • ✅ EXCELLENT balance!")
            elif balance_ratio >= 0.7:
                print(f"  • ✅ GOOD balance")
            else:
                print(f"  • ⚠️  Needs improvement")
        
        self.conn.close()
        print(f"\n✅ Aggressive balanced scraping completed!")
        
async def main():
    """Run aggressive balanced scraping"""
    scraper = AggressiveBalancedScraper()
    
    try:
        await scraper.run_aggressive_scraping()
    except KeyboardInterrupt:
        print("\n⚠️  Aggressive scraping interrupted")
    except Exception as e:
        print(f"\n❌ Error: {e}")

if __name__ == "__main__":
    asyncio.run(main())