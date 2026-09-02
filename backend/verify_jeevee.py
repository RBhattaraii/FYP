import asyncio
import asyncpg
import os
from dotenv import load_dotenv

load_dotenv()

async def main():
    conn = await asyncpg.connect(os.getenv('DATABASE_URL'), statement_cache_size=0)
    
    # Count Jeevee products
    count = await conn.fetchval("SELECT COUNT(*) FROM home_screen_products WHERE store_name = 'Jeevee'")
    print(f"\n✅ Total Jeevee products in database: {count}")
    
    # Show recent products
    result = await conn.fetch("""
        SELECT title, price, product_url 
        FROM home_screen_products 
        WHERE store_name = 'Jeevee' 
        ORDER BY scraped_at DESC 
        LIMIT 10
    """)
    
    print("\n📋 Recently added Jeevee products:")
    print("=" * 80)
    for row in result:
        print(f"{row['title'][:60]}")
        print(f"  Price: Rs {row['price']:,.0f}")
        print(f"  URL: {row['product_url']}")
        print()
    
    await conn.close()

asyncio.run(main())
