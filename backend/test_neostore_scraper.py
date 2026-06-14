import sys
import asyncio

# Add the FYP directory to sys.path so we can import scrapers
sys.path.append(r"C:\Users\NITOR 5\Desktop\FYP")

from scrapers.neostore.neostore_scraper import async_scrape_neostore

async def test_neostore():
    print("Testing NeoStore scraper for 'macbook'...")
    products = await async_scrape_neostore("macbook")
    
    if products:
        print(f"Found {len(products)} products.")
        p = products[0]
        print(f"Name: {p['product_name']}")
        print(f"Price: {p['price']}")
        print(f"Original Price: {p['original_price']}")
        print(f"URL: {p['product_url']}")
        print(f"Image: {p['image_url']}")
    else:
        print("No products found.")

if __name__ == "__main__":
    asyncio.run(test_neostore())
