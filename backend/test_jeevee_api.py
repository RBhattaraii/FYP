import requests
import json

def test_jeevee_api():
    url = "https://search.jeevee.com/search-test-updated"
    params = {
        "search": "facewash",
        "item_per_page": 24,
        "page": 1,
        "pagination": "true",
        "query": "facewash"
    }
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
        "Accept": "application/json, text/plain, */*",
        "Origin": "https://www.jeevee.com",
        "Referer": "https://www.jeevee.com/"
    }
    
    response = requests.get(url, params=params, headers=headers, timeout=15)
    print(f"Status: {response.status_code}")
    
    if response.status_code == 200:
        data = response.json()
        print(f"Type: {type(data)}")
        if isinstance(data, dict):
            print(f"Keys: {data.keys()}")
            if 'data' in data:
                items = data['data']
                if isinstance(items, list):
                    print(f"Found {len(items)} products")
                    if items:
                        print(f"First item keys: {items[0].keys()}")
                        print(json.dumps(items[0], indent=2, default=str))
                elif isinstance(items, dict):
                    print(f"Data keys: {items.keys()}")
                    # Check if there's a nested products list
                    for k, v in items.items():
                        if isinstance(v, list) and len(v) > 0:
                            print(f"  {k}: list of {len(v)} items")
                            print(f"  First item keys: {v[0].keys()}")
                            print(json.dumps(v[0], indent=2, default=str))
                            break
            else:
                # Maybe it's a list at the top level
                print(json.dumps(data, indent=2, default=str)[:2000])
        elif isinstance(data, list):
            print(f"Found {len(data)} products (top-level list)")
            if data:
                print(f"First item keys: {data[0].keys()}")
                print(json.dumps(data[0], indent=2, default=str))
    else:
        print(response.text[:500])

if __name__ == "__main__":
    test_jeevee_api()
