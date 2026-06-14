import requests
import json

def test_api():
    url = "https://www.cgdigital.com.np/api/web-search?keywords=tv"
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
        "Accept": "application/json, text/plain, */*"
    }
    
    response = requests.get(url, headers=headers)
    print(f"Status: {response.status_code}")
    
    try:
        data = response.json()
        if 'data' in data and 'products' in data['data']:
            products = data['data']['products']
            print(f"Found {len(products)} products for 'tv'")
            if products:
                first = products[0]
                print(f"Name: {first.get('name')}")
                print(f"Price: {first.get('price')}")
                print(f"Discount Price: {first.get('discount_price')}")
                print(f"Discount %: {first.get('discount_percent')}")
                print(f"Image: {first.get('featured_image')}")
                print(f"Link: {first.get('page_link')}")
                print(f"Brand: {first.get('brand')}")
    except Exception as e:
        print(f"Failed to parse JSON: {e}")

if __name__ == "__main__":
    test_api()
