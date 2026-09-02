"""
Database Migration Script
Applies the new tables (home_screen_products, search_cache, scrape_metadata) to PostgreSQL
"""

import asyncio
import asyncpg
from dotenv import load_dotenv
import os

# Load environment variables
load_dotenv()

async def apply_migration():
    """Apply database schema migration"""
    
    database_url = os.getenv("DATABASE_URL")
    
    if not database_url:
        print("❌ ERROR: DATABASE_URL not found in .env file")
        return
    
    print("🔄 Connecting to PostgreSQL database...")
    
    try:
        # Create connection (disable prepared statements for pgbouncer compatibility)
        conn = await asyncpg.connect(database_url, statement_cache_size=0)
        print("✅ Connected to database successfully")
        
        # Read the schema SQL file
        print("\n🔄 Reading database_schema.sql file...")
        with open("database_schema.sql", "r", encoding="utf-8") as f:
            sql_content = f.read()
        
        # Extract only the new tables SQL (skip users table creation)
        print("\n🔄 Applying new table schemas...")
        
        # Create home_screen_products table
        await conn.execute("""
            CREATE TABLE IF NOT EXISTS home_screen_products (
                id                SERIAL PRIMARY KEY,
                section           TEXT NOT NULL,
                title             TEXT NOT NULL,
                price             DECIMAL(10, 2) NOT NULL,
                original_price    DECIMAL(10, 2),
                discount_percent  INTEGER,
                image_url         TEXT NOT NULL,
                store_name        TEXT NOT NULL,
                product_url       TEXT NOT NULL,
                category          TEXT,
                scraped_at        TIMESTAMPTZ NOT NULL DEFAULT NOW()
            )
        """)
        print("✅ Created table: home_screen_products")
        
        # Create indexes for home_screen_products
        await conn.execute("""
            CREATE INDEX IF NOT EXISTS idx_home_products_section 
            ON home_screen_products(section)
        """)
        await conn.execute("""
            CREATE INDEX IF NOT EXISTS idx_home_products_scraped 
            ON home_screen_products(scraped_at)
        """)
        print("✅ Created indexes for home_screen_products")
        
        # Create search_cache table
        await conn.execute("""
            CREATE TABLE IF NOT EXISTS search_cache (
                id                SERIAL PRIMARY KEY,
                query             TEXT NOT NULL,
                tier1_results     JSONB,
                tier2_results     JSONB,
                tier1_cached_at   TIMESTAMPTZ,
                tier2_cached_at   TIMESTAMPTZ,
                is_complete       BOOLEAN DEFAULT FALSE,
                request_id        TEXT UNIQUE,
                UNIQUE(query)
            )
        """)
        print("✅ Created table: search_cache")
        
        # Create indexes for search_cache
        await conn.execute("""
            CREATE INDEX IF NOT EXISTS idx_search_cache_query 
            ON search_cache(query)
        """)
        await conn.execute("""
            CREATE INDEX IF NOT EXISTS idx_search_cache_request 
            ON search_cache(request_id)
        """)
        await conn.execute("""
            CREATE INDEX IF NOT EXISTS idx_search_cache_cached 
            ON search_cache(tier1_cached_at)
        """)
        print("✅ Created indexes for search_cache")
        
        # Create scrape_metadata table
        await conn.execute("""
            CREATE TABLE IF NOT EXISTS scrape_metadata (
                id                SERIAL PRIMARY KEY,
                scrape_type       TEXT NOT NULL,
                last_scrape_time  TIMESTAMPTZ,
                next_scrape_time  TIMESTAMPTZ,
                status            TEXT,
                products_found    INTEGER,
                error_message     TEXT,
                created_at        TIMESTAMPTZ NOT NULL DEFAULT NOW()
            )
        """)
        print("✅ Created table: scrape_metadata")
        
        # Create indexes for scrape_metadata
        await conn.execute("""
            CREATE INDEX IF NOT EXISTS idx_scrape_metadata_type 
            ON scrape_metadata(scrape_type)
        """)
        await conn.execute("""
            CREATE INDEX IF NOT EXISTS idx_scrape_metadata_last 
            ON scrape_metadata(last_scrape_time)
        """)
        print("✅ Created indexes for scrape_metadata")
        
        # Verify tables were created
        print("\n🔄 Verifying tables exist...")
        tables = await conn.fetch("""
            SELECT table_name 
            FROM information_schema.tables 
            WHERE table_schema = 'public' 
            AND table_name IN ('home_screen_products', 'search_cache', 'scrape_metadata')
            ORDER BY table_name
        """)
        
        print("\n📊 Tables in database:")
        for table in tables:
            print(f"  ✅ {table['table_name']}")
        
        if len(tables) == 3:
            print("\n🎉 Migration completed successfully!")
            print("✅ All 3 new tables created with indexes")
        else:
            print(f"\n⚠️  Warning: Expected 3 tables, but found {len(tables)}")
        
        # Close connection
        await conn.close()
        print("\n✅ Database connection closed")
        
    except Exception as e:
        print(f"\n❌ ERROR during migration: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    print("=" * 60)
    print("PostgreSQL Database Migration")
    print("Adding tables: home_screen_products, search_cache, scrape_metadata")
    print("=" * 60)
    
    asyncio.run(apply_migration())
