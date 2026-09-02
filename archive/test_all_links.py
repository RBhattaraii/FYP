import requests

r = requests.get('http://localhost:8000/products/search?q=iphone', timeout=60)
data = r.json()
results = data.get('results', [])

print(f"Testing URLs for {len(results)} products:")
tested_platforms = set()
for p in results:
    if p['store_name'] in tested_platforms:
        continue
    url = p['product_url']
    store = p['store_name']
    
    print(f"\nTesting {store}: {url}")
    try:
        res = requests.head(url, headers={"User-Agent": "Mozilla/5.0"}, allow_redirects=True, timeout=5)
        print(f"[{store}] Status: {res.status_code}")
    except Exception as e:
        print(f"[{store}] ERROR: {e}")
        
    tested_platforms.add(store)
