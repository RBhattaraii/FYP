"""Clear search cache and test a fresh search"""
import asyncio
import os
import sys
sys.path.insert(0, os.path.dirname(__file__))

from dotenv import load_dotenv
load_dotenv(os.path.join(os.path.dirname(__file__), 'backend', '.env'))
import asyncpg

async def main():
    db_url = os.getenv("DATABASE_URL")
    if not db_url:
        print("ERROR: DATABASE_URL not set")
        return
        
    conn = await asyncpg.connect(db_url, statement_cache_size=0)
    
    # Clear search cache
    result = await conn.execute("DELETE FROM search_cache")
    print(f"Cleared search cache: {result}")
    
    # Check how many home screen products we have
    count = await conn.fetchval("SELECT COUNT(*) FROM home_screen_products")
    print(f"Home screen products: {count}")
    
    # Check latest scrape metadata
    meta = await conn.fetchrow("""
        SELECT scrape_type, last_scrape_time, status, products_found 
        FROM scrape_metadata 
        ORDER BY last_scrape_time DESC LIMIT 1
    """)
    if meta:
        print(f"Last scrape: {dict(meta)}")
    else:
        print("No scrape metadata found")
    
    await conn.close()
    print("Done!")

asyncio.run(main())
