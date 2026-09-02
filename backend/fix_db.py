import asyncio
import asyncpg
import os
from dotenv import load_dotenv

async def run():
    load_dotenv()
    conn = await asyncpg.connect(os.getenv("DATABASE_URL"), statement_cache_size=0)
    
    # 1. Delete all products with 0 price (or less)
    deleted = await conn.execute("DELETE FROM products WHERE price <= 0")
    print(f"Deleted products with 0 price: {deleted}")
    
    # 2. Nullify the generic iPhone image that was applied to many Oliz products
    bad_img_url = "https://wsrv.nl/?w=560&url=https://cdn2.blanxer.com/uploads/682feff88c633f25b4c7ce32/product_image-iphone-17e-collection-9526.webp"
    updated = await conn.execute("UPDATE products SET image_url = NULL WHERE image_url = $1", bad_img_url)
    print(f"Removed generic image from products: {updated}")
    
    await conn.close()

if __name__ == "__main__":
    asyncio.run(run())
