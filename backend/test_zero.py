import json

with open('oliz_next_data.json', 'r', encoding='utf-8') as f:
    data = json.load(f)

response = data['props']['pageProps']['response']
zero_prices = [p for p in response if not p.get('price')]

print(f"Total items: {len(response)}")
print(f"Items with no price or price=0: {len(zero_prices)}")

if zero_prices:
    p = zero_prices[0]
    print(f"Example: {p.get('name')}")
    print(f"  Price: {p.get('price')}")
    print(f"  Min Price: {p.get('min_price')}")
    print(f"  Max Price: {p.get('max_price')}")
