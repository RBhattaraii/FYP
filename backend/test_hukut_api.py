import requests
import json

def test_api():
    url = "https://hukut.com/api-server/v1/product/list-elastic"
    headers = {
        "User-Agent": "Mozilla/5.0",
        "Content-Type": "application/json"
    }
    
    payload = {"searchText":"macbook","pagination":{"limit":20,"offset":0}}
    res = requests.post(url, headers=headers, json=payload)
    
    data = res.json()
    rows = data.get('data', {}).get('rows', [])
    print(f"Found {len(rows)} products")
    if rows:
        p = rows[0]
        print("Keys:", p.keys())
        print(f"Name: {p.get('name')}")
        print(f"Slug: {p.get('slug')}")
        print(f"Selling Price: {p.get('sellingPrice')}")
        print(f"Marked Price: {p.get('markedPrice')}")
        print(f"Image: {p.get('image')}")
        
if __name__ == "__main__":
    test_api()
