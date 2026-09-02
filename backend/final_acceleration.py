#!/usr/bin/env python3
"""
FINAL ACCELERATION STRATEGY
Deploy multiple parallel scrapers with different approaches to reach 300k target
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

# Import scrapers
from scrapers.daraz.daraz_scraper import sync_scrape_daraz
from scrapers.cgdigital.cgdigital_scraper import async_scrape_cgdigital

# MASSIVE SEARCH TERM EXPANSION - Maximum coverage
MEGA_SEARCH_TERMS = [
    # Electronics - Expanded
    "electronics", "gadget", "device", "tech", "digital", "smart", "wireless", "bluetooth",
    "android", "ios", "windows", "apple", "samsung", "xiaomi", "oppo", "vivo", "oneplus",
    "huawei", "realme", "poco", "redmi", "mi", "iphone", "ipad", "macbook", "imac",
    
    # Computers & Laptops - Brand specific
    "hp", "dell", "lenovo", "acer", "asus", "msi", "alienware", "surface", "thinkpad",
    "pavilion", "inspiron", "ideapad", "vivobook", "zenbook", "gaming pc", "workstation",
    
    # Mobile & Accessories
    "mobile", "cell phone", "smartphone", "feature phone", "mobile case", "screen protector",
    "mobile charger", "power adapter", "usb charger", "wireless charger", "car charger",
    "earphone", "earbuds", "headset", "bluetooth headset", "gaming headset", "airpods",
    
    # Audio & Video
    "speaker", "soundbar", "subwoofer", "amplifier", "music system", "home theater",
    "tv", "television", "led tv", "smart tv", "android tv", "4k tv", "oled", "qled",
    "projector", "home cinema", "dvd player", "blu ray", "streaming device", "chromecast",
    
    # Computing Accessories
    "mouse", "gaming mouse", "wireless mouse", "trackpad", "keyboard", "mechanical keyboard",
    "gaming keyboard", "webcam", "microphone", "usb hub", "docking station", "laptop stand",
    "monitor", "gaming monitor", "4k monitor", "ultrawide", "curved monitor", "display",
    
    # Storage & Memory
    "hard drive", "ssd", "nvme", "external drive", "usb drive", "pen drive", "memory card",
    "sd card", "micro sd", "flash drive", "external storage", "backup drive", "nas",
    "ram", "memory", "ddr4", "ddr5", "graphics card", "gpu", "video card", "rtx", "gtx",
    
    # Fashion - Comprehensive
    "fashion", "clothing", "apparel", "garment", "outfit", "style", "trend", "designer",
    "shirt", "t-shirt", "polo", "formal shirt", "casual shirt", "long sleeve", "short sleeve",
    "jeans", "trousers", "pants", "chinos", "cargo", "shorts", "bermuda", "track pants",
    "dress", "gown", "frock", "maxi dress", "mini dress", "party dress", "casual dress",
    "saree", "lehenga", "salwar kameez", "kurti", "ethnic wear", "traditional", "festive",
    "jacket", "blazer", "coat", "hoodie", "sweatshirt", "cardigan", "sweater", "pullover",
    
    # Footwear - Detailed
    "shoes", "footwear", "sneakers", "running shoes", "sports shoes", "casual shoes",
    "formal shoes", "office shoes", "leather shoes", "canvas shoes", "boots", "ankle boots",
    "sandals", "flip flops", "slippers", "slides", "crocs", "loafers", "oxford", "derby",
    
    # Bags & Accessories
    "bag", "handbag", "purse", "clutch", "sling bag", "tote bag", "shoulder bag",
    "backpack", "rucksack", "laptop bag", "office bag", "school bag", "college bag",
    "travel bag", "duffel bag", "trolley bag", "suitcase", "luggage", "briefcase",
    "wallet", "purse", "card holder", "money clip", "belt", "leather belt", "canvas belt",
    
    # Watches & Jewelry
    "watch", "wristwatch", "smartwatch", "fitness tracker", "digital watch", "analog watch",
    "luxury watch", "sports watch", "diving watch", "chronograph", "apple watch", "fitbit",
    "jewelry", "necklace", "chain", "pendant", "earrings", "bracelet", "ring", "anklet",
    
    # Home & Kitchen - Extensive
    "home", "house", "household", "domestic", "living", "interior", "decor", "furniture",
    "kitchen", "cooking", "culinary", "dining", "tableware", "cookware", "kitchenware",
    "appliances", "electrical", "electronic appliances", "home appliances", "white goods",
    
    # Kitchen Essentials
    "refrigerator", "fridge", "freezer", "microwave", "oven", "toaster", "mixer", "grinder",
    "blender", "food processor", "juicer", "coffee maker", "tea maker", "electric kettle",
    "rice cooker", "pressure cooker", "slow cooker", "air fryer", "sandwich maker", "waffle maker",
    
    # Home Appliances
    "washing machine", "dryer", "dishwasher", "vacuum cleaner", "steam cleaner", "iron",
    "air conditioner", "ac", "cooler", "heater", "humidifier", "dehumidifier", "purifier",
    "fan", "ceiling fan", "table fan", "exhaust fan", "chimney", "water heater", "geyser",
    
    # Furniture & Decor
    "furniture", "chair", "table", "bed", "sofa", "couch", "cabinet", "wardrobe", "dresser",
    "bookshelf", "tv unit", "dining set", "office chair", "gaming chair", "recliner",
    "mattress", "pillow", "cushion", "blanket", "bedsheet", "curtain", "carpet", "rug",
    "lamp", "light", "lighting", "chandelier", "wall art", "photo frame", "mirror", "vase",
    
    # Health & Beauty - Complete
    "health", "healthcare", "wellness", "fitness", "medical", "pharmacy", "medicine",
    "beauty", "cosmetics", "skincare", "haircare", "personal care", "grooming", "hygiene",
    "makeup", "cosmetic", "foundation", "concealer", "lipstick", "lip balm", "mascara",
    "eyeliner", "eyeshadow", "blush", "powder", "nail polish", "nail care", "manicure",
    "skincare", "face cream", "moisturizer", "cleanser", "toner", "serum", "mask",
    "sunscreen", "anti aging", "acne treatment", "face wash", "scrub", "exfoliant",
    "haircare", "shampoo", "conditioner", "hair oil", "hair mask", "hair serum", "styling",
    "hair dryer", "straightener", "curler", "trimmer", "razor", "shaving", "aftershave",
    
    # Personal Care
    "soap", "body wash", "shower gel", "lotion", "body cream", "deodorant", "perfume",
    "cologne", "fragrance", "toothpaste", "toothbrush", "mouthwash", "floss", "oral care",
    
    # Sports & Fitness - Comprehensive
    "sports", "fitness", "gym", "exercise", "workout", "training", "athletic", "outdoor",
    "equipment", "gear", "accessories", "sportswear", "activewear", "athleisure",
    "cricket", "football", "basketball", "volleyball", "tennis", "badminton", "table tennis",
    "swimming", "cycling", "running", "jogging", "marathon", "triathlon", "yoga", "pilates",
    "gym equipment", "weights", "dumbbells", "barbells", "kettlebell", "resistance band",
    "treadmill", "elliptical", "exercise bike", "rowing machine", "home gym", "cross trainer",
    "yoga mat", "fitness mat", "foam roller", "protein", "supplement", "nutrition", "vitamins",
    
    # Books & Education - Detailed
    "books", "reading", "literature", "education", "learning", "study", "academic",
    "textbook", "reference", "guide", "manual", "dictionary", "encyclopedia", "atlas",
    "novel", "fiction", "non-fiction", "biography", "history", "science", "technology",
    "children book", "kids book", "comic", "magazine", "journal", "notebook", "diary",
    "stationery", "office supplies", "school supplies", "pen", "pencil", "marker", "highlighter",
    "calculator", "ruler", "compass", "protractor", "geometry", "art supplies", "drawing",
    
    # Baby & Kids - Complete
    "baby", "infant", "toddler", "kids", "children", "nursery", "maternity", "parenting",
    "baby care", "feeding", "diaper", "baby food", "formula", "bottle", "pacifier",
    "stroller", "pram", "car seat", "high chair", "baby monitor", "baby bath", "baby oil",
    "toys", "games", "educational toys", "learning toys", "puzzle", "blocks", "doll",
    "action figure", "remote control", "electronic toys", "outdoor toys", "indoor toys",
    
    # Automotive - Extensive
    "automotive", "car", "vehicle", "automobile", "bike", "motorcycle", "scooter",
    "car accessories", "auto parts", "spare parts", "car care", "car cleaning", "car wash",
    "car polish", "car wax", "car shampoo", "tire cleaner", "dashboard cleaner",
    "car charger", "car mount", "phone holder", "gps", "dashcam", "car camera",
    "car cover", "seat cover", "steering cover", "floor mat", "car mat", "mudflap",
    "car perfume", "air freshener", "car vacuum", "jump starter", "car battery", "inverter",
    
    # General High-Volume Terms
    "accessories", "parts", "components", "tools", "equipment", "supplies", "materials",
    "products", "items", "goods", "merchandise", "deals", "offers", "sale", "discount",
    "new", "latest", "trending", "popular", "best", "top", "premium", "quality", "branded"
]

class AcceleratedScraper:
    def __init__(self):
        self.db_path = 'accelerated_products.db'
        self.setup_database()
        self.success_count = 0
        self.error_count = 0
        
    def setup_database(self):
        """Setup accelerated scraper database"""
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
                search_term TEXT
            )
        ''')
        self.conn.commit()
        
    def store_products(self, products, store_name, search_term):
        """Fast product storage"""
        if not products:
            return 0
            
        cursor = self.conn.cursor()
        stored = 0
        
        for product in products:
            try:
                cursor.execute('''
                    INSERT OR REPLACE INTO products 
                    (title, price, original_price, discount_percent, image_url, 
                     store_name, product_url, category, scraped_at, platform, search_term)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
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
                    search_term
                ))
                stored += 1
            except:
                continue
                
        self.conn.commit()
        return stored
    
    async def accelerated_scrape(self, search_term):
        """Try CGDigital with aggressive settings"""
        try:
            products = await async_scrape_cgdigital(search_term)
            
            if products and len(products) > 0:
                stored = self.store_products(products, "CGDigital", search_term)
                self.success_count += 1
                return stored
            else:
                self.error_count += 1
                return 0
                
        except Exception:
            self.error_count += 1
            return 0
    
    async def run_acceleration(self):
        """Run accelerated scraping with maximum terms"""
        print("🚀 FINAL ACCELERATION - MAXIMUM SPEED")
        print("=" * 60)
        print(f"🔍 Processing {len(MEGA_SEARCH_TERMS):,} search terms")
        print("⚡ Focus on CGDigital (most reliable)")
        print("=" * 60)
        
        start_time = time.time()
        total_products = 0
        
        # Process in parallel batches for maximum speed
        batch_size = 3
        
        for i in range(0, len(MEGA_SEARCH_TERMS), batch_size):
            batch = MEGA_SEARCH_TERMS[i:i+batch_size]
            batch_num = i // batch_size + 1
            total_batches = (len(MEGA_SEARCH_TERMS) + batch_size - 1) // batch_size
            
            print(f"\n🔥 BATCH {batch_num}/{total_batches}: {', '.join(batch)}")
            
            # Execute batch in parallel
            tasks = [self.accelerated_scrape(term) for term in batch]
            results = await asyncio.gather(*tasks, return_exceptions=True)
            
            # Count results
            batch_total = sum(r for r in results if isinstance(r, int))
            total_products += batch_total
            
            print(f"  📊 Batch: {batch_total} products | Total: {total_products:,}")
            print(f"  📈 Success: {self.success_count}, Errors: {self.error_count}")
            
            # Brief pause
            await asyncio.sleep(0.5)
            
            # Progress update every 20 batches
            if batch_num % 20 == 0:
                elapsed = time.time() - start_time
                rate = total_products / (elapsed / 60) if elapsed > 0 else 0
                print(f"\n📊 PROGRESS: {total_products:,} products in {elapsed/60:.1f} min ({rate:.0f}/min)")
        
        # Final statistics
        elapsed_time = time.time() - start_time
        
        print("\n" + "=" * 60)
        print("🚀 ACCELERATION COMPLETE!")
        print(f"⏱️  Time: {elapsed_time/60:.1f} minutes")
        print(f"📊 Total products: {total_products:,}")
        print(f"🎯 Success rate: {(self.success_count/(self.success_count+self.error_count))*100:.1f}%")
        
        # Database stats
        cursor = self.conn.cursor()
        cursor.execute("SELECT COUNT(*) FROM products")
        db_total = cursor.fetchone()[0]
        
        file_size = os.path.getsize(self.db_path) / (1024 * 1024)
        
        print(f"💾 Database: {db_total:,} products ({file_size:.1f} MB)")
        
        self.conn.close()
        
        print("\n✅ Final acceleration completed successfully!")
        return db_total

async def main():
    """Run final acceleration"""
    scraper = AcceleratedScraper()
    
    try:
        await scraper.run_acceleration()
    except Exception as e:
        print(f"❌ Acceleration error: {e}")

if __name__ == "__main__":
    asyncio.run(main())