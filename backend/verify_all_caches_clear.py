"""
Verify that all caches are cleared and ready for fresh data
"""
import asyncio
import asyncpg
import os
from dotenv import load_dotenv

load_dotenv()

async def main():
    print("=" * 60)
    print("CACHE STATUS VERIFICATION")
    print("=" * 60)
    
    conn = await asyncpg.connect(os.getenv('DATABASE_URL'), statement_cache_size=0)
    
    # Check search cache
    search_count = await conn.fetchval('SELECT COUNT(*) FROM search_cache')
    print(f"\n📊 Search Cache: {search_count} entries")
    if search_count == 0:
        print("   ✅ CLEAR - Next search will use fixed scrapers")
    else:
        print("   ⚠️ NOT CLEAR - Run: python clear_search_cache.py")
    
    # Check home screen products
    home_count = await conn.fetchval('SELECT COUNT(*) FROM home_screen_products')
    print(f"\n📊 Home Screen Products: {home_count} entries")
    if home_count == 0:
        print("   ✅ CLEAR - Next home screen load will use fixed scrapers")
    else:
        print("   ⚠️ NOT CLEAR - Run: python clear_home_products.py")
    
    # Check if there are any old Jeevee/Oliz/Hukut URLs in cache
    if search_count > 0:
        print("\n🔍 Checking for old URLs in search cache...")
        old_jeevee = await conn.fetchval("""
            SELECT COUNT(*) FROM search_cache 
            WHERE cached_results::text LIKE '%jeevee.com/products/%'
            AND cached_results::text NOT LIKE '%jeevee.com/products/%-[0-9]%'
        """)
        if old_jeevee > 0:
            print(f"   ⚠️ Found {old_jeevee} entries with old Jeevee URLs")
    
    await conn.close()
    
    print("\n" + "=" * 60)
    print("SUMMARY")
    print("=" * 60)
    
    if search_count == 0 and home_count == 0:
        print("✅ All caches are clear!")
        print("✅ Ready to start backend server")
        print("\nNext: Run 'start_fresh.bat' to start the server")
    else:
        print("⚠️ Some caches still have data")
        print("\nRun these commands to clear:")
        if search_count > 0:
            print("  python clear_search_cache.py")
        if home_count > 0:
            print("  python clear_home_products.py")

if __name__ == "__main__":
    asyncio.run(main())
