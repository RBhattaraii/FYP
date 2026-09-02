import asyncpg
import asyncio
import os
from dotenv import load_dotenv

load_dotenv()

async def main():
    conn = await asyncpg.connect(os.getenv('DATABASE_URL'), statement_cache_size=0)
    for store in ['Oliz Store', 'Hukut', 'Jeevee', 'Daraz']:
        count = await conn.fetchval(f"SELECT count(*) FROM products WHERE store_name ILIKE '%{store}%'")
        null_count = await conn.fetchval(f"SELECT count(*) FROM products WHERE store_name ILIKE '%{store}%' AND product_url IS NULL")
        synthetic = await conn.fetchval(f"SELECT count(*) FROM products WHERE store_name ILIKE '%{store}%' AND product_url LIKE '%synthetic%'")
        print(f'{store}: {count} total, {null_count} nulls, {synthetic} synthetic')
    await conn.close()

asyncio.run(main())
