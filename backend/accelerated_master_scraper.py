#!/usr/bin/env python3
"""
ACCELERATED MASTER SCRAPER
Fast addition of unique products to master database
GOAL: Reach 50k+ unique products quickly
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

# Import all working scrapers
from scrapers.daraz.daraz_scraper import sync_scrape_daraz
from scrapers.better.better_scraper import async_scrape_better
from scrapers.hardwarepasal.hardwarepasal_scraper import async_scrape_hardwarepasal
from scrapers.hukut.hukut_scraper import async_scrape_hukut
from scrapers.jeevee.jeevee_scraper import async_scrape_jeevee
from scrapers.neostore.neostore_scraper import async_scrape_neostore
from scrapers.oliz.oliz_scraper import async_scrape_oliz

# Expanded search terms for maximum coverage
AGGRESSIVE_SEARCH_TERMS = [
    # Electronics - comprehensive coverage
    "laptop", "notebook", "computer", "pc", "desktop", "workstation", "gaming laptop",
    "mobile", "phone", "smartphone", "cellphone", "android", "iphone", "samsung phone",
    "tablet", "ipad", "android tablet", "kindle", "e-reader",
    "headphone", "headset", "earphone", "earbuds", "airpods", "wireless earbuds",
    "speaker", "bluetooth speaker", "sound bar", "home theater", "audio system",
    "mouse", "wireless mouse", "gaming mouse", "optical mouse", "trackpad",
    "keyboard", "mechanical keyboard", "wireless keyboard", "gaming keyboard",
    "monitor", "display", "led monitor", "gaming monitor", "4k monitor", "curved monitor",
    "webcam", "camera", "security camera", "action camera", "digital camera",
    "printer", "scanner", "projector", "ups", "power bank", "external battery",
    "hard drive", "ssd", "external drive", "memory card", "usb drive", "storage",
    "router", "modem", "wifi", "network", "ethernet cable", "hdmi cable", "usb cable",
    
    # Popular brands
    "apple", "samsung", "xiaomi", "oppo", "vivo", "realme", "oneplus", "huawei", "nokia",
    "sony", "lg", "panasonic", "canon", "nikon", "hp", "dell", "lenovo", "acer", "asus",
    "msi", "gigabyte", "corsair", "logitech", "razer", "steelseries", "hyperx",
    
    # Fashion comprehensive
    "shirt", "t-shirt", "polo shirt", "formal shirt", "casual shirt", "long sleeve",
    "jeans", "pants", "trousers", "chinos", "cargo pants", "formal pants",
    "dress", "casual dress", "formal dress", "maxi dress", "mini dress", "party dress",
    "jacket", "coat", "blazer", "hoodie", "sweater", "cardigan", "winter jacket",
    "shoes", "sneakers", "running shoes", "casual shoes", "formal shoes", "boots",
    "sandals", "slippers", "flip flops", "high heels", "flat shoes", "sports shoes",
    "bag", "backpack", "laptop bag", "handbag", "shoulder bag", "travel bag", "wallet",
    "watch", "smartwatch", "digital watch", "analog watch", "fitness tracker",
    "sunglasses", "eyeglasses", "reading glasses", "safety glasses",
    "belt", "leather belt", "casual belt", "formal belt", "chain belt",
    "cap", "hat", "beanie", "baseball cap", "sun hat", "winter hat",
    
    # Home & Kitchen expanded
    "furniture", "chair", "office chair", "dining chair", "sofa chair", "recliner",
    "table", "dining table", "coffee table", "study table", "office table", "side table",
    "bed", "single bed", "double bed", "queen bed", "king bed", "bunk bed", "sofa bed",
    "mattress", "foam mattress", "spring mattress", "memory foam", "pillow", "bedsheet",
    "sofa", "sectional sofa", "reclining sofa", "leather sofa", "fabric sofa",
    "wardrobe", "closet", "dresser", "cabinet", "bookshelf", "tv stand", "shoe rack",
    "lamp", "table lamp", "floor lamp", "ceiling light", "led light", "smart bulb",
    "mirror", "wall mirror", "dressing mirror", "bathroom mirror", "decorative mirror",
    "curtain", "blinds", "carpet", "rug", "wall art", "photo frame", "clock", "vase",
    
    # Kitchen appliances
    "refrigerator", "fridge", "freezer", "microwave", "oven", "toaster", "air fryer",
    "rice cooker", "pressure cooker", "slow cooker", "blender", "mixer", "juicer",
    "kettle", "electric kettle", "coffee maker", "tea maker", "water purifier",
    "dishwasher", "washing machine", "dryer", "iron", "vacuum cleaner", "air purifier",
    "fan", "ceiling fan", "table fan", "pedestal fan", "exhaust fan", "air conditioner",
    "heater", "room heater", "water heater", "geyser", "inverter", "generator",
    
    # Beauty & Personal Care
    "shampoo", "conditioner", "hair oil", "hair mask", "hair dryer", "straightener",
    "cream", "face cream", "moisturizer", "sunscreen", "face wash", "cleanser",
    "serum", "toner", "mask", "scrub", "lotion", "body wash", "soap", "hand wash",
    "perfume", "cologne", "deodorant", "body spray", "aftershave", "hair gel",
    "makeup", "foundation", "concealer", "powder", "lipstick", "lip gloss", "mascara",
    "eyeliner", "eyeshadow", "blush", "nail polish", "makeup brush", "beauty tools",
    "toothbrush", "electric toothbrush", "toothpaste", "mouthwash", "dental floss",
    "razor", "shaving cream", "trimmer", "epilator", "grooming kit",
    
    # Sports & Fitness
    "gym", "fitness", "exercise", "workout", "yoga", "pilates", "aerobics",
    "dumbbell", "barbell", "weight", "kettlebell", "resistance band", "yoga mat",
    "treadmill", "exercise bike", "elliptical", "rowing machine", "home gym",
    "sports shoes", "running shoes", "training shoes", "basketball shoes", "football boots",
    "cricket", "bat", "ball", "gloves", "helmet", "pads", "wickets", "stumps",
    "football", "soccer ball", "volleyball", "basketball", "tennis ball", "badminton",
    "racket", "tennis racket", "badminton racket", "shuttlecock", "net", "sports bag",
    "swimming", "goggles", "swimsuit", "pool accessories", "diving gear",
    "cycling", "bicycle", "bike", "helmet", "cycling gear", "bike accessories",
    
    # Health & Medical
    "thermometer", "blood pressure monitor", "glucometer", "pulse oximeter", "nebulizer",
    "first aid", "bandage", "antiseptic", "medicine", "vitamins", "supplements",
    "mask", "sanitizer", "gloves", "safety equipment", "health monitor",
    
    # Baby & Kids
    "baby", "infant", "newborn", "toddler", "kids", "children",
    "diapers", "baby clothes", "baby shoes", "baby food", "formula", "bottle",
    "stroller", "car seat", "high chair", "baby bed", "crib", "playpen",
    "toys", "educational toys", "soft toys", "action figures", "dolls", "puzzle",
    "games", "board games", "card games", "video games", "outdoor toys",
    "baby care", "baby oil", "baby powder", "baby shampoo", "baby lotion",
    
    # Automotive
    "car", "auto", "vehicle", "motorcycle", "bike accessories", "car accessories",
    "helmet", "car cover", "bike cover", "car charger", "car mount", "dashboard",
    "seat cover", "steering wheel", "car perfume", "car cleaning", "car wash",
    "engine oil", "brake oil", "coolant", "car battery", "tire", "wheel",
    "car audio", "car speaker", "car stereo", "gps", "dash cam", "car camera",
    
    # Books & Education
    "book", "textbook", "novel", "story book", "educational book", "reference book",
    "notebook", "diary", "planner", "calendar", "pen", "pencil", "marker", "highlighter",
    "eraser", "sharpener", "ruler", "compass", "calculator", "scientific calculator",
    "school bag", "college bag", "study material", "stationery", "office supplies",
    
    # Generic high-yield terms
    "sale", "offer", "discount", "best", "top", "quality", "premium", "luxury",
    "cheap", "affordable", "budget", "value", "deal", "special", "new", "latest"
]

class AcceleratedMasterScraper:
    def __init__(self):
        self.db_path = 'master_products.db'
        self.conn = sqlite3.connect(self.db_path)
        self.total_new_products = 0
        self.total_duplicates_prevented = 0
        
        # Ensure master database exists
        self.setup_master_database()
        
        # Get current counts
        self.load_current_stats()
        
        # Platform configurations for balanced scraping
        self.platforms = {
            'Daraz': {'scraper': self.scrape_daraz, 'async': False, 'priority': 2},
            'Jeevee': {'scraper': async_scrape_jeevee, 'async': True, 'priority': 1},
            'Oliz': {'scraper': async_scrape_oliz, 'async': True, 'priority': 1},
            'Hukut': {'scraper': async_scrape_hukut, 'async': True, 'priority': 1},
            'HardwarePasal': {'scraper': async_scrape_hardwarepasal, 'async': True, 'priority': 1},
            'Neostore': {'scraper': async_scrape_neostore, 'async': True, 'priority': 1},
            'Better': {'scraper': async_scrape_better, 'async': True, 'priority': 1}
        }
        
    def setup_master_database(self):
        """Ensure master database has proper schema"""
        self.conn.execute('''
            CREATE TABLE IF NOT EXISTS products (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                title TEXT NOT NULL,
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
                last_updated TEXT
            )
        ''')
        
        self.conn.execute('CREATE INDEX IF NOT EXISTS idx_product_url ON products(product_url)')
        self.conn.commit()
        
    def load_current_stats(self):
        """Load current database statistics"""
        cursor = self.conn.cursor()
        
        # Total products
        cursor.execute('SELECT COUNT(*) FROM products')
        self.current_total = cursor.fetchone()[0]
        
        # Platform distribution
        cursor.execute('SELECT platform, COUNT(*) FROM products GROUP BY platform')
        self.platform_stats = {}
        for platform, count in cursor.fetchall():
            self.platform_stats[platform] = count
        
        # Ensure all platforms are initialized
        for platform in self.platforms.keys():
            if platform not in self.platform_stats:
                self.platform_stats[platform] = 0
    
    def scrape_daraz(self, search_term):
        """Enhanced Daraz scraper"""
        return sync_scrape_daraz(search_term, max_pages=5)  # More pages for more products
    
    def is_duplicate_url(self, product_url):
        """Fast duplicate check"""
        if not product_url:
            return True
        
        cursor = self.conn.cursor()
        cursor.execute("SELECT 1 FROM products WHERE product_url = ? LIMIT 1", (product_url,))
        return cursor.fetchone() is not None
    
    def add_products_to_master(self, products, platform_name, search_term):
        """Add products to master database with duplicate prevention"""
        if not products:
            return 0, 0
        
        new_added = 0
        duplicates_skipped = 0
        cursor = self.conn.cursor()
        
        for product in products:
            product_url = product.get('product_url', '')
            
            if not product_url or self.is_duplicate_url(product_url):
                duplicates_skipped += 1
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
                new_added += 1
                
            except sqlite3.IntegrityError:
                duplicates_skipped += 1
            except Exception:
                continue
        
        self.conn.commit()
        
        # Update stats
        self.platform_stats[platform_name] += new_added
        self.total_new_products += new_added
        self.total_duplicates_prevented += duplicates_skipped
        
        return new_added, duplicates_skipped
    
    async def scrape_platform_accelerated(self, platform_name, search_term):
        """Accelerated platform scraping"""
        platform_info = self.platforms[platform_name]
        
        print(f"🚀 {platform_name}: '{search_term}'")
        
        try:
            if platform_info['async']:
                products = await platform_info['scraper'](search_term)
            else:
                products = platform_info['scraper'](search_term)
            
            if products and len(products) > 0:
                new_added, duplicates = self.add_products_to_master(products, platform_name, search_term)
                
                total_platform = self.platform_stats[platform_name]
                print(f"   ✅ {len(products)} found → {new_added} NEW, {duplicates} duplicates | Platform total: {total_platform:,}")
                
                return new_added, duplicates
            else:
                print(f"   ❌ No products found")
                return 0, 0
                
        except Exception as e:
            print(f"   ❌ Error: {str(e)[:50]}...")
            return 0, 0
    
    async def run_accelerated_scraping(self):
        """Run accelerated scraping to build master database"""
        print("⚡ ACCELERATED MASTER DATABASE BUILDER")
        print("=" * 50)
        print(f"🎯 TARGET: Add products to reach 50k+ unique products")
        print(f"📊 Starting with: {self.current_total:,} products")
        print(f"🔒 Duplicate prevention: ACTIVE")
        print(f"⚖️ Platform balancing: ACTIVE")
        print("=" * 50)
        
        start_time = time.time()
        
        # Aggressive scraping rounds
        for round_num in range(1, 30):  # Up to 30 rounds for rapid growth
            print(f"\n⚡ ACCELERATED ROUND {round_num}")
            
            round_new = 0
            round_duplicates = 0
            
            # Get platforms needing more products (prioritize underperforming)
            platform_priorities = []
            for platform, info in self.platforms.items():
                current_count = self.platform_stats[platform]
                priority_score = info['priority'] * (1 + (20000 - min(current_count, 20000)) / 20000)
                platform_priorities.append((platform, priority_score))
            
            # Sort by priority (higher score = more priority)
            platform_priorities.sort(key=lambda x: x[1], reverse=True)
            
            # Use more search terms per round for faster growth
            terms_per_round = min(len(AGGRESSIVE_SEARCH_TERMS), 15)
            
            for i in range(terms_per_round):
                if i >= len(platform_priorities):
                    break
                
                # Rotate through platforms and terms
                platform_name, _ = platform_priorities[i % len(platform_priorities)]
                search_term = AGGRESSIVE_SEARCH_TERMS[(round_num * terms_per_round + i) % len(AGGRESSIVE_SEARCH_TERMS)]
                
                new_added, duplicates = await self.scrape_platform_accelerated(platform_name, search_term)
                round_new += new_added
                round_duplicates += duplicates
                
                # Shorter delays for speed
                await asyncio.sleep(random.uniform(0.5, 1.5))
            
            # Update current total
            cursor = self.conn.cursor()
            cursor.execute('SELECT COUNT(*) FROM products')
            current_total = cursor.fetchone()[0]
            
            # Round summary
            print(f"\n📊 ROUND {round_num} RESULTS:")
            print(f"   • New products added: {round_new}")
            print(f"   • Duplicates prevented: {round_duplicates}")
            print(f"   • Total products: {current_total:,}")
            print(f"   • 50k progress: {(current_total/50000)*100:.1f}%")
            
            # Check if we've reached 50k
            if current_total >= 50000:
                print(f"\n🎉 50K MILESTONE ACHIEVED!")
                break
            
            # Platform balance every 5 rounds
            if round_num % 5 == 0:
                print(f"\n⚖️ PLATFORM BALANCE CHECK:")
                for platform in sorted(self.platform_stats.keys()):
                    count = self.platform_stats[platform]
                    percentage = (count / current_total) * 100 if current_total > 0 else 0
                    print(f"   • {platform}: {count:,} ({percentage:.1f}%)")
            
            # Break if no progress for efficiency
            if round_new == 0:
                print(f"   ⚠️ No new products found - may need different search terms")
                continue
        
        # Final statistics
        elapsed_time = time.time() - start_time
        final_total = current_total
        
        print(f"\n" + "=" * 50)
        print("⚡ ACCELERATED SCRAPING COMPLETE!")
        print("=" * 50)
        print(f"⏱️ Time taken: {elapsed_time/60:.1f} minutes")
        print(f"📊 Final total: {final_total:,} unique products")
        print(f"📈 Products added: {self.total_new_products:,}")
        print(f"🔒 Duplicates prevented: {self.total_duplicates_prevented:,}")
        print(f"🎯 50k progress: {(final_total/50000)*100:.1f}%")
        
        # Final platform distribution
        print(f"\n🏪 FINAL PLATFORM DISTRIBUTION:")
        for platform, count in sorted(self.platform_stats.items(), key=lambda x: x[1], reverse=True):
            percentage = (count / final_total) * 100 if final_total > 0 else 0
            print(f"   • {platform}: {count:,} products ({percentage:.1f}%)")
        
        # Database info
        db_size = os.path.getsize(self.db_path) / (1024 * 1024)
        print(f"\n💾 MASTER DATABASE INFO:")
        print(f"   • File: {self.db_path}")
        print(f"   • Size: {db_size:.1f} MB")
        print(f"   • Unique products: {final_total:,}")
        
        self.conn.close()
        print(f"\n✅ Master database ready for production!")

async def main():
    """Run accelerated master database building"""
    scraper = AcceleratedMasterScraper()
    
    try:
        await scraper.run_accelerated_scraping()
    except KeyboardInterrupt:
        print("\n⚠️ Accelerated scraping interrupted")
    except Exception as e:
        print(f"\n❌ Error: {e}")

if __name__ == "__main__":
    asyncio.run(main())