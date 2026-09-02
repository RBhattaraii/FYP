#!/usr/bin/env python3
"""
PARALLEL MASTER BUILDER
Multiple focused scrapers working on master database simultaneously
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

# Focus terms for non-Daraz platforms
FOCUS_TERMS = [
    "mobile", "phone", "headphone", "speaker", "watch", "tablet", "laptop",
    "shirt", "jeans", "shoes", "bag", "dress", "jacket", "belt", "cap",
    "home", "kitchen", "chair", "table", "lamp", "fan", "cooker", "blender",
    "cream", "shampoo", "perfume", "makeup", "soap", "lotion", "skincare"
]

class ParallelMasterBuilder:
    def __init__(self, platform_name, platform_scraper):
        self.platform_name = platform_name
        self.platform_scraper = platform_scraper
        self.db_path = 'master_products.db'
        self.products_added = 0
        self.duplicates_prevented = 0
        
    def add_to_master(self, products, search_term):
        """Add products to master database"""
        if not products:
            return 0, 0
            
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        new_added = 0
        duplicates = 0
        
        for product in products:
            product_url = product.get('product_url', '')
            
            if not product_url:
                continue
                
            # Check for duplicate
            cursor.execute("SELECT 1 FROM products WHERE product_url = ? LIMIT 1", (product_url,))
            if cursor.fetchone():
                duplicates += 1
                continue
            
            try:
                cursor.execute('''
                    INSERT INTO products 
                    (title, price, original_price, discount_percent, image_url, 
                     store_name, product_url, category, scraped_at, platform, search_term, last_updated)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                ''', (
                    product.get('product_name', 'Unknown'),
                    float(product.get('price', 0)),
                    float(product.get('original_price', 0)) if product.get('original_price') else None,
                    float(product.get('discount_percentage', 0)) if product.get('discount_percentage') else None,
                    product.get('image_url', ''),
                    self.platform_name,
                    product_url,
                    search_term,
                    datetime.now(timezone.utc).isoformat(),
                    self.platform_name,
                    search_term,
                    datetime.now(timezone.utc).isoformat()
                ))
                new_added += 1
                
            except sqlite3.IntegrityError:
                duplicates += 1
            except Exception:
                continue
        
        conn.commit()
        conn.close()
        
        self.products_added += new_added
        self.duplicates_prevented += duplicates
        
        return new_added, duplicates
    
    async def run_parallel_scraping(self):
        """Run focused scraping for this platform"""
        print(f"🔄 PARALLEL BUILDER: {self.platform_name}")
        print(f"🎯 Adding unique products to master database")
        
        for round_num in range(1, 20):  # 20 rounds of focused scraping
            print(f"\\n📍 {self.platform_name} Round {round_num}")
            
            round_added = 0
            
            # Use multiple search terms per round
            for i, term in enumerate(FOCUS_TERMS):
                if i >= 5:  # 5 terms per round
                    break
                
                term_index = (round_num * 5 + i) % len(FOCUS_TERMS)
                search_term = FOCUS_TERMS[term_index]
                
                print(f"🔍 {self.platform_name}: '{search_term}'")
                
                try:
                    products = await self.platform_scraper(search_term)
                    
                    if products:
                        new_added, duplicates = self.add_to_master(products, search_term)
                        round_added += new_added
                        
                        print(f"   ✅ {len(products)} found → {new_added} new, {duplicates} duplicates")
                    else:
                        print(f"   ❌ No products")
                        
                except Exception as e:
                    print(f"   ❌ Error: {str(e)[:40]}...")
                
                # Short delay
                await asyncio.sleep(random.uniform(1, 2))
            
            print(f"📊 {self.platform_name} Round {round_num}: {round_added} new products")
            
            # Break if no new products
            if round_added == 0:
                print(f"⚠️ {self.platform_name}: No new products found")
                break
        
        print(f"\\n✅ {self.platform_name} COMPLETE:")
        print(f"   • Products added: {self.products_added}")
        print(f"   • Duplicates prevented: {self.duplicates_prevented}")

async def main():
    """Run parallel builders for multiple platforms"""
    print("🚀 PARALLEL MASTER BUILDERS")
    print("=" * 40)
    
    # Create builders for different platforms
    builders = [
        ParallelMasterBuilder("Jeevee", async_scrape_jeevee),
        ParallelMasterBuilder("Oliz", async_scrape_oliz),
        ParallelMasterBuilder("Hukut", async_scrape_hukut)
    ]
    
    # Run all builders concurrently
    tasks = [builder.run_parallel_scraping() for builder in builders]
    
    try:
        await asyncio.gather(*tasks)
        
        # Final summary
        total_added = sum(b.products_added for b in builders)
        total_duplicates = sum(b.duplicates_prevented for b in builders)
        
        print(f"\\n🎉 PARALLEL BUILDING COMPLETE!")
        print(f"📊 Total new products: {total_added}")
        print(f"🔒 Total duplicates prevented: {total_duplicates}")
        
    except Exception as e:
        print(f"❌ Error: {e}")

if __name__ == "__main__":
    asyncio.run(main())