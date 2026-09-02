import asyncio
import sys
import os
sys.path.insert(0, os.path.dirname(__file__))

from scrapers.daraz.daraz_scraper import async_scrape_daraz
from scrapers.oliz.oliz_scraper import async_scrape_oliz
from scrapers.hukut.hukut_scraper import async_scrape_hukut
from scrapers.neostore.neostore_scraper import async_scrape_neostore
from scrapers.cgdigital.cgdigital_scraper import async_scrape_cgdigital
from scrapers.better.better_scraper import async_scrape_better
from scrapers.hardwarepasal.hardwarepasal_scraper import async_scrape_hardwarepasal
from scrapers.ufonepal.ufonepal_scraper import async_scrape_ufonepal
from scrapers.jeevee.jeevee_scraper import async_scrape_jeevee

async def test_all():
    query = "iphone"
    scrapers = {
        "Daraz": lambda: async_scrape_daraz(query, 2),
        "Oliz": lambda: async_scrape_oliz(query),
        "Hukut": lambda: async_scrape_hukut(query),
        "NeoStore": lambda: async_scrape_neostore(query),
        "CGDigital": lambda: async_scrape_cgdigital(query),
        "HardwarePasal": lambda: async_scrape_hardwarepasal(query),
        "UfoNepal": lambda: async_scrape_ufonepal(query),
        "Jeevee": lambda: async_scrape_jeevee(query),
    }
    
    print(f"Testing all scrapers with query: '{query}'")
    print("=" * 60)
    
    for name, func in scrapers.items():
        try:
            products = await func()
            count = len(products)
            urls_ok = sum(1 for p in products if p.get('product_url', '').startswith('http'))
            print(f"{name:20s}: {count:4d} products, {urls_ok:4d} have valid URLs")
            if products:
                p = products[0]
                print(f"  Sample: {p.get('product_name', 'N/A')[:50]}")
                print(f"  URL: {p.get('product_url', 'N/A')[:80]}")
                print(f"  Price: {p.get('price')}")
        except Exception as e:
            print(f"{name:20s}: ERROR - {e}")
        print()

if __name__ == "__main__":
    asyncio.run(test_all())
