#!/usr/bin/env python3
"""
Test the working base URLs to extract products directly
"""

import requests
from bs4 import BeautifulSoup
import time

def test_direct_scraping():
    """Test scraping products from the base URLs that worked"""
    
    working_sites = [
        ("Jeevee", "https://jeevee.com", 'div[class*="product"]'),
        ("Oliz", "https://olizstore.com/products", 'div[class*="product"]'),
        ("Hukut", "https://hukut.com", 'div[class*="item"]'),
        ("HardwarePasal", "https://hardwarepasal.com", 'div[class*="product"]')
    ]
    
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'
    }
    
    for site_name, url, selector in working_sites:
        print(f"\n🔍 TESTING {site_name.upper()}: {url}")
        print("=" * 60)
        
        try:
            response = requests.get(url, headers=headers, timeout=20)
            
            if response.status_code == 200:
                soup = BeautifulSoup(response.content, 'html.parser')
                elements = soup.select(selector)
                
                print(f"✅ Found {len(elements)} elements with selector: {selector}")
                
                products_found = 0
                for i, elem in enumerate(elements[:5]):  # Test first 5
                    try:
                        # Look for title, price, link
                        title_selectors = ['h3', 'h4', 'h2', '.title', '.product-title', '.product-name', 'a']
                        price_selectors = ['.price', '.product-price', '.cost', '.amount', '.cnit-product-price']
                        
                        title = ""
                        for title_sel in title_selectors:
                            title_elem = elem.select_one(title_sel)
                            if title_elem:
                                title = title_elem.get_text(strip=True)
                                if len(title) > 8:
                                    break
                        
                        price = ""
                        for price_sel in price_selectors:
                            price_elem = elem.select_one(price_sel)
                            if price_elem:
                                price = price_elem.get_text(strip=True)
                                if price and any(c.isdigit() for c in price):
                                    break
                        
                        link_elem = elem.select_one('a')
                        
                        if title and price and link_elem:
                            products_found += 1
                            print(f"   [{products_found}] Title: {title[:50]}...")
                            print(f"       Price: {price}")
                            print(f"       Link: {link_elem.get('href', '')[:50]}...")
                            
                    except Exception as e:
                        continue
                
                print(f"\n📊 RESULT: {products_found} valid products found from {len(elements)} elements")
                
                if products_found > 0:
                    print(f"✅ {site_name} SCRAPER SHOULD WORK!")
                else:
                    print(f"❌ {site_name} needs selector adjustment")
                    
            else:
                print(f"❌ HTTP {response.status_code}")
                
        except Exception as e:
            print(f"❌ Error: {e}")
            
        time.sleep(2)
        
    print(f"\n💡 RECOMMENDATION:")
    print("Use direct URL scraping instead of search URLs")
    print("Scrape from base pages first, then explore pagination")

if __name__ == "__main__":
    test_direct_scraping()