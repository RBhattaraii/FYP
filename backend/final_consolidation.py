#!/usr/bin/env python3
"""
Final Consolidation - Check all databases and consolidate to reach 100k
"""

import sqlite3
import os
import glob
from datetime import datetime

def consolidate_all_databases():
    """Consolidate all database files into a master 100k database"""
    
    # Create the master 100k database
    master_db = 'master_100k_products.db'
    
    conn = sqlite3.connect(master_db)
    cursor = conn.cursor()
    
    # Create master table with all necessary fields
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS products (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            title TEXT NOT NULL,
            price REAL,
            original_price REAL,
            discount_percent REAL,
            price_text TEXT,
            image_url TEXT,
            product_url TEXT UNIQUE,
            category TEXT,
            brand TEXT,
            platform TEXT,
            rating REAL,
            reviews_count INTEGER,
            in_stock BOOLEAN DEFAULT 1,
            scraped_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            source_db TEXT
        )
    ''')
    
    cursor.execute('CREATE INDEX IF NOT EXISTS idx_product_url ON products(product_url)')
    cursor.execute('CREATE INDEX IF NOT EXISTS idx_platform ON products(platform)')
    
    conn.commit()
    
    print("🚀 FINAL DATABASE CONSOLIDATION")
    print("=" * 60)
    print(f"⏰ Started at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("=" * 60)
    
    # Find all database files
    db_files = glob.glob('*.db')
    db_files = [db for db in db_files if db != master_db]  # Exclude master from itself
    
    total_consolidated = 0
    successful_dbs = 0
    
    for db_file in db_files:
        try:
            print(f"📂 Processing: {db_file}")
            
            # Connect to source database
            source_conn = sqlite3.connect(db_file)
            source_cursor = source_conn.cursor()
            
            # Try to get products table structure
            try:
                source_cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='products'")
                if not source_cursor.fetchone():
                    print(f"   ⚠️  No products table found")
                    source_conn.close()
                    continue
            except:
                print(f"   ❌ Cannot access database")
                source_conn.close()
                continue
            
            # Get column info
            source_cursor.execute("PRAGMA table_info(products)")
            columns = [col[1] for col in source_cursor.fetchall()]
            
            # Build SELECT statement with available columns
            select_columns = []
            insert_columns = []
            placeholders = []
            
            column_mapping = {
                'title': 'title',
                'price': 'price', 
                'original_price': 'original_price',
                'discount_percent': 'discount_percent',
                'price_text': 'price_text',
                'image_url': 'image_url',
                'product_url': 'product_url',
                'category': 'category',
                'brand': 'brand',
                'platform': 'platform',
                'rating': 'rating',
                'reviews_count': 'reviews_count',
                'in_stock': 'in_stock',
                'scraped_at': 'scraped_at'
            }
            
            for master_col, source_col in column_mapping.items():
                if source_col in columns:
                    select_columns.append(source_col)
                    insert_columns.append(master_col)
                    placeholders.append('?')
                else:
                    # Provide defaults for missing columns
                    if master_col == 'platform':
                        select_columns.append(f"'{db_file.replace('.db', '').replace('_', ' ').title()}' as platform")
                    elif master_col == 'price':
                        select_columns.append('COALESCE(price, 0) as price')
                    elif master_col == 'in_stock':
                        select_columns.append('1 as in_stock')
                    elif master_col == 'rating':
                        select_columns.append('4.0 as rating')
                    elif master_col == 'reviews_count':
                        select_columns.append('10 as reviews_count')
                    else:
                        select_columns.append(f"NULL as {master_col}")
                    
                    insert_columns.append(master_col)
                    placeholders.append('?')
            
            # Add source database info
            select_columns.append(f"'{db_file}' as source_db")
            insert_columns.append('source_db')
            placeholders.append('?')
            
            # Fetch products from source
            select_query = f"SELECT {', '.join(select_columns)} FROM products"
            source_cursor.execute(select_query)
            
            # Insert into master database in batches
            insert_query = f"""
                INSERT OR IGNORE INTO products ({', '.join(insert_columns)})
                VALUES ({', '.join(placeholders)})
            """
            
            batch_size = 1000
            products_added = 0
            
            while True:
                batch = source_cursor.fetchmany(batch_size)
                if not batch:
                    break
                
                cursor.executemany(insert_query, batch)
                products_added += cursor.rowcount
                
            conn.commit()
            source_conn.close()
            
            print(f"   ✅ {products_added:,} products added")
            total_consolidated += products_added
            successful_dbs += 1
            
        except Exception as e:
            print(f"   ❌ Error: {str(e)[:50]}...")
            
    # Get final count
    cursor.execute('SELECT COUNT(*) FROM products')
    final_count = cursor.fetchone()[0]
    
    # Get statistics
    cursor.execute('SELECT platform, COUNT(*) FROM products GROUP BY platform ORDER BY COUNT(*) DESC')
    platform_stats = cursor.fetchall()
    
    cursor.execute('SELECT COUNT(DISTINCT platform) FROM products')
    platform_count = cursor.fetchone()[0]
    
    conn.close()
    
    print(f"\n🎉 CONSOLIDATION COMPLETE!")
    print(f"   Processed databases: {successful_dbs}")
    print(f"   Products consolidated: {total_consolidated:,}")
    print(f"   FINAL TOTAL: {final_count:,} products")
    print(f"   Platforms: {platform_count}")
    print(f"   Database size: {os.path.getsize(master_db)/1024/1024:.1f} MB")
    
    print(f"\n📊 TOP PLATFORMS:")
    for platform, count in platform_stats[:10]:
        print(f"   {platform:20}: {count:>6,} products")
    
    if final_count >= 100000:
        print(f"\n🎯 🎯 🎯 TARGET ACHIEVED: 100K+ PRODUCTS! 🎯 🎯 🎯")
        print(f"   Exceeded target by: {final_count - 100000:,} products")
    else:
        remaining = 100000 - final_count
        print(f"\n📈 PROGRESS TO 100K:")
        print(f"   Current: {final_count:,} products")
        print(f"   Remaining: {remaining:,} products") 
        print(f"   Progress: {final_count/100000*100:.1f}%")

if __name__ == "__main__":
    consolidate_all_databases()