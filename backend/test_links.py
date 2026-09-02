import asyncpg
import asyncio
import os
from dotenv import load_dotenv

load_dotenv()

async def main():
    conn = await asyncpg.connect(os.getenv('DATABASE_URL'), statement_cache_size=0)
    for store in ['Oliz Store', 'Hukut', 'Jeevee']:
        url = await conn.fetchval(f"SELECT product_url FROM products WHERE store_name ILIKE '%{store}%' LIMIT 1")
        print(f'{store}: {url}')
    await conn.close()

asyncio.run(main())
