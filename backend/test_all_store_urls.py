import asyncio
import asyncpg
import os
import requests
from dotenv import load_dotenv

load_dotenv()

async def test_store_urls():
    conn = await asyncpg.connect(os.getenv('DATABASE_URL'), statement_cache_size=0)
    
    # Get one product URL from each store
    stores = await conn.fetch("""
        SELECT DISTINCT store_name 
        FROM home_screen_products
    """)
    
    print("Testing one URL from each store:\n")
    
    for store_row in stores:
        store_name = store_row['store_name']
        
        # Get one product from this store
        product = await conn.fetchrow("""
            SELECT title, product_url 
            FROM home_screen_products 
            WHERE store_name = $1 
            LIMIT 1
        """, store_name)
        
        if not product:
            continue
            
        url = product['product_url']
        title = product['title'][:50]
        
        print(f"\n{'='*70}")
        print(f"Store: {store_name}")
        print(f"Product: {title}")
        print(f"URL: {url}")
        
        try:
            # Oliz blocks HEAD requests with 403, but GET works fine
            if store_name == 'Oliz':
                response = requests.get(
                    url, 
                    headers={"User-Agent": "Mozilla/5.0"}, 
                    allow_redirects=True, 
                    timeout=10
                )
            else:
                response = requests.head(
                    url, 
                    headers={"User-Agent": "Mozilla/5.0"}, 
                    allow_redirects=True, 
                    timeout=10
                )
            status = response.status_code
            
            if status == 200:
                print(f"✓ Status: {status} - WORKING")
            elif status == 404:
                print(f"✗ Status: {status} - NOT FOUND (404)")
            else:
                print(f"⚠ Status: {status}")
                
        except requests.exceptions.Timeout:
            print(f"✗ TIMEOUT")
        except requests.exceptions.RequestException as e:
            print(f"✗ ERROR: {str(e)[:100]}")
    
    await conn.close()

asyncio.run(test_store_urls())
