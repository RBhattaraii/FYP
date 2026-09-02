#!/usr/bin/env python3
"""
ULTRA AGGRESSIVE 50K FINISHER
Maximum parallel scraping to cross 50k finish line
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

# Ultra-aggressive terms - maximum diversity and specificity
ULTRA_TERMS = [
    # Highly specific product searches
    "samsung galaxy a54 5g", "iphone 14 pro max", "xiaomi redmi note 12", "oppo reno 8",
    "dell inspiron 15 3000", "hp pavilion gaming", "lenovo ideapad 3", "asus vivobook 15",
    "sony wh-1000xm4", "airpods pro 2nd gen", "jbl tune 760nc", "boat airdopes 441",
    
    # Specific fashion items
    "levi strauss jeans", "nike air force 1", "adidas ultraboost 22", "puma rs-x",
    "polo ralph lauren", "tommy hilfiger shirt", "calvin klein underwear", "levis t shirt",
    
    # Appliance model numbers and brands
    "lg 260l refrigerator", "samsung 7kg washing", "whirlpool microwave", "bajaj mixer 750w",
    "philips air fryer", "prestige pressure cooker", "pigeon induction cooktop", "crompton fan",
    
    # Electronics with specifications  
    "64gb pendrive", "1tb external hard", "32gb memory card", "wireless mouse", 
    "mechanical keyboard", "webcam 1080p", "bluetooth speaker 20w", "power bank 10000mah",
    
    # Beauty brand specific
    "lakme foundation", "maybelline lipstick", "loreal shampoo", "nivea cream",
    "garnier face wash", "dove soap", "head shoulders", "pantene conditioner",
    
    # Home specific items
    "cotton bed sheet", "memory foam pillow", "led ceiling light", "wall clock digital",
    "dining table 4 seater", "office chair ergonomic", "study table wooden", "wardrobe 3 door",
    
    # Kitchen essentials
    "non stick tawa", "steel kadhai", "glass bowl set", "ceramic dinner set",
    "stainless steel bottle", "lunch box steel", "tea kettle", "coffee mug ceramic",
    
    # Baby and kids specific
    "pampers diapers", "johnson baby oil", "cerelac baby food", "horlicks growth",
    "school bag disney", "lunch box kids", "water bottle kids", "shoes school black",
    
    # Sports brand specific
    "nike running shoes", "adidas football", "puma tracksuit", "reebok gym shoes",
    "decathlon sports", "yonex badminton", "cosco cricket bat", "nivia volleyball",
    
    # Health and wellness
    "protein powder 1kg", "whey isolate", "vitamin d3 tablets", "omega 3 capsules",
    "blood pressure monitor", "digital thermometer", "glucometer strips", "pulse oximeter",
    
    # Automotive accessories
    "car mobile holder", "dash cam full hd", "car air freshener", "seat cover leather",
    "steering wheel cover", "car charger fast", "bike helmet full face", "car vacuum cleaner",
    
    # Books and education
    "ncert books class", "competitive exam books", "english grammar book", "dictionary english",
    "atlas world map", "calculator scientific", "geometry box set", "pen refill blue",
    
    # Festival and occasion
    "diwali decoration", "christmas lights", "birthday party supplies", "wedding gift items",
    "rakhi for brother", "mothers day gift", "valentine gift girlfriend", "anniversary gift wife",
    
    # Seasonal clothing
    "winter jacket men", "sweater women wool", "cotton kurta men", "silk saree women",
    "shorts summer men", "maxi dress women", "formal blazer men", "ethnic wear women",
    
    # Tech accessories
    "phone case transparent", "tempered glass screen", "car mount phone", "laptop cooling pad",
    "usb hub 4 port", "hdmi cable 2m", "extension cord 5m", "adapter type c",
    
    # Grooming and personal care
    "razor blades", "shaving cream", "beard oil", "hair gel strong",
    "deodorant spray men", "perfume women", "nail cutter steel", "tweezers eyebrow",
    
    # Work from home essentials
    "laptop stand adjustable", "webcam logitech", "microphone usb", "ring light led",
    "desk organizer", "cable management", "monitor riser", "keyboard wrist rest"
]

class UltraAggressive50k:
    def __init__(self):
        self.db_path = 'master_products.db'
        
    def ultra_fast_add(self, products, platform_name, search_term):
        """Ultra-fast product insertion"""
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
                    product.get('product_name', 'Product')[:150],
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
        
    async def ultra_scrape(self, platform_name, scraper_func, search_term, is_async=True):
        """Ultra-fast scraping"""
        try:
            if is_async:
                products = await scraper_func(search_term)
            else:
                products = scraper_func(search_term)
                
            if products:
                new_count = self.ultra_fast_add(products, platform_name, search_term)
                
                # Check current total
                conn = sqlite3.connect(self.db_path)
                cursor = conn.cursor()
                cursor.execute('SELECT COUNT(*) FROM products')
                total = cursor.fetchone()[0]
                conn.close()
                
                if new_count > 0:
                    progress = (total / 50000) * 100
                    print(f"⚡ {platform_name}: +{new_count} | Total: {total:,} ({progress:.1f}%)")
                
                return total >= 50000
            else:
                return False
                
        except Exception:
            return False
    
    async def run_ultra_aggressive(self):
        """Run ultra-aggressive parallel scraping"""
        print(f"⚡ ULTRA AGGRESSIVE 50K FINISHER")
        print(f"🎯 Maximum parallel execution")
        print("=" * 40)
        
        scrapers = [
            ("Daraz", lambda t: sync_scrape_daraz(t, max_pages=10), False),
            ("Jeevee", async_scrape_jeevee, True),
            ("Oliz", async_scrape_oliz, True),
            ("Hukut", async_scrape_hukut, True)
        ]
        
        term_index = 0
        
        for ultra_round in range(1, 1000):  # Up to 1000 ultra rounds
            print(f"\\n⚡ ULTRA ROUND {ultra_round}")
            
            # Create massive parallel tasks
            tasks = []
            
            for i in range(20):  # 20 parallel tasks per round
                if term_index >= len(ULTRA_TERMS):
                    term_index = 0
                
                search_term = ULTRA_TERMS[term_index]
                platform_name, scraper_func, is_async = scrapers[i % len(scrapers)]
                
                task = self.ultra_scrape(platform_name, scraper_func, search_term, is_async)
                tasks.append(task)
                
                term_index += 1
            
            # Execute all tasks in parallel
            results = await asyncio.gather(*tasks, return_exceptions=True)
            
            # Check if 50k reached
            for result in results:
                if result is True:
                    print(f"\\n🎉🎉🎉 50K ACHIEVED BY ULTRA SCRAPER! 🎉🎉🎉")
                    return True
            
            # No delay - maximum speed
        
        return False

async def main():
    ultra = UltraAggressive50k()
    
    try:
        success = await ultra.run_ultra_aggressive()
        if success:
            print(f"\\n🏆 ULTRA SCRAPER REACHED 50K!")
    except Exception as e:
        print(f"❌ Ultra error: {e}")

if __name__ == "__main__":
    asyncio.run(main())