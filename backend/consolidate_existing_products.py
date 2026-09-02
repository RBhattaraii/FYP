#!/usr/bin/env python3
"""
CONSOLIDATE EXISTING PRODUCTS
Move existing 18k products to master database with duplicate removal
"""

import sqlite3
import os
from datetime import datetime, timezone

def consolidate_existing_products():
    """Consolidate existing products into master database"""
    print("🔄 CONSOLIDATING EXISTING PRODUCTS")
    print("=" * 40)
    
    # Source database (your main 18k products)
    source_db = 'local_products.db'
    
    # Master database (new consolidated one)
    master_db = 'master_products.db'
    
    if not os.path.exists(source_db):
        print(f"❌ Source database {source_db} not found")
        return
    
    # Connect to both databases
    source_conn = sqlite3.connect(source_db)
    master_conn = sqlite3.connect(master_db)
    
    # Ensure master database exists with proper schema
    master_conn.execute('''
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
    
    # Create index for performance
    master_conn.execute('CREATE INDEX IF NOT EXISTS idx_product_url ON products(product_url)')
    master_conn.commit()
    
    # Get all products from source
    source_cursor = source_conn.cursor()
    source_cursor.execute('SELECT * FROM products')
    source_products = source_cursor.fetchall()
    
    # Get column names for mapping
    source_cursor.execute('PRAGMA table_info(products)')
    source_columns = [col[1] for col in source_cursor.fetchall()]
    
    print(f"📊 Found {len(source_products):,} products in source database")
    
    # Transfer products with duplicate checking
    master_cursor = master_conn.cursor()
    
    transferred = 0
    skipped_duplicates = 0
    skipped_no_url = 0
    
    for row in source_products:
        # Map row to dictionary
        product = dict(zip(source_columns, row))
        
        product_url = product.get('product_url', '')
        
        # Skip products without URLs
        if not product_url:
            skipped_no_url += 1
            continue
        
        # Check if already exists in master
        master_cursor.execute('SELECT id FROM products WHERE product_url = ?', (product_url,))
        if master_cursor.fetchone():
            skipped_duplicates += 1
            continue
        
        try:
            # Insert into master database
            master_cursor.execute('''
                INSERT INTO products 
                (title, price, original_price, discount_percent, image_url, 
                 store_name, product_url, category, scraped_at, platform, search_term, last_updated)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            ''', (
                product.get('title', 'Unknown Product'),
                product.get('price', 0),
                product.get('original_price'),
                product.get('discount_percentage'),
                product.get('image_url', ''),
                product.get('store_name', ''),
                product_url,
                product.get('category', ''),
                product.get('scraped_at', datetime.now(timezone.utc).isoformat()),
                product.get('store_name', ''),  # Use store_name as platform
                'consolidation',
                datetime.now(timezone.utc).isoformat()
            ))
            transferred += 1
            
            if transferred % 1000 == 0:
                print(f"   Transferred: {transferred:,} products...")
            
        except sqlite3.IntegrityError:
            # Duplicate URL (shouldn't happen due to pre-check)
            skipped_duplicates += 1
        except Exception as e:
            # Other error - skip
            continue
    
    master_conn.commit()
    
    # Final count in master database
    master_cursor.execute('SELECT COUNT(*) FROM products')
    final_count = master_cursor.fetchone()[0]
    
    # Platform distribution
    master_cursor.execute('SELECT store_name, COUNT(*) FROM products GROUP BY store_name ORDER BY COUNT(*) DESC')
    platforms = master_cursor.fetchall()
    
    print(f"\n✅ CONSOLIDATION COMPLETE!")
    print(f"📊 Results:")
    print(f"   • Transferred: {transferred:,} unique products")
    print(f"   • Skipped duplicates: {skipped_duplicates:,}")
    print(f"   • Skipped (no URL): {skipped_no_url:,}")
    print(f"   • Total in master: {final_count:,} products")
    
    print(f"\n🏪 Platform distribution in master database:")
    for platform, count in platforms:
        percentage = (count / final_count * 100) if final_count > 0 else 0
        print(f"   • {platform}: {count:,} products ({percentage:.1f}%)")
    
    # Database size
    master_size = os.path.getsize(master_db) / (1024 * 1024)
    print(f"\n💾 Master database: {master_size:.1f} MB")
    
    source_conn.close()
    master_conn.close()
    
    print(f"\n🎯 Master database ready for continued scraping!")
    print(f"   New products will be added without duplicates")

if __name__ == "__main__":
    consolidate_existing_products()