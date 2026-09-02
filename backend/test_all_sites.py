#!/usr/bin/env python3
"""
Test all websites to find working URLs and selectors
"""

import requests
from bs4 import BeautifulSoup
import time

def test_site(name, urls_to_test):
    print(f"\n🔍 TESTING {name.upper()}")
    print("=" * 40)
    
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'
    }
    
    for url in urls_to_test:
        try:
            print(f"📱 {url}")
            response = requests.get(url, headers=headers, timeout=15)
            print(f"   Status: {response.status_code}")
            
            if response.status_code == 200:
                soup = BeautifulSoup(response.content, 'html.parser')
                print(f"   Page size: {len(response.content):,} bytes")
                
                # Test common product selectors
                selectors = [
                    'div[class*="product"]',
                    'div[class*="item"]', 
                    'article',
                    '.product',
                    '.item-box',
                    'div[id*="product"]'
                ]
                
                found_products = False
                for sel in selectors:
                    try:
                        elements = soup.select(sel)
                        if elements and len(elements) > 5:  # Reasonable number
                            print(f"   ✅ {sel}: {len(elements)} elements")
                            # Check if elements have text content
                            text_elements = [e for e in elements if len(e.get_text(strip=True)) > 20]
                            if text_elements:
                                print(f"      → {len(text_elements)} with substantial text content")
                                found_products = True
                                break
                    except:
                        pass
                
                if not found_products:
                    print("   ❌ No product containers found")
                    
                # Check if redirect or error page
                title = soup.title.string if soup.title else ""
                if any(word in title.lower() for word in ['error', '404', 'not found', 'maintenance']):
                    print(f"   ⚠️  Error page detected: {title}")
                    
            elif response.status_code == 404:
                print("   ❌ 404 Not Found")
            else:
                print(f"   ❌ HTTP {response.status_code}")
                
        except Exception as e:
            print(f"   ❌ Error: {str(e)[:50]}...")
            
        time.sleep(1)

def main():
    # Test different URL patterns for each site
    sites_to_test = {
        'Jeevee': [
            'https://jeevee.com',
            'https://www.jeevee.com',
            'https://jeevee.com.np',
            'https://www.jeevee.com.np',
            'https://jeevee.com.np/products',
            'https://jeevee.com.np/shop'
        ],
        'CGDigital': [
            'https://cgdigital.com.np',
            'https://cgdigital.com.np/products',
            'https://cgdigital.com.np/shop',
            'https://cgdigital.com.np/search?q=laptop'
        ],
        'Hukut': [
            'https://hukut.com',
            'https://hukut.com/products',
            'https://hukut.com/shop',
            'https://hukut.com/search?q=phone'
        ],
        'Oliz': [
            'https://olizstore.com',
            'https://olizstore.com/products',
            'https://olizstore.com/shop',
            'https://olizstore.com/search?q=phone'
        ],
        'Better': [
            'https://better.com.np',
            'https://www.better.com.np',
            'https://better.com.np/products',
            'https://better.com.np/shop'
        ],
        'HardwarePasal': [
            'https://hardwarepasal.com',
            'https://hardwarepasal.com/search?q=motherboard'  # We know this works
        ]
    }
    
    for site_name, urls in sites_to_test.items():
        test_site(site_name, urls)
    
    print(f"\n💡 ANALYSIS COMPLETE")
    print("Update scrapers with working URLs and selectors found above")

if __name__ == "__main__":
    main()