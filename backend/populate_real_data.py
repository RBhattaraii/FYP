#!/usr/bin/env python3
"""
Real Data Population Script
Scrapes actual websites and populates database with real products
"""

import asyncio
import asyncpg
import sys
import os
from datetime import datetime, timezone

# Add paths for imports
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))
sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'scrapers'))

# Import real scrapers
from scrapers.daraz.daraz_scraper import sync_scrape_daraz
from scrapers.cgdigital.cgdigital_scraper import async_scrape_cgdigital

# Database connection
DATABASE_URL = "postgresql://postgres.cukfnnjuofbvsrwwkdsh:gKaBwfxiaFauuKyS@aws-1-ap-northeast-1.pooler.supabase.com:6543/postgres"

# Search queries for scraping
SEARCH_QUERIES = [
    "laptop",
    "mobile phone", 
    "headphones",
    "mouse",
    "keyboard",
    "smartphone",
    "tablet",
    "charger",
    "power bank",
    "speaker"
]

async def insert_products(conn, products, store_name):
    """Insert products into the database"""
    if not products:
        print(f"❌ No products to insert for {store_name}")
        return 0
    
    inserted_count = 0
    
    for product in products:
        try:
            # Insert into main products table
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
                product.get('product_name', 'Unknown Product'),
                float(product.get('price', 0)),
                float(product.get('original_price', 0)) if product.get('original_price') else None,
                float(product.get('discount_percentage', 0)) if product.get('discount_percentage') else None,
                product.get('image_url', ''),
                store_name,
                product.get('product_url', ''),
                product.get('category', 'General'),
                datetime.now(timezone.utc),
            )
            inserted_count += 1
            
        except Exception as e:
            print(f"❌ Error inserting product: {e}")
            continue
    
    print(f"✅ Inserted {inserted_count} products from {store_name}")
    return inserted_count

async def scrape_daraz_products(conn):
    """Scrape products from Daraz"""
    print("🔥 SCRAPING DARAZ (Real Website)...")
    total_products = 0
    
    for query in SEARCH_QUERIES:
        print(f"  🔍 Searching for: {query}")
        try:
            products = sync_scrape_daraz(query, max_pages=2)  # 2 pages per query
            count = await insert_products(conn, products, "Daraz")
            total_products += count
            print(f"    ➡️  Added {count} products for '{query}'")
            
            # Small delay to be respectful
            await asyncio.sleep(1)
            
        except Exception as e:
            print(f"    ❌ Error scraping Daraz for '{query}': {e}")
    
    print(f"🎯 DARAZ TOTAL: {total_products} real products added")
    return total_products

async def scrape_cgdigital_products(conn):
    """Scrape products from CGDigital"""
    print("💻 SCRAPING CGDIGITAL (Real Website)...")
    total_products = 0
    
    for query in SEARCH_QUERIES:
        print(f"  🔍 Searching for: {query}")
        try:
            products = await async_scrape_cgdigital(query)  # Use async version
            count = await insert_products(conn, products, "CgDigital")
            total_products += count
            print(f"    ➡️  Added {count} products for '{query}'")
            
            # Small delay to be respectful
            await asyncio.sleep(2)
            
        except Exception as e:
            print(f"    ❌ Error scraping CGDigital for '{query}': {e}")
    
    print(f"🎯 CGDIGITAL TOTAL: {total_products} real products added")
    return total_products

async def update_home_screen_products(conn):
    """Populate home screen with best products"""
    print("🏠 CREATING HOME SCREEN CURATED PRODUCTS...")
    
    try:
        # Clear existing home screen products
        await conn.execute("DELETE FROM home_screen_products")
        
        # Get best deals (highest discount)
        best_deals = await conn.fetch("""
            SELECT * FROM products 
            WHERE discount_percent > 0 
            ORDER BY discount_percent DESC 
            LIMIT 25
        """)
        
        # Insert as best deals
        for product in best_deals:
            await conn.execute("""
                INSERT INTO home_screen_products (
                    title, price, original_price, discount_percent,
                    image_url, store_name, product_url, category, section, scraped_at
                ) VALUES ($1, $2, $3, $4, $5, $6, $7, $8, $9, $10)
            """, 
                product['title'], product['price'], product['original_price'],
                product['discount_percent'], product['image_url'], product['store_name'],
                product['product_url'], product['category'], 'best_deals',
                datetime.now(timezone.utc)
            )
        
        # Get price drops (products with original price)
        price_drops = await conn.fetch("""
            SELECT * FROM products 
            WHERE original_price IS NOT NULL AND original_price > price
            ORDER BY (original_price - price) DESC 
            LIMIT 25
        """)
        
        # Insert as price drops
        for product in price_drops:
            await conn.execute("""
                INSERT INTO home_screen_products (
                    title, price, original_price, discount_percent,
                    image_url, store_name, product_url, category, section, scraped_at
                ) VALUES ($1, $2, $3, $4, $5, $6, $7, $8, $9, $10)
            """, 
                product['title'], product['price'], product['original_price'],
                product['discount_percent'], product['image_url'], product['store_name'],
                product['product_url'], product['category'], 'top_price_drops',
                datetime.now(timezone.utc)
            )
        
        print(f"✅ Created {len(best_deals)} best deals and {len(price_drops)} price drops")
        
    except Exception as e:
        print(f"❌ Error creating home screen products: {e}")

async def main():
    """Main function to populate real data"""
    print("🚀 STARTING REAL DATA POPULATION")
    print("=" * 50)
    
    try:
        # Connect to database
        conn = await asyncpg.connect(DATABASE_URL, statement_cache_size=0)
        print("✅ Connected to database")
        
        # Check initial state
        initial_count = await conn.fetchval("SELECT COUNT(*) FROM products")
        print(f"📊 Initial products in database: {initial_count}")
        
        total_scraped = 0
        
        # Scrape Daraz (most reliable)
        daraz_count = await scrape_daraz_products(conn)
        total_scraped += daraz_count
        
        # Scrape CGDigital  
        cg_count = await scrape_cgdigital_products(conn)
        total_scraped += cg_count
        
        # Update home screen
        await update_home_screen_products(conn)
        
        # Final count
        final_count = await conn.fetchval("SELECT COUNT(*) FROM products")
        home_count = await conn.fetchval("SELECT COUNT(*) FROM home_screen_products")
        
        print("\n" + "=" * 50)
        print("🎉 REAL DATA POPULATION COMPLETE!")
        print(f"📊 Total products now: {final_count}")
        print(f"🏠 Home screen products: {home_count}")
        print(f"➕ New products added: {final_count - initial_count}")
        print(f"🔥 Successfully scraped: {total_scraped} real products")
        
        # Show sample products
        print("\n📋 SAMPLE REAL PRODUCTS:")
        samples = await conn.fetch("SELECT title, price, store_name FROM products ORDER BY scraped_at DESC LIMIT 5")
        for i, product in enumerate(samples, 1):
            print(f"  {i}. {product['title'][:50]}... - Rs {product['price']} ({product['store_name']})")
        
        await conn.close()
        
    except Exception as e:
        print(f"❌ Critical error: {e}")
        return 1
    
    print("\n✅ Database now contains REAL products from actual websites!")
    print("🎯 Your app will now show real Daraz and CGDigital products!")
    return 0

if __name__ == "__main__":
    exit_code = asyncio.run(main())
    sys.exit(exit_code)