import requests
import json

try:
    # Test the search endpoint
    print("Testing search endpoint...")
    r = requests.get('http://localhost:8000/products/search?q=laptop', timeout=30)
    print(f'Status: {r.status_code}')
    
    if r.status_code == 200:
        data = r.json()
        
        # Check Jeevee products
        jeevee = [p for p in data.get('products', []) if p.get('platform') == 'jeevee'][:5]
        print(f'\n=== JEEVEE PRODUCTS ({len(jeevee)} found) ===')
        for p in jeevee:
            print(f"Name: {p['product_name']}")
            print(f"URL: {p['product_url']}")
            print()
        
        # Check Oliz products
        oliz = [p for p in data.get('products', []) if p.get('platform') == 'oliz_store'][:5]
        print(f'\n=== OLIZ PRODUCTS ({len(oliz)} found) ===')
        for p in oliz:
            print(f"Name: {p['product_name']}")
            print(f"URL: {p['product_url']}")
            print()
        
        # Check Hukut products
        hukut = [p for p in data.get('products', []) if p.get('platform') == 'hukut_store'][:5]
        print(f'\n=== HUKUT PRODUCTS ({len(hukut)} found) ===')
        for p in hukut:
            print(f"Name: {p['product_name']}")
            print(f"URL: {p['product_url']}")
            print()
            
except Exception as e:
    print(f"Error: {e}")
