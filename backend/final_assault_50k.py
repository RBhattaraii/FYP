#!/usr/bin/env python3
"""
FINAL ASSAULT 50K
Ultimate aggressive scraping - no holds barred approach to 50k
"""

import asyncio
import sqlite3
import sys
import os
from datetime import datetime, timezone

sys.path.append(os.path.join(os.path.dirname(__file__), '..'))
sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'scrapers'))

from scrapers.daraz.daraz_scraper import sync_scrape_daraz
from scrapers.jeevee.jeevee_scraper import async_scrape_jeevee
from scrapers.oliz.oliz_scraper import async_scrape_oliz
from scrapers.hukut.hukut_scraper import async_scrape_hukut
from scrapers.better.better_scraper import async_scrape_better
from scrapers.neostore.neostore_scraper import async_scrape_neostore
from scrapers.hardwarepasal.hardwarepasal_scraper import async_scrape_hardwarepasal

# Final assault terms - every conceivable search
ASSAULT_TERMS = [
    # Single letter + category (covers everything)
    "a mobile", "a laptop", "a shirt", "a shoes", "a bag", "a watch", "a phone", "a tablet",
    "b mobile", "b laptop", "b shirt", "b shoes", "b bag", "b watch", "b phone", "b tablet", 
    "c mobile", "c laptop", "c shirt", "c shoes", "c bag", "c watch", "c phone", "c tablet",
    "d mobile", "d laptop", "d shirt", "d shoes", "d bag", "d watch", "d phone", "d tablet",
    "e mobile", "e laptop", "e shirt", "e shoes", "e bag", "e watch", "e phone", "e tablet",
    
    # Number combinations
    "1 piece", "2 piece", "3 piece", "4 piece", "5 piece", "6 piece", "10 piece", "12 piece",
    "100", "200", "500", "1000", "2000", "5000", "10000", "15000", "20000", "25000", "30000",
    
    # Color + product combinations
    "black shirt", "white shirt", "blue jeans", "red dress", "green bag", "brown shoes",
    "pink mobile", "yellow watch", "purple bag", "orange shirt", "gray laptop", "silver phone",
    
    # Size + product combinations  
    "small bag", "medium shirt", "large shoes", "xl dress", "xxl jacket", "32 inch tv",
    "43 inch smart tv", "55 inch led", "6 inch phone", "5.5 inch mobile", "15 inch laptop",
    
    # Material + product
    "cotton shirt", "silk dress", "leather bag", "steel watch", "plastic bottle", "glass bowl",
    "wooden table", "metal chair", "ceramic plate", "rubber shoes", "fabric sofa", "paper book",
    
    # Brand initials + product
    "s mobile", "s laptop", "s shirt", "h laptop", "h mobile", "l jeans", "n shoes", "a watch",
    "i phone", "i pad", "m laptop", "d laptop", "hp laptop", "lg tv", "mi phone", "op phone",
    
    # Generic terms with numbers
    "mobile 1", "mobile 2", "laptop 1", "laptop 2", "shirt 1", "shirt 2", "shoes 1", "shoes 2",
    "phone case 1", "power bank 1", "headphones 1", "speaker 1", "charger 1", "cable 1",
    
    # Action words + products
    "buy mobile", "buy laptop", "buy shirt", "buy shoes", "new mobile", "new laptop", "new shirt",
    "best mobile", "best laptop", "top shirt", "cheap mobile", "sale laptop", "offer shirt",
    
    # Common misspellings and variations
    "mobil", "laptp", "headfone", "speker", "chargr", "cabl", "wirless", "blutooth", "smartfone",
    "compter", "tablat", "camra", "printr", "mous", "keybord", "monitr", "lapbag", "powrbank",
    
    # Category + adjective
    "good mobile", "nice laptop", "cool shirt", "smart watch", "fast charger", "long cable",
    "big screen", "small phone", "light laptop", "heavy bag", "soft shirt", "hard drive",
    
    # Very specific model variations
    "phone 128gb", "laptop 8gb ram", "tv 4k hdr", "watch gps", "bag waterproof", "shoes running",
    "shirt cotton 100%", "jeans stretch", "dress party wear", "jacket winter warm", "cap baseball",
    
    # Product + usage
    "office laptop", "gaming mobile", "party dress", "gym shoes", "travel bag", "study table",
    "kitchen appliance", "bedroom furniture", "living room", "bathroom accessories", "garden tools",
    
    # Seasonal specific
    "winter clothes", "summer wear", "monsoon gear", "festival outfit", "wedding dress", "birthday gift",
    "christmas decoration", "diwali lights", "new year party", "valentine special", "mothers day",
    
    # Technical specs
    "4gb mobile", "8gb laptop", "16gb tablet", "32gb storage", "64gb memory", "128gb phone",
    "wifi router", "bluetooth speaker", "usb cable", "type c charger", "fast charging", "wireless charging"
]

