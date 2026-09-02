"""
Check actual Jeevee products in the products database table
"""
import asyncio
import asyncpg
import os
import requests
from dotenv import load_dotenv

load_dotenv()

async def main():
    conn = await asyncpg.connect(os.getenv('DATABASE_URL'), statement_cache_size=0)
    
    # Get Jeevee products from the products table
    jeevee_products = await conn.fetch("""
        SELECT title, product_url, store_name, price
        FROM products
        WHERE store_name ILIKE '%jeevee%'
        ORDER BY scraped_at DESC
        LIMIT 5
    """)
    
    if jeevee_products:
        print(f"✅ Found {len(jeevee_products)} Jeevee products in database")
        print("\n" + "="*80)
        print("Testing Jeevee URLs from DATABASE:")
        print("="*80)
        
        for i, product in enumerate(jeevee_products, 1):
            url = product['product_url']
            name = product['title'][:60]
            
            # Test the URL
            try:
                response = requests.head(url, timeout=5, allow_redirects=True)
                status = response.status_code
                
                if status == 200:
                    result = "✅ WORKING"
                elif status == 404:
                    result = "❌ 404 NOT FOUND"
                elif status in [301, 302, 303]:
                    result = f"✅ REDIRECT ({status})"
                else:
                    result = f"⚠️ Status {status}"
                    
                print(f"\n{i}. {result}")
                print(f"   Name: {name}")
                print(f"   URL: {url}")
                if status in [301, 302, 303]:
                    print(f"   Final: {response.url}")
                    
            except Exception as e:
                print(f"\n{i}. ❌ ERROR")
                print(f"   Name: {name}")
                print(f"   URL: {url}")
                print(f"   Error: {str(e)[:50]}")
        
        print("\n" + "="*80)
        
    else:
        print("❌ No Jeevee products found in database")
        print("\nChecking all products...")
        total = await conn.fetchval("SELECT COUNT(*) FROM products")
        print(f"Total products in database: {total}")
        
        if total > 0:
            # Get sample of store names
            stores = await conn.fetch("""
                SELECT DISTINCT store_name, COUNT(*) as count
                FROM products
                GROUP BY store_name
                ORDER BY count DESC
            """)
            print("\nProducts by store:")
            for store in stores:
                print(f"  {store['store_name']}: {store['count']}")
    
    await conn.close()

if __name__ == "__main__":
    asyncio.run(main())
