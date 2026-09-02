"""
generate_synthetic_products.py  (v2 - fast)
=============================================
Generates realistic synthetic products to reach 500,000 total.
Uses UUID-based URLs for guaranteed uniqueness and large batch inserts.

Run:  python generate_synthetic_products.py
"""

import asyncio
import asyncpg
import os
import random
import uuid
import time
from dotenv import load_dotenv

load_dotenv()

TARGET     = 500_000
BATCH_SIZE = 5_000

# ─── Variant templates per category ─────────────────────────────────────────
VARIANT_CONFIGS = {
    "Electronics": {
        "prefixes": ["Samsung", "Apple", "Xiaomi", "OnePlus", "Dell", "HP", "Lenovo", "Asus", "Acer", "Sony", "LG", "TCL", "Hisense", "JBL", "Bose", "Anker"],
        "products": ["Smartphone", "Laptop", "Tablet", "Smart TV", "Monitor", "Headphones", "Earbuds", "Bluetooth Speaker", "Power Bank", "Smartwatch", "Keyboard", "Mouse", "Webcam", "Router", "Printer", "SSD", "External HDD", "USB Hub", "HDMI Cable", "Charger"],
        "suffixes": ["64GB", "128GB", "256GB", "512GB", "1TB", "4GB RAM", "8GB RAM", "16GB RAM", "32GB RAM", "Black", "White", "Silver", "Gold", "Blue", "Red", "Pro", "Plus", "Max", "Ultra", "Lite", "Mini", "SE"],
        "price_range": (1500, 500000),
    },
    "Mobile Accessories": {
        "prefixes": ["Spigen", "ESR", "Nillkin", "Baseus", "Anker", "Ugreen", "Generic", "Premium"],
        "products": ["Phone Case", "Screen Protector", "Car Mount", "Phone Stand", "Selfie Stick", "USB-C Cable", "Lightning Cable", "Wireless Charger", "Car Charger", "Pop Socket", "Ring Holder", "Camera Lens Kit"],
        "suffixes": ["for iPhone 15", "for iPhone 14", "for Samsung S24", "for Samsung S23", "for Xiaomi 14", "for OnePlus 12", "Black", "Clear", "Blue", "Red", "Matte", "Glossy", "Slim", "Heavy Duty"],
        "price_range": (200, 8000),
    },
    "Home Appliances": {
        "prefixes": ["Samsung", "LG", "Panasonic", "Philips", "Midea", "Haier", "Daikin", "Sharp", "Bosch", "Whirlpool"],
        "products": ["Refrigerator", "Washing Machine", "Air Conditioner", "Microwave Oven", "Vacuum Cleaner", "Air Purifier", "Water Heater", "Rice Cooker", "Iron", "Fan", "Dishwasher", "Dehumidifier"],
        "suffixes": ["5L", "7L", "180L", "260L", "350L", "500L", "1.5 Ton", "2 Ton", "Inverter", "Smart", "Energy Star", "White", "Silver", "Black"],
        "price_range": (3000, 250000),
    },
    "Kitchen": {
        "prefixes": ["Prestige", "Hawkins", "Pigeon", "Butterfly", "Wonderchef", "Milton", "Borosil", "Cello"],
        "products": ["Pressure Cooker", "Frying Pan", "Cookware Set", "Knife Set", "Cutting Board", "Food Container", "Thermos Flask", "Lunch Box", "Blender", "Mixer Grinder", "Electric Kettle", "Toaster", "Coffee Maker", "Juicer"],
        "suffixes": ["3L", "5L", "Set of 3", "Set of 5", "Stainless Steel", "Non-Stick", "Ceramic", "Glass", "Small", "Medium", "Large", "Red", "Black", "Silver"],
        "price_range": (500, 25000),
    },
    "Fashion": {
        "prefixes": ["Nike", "Adidas", "Puma", "Zara", "H&M", "Uniqlo", "Levi's", "Tommy Hilfiger", "Calvin Klein", "Under Armour", "New Balance", "Goldstar"],
        "products": ["T-Shirt", "Polo Shirt", "Hoodie", "Jacket", "Jeans", "Chinos", "Shorts", "Dress", "Skirt", "Sneakers", "Running Shoes", "Sandals", "Formal Shoes", "Backpack", "Crossbody Bag", "Wallet", "Belt", "Watch", "Sunglasses", "Cap"],
        "suffixes": ["XS", "S", "M", "L", "XL", "XXL", "Black", "White", "Navy", "Grey", "Red", "Green", "Beige", "Blue", "Pink", "Men's", "Women's", "Unisex"],
        "price_range": (500, 35000),
    },
    "Beauty & Health": {
        "prefixes": ["Cetaphil", "CeraVe", "The Ordinary", "Neutrogena", "L'Oreal", "Maybelline", "Nivea", "Dove", "Himalaya", "Biotique", "Lakme", "Garnier"],
        "products": ["Face Wash", "Moisturizer", "Sunscreen SPF50", "Serum", "Foundation", "Lipstick", "Mascara", "Shampoo", "Conditioner", "Body Lotion", "Face Mask", "Toner", "Eye Cream", "Hair Oil", "Deodorant", "Perfume", "Nail Polish"],
        "suffixes": ["50ml", "100ml", "200ml", "300ml", "500ml", "30g", "50g", "Original", "For Oily Skin", "For Dry Skin", "For Sensitive Skin", "Matte", "Natural", "SPF30", "SPF50"],
        "price_range": (200, 15000),
    },
    "Sports": {
        "prefixes": ["Nike", "Adidas", "Puma", "Under Armour", "Reebok", "Decathlon", "Yonex", "Wilson", "Head"],
        "products": ["Yoga Mat", "Dumbbell Set", "Resistance Band", "Jump Rope", "Cricket Bat", "Football", "Badminton Racket", "Tennis Racket", "Cycling Helmet", "Gym Gloves", "Sports Bra", "Track Pants", "Wrist Band", "Knee Support"],
        "suffixes": ["S", "M", "L", "XL", "Black", "Blue", "Red", "Green", "Grey", "Pro", "Lite", "5kg", "10kg", "15kg", "20kg"],
        "price_range": (300, 25000),
    },
    "Baby & Kids": {
        "prefixes": ["Johnson's", "Pampers", "Huggies", "Fisher-Price", "Lego", "Hot Wheels", "Disney", "Carter's", "Mothercare"],
        "products": ["Baby Onesie", "Baby Shoes", "Diapers Pack", "Baby Shampoo", "Baby Lotion", "Stroller", "Car Seat", "Toy Set", "Building Blocks", "Puzzle", "School Bag", "Lunch Box", "Water Bottle", "Baby Blanket"],
        "suffixes": ["0-6M", "6-12M", "1-2Y", "2-3Y", "3-5Y", "5-8Y", "Pink", "Blue", "Yellow", "Green", "Multi", "Small", "Medium", "Large"],
        "price_range": (200, 35000),
    },
    "Books & Stationery": {
        "prefixes": ["Classmate", "Doms", "Faber-Castell", "Staedtler", "Parker", "Cello", "Camlin", "Natraj"],
        "products": ["Notebook A4", "Notebook A5", "Ballpoint Pen", "Gel Pen Set", "Pencil Set", "Marker Set", "Highlighter Set", "File Folder", "Sticky Notes", "Calculator", "Geometry Box", "Sketch Book", "Color Pencils", "Eraser Pack"],
        "suffixes": ["Pack of 5", "Pack of 10", "Pack of 20", "Single", "Set", "Blue", "Black", "Red", "Multi Color", "100 Pages", "200 Pages", "300 Pages"],
        "price_range": (50, 5000),
    },
    "Gaming": {
        "prefixes": ["Logitech", "Razer", "SteelSeries", "Corsair", "HyperX", "Redragon", "MSI", "ASUS ROG"],
        "products": ["Gaming Mouse", "Gaming Keyboard", "Gaming Headset", "Gaming Chair", "Controller", "Mousepad", "GPU", "RAM", "Gaming Monitor", "Capture Card", "Streaming Mic", "Webcam"],
        "suffixes": ["RGB", "Wireless", "Wired", "Mechanical", "Black", "White", "Red", "TKL", "Full Size", "7.1 Surround", "4K", "1080p", "144Hz", "240Hz"],
        "price_range": (1000, 200000),
    },
}

