import asyncpg, asyncio, os, json
from dotenv import load_dotenv
load_dotenv()

from app.services.scraper_coordinator import sort_search_results
from app.services.entity_resolution import resolve_entities

async def main():
    url = os.getenv('DATABASE_URL')
    conn = await asyncpg.connect(url, statement_cache_size=0)
    
    # Fetch cached results for 'laptop'
    row = await conn.fetchrow(
        "SELECT tier1_results, tier2_results FROM search_cache WHERE query = 'laptop'"
    )
    if not row:
        print("No cache found for 'laptop'")
        await conn.close()
        return
        
    t1 = json.loads(row['tier1_results']) if row['tier1_results'] else []
    t2 = json.loads(row['tier2_results']) if row['tier2_results'] else []
    all_results = [p for p in t1 + t2 if p.get("product_url")]
    
    # Sort
    sorted_results = sort_search_results("laptop", all_results)
    
    print("\nTop 15 sorted results for 'laptop':")
    for idx, p in enumerate(sorted_results[:15]):
        title = p['title'].encode('ascii', 'ignore').decode('ascii')
        print(f"{idx+1}. {p['store_name']} | Price: {p['price']} | Title: {title}")
        
    await conn.close()

asyncio.run(main())
