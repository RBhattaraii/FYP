"""
Populate database with dummy product data for testing
Run this if the scraper isn't working yet
"""
import asyncio
import asyncpg
from dotenv import load_dotenv
import os
from datetime import datetime, timezone

load_dotenv()

async def populate_dummy_data():
    """Insert dummy products into the database for testing"""
    
    database_url = os.getenv("DATABASE_URL")
    if not database_url:
        print("❌ DATABASE_URL not found in .env")
        return
    
    try:
        # Connect to database
        conn = await asyncpg.connect(database_url, statement_cache_size=0)
        print("✓ Connected to database")
        
        # Clear existing products
        await conn.execute("DELETE FROM home_screen_products")
        print("✓ Cleared existing products")
        
        # Dummy product data
        products = []
        
        # Best deals (25 products)
        for i in range(1, 26):
            products.append((
                f"Product {i} - Best Deal",
                f"https://picsum.photos/200/200?random={i}",
                15000 + (i * 100),
                25000 + (i * 100),
                30 + i,
                f"https://example.com/product-{i}",
                ["Daraz", "Oliz", "CGDigital"][i % 3],
                ["Electronics", "Computers", "Phones"][i % 3],
                'best_deals'
            ))
        
        # Top price drops (25 products)
        for i in range(26, 51):
            products.append((
                f"Product {i} - Price Drop",
                f"https://picsum.photos/200/200?random={i}",
                20000 + (i * 100),
                30000 + (i * 100),
                25 + (i % 20),
                f"https://example.com/product-{i}",
                ["Better", "Hukut", "Jeevee"][i % 3],
                ["Electronics", "Accessories", "Gadgets"][i % 3],
                'top_price_drops'
            ))
        
        # Insert products
        await conn.executemany("""
            INSERT INTO home_screen_products 
            (title, image_url, price, original_price, discount_percent, product_url, store_name, category, section)
            VALUES ($1, $2, $3, $4, $5, $6, $7, $8, $9)
        """, products)
        
        print(f"✓ Inserted {len(products)} dummy products")
        
        # Update scrape_metadata
        # First delete old entry, then insert new one
        await conn.execute("DELETE FROM scrape_metadata WHERE scrape_type = $1", 'daily_homepage')
        
        await conn.execute("""
            INSERT INTO scrape_metadata 
            (scrape_type, last_scrape_time, next_scrape_time, status, products_found)
            VALUES ($1, $2, $3, $4, $5)
        """, 
        'daily_homepage',
        datetime.now(timezone.utc),
        datetime.now(timezone.utc),
        'completed',
        50
        )
        
        print("✓ Updated scrape_metadata")
        
        # Verify
        count = await conn.fetchval("SELECT COUNT(*) FROM home_screen_products")
        print(f"✓ Total products in database: {count}")
        
        best_deals_count = await conn.fetchval(
            "SELECT COUNT(*) FROM home_screen_products WHERE section = 'best_deals'"
        )
        top_drops_count = await conn.fetchval(
            "SELECT COUNT(*) FROM home_screen_products WHERE section = 'top_price_drops'"
        )
        
        print(f"  - Best deals: {best_deals_count}")
        print(f"  - Top price drops: {top_drops_count}")
        
        await conn.close()
        print("\n✅ Database populated with dummy data!")
        print("📱 Refresh your mobile app to see the products")
        
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    asyncio.run(populate_dummy_data())
