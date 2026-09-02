#!/usr/bin/env python3
"""
DIAGNOSE SCRAPING ISSUES
Test individual platforms to see what's working and what's not
"""

import requests
from bs4 import BeautifulSoup
import time

def test_jeevee():
    """Test Jeevee connection and parsing"""
    print("🔍 TESTING JEEVEE...")
    
    try:
        url = "https://jeevee.com.np/search?q=laptop"
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
        }
        
        response = requests.get(url, timeout=10, headers=headers)
        print(f"   Status Code: {response.status_code}")
        print(f"   Content Length: {len(response.content)}")
        
        if response.status_code == 200:
            soup = BeautifulSoup(response.content, 'html.parser')
            
            # Look for product indicators
            selectors = ['div.product-item', 'div.product-card', 'article.product', '.product', '.item']
            
            for selector in selectors:
                items = soup.select(selector)
                if items:
                    print(f"   Found {len(items)} items with selector '{selector}'")
                    
                    # Check first item content
                    if items:
                        first_item = items[0]
                        title_elem = first_item.find(['h3', 'h4', 'h5']) or first_item.select_one('.title')
                        price_elem = first_item.select_one('.price') or first_item.select_one('[class*="price"]')
                        
                        print(f"   Sample title element: {title_elem}")
                        print(f"   Sample price element: {price_elem}")
                    break
            else:
                print("   ❌ No product elements found")
                # Print some page content for debugging
                print(f"   Page title: {soup.title.get_text() if soup.title else 'No title'}")
                print(f"   Sample content: {str(soup)[:200]}...")
        
    except Exception as e:
        print(f"   ❌ Error: {e}")

def test_hukut():
    """Test Hukut connection"""
    print("\\n🔍 TESTING HUKUT...")
    
    try:
        url = "https://hukut.com/search?q=phone"
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
        }
        
        response = requests.get(url, timeout=10, headers=headers)
        print(f"   Status Code: {response.status_code}")
        print(f"   Content Length: {len(response.content)}")
        
        if response.status_code == 200:
            soup = BeautifulSoup(response.content, 'html.parser')
            
            # Look for product indicators
            selectors = ['div.product', 'article.product', 'div.product-item', '.item']
            
            for selector in selectors:
                items = soup.select(selector)
                if items:
                    print(f"   Found {len(items)} items with selector '{selector}'")
                    break
            else:
                print("   ❌ No product elements found")
                print(f"   Page title: {soup.title.get_text() if soup.title else 'No title'}")
        
    except Exception as e:
        print(f"   ❌ Error: {e}")

def test_cgdigital():
    """Test CGDigital connection"""
    print("\\n🔍 TESTING CGDIGITAL...")
    
    try:
        url = "https://cgdigital.com.np/search?q=laptop"
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
        }
        
        response = requests.get(url, timeout=10, headers=headers)
        print(f"   Status Code: {response.status_code}")
        print(f"   Content Length: {len(response.content)}")
        
        if response.status_code == 200:
            soup = BeautifulSoup(response.content, 'html.parser')
            
            # Look for product indicators
            selectors = ['div.product-item', 'div.product-card', 'article.product']
            
            for selector in selectors:
                items = soup.select(selector)
                if items:
                    print(f"   Found {len(items)} items with selector '{selector}'")
                    break
            else:
                print("   ❌ No product elements found")
                print(f"   Page title: {soup.title.get_text() if soup.title else 'No title'}")
        
    except Exception as e:
        print(f"   ❌ Error: {e}")

def main():
    print("🔧 SCRAPING DIAGNOSIS REPORT")
    print("=" * 50)
    
    test_jeevee()
    test_hukut()
    test_cgdigital()
    
    print("\\n📊 DIAGNOSIS COMPLETE")
    print("Check the results above to see which platforms are accessible")

if __name__ == "__main__":
    main()