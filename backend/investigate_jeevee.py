"""
Comprehensive Jeevee URL investigation.
Try every possible URL format to find what actually works.
"""
import requests
import re
import json

# Get a real product from Jeevee search API
url = 'https://search.jeevee.com/search-test-updated?search=redmi+note+14&item_per_page=3&page=1'
r = requests.get(url)
data = r.json().get('data', [])

if not data:
    print("No data from search API!")
    exit()

item = data[0]
print("=" * 60)
print("FULL RAW API RESPONSE FOR FIRST ITEM:")
print("=" * 60)
print(json.dumps(item, indent=2, default=str))
print("=" * 60)

product_name = item.get('label', '')
product_id = item.get('product_id', '')
template_id = item.get('product_template_id', '')
slug = item.get('seo_details', {}).get('slug', '')

slug_from_name = re.sub(r'[^a-z0-9]+', '-', product_name.lower()).strip('-')

print(f"\nProduct: {product_name}")
print(f"product_id: {product_id}")
print(f"template_id: {template_id}")
print(f"slug: '{slug}'")
print(f"slug_from_name: '{slug_from_name}'")

# Try every possible URL pattern
patterns = [
    f"https://www.jeevee.com/products/{slug_from_name}-{template_id}",
    f"https://www.jeevee.com/products/{slug_from_name}-{product_id}",
    f"https://www.jeevee.com/product/{slug_from_name}-{template_id}",
    f"https://www.jeevee.com/product/{slug_from_name}-{product_id}",
    f"https://www.jeevee.com/products/{slug_from_name}",
    f"https://www.jeevee.com/product/{slug_from_name}",
    f"https://www.jeevee.com/products/{template_id}",
    f"https://www.jeevee.com/product/{template_id}",
    f"https://www.jeevee.com/products/{product_id}",
    f"https://www.jeevee.com/product/{product_id}",
    f"https://www.jeevee.com/p/{template_id}",
    f"https://www.jeevee.com/p/{product_id}",
]

if slug:
    patterns.insert(0, f"https://www.jeevee.com/products/{slug}-{template_id}")
    patterns.insert(0, f"https://www.jeevee.com/products/{slug}")

print("\n" + "=" * 60)
print("TESTING URL PATTERNS:")
print("=" * 60)

for pattern_url in patterns:
    try:
        res = requests.get(pattern_url, allow_redirects=True, timeout=10)
        is_404 = 'not found' in res.text.lower()[:2000] or 'page not found' in res.text.lower()[:2000]
        final_url = res.url
        status = "SOFT 404" if is_404 else "VALID!"
        redirect = f" -> {final_url}" if final_url != pattern_url else ""
        print(f"  [{res.status_code}] [{status}] {pattern_url}{redirect}")
    except Exception as e:
        print(f"  [ERR] {pattern_url}: {e}")

# Also try the Jeevee main website to find real product links
print("\n" + "=" * 60)
print("SEARCHING JEEVEE WEBSITE FOR REAL PRODUCT LINKS:")
print("=" * 60)
try:
    r2 = requests.get(f"https://www.jeevee.com/products/search?query=redmi+note+14", timeout=10)
    # Find all product links in the HTML
    links = re.findall(r'href=["\']([^"\']*(?:product|item)[^"\']*)["\']', r2.text, re.IGNORECASE)
    seen = set()
    for link in links:
        if link not in seen and '/product' in link.lower():
            seen.add(link)
            print(f"  {link}")
            if len(seen) >= 15:
                break
except Exception as e:
    print(f"  Error: {e}")
