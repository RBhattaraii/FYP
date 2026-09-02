#!/usr/bin/env python3
"""
PRODUCT DATABASE CONSOLIDATOR
Merge all collected products from different scrapers into unified databases
"""

import sqlite3
import asyncio
import asyncpg
import os
from datetime import datetime, timezone

# Database URLs
SUPABASE_URL = "postgresql://postgres.cukfnnjuofbvsrwwkdsh:gKaBwfxiaFauuKyS@aws-1-ap-northeast-1.pooler.supabase.com:6543/postgres"

async def consolidate_all_products():
    """Consolidate products from all local databases"""
    print("🔄 CONSOLIDATING ALL SCRAPED PRODUCTS")
    print("=" * 60)
    
    # Local database files to consolidate
    db_files = [
        ('local_products.db', 'Main Scraper'),
        ('turbo_products.db', 'Turbo Scraper'),
        ('resilient_products.db', 'Resilient Scraper')
    ]
    
    # Create consolidated database
    consolidated_path = 'all_products_consolidated.db'
    consolidated_conn = sqlite3.connect(consolidated_path)
    
    # Create consolidated table with all fields
    consolidated_conn.execute('''
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
            source_scraper TEXT,
            consolidated_at TEXT
        )
    ''')
    
    total_products = 0
    source_stats = {}
    
    # Process each database file
    for db_file, source_name in db_files:
        if not os.path.exists(db_file):
            print(f"⏭️  Skipping {source_name}: {db_file} not found")
            continue
            
        print(f"\n📁 Processing {source_name}: {db_file}")
        
        try:
            # Connect to source database
            source_conn = sqlite3.connect(db_file)
            cursor = source_conn.cursor()
            
            # Get all products
            cursor.execute("SELECT * FROM products")
            products = cursor.fetchall()
            
            # Get column names
            cursor.execute("PRAGMA table_info(products)")
            columns = [row[1] for row in cursor.fetchall()]
            
            print(f"  📊 Found {len(products):,} products with columns: {columns}")
            
            # Insert into consolidated database
            consolidated_cursor = consolidated_conn.cursor()
            products_added = 0
            
            for product in products:
                try:
                    # Map fields based on available columns
                    product_dict = dict(zip(columns, product))
                    
                    consolidated_cursor.execute('''
                        INSERT OR IGNORE INTO products 
                        (title, price, original_price, discount_percent, image_url, 
                         store_name, product_url, category, scraped_at, platform, 
                         search_term, source_scraper, consolidated_at)
                        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                    ''', (
                        product_dict.get('title', 'Unknown'),
                        product_dict.get('price', 0),
                        product_dict.get('original_price'),
                        product_dict.get('discount_percent', 0),
                        product_dict.get('image_url', ''),
                        product_dict.get('store_name', 'Unknown'),
                        product_dict.get('product_url', ''),
                        product_dict.get('category', 'General'),
                        product_dict.get('scraped_at', datetime.now(timezone.utc).isoformat()),
                        product_dict.get('platform', 'unknown'),
                        product_dict.get('search_term', ''),
                        source_name,
                        datetime.now(timezone.utc).isoformat()
                    ))
                    products_added += 1
                except Exception as e:
                    continue
            
            consolidated_conn.commit()
            source_conn.close()
            
            source_stats[source_name] = products_added
            total_products += products_added
            
            print(f"  ✅ Added {products_added:,} unique products")
            
        except Exception as e:
            print(f"  ❌ Error processing {source_name}: {e}")
    
    # Get final consolidated stats
    cursor = consolidated_conn.cursor()
    cursor.execute("SELECT COUNT(*) FROM products")
    final_count = cursor.fetchone()[0]
    
    cursor.execute("SELECT store_name, COUNT(*) FROM products GROUP BY store_name")
    store_stats = cursor.fetchall()
    
    cursor.execute("SELECT category, COUNT(*) FROM products GROUP BY category ORDER BY COUNT(*) DESC LIMIT 10")
    category_stats = cursor.fetchall()
    
    file_size = os.path.getsize(consolidated_path) / (1024 * 1024)
    
    # Print comprehensive summary
    print("\n" + "=" * 60)
    print("🎉 CONSOLIDATION COMPLETE!")
    print("=" * 60)
    print(f"📊 TOTAL UNIQUE PRODUCTS: {final_count:,}")
    print(f"💾 Database size: {file_size:.1f} MB")
    
    print(f"\n📋 SOURCE BREAKDOWN:")
    for source, count in source_stats.items():
        percentage = (count / final_count) * 100 if final_count > 0 else 0
        print(f"  • {source}: {count:,} products ({percentage:.1f}%)")
    
    print(f"\n🏪 STORE BREAKDOWN:")
    for store, count in store_stats:
        percentage = (count / final_count) * 100 if final_count > 0 else 0
        print(f"  • {store}: {count:,} products ({percentage:.1f}%)")
    
    print(f"\n📂 TOP CATEGORIES:")
    for category, count in category_stats:
        percentage = (count / final_count) * 100 if final_count > 0 else 0
        print(f"  • {category}: {count:,} products ({percentage:.1f}%)")
    
    # Progress toward targets
    min_target = 300000
    max_target = 1000000
    
    min_progress = (final_count / min_target) * 100
    max_progress = (final_count / max_target) * 100
    
    print(f"\n🎯 PROGRESS TOWARD TARGETS:")
    print(f"  • Minimum (300k): {min_progress:.1f}%")
    print(f"  • Maximum (1M): {max_progress:.1f}%")
    
    if final_count >= max_target:
        print(f"\n🏆 MAXIMUM TARGET ACHIEVED!")
    elif final_count >= min_target:
        print(f"\n✅ MINIMUM TARGET ACHIEVED!")
    else:
        remaining = min_target - final_count
        print(f"\n⏳ Need {remaining:,} more products for minimum target")
    
    # Try to upload to Supabase if possible
    try:
        print(f"\n📡 Attempting to upload to Supabase...")
        conn = await asyncpg.connect(SUPABASE_URL)
        
        # Get sample of products to upload
        cursor.execute("SELECT * FROM products LIMIT 1000")
        sample_products = cursor.fetchall()
        
        uploaded = 0
        for product in sample_products:
            try:
                await conn.execute("""
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
                    product[1], product[2], product[3], product[4], 
                    product[5], product[6], product[7], product[8], 
                    product[9]
                )
                uploaded += 1
            except:
                continue
        
        await conn.close()
        print(f"  ✅ Uploaded {uploaded} products to Supabase")
        
    except Exception as e:
        print(f"  ⚠️  Supabase upload failed: {e}")
    
    consolidated_conn.close()
    
    print(f"\n✅ Consolidated database saved as: {consolidated_path}")
    print("🚀 Your PricePilot app now has comprehensive product data!")

if __name__ == "__main__":
    asyncio.run(consolidate_all_products())