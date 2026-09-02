#!/usr/bin/env python3
"""
COMPREHENSIVE MASS SCRAPER - Target 300k+ Products
Scrapes ALL available websites with intelligent storage management
"""

import asyncio
import asyncpg
import sys
import os
import json
import sqlite3
from datetime import datetime, timezone
from pymongo import MongoClient
from pymongo.errors import ServerSelectionTimeoutError
import time

# Add paths for imports
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))
sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'scrapers'))

# Import ALL scrapers
from scrapers.daraz.daraz_scraper import sync_scrape_daraz, async_scrape_daraz
from scrapers.cgdigital.cgdigital_scraper import async_scrape_cgdigital
from scrapers.better.better_scraper import async_scrape_better
from scrapers.hardwarepasal.hardwarepasal_scraper import async_scrape_hardwarepasal
from scrapers.hukut.hukut_scraper import async_scrape_hukut
from scrapers.jeevee.jeevee_scraper import async_scrape_jeevee
from scrapers.neostore.neostore_scraper import async_scrape_neostore
from scrapers.oliz.oliz_scraper import async_scrape_oliz
from scrapers.ufonepal.ufonepal_scraper import async_scrape_ufonepal

# Database URLs
SUPABASE_URL = "postgresql://postgres.cukfnnjuofbvsrwwkdsh:gKaBwfxiaFauuKyS@aws-1-ap-northeast-1.pooler.supabase.com:6543/postgres"
MONGO_URL = "mongodb://localhost:27017/"

# TARGET: 300k MINIMUM - AIM FOR 1 MILLION+ products across 10 categories
TARGET_PRODUCTS_MIN = 300000
TARGET_PRODUCTS_MAX = 1000000
PRODUCTS_PER_PLATFORM_MIN = TARGET_PRODUCTS_MIN // 9  # ~33k per platform minimum
PRODUCTS_PER_PLATFORM_MAX = TARGET_PRODUCTS_MAX // 9  # ~110k per platform maximum

