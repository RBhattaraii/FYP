"""
Script to refresh Jeevee products in the database.
1. Deletes old Jeevee products
2. Scrapes fresh Jeevee products
"""
import asyncio
import asyncpg
import os
import sys
from dotenv import load_dotenv

# Add parent directory to path for imports
sys.path.append(os.path.dirname(os.path.dirname(__file__)))

from scrapers.jeevee.jeevee_scraper import async_scrape_jeevee

load_dotenv()

async def refresh_jeevee():
    conn = await asyncpg.connect(os.getenv('DATABASE_URL'), statement_cache_size=0)
    
    # Step 1: Delete old Jeevee products
    print("\n🗑️  Deleting old Jeevee products...")
    deleted = await conn.execute("DELETE FROM home_screen_products WHERE store_name = 'Jeevee'")
    print(f"   Deleted: {deleted.split()[-1]} products")
    
    # Step 2: Scrape fresh Jeevee products for popular search terms
    search_terms = [
        "laptop",
        "phone",
        "headphone",
        "charger",
        "watch",
        "tablet",
        "speaker",
        "earbuds",
        "powerbank",
        "camera"
    ]
    
    print(f"\n🔍 Scraping Jeevee for {len(search_terms)} search terms...")
    
    all_products = []
    for term in search_terms:
        print(f"\n   Searching: {term}")
        products = await async_scrape_jeevee(term)
        print(f"   Found: {len(products)} products")
        all_products.extend(products)
    
    # Remove duplicates (same URL)
    seen_urls = set()
    unique_products = []
    for product in all_products:
        if product['product_url'] not in seen_urls:
            seen_urls.add(product['product_url'])
            unique_products.append(product)
    
    print(f"\n📦 Total unique products: {len(unique_products)}")
    
    # Step 3: Insert into database using batch insert for better performance
    print("\n💾 Inserting into database...")
    
    # Filter out products with missing required fields
    valid_products = []
    skipped = 0
    for product in unique_products:
        if not product.get('image_url'):
            skipped += 1
            continue
        valid_products.append(product)
    
    if skipped > 0:
        print(f"   Filtered out {skipped} products with missing image_url")
    
    # Batch insert all products at once
    if valid_products:
        await conn.executemany("""
            INSERT INTO home_screen_products (
                section, title, price, original_price, discount_percent,
                image_url, product_url, store_name, category, scraped_at
            )
            VALUES ($1, $2, $3, $4, $5, $6, $7, $8, $9, NOW())
        """, [
            (
                'home',  # Default section for scraped products
                p['product_name'],
                p['price'],
                p.get('original_price'),
                p.get('discount_percentage'),
                p['image_url'],
                p['product_url'],
                'Jeevee',
                p.get('category', 'Electronics')
            ) for p in valid_products
        ])
    
    inserted = len(valid_products)
    
    print(f"\n✅ Successfully inserted {inserted} Jeevee products!")
    
    # Show sample of new products
    print("\n📋 Sample of new products:")
    samples = await conn.fetch("""
        SELECT title, price, product_url 
        FROM home_screen_products 
        WHERE store_name = 'Jeevee' 
        LIMIT 5
    """)
    
    for sample in samples:
        print(f"   - {sample['title'][:60]}")
        print(f"     Price: Rs {sample['price']:,.0f}")
        print(f"     URL: {sample['product_url']}")
        print()
    
    await conn.close()

if __name__ == "__main__":
    print("=" * 70)
    print("JEEVEE PRODUCT REFRESH SCRIPT")
    print("=" * 70)
    asyncio.run(refresh_jeevee())
    print("\n" + "=" * 70)
    print("✨ Refresh complete!")
    print("=" * 70)
