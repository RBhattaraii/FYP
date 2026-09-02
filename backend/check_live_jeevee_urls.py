"""
Check the actual Jeevee URLs from the live search that just ran
"""
import requests
import json

try:
    # The backend just ran a search for "laptop" - check what URLs it returned
    response = requests.get('http://localhost:8000/products/search?q=laptop', timeout=10)
    
    if response.status_code == 200:
        data = response.json()
        products = data.get('products', [])
        
        # Filter Jeevee products
        jeevee_products = [p for p in products if p.get('platform') == 'jeevee']
        
        print(f"Found {len(jeevee_products)} Jeevee products from live search")
        print("\n" + "="*80)
        print("Testing first 5 Jeevee URLs from LIVE search:")
        print("="*80)
        
        for i, product in enumerate(jeevee_products[:5], 1):
            url = product['product_url']
            name = product['product_name'][:60]
            
            # Test the URL
            try:
                test_response = requests.head(url, timeout=5, allow_redirects=True)
                status = test_response.status_code
                
                if status == 200:
                    result = "✅ WORKING"
                elif status == 404:
                    result = "❌ 404 NOT FOUND"
                elif status in [301, 302, 303]:
                    result = f"✅ REDIRECT ({status})"
                else:
                    result = f"⚠️ Status {status}"
                    
                print(f"\n{i}. {result}")
                print(f"   Name: {name}")
                print(f"   URL: {url}")
                if status in [301, 302, 303]:
                    print(f"   Final: {test_response.url}")
                    
            except Exception as e:
                print(f"\n{i}. ❌ ERROR")
                print(f"   Name: {name}")
                print(f"   URL: {url}")
                print(f"   Error: {str(e)[:50]}")
        
        print("\n" + "="*80)
        
    else:
        print(f"Error: Backend returned status {response.status_code}")
        
except Exception as e:
    print(f"Error: {e}")
