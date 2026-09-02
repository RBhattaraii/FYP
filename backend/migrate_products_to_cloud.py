#!/usr/bin/env python3
"""
Migration script to upload 46k+ scraped products from local SQLite to cloud PostgreSQL
This populates the products table for search functionality while keeping 
home_screen_products separate for curated home screen content.
"""

import sqlite3
import asyncpg
import asyncio
from dotenv import load_dotenv
import os
from datetime import datetime

# Load environment variables
load_dotenv()

async def migrate_products():
    """
    Migrate products from local SQLite to cloud PostgreSQL products table
    """
    
    # Database configurations
    sqlite_db = "master_100k_products.db"
    postgres_url = os.getenv('DATABASE_URL')
    
    if not os.path.exists(sqlite_db):
        print(f"❌ SQLite database {sqlite_db} not found!")
        return
    
    print("🚀 Starting migration of 46k+ products to cloud database...")
    print(f"📁 Source: {sqlite_db}")
    print(f"☁️  Destination: PostgreSQL (products table)")
    
    # Connect to SQLite (source)
    sqlite_conn = sqlite3.connect(sqlite_db)
    sqlite_conn.row_factory = sqlite3.Row  # Enable column access by name
    sqlite_cursor = sqlite_conn.cursor()
    
    # Connect to PostgreSQL (destination) with disabled statement cache for pgbouncer
    pg_conn = await asyncpg.connect(postgres_url, statement_cache_size=0)
    
    try:
        # Get total count from SQLite
        sqlite_cursor.execute("SELECT COUNT(*) FROM products")
        total_products = sqlite_cursor.fetchone()[0]
        print(f"📊 Total products to migrate: {total_products:,}")
        
        # Check current PostgreSQL products count
        current_count = await pg_conn.fetchval("SELECT COUNT(*) FROM products")
        print(f"📊 Current products in cloud: {current_count:,}")
        
        # Clear existing products table (optional - comment out if you want to keep existing)
        print("🗑️  Clearing existing products table...")
        await pg_conn.execute("TRUNCATE TABLE products RESTART IDENTITY CASCADE")
        
        # Batch processing for efficiency
        batch_size = 1000
        processed = 0
        
        # Get all products from SQLite
        sqlite_cursor.execute("""
            SELECT title, price, original_price, discount_percent, 
                   image_url, product_url, category, brand, platform,
                   rating, reviews_count, in_stock, scraped_at
            FROM products 
            WHERE title IS NOT NULL AND product_url IS NOT NULL
            ORDER BY id
        """)
        
        batch = []
        
        while True:
            rows = sqlite_cursor.fetchmany(batch_size)
            if not rows:
                break
                
            # Prepare batch data for PostgreSQL
            for row in rows:
                # Map SQLite columns to PostgreSQL schema
                product_data = {
                    'title': row['title'],
                    'price': min(row['price'] if row['price'] is not None else 0.0, 99999999.99),  # Cap at max DECIMAL(10,2)
                    'original_price': min(row['original_price'] if row['original_price'] is not None else None, 99999999.99) if row['original_price'] is not None else None,
                    'discount_percent': int(row['discount_percent']) if row['discount_percent'] is not None else None,
                    'image_url': row['image_url'],
                    'store_name': row['platform'],  # platform -> store_name
                    'product_url': row['product_url'],
                    'category': row['category'],
                    'scraped_at': datetime.now()  # Use current timestamp
                }
                batch.append(product_data)
            
            # Insert batch into PostgreSQL
            if batch:
                await pg_conn.executemany("""
                    INSERT INTO products (
                        title, price, original_price, discount_percent,
                        image_url, store_name, product_url, category, scraped_at
                    ) VALUES (
                        $1, $2, $3, $4, $5, $6, $7, $8, $9
                    ) ON CONFLICT (product_url) DO NOTHING
                """, [
                    (
                        p['title'], p['price'], p['original_price'], p['discount_percent'],
                        p['image_url'], p['store_name'], p['product_url'], p['category'], p['scraped_at']
                    ) for p in batch
                ])
                
                processed += len(batch)
                print(f"✅ Migrated {processed:,}/{total_products:,} products ({processed/total_products*100:.1f}%)")
                batch.clear()
        
        # Final count verification
        final_count = await pg_conn.fetchval("SELECT COUNT(*) FROM products")
        print(f"\n🎉 Migration completed!")
        print(f"📊 Final count in cloud: {final_count:,} products")
        
        # Show sample by store
        print(f"\n📈 Products by store:")
        stores = await pg_conn.fetch("""
            SELECT store_name, COUNT(*) as count 
            FROM products 
            GROUP BY store_name 
            ORDER BY count DESC
        """)
        
        for store in stores:
            print(f"   {store['store_name']}: {store['count']:,} products")
            
    except Exception as e:
        print(f"❌ Error during migration: {e}")
        raise
        
    finally:
        # Close connections
        sqlite_conn.close()
        await pg_conn.close()
        
    print(f"\n🔍 Your search will now return results from {final_count:,} products instead of 2,194!")
    print("🏠 Home screen products remain separate and curated (110 products)")

if __name__ == "__main__":
    asyncio.run(migrate_products())