import asyncio
import os
import sys
from dotenv import load_dotenv

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import asyncpg

async def check_db():
    load_dotenv()
    database_url = os.getenv("DATABASE_URL")
    conn = await asyncpg.connect(database_url, statement_cache_size=0)
    
    count = await conn.fetchval("SELECT count(*) FROM products")
    print(f"Products in Supabase: {count}")
    
    await conn.close()

if __name__ == "__main__":
    asyncio.run(check_db())
