import asyncio
import asyncpg
import os
from dotenv import load_dotenv

async def run():
    load_dotenv()
    conn = await asyncpg.connect(os.getenv("DATABASE_URL"), statement_cache_size=0)
    
    img_url = "https://wsrv.nl/?w=560&url=https://cdn2.blanxer.com/uploads/682feff88c633f25b4c7ce32/product_image-iphone-17e-collection-9526.webp"
    bad_imgs = await conn.fetch("SELECT id, title, price FROM products WHERE image_url = $1 LIMIT 20", img_url)
    
    print("Sample of products with bad image:")
    for b in bad_imgs:
        print(f"{b['id']} | {b['title']} | Rs {b['price']}")
        
    await conn.close()

if __name__ == "__main__":
    asyncio.run(run())
