import asyncio
import asyncpg
from dotenv import load_dotenv
import os

load_dotenv()

async def main():
    url = os.getenv("DATABASE_URL")
    print(f"Testing: {url[:50]}...")
    try:
        conn = await asyncpg.connect(url, timeout=10, statement_cache_size=0)
        result = await conn.fetchval("SELECT 1")
        print(f"SUCCESS! Connected to PostgreSQL. Result: {result}")
        count = await conn.fetchval("SELECT COUNT(*) FROM users")
        print(f"Users in database: {count}")
        await conn.close()
    except Exception as e:
        print(f"FAILED: {type(e).__name__}: {e}")

asyncio.run(main())
