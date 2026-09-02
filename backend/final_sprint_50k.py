#!/usr/bin/env python3
"""
FINAL SPRINT TO 50K
Ultra-aggressive final push to reach 50k unique products
"""

import asyncio
import sqlite3
import sys
import os
import random
from datetime import datetime, timezone

sys.path.append(os.path.join(os.path.dirname(__file__), '..'))
sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'scrapers'))

from scrapers.daraz.daraz_scraper import sync_scrape_daraz
from scrapers.jeevee.jeevee_scraper import async_scrape_jeevee
from scrapers.oliz.oliz_scraper import async_scrape_oliz
from scrapers.hukut.hukut_scraper import async_scrape_hukut

# Final sprint terms - maximum variety
SPRINT_TERMS = [
    # Long-tail specific searches
    "gaming laptop under 100000", "wireless bluetooth earbuds", "smart led tv 43 inch",
    "men formal shirt white", "women party dress red", "running shoes nike adidas",
    "stainless steel pressure cooker", "non stick frying pan", "cotton bed sheet king size",
    "leather wallet men brown", "designer handbag women", "wrist watch digital analog",
    
    # Brand + category combinations  
    "samsung mobile phone", "apple iphone case", "xiaomi power bank", "sony headphones",
    "hp laptop bag", "dell mouse keyboard", "lenovo tablet cover", "asus gaming accessories",
    "lg refrigerator", "whirlpool washing machine", "godrej microwave oven", "bajaj mixer grinder",
    
    # Seasonal and trending
    "winter jacket warm", "summer cotton shirt", "monsoon umbrella", "festival ethnic wear",
    "birthday gift ideas", "anniversary special", "valentine day gift", "mothers day present",
    
    # Price-based searches
    "under 1000 rupees", "under 5000 budget", "under 10000 price", "premium quality expensive",
    "cheap affordable price", "discount sale offer", "best deal today", "lowest price guarantee",
    
    # Category + adjective combinations
    "comfortable running shoes", "stylish casual wear", "elegant formal dress", "trendy accessories",
    "durable travel bag", "lightweight laptop", "powerful smartphone", "energy efficient appliances",
    
    # Problem-solving searches
    "back pain office chair", "dry skin moisturizer", "hair fall shampoo", "acne face wash",
    "weight loss supplement", "muscle gain protein", "joint pain relief", "eye strain glasses",
    
    # Activity-based
    "work from home setup", "study table lamp", "kitchen cooking essentials", "bedroom decor items",
    "living room furniture", "bathroom accessories", "garden outdoor furniture", "car cleaning kit",
    
    # Technical specifications
    "4gb ram mobile", "256gb storage laptop", "full hd display", "fast charging support",
    "wireless connectivity", "bluetooth enabled", "touch screen", "voice control",
    
    # Lifestyle categories
    "fitness gym equipment", "yoga meditation accessories", "travel adventure gear", "photography camera",
    "music instrument", "art craft supplies", "book reading accessories", "cooking baking tools",
    
    # Comprehensive single words for broad coverage
    "electronics", "mobiles", "laptops", "computers", "tablets", "cameras", "printers", "accessories",
    "clothing", "fashion", "shoes", "bags", "watches", "jewelry", "sunglasses", "perfumes",
    "furniture", "appliances", "kitchen", "home", "decor", "lighting", "storage", "garden",
    "health", "beauty", "skincare", "makeup", "haircare", "fragrances", "wellness", "fitness",
    "sports", "outdoor", "travel", "automotive", "books", "stationery", "toys", "games",
    "baby", "kids", "maternity", "pet", "office", "industrial", "medical", "tools"
]

