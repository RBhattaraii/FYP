"""
Direct scraper verification script - tests URL generation without backend/cache
"""
import asyncio
import sys
import requests

# Add parent directory to path to import scrapers
sys.path.insert(0, r'C:\Users\NITOR 5\Desktop\FYP')

from scrapers.jeevee.jeevee_scraper import async_scrape_jeevee
from scrapers.oliz.oliz_scraper import async_scrape_oliz
from scrapers.hukut.hukut_scraper import async_scrape_hukut


def test_url(url: str, platform: str) -> str:
    """Test if a URL returns a valid status code"""
    try:
        response = requests.head(url, timeout=5, allow_redirects=True)
        status = response.status_code
        if status in [200, 301, 302, 303]:
            return "✅ WORKING"
        elif status == 404:
            return f"❌ 404 NOT FOUND"
        elif status == 403:
            return f"❌ 403 FORBIDDEN"
        else:
            return f"⚠️ Status {status}"
    except requests.Timeout:
        return "⏱️ TIMEOUT"
    except Exception as e:
        return f"❌ ERROR: {str(e)[:50]}"


async def main():
    print("=" * 80)
    print("DIRECT SCRAPER URL VERIFICATION")
    print("Testing scrapers directly (bypassing backend cache)")
    print("=" * 80)
    
    # Test Jeevee
    print("\n🔍 Testing JEEVEE scraper...")
    jeevee_products = await async_scrape_jeevee("laptop")
    print(f"Found {len(jeevee_products)} Jeevee products")
    
    if jeevee_products:
        print("\nTesting first 5 Jeevee URLs:")
        for i, product in enumerate(jeevee_products[:5], 1):
            url = product['product_url']
            name = product['product_name'][:50]
            result = test_url(url, 'jeevee')
            print(f"{i}. {result}")
            print(f"   Name: {name}")
            print(f"   URL: {url}")
            print()
    
    # Test Oliz
    print("\n🔍 Testing OLIZ scraper...")
    oliz_products = await async_scrape_oliz("laptop")
    print(f"Found {len(oliz_products)} Oliz products")
    
    if oliz_products:
        print("\nTesting first 5 Oliz URLs:")
        for i, product in enumerate(oliz_products[:5], 1):
            url = product['product_url']
            name = product['product_name'][:50]
            result = test_url(url, 'oliz')
            print(f"{i}. {result}")
            print(f"   Name: {name}")
            print(f"   URL: {url}")
            print()
    
    # Test Hukut
    print("\n🔍 Testing HUKUT scraper...")
    hukut_products = await async_scrape_hukut("laptop")
    print(f"Found {len(hukut_products)} Hukut products")
    
    if hukut_products:
        print("\nTesting first 5 Hukut URLs:")
        for i, product in enumerate(hukut_products[:5], 1):
            url = product['product_url']
            name = product['product_name'][:50]
            result = test_url(url, 'hukut')
            print(f"{i}. {result}")
            print(f"   Name: {name}")
            print(f"   URL: {url}")
            print()
    
    print("=" * 80)
    print("VERIFICATION COMPLETE")
    print("=" * 80)


if __name__ == "__main__":
    asyncio.run(main())