class FinalAssault50k:
    def __init__(self):
        self.db_path = 'master_products.db'
        
    def assault_add_products(self, products, platform_name):
        """Assault-speed product addition"""
        if not products:
            return 0
            
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        new_count = 0
        
        for product in products:
            url = product.get('product_url', '')
            if not url:
                continue
                
            try:
                cursor.execute('''
                    INSERT OR IGNORE INTO products 
                    (title, price, store_name, product_url, platform, last_updated)
                    VALUES (?, ?, ?, ?, ?, ?)
                ''', (
                    product.get('product_name', 'P')[:80],
                    float(product.get('price', 0)),
                    platform_name,
                    url,
                    platform_name,
                    datetime.now(timezone.utc).isoformat()
                ))
                if cursor.rowcount > 0:
                    new_count += 1
                    
            except Exception:
                continue
        
        conn.commit()
        conn.close()
        return new_count
        
    async def assault_scrape(self, platform_name, scraper_func, search_term, is_async=True):
        """Final assault scraping"""
        try:
            if is_async:
                products = await scraper_func(search_term)
            else:
                products = scraper_func(search_term)
                
            if products:
                new_count = self.assault_add_products(products, platform_name)
                
                if new_count > 0:
                    conn = sqlite3.connect(self.db_path)
                    cursor = conn.cursor()
                    cursor.execute('SELECT COUNT(*) FROM products')
                    total = cursor.fetchone()[0]
                    conn.close()
                    
                    if total % 100 == 0:  # Print every 100th milestone
                        print(f"🚀 {total:,} | +{new_count} from {platform_name}")
                    
                    return total >= 50000
            
            return False
                
        except Exception:
            return False
    
    async def run_final_assault(self):
        """Execute final assault on 50k target"""
        print(f"🚀 FINAL ASSAULT ON 50K TARGET")
        print(f"💥 All scrapers, maximum concurrency")
        print(f"🎯 No mercy until 50,000 distinct products")
        print("=" * 50)
        
        # ALL working scrapers
        scrapers = [
            ("Daraz", lambda t: sync_scrape_daraz(t, max_pages=15), False),
            ("Jeevee", async_scrape_jeevee, True),
            ("Oliz", async_scrape_oliz, True),
            ("Hukut", async_scrape_hukut, True),
            ("Better", async_scrape_better, True),
            ("Neostore", async_scrape_neostore, True),
            ("HardwarePasal", async_scrape_hardwarepasal, True)
        ]
        
        term_index = 0
        
        # Final assault - maximum concurrency
        for assault_wave in range(1, 50000):  # Up to 50k waves if needed
            
            # Massive parallel wave
            tasks = []
            
            for i in range(35):  # 35 concurrent tasks per wave (maximum)
                if term_index >= len(ASSAULT_TERMS):
                    term_index = 0
                
                search_term = ASSAULT_TERMS[term_index]
                platform_name, scraper_func, is_async = scrapers[i % len(scrapers)]
                
                task = self.assault_scrape(platform_name, scraper_func, search_term, is_async)
                tasks.append(task)
                
                term_index += 1
            
            # Execute massive wave
            results = await asyncio.gather(*tasks, return_exceptions=True)
            
            # Check if 50k achieved
            for result in results:
                if result is True:
                    print(f"\\n🚀 FINAL ASSAULT SUCCESSFUL - 50K ACHIEVED!")
                    return True
            
            # Zero delay - maximum assault speed
        
        return False

async def main():
    assault = FinalAssault50k()
    
    try:
        await assault.run_final_assault()
    except Exception as e:
        print(f"🚀 Assault error: {e}")

if __name__ == "__main__":
    asyncio.run(main())