"""
Database Schema Verification Script
Verifies that all tables and indexes exist with correct structure
"""

import asyncio
import asyncpg
from dotenv import load_dotenv
import os

# Load environment variables
load_dotenv()

async def verify_schema():
    """Verify database schema"""
    
    database_url = os.getenv("DATABASE_URL")
    
    if not database_url:
        print("❌ ERROR: DATABASE_URL not found in .env file")
        return
    
    print("🔄 Connecting to PostgreSQL database...")
    
    try:
        # Create connection (disable prepared statements for pgbouncer compatibility)
        conn = await asyncpg.connect(database_url, statement_cache_size=0)
        print("✅ Connected to database successfully\n")
        
        # Check home_screen_products table
        print("=" * 60)
        print("TABLE: home_screen_products")
        print("=" * 60)
        
        columns = await conn.fetch("""
            SELECT column_name, data_type, is_nullable, column_default
            FROM information_schema.columns
            WHERE table_name = 'home_screen_products'
            ORDER BY ordinal_position
        """)
        
        print("\nColumns:")
        for col in columns:
            nullable = "NULL" if col['is_nullable'] == 'YES' else "NOT NULL"
            default = f" DEFAULT {col['column_default']}" if col['column_default'] else ""
            print(f"  • {col['column_name']}: {col['data_type']} {nullable}{default}")
        
        indexes = await conn.fetch("""
            SELECT indexname, indexdef
            FROM pg_indexes
            WHERE tablename = 'home_screen_products'
        """)
        
        print("\nIndexes:")
        for idx in indexes:
            print(f"  • {idx['indexname']}")
        
        # Check search_cache table
        print("\n" + "=" * 60)
        print("TABLE: search_cache")
        print("=" * 60)
        
        columns = await conn.fetch("""
            SELECT column_name, data_type, is_nullable, column_default
            FROM information_schema.columns
            WHERE table_name = 'search_cache'
            ORDER BY ordinal_position
        """)
        
        print("\nColumns:")
        for col in columns:
            nullable = "NULL" if col['is_nullable'] == 'YES' else "NOT NULL"
            default = f" DEFAULT {col['column_default']}" if col['column_default'] else ""
            print(f"  • {col['column_name']}: {col['data_type']} {nullable}{default}")
        
        indexes = await conn.fetch("""
            SELECT indexname, indexdef
            FROM pg_indexes
            WHERE tablename = 'search_cache'
        """)
        
        print("\nIndexes:")
        for idx in indexes:
            print(f"  • {idx['indexname']}")
        
        # Check scrape_metadata table
        print("\n" + "=" * 60)
        print("TABLE: scrape_metadata")
        print("=" * 60)
        
        columns = await conn.fetch("""
            SELECT column_name, data_type, is_nullable, column_default
            FROM information_schema.columns
            WHERE table_name = 'scrape_metadata'
            ORDER BY ordinal_position
        """)
        
        print("\nColumns:")
        for col in columns:
            nullable = "NULL" if col['is_nullable'] == 'YES' else "NOT NULL"
            default = f" DEFAULT {col['column_default']}" if col['column_default'] else ""
            print(f"  • {col['column_name']}: {col['data_type']} {nullable}{default}")
        
        indexes = await conn.fetch("""
            SELECT indexname, indexdef
            FROM pg_indexes
            WHERE tablename = 'scrape_metadata'
        """)
        
        print("\nIndexes:")
        for idx in indexes:
            print(f"  • {idx['indexname']}")
        
        # Summary
        print("\n" + "=" * 60)
        print("VERIFICATION SUMMARY")
        print("=" * 60)
        
        all_tables = await conn.fetch("""
            SELECT table_name
            FROM information_schema.tables
            WHERE table_schema = 'public'
            ORDER BY table_name
        """)
        
        print(f"\n✅ Total tables in database: {len(all_tables)}")
        for table in all_tables:
            print(f"  • {table['table_name']}")
        
        # Count indexes for new tables
        all_indexes = await conn.fetch("""
            SELECT tablename, COUNT(*) as index_count
            FROM pg_indexes
            WHERE tablename IN ('home_screen_products', 'search_cache', 'scrape_metadata')
            GROUP BY tablename
        """)
        
        print(f"\n✅ Indexes on new tables:")
        for idx in all_indexes:
            print(f"  • {idx['tablename']}: {idx['index_count']} indexes")
        
        print("\n🎉 Schema verification completed successfully!")
        
        # Close connection
        await conn.close()
        
    except Exception as e:
        print(f"\n❌ ERROR during verification: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    asyncio.run(verify_schema())
