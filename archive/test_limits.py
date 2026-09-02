import asyncio
import requests

def test_jeevee():
    url = "https://search.jeevee.com/search-test-updated"
    params = {
        "search": "iphone",
        "item_per_page": 100,
        "page": 1,
        "pagination": "true",
        "query": "iphone"
    }
    headers = {"User-Agent": "Mozilla/5.0"}
    res = requests.get(url, params=params, headers=headers)
    print("Jeevee length:", len(res.json().get('data', [])))

def test_cg():
    url = "https://cgdigital.com.np/api/web-search?keywords=tv&limit=100&per_page=100"
    headers = {"User-Agent": "Mozilla/5.0"}
    res = requests.get(url, headers=headers)
    print("CG length:", len(res.json().get('data', {}).get('products', [])))

if __name__ == "__main__":
    test_jeevee()
    test_cg()
