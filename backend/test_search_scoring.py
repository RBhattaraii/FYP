import asyncpg, asyncio, os
from dotenv import load_dotenv
load_dotenv()

async def main():
    conn = await asyncpg.connect(os.getenv("DATABASE_URL"), statement_cache_size=0)
    
    query = "Redmi Note 14"
    
    # We will build a complex SQL query to calculate the relevance score.
    # We need pg_trgm for fuzzy matching. Let's make sure it's installed.
    await conn.execute("CREATE EXTENSION IF NOT EXISTS pg_trgm;")
    
    sql = """
    WITH search_tokens AS (
        SELECT 
            $1::text AS raw_query,
            regexp_replace(lower($1), '[^a-z0-9\s]', ' ', 'g') AS clean_query,
            string_to_array(regexp_replace(lower($1), '[^a-z0-9\s]', ' ', 'g'), ' ') AS tokens
    ),
    scored_products AS (
        SELECT 
            id, title, price, store_name, category, product_url, image_url,
            (
                -- Exact match
                CASE WHEN lower(title) = lower(st.raw_query) THEN 100 ELSE 0 END +
                
                -- Starts with query
                CASE WHEN lower(title) LIKE lower(st.raw_query) || '%' THEN 80 ELSE 0 END +
                
                -- Contains entire query string exactly
                CASE WHEN lower(title) LIKE '%' || lower(st.raw_query) || '%' THEN 60 ELSE 0 END +
                
                -- Contains all keywords (tsvector match)
                CASE WHEN search_vector @@ plainto_tsquery('english', st.raw_query) THEN 40 ELSE 0 END +
                
                -- Brand match (assume first word is brand for now)
                CASE WHEN lower(title) LIKE lower(st.tokens[1]) || '%' THEN 20 ELSE 0 END -
                
                -- Accessory penalty (if query doesn't contain 'case', 'cover' etc., but title does)
                CASE WHEN 
                    st.raw_query NOT ILIKE '%case%' AND st.raw_query NOT ILIKE '%cover%' 
                    AND (title ILIKE '%case%' OR title ILIKE '%cover%' OR title ILIKE '%tempered glass%' OR title ILIKE '%charger%') 
                THEN 50 ELSE 0 END +
                
                -- Fuzzy matching for small spelling mistakes (using word_similarity)
                (word_similarity(st.raw_query, title) * 10)
            ) AS relevance_score
        FROM products p, search_tokens st
        WHERE 
            search_vector @@ plainto_tsquery('english', st.raw_query)
            OR word_similarity(st.raw_query, title) > 0.3
            OR lower(title) LIKE '%' || lower(st.raw_query) || '%'
    )
    SELECT title, store_name, relevance_score, price 
    FROM scored_products
    ORDER BY relevance_score DESC, price ASC
    LIMIT 20;
    """
    
    rows = await conn.fetch(sql, query)
    print(f"Results for '{query}':")
    for r in rows:
        print(f"[{r['relevance_score']:.2f}] {r['title'][:50]} ({r['store_name']} - Rs {r['price']})")
        
    await conn.close()

asyncio.run(main())
