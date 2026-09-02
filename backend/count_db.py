import asyncpg, asyncio, os
from dotenv import load_dotenv
load_dotenv()

async def main():
    conn = await asyncpg.connect(os.getenv("DATABASE_URL"), statement_cache_size=0)
    total = await conn.fetchval("SELECT COUNT(*) FROM products")
    by_store = await conn.fetch("SELECT store_name, COUNT(*) as cnt FROM products GROUP BY store_name ORDER BY cnt DESC")
    print(f"Total products: {total}")
    for row in by_store:
        print(f"  {row['store_name']}: {row['cnt']}")
    await conn.close()

asyncio.run(main())
