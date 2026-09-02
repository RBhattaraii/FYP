import asyncpg, asyncio, os
from dotenv import load_dotenv
load_dotenv()

async def main():
    url = os.getenv('DATABASE_URL')
    conn = await asyncpg.connect(url, statement_cache_size=0)
    
    query = 'redmi note 11'
    
    # Test full-text search
    rows_fts = await conn.fetch(
        "SELECT id, title, store_name FROM products WHERE search_vector @@ websearch_to_tsquery('english', $1) LIMIT 20",
        query
    )
    print(f"Full-text search results for '{query}': {len(rows_fts)}")
    
    # Test ILIKE
    rows_ilike = await conn.fetch(
        "SELECT id, title, store_name FROM products WHERE title ILIKE $1 LIMIT 20",
        f'%{query}%'
    )
    print(f"ILIKE results: {len(rows_ilike)}")
    
    # Test combined
    rows_combined = await conn.fetch(
        "SELECT id, title, store_name FROM products WHERE search_vector @@ websearch_to_tsquery('english', $1) OR title ILIKE $2 LIMIT 100",
        query, f'%redmi note 11%'
    )
    print(f"Combined results: {len(rows_combined)}")
    for r in rows_combined[:10]:
        print(f"  {r['store_name']}: {r['title'][:60]}")
    
    # Check if search_vector is populated
    sample = await conn.fetchrow("SELECT title, search_vector FROM products LIMIT 1")
    print(f"\nsearch_vector populated: {sample['search_vector'] is not None}")
    
    await conn.close()

asyncio.run(main())
