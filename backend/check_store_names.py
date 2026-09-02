import asyncio
import asyncpg
import os
from dotenv import load_dotenv

load_dotenv()

async def check_stores():
    conn = await asyncpg.connect(os.getenv('DATABASE_URL'), statement_cache_size=0)
    
    stores = await conn.fetch("SELECT DISTINCT store_name FROM home_screen_products ORDER BY store_name")
    
    print("\nAll store names in database:\n")
    for s in stores:
        print(f"  - '{s['store_name']}'")
    
    await conn.close()

asyncio.run(check_stores())
