import requests
import json

print("\n🔍 Testing search with fresh Jeevee products...\n")

response = requests.get("http://localhost:8000/products/search?q=laptop", timeout=60)
data = response.json()

print(f"✅ Search complete!")
print(f"   Total products: {data['results_count']}")
print(f"   Platforms: {len(data['tier1_platforms'])}")
print(f"   Status: {data['message']}\n")

# Find Jeevee products
jeevee_products = [p for p in data['results'] if p['store_name'] == 'Jeevee']
print(f"📦 Jeevee products found: {len(jeevee_products)}\n")

if jeevee_products:
    print("Sample Jeevee products with URLs:\n")
    for i, p in enumerate(jeevee_products[:5], 1):
        print(f"{i}. {p['title'][:60]}")
        print(f"   Price: Rs {p['price']:,.0f}")
        print(f"   URL: {p['product_url']}")
        
        # Test the URL
        try:
            test_resp = requests.head(p['product_url'], timeout=5, allow_redirects=True)
            if test_resp.status_code == 200:
                print(f"   ✅ Link works! (200 OK)")
            else:
                print(f"   ❌ Link broken ({test_resp.status_code})")
        except Exception as e:
            print(f"   ❌ Link error: {e}")
        print()
else:
    print("❌ No Jeevee products in search results")
    print("   This might mean Jeevee scraper failed or returned no results")
