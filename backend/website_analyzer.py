#!/usr/bin/env python3
"""
Website Structure Analyzer
Quickly analyze website HTML to find correct CSS selectors
"""

import requests
from bs4 import BeautifulSoup
import time
import random

def analyze_website(name, base_url, search_path=""):
    """Analyze website structure to find product selectors"""
    print(f"\n🔍 ANALYZING {name.upper()}")
    print("=" * 50)
    
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'
    }
    
    # Test main page first
    try:
        url = base_url if not search_path else f"{base_url}{search_path}"
        print(f"📱 Testing: {url}")
        
        response = requests.get(url, headers=headers, timeout=15)
        print(f"   Status: {response.status_code}")
        
        if response.status_code == 200:
            soup = BeautifulSoup(response.content, 'html.parser')
            
            # Look for common product container patterns
            potential_selectors = [
                'div[class*="product"]',
                'article[class*="product"]', 
                'div[class*="item"]',
                'div[class*="card"]',
                'div[class*="grid"]',
                '.product',
                '.item',
                '.card'
            ]
            
            print(f"   Page size: {len(response.content):,} bytes")
            print(f"   Title: {soup.title.string[:60] if soup.title else 'No title'}...")
            
            print(f"\n📦 PRODUCT CONTAINER ANALYSIS:")
            for selector in potential_selectors:
                try:
                    items = soup.select(selector)
                    if items:
                        print(f"   ✅ {selector:25}: {len(items)} elements")
                        
                        # Analyze first few items
                        for i, item in enumerate(items[:3]):
                            if item.get_text(strip=True):
                                text_preview = item.get_text(strip=True)[:100]
                                print(f"      [{i+1}] {text_preview}...")
                    else:
                        print(f"   ❌ {selector:25}: 0 elements")
                except:
                    print(f"   ⚠️  {selector:25}: selector error")
            
            # Look for common class patterns
            print(f"\n🏷️  COMMON CLASS PATTERNS:")
            all_classes = []
            for elem in soup.find_all(class_=True):
                if elem.get('class'):
                    all_classes.extend(elem.get('class'))
            
            # Find product-related classes
            product_classes = [cls for cls in set(all_classes) 
                             if any(word in cls.lower() for word in ['product', 'item', 'card', 'grid'])]
            
            for cls in sorted(product_classes)[:10]:
                count = len(soup.select(f'.{cls}'))
                print(f"   .{cls:30}: {count} elements")
            
            # Check if it's a search results page or main page
            if 'search' in url.lower() or 'query' in url.lower():
                print(f"\n🔍 SEARCH PAGE DETECTED")
            else:
                print(f"\n🏠 MAIN PAGE - Try search URLs:")
                search_suggestions = [
                    f"{base_url}/search?q=phone",
                    f"{base_url}/products?search=phone", 
                    f"{base_url}/shop?query=phone"
                ]
                for suggestion in search_suggestions:
                    print(f"   • {suggestion}")
                    
        else:
            print(f"   ❌ HTTP {response.status_code} - Cannot access website")
            
    except Exception as e:
        print(f"   ❌ Error: {str(e)[:100]}...")

def main():
    print("🔍 WEBSITE STRUCTURE ANALYZER")
    print("Analyzing current website layouts to fix scrapers...")
    print("=" * 60)
    
    websites = [
        ("Jeevee", "https://www.jeevee.com", "/search?q=phone"),
        ("CGDigital", "https://cgdigital.com.np", "/search?q=laptop"),
        ("Hukut", "https://hukut.com", "/search?q=phone"),
        ("Oliz", "https://olizstore.com", "/search?q=shirt"),
        ("Better", "https://better.com.np", "/search?q=electronics"),
        ("HardwarePasal", "https://hardwarepasal.com", "/search?q=motherboard")
    ]
    
    for name, base_url, search_path in websites:
        try:
            analyze_website(name, base_url, search_path)
            time.sleep(2)  # Brief delay between requests
        except Exception as e:
            print(f"\n❌ Failed to analyze {name}: {e}")
    
    print(f"\n💡 NEXT STEPS:")
    print("   1. Review the analysis above")
    print("   2. Update CSS selectors in scrapers based on findings")
    print("   3. Test individual scrapers with correct selectors")

if __name__ == "__main__":
    main()