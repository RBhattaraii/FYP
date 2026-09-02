#!/usr/bin/env python3
"""
TURBO 50K SCRAPER
Aggressive scraping to reach 50k unique products quickly
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
from scrapers.better.better_scraper import async_scrape_better
from scrapers.hardwarepasal.hardwarepasal_scraper import async_scrape_hardwarepasal
from scrapers.neostore.neostore_scraper import async_scrape_neostore

# Extensive search terms for maximum coverage
TURBO_SEARCH_TERMS = [
    # Electronics - Brand + Product combinations
    "apple iphone", "samsung galaxy", "xiaomi redmi", "oppo reno", "vivo v", "realme narzo",
    "oneplus nord", "huawei mate", "nokia smartphone", "infinix hot", "tecno spark",
    
    # Laptops - Brand + Series
    "hp pavilion", "dell inspiron", "lenovo thinkpad", "acer aspire", "asus vivobook",
    "msi gaming", "macbook air", "macbook pro", "surface laptop", "gaming laptop",
    
    # Electronics accessories
    "wireless earbuds", "bluetooth headphones", "gaming headset", "phone case", "screen protector",
    "power bank", "wireless charger", "car charger", "usb cable", "hdmi cable",
    "memory card", "usb drive", "external hard drive", "ssd", "laptop bag",
    
    # Fashion - Detailed categories
    "men shirt", "women dress", "kids clothes", "formal wear", "casual wear", "party wear",
    "winter jacket", "summer dress", "sports wear", "gym clothes", "running shoes",
    "casual shoes", "formal shoes", "sandals", "boots", "slippers",
    
    # Fashion accessories
    "wrist watch", "smart watch", "wall clock", "handbag", "backpack", "wallet",
    "belt", "tie", "scarf", "hat", "cap", "sunglasses", "jewelry",
    
    # Home & Kitchen - Specific appliances
    "rice cooker", "pressure cooker", "air fryer", "microwave oven", "electric kettle",
    "coffee maker", "blender", "juicer", "mixer grinder", "toaster", "sandwich maker",
    "induction cooktop", "gas stove", "chimney", "water purifier", "refrigerator",
    
    # Furniture
    "office chair", "study table", "bed", "mattress", "sofa set", "dining table",
    "bookshelf", "wardrobe", "dressing table", "tv stand", "computer table",
    
    # Home decor
    "wall clock", "photo frame", "flower vase", "table lamp", "floor lamp",
    "ceiling fan", "wall fan", "curtains", "bed sheet", "pillow", "cushion",
    
    # Beauty & Personal Care - Specific products
    "face cream", "body lotion", "hair oil", "shampoo", "conditioner", "face wash",
    "sunscreen", "moisturizer", "serum", "toner", "makeup kit", "lipstick",
    "nail polish", "perfume", "deodorant", "hair dryer", "straightener",
    
    # Health & Fitness
    "fitness tracker", "blood pressure monitor", "thermometer", "weighing scale",
    "yoga mat", "dumbbell", "resistance band", "protein powder", "vitamin",
    
    # Baby & Kids - Specific items
    "baby clothes", "baby shoes", "feeding bottle", "diaper", "baby food",
    "stroller", "car seat", "high chair", "baby toy", "educational toy",
    
    # Sports specific
    "cricket bat", "football", "badminton racket", "tennis ball", "volleyball",
    "basketball", "table tennis", "chess board", "carrom board",
    
    # Automotive
    "car accessories", "bike accessories", "helmet", "car cover", "seat cover",
    "steering wheel cover", "car charger", "dash cam", "car perfume",
    
    # Books & Stationery - Specific
    "notebook", "diary", "pen set", "pencil", "marker", "highlighter",
    "calculator", "geometry box", "school bag", "college bag",
    
    # Kitchen utensils
    "knife set", "cutting board", "mixing bowl", "storage container",
    "lunch box", "water bottle", "thermos", "dinner set", "tea set",
    
    # Cleaning & Maintenance
    "vacuum cleaner", "floor cleaner", "dish soap", "detergent", "fabric softener",
    "toilet cleaner", "glass cleaner", "mop", "broom", "dustbin",
    
    # Seasonal & Occasion
    "winter wear", "summer collection", "festival wear", "birthday gift",
    "wedding gift", "valentine gift", "mother day gift", "father day gift",
    
    # Generic high-demand terms
    "bestseller", "trending", "popular", "top rated", "budget friendly",
    "premium quality", "luxury", "affordable", "value pack", "combo offer"
]

class Turbo50kScraper:
    def __init__(self):
        self.db_path = 'master_products.db'
        self.conn = sqlite3.connect(self.db_path)
        self.products_added = 0
        self.duplicates_prevented = 0
        
        # Get current count
        cursor = self.conn.cursor()
        cursor.execute('SELECT COUNT(*) FROM products')
        self.starting_count = cursor.fetchone()[0]
        
        print(f"🚀 TURBO 50K SCRAPER")
        print(f"📊 Starting count: {self.starting_count:,}")
        print(f"🎯 Target: 50,000 unique products")
        print(f"📈 Need: {50000 - self.starting_count:,} more products")
        
    def add_products_turbo(self, products, platform_name, search_term):
        """Fast product addition with duplicate checking"""
        if not products:
            return 0, 0
            
        new_count = 0
        duplicate_count = 0
        cursor = self.conn.cursor()
        
        for product in products:
            url = product.get('product_url', '')
            if not url:
                continue
                
            # Quick duplicate check
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
                
        self.conn.commit()
        self.products_added += new_count
        self.duplicates_prevented += duplicate_count
        
        return new_count, duplicate_count
    
    def scrape_daraz_turbo(self, term):
        """Enhanced Daraz scraping"""
        return sync_scrape_daraz(term, max_pages=6)  # More pages for more products
    
    async def scrape_platform_turbo(self, platform_name, scraper_func, search_term, is_async=True):
        """Turbo platform scraping"""
        try:
            if is_async:
                products = await scraper_func(search_term)
            else:
                products = scraper_func(search_term)
                
            if products:
                new_count, duplicates = self.add_products_turbo(products, platform_name, search_term)
                
                # Get current total
                cursor = self.conn.cursor()
                cursor.execute('SELECT COUNT(*) FROM products')
                current_total = cursor.fetchone()[0]
                
                print(f"🔥 {platform_name}: '{search_term}' → {new_count} new | Total: {current_total:,} | 50k: {(current_total/50000)*100:.1f}%")
                
                return new_count, current_total
            else:
                return 0, 0
                
        except Exception as e:
            print(f"❌ {platform_name} error: {str(e)[:40]}...")
            return 0, 0
    
    async def run_turbo_scraping(self):
        """Run aggressive turbo scraping"""
        print(f"\n🚀 TURBO SCRAPING TO 50K INITIATED")
        print("=" * 50)
        
        # Platform scrapers with priorities
        scrapers = [
            ("Daraz", self.scrape_daraz_turbo, False, 3),  # High priority
            ("Better", async_scrape_better, True, 2),
            ("HardwarePasal", async_scrape_hardwarepasal, True, 2),
            ("Neostore", async_scrape_neostore, True, 1)
        ]
        
        term_index = 0
        
        # Continue until 50k reached
        for round_num in range(1, 200):  # Up to 200 rounds if needed
            print(f"\n⚡ TURBO ROUND {round_num}")
            
            round_new = 0
            current_total = self.starting_count
            
            # Multiple terms per round for speed
            for i in range(8):  # 8 terms per round = faster growth
                if term_index >= len(TURBO_SEARCH_TERMS):
                    term_index = 0  # Restart terms
                
                search_term = TURBO_SEARCH_TERMS[term_index]
                
                # Rotate through platforms based on priority
                platform_name, scraper_func, is_async, priority = scrapers[i % len(scrapers)]
                
                new_count, current_total = await self.scrape_platform_turbo(
                    platform_name, scraper_func, search_term, is_async
                )
                
                round_new += new_count
                term_index += 1
                
                # Check if 50k reached
                if current_total >= 50000:
                    print(f"\n🎉 50K MILESTONE ACHIEVED!")
                    print(f"✅ Final count: {current_total:,} unique products")
                    return True
                
                # Short delay for speed
                await asyncio.sleep(random.uniform(0.3, 0.8))
            
            # Round summary
            print(f"📊 Round {round_num}: +{round_new} products | Total: {current_total:,} | Progress: {(current_total/50000)*100:.1f}%")
            
            # If no progress, try different approach
            if round_new == 0:
                print(f"⚠️ No new products this round - switching terms...")
                term_index += 10  # Skip ahead in terms
            
            self.starting_count = current_total
        
        # If we exit the loop without reaching 50k
        print(f"\n⏸️ Turbo scraping completed")
        print(f"📊 Final count: {current_total:,} products")
        print(f"🎯 50k progress: {(current_total/50000)*100:.1f}%")
        
        return False

async def main():
    scraper = Turbo50kScraper()
    
    try:
        success = await scraper.run_turbo_scraping()
        if success:
            print(f"\n🏆 SUCCESS: 50K UNIQUE PRODUCTS ACHIEVED!")
        else:
            print(f"\n📊 Turbo scraping completed - continue with other scrapers")
    except KeyboardInterrupt:
        print(f"\n⚠️ Turbo scraping interrupted")
    except Exception as e:
        print(f"\n❌ Error: {e}")
    finally:
        if hasattr(scraper, 'conn'):
            scraper.conn.close()

if __name__ == "__main__":
    asyncio.run(main())