import asyncio
import asyncpg
import os
from dotenv import load_dotenv

load_dotenv()

async def check_urls():
    conn = await asyncpg.connect(os.getenv('DATABASE_URL'))
    
    print("\n=== Jeevee Product URLs ===")
    jeevee_rows = await conn.fetch("""
        SELECT title, product_url, store_name 
        FROM home_screen_products 
        WHERE store_name = 'Jeevee' 
        LIMIT 10
    """)
    
    for row in jeevee_rows:
        print(f"\nTitle: {row['title'][:60]}")
        print(f"URL: {row['product_url']}")
    
    print(f"\nTotal Jeevee products: {len(jeevee_rows)}")
    
    print("\n\n=== Other Store URLs (Sample) ===")
    other_rows = await conn.fetch("""
        SELECT title, product_url, store_name 
        FROM home_screen_products 
        WHERE store_name IN ('CGDigital', 'Better', 'Hukut', 'Neostore', 'Hardware Pasal', 'UFO Nepal')
        LIMIT 2
    """)
    
    for row in other_rows:
        print(f"\nStore: {row['store_name']}")
        print(f"Title: {row['title'][:60]}")
        print(f"URL: {row['product_url']}")
    
    await conn.close()

asyncio.run(check_urls())
