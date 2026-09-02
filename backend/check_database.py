"""
Database Diagnostic Script
Checks if tables exist and have data
"""
import asyncio
import asyncpg
from dotenv import load_dotenv
import os

# Load environment variables
load_dotenv()

async def check_database():
    """Check database connection and data"""
    
    print("🔍 Checking Database Connection...")
    print("=" * 60)
    print()
    
    # Get DATABASE_URL
    db_url = os.getenv("DATABASE_URL")
    if not db_url:
        print("❌ DATABASE_URL not found in .env file!")
        return
    
    print(f"✓ DATABASE_URL found: {db_url[:50]}...")
    print()
    
    try:
        # Connect to database
        conn = await asyncpg.connect(db_url)
        print("✓ Connected to database successfully!")
        print()
        
        # Check users table
        print("📊 Checking 'users' table...")
        users_count = await conn.fetchval("SELECT COUNT(*) FROM users")
        print(f"   Users: {users_count}")
        print()
        
        # Check home_screen_products table
        print("📊 Checking 'home_screen_products' table...")
        try:
            total_products = await conn.fetchval("SELECT COUNT(*) FROM home_screen_products")
            best_deals = await conn.fetchval("SELECT COUNT(*) FROM home_screen_products WHERE section = 'best_deals'")
            top_price_drops = await conn.fetchval("SELECT COUNT(*) FROM home_screen_products WHERE section = 'top_price_drops'")
            
            print(f"   Total products: {total_products}")
            print(f"   Best deals: {best_deals}")
            print(f"   Top price drops: {top_price_drops}")
            print()
            
            if total_products == 0:
                print("⚠️  Warning: No products in database!")
                print("   Run: .\\trigger_scraper.ps1")
                print()
            else:
                # Show sample products
                print("📦 Sample Products:")
                products = await conn.fetch("""
                    SELECT title, price, store_name, section
                    FROM home_screen_products
                    LIMIT 5
                """)
                for i, p in enumerate(products, 1):
                    print(f"   {i}. {p['title'][:50]} - Rs.{p['price']} ({p['store_name']})")
                print()
                
        except Exception as e:
            print(f"   ❌ Error: {e}")
            print("   Table might not exist. Run database_schema.sql in Supabase!")
            print()
        
        # Check search_cache table
        print("📊 Checking 'search_cache' table...")
        try:
            cache_count = await conn.fetchval("SELECT COUNT(*) FROM search_cache")
            print(f"   Cached searches: {cache_count}")
            print()
        except Exception as e:
            print(f"   ❌ Error: {e}")
            print("   Table might not exist. Run database_schema.sql in Supabase!")
            print()
        
        # Check scrape_metadata table
        print("📊 Checking 'scrape_metadata' table...")
        try:
            metadata_count = await conn.fetchval("SELECT COUNT(*) FROM scrape_metadata")
            print(f"   Scrape records: {metadata_count}")
            
            if metadata_count > 0:
                last_scrape = await conn.fetchrow("""
                    SELECT scrape_type, last_scrape_time, status, products_found
                    FROM scrape_metadata
                    ORDER BY last_scrape_time DESC
                    LIMIT 1
                """)
                print(f"   Last scrape: {last_scrape['scrape_type']} at {last_scrape['last_scrape_time']}")
                print(f"   Status: {last_scrape['status']}")
                print(f"   Products found: {last_scrape['products_found']}")
            print()
        except Exception as e:
            print(f"   ❌ Error: {e}")
            print("   Table might not exist. Run database_schema.sql in Supabase!")
            print()
        
        await conn.close()
        
        print("=" * 60)
        print("✅ Database check complete!")
        print()
        
    except Exception as e:
        print(f"❌ Database connection failed: {e}")
        print()
        print("Troubleshooting:")
        print("1. Check if DATABASE_URL is correct in .env")
        print("2. Verify Supabase project is active")
        print("3. Check if database_schema.sql was run in Supabase SQL Editor")
        print()

if __name__ == "__main__":
    asyncio.run(check_database())
