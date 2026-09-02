import asyncio
import os
import sys
sys.path.insert(0, os.path.dirname(__file__))
from dotenv import load_dotenv
load_dotenv(os.path.join(os.path.dirname(__file__), 'backend', '.env'))
import asyncpg

async def main():
    db_url = os.getenv("DATABASE_URL")
    conn = await asyncpg.connect(db_url, statement_cache_size=0)
    
    products = await conn.fetch("SELECT id, store_name, product_url FROM home_screen_products")
    
    print(f"Total products: {len(products)}")
    stores = {}
    for p in products:
        store = p['store_name']
        if store not in stores:
            stores[store] = []
        stores[store].append(p['product_url'])
        
    for store, urls in stores.items():
        print(f"\n{store}: {len(urls)} products")
        for url in urls[:3]:
            print(f"  {url}")
            
    await conn.close()

asyncio.run(main())
