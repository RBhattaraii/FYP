#!/usr/bin/env python3
"""
ENHANCED MASTER CONSOLIDATOR
Combines all individual platform databases into a master database
Handles duplicates, validates data, and provides comprehensive statistics
"""

import sqlite3
import os
from datetime import datetime
import time

class MasterConsolidator:
    def __init__(self):
        self.master_db = 'master_enhanced_products.db'
        self.platform_dbs = {
            'jeevee': 'jeevee_enhanced.db',
            'cgdigital': 'cgdigital_enhanced.db', 
            'hukut': 'hukut_enhanced.db',
            'oliz': 'oliz_enhanced.db',
            'better': 'better_enhanced.db',
            'hardwarepasal': 'hardwarepasal_enhanced.db'
        }
        self.setup_master_database()
        
    def setup_master_database(self):
        """Setup master database with enhanced schema"""
        conn = sqlite3.connect(self.master_db)
        cursor = conn.cursor()
        
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS products (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                title TEXT NOT NULL,
                price REAL,
                original_price REAL,
                discount_percent REAL,
                image_url TEXT,
                product_url TEXT UNIQUE,
                category TEXT,
                brand TEXT,
                rating REAL,
                reviews_count INTEGER,
                in_stock BOOLEAN,
                platform TEXT,
                scraped_at TIMESTAMP,
                search_term TEXT,
                page_number INTEGER,
                consolidated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        # Enhanced indexes for better performance
        cursor.execute('CREATE INDEX IF NOT EXISTS idx_product_url ON products(product_url)')
        cursor.execute('CREATE INDEX IF NOT EXISTS idx_platform ON products(platform)')
        cursor.execute('CREATE INDEX IF NOT EXISTS idx_brand ON products(brand)')
        cursor.execute('CREATE INDEX IF NOT EXISTS idx_category ON products(category)')
        cursor.execute('CREATE INDEX IF NOT EXISTS idx_price ON products(price)')
        
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS consolidation_log (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                platform TEXT,
                products_added INTEGER,
                duplicates_skipped INTEGER,
                consolidation_time TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        conn.commit()
        conn.close()
        print("✅ Master database setup complete")

    def get_platform_stats(self, platform, db_file):
        """Get statistics from individual platform database"""
        if not os.path.exists(db_file):
            return 0, 0
            
        try:
            conn = sqlite3.connect(db_file)
            cursor = conn.cursor()
            cursor.execute('SELECT COUNT(*) FROM products')
            total = cursor.fetchone()[0]
            cursor.execute('SELECT COUNT(DISTINCT brand) FROM products WHERE brand IS NOT NULL')
            brands = cursor.fetchone()[0]
            conn.close()
            return total, brands
        except Exception as e:
            print(f"❌ Error reading {platform} database: {e}")
            return 0, 0

    def get_master_stats(self):
        """Get master database statistics"""
        try:
            conn = sqlite3.connect(self.master_db)
            cursor = conn.cursor()
            
            cursor.execute('SELECT COUNT(*) FROM products')
            total = cursor.fetchone()[0]
            
            cursor.execute('SELECT COUNT(DISTINCT platform) FROM products')
            platforms = cursor.fetchone()[0]
            
            cursor.execute('SELECT COUNT(DISTINCT brand) FROM products WHERE brand IS NOT NULL')
            brands = cursor.fetchone()[0]
            
            cursor.execute('SELECT COUNT(DISTINCT category) FROM products WHERE category IS NOT NULL')
            categories = cursor.fetchone()[0]
            
            cursor.execute('SELECT platform, COUNT(*) FROM products GROUP BY platform')
            platform_counts = dict(cursor.fetchall())
            
            cursor.execute('SELECT AVG(price) FROM products WHERE price > 0')
            avg_price = cursor.fetchone()[0] or 0
            
            conn.close()
            return {
                'total': total,
                'platforms': platforms,
                'brands': brands,
                'categories': categories,
                'platform_counts': platform_counts,
                'avg_price': avg_price
            }
        except Exception as e:
            print(f"❌ Error reading master database: {e}")
            return {}

    def consolidate_platform(self, platform, db_file):
        """Consolidate products from a single platform database"""
        if not os.path.exists(db_file):
            print(f"⚠️  {platform} database not found: {db_file}")
            return 0, 0
            
        print(f"\n🔄 Consolidating {platform.upper()} products...")
        
        try:
            # Connect to both databases
            platform_conn = sqlite3.connect(db_file)
            master_conn = sqlite3.connect(self.master_db)
            
            platform_cursor = platform_conn.cursor()
            master_cursor = master_conn.cursor()
            
            # Get all products from platform database
            platform_cursor.execute('''
                SELECT title, price, original_price, discount_percent, image_url, 
                       product_url, category, brand, rating, reviews_count, in_stock, 
                       platform, scraped_at, search_term, page_number
                FROM products
            ''')
            
            products = platform_cursor.fetchall()
            added = 0
            duplicates = 0
            
            for product in products:
                try:
                    # Try to insert, ignore duplicates based on product_url
                    master_cursor.execute('''
                        INSERT OR IGNORE INTO products 
                        (title, price, original_price, discount_percent, image_url, 
                         product_url, category, brand, rating, reviews_count, in_stock, 
                         platform, scraped_at, search_term, page_number)
                        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                    ''', product)
                    
                    if master_cursor.rowcount > 0:
                        added += 1
                    else:
                        duplicates += 1
                        
                except Exception as e:
                    print(f"❌ Error inserting product: {e}")
                    continue
            
            # Log consolidation
            master_cursor.execute('''
                INSERT INTO consolidation_log (platform, products_added, duplicates_skipped)
                VALUES (?, ?, ?)
            ''', (platform, added, duplicates))
            
            master_conn.commit()
            
            platform_conn.close()
            master_conn.close()
            
            print(f"   ✅ {platform}: +{added:,} products, {duplicates:,} duplicates skipped")
            return added, duplicates
            
        except Exception as e:
            print(f"❌ Error consolidating {platform}: {e}")
            return 0, 0

    def consolidate_all(self):
        """Consolidate all platform databases into master"""
        print("🚀 ENHANCED MASTER CONSOLIDATOR STARTED")
        print("=" * 60)
        print(f"🎯 Consolidating all platform databases into master")
        print(f"💾 Master database: {self.master_db}")
        print(f"⏰ Started at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        print("=" * 60)
        
        # Show current status of all databases
        print("\n📊 CURRENT DATABASE STATUS:")
        total_individual = 0
        
        for platform, db_file in self.platform_dbs.items():
            count, brands = self.get_platform_stats(platform, db_file)
            total_individual += count
            status = "✅" if count > 0 else "❌"
            file_size = f"({os.path.getsize(db_file)/1024/1024:.1f} MB)" if os.path.exists(db_file) else "(not found)"
            print(f"   {status} {platform.upper():12}: {count:,} products, {brands} brands {file_size}")
        
        print(f"\n📈 Total individual databases: {total_individual:,} products")
        
        # Get current master stats
        master_stats = self.get_master_stats()
        current_master = master_stats.get('total', 0)
        print(f"📈 Current master database: {current_master:,} products")
        
        # Consolidate each platform
        print(f"\n🔄 CONSOLIDATION PROCESS:")
        start_time = time.time()
        total_added = 0
        total_duplicates = 0
        
        for platform, db_file in self.platform_dbs.items():
            added, duplicates = self.consolidate_platform(platform, db_file)
            total_added += added
            total_duplicates += duplicates
        
        # Final statistics
        consolidation_time = time.time() - start_time
        final_stats = self.get_master_stats()
        
        print(f"\n🎉 CONSOLIDATION COMPLETED!")
        print(f"⏰ Consolidation time: {consolidation_time:.1f} seconds")
        print(f"📊 Products added: {total_added:,}")
        print(f"🔄 Duplicates skipped: {total_duplicates:,}")
        print(f"📈 Master database total: {final_stats.get('total', 0):,} products")
        print(f"🏪 Platforms: {final_stats.get('platforms', 0)}")
        print(f"🏷️  Brands: {final_stats.get('brands', 0)}")
        print(f"📂 Categories: {final_stats.get('categories', 0)}")
        print(f"💰 Average price: Rs. {final_stats.get('avg_price', 0):.0f}")
        
        # Platform breakdown
        platform_counts = final_stats.get('platform_counts', {})
        if platform_counts:
            print(f"\n📊 PRODUCTS BY PLATFORM:")
            for platform, count in sorted(platform_counts.items(), key=lambda x: x[1], reverse=True):
                percentage = (count / final_stats.get('total', 1)) * 100
                print(f"   {platform.upper():12}: {count:,} products ({percentage:.1f}%)")
        
        # Database file size
        master_size = os.path.getsize(self.master_db) / 1024 / 1024
        print(f"\n💾 Master database: {self.master_db} ({master_size:.1f} MB)")
        
        return final_stats

    def show_detailed_stats(self):
        """Show detailed statistics of the master database"""
        stats = self.get_master_stats()
        
        if not stats:
            print("❌ No statistics available")
            return
            
        print("\n📊 DETAILED MASTER DATABASE STATISTICS:")
        print("=" * 50)
        
        conn = sqlite3.connect(self.master_db)
        cursor = conn.cursor()
        
        # Top brands
        cursor.execute('''
            SELECT brand, COUNT(*) as count 
            FROM products 
            WHERE brand IS NOT NULL AND brand != '' 
            GROUP BY brand 
            ORDER BY count DESC 
            LIMIT 10
        ''')
        
        print(f"\n🏷️  TOP 10 BRANDS:")
        for brand, count in cursor.fetchall():
            print(f"   {brand:15}: {count:,} products")
        
        # Price ranges
        cursor.execute('''
            SELECT 
                COUNT(CASE WHEN price < 1000 THEN 1 END) as under_1k,
                COUNT(CASE WHEN price BETWEEN 1000 AND 10000 THEN 1 END) as 1k_10k,
                COUNT(CASE WHEN price BETWEEN 10000 AND 50000 THEN 1 END) as 10k_50k,
                COUNT(CASE WHEN price BETWEEN 50000 AND 100000 THEN 1 END) as 50k_100k,
                COUNT(CASE WHEN price > 100000 THEN 1 END) as over_100k
            FROM products WHERE price > 0
        ''')
        
        price_ranges = cursor.fetchone()
        print(f"\n💰 PRICE DISTRIBUTION:")
        ranges = [
            ("Under Rs. 1,000", price_ranges[0]),
            ("Rs. 1K - 10K", price_ranges[1]),
            ("Rs. 10K - 50K", price_ranges[2]),
            ("Rs. 50K - 100K", price_ranges[3]),
            ("Over Rs. 100K", price_ranges[4])
        ]
        
        for range_name, count in ranges:
            print(f"   {range_name:15}: {count:,} products")
        
        # Top categories
        cursor.execute('''
            SELECT category, COUNT(*) as count 
            FROM products 
            WHERE category IS NOT NULL AND category != '' 
            GROUP BY category 
            ORDER BY count DESC 
            LIMIT 10
        ''')
        
        print(f"\n📂 TOP 10 CATEGORIES:")
        for category, count in cursor.fetchall():
            print(f"   {category[:20]:20}: {count:,} products")
        
        conn.close()

if __name__ == "__main__":
    consolidator = MasterConsolidator()
    final_stats = consolidator.consolidate_all()
    consolidator.show_detailed_stats()
    
    print(f"\n🎯 TARGET PROGRESS:")
    total_products = final_stats.get('total', 0)
    target = 100000
    percentage = (total_products / target) * 100
    remaining = max(0, target - total_products)
    
    print(f"   Current: {total_products:,} / {target:,} products ({percentage:.1f}%)")
    print(f"   Remaining: {remaining:,} products")
    
    if total_products >= target:
        print(f"   🎉 TARGET ACHIEVED! ({total_products - target:,} over target)")
    else:
        print(f"   📈 Keep scraping to reach {target:,} products!")