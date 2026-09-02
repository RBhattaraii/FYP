#!/usr/bin/env python3
"""
TEST ALL 9 SCRAPERS
Verify which platforms are working and get sample data from each
"""

import asyncio
import sys
import os

# Add paths for imports
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))
sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'scrapers'))

# Import ALL scrapers
from scrapers.daraz.daraz_scraper import sync_scrape_daraz
from scrapers.cgdigital.cgdigital_scraper import async_scrape_cgdigital
from scrapers.better.better_scraper import async_scrape_better
from scrapers.hardwarepasal.hardwarepasal_scraper import async_scrape_hardwarepasal
from scrapers.hukut.hukut_scraper import async_scrape_hukut
from scrapers.jeevee.jeevee_scraper import async_scrape_jeevee
from scrapers.neostore.neostore_scraper import async_scrape_neostore
from scrapers.oliz.oliz_scraper import async_scrape_oliz
from scrapers.ufonepal.ufonepal_scraper import async_scrape_ufonepal

async def test_scraper(scraper_name, scraper_func, test_term, is_sync=False):
    """Test a single scraper"""
    print(f"\n🧪 TESTING {scraper_name}")
    print(f"   Search term: '{test_term}'")
    
    try:
        if is_sync:
            products = scraper_func(test_term, max_pages=1)
        else:
            products = await scraper_func(test_term)
        
        if products and len(products) > 0:
            print(f"   ✅ SUCCESS: {len(products)} products found")
            
            # Show sample product
            sample = products[0]
            title = sample.get('product_name', 'No title')[:50]
            price = sample.get('price', 'No price')
            print(f"   📦 Sample: {title}... - Rs {price}")
            return True, len(products)
        else:
            print(f"   ❌ FAILED: No products returned")
            return False, 0
            
    except Exception as e:
        print(f"   ❌ ERROR: {str(e)[:100]}...")
        return False, 0

async def main():
    """Test all 9 scrapers"""
    print("🔍 TESTING ALL 9 E-COMMERCE SCRAPERS")
    print("=" * 60)
    
    # Define all scrapers to test
    scrapers_to_test = [
        ("Daraz", sync_scrape_daraz, "laptop", True),
        ("CGDigital", async_scrape_cgdigital, "laptop", False),
        ("Better", async_scrape_better, "laptop", False), 
        ("HardwarePasal", async_scrape_hardwarepasal, "laptop", False),
        ("Hukut", async_scrape_hukut, "laptop", False),
        ("Jeevee", async_scrape_jeevee, "laptop", False),
        ("Neostore", async_scrape_neostore, "laptop", False),
        ("Oliz", async_scrape_oliz, "laptop", False),
        ("UFONepal", async_scrape_ufonepal, "laptop", False)
    ]
    
    working_scrapers = []
    failed_scrapers = []
    total_products = 0
    
    for scraper_name, scraper_func, test_term, is_sync in scrapers_to_test:
        success, product_count = await test_scraper(scraper_name, scraper_func, test_term, is_sync)
        
        if success:
            working_scrapers.append((scraper_name, product_count))
            total_products += product_count
        else:
            failed_scrapers.append(scraper_name)
        
        # Small delay between tests
        await asyncio.sleep(2)
    
    # Summary
    print("\n" + "=" * 60)
    print("📊 SCRAPER TEST SUMMARY")
    print("=" * 60)
    
    print(f"✅ WORKING SCRAPERS ({len(working_scrapers)}/9):")
    for scraper_name, count in working_scrapers:
        print(f"   • {scraper_name}: {count} products")
    
    if failed_scrapers:
        print(f"\n❌ FAILED SCRAPERS ({len(failed_scrapers)}/9):")
        for scraper_name in failed_scrapers:
            print(f"   • {scraper_name}")
    
    print(f"\n📈 TOTAL TEST PRODUCTS: {total_products}")
    print(f"🎯 SUCCESS RATE: {(len(working_scrapers)/9)*100:.1f}%")
    
    if len(working_scrapers) >= 5:
        print("\n✅ SUFFICIENT PLATFORMS for balanced scraping!")
    elif len(working_scrapers) >= 3:
        print("\n⚠️  LIMITED PLATFORMS - may need alternative approaches")
    else:
        print("\n❌ INSUFFICIENT PLATFORMS - need to fix scrapers")

if __name__ == "__main__":
    asyncio.run(main())