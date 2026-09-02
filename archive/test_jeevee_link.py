import requests

url = "https://www.jeevee.com/products/pepper-blue-phonecase-iphone-58820"
try:
    res = requests.get(url, allow_redirects=True, headers={'User-Agent': 'Mozilla/5.0'})
    print(f"Jeevee URL status: {res.status_code}")
except Exception as e:
    print(f"Error: {e}")
