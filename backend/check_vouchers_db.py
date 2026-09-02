import asyncio
import asyncpg
import os
from dotenv import load_dotenv

async def check():
    load_dotenv()
    conn = await asyncpg.connect(os.getenv("DATABASE_URL"), statement_cache_size=0)
    rows = await conn.fetch("SELECT * FROM vouchers")
    for row in rows:
        print(dict(row))
    await conn.close()
    
if __name__ == "__main__":
    asyncio.run(check())
