import asyncio
from app.services.scraper_service import async_scrape_hukut

async def test():
    products = await async_scrape_hukut("macbook")
    if products:
        print(f"Top Result: {products[0]['product_name']} - Rs. {products[0]['price']} - Original: {products[0]['original_price']} - Image: {products[0]['image_url']}")
    else:
        print("No products found")

asyncio.run(test())
