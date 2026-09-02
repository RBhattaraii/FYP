import asyncpg, asyncio, os, time
from dotenv import load_dotenv
load_dotenv()

async def main():
    conn = await asyncpg.connect(os.getenv("DATABASE_URL"), statement_cache_size=0)
    
    query = "Redmi Note 14"
    
    # We will build a complex SQL query to calculate the relevance score.
    sql = """
    WITH search_context AS (
        SELECT 
            $1::text AS raw_query,
            lower(regexp_replace($1, '[^a-zA-Z0-9\s]', ' ', 'g')) AS clean_query,
            string_to_array(lower(regexp_replace($1, '[^a-zA-Z0-9\s]', ' ', 'g')), ' ') AS tokens
    ),
    scored_products AS (
        SELECT 
            p.id, p.title, p.price, p.store_name, p.category, p.image_url, p.product_url, p.original_price, p.discount_percent,
            lower(regexp_replace(p.title, '[^a-zA-Z0-9\s]', ' ', 'g')) AS clean_title,
            (
                CASE WHEN lower(regexp_replace(p.title, '[^a-zA-Z0-9\s]', ' ', 'g')) = (SELECT clean_query FROM search_context) THEN 100 ELSE 0 END
                + CASE WHEN lower(regexp_replace(p.title, '[^a-zA-Z0-9\s]', ' ', 'g')) LIKE (SELECT clean_query FROM search_context) || '%' THEN 80 ELSE 0 END
                + CASE WHEN lower(regexp_replace(p.title, '[^a-zA-Z0-9\s]', ' ', 'g')) LIKE '%' || (SELECT clean_query FROM search_context) || '%' THEN 60 ELSE 0 END
                + CASE WHEN p.search_vector @@ websearch_to_tsquery('english', $1) THEN 40 ELSE 0 END
                + CASE WHEN split_part(lower(regexp_replace(p.title, '[^a-zA-Z0-9\s]', ' ', 'g')), ' ', 1) = (SELECT tokens[1] FROM search_context) THEN 20 ELSE 0 END
                - CASE WHEN 
                    (SELECT clean_query FROM search_context) !~ '\\b(case|cover|charger|adapter|earphone|earbuds|cable|protector|tempered|glass|wallet|power bank|stand|holder|mount|skin|sticker|lens)\\b'
                    AND lower(regexp_replace(p.title, '[^a-zA-Z0-9\s]', ' ', 'g')) ~ '\\b(case|cover|charger|adapter|earphone|earbuds|cable|protector|tempered|glass|wallet|power bank|stand|holder|mount|skin|sticker|lens)\\b'
                  THEN 100 ELSE 0 END
                + (similarity((SELECT raw_query FROM search_context), p.title) * 10)
            ) AS relevance_score
        FROM products p
        WHERE 
            p.search_vector @@ websearch_to_tsquery('english', $1)
            OR p.title ILIKE '%' || $1 || '%'
            OR p.title % $1
    ),
    grouped_products AS (
        SELECT 
            clean_title,
            MAX(relevance_score) as best_score,
            MIN(price) as best_price,
            COUNT(DISTINCT store_name) as store_count,
            (array_agg(id ORDER BY price ASC))[1] as best_id
        FROM scored_products
        GROUP BY clean_title
    )
    SELECT 
        p.id, p.title, gp.best_price as price, p.original_price, p.discount_percent,
        p.image_url, p.store_name, p.product_url, p.category, gp.store_count, gp.best_score
    FROM grouped_products gp
    JOIN products p ON p.id = gp.best_id
    ORDER BY gp.best_score DESC, gp.best_price ASC
    LIMIT 20;
    """
    
    start = time.time()
    rows = await conn.fetch(sql, query)
    elapsed = time.time() - start
    
    print(f"Query took {elapsed:.3f} seconds. Results:")
    for r in rows:
        print(f"[{r['best_score']:.2f}] {r['title'][:50]} ({r['store_name']} - Rs {r['price']})")
        
    await conn.close()

asyncio.run(main())
