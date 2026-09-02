import asyncio
import asyncpg
import os
from dotenv import load_dotenv

load_dotenv()

async def check_db():
    url = os.getenv('DATABASE_URL')
    conn = await asyncpg.connect(url, statement_cache_size=0)
    
    # Check total count
    count = await conn.fetchval("SELECT count(*) FROM products")
    print(f"Total products: {count}")
    
    # Check count by store
    stores = await conn.fetch("SELECT store_name, count(*) FROM products GROUP BY store_name")
    for s in stores:
        print(f"{s['store_name']}: {s['count']}")
        
    await conn.close()

if __name__ == "__main__":
    asyncio.run(check_db())
