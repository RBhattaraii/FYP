import asyncio
import asyncpg
import os
from dotenv import load_dotenv

load_dotenv()

async def main():
    conn = await asyncpg.connect(os.getenv('DATABASE_URL'), statement_cache_size=0)
    
    # Get sample Jeevee products
    result = await conn.fetch("""
        SELECT title, product_url, scraped_at
        FROM home_screen_products 
        WHERE store_name = 'Jeevee' 
        ORDER BY scraped_at DESC
        LIMIT 10
    """)
    
    print(f"\n📋 Jeevee Products in Database ({len(result)} samples):\n")
    for i, row in enumerate(result, 1):
        print(f"{i}. {row['title'][:60]}")
        print(f"   URL: {row['product_url']}")
        print(f"   Scraped: {row['scraped_at']}")
        print()
    
    # Count total
    count = await conn.fetchval("SELECT COUNT(*) FROM home_screen_products WHERE store_name = 'Jeevee'")
    print(f"Total Jeevee products in DB: {count}")
    
    await conn.close()

asyncio.run(main())
