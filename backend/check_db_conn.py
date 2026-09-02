import asyncio
import asyncpg
import os
from dotenv import load_dotenv

async def check():
    load_dotenv()
    conn = await asyncpg.connect(os.getenv("DATABASE_URL"))
    rows = await conn.fetch("SELECT datname, usename, client_addr, state, query FROM pg_stat_activity WHERE datname = 'pricepilot'")
    for row in rows:
        print(dict(row))
    await conn.close()
    
if __name__ == "__main__":
    asyncio.run(check())
