import requests
import json

url = "https://search.jeevee.com/search-test-updated"
params = {
    "search": "ultima rapid 75w pd qc car charger",
    "item_per_page": 5,
    "page": 1,
    "pagination": "true"
}

headers = {"User-Agent": "Mozilla/5.0"}
r = requests.get(url, params=params, headers=headers)
data = r.json()

if 'data' in data and data['data']:
    item = data['data'][0]
    print(json.dumps({
        "label": item.get('label'),
        "product_id": item.get('product_id'),
        "product_template_id": item.get('product_template_id'),
        "seo_details": item.get('seo_details')
    }, indent=2))
