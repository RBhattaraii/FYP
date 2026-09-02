import asyncio
import os
import sys
from dotenv import load_dotenv

# Add the parent directory to the path so we can import from app
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import asyncpg

async def apply_products_schema():
    load_dotenv()
    database_url = os.getenv("DATABASE_URL")
    
    if not database_url:
        print("DATABASE_URL not found in .env")
        return
        
    print(f"Connecting to database...")
    
    try:
        conn = await asyncpg.connect(database_url)
        print("Connected successfully!")
        
        # SQL to create the products table
        sql = """
        CREATE TABLE IF NOT EXISTS products (
            id                SERIAL PRIMARY KEY,
            title             TEXT NOT NULL,
            price             DECIMAL(10, 2) NOT NULL,
            original_price    DECIMAL(10, 2),
            discount_percent  INTEGER,
            image_url         TEXT,
            store_name        TEXT NOT NULL,
            product_url       TEXT NOT NULL,
            category          TEXT,
            mongo_id          TEXT,
            scraped_at        TIMESTAMPTZ NOT NULL DEFAULT NOW(),
            
            -- Search vector for full-text search
            search_vector     tsvector GENERATED ALWAYS AS (
                setweight(to_tsvector('english', coalesce(title, '')), 'A') ||
                setweight(to_tsvector('english', coalesce(store_name, '')), 'B') ||
                setweight(to_tsvector('english', coalesce(category, '')), 'C')
            ) STORED
        );
        """
        
        print("Creating products table if it doesn't exist...")
        await conn.execute(sql)
        
        # Create indexes
        print("Creating indexes...")
        
        # For unique index, we need to handle potential conflicts or just use IF NOT EXISTS equivalents 
        # (Postgres doesn't support IF NOT EXISTS directly on indexes before pg 9.5, but we are likely on a newer version).
        
        index_sqls = [
            "CREATE INDEX IF NOT EXISTS idx_products_search ON products USING GIN(search_vector);",
            "CREATE INDEX IF NOT EXISTS idx_products_store ON products(store_name);",
            "CREATE INDEX IF NOT EXISTS idx_products_scraped ON products(scraped_at);",
            "CREATE UNIQUE INDEX IF NOT EXISTS idx_products_url ON products(product_url);"
        ]
        
        for idx_sql in index_sqls:
            try:
                await conn.execute(idx_sql)
            except Exception as e:
                print(f"Notice (index might already exist): {e}")
                
        print("Products table schema applied successfully!")
        await conn.close()
        
    except Exception as e:
        print(f"Failed to apply schema: {e}")

if __name__ == "__main__":
    asyncio.run(apply_products_schema())
