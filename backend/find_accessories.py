import asyncpg, asyncio, os
from dotenv import load_dotenv
load_dotenv()

async def main():
    url = os.getenv('DATABASE_URL')
    conn = await asyncpg.connect(url, statement_cache_size=0)
    
    # Query for products resembling Apple iPhone 17
    rows = await conn.fetch(
        "SELECT id, title, price, store_name, category FROM products WHERE title ILIKE '%Apple iPhone 17%' OR title ILIKE '%Apple iPhone 15%' OR title ILIKE '%Apple iPhone 16%' LIMIT 20"
    )
    
    print("Found products:")
    for r in rows:
        print(f"ID: {r['id']} | Price: {r['price']} | Store: {r['store_name']} | Category: {r['category']}")
        print(f"  Title: {r['title']}")
        print("-" * 50)
        
    await conn.close()

asyncio.run(main())
