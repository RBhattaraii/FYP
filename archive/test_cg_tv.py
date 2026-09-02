import requests

url = "https://cgdigital.com.np/api/web-search?keywords=tv"
headers = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64)",
    "Accept": "application/json, text/plain, */*",
    "Origin": "https://cgdigital.com.np",
    "Referer": "https://cgdigital.com.np/search/tv"
}

try:
    res = requests.get(url, headers=headers)
    print(f"Status TV: {res.status_code}")
    print("TV products:", len(res.json().get('data', {}).get('products', [])))
    
    url2 = "https://cgdigital.com.np/api/web-search?keywords=refrigerator"
    res2 = requests.get(url2, headers=headers)
    print("Fridge products:", len(res2.json().get('data', {}).get('products', [])))
except Exception as e:
    print(e)
