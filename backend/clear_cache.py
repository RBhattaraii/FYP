"""Clear the search cache so fresh scrapes use the new URL normalization."""
import asyncio
import asyncpg
import os
from dotenv import load_dotenv

load_dotenv()

async def clear():
    db_url = os.getenv("DATABASE_URL")
    if not db_url:
        print("No DATABASE_URL found")
        return
    conn = await asyncpg.connect(db_url)
    deleted = await conn.execute("DELETE FROM search_cache")
    print(f"Search cache cleared: {deleted}")
    await conn.close()

if __name__ == "__main__":
    asyncio.run(clear())