# 10 STRATEGIC CATEGORIES for Nepali e-commerce - EXPANDED FOR MAXIMUM COVERAGE
SEARCH_CATEGORIES = {
    "Electronics": [
        "laptop", "computer", "desktop", "gaming laptop", "macbook", "hp laptop", "dell laptop", "lenovo laptop", "acer laptop", "asus laptop",
        "smartphone", "mobile phone", "iphone", "samsung phone", "android phone", "5g phone", "xiaomi phone", "oppo phone", "vivo phone", "oneplus phone",
        "tablet", "ipad", "android tablet", "gaming tablet", "tab", "samsung tablet",
        "headphones", "earphones", "wireless headphones", "bluetooth headphones", "airpods", "earbuds", "gaming headset", "sony headphones",
        "speaker", "bluetooth speaker", "wireless speaker", "sound system", "home theater", "soundbar", "portable speaker", "smart speaker",
        "smartwatch", "fitness tracker", "apple watch", "samsung watch", "mi band", "fitness band", "smart band"
    ],
    "Home_Appliances": [
        "refrigerator", "fridge", "washing machine", "microwave", "oven", "air conditioner", "ac", "split ac", "window ac",
        "vacuum cleaner", "water purifier", "electric kettle", "rice cooker", "blender", "mixer", "grinder", "pressure cooker",
        "iron", "hair dryer", "fan", "ceiling fan", "table fan", "heater", "air cooler", "room heater", "water heater", "geyser",
        "dishwasher", "chimney", "induction cooktop", "gas stove", "electric cooker", "toaster", "sandwich maker"
    ],
    "Fashion_Clothing": [
        "shirt", "t-shirt", "jeans", "trouser", "pant", "dress", "saree", "kurta", "jacket", "sweater", "hoodie", "cardigan",
        "shoes", "sandals", "sneakers", "formal shoes", "boots", "slippers", "sports shoes", "running shoes", "casual shoes",
        "bag", "backpack", "handbag", "laptop bag", "school bag", "travel bag", "wallet", "purse", "belt", "watch", "sunglasses",
        "ethnic wear", "lehenga", "salwar kameez", "sherwani", "blazer", "coat", "winter wear", "inner wear", "undergarments"
    ],
    "Books_Stationery": [
        "book", "novel", "textbook", "story book", "children book", "educational book", "reference book", "competition book",
        "notebook", "diary", "pen", "pencil", "marker", "highlighter", "eraser", "ruler", "calculator", "geometry box",
        "school bag", "pencil box", "file", "folder", "paper", "chart paper", "drawing book", "coloring book", "sketch book",
        "office supplies", "stapler", "paper clip", "sticky notes", "whiteboard", "blackboard"
    ],
    "Health_Beauty": [
        "face cream", "moisturizer", "face wash", "cleanser", "toner", "serum", "sunscreen", "night cream", "eye cream",
        "shampoo", "conditioner", "hair oil", "hair mask", "soap", "body wash", "body lotion", "hand cream", "lip balm",
        "toothpaste", "toothbrush", "mouthwash", "dental care", "oral care", "perfume", "deodorant", "body spray",
        "makeup", "lipstick", "foundation", "concealer", "mascara", "eyeliner", "kajal", "nail polish", "compact powder",
        "hair care", "skin care", "beauty products", "cosmetics", "personal care", "hygiene products"
    ],
    "Sports_Fitness": [
        "gym equipment", "dumbbell", "barbell", "weight plate", "bench press", "treadmill", "exercise bike", "elliptical",
        "yoga mat", "yoga block", "resistance band", "skipping rope", "pull up bar", "push up bar", "ab roller",
        "football", "basketball", "volleyball", "cricket bat", "cricket ball", "badminton racket", "tennis racket",
        "table tennis", "ping pong", "chess board", "carrom board", "sports shoes", "running shoes", "track suit",
        "sports wear", "gym wear", "fitness tracker", "smart watch", "heart rate monitor", "protein powder", "supplement"
    ],
    "Automotive": [
        "car accessories", "bike accessories", "helmet", "car charger", "bike cover", "car cover", "seat cover",
        "car perfume", "air freshener", "steering cover", "steering wheel cover", "gear cover", "bike lock", "car lock",
        "car vacuum", "car cleaner", "car polish", "car wax", "car mat", "floor mat", "dashboard cover",
        "mobile holder", "phone holder", "car mount", "bike mount", "headlight", "tail light", "indicator", "horn",
        "car tool kit", "bike tool kit", "tire pressure gauge", "jump starter", "car battery", "bike battery"
    ],
    "Toys_Games": [
        "toy", "soft toy", "teddy bear", "doll", "barbie doll", "action figure", "car toy", "bike toy", "truck toy",
        "puzzle", "jigsaw puzzle", "board game", "card game", "chess", "ludo", "snake ladder", "monopoly", "scrabble",
        "remote control car", "rc car", "drone", "helicopter toy", "robot toy", "building blocks", "lego", "construction toy",
        "educational toy", "learning toy", "baby toy", "infant toy", "toddler toy", "kids toy", "outdoor toy", "indoor toy",
        "video game", "gaming console", "gaming accessories", "controller", "joystick", "gaming keyboard", "gaming mouse"
    ],
    "Kitchen_Dining": [
        "cookware", "pressure cooker", "non-stick pan", "frying pan", "sauce pan", "kadhai", "tawa", "griddle",
        "dinner set", "plate set", "bowl set", "glass set", "cup set", "mug set", "cutlery set", "spoon set", "fork set",
        "kitchen utensils", "spatula", "ladle", "tongs", "whisk", "can opener", "bottle opener", "peeler", "grater",
        "spice box", "masala box", "storage container", "lunch box", "tiffin box", "water bottle", "thermos flask",
        "kitchen appliances", "mixer grinder", "food processor", "hand blender", "electric kettle", "sandwich maker",
        "chopping board", "knife set", "kitchen knife", "vegetable cutter", "kitchen scale", "measuring cup"
    ],
    "Computer_Accessories": [
        "mouse", "wireless mouse", "gaming mouse", "optical mouse", "computer mouse", "laptop mouse", "bluetooth mouse",
        "keyboard", "wireless keyboard", "gaming keyboard", "mechanical keyboard", "membrane keyboard", "bluetooth keyboard",
        "webcam", "web camera", "hd webcam", "usb webcam", "laptop webcam", "computer camera", "video camera",
        "usb cable", "charging cable", "data cable", "micro usb", "type c cable", "lightning cable", "hdmi cable",
        "hard drive", "external hard drive", "portable hard drive", "hdd", "ssd", "external ssd", "usb drive", "pen drive",
        "ram", "memory", "ddr4 ram", "laptop ram", "desktop ram", "graphics card", "gpu", "video card", "sound card",
        "monitor", "computer monitor", "gaming monitor", "led monitor", "lcd monitor", "4k monitor", "ultrawide monitor",
        "printer", "inkjet printer", "laser printer", "all in one printer", "scanner", "photocopier", "3d printer",
        "router", "wifi router", "modem", "network switch", "ethernet cable", "lan cable", "wifi adapter", "bluetooth adapter",
        "power bank", "portable charger", "mobile charger", "laptop charger", "phone charger", "wireless charger", "car charger",
        "usb hub", "usb splitter", "card reader", "memory card", "sd card", "micro sd", "flash drive", "otg cable"
    ]
}

