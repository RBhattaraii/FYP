import asyncio
import asyncpg
import os
from dotenv import load_dotenv

load_dotenv()

async def delete_old_data():
    url = os.getenv('DATABASE_URL')
    conn = await asyncpg.connect(url, statement_cache_size=0)
    
    # Check count before deletion
    count_before = await conn.fetchval("SELECT count(*) FROM products")
    print(f"Total products before deletion: {count_before}")
    
    # Delete everything except the 4 CSV stores
    res = await conn.execute(
        "DELETE FROM products WHERE store_name NOT IN ('Oliz', 'CG Digital', 'KoreanBP', 'Hukut')"
    )
    print(f"Delete result: {res}")
    
    # Check count after deletion
    count_after = await conn.fetchval("SELECT count(*) FROM products")
    print(f"Total products after deletion: {count_after}")
    
    # Check count by store
    stores = await conn.fetch("SELECT store_name, count(*) FROM products GROUP BY store_name")
    for s in stores:
        print(f"{s['store_name']}: {s['count']}")
        
    await conn.close()

if __name__ == "__main__":
    asyncio.run(delete_old_data())
