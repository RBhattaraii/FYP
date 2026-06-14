from fastapi import APIRouter, HTTPException, BackgroundTasks
from pydantic import BaseModel
from typing import List, Optional
from datetime import datetime, timezone, timedelta
import asyncio

from app.database.mongo import get_raw_products_collection
from app.services.scraper_service import async_scrape_daraz, async_scrape_oliz, async_scrape_hukut, async_scrape_neostore, async_scrape_cgdigital, async_scrape_better, async_scrape_hardwarepasal, async_scrape_ufonepal, async_scrape_jeevee

router = APIRouter(
    prefix="/products",
    tags=["products"],
    responses={404: {"description": "Not found"}},
)

CACHE_DURATION_HOURS = 24

def serialize_mongo_doc(doc):
    """Convert MongoDB _id ObjectId to string for JSON serialization."""
    if doc and "_id" in doc:
        doc["_id"] = str(doc["_id"])
    return doc

@router.get("/search")
async def search_products(q: str):
    """
    Search for products across e-commerce platforms.
    First checks MongoDB cache. If cache miss or expired, runs live scraper.
    """
    if not q or len(q.strip()) == 0:
        raise HTTPException(status_code=400, detail="Search query cannot be empty")
        
    search_query = q.strip().lower()
    
    try:
        collection = get_raw_products_collection()
    except RuntimeError as e:
        # MongoDB might not be connected if not set up properly in main.py
        raise HTTPException(status_code=503, detail=str(e))

    # 1. Check Cache
    # We look for documents that match the exact search_term
    cutoff_time = datetime.now(timezone.utc) - timedelta(hours=CACHE_DURATION_HOURS)
    
    cached_products = list(collection.find({
        "search_term": search_query,
        # Check if scraped_at string represents a time > cutoff_time
        "scraped_at": {"$gte": cutoff_time.isoformat()}
    }))
    
    if cached_products and len(cached_products) > 0:
        print(f"CACHE HIT: Found {len(cached_products)} products for '{search_query}'")
        return {
            "source": "cache",
            "search_query": search_query,
            "results_count": len(cached_products),
            "data": [serialize_mongo_doc(p) for p in cached_products]
        }

    print(f"CACHE MISS: Running live scrapers for '{search_query}'...")
    
    # 2. Run Live Scrapers Concurrently
    try:
        # We await the scraping here. All scrapers run at the same time.
        daraz_task = async_scrape_daraz(search_query, max_pages=1)
        oliz_task = async_scrape_oliz(search_query)
        hukut_task = async_scrape_hukut(search_query)
        neostore_task = async_scrape_neostore(search_query)
        cgdigital_task = async_scrape_cgdigital(search_query)
        better_task = async_scrape_better(search_query)
        hardwarepasal_task = async_scrape_hardwarepasal(search_query)
        ufonepal_task = async_scrape_ufonepal(search_query)
        jeevee_task = async_scrape_jeevee(search_query)
        
        results = await asyncio.gather(daraz_task, oliz_task, hukut_task, neostore_task, cgdigital_task, better_task, hardwarepasal_task, ufonepal_task, jeevee_task, return_exceptions=True)
        
        new_products = []
        for result in results:
            if isinstance(result, Exception):
                print(f"Scraper returned exception: {result}")
            elif result:
                new_products.extend(result)
                
    except Exception as e:
        print(f"Scraping error: {e}")
        raise HTTPException(status_code=500, detail="Failed to scrape products")
        
    if not new_products:
        return {
            "source": "live",
            "search_query": search_query,
            "results_count": 0,
            "data": []
        }
        
    # 3. Save to Cache
    # We delete old cached items for this exact search term to keep DB clean
    collection.delete_many({"search_term": search_query})
    
    # Insert new items
    try:
        collection.insert_many(new_products)
    except Exception as e:
        print(f"Failed to cache products to MongoDB: {e}")
        # Even if caching fails, we still return the products to the user
        
    return {
        "source": "live",
        "search_query": search_query,
        "results_count": len(new_products),
        "data": [serialize_mongo_doc(p) for p in new_products]
    }
