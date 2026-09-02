import asyncpg, asyncio, os
from dotenv import load_dotenv
load_dotenv()

async def main():
    conn = await asyncpg.connect(os.getenv("DATABASE_URL"), statement_cache_size=0)
    
    print("Creating extensions and indexes to speed up search on 500k rows...")
    
    # Enable pg_trgm for fast LIKE and fuzzy matching
    await conn.execute("CREATE EXTENSION IF NOT EXISTS pg_trgm;")
    
    # Create GIN index for full-text search
    print("Creating GIN index on search_vector...")
    await conn.execute("CREATE INDEX CONCURRENTLY IF NOT EXISTS idx_products_search_vector ON products USING GIN (search_vector);")
    
    # Create GIN index for fast fuzzy text matching and ILIKE
    print("Creating GIN index on title (pg_trgm)...")
    await conn.execute("CREATE INDEX CONCURRENTLY IF NOT EXISTS idx_products_title_trgm ON products USING GIN (title gin_trgm_ops);")
    
    print("Done optimizing!")
    await conn.close()

asyncio.run(main())
