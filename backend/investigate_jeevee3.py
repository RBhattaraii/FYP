"""
Final Jeevee URL test:
The real issue is some products return HTTP 404 because the slug is wrong.
Let's try using JUST the template_id without the slug, since Jeevee
might route by ID alone.
"""
import requests
import re

searches = ['samsung', 'laptop', 'iphone', 'redmi note 14']
for search in searches:
    url = f'https://search.jeevee.com/search-test-updated?search={search}&item_per_page=2&page=1'
    r = requests.get(url)
    data = r.json().get('data', [])
    if not data:
        continue
    
    item = data[0]
    product_name = item.get('label', '')
    template_id = item.get('product_template_id', '')
    product_id = item.get('product_id', '')
    
    slug_from_name = re.sub(r'[^a-z0-9]+', '-', product_name.lower()).strip('-')
    
    # Pattern A: slug-template_id (current)
    url_a = f"https://www.jeevee.com/products/{slug_from_name}-{template_id}"
    # Pattern B: Just template_id
    url_b = f"https://www.jeevee.com/products/{template_id}"
    # Pattern C: Just product_id
    url_c = f"https://www.jeevee.com/products/{product_id}"
    # Pattern D: slug-product_id
    url_d = f"https://www.jeevee.com/products/{slug_from_name}-{product_id}"
    
    print(f"\n=== {product_name[:50]} ===")
    for label, u in [('A:slug-tmpl', url_a), ('B:tmpl_only', url_b), ('C:pid_only', url_c), ('D:slug-pid', url_d)]:
        r2 = requests.get(u, timeout=10, allow_redirects=True)
        is_404 = r2.status_code == 404 or 'page not found' in r2.text.lower()[:3000] or 'product not found' in r2.text.lower()[:3000]
        status = '404' if is_404 else 'OK '
        print(f"  [{status}] {label}: {u}")
