import requests

url = "https://cgdigital.com.np/product/4728"
try:
    res = requests.get(url, allow_redirects=True, headers={'User-Agent': 'Mozilla/5.0'})
    print(f"CG URL status: {res.status_code}")
except Exception as e:
    print(f"Error: {e}")
