import asyncio
import asyncpg
import os
import sys
from datetime import datetime, timezone
from dotenv import load_dotenv

sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from ingest_csvs import ingest
from app.services.scraper_coordinator import live_search_and_save

async def refresh_home():
    load_dotenv()
    url = os.getenv('DATABASE_URL')
    conn = await asyncpg.connect(url, statement_cache_size=0)
    
    print("1. Ingesting CSVs from Data folder (Oliz, CGDigital, etc)...")
    await ingest()
    
    print("2. Scraping Daraz for fresh deals (this will take a moment)...")
    queries = ["laptop", "smartphone", "earbuds", "smartwatch", "refrigerator", "charger", "power bank"]
    for query in queries:
        await live_search_and_save(query, "Daraz")
        
    print("3. Updating home screen products...")
    # Clear existing
    await conn.execute("DELETE FROM home_screen_products")
    
    # 3.1 Best Deals
    best_deals = await conn.fetch("""
        SELECT * FROM products 
        WHERE discount_percent > 0 
        ORDER BY discount_percent DESC 
        LIMIT 25
    """)
    for p in best_deals:
        await insert_home_product(conn, p, 'best_deals')
        
    # 3.2 Top Price Drops
    price_drops = await conn.fetch("""
        SELECT * FROM products 
        WHERE original_price IS NOT NULL AND original_price > price
        ORDER BY (original_price - price) DESC 
        LIMIT 25
    """)
    for p in price_drops:
        await insert_home_product(conn, p, 'top_price_drops')
        
    # 3.3 Tech Gadgets
    tech_gadgets = await conn.fetch("""
        SELECT * FROM products 
        WHERE title ILIKE '%laptop%' OR title ILIKE '%phone%' OR title ILIKE '%macbook%' OR title ILIKE '%watch%'
        ORDER BY scraped_at DESC 
        LIMIT 25
    """)
    for p in tech_gadgets:
        await insert_home_product(conn, p, 'tech_gadgets')
        
    # 3.4 Audio Essentials
    audio = await conn.fetch("""
        SELECT * FROM products 
        WHERE title ILIKE '%earbuds%' OR title ILIKE '%headphone%' OR title ILIKE '%airpods%' OR title ILIKE '%speaker%'
        ORDER BY scraped_at DESC 
        LIMIT 25
    """)
    for p in audio:
        await insert_home_product(conn, p, 'audio_essentials')
        
    # 3.5 Home Appliances
    appliances = await conn.fetch("""
        SELECT * FROM products 
        WHERE title ILIKE '%refrigerator%' OR title ILIKE '%washing machine%' OR title ILIKE '%tv %' OR title ILIKE '%oven%'
        ORDER BY scraped_at DESC 
        LIMIT 25
    """)
    for p in appliances:
        await insert_home_product(conn, p, 'home_appliances')

    print("Done populating all sections!")
    await conn.close()

async def insert_home_product(conn, product, section):
    try:
        await conn.execute("""
            INSERT INTO home_screen_products (
                title, price, original_price, discount_percent,
                image_url, store_name, product_url, category, section, scraped_at
            ) VALUES ($1, $2, $3, $4, $5, $6, $7, $8, $9, $10)
        """, 
            product['title'][:255], product['price'], product['original_price'],
            product['discount_percent'], product['image_url'], product['store_name'],
            product['product_url'][:1000], product['category'], section,
            datetime.now(timezone.utc)
        )
    except Exception as e:
        print(f"Error inserting {product['title']}: {e}")

if __name__ == "__main__":
    asyncio.run(refresh_home())
