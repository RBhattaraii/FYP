"""
Re-scrape Jeevee products to get correct URLs with template_id format.
Since the database doesn't have template_id, we need to fetch fresh from Jeevee API.
"""
import asyncio
import asyncpg
import os
from dotenv import load_dotenv
import sys

# Add parent directory to path to import scrapers
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from scrapers.jeevee.jeevee_scraper import async_scrape_jeevee

load_dotenv()

async def rescrape_and_update():
    conn = await asyncpg.connect(os.getenv('DATABASE_URL'), statement_cache_size=0)
    
    # Delete existing Jeevee products
    deleted = await conn.execute("DELETE FROM home_screen_products WHERE store_name = 'Jeevee'")
    print(f"Deleted existing Jeevee products: {deleted}")
    
    # Re-scrape with common search terms
    search_terms = ["laptop", "phone", "earbuds", "speaker", "refrigerator", "tv"]
    
    all_products = []
    for term in search_terms:
        print(f"\nScraping Jeevee for: {term}")
        products = await async_scrape_jeevee(term)
        print(f"  Found {len(products)} products")
        all_products.extend(products)
    
    # Remove duplicates based on product_url
    unique_products = {}
    for p in all_products:
        url = p['product_url']
        if url not in unique_products:
            unique_products[url] = p
    
    print(f"\nTotal unique Jeevee products: {len(unique_products)}")
    
    # Insert into database using raw SQL
    for product in unique_products.values():
        await conn.execute("""
            INSERT INTO home_screen_products 
            (section, title, price, original_price, discount_percent,
             image_url, store_name, product_url, category)
            VALUES ($1, $2, $3, $4, $5, $6, $7, $8, $9)
        """, 
        "home",  # section
        product['product_name'],
        product['price'],
        product.get('original_price'),
        product.get('discount_percentage'),
        product.get('image_url'),
        'Jeevee',  # store_name
        product['product_url'],
        None  # category
        )
    
    print("✓ Inserted updated Jeevee products into database")
    await conn.close()

if __name__ == "__main__":
    asyncio.run(rescrape_and_update())
