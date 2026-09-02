import requests

urls = [
    "https://www.olizstore.com/product/iphone-17-pro-max",
    "https://hukut.com/product/apple-iphone-17-pro-max",
    "https://www.jeevee.com/products/pepper-blue-phonecase-iphone-58820",
    "https://cgdigital.com.np/product/4728"
]

headers = {"User-Agent": "Mozilla/5.0"}
for url in urls:
    try:
        r = requests.head(url, headers=headers, allow_redirects=True, timeout=5)
        print(f"{r.status_code} - {url}")
    except Exception as e:
        print(f"ERROR - {url}: {e}")
