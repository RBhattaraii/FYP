import asyncpg, asyncio, os, json
from dotenv import load_dotenv
load_dotenv()

from app.services.scraper_coordinator import sort_search_results
from app.services.entity_resolution import resolve_entities

async def main():
    url = os.getenv('DATABASE_URL')
    conn = await asyncpg.connect(url, statement_cache_size=0)
    
    # Fetch cached results for 'iphone'
    row = await conn.fetchrow(
        "SELECT tier1_results, tier2_results FROM search_cache WHERE query = 'iphone'"
    )
    if not row:
        print("No cache found for 'iphone'")
        await conn.close()
        return
        
    t1 = json.loads(row['tier1_results']) if row['tier1_results'] else []
    t2 = json.loads(row['tier2_results']) if row['tier2_results'] else []
    all_results = [p for p in t1 + t2 if p.get("product_url")]
    
    print(f"Total raw results: {len(all_results)}")
    
    # Sort
    sorted_results = sort_search_results("iphone", all_results)
    
    # Group
    resolved = resolve_entities(sorted_results)
    
    print("\nTop 15 resolved results:")
    for idx, p in enumerate(resolved[:15]):
        print(f"{idx+1}. {p['store_name']} | Price: {p['price']} | Title: {p['title']}")
        print(f"  Alternative offers count: {len(p['alternative_offers'])}")
        
    await conn.close()

asyncio.run(main())
