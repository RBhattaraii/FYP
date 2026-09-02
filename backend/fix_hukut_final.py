import asyncio, asyncpg, os
from dotenv import load_dotenv

import sys
sys.path.append(os.path.dirname(os.path.abspath(__file__)))
from ingest_csvs import ingest

async def run():
    load_dotenv()
    url = os.getenv('DATABASE_URL')
    conn = await asyncpg.connect(url, statement_cache_size=0)
    
    # Run ingestion first, which will UPSERT with correct URLs
    print("Running ingest_csvs...")
    await ingest()
    
    # Delete the old /product/ ones from home screen
    res2 = await conn.execute('''
        DELETE FROM home_screen_products 
        WHERE store_name = 'Hukut' AND product_url LIKE 'https://hukut.com/product/%'
    ''')
    print(f'Home screen products deleted old: {res2}')
    
    # Delete old ones from products table
    res1 = await conn.execute('''
        DELETE FROM products 
        WHERE store_name = 'Hukut' AND product_url LIKE 'https://hukut.com/product/%'
    ''')
    print(f'Products table deleted old: {res1}')
    
    # Finally, run update_home_screen_products to replenish
    from populate_real_data import update_home_screen_products
    # Wait we just deleted some, so we can refill the home screen completely just to be safe
    # Wait, my previous script refresh_home_script.py was better for home screen. I'll just run it.
    
    await conn.close()

asyncio.run(run())
