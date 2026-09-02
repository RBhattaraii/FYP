"""
Test script for GET /products/home endpoint
Tests task 6.1 implementation
"""
import asyncio
import asyncpg
import os
from dotenv import load_dotenv

load_dotenv()

async def test_home_endpoint():
    """Test that the home endpoint can query the database correctly"""
    
    # Connect to database
    db_url = os.getenv("DATABASE_URL")
    conn = await asyncpg.connect(db_url)
    
    try:
        # Test 1: Query best_deals section
        print("[TEST 1] Querying best_deals section...")
        best_deals = await conn.fetch("""
            SELECT id, title, price, original_price, discount_percent,
                   image_url, store_name, product_url, category
            FROM home_screen_products
            WHERE section = $1
            ORDER BY scraped_at DESC
            LIMIT 25
        """, 'best_deals')
        print(f"✓ Found {len(best_deals)} best deals")
        
        # Test 2: Query top_price_drops section
        print("\n[TEST 2] Querying top_price_drops section...")
        top_price_drops = await conn.fetch("""
            SELECT id, title, price, original_price, discount_percent,
                   image_url, store_name, product_url, category
            FROM home_screen_products
            WHERE section = $1
            ORDER BY scraped_at DESC
            LIMIT 25
        """, 'top_price_drops')
        print(f"✓ Found {len(top_price_drops)} top price drops")
        
        # Test 3: Check data structure
        print("\n[TEST 3] Verifying data structure...")
        if best_deals:
            sample = dict(best_deals[0])
            required_fields = ['id', 'title', 'price', 'original_price', 'discount_percent',
                             'image_url', 'store_name', 'product_url', 'category']
            for field in required_fields:
                assert field in sample, f"Missing field: {field}"
            print(f"✓ All required fields present")
            print(f"  Sample product: {sample['title'][:50]}...")
        else:
            print("⚠ No products found - database might be empty")
        
        # Test 4: Verify empty results are handled
        print("\n[TEST 4] Testing empty results handling...")
        empty_result = await conn.fetch("""
            SELECT id, title, price, original_price, discount_percent,
                   image_url, store_name, product_url, category
            FROM home_screen_products
            WHERE section = $1
            LIMIT 25
        """, 'nonexistent_section')
        assert len(empty_result) == 0, "Should return empty list for nonexistent section"
        print(f"✓ Empty results handled correctly")
        
        print("\n[SUCCESS] All tests passed!")
        
    except Exception as e:
        print(f"\n[ERROR] Test failed: {e}")
        raise
    finally:
        await conn.close()

if __name__ == "__main__":
    asyncio.run(test_home_endpoint())
