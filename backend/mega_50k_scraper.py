#!/usr/bin/env python3
"""
MEGA 50K SCRAPER
Parallel aggressive scraping with ALL working platforms
"""

import asyncio
import sqlite3
import sys
import os
import random
from datetime import datetime, timezone

sys.path.append(os.path.join(os.path.dirname(__file__), '..'))
sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'scrapers'))

from scrapers.jeevee.jeevee_scraper import async_scrape_jeevee
from scrapers.oliz.oliz_scraper import async_scrape_oliz
from scrapers.hukut.hukut_scraper import async_scrape_hukut

# Mega search terms - specific and targeted
MEGA_TERMS = [
    # Electronics - specific models
    "iphone 14", "iphone 13", "samsung s23", "samsung a54", "xiaomi 13", "redmi note",
    "hp laptop", "dell laptop", "lenovo laptop", "asus laptop", "acer laptop",
    "airpods", "earbuds", "headphones", "speaker", "smartwatch", "fitness band",
    
    # Fashion - specific types
    "men t-shirt", "women top", "jeans", "formal shirt", "casual dress", "party dress",
    "sports shoes", "casual shoes", "sandals", "boots", "sneakers", "formal shoes",
    "handbag", "backpack", "wallet", "belt", "watch", "sunglasses",
    
    # Home - specific products
    "led tv", "smart tv", "refrigerator", "washing machine", "ac", "cooler",
    "mixer grinder", "rice cooker", "pressure cooker", "microwave", "oven",
    "sofa", "bed", "table", "chair", "mattress", "pillow",
    
    # Beauty - specific items
    "face cream", "shampoo", "perfume", "lipstick", "foundation", "moisturizer",
    "body lotion", "face wash", "sunscreen", "hair oil", "conditioner",
    
    # Categories for broad coverage
    "mobile", "laptop", "tablet", "camera", "printer", "router",
    "shirt", "dress", "shoes", "bag", "jewellery", "accessories",
    "kitchen", "furniture", "decor", "lighting", "storage",
    "health", "fitness", "sports", "outdoor", "gaming"
]

class Mega50kScraper:
    def __init__(self):
        self.db_path = 'master_products.db'
        self.products_added = 0
        self.duplicates_prevented = 0
        
    def add_to_master_db(self, products, platform_name, search_term):
        """Add products to master database"""
        if not products:
            return 0, 0
            
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        new_count = 0
        duplicate_count = 0
        
        for product in products:
            url = product.get('product_url', '')
            if not url:
                continue
                
            # Check duplicate
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
                    product.get('product_name', 'Product'),
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
        
        conn.commit()
        conn.close()
        
        self.products_added += new_count
        self.duplicates_prevented += duplicate_count
        
        return new_count, duplicate_count
        
    async def mega_scrape_platform(self, platform_name, scraper_func, search_term):
        """Mega scrape with progress tracking"""
        try:
            products = await scraper_func(search_term)
            
            if products:
                new_count, duplicates = self.add_to_master_db(products, platform_name, search_term)
                
                # Get current total
                conn = sqlite3.connect(self.db_path)
                cursor = conn.cursor()
                cursor.execute('SELECT COUNT(*) FROM products')
                total = cursor.fetchone()[0]
                conn.close()
                
                progress = (total / 50000) * 100
                
                if new_count > 0:
                    print(f"💥 {platform_name}: '{search_term}' → +{new_count} | Total: {total:,} ({progress:.1f}%)")
                
                return new_count, total >= 50000
            else:
                return 0, False
                
        except Exception as e:
            return 0, False
    
    async def run_mega_scraping(self):
        """Run mega scraping operation"""
        print(f"💥 MEGA 50K SCRAPER ACTIVATED")
        print(f"🎯 Target: Rapid growth to 50,000 products")
        print("=" * 45)
        
        # Platform scrapers
        platforms = [
            ("Jeevee", async_scrape_jeevee),
            ("Oliz", async_scrape_oliz),
            ("Hukut", async_scrape_hukut)
        ]
        
        term_index = 0
        
        for mega_round in range(1, 100):  # Up to 100 mega rounds
            print(f"\\n💥 MEGA ROUND {mega_round}")
            
            round_new = 0
            target_reached = False
            
            # Process multiple terms concurrently
            tasks = []
            
            for i in range(6):  # 6 concurrent scraping tasks per round
                if term_index >= len(MEGA_TERMS):
                    term_index = 0
                
                search_term = MEGA_TERMS[term_index]
                platform_name, scraper_func = platforms[i % len(platforms)]
                
                task = self.mega_scrape_platform(platform_name, scraper_func, search_term)
                tasks.append(task)
                
                term_index += 1
            
            # Execute all tasks concurrently
            results = await asyncio.gather(*tasks, return_exceptions=True)
            
            # Process results
            for result in results:
                if isinstance(result, tuple):
                    new_count, reached_50k = result
                    round_new += new_count
                    if reached_50k:
                        target_reached = True
            
            print(f"📊 Mega Round {mega_round}: +{round_new} products")
            
            # Check if 50k reached
            if target_reached:
                conn = sqlite3.connect(self.db_path)
                cursor = conn.cursor()
                cursor.execute('SELECT COUNT(*) FROM products')
                final_total = cursor.fetchone()[0]
                conn.close()
                
                print(f"\\n🎉 50K TARGET ACHIEVED!")
                print(f"✅ Final count: {final_total:,} unique products")
                print(f"💥 Mega scraper contributed: {self.products_added:,} products")
                return True
            
            # Short delay between mega rounds
            await asyncio.sleep(1)
            
            if round_new == 0:
                print("⚠️ No new products - switching strategy...")
        
        print(f"\\n💥 Mega scraping completed")
        print(f"📊 Total contributed: {self.products_added:,} products")
        return False

async def main():
    scraper = Mega50kScraper()
    
    try:
        success = await scraper.run_mega_scraping()
        if success:
            print(f"\\n🏆 50K MILESTONE ACHIEVED BY MEGA SCRAPER!")
        else:
            print(f"\\n📊 Mega scraper finished - check other scrapers")
            
    except KeyboardInterrupt:
        print(f"\\n⚠️ Mega scraping interrupted")
    except Exception as e:
        print(f"\\n❌ Error: {e}")

if __name__ == "__main__":
    asyncio.run(main())