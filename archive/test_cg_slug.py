import requests

url = "https://cgdigital.com.np/api/web-search?keywords=tv"
headers = {
    "User-Agent": "Mozilla/5.0",
    "Origin": "https://cgdigital.com.np"
}
res = requests.get(url, headers=headers)
data = res.json()
for product in data['data']['products'][:3]:
    print(product['name'])
    print(f"ID: {product['id']}, Slug: {product.get('slug')}")
