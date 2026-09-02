import asyncio
import asyncpg
import os
from dotenv import load_dotenv

load_dotenv()

async def categorize_data():
    url = os.getenv('DATABASE_URL')
    conn = await asyncpg.connect(url, statement_cache_size=0)
    
    print("Fetching all products for categorization...")
    products = await conn.fetch("SELECT id, title FROM products")
    print(f"Loaded {len(products)} products.")
    
    updates = []
    
    for p in products:
        title = p['title'].lower()
        category = "Others"
        
        # 1. Mobile Phones
        if any(w in title for w in ['iphone', 'smartphone', 'samsung galaxy', 'redmi', 'realme', 'poco', 'vivo', 'oppo', 'oneplus', 'pixel']):
            category = "Mobile Phones"
        # 2. Laptops & Computers
        elif any(w in title for w in ['laptop', 'macbook', 'desktop', 'monitor', 'pc', 'thinkpad', 'ideapad', 'zenbook', 'processor', 'motherboard', 'ram']):
            category = "Laptops & Computers"
        # 3. Audio
        elif any(w in title for w in ['earbud', 'headphone', 'earphone', 'airpod', 'speaker', 'soundbar', 'jbl', 'bose']):
            category = "Audio"
        # 4. Televisions
        elif any(w in title for w in ['tv', 'television', 'smart tv', 'oled', 'qled']):
            category = "Televisions"
        # 5. Watches & Wearables
        elif any(w in title for w in ['watch', 'smartwatch', 'apple watch', 'band', 'fitness tracker']):
            category = "Watches & Wearables"
        # 6. Cameras
        elif any(w in title for w in ['camera', 'dslr', 'mirrorless', 'lens', 'gopro', 'dji', 'drone']):
            category = "Cameras"
        # 7. Gaming
        elif any(w in title for w in ['playstation', 'xbox', 'nintendo', 'gaming console', 'controller', 'ps5']):
            category = "Gaming"
        # 8. Home Appliances
        elif any(w in title for w in ['fridge', 'refrigerator', 'washing machine', 'microwave', 'oven', 'ac ', 'air conditioner', 'vacuum', 'heater', 'iron', 'blender', 'mixer']):
            category = "Home Appliances"
        # 9. Beauty
        elif any(w in title for w in ['skincare', 'cream', 'serum', 'makeup', 'perfume', 'fragrance', 'shampoo', 'lotion', 'lipstick', 'cleanser']):
            category = "Beauty & Skincare"
        # 10. Fashion & Accessories
        elif any(w in title for w in ['shirt', 'pant', 'shoe', 'bag', 'backpack', 'jewelry', 'necklace', 'ring', 'jacket', 'hoodie', 'case', 'cover']):
            category = "Fashion & Accessories"
            
        updates.append((category, p['id']))
        
    print("Updating database...")
    # Execute batch update
    await conn.executemany(
        "UPDATE products SET category = $1 WHERE id = $2",
        updates
    )
    
    print("Categorization complete!")
    await conn.close()

if __name__ == "__main__":
    asyncio.run(categorize_data())
