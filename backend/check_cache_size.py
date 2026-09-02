import asyncpg, asyncio, os, json
from dotenv import load_dotenv
load_dotenv()

async def main():
    url = os.getenv('DATABASE_URL')
    conn = await asyncpg.connect(url, statement_cache_size=0)
    
    row = await conn.fetchrow(
        "SELECT id, query, is_complete, length(tier1_results::text) as len1, length(tier2_results::text) as len2 FROM search_cache WHERE query = 'laptop'"
    )
    if row:
        print(f"Cache row found:")
        print(f"  Query: {row['query']}")
        print(f"  Is complete: {row['is_complete']}")
        print(f"  Tier 1 size in chars: {row['len1']}")
        print(f"  Tier 2 size in chars: {row['len2']}")
        
        # Load and count actual items
        data = await conn.fetchrow(
            "SELECT tier1_results, tier2_results FROM search_cache WHERE query = 'laptop'"
        )
        t1 = json.loads(data['tier1_results']) if data['tier1_results'] else []
        t2 = json.loads(data['tier2_results']) if data['tier2_results'] else []
        print(f"  Tier 1 count: {len(t1)}")
        print(f"  Tier 2 count: {len(t2)}")
        print(f"  Total count: {len(t1) + len(t2)}")
    else:
        print("No cache found for 'laptop'")
        
    await conn.close()

asyncio.run(main())
