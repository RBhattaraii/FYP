"""
==============================================================
  VERIFY SCRAPED DATA IN MONGODB
  ──────────────────────────────
  Run this after the scraper to check if data was saved
  correctly in MongoDB Atlas.
==============================================================
"""

import os
import certifi
from pathlib import Path
from dotenv import load_dotenv
from pymongo import MongoClient

# Load from backend/.env (same file the backend uses)
env_path = Path(__file__).parent.parent / "backend" / ".env"
load_dotenv(env_path)

MONGODB_URI = os.getenv("MONGODB_URI")
DB_NAME = "pricepilot_raw"
COLLECTION_NAME = "raw_products"


def verify():
    print("=" * 60)
    print("  MONGODB VERIFICATION - pricepilot_raw.raw_products")
    print("=" * 60)
    print()
    
    client = MongoClient(MONGODB_URI, tlsCAFile=certifi.where())
    db = client[DB_NAME]
    collection = db[COLLECTION_NAME]
    
    # 1. Total document count
    total = collection.count_documents({})
    print(f"  Total documents in collection : {total}")
    
    # 2. Count by source
    daraz_count = collection.count_documents({"source": "daraz_scraper"})
    print(f"  Documents from daraz_scraper  : {daraz_count}")
    
    # 3. Show latest 3 products
    print()
    print("  LATEST 3 SCRAPED PRODUCTS:")
    print("  " + "-" * 50)
    
    latest = collection.find(
        {"source": "daraz_scraper"}
    ).sort("scraped_at", -1).limit(3)
    
    for i, doc in enumerate(latest, 1):
        print(f"\n  [{i}] {doc.get('product_name', 'N/A')}")
        print(f"      Price     : Rs. {doc.get('price', 'N/A')}")
        print(f"      Original  : Rs. {doc.get('original_price', 'N/A')}")
        print(f"      Discount  : {doc.get('discount_percentage', 'N/A')}%")
        print(f"      Rating    : {doc.get('rating', 'N/A')}")
        print(f"      Reviews   : {doc.get('review_count', 'N/A')}")
        print(f"      Platform  : {doc.get('platform', 'N/A')}")
        print(f"      Scraped   : {doc.get('scraped_at', 'N/A')}")
        print(f"      URL       : {doc.get('product_url', 'N/A')[:80]}...")
    
    # 4. Products with discounts
    discounted = collection.count_documents({
        "source": "daraz_scraper",
        "discount_percentage": {"$ne": None}
    })
    print(f"\n  Products with discounts : {discounted}")
    
    # 5. Products with ratings
    rated = collection.count_documents({
        "source": "daraz_scraper",
        "rating": {"$ne": None}
    })
    print(f"  Products with ratings   : {rated}")
    
    print()
    print("=" * 60)
    print("  Verification complete!")
    print("=" * 60)
    
    client.close()


if __name__ == "__main__":
    verify()