STORES = ["Daraz", "Jeevee", "Hukut", "Oliz", "CgDigital", "Better", "HardwarePasal", "NeoStore", "UfoNepal"]
STORE_WEIGHTS = [0.30, 0.18, 0.15, 0.10, 0.08, 0.07, 0.05, 0.04, 0.03]


def generate_product(category: str, config: dict) -> tuple:
    """Generate a single synthetic product as a tuple ready for DB insert."""
    prefix  = random.choice(config["prefixes"])
    product = random.choice(config["products"])
    suffix  = random.choice(config["suffixes"])
    
    title = f"{prefix} {product} {suffix}"
    
    lo, hi = config["price_range"]
    price = round(random.uniform(lo, hi), 2)
    
    # 50% chance of having an original (higher) price
    if random.random() > 0.5:
        original_price = round(price * random.uniform(1.05, 1.40), 2)
        discount = int(round((1 - price / original_price) * 100))
    else:
        original_price = None
        discount = None
    
    store = random.choices(STORES, weights=STORE_WEIGHTS, k=1)[0]
    
    # Image URL from a real product placeholder per store
    image_url = f"https://via.placeholder.com/300x300.png?text={prefix}+{product}".replace(" ", "+")
    
    # Truly unique URL using UUID
    product_url = f"https://{store.lower()}.synthetic/{uuid.uuid4().hex}"
    
    return (title, price, original_price, discount, image_url, store, product_url, category)


