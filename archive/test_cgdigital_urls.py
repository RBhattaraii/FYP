import requests, json

headers = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36",
    "Accept": "application/json, text/plain, */*",
    "Origin": "https://cgdigital.com.np",
    "Referer": "https://cgdigital.com.np/search/tv"
}

url = "https://www.cgdigital.com.np/api/web-search?keywords=tv&page=1"
res = requests.get(url, headers=headers, timeout=15)
print("Status:", res.status_code)

if res.status_code == 200:
    data = res.json()
    items = data.get('data', {}).get('products', [])
    print(f"Products: {len(items)}")
    
    if items:
        # Print first item fully to see all available fields
        first = items[0]
        print("\nFirst item keys:", list(first.keys()))
        print(json.dumps(first, indent=2, default=str)[:2000])
        
        # Check slug field
        for item in items[:3]:
            slug = item.get('slug', '')
            pid = item.get('id', '')
            name = item.get('name', '')
            print(f"\n  Name: {name[:50]}")
            print(f"  ID: {pid}")
            print(f"  Slug: {slug}")
            
            # Test both URL formats
            url1 = f"https://cgdigital.com.np/product/{pid}"
            url2 = f"https://cgdigital.com.np/product/{slug}" if slug else None
            
            r1 = requests.head(url1, headers={"User-Agent": headers["User-Agent"]}, timeout=5, allow_redirects=True)
            print(f"  URL by ID: {url1} -> {r1.status_code}")
            
            if url2:
                r2 = requests.head(url2, headers={"User-Agent": headers["User-Agent"]}, timeout=5, allow_redirects=True)
                print(f"  URL by slug: {url2} -> {r2.status_code}")
