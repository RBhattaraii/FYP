#!/usr/bin/env python3
"""
TURBO SCRAPER - Parallel Multi-Platform Accelerated Scraping
Works alongside main scraper to reach 300k-1M products faster
"""

import asyncio
import sqlite3
import sys
import os
from datetime import datetime, timezone
import time

# Add paths for imports
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))
sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'scrapers'))

from scrapers.daraz.daraz_scraper import sync_scrape_daraz

# HIGH-VALUE SEARCH TERMS for maximum product yield
TURBO_SEARCH_TERMS = [
    # Electronics - High yield terms
    "phone", "mobile", "laptop", "computer", "tablet", "headphone", "speaker", "charger", "cable", "mouse",
    "keyboard", "monitor", "camera", "tv", "watch", "earphone", "bluetooth", "wireless", "smart", "gaming",
    
    # Fashion - Popular items
    "shirt", "dress", "shoes", "bag", "jeans", "jacket", "watch", "belt", "wallet", "sunglass",
    "sneaker", "sandal", "boot", "cap", "hat", "ring", "necklace", "bracelet", "perfume", "makeup",
    
    # Home & Kitchen - Essential items
    "kitchen", "home", "furniture", "bed", "chair", "table", "lamp", "curtain", "pillow", "blanket",
    "cookware", "utensil", "plate", "cup", "glass", "bottle", "container", "storage", "organizer", "decor",
    
    # Health & Beauty
    "beauty", "skincare", "makeup", "cream", "lotion", "shampoo", "soap", "toothbrush", "medicine", "vitamin",
    "supplement", "protein", "fitness", "yoga", "exercise", "wellness", "care", "treatment", "mask", "serum",
    
    # Sports & Outdoor
    "sport", "outdoor", "cycling", "running", "swimming", "basketball", "football", "tennis", "badminton", "cricket",
    "gym", "fitness", "workout", "equipment", "gear", "accessory", "clothing", "wear", "shoe", "bag",
    
    # Books & Education
    "book", "education", "learning", "study", "school", "college", "university", "course", "training", "skill",
    "notebook", "pen", "pencil", "marker", "calculator", "diary", "planner", "organizer", "stationary", "office",
    
    # Automotive & Tools
    "car", "bike", "auto", "vehicle", "tool", "equipment", "parts", "accessory", "maintenance", "repair",
    "helmet", "cover", "charger", "mount", "holder", "cleaner", "polish", "wax", "oil", "battery",
    
    # Baby & Kids
    "baby", "kids", "children", "toy", "game", "puzzle", "doll", "car", "truck", "educational", 
    "learning", "development", "safety", "care", "feeding", "clothing", "diaper", "stroller", "seat", "monitor",
    
    # Pets & Animals
    "pet", "dog", "cat", "fish", "bird", "animal", "food", "toy", "care", "health",
    "collar", "leash", "bed", "house", "cage", "aquarium", "bowl", "treat", "grooming", "cleaning"
]

class TurboScraper:
    def __init__(self):
        self.db_path = 'turbo_products.db'
        self.setup_database()
        
    def setup_database(self):
        """Setup turbo scraper database"""
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
                turbo_batch TEXT
            )
        ''')
        self.conn.commit()
        print(f"✅ Turbo database ready: {self.db_path}")

    def store_products_fast(self, products, store_name, search_term, batch_id):
        """Ultra-fast product storage"""
        if not products:
            return 0
            
        stored = 0
        cursor = self.conn.cursor()
        
        for product in products:
            try:
                cursor.execute('''
                    INSERT OR REPLACE INTO products 
                    (title, price, original_price, discount_percent, image_url, 
                     store_name, product_url, category, scraped_at, platform, search_term, turbo_batch)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                ''', (
                    product.get('product_name', 'Unknown Product'),
                    float(product.get('price', 0)),
                    float(product.get('original_price', 0)) if product.get('original_price') else None,
                    float(product.get('discount_percentage', 0)) if product.get('discount_percentage') else None,
                    product.get('image_url', ''),
                    store_name,
                    product.get('product_url', ''),
                    search_term,  # Use search term as category
                    datetime.now(timezone.utc).isoformat(),
                    product.get('platform', store_name.lower()),
                    search_term,
                    batch_id
                ))
                stored += 1
            except Exception as e:
                continue
                
        self.conn.commit()
        return stored

    async def turbo_scrape_term(self, search_term, batch_id):
        """Scrape a single term with maximum pages"""
        print(f"🚀 TURBO: {search_term}")
        
        try:
            # Use maximum pages for high yield
            products = sync_scrape_daraz(search_term, max_pages=25)  # 25 pages = 1000 products per term
            
            if products:
                stored = self.store_products_fast(products, "Daraz", search_term, batch_id)
                print(f"  ✅ {len(products)} found → {stored} stored")
                return stored
            else:
                print(f"  ❌ No products")
                return 0
                
        except Exception as e:
            print(f"  ❌ Error: {e}")
            return 0

    async def run_turbo_scraping(self):
        """Execute turbo scraping with parallel processing"""
        print("🚀 TURBO SCRAPER STARTING - MAXIMUM SPEED MODE")
        print("=" * 60)
        
        start_time = time.time()
        batch_id = f"turbo_{int(time.time())}"
        total_products = 0
        
        # Process terms in parallel batches
        batch_size = 5  # 5 terms at once
        
        for i in range(0, len(TURBO_SEARCH_TERMS), batch_size):
            batch = TURBO_SEARCH_TERMS[i:i+batch_size]
            print(f"\n🔥 BATCH {i//batch_size + 1}: {', '.join(batch)}")
            
            # Create tasks for parallel execution
            tasks = [self.turbo_scrape_term(term, batch_id) for term in batch]
            
            # Execute batch in parallel
            batch_results = await asyncio.gather(*tasks, return_exceptions=True)
            
            # Count successful results
            batch_total = sum(r for r in batch_results if isinstance(r, int))
            total_products += batch_total
            
            print(f"  📊 Batch total: {batch_total:,} products")
            print(f"  🎯 Running total: {total_products:,} products")
            
            # Brief pause between batches
            await asyncio.sleep(2)
        
        # Final statistics
        elapsed_time = time.time() - start_time
        
        print("\n" + "=" * 60)
        print("🎉 TURBO SCRAPING COMPLETE!")
        print(f"⏱️  Time: {elapsed_time/60:.1f} minutes")
        print(f"📊 Total products: {total_products:,}")
        print(f"🚀 Rate: {total_products/(elapsed_time/60):.0f} products/minute")
        
        # Show database stats
        cursor = self.conn.cursor()
        cursor.execute("SELECT COUNT(*) FROM products")
        db_total = cursor.fetchone()[0]
        
        file_size = os.path.getsize(self.db_path) / (1024 * 1024)  # MB
        
        print(f"💾 Database: {db_total:,} products ({file_size:.1f} MB)")
        
        print("\n✅ Turbo scraping accelerated the main operation!")

    def cleanup(self):
        """Close database connection"""
        if hasattr(self, 'conn'):
            self.conn.close()

async def main():
    """Main turbo scraper execution"""
    scraper = TurboScraper()
    
    try:
        await scraper.run_turbo_scraping()
    except KeyboardInterrupt:
        print("\n⚠️  Turbo scraping interrupted")
    except Exception as e:
        print(f"\n❌ Turbo error: {e}")
    finally:
        scraper.cleanup()

if __name__ == "__main__":
    asyncio.run(main())