async def main():
    conn = await asyncpg.connect(os.getenv("DATABASE_URL"), statement_cache_size=0)
    
    current = await conn.fetchval("SELECT COUNT(*) FROM products")
    need = TARGET - current
    
    print(f"\n{'='*60}")
    print(f"  SYNTHETIC GENERATOR v2 (fast)")
    print(f"  Current: {current:,}  |  Target: {TARGET:,}  |  Need: {need:,}")
    print(f"{'='*60}\n")
    
    if need <= 0:
        print("  Already at or above target!")
        await conn.close()
        return
    
    # Also normalize existing store names
    print("  Normalizing existing store names...")
    await conn.execute("UPDATE products SET store_name = 'CgDigital' WHERE store_name = 'Cgdigital'")
    await conn.execute("UPDATE products SET store_name = 'HardwarePasal' WHERE store_name = 'Hardwarepasal'")
    await conn.execute("UPDATE products SET store_name = 'NeoStore' WHERE store_name = 'Neostore'")
    await conn.execute("UPDATE products SET store_name = 'UfoNepal' WHERE store_name = 'Ufonepal'")
    print("  Done.\n")
    
    categories = list(VARIANT_CONFIGS.keys())
    products_per_category = need // len(categories)
    remainder = need % len(categories)
    
    start_time = time.time()
    total_inserted = 0
    
    for i, category in enumerate(categories):
        config = VARIANT_CONFIGS[category]
        count_for_cat = products_per_category + (1 if i < remainder else 0)
        
        print(f"  [{i+1}/{len(categories)}] {category}: generating {count_for_cat:,} products...")
        
        batch = []
        cat_inserted = 0
        
        for _ in range(count_for_cat):
            batch.append(generate_product(category, config))
            
            if len(batch) >= BATCH_SIZE:
                try:
                    await conn.executemany("""
                        INSERT INTO products
                          (title, price, original_price, discount_percent,
                           image_url, store_name, product_url, category)
                        VALUES ($1, $2, $3, $4, $5, $6, $7, $8)
                        ON CONFLICT (product_url) DO NOTHING
                    """, batch)
                    cat_inserted += len(batch)
                    total_inserted += len(batch)
                except Exception as e:
                    print(f"    [DB ERROR] {e}")
                batch.clear()
                
                elapsed = time.time() - start_time
                rate = total_inserted / elapsed if elapsed > 0 else 0
                eta = (need - total_inserted) / rate if rate > 0 else 0
                pct = (total_inserted / need) * 100
                print(f"    {total_inserted:,}/{need:,} ({pct:.1f}%) | {rate:.0f} products/sec | ETA: {eta:.0f}s")
        
        # Flush remaining
        if batch:
            try:
                await conn.executemany("""
                    INSERT INTO products
                      (title, price, original_price, discount_percent,
                       image_url, store_name, product_url, category)
                    VALUES ($1, $2, $3, $4, $5, $6, $7, $8)
                    ON CONFLICT (product_url) DO NOTHING
                """, batch)
                cat_inserted += len(batch)
                total_inserted += len(batch)
            except Exception as e:
                print(f"    [DB ERROR] {e}")
            batch.clear()
        
        print(f"    -> {cat_inserted:,} inserted for {category}")
    
    # Rebuild search vectors
    print(f"\n  Refreshing search vectors for all products...")
    await conn.execute("""
        UPDATE products
        SET search_vector = to_tsvector('english', title)
        WHERE search_vector IS NULL
    """)
    print("  Search vectors updated.")
    
    # Final count
    after = await conn.fetchval("SELECT COUNT(*) FROM products")
    elapsed = time.time() - start_time
    
    print(f"\n{'='*60}")
    print(f"  DONE!")
    print(f"  Inserted: {total_inserted:,} synthetic products")
    print(f"  Total in DB: {after:,}")
    print(f"  Time: {elapsed:.1f}s ({elapsed/60:.1f} min)")
    print(f"{'='*60}\n")
    
    # Show distribution
    by_store = await conn.fetch("SELECT store_name, COUNT(*) as cnt FROM products GROUP BY store_name ORDER BY cnt DESC")
    print("  Store distribution:")
    for row in by_store:
        print(f"    {row['store_name']}: {row['cnt']:,}")
    
    by_cat = await conn.fetch("SELECT category, COUNT(*) as cnt FROM products GROUP BY category ORDER BY cnt DESC LIMIT 15")
    print("\n  Category distribution:")
    for row in by_cat:
        print(f"    {row['category']}: {row['cnt']:,}")
    
    await conn.close()


if __name__ == "__main__":
    asyncio.run(main())
