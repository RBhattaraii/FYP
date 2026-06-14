import requests
import json

def test_wix_api():
    url = "https://www.thebetterappliances.com/_api/search-services-sitesearch/v1/search"
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
        "Content-Type": "application/json",
        "Accept": "*/*"
    }
    payload = {
        "documentType": "public/stores/products",
        "query": "tv",
        "paging": {"skip": 0, "limit": 12},
        "ordering": {"ordering": []},
        "includeSeoHidden": False,
        "facets": {
            "clauses": [
                {"aggregation": {"name": "discountedPriceNumeric", "aggregation": "MIN"}},
                {"aggregation": {"name": "discountedPriceNumeric", "aggregation": "MAX"}},
                {"term": {"name": "collections", "limit": 999}}
            ]
        },
        "language": "en",
        "properties": [{"name": "result-format", "value": "store-front"}],
        "fuzzy": True,
        "fields": ["description", "title", "id", "currency", "discountedPrice", "inStock"]
    }
    
    response = requests.post(url, headers=headers, json=payload)
    print(f"Status: {response.status_code}")
    
    if response.status_code == 200:
        data = response.json()
        print("Success! Keys in response:", data.keys())
        if 'documents' in data:
            docs = data['documents']
            print(f"Found {len(docs)} documents")
            if docs:
                first = docs[0]
                print(f"First doc keys: {first.keys()}")
                print(json.dumps(first, indent=2))
    else:
        print(response.text[:500])

if __name__ == "__main__":
    test_wix_api()
