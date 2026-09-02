import asyncio
from scrapers.jeevee.jeevee_scraper import async_scrape_jeevee
from scrapers.cgdigital.cgdigital_scraper import async_scrape_cgdigital

async def test_scrapers():
    print("Testing Jeevee...")
    jeevee_products = await async_scrape_jeevee("iphone")
    print(f"Jeevee found {len(jeevee_products)} products.")
    if jeevee_products:
        print(jeevee_products[0])
        
    print("\nTesting CGDigital...")
    cgdigital_products = await async_scrape_cgdigital("iphone")
    print(f"CGDigital found {len(cgdigital_products)} products.")
    if cgdigital_products:
        print(cgdigital_products[0])

if __name__ == "__main__":
    asyncio.run(test_scrapers())
