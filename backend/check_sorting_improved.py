import asyncpg, asyncio, os, json
from dotenv import load_dotenv
load_dotenv()

from app.services.scraper_coordinator import sort_search_results
from app.services.entity_resolution import resolve_entities

def custom_sort_search_results(query, products):
    import re
    query_lower = query.lower().strip()
    query_tokens = [t for t in re.split(r'[\s\-_]+', query_lower) if len(t) > 1]
    query_token_set = set(query_tokens)

    # Removed specs from accessory keywords
    accessory_keywords = {
        "cover", "case", "protector", "glass", "cable", "charger", "adapter",
        "strap", "band", "mount", "remote", "stand", "skin", "decal", "sticker",
        "hybrid", "magsafe", "magnetic", "silicone", "leather", "wallet",
        "tempered", "lens", "guard", "ring", "holder", "tripod", "pouch", "sleeve",
        "screen", "film", "back", "bumper", "grip", "clip", "dock", "hub",
        "mouse", "bag", "backpack", "cooling", "pad", "cooler"
    }
    query_has_accessory = bool(query_token_set & accessory_keywords)

    valid_products = []
    for p in products:
        title = (p.get("title") or p.get("product_name") or "").lower()
        cat = (p.get("category") or "").lower()
        title_cat = title + " " + cat
        
        # Issue 1 Fix: Filter out completely irrelevant products for specific queries
        if len(query_tokens) > 1:
            matched = sum(1 for tok in query_tokens if tok in title_cat)
            if matched == 0:
                continue # Skip products that don't match ANY tokens (e.g. Daraz Motherboard for 'acer nitro v')
        
        valid_products.append(p)

    def score_product(p):
        title = (p.get("title") or p.get("product_name") or "").lower()
        cat = (p.get("category") or "").lower()
        title_cat = title + " " + cat

        # Issue 2 Fix: Match against title AND category
        matched_tokens = sum(1 for tok in query_tokens if tok in title_cat)
        total_tokens = max(len(query_tokens), 1)
        unmatched_fraction = (total_tokens - matched_tokens) / total_tokens

        exact_phrase = 0 if query_lower in title_cat else 1

        accessory_penalty = 0
        if not query_has_accessory and any(acc in title for acc in accessory_keywords):
            accessory_penalty = 1

        price = p.get("price") or 0

        return (
            round(unmatched_fraction, 2),
            exact_phrase,
            accessory_penalty,
            -price,
        )

    return sorted(valid_products, key=score_product)

async def main():
    url = os.getenv('DATABASE_URL')
    conn = await asyncpg.connect(url, statement_cache_size=0)
    
    # Test for 'laptop'
    row = await conn.fetchrow("SELECT tier1_results, tier2_results FROM search_cache WHERE query = 'laptop'")
    if row:
        t1 = json.loads(row['tier1_results']) if row['tier1_results'] else []
        t2 = json.loads(row['tier2_results']) if row['tier2_results'] else []
        all_results = [p for p in t1 + t2 if p.get("product_url")]
        
        sorted_results = custom_sort_search_results("laptop", all_results)
        print("\n--- Top 15 for 'laptop' ---")
        for idx, p in enumerate(sorted_results[:15]):
            title = p['title'].encode('ascii', 'ignore').decode('ascii')
            print(f"{idx+1}. {p['store_name']} | Price: {p['price']} | Title: {title}")
            
    # Test for 'acer nitro v'
    row = await conn.fetchrow("SELECT tier1_results, tier2_results FROM search_cache WHERE query = 'acer nitro v'")
    if row:
        t1 = json.loads(row['tier1_results']) if row['tier1_results'] else []
        t2 = json.loads(row['tier2_results']) if row['tier2_results'] else []
        all_results = [p for p in t1 + t2 if p.get("product_url")]
        
        sorted_results = custom_sort_search_results("acer nitro v", all_results)
        print("\n--- Top 15 for 'acer nitro v' ---")
        for idx, p in enumerate(sorted_results[:15]):
            title = p['title'].encode('ascii', 'ignore').decode('ascii')
            print(f"{idx+1}. {p['store_name']} | Price: {p['price']} | Title: {title}")

    await conn.close()

asyncio.run(main())
