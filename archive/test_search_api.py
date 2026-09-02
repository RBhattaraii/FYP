import requests, json

r = requests.get('http://localhost:8000/products/search?q=iphone', timeout=60)
data = r.json()
print('Status:', r.status_code)
print('Results count:', data.get('results_count'))
print('Is complete:', data.get('is_complete'))
print('Tier:', data.get('tier'))
print('Request ID:', data.get('request_id'))

results = data.get('results', [])
print(f'\nFirst 10 results (sorted by relevance):')
for i, p in enumerate(results[:10]):
    title = p['title'][:55]
    store = p['store_name']
    price = p['price']
    print(f"  {i+1:2d}. [{store:15s}] {title:55s} Rs.{price}")

if len(results) > 10:
    print(f'\nLast 5 results:')
    for p in results[-5:]:
        title = p['title'][:55]
        store = p['store_name']
        price = p['price']
        print(f"      [{store:15s}] {title:55s} Rs.{price}")

print(f'\nTotal: {len(results)} results')
