import asyncio, asyncpg, os
from dotenv import load_dotenv

async def run():
    load_dotenv()
    url = os.getenv('DATABASE_URL')
    conn = await asyncpg.connect(url, statement_cache_size=0)
    
    res1 = await conn.execute('''
        UPDATE products 
        SET product_url = REPLACE(product_url, 'https://hukut.com/product/', 'https://hukut.com/') 
        WHERE store_name = 'Hukut' AND product_url LIKE 'https://hukut.com/product/%'
    ''')
    print(f'Products table updated: {res1}')
    
    res2 = await conn.execute('''
        UPDATE home_screen_products 
        SET product_url = REPLACE(product_url, 'https://hukut.com/product/', 'https://hukut.com/') 
        WHERE store_name = 'Hukut' AND product_url LIKE 'https://hukut.com/product/%'
    ''')
    print(f'Home screen products table updated: {res2}')
    
    await conn.close()

asyncio.run(run())