class StorageManager:
    def __init__(self):
        self.supabase_conn = None
        self.mongo_client = None
        self.mongo_db = None
        self.local_db = None
        self.storage_stats = {
            'supabase': 0,
            'mongodb': 0,
            'local': 0,
            'total': 0
        }

    async def initialize_storage(self):
        """Initialize all storage options"""
        # 1. Try Supabase (PostgreSQL)
        try:
            self.supabase_conn = await asyncpg.connect(SUPABASE_URL, statement_cache_size=0)
            print("✅ Connected to Supabase (PostgreSQL)")
        except Exception as e:
            print(f"❌ Supabase connection failed: {e}")
            
        # 2. Try MongoDB
        try:
            self.mongo_client = MongoClient(MONGO_URL, serverSelectionTimeoutMS=5000)
            self.mongo_client.server_info()  # Test connection
            self.mongo_db = self.mongo_client['pricepilot']
            print("✅ Connected to MongoDB")
        except Exception as e:
            print(f"❌ MongoDB connection failed: {e}")
            
        # 3. Setup local SQLite as fallback
        try:
            self.local_db = sqlite3.connect('local_products.db')
            self.local_db.execute('''
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
            self.local_db.commit()
            print("✅ Local SQLite database ready")
        except Exception as e:
            print(f"❌ Local database setup failed: {e}")

    async def store_products_batch(self, products, store_name):
        """Store products with intelligent storage management"""
        if not products:
            return 0
            
        stored_count = 0
        
        # Try Supabase first (if available and under limits)
        if self.supabase_conn and self.storage_stats['supabase'] < 500000:  # Increase limit
            try:
                stored = await self._store_supabase(products, store_name)
                if stored > 0:
                    self.storage_stats['supabase'] += stored
                    self.storage_stats['total'] += stored
                    stored_count += stored
                    print(f"  📊 Supabase: {stored} products | Total: {self.storage_stats['supabase']}")
                    if stored == len(products):
                        return stored_count
            except Exception as e:
                print(f"  ⚠️  Supabase storage failed: {e}")
                
        # Try MongoDB next
        if self.mongo_db and self.storage_stats['mongodb'] < 500000:  # Increase limit
            try:
                remaining = [p for i, p in enumerate(products) if i >= stored_count]
                if remaining:
                    stored = await self._store_mongodb(remaining, store_name)
                    if stored > 0:
                        self.storage_stats['mongodb'] += stored
                        self.storage_stats['total'] += stored
                        stored_count += stored
                        print(f"  📊 MongoDB: {stored} products | Total: {self.storage_stats['mongodb']}")
                        if stored_count == len(products):
                            return stored_count
            except Exception as e:
                print(f"  ⚠️  MongoDB storage failed: {e}")
                
        # Store remaining in local SQLite
        if self.local_db:
            try:
                remaining = [p for i, p in enumerate(products) if i >= stored_count]
                if remaining:
                    stored = self._store_local(remaining, store_name)
                    if stored > 0:
                        self.storage_stats['local'] += stored
                        self.storage_stats['total'] += stored
                        stored_count += stored
                        print(f"  📊 Local: {stored} products | Total: {self.storage_stats['local']}")
            except Exception as e:
                print(f"  ⚠️  Local storage failed: {e}")
                
        return stored_count

    async def _store_supabase(self, products, store_name):
        """Store in Supabase PostgreSQL"""
        stored = 0
        for product in products:
            try:
                await self.supabase_conn.execute("""
                    INSERT INTO products (
                        title, price, original_price, discount_percent, 
                        image_url, store_name, product_url, category, 
                        scraped_at, search_vector
                    ) VALUES ($1, $2, $3, $4, $5, $6, $7, $8, $9, to_tsvector('english', $1))
                    ON CONFLICT (product_url) DO UPDATE SET
                        price = EXCLUDED.price,
                        original_price = EXCLUDED.original_price,
                        discount_percent = EXCLUDED.discount_percent,
                        scraped_at = EXCLUDED.scraped_at
                """, 
                    product.get('product_name', 'Unknown Product'),
                    float(product.get('price', 0)),
                    float(product.get('original_price', 0)) if product.get('original_price') else None,
                    float(product.get('discount_percentage', 0)) if product.get('discount_percentage') else None,
                    product.get('image_url', ''),
                    store_name,
                    product.get('product_url', ''),
                    product.get('category', 'General'),
                    datetime.now(timezone.utc)
                )
                stored += 1
            except Exception as e:
                continue
        return stored

    async def _store_mongodb(self, products, store_name):
        """Store in MongoDB"""
        try:
            collection = self.mongo_db['products']
            documents = []
            
            for product in products:
                doc = {
                    'title': product.get('product_name', 'Unknown Product'),
                    'price': float(product.get('price', 0)),
                    'original_price': float(product.get('original_price', 0)) if product.get('original_price') else None,
                    'discount_percent': float(product.get('discount_percentage', 0)) if product.get('discount_percentage') else None,
                    'image_url': product.get('image_url', ''),
                    'store_name': store_name,
                    'product_url': product.get('product_url', ''),
                    'category': product.get('category', 'General'),
                    'scraped_at': datetime.now(timezone.utc),
                    'platform': product.get('platform', store_name.lower())
                }
                documents.append(doc)
                
            if documents:
                collection.insert_many(documents, ordered=False)
                return len(documents)
        except Exception as e:
            print(f"MongoDB insert error: {e}")
            
        return 0

    def _store_local(self, products, store_name):
        """Store in local SQLite"""
        stored = 0
        cursor = self.local_db.cursor()
        
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
                    product.get('category', 'General'),
                    datetime.now(timezone.utc).isoformat(),
                    product.get('platform', store_name.lower()),
                    product.get('search_term', '')
                ))
                stored += 1
            except Exception as e:
                continue
                
        self.local_db.commit()
        return stored

    def get_storage_summary(self):
        """Get storage distribution summary"""
        return self.storage_stats

    async def cleanup(self):
        """Close all connections"""
        if self.supabase_conn:
            await self.supabase_conn.close()
        if self.mongo_client:
            self.mongo_client.close()
        if self.local_db:
            self.local_db.close()

class MassScraper:
    def __init__(self):
        self.storage_manager = StorageManager()
        self.scraped_stats = {}
        
    async def initialize(self):
        """Initialize storage and connections"""
        await self.storage_manager.initialize_storage()
        
    async def scrape_platform_comprehensive(self, platform_name, scraper_func, is_sync=False):
        """Scrape a platform comprehensively across all categories - AIM FOR MAXIMUM PRODUCTS"""
        print(f"\n🔥 SCRAPING {platform_name.upper()} - TARGET: {PRODUCTS_PER_PLATFORM_MIN:,}-{PRODUCTS_PER_PLATFORM_MAX:,} products")
        platform_total = 0
        
        # Flatten all search terms from all categories
        all_search_terms = []
        for category, terms in SEARCH_CATEGORIES.items():
            for term in terms:
                all_search_terms.append((term, category))
        
        print(f"  📋 {len(all_search_terms)} search terms across 10 categories")
        
        # AGGRESSIVE SCRAPING - Multiple passes with different page counts
        max_passes = 3  # Do multiple passes to get maximum products
        pages_per_pass = [10, 20, 30]  # Increase pages per pass
        
        for pass_num in range(max_passes):
            if platform_total >= PRODUCTS_PER_PLATFORM_MAX:
                print(f"  🎯 Platform maximum reached: {platform_total:,} products")
                break
                
            print(f"\n  🚀 PASS {pass_num + 1}: Using {pages_per_pass[pass_num]} pages per search")
            
            # Scrape systematically
            for i, (search_term, category) in enumerate(all_search_terms, 1):
                if platform_total >= PRODUCTS_PER_PLATFORM_MAX:
                    break
                    
                print(f"    🔍 [{i}/{len(all_search_terms)}] '{search_term}' ({category})")
                
                try:
                    if is_sync:
                        # For sync scrapers like Daraz - use more pages
                        products = scraper_func(search_term, max_pages=pages_per_pass[pass_num])
                    else:
                        # For async scrapers - multiple calls if possible
                        products = await scraper_func(search_term)
                    
                    if products:
                        # Add category to products
                        for product in products:
                            product['category'] = category
                            product['search_term'] = search_term
                        
                        stored = await self.storage_manager.store_products_batch(products, platform_name)
                        platform_total += stored
                        
                        print(f"      ✅ {len(products)} found, {stored} stored | Platform total: {platform_total:,}")
                    else:
                        print(f"      ❌ No products found")
                        
                    # Shorter delay for aggressive scraping
                    await asyncio.sleep(0.5)
                    
                except Exception as e:
                    print(f"      ❌ Error scraping '{search_term}': {e}")
                    continue
        
        self.scraped_stats[platform_name] = platform_total
        print(f"🎯 {platform_name} COMPLETE: {platform_total:,} products scraped")
        return platform_total

    async def run_mass_scraping(self):
        """Execute comprehensive mass scraping - AIM FOR 1 MILLION PRODUCTS"""
        print("🚀 STARTING MASS SCRAPING - MINIMUM: 300k, TARGET: 1 MILLION+ PRODUCTS")
        print("=" * 70)
        
        start_time = time.time()
        
        # Define all scraping targets - prioritize by reliability and size
        scraping_plan = [
            ("Daraz", sync_scrape_daraz, True),  # Largest platform first
            ("CGDigital", async_scrape_cgdigital, False),
            ("Oliz", async_scrape_oliz, False),  # Move up in priority
            ("Hukut", async_scrape_hukut, False),
            ("Better", async_scrape_better, False),
            ("HardwarePasal", async_scrape_hardwarepasal, False),
            ("Jeevee", async_scrape_jeevee, False),
            ("Neostore", async_scrape_neostore, False),
            ("UFONepal", async_scrape_ufonepal, False),
        ]
        
        total_scraped = 0
        
        # Execute scraping for each platform
        for platform_name, scraper_func, is_sync in scraping_plan:
            try:
                platform_count = await self.scrape_platform_comprehensive(
                    platform_name, scraper_func, is_sync
                )
                total_scraped += platform_count
                
                # Progress update
                progress_min = (total_scraped / TARGET_PRODUCTS_MIN) * 100
                progress_max = (total_scraped / TARGET_PRODUCTS_MAX) * 100
                print(f"\n📊 PROGRESS: {total_scraped:,} products")
                print(f"   Minimum target: {progress_min:.1f}% ({TARGET_PRODUCTS_MIN:,})")
                print(f"   Maximum target: {progress_max:.1f}% ({TARGET_PRODUCTS_MAX:,})")
                
                # Continue until we reach at least minimum or exceed maximum
                if total_scraped >= TARGET_PRODUCTS_MAX:
                    print("🎉 MAXIMUM TARGET EXCEEDED! Amazing scraping performance!")
                    break
                    
            except Exception as e:
                print(f"❌ Platform {platform_name} failed: {e}")
                continue
        
        # Final statistics
        elapsed_time = time.time() - start_time
        storage_stats = self.storage_manager.get_storage_summary()
        
        print("\n" + "=" * 70)
        print("🎉 MASS SCRAPING COMPLETE!")
        print(f"⏱️  Time taken: {elapsed_time/3600:.2f} hours ({elapsed_time/60:.1f} minutes)")
        print(f"📊 Total products: {total_scraped:,}")
        
        if total_scraped >= TARGET_PRODUCTS_MAX:
            print(f"🏆 EXCEEDED MAXIMUM TARGET: {(total_scraped/TARGET_PRODUCTS_MAX)*100:.1f}%")
        elif total_scraped >= TARGET_PRODUCTS_MIN:
            print(f"✅ MINIMUM TARGET ACHIEVED: {(total_scraped/TARGET_PRODUCTS_MIN)*100:.1f}%")
        else:
            print(f"⚠️  Target progress: {(total_scraped/TARGET_PRODUCTS_MIN)*100:.1f}%")
        
        print("\n📋 PLATFORM BREAKDOWN:")
        for platform, count in self.scraped_stats.items():
            percentage = (count / total_scraped) * 100 if total_scraped > 0 else 0
            print(f"  • {platform}: {count:,} products ({percentage:.1f}%)")
            
        print("\n💾 STORAGE DISTRIBUTION:")
        print(f"  • Supabase: {storage_stats['supabase']:,} products")
        print(f"  • MongoDB: {storage_stats['mongodb']:,} products")
        print(f"  • Local SQLite: {storage_stats['local']:,} products")
        print(f"  • Total stored: {storage_stats['total']:,} products")
        
        if total_scraped >= TARGET_PRODUCTS_MIN:
            print("\n✅ Your PricePilot app is now PRODUCTION READY!")
            print("🛍️  Comprehensive product database with real data from 9+ Nepali platforms!")
            print("🚀 Ready to compete with major e-commerce aggregators!")
        else:
            print(f"\n⚠️  Need {TARGET_PRODUCTS_MIN - total_scraped:,} more products to reach minimum target")

    async def cleanup(self):
        """Clean up resources"""
        await self.storage_manager.cleanup()

async def main():
    """Main execution function"""
    scraper = MassScraper()
    
    try:
        await scraper.initialize()
        await scraper.run_mass_scraping()
    except KeyboardInterrupt:
        print("\n⚠️  Scraping interrupted by user")
    except Exception as e:
        print(f"\n❌ Critical error: {e}")
    finally:
        await scraper.cleanup()
    
    print("\n🚀 Mass scraping session completed!")

if __name__ == "__main__":
    asyncio.run(main())