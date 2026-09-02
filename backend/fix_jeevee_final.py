"""
Final Fix for Jeevee Links

Problem: Old Jeevee products in database have expired/invalid URLs
Solution: Delete all Jeevee products from home_screen_products
Result: Search will scrape fresh Jeevee products with working URLs every time
"""
import asyncio
import asyncpg
import os
from dotenv import load_dotenv

load_dotenv()

async def main():
    conn = await asyncpg.connect(os.getenv('DATABASE_URL'), statement_cache_size=0)
    
    print("\n" + "=" * 70)
    print("JEEVEE LINK FIX - FINAL")
    print("=" * 70)
    
    # Count current Jeevee products
    count_before = await conn.fetchval(
        "SELECT COUNT(*) FROM home_screen_products WHERE store_name = 'Jeevee'"
    )
    print(f"\n📊 Current Jeevee products in database: {count_before}")
    
    # Delete all Jeevee products
    print(f"\n🗑️  Deleting old Jeevee products...")
    deleted = await conn.execute(
        "DELETE FROM home_screen_products WHERE store_name = 'Jeevee'"
    )
    print(f"✅ Deleted: {deleted.split()[-1]} products")
    
    # Verify deletion
    count_after = await conn.fetchval(
        "SELECT COUNT(*) FROM home_screen_products WHERE store_name = 'Jeevee'"
    )
    print(f"\n📊 Remaining Jeevee products: {count_after}")
    
    print("\n" + "=" * 70)
    print("✨ FIX COMPLETE!")
    print("=" * 70)
    print("\n📝 What happens now:")
    print("  1. No Jeevee products in home screen (they expire quickly anyway)")
    print("  2. When users SEARCH, they get FRESH Jeevee products")
    print("  3. Fresh products have WORKING links (just scraped)")
    print("  4. Search cache lasts 24 hours, then scrapes fresh again")
    print("\n💡 Test it:")
    print('  curl "http://localhost:8000/products/search?q=laptop"')
    print("  → Will include fresh Jeevee products with working links!")
    print()
    
    await conn.close()

asyncio.run(main())
