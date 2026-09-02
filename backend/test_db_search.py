import asyncio
import asyncpg
import os
from dotenv import load_dotenv

load_dotenv()

async def test_db_search():
    url = os.getenv('DATABASE_URL')
    conn = await asyncpg.connect(url, statement_cache_size=0)
    
    # Simulate DB search logic for "laptop"
    print("Testing DB search...")
    query = """
        WITH search_context AS (
            SELECT 
                $1::text AS raw_query,
                lower(regexp_replace($1, '[^a-zA-Z0-9\s]', ' ', 'g')) AS clean_query,
                string_to_array(lower(regexp_replace($1, '[^a-zA-Z0-9\s]', ' ', 'g')), ' ') AS tokens
        ),
        scored_products AS (
            SELECT 
                p.id, p.title, p.price, p.original_price, p.discount_percent, 
                p.image_url, p.store_name, p.product_url, p.category,
                
                (SELECT count(*) FROM unnest(c.tokens) t WHERE p.search_vector @@ to_tsquery('english', t || ':*')) AS matched_tokens,
                cardinality(c.tokens) AS total_tokens,
                
                CASE WHEN lower(p.title) LIKE '%' || c.clean_query || '%' THEN 1 ELSE 0 END AS exact_match
            FROM products p, search_context c
            WHERE p.search_vector @@ to_tsquery('english', array_to_string(c.tokens, ' | '))
        )
        SELECT *
        FROM scored_products
        ORDER BY 
            exact_match DESC,
            matched_tokens DESC,
            price DESC
        LIMIT 5;
    """
    
    results = await conn.fetch(query, "laptop")
    print(f"Found {len(results)} results")
    for r in results:
        print(f"{r['store_name']} | {r['price']} | {r['title'][:50]}")
        
    await conn.close()

asyncio.run(test_db_search())
