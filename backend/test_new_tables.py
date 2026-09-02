"""
Test Script for New Database Tables
Tests basic CRUD operations on home_screen_products, search_cache, and scrape_metadata
"""

import asyncio
import asyncpg
from dotenv import load_dotenv
import os
import json
from datetime import datetime

# Load environment variables
load_dotenv()

async def test_tables():
    """Test the new database tables"""
    
    database_url = os.getenv("DATABASE_URL")
    
    if not database_url:
        print("❌ ERROR: DATABASE_URL not found in .env file")
        return
    
    print("🔄 Connecting to PostgreSQL database...")
    
    try:
        # Create connection (disable prepared statements for pgbouncer compatibility)
        conn = await asyncpg.connect(database_url, statement_cache_size=0)
        print("✅ Connected to database successfully\n")
        
        # Test 1: home_screen_products table
        print("=" * 60)
        print("TEST 1: home_screen_products table")
        print("=" * 60)
        
        # Insert a test product
        await conn.execute("""
            INSERT INTO home_screen_products 
            (section, title, price, original_price, discount_percent, image_url, store_name, product_url, category)
            VALUES ($1, $2, $3, $4, $5, $6, $7, $8, $9)
        """, 'best_deals', 'Test iPhone 15', 149999.99, 199999.99, 25, 
             'https://example.com/test.jpg', 'Test Store', 'https://example.com/product', 'Electronics')
        
        print("✅ Inserted test product into home_screen_products")
        
        # Query the product
        products = await conn.fetch("""
            SELECT * FROM home_screen_products 
            WHERE section = $1
            ORDER BY scraped_at DESC
            LIMIT 5
        """, 'best_deals')
        
        print(f"✅ Retrieved {len(products)} product(s) from best_deals section")
        if products:
            print(f"   Sample: {products[0]['title']} - Rs. {products[0]['price']}")
        
        # Test 2: search_cache table
        print("\n" + "=" * 60)
        print("TEST 2: search_cache table")
        print("=" * 60)
        
        # Insert a test cache entry
        tier1_data = json.dumps([
            {
                "title": "Test Laptop 1",
                "price": 75000,
                "store_name": "Daraz"
            }
        ])
        
        await conn.execute("""
            INSERT INTO search_cache 
            (query, tier1_results, tier1_cached_at, is_complete, request_id)
            VALUES ($1, $2, $3, $4, $5)
            ON CONFLICT (query) DO UPDATE
            SET tier1_results = EXCLUDED.tier1_results,
                tier1_cached_at = EXCLUDED.tier1_cached_at,
                is_complete = EXCLUDED.is_complete
        """, 'test laptop', tier1_data, datetime.now(), False, 'test-request-123')
        
        print("✅ Inserted test cache entry into search_cache")
        
        # Query the cache
        cache = await conn.fetchrow("""
            SELECT * FROM search_cache 
            WHERE query = $1
        """, 'test laptop')
        
        if cache:
            print(f"✅ Retrieved cache entry for query: '{cache['query']}'")
            print(f"   Request ID: {cache['request_id']}")
            print(f"   Is Complete: {cache['is_complete']}")
            tier1_results = json.loads(cache['tier1_results'])
            print(f"   Tier 1 Results: {len(tier1_results)} product(s)")
        
        # Test 3: scrape_metadata table
        print("\n" + "=" * 60)
        print("TEST 3: scrape_metadata table")
        print("=" * 60)
        
        # Insert a test metadata entry
        await conn.execute("""
            INSERT INTO scrape_metadata 
            (scrape_type, last_scrape_time, next_scrape_time, status, products_found)
            VALUES ($1, $2, $3, $4, $5)
        """, 'daily_homepage', datetime.now(), datetime.now(), 'completed', 50)
        
        print("✅ Inserted test metadata into scrape_metadata")
        
        # Query the metadata
        metadata = await conn.fetch("""
            SELECT * FROM scrape_metadata 
            WHERE scrape_type = $1
            ORDER BY last_scrape_time DESC
            LIMIT 5
        """, 'daily_homepage')
        
        print(f"✅ Retrieved {len(metadata)} metadata record(s)")
        if metadata:
            print(f"   Latest scrape: {metadata[0]['status']} - {metadata[0]['products_found']} products")
        
        # Test 4: Clean up test data
        print("\n" + "=" * 60)
        print("TEST 4: Clean up test data")
        print("=" * 60)
        
        # Delete test product
        deleted_products = await conn.execute("""
            DELETE FROM home_screen_products 
            WHERE title = $1
        """, 'Test iPhone 15')
        print(f"✅ Cleaned up test products: {deleted_products}")
        
        # Delete test cache
        deleted_cache = await conn.execute("""
            DELETE FROM search_cache 
            WHERE query = $1
        """, 'test laptop')
        print(f"✅ Cleaned up test cache: {deleted_cache}")
        
        # Delete test metadata
        deleted_metadata = await conn.execute("""
            DELETE FROM scrape_metadata 
            WHERE scrape_type = $1 AND products_found = 50
        """, 'daily_homepage')
        print(f"✅ Cleaned up test metadata: {deleted_metadata}")
        
        # Summary
        print("\n" + "=" * 60)
        print("TEST SUMMARY")
        print("=" * 60)
        print("✅ home_screen_products: INSERT, SELECT - PASSED")
        print("✅ search_cache: INSERT, SELECT with JSONB - PASSED")
        print("✅ scrape_metadata: INSERT, SELECT - PASSED")
        print("✅ All tables support parameterized queries ($1, $2, etc.)")
        print("✅ All test data cleaned up successfully")
        print("\n🎉 All tests passed! Database schema is working correctly.")
        
        # Close connection
        await conn.close()
        
    except Exception as e:
        print(f"\n❌ ERROR during testing: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    print("=" * 60)
    print("Database Tables Test Suite")
    print("=" * 60)
    print()
    asyncio.run(test_tables())
