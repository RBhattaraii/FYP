#!/usr/bin/env python3
"""
Test HardwarePasal structure since it's working
"""

import requests
from bs4 import BeautifulSoup

def test_hardwarepasal():
    url = 'https://hardwarepasal.com/search?q=motherboard'
    headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'}
    
    try:
        response = requests.get(url, headers=headers, timeout=15)
        
        if response.status_code == 200:
            soup = BeautifulSoup(response.content, 'html.parser')
            
            # Test different selectors
            selectors_to_test = [
                'div.product',
                'div[class*="product"]',
                '.cnit-product-price',
                'div.product-item',
                'article'
            ]
            
            for selector in selectors_to_test:
                try:
                    elements = soup.select(selector)
                    print(f"{selector}: {len(elements)} elements")
                    
                    if elements and len(elements) > 10:  # Looks promising
                        print(f"  ANALYZING TOP 3 ELEMENTS:")
                        for i, elem in enumerate(elements[:3]):
                            text = elem.get_text(strip=True)[:100]
                            classes = elem.get('class', [])
                            print(f"    [{i+1}] Classes: {classes}")
                            print(f"    [{i+1}] Text: {text}...")
                            
                            # Look for links and images
                            link = elem.select_one('a')
                            img = elem.select_one('img')
                            
                            if link:
                                print(f"    [{i+1}] Link: {link.get('href', '')[:50]}...")
                            if img:
                                print(f"    [{i+1}] Img: {img.get('src', '')[:50]}...")
                            
                        break  # Found good selector
                except Exception as e:
                    print(f"{selector}: Error - {e}")
                    
        else:
            print(f'HTTP Error: {response.status_code}')
            
    except Exception as e:
        print(f'Request Error: {e}')

if __name__ == "__main__":
    test_hardwarepasal()