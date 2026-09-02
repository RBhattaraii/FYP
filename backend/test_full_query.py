import asyncio
import asyncpg
import os
from dotenv import load_dotenv

load_dotenv()

async def test_db_search(q: str):
    url = os.getenv('DATABASE_URL')
    conn = await asyncpg.connect(url, statement_cache_size=0)
    
    query_str = q.strip()
    
    sql_base = """
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
                lower(regexp_replace(p.title, '[^a-zA-Z0-9\s]', ' ', 'g')) AS clean_title,
                (
                    -- 1. Exact match (+100)
                    CASE WHEN lower(regexp_replace(p.title, '[^a-zA-Z0-9\s]', ' ', 'g')) = (SELECT clean_query FROM search_context) THEN 100 ELSE 0 END
                    
                    -- 2. Starts with query (+80)
                    + CASE WHEN lower(regexp_replace(p.title, '[^a-zA-Z0-9\s]', ' ', 'g')) LIKE (SELECT clean_query FROM search_context) || '%' THEN 80 ELSE 0 END
                    
                    -- 3. Contains entire query (+60)
                    + CASE WHEN lower(regexp_replace(p.title, '[^a-zA-Z0-9\s]', ' ', 'g')) LIKE '%' || (SELECT clean_query FROM search_context) || '%' THEN 60 ELSE 0 END
                    
                    -- 4. Contains all keywords / full text search (+40)
                    + CASE WHEN p.search_vector @@ websearch_to_tsquery('english', $1) THEN 40 ELSE 0 END
                    
                    -- 4.5. Offline Platform Boost (+500)
                    + CASE WHEN p.store_name IN ('Oliz', 'CG Digital', 'KoreanBP', 'Hukut') THEN 500 ELSE 0 END
                    
                    -- 5. Brand match (+20) (first token matches first word of title)
                    + CASE WHEN split_part(lower(regexp_replace(p.title, '[^a-zA-Z0-9\s]', ' ', 'g')), ' ', 1) = (SELECT tokens[1] FROM search_context) THEN 20 ELSE 0 END
                    
                    -- 5.5. Complete laptop product boost (+150) when searching for "laptop"
                    + CASE WHEN 
                        (SELECT clean_query FROM search_context) = 'laptop'
                        AND lower(regexp_replace(p.title, '[^a-zA-Z0-9\s]', ' ', 'g')) ~ '\\y(pavilion|inspiron|thinkpad|vivobook|ideapad|aspire|zenbook|elitebook|macbook)\\y'
                        AND lower(regexp_replace(p.title, '[^a-zA-Z0-9\s]', ' ', 'g')) !~ '\\y(battery|backpack|bag|case|cover|charger|adapter|cable|stand|table|desk|speaker|webcam|internal|external|component|part|accessory|fan|cooling|sleeve|screw|repair|tool)\\y'
                      THEN 150 ELSE 0 END
                      
                    -- 5.6. Computer model boost (+100) for actual computer products 
                    + CASE WHEN 
                        lower(regexp_replace(p.title, '[^a-zA-Z0-9\s]', ' ', 'g')) ~ '\\y(hp|dell|lenovo|asus|acer|apple)\\s+(pavilion|inspiron|thinkpad|vivobook|ideapad|aspire|zenbook|elitebook|macbook)'
                        OR lower(regexp_replace(p.title, '[^a-zA-Z0-9\s]', ' ', 'g')) ~ '\\y(intel|amd|ryzen|core)\\s+(i[3-9]|[3-9][0-9]{3}[a-z]?)'
                      THEN 100 ELSE 0 END
                    
                    -- 6. Heavy accessory penalty (-500) if query doesn't contain accessory words, but product does
                    - CASE WHEN 
                        (SELECT clean_query FROM search_context) !~ '\\y(case|cover|charger|adapter|earphone|earbuds|cable|protector|tempered|glass|wallet|power bank|stand|holder|mount|skin|sticker|lens|bag|pouch|sleeve|fan|cooling|table|desk|speaker|webcam|internal|external|component|part|accessory|battery|backpack|screw|repair|tool)\\y'
                        AND lower(regexp_replace(p.title, '[^a-zA-Z0-9\s]', ' ', 'g')) ~ '\\y(case|cover|charger|adapter|earphone|earbuds|cable|protector|tempered|glass|wallet|power bank|stand|holder|mount|skin|sticker|lens|bag|pouch|sleeve|fan|cooling|table|desk|speaker|webcam|internal|external|component|part|accessory|battery|backpack|screw|repair|tool)\\y'
                      THEN 500 ELSE 0 END
                      
                    -- 7. Fuzzy score (+ up to 10)
                    + (similarity((SELECT raw_query FROM search_context), p.title) * 10)
                ) AS relevance_score
            FROM products p
            WHERE 
                p.search_vector @@ websearch_to_tsquery('english', $1)
                OR p.title ILIKE '%' || $1 || '%'
                OR p.title % $1
        ),
        filtered_scored_products AS (
            SELECT *
            FROM scored_products
            WHERE relevance_score > 0  -- Filter out products with negative relevance (accessories)
            AND NOT (
                -- Additional filter: remove obvious components/accessories even if they got positive scores
                lower(regexp_replace(title, '[^a-zA-Z0-9\s]', ' ', 'g')) ~ '\\y(lcd|screen|display|panel|matrix|battery|charger|adapter|cable|fan|cooling|component|part)\\y'
                AND NOT lower(regexp_replace(title, '[^a-zA-Z0-9\s]', ' ', 'g')) ~ '\\y(laptop computer|notebook computer|gaming laptop|business laptop)\\y'
            )
        ),
        grouped_products AS (
            SELECT 
                clean_title,
                MAX(relevance_score) as best_score,
                MIN(price) as best_price,
                COUNT(DISTINCT store_name) as store_count,
                (array_agg(id ORDER BY price ASC))[1] as best_id
            FROM filtered_scored_products
            GROUP BY clean_title
        )
        """
        
    count_sql = sql_base + " SELECT COUNT(*) as total FROM grouped_products"
    count_row = await conn.fetchrow(count_sql, query_str)
    print(f"Total grouped products: {count_row['total']}")

    data_sql = sql_base + """
    SELECT 
        p.id, p.title, gp.best_price as price, p.original_price, p.discount_percent,
        p.image_url, p.store_name, p.product_url, p.category, gp.store_count, gp.best_score
    FROM grouped_products gp
    JOIN products p ON p.id = gp.best_id
    ORDER BY gp.best_score DESC, gp.best_price ASC
    LIMIT 20 OFFSET 0
    """
    
    rows = await conn.fetch(data_sql, query_str)
    for r in rows:
        title = r['title'].encode('ascii', 'ignore').decode('ascii')
        print(f"{r['store_name']} | {r['best_score']:.1f} | {r['price']} | {title[:60]}")
        
    await conn.close()

asyncio.run(test_db_search("iphone"))
