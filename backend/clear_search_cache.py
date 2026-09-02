import asyncio
import asyncpg
import os
from dotenv import load_dotenv

load_dotenv()

async def main():
    conn = await asyncpg.connect(os.getenv('DATABASE_URL'), statement_cache_size=0)
    await conn.execute('DELETE FROM search_cache')
    print('✅ Search cache cleared - next search will scrape fresh Jeevee products!')
    await conn.close()

asyncio.run(main())
