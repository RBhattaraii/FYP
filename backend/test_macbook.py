import asyncio
from app.services.scraper_service import async_scrape_oliz

async def test():
    products = await async_scrape_oliz('macbook')
    print(f"Found {len(products)} products for 'macbook'!")
    if products:
        print(f"Top Result: {products[0]['product_name']} - Rs. {products[0]['price']}")

asyncio.run(test())