class FinalSprint50k:
    def __init__(self):
        self.db_path = 'master_products.db'
        self.conn = sqlite3.connect(self.db_path)
        
        # Get current count
        cursor = self.conn.cursor()
        cursor.execute('SELECT COUNT(*) FROM products')
        self.current_count = cursor.fetchone()[0]
        
        self.products_added = 0
        self.target_reached = False
        
        print(f"🏁 FINAL SPRINT TO 50K")
        print(f"📊 Current: {self.current_count:,} products")
        print(f"🎯 Need: {50000 - self.current_count:,} more products")
        print(f"🚀 MAXIMUM SPEED ENGAGEMENT!")
        
    def rapid_add_products(self, products, platform_name, search_term):
        """Ultra-fast product addition"""
        if not products:
            return 0
            
        new_count = 0
        cursor = self.conn.cursor()
        
        for product in products:
            url = product.get('product_url', '')
            if not url:
                continue
                
            # Quick duplicate check - minimal processing for speed
            cursor.execute('SELECT 1 FROM products WHERE product_url = ? LIMIT 1', (url,))
            if cursor.fetchone():
                continue
                
            try:
                cursor.execute('''
                    INSERT INTO products 
                    (title, price, store_name, product_url, platform, search_term, last_updated)
                    VALUES (?, ?, ?, ?, ?, ?, ?)
                ''', (
                    product.get('product_name', 'Product')[:200],  # Truncate for speed
                    float(product.get('price', 0)),
                    platform_name,
                    url,
                    platform_name,
                    search_term,
                    datetime.now(timezone.utc).isoformat()
                ))
                new_count += 1
                
            except sqlite3.IntegrityError:
                continue
            except Exception:
                continue
        
        self.conn.commit()
        self.products_added += new_count
        
        # Update current count
        cursor.execute('SELECT COUNT(*) FROM products')
        self.current_count = cursor.fetchone()[0]
        
        if self.current_count >= 50000:
            self.target_reached = True
        
        return new_count
        
    async def sprint_scrape(self, platform_name, scraper_func, search_term, is_async=True):
        """Sprint scraping with real-time progress"""
        try:
            if is_async:
                products = await scraper_func(search_term)
            else:
                products = scraper_func(search_term)
                
            if products:
                new_count = self.rapid_add_products(products, platform_name, search_term)
                
                progress = (self.current_count / 50000) * 100
                remaining = 50000 - self.current_count
                
                if new_count > 0:
                    print(f"🏁 {platform_name}: +{new_count} | Total: {self.current_count:,} | Remaining: {remaining:,} ({progress:.1f}%)")
                
                return self.target_reached
            else:
                return False
                
        except Exception:
            return False
    
    async def run_final_sprint(self):
        """Execute final sprint to 50k"""
        print(f"\n🏁 FINAL SPRINT INITIATED - MAXIMUM SPEED!")
        print("=" * 50)
        
        # All working scrapers
        scrapers = [
            ("Daraz", lambda term: sync_scrape_daraz(term, max_pages=8), False),
            ("Jeevee", async_scrape_jeevee, True),
            ("Oliz", async_scrape_oliz, True),
            ("Hukut", async_scrape_hukut, True)
        ]
        
        term_index = 0
        
        # Ultra-aggressive sprinting
        for sprint_round in range(1, 500):  # Up to 500 sprint rounds
            if self.target_reached:
                break
                
            print(f"\\n🏃‍♂️ SPRINT {sprint_round}")
            
            sprint_new = 0
            
            # Multiple concurrent scraping tasks per sprint
            tasks = []
            
            for i in range(12):  # 12 concurrent tasks for maximum speed
                if term_index >= len(SPRINT_TERMS):
                    term_index = 0
                
                search_term = SPRINT_TERMS[term_index]
                platform_name, scraper_func, is_async = scrapers[i % len(scrapers)]
                
                task = self.sprint_scrape(platform_name, scraper_func, search_term, is_async)
                tasks.append(task)
                
                term_index += 1
            
            # Execute all tasks concurrently for maximum speed
            results = await asyncio.gather(*tasks, return_exceptions=True)
            
            # Check if target reached in any task
            for result in results:
                if result is True:
                    self.target_reached = True
                    break
            
            if self.target_reached:
                print(f"\\n🎉🎉🎉 50K TARGET ACHIEVED! 🎉🎉🎉")
                print(f"🏆 FINAL COUNT: {self.current_count:,} UNIQUE PRODUCTS")
                print(f"🏁 Sprint contributed: {self.products_added:,} products")
                print(f"🚀 MISSION ACCOMPLISHED!")
                return True
            
            # Micro delay for ultra-speed
            await asyncio.sleep(0.1)
        
        print(f"\\n🏃‍♂️ Sprint completed")
        print(f"📊 Final count: {self.current_count:,} products")
        print(f"🏁 Sprint contributed: {self.products_added:,} products")
        
        return self.current_count >= 50000

async def main():
    sprinter = FinalSprint50k()
    
    try:
        success = await sprinter.run_final_sprint()
        if success:
            print(f"\\n🏆 🎉 50,000 UNIQUE PRODUCTS ACHIEVED! 🎉 🏆")
        else:
            print(f"\\n🏃‍♂️ Final sprint completed - continue with other methods")
    except KeyboardInterrupt:
        print(f"\\n⚠️ Sprint interrupted")
    except Exception as e:
        print(f"\\n❌ Error: {e}")
    finally:
        if hasattr(sprinter, 'conn'):
            sprinter.conn.close()

if __name__ == "__main__":
    asyncio.run(main())