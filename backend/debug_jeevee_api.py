import requests
import json

# Call Jeevee search API
url = "https://search.jeevee.com/search-test-updated"
params = {
    "search": "laptop",
    "item_per_page": 5,
    "page": 1,
    "pagination": "true",
    "query": "laptop"
}

headers = {
    "User-Agent": "Mozilla/5.0",
    "Accept": "application/json",
    "Origin": "https://www.jeevee.com",
    "Referer": "https://www.jeevee.com/products/search?query=laptop"
}

response = requests.get(url, params=params, headers=headers, timeout=15)
data = response.json()

print("\n🔍 Jeevee API Response Structure:\n")
print(f"Total products: {len(data.get('data', []))}\n")

if data.get('data'):
    print("First product structure:")
    product = data['data'][0]
    print(json.dumps(product, indent=2))
    
    print("\n📋 Key fields:")
    print(f"  - product_id: {product.get('product_id')}")
    print(f"  - product_template_id: {product.get('product_template_id')}")
    print(f"  - label: {product.get('label')}")
    
    # Check for slug or seo_details
    if 'seo_details' in product:
        print(f"\n  ✅ seo_details found:")
        print(json.dumps(product['seo_details'], indent=4))
    
    # Current URL construction
    template_id = product.get('product_template_id')
    current_url = f"https://www.jeevee.com/products/{template_id}"
    print(f"\n📌 Current URL: {current_url}")
    
    # Test it
    test_resp = requests.head(current_url, timeout=5, allow_redirects=True)
    print(f"  Status: {test_resp.status_code}")
