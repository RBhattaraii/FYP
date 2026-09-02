"""
Inspect what's in the search cache after the live search
"""
import asyncio
import asyncpg
import os
import json
from dotenv import load_dotenv

load_dotenv()

async def main():
    conn = await asyncpg.connect(os.getenv('DATABASE_URL'), statement_cache_size=0)
    
    # Check if laptop search exists
    cache_entry = await conn.fetchrow("""
        SELECT search_term, cached_results, scraped_at 
        FROM search_cache 
        WHERE search_term = 'laptop'
    """)
    
    if cache_entry:
        print("✅ Found 'laptop' search in cache")
        print(f"Scraped at: {cache_entry['scraped_at']}")
        
        # Parse the cached results
        results = json.loads(cache_entry['cached_results'])
        products = results.get('products', [])
        
        print(f"\nTotal products: {len(products)}")
        
        # Count by platform
        platforms = {}
        for p in products:
            platform = p.get('platform', 'unknown')
            platforms[platform] = platforms.get(platform, 0) + 1
        
        print("\nProducts by platform:")
        for platform, count in sorted(platforms.items()):
            print(f"  {platform}: {count}")
        
        # Check Jeevee URLs
        jeevee = [p for p in products if p.get('platform') == 'jeevee']
        if jeevee:
            print(f"\n{'='*80}")
            print("Sample Jeevee URLs:")
            print('='*80)
            for p in jeevee[:3]:
                print(f"\nName: {p['product_name'][:60]}")
                print(f"URL: {p['product_url']}")
        else:
            print("\n⚠️ NO JEEVEE PRODUCTS IN CACHE")
    else:
        print("❌ No 'laptop' search found in cache")
        print("\nChecking all cache entries...")
        all_entries = await conn.fetch("SELECT search_term FROM search_cache")
        if all_entries:
            print(f"Found {len(all_entries)} cache entries:")
            for entry in all_entries:
                print(f"  - {entry['search_term']}")
        else:
            print("Cache is empty")
    
    await conn.close()

if __name__ == "__main__":
    asyncio.run(main())
