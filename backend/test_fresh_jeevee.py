"""
Test Jeevee scraper with FRESH products from their live API
This proves the scraper generates working URLs for current inventory
"""
import asyncio
import requests
import sys
import os

# Add parent directory to import scrapers
sys.path.insert(0, r'C:\Users\NITOR 5\Desktop\FYP')

from scrapers.jeevee.jeevee_scraper import async_scrape_jeevee

async def main():
    print("="*80)
    print("TESTING JEEVEE SCRAPER WITH LIVE DATA")
    print("="*80)
    
    # Scrape fresh products from Jeevee API
    print("\n1. Scraping fresh products from Jeevee API...")
    products = await async_scrape_jeevee("laptop")
    
    if not products:
        print("❌ No products scraped")
        return
    
    print(f"✅ Scraped {len(products)} products")
    
    # Test first 5 URLs
    print("\n2. Testing first 5 product URLs:")
    print("="*80)
    
    working_count = 0
    broken_count = 0
    
    for i, product in enumerate(products[:5], 1):
        url = product['product_url']
        name = product['product_name'][:60]
        
        try:
            response = requests.head(url, timeout=5, allow_redirects=True)
            status = response.status_code
            final_url = response.url
            
            if status == 200:
                result = "✅ WORKING"
                working_count += 1
            elif status == 404:
                result = "❌ 404 NOT FOUND"
                broken_count += 1
            elif status in [301, 302, 303]:
                # Check if redirect goes to 404 page
                if '/404' in final_url:
                    result = "❌ REDIRECTS TO 404"
                    broken_count += 1
                else:
                    result = f"✅ REDIRECT ({status})"
                    working_count += 1
            else:
                result = f"⚠️ Status {status}"
                
            print(f"\n{i}. {result}")
            print(f"   Name: {name}")
            print(f"   URL: {url}")
            if final_url != url:
                print(f"   Final: {final_url}")
                
        except Exception as e:
            print(f"\n{i}. ❌ ERROR")
            print(f"   Name: {name}")
            print(f"   URL: {url}")
            print(f"   Error: {str(e)[:50]}")
            broken_count += 1
    
    print("\n" + "="*80)
    print("SUMMARY")
    print("="*80)
    print(f"Working URLs: {working_count}/5")
    print(f"Broken URLs: {broken_count}/5")
    
    if working_count >= 4:
        print("\n✅ SUCCESS: Scraper generates working URLs!")
    elif working_count >= 2:
        print("\n⚠️ PARTIAL: Some URLs work, some don't")
    else:
        print("\n❌ FAILED: Most URLs are broken")

if __name__ == "__main__":
    asyncio.run(main())
