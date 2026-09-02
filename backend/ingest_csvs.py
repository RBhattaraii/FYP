import os
import asyncio
import asyncpg
import pandas as pd
import re
from dotenv import load_dotenv
from app.database.mongodb import MongoDBService
import datetime

load_dotenv()

def clean_price(price_str):
    if pd.isna(price_str):
        return 0.0
    price_str = str(price_str)
    # Remove all non-numeric characters except dot
    cleaned = re.sub(r'[^\d.]', '', price_str)
    try:
        val = float(cleaned) if cleaned else 0.0
        return min(val, 99999999.99)
    except ValueError:
        return 0.0

async def ingest():
    url = os.getenv('DATABASE_URL')
    if not url:
        print("Error: DATABASE_URL not set in .env")
        return
        
    conn = await asyncpg.connect(url, statement_cache_size=0)
    
    await MongoDBService.connect()
    mongo_db = MongoDBService.get_db()
    
    data_dir = r"C:\Users\NITOR 5\Desktop\FYP\Data"
    all_products = []
    
    # 1. Oliz
    oliz_path = os.path.join(data_dir, "Oliz", "Oliz (1).csv")
    if os.path.exists(oliz_path):
        df = pd.read_csv(oliz_path)
        for _, row in df.iterrows():
            if pd.isna(row.get('product_name')) or pd.isna(row.get('product_link')): continue
            title = str(row['product_name']).strip()
            price = clean_price(row.get('product_price'))
            image_url = str(row.get('product_image')) if not pd.isna(row.get('product_image')) else None
            product_url = str(row['product_link']).strip()
            # Category can be derived from brand_link or just use "Electronics"
            category = "Electronics"
            
            mongo_id = None
            if mongo_db is not None:
                mongo_doc = row.to_dict()
                mongo_doc['scraped_at'] = datetime.datetime.now()
                mongo_res = await mongo_db['raw_products'].insert_one(mongo_doc)
                mongo_id = str(mongo_res.inserted_id)

            all_products.append((title[:255], price, None, None, image_url, "Oliz", product_url, category, mongo_id))
        print(f"Loaded Oliz: {len(df)} rows")
    
    # 2. CG Digital
    cg_path = os.path.join(data_dir, "CG Digital", "CGDigital.csv")
    if os.path.exists(cg_path):
        df = pd.read_csv(cg_path)
        for _, row in df.iterrows():
            if pd.isna(row.get('name')) or pd.isna(row.get('url')): continue
            title = str(row['name']).replace('\n', ' ').strip()
            price = clean_price(row.get('price'))
            image_url = str(row.get('image')) if not pd.isna(row.get('image')) else None
            product_url = str(row['url']).strip()
            category = str(row.get('category')) if not pd.isna(row.get('category')) else None
            
            mongo_id = None
            if mongo_db is not None:
                mongo_doc = row.to_dict()
                mongo_doc['scraped_at'] = datetime.datetime.now()
                mongo_res = await mongo_db['raw_products'].insert_one(mongo_doc)
                mongo_id = str(mongo_res.inserted_id)

            all_products.append((title[:255], price, None, None, image_url, "CG Digital", product_url, category, mongo_id))
        print(f"Loaded CG Digital: {len(df)} rows")
            
    # 3. KoreanBP
    kbp_path = os.path.join(data_dir, "KBP", "KoreanBP.csv")
    if os.path.exists(kbp_path):
        df = pd.read_csv(kbp_path)
        for _, row in df.iterrows():
            if pd.isna(row.get('name')) or pd.isna(row.get('url')): continue
            title = str(row['name']).strip()
            price = clean_price(row.get('price'))
            image_url = str(row.get('image')) if not pd.isna(row.get('image')) else None
            product_url = str(row['url']).strip()
            category = str(row.get('brand')) if not pd.isna(row.get('brand')) else "Beauty"
            
            mongo_id = None
            if mongo_db is not None:
                mongo_doc = row.to_dict()
                mongo_doc['scraped_at'] = datetime.datetime.now()
                mongo_res = await mongo_db['raw_products'].insert_one(mongo_doc)
                mongo_id = str(mongo_res.inserted_id)

            all_products.append((title[:255], price, None, None, image_url, "KoreanBP", product_url, category, mongo_id))
        print(f"Loaded KoreanBP: {len(df)} rows")
            
    # 4. Hukut
    hukut_path = os.path.join(data_dir, "Hukut", "Hukut-s.csv")
    if os.path.exists(hukut_path):
        df = pd.read_csv(hukut_path)
        for _, row in df.iterrows():
            if pd.isna(row.get('Pname')) or pd.isna(row.get('P-URL')): continue
            title = str(row['Pname']).strip()
            price = clean_price(row.get('P-Price'))
            image_url = str(row.get('P-Image')) if not pd.isna(row.get('P-Image')) else None
            product_url = str(row['P-URL']).strip()
            if product_url.startswith('https://hukut.com/product/'):
                product_url = product_url.replace('https://hukut.com/product/', 'https://hukut.com/')
            category = str(row.get('brand')) if not pd.isna(row.get('brand')) else "Electronics"
            
            mongo_id = None
            if mongo_db is not None:
                mongo_doc = row.to_dict()
                mongo_doc['scraped_at'] = datetime.datetime.now()
                mongo_res = await mongo_db['raw_products'].insert_one(mongo_doc)
                mongo_id = str(mongo_res.inserted_id)

            all_products.append((title[:255], price, None, None, image_url, "Hukut", product_url, category, mongo_id))
        print(f"Loaded Hukut: {len(df)} rows")
            
    print(f"Total valid products to insert: {len(all_products)}")
    
    if all_products:
        try:
            await conn.executemany("""
                INSERT INTO products 
                (title, price, original_price, discount_percent, image_url, store_name, product_url, category, mongo_id)
                VALUES ($1, $2, $3, $4, $5, $6, $7, $8, $9)
                ON CONFLICT (product_url) DO UPDATE
                SET title = EXCLUDED.title,
                    price = EXCLUDED.price,
                    image_url = EXCLUDED.image_url,
                    category = EXCLUDED.category,
                    mongo_id = EXCLUDED.mongo_id,
                    scraped_at = NOW()
            """, all_products)
            print("Successfully inserted all products into database.")
        except Exception as e:
            print(f"Error inserting products: {e}")
            
    await conn.close()
    await MongoDBService.disconnect()

if __name__ == "__main__":
    asyncio.run(ingest())
