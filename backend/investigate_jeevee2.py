"""
Test which Jeevee URL format works reliably in a browser.
Since Jeevee is an SPA, server-side HTML may not contain product data.
We need to test if the URL loads the product correctly in a browser.
"""
import requests
import re

# Test with multiple products to find pattern
searches = ['redmi note 14', 'samsung', 'iphone', 'laptop']
for search in searches:
    url = f'https://search.jeevee.com/search-test-updated?search={search}&item_per_page=2&page=1'
    r = requests.get(url)
    data = r.json().get('data', [])
    if not data:
        print(f"No results for '{search}'")
        continue
    
    item = data[0]
    product_name = item.get('label', '')
    template_id = item.get('product_template_id', '')
    product_id = item.get('product_id', '')
    slug = item.get('seo_details', {}).get('slug', '')
    
    slug_from_name = re.sub(r'[^a-z0-9]+', '-', product_name.lower()).strip('-')
    
    # URL format 1: /products/{slug}-{template_id}
    url1 = f"https://www.jeevee.com/products/{slug_from_name}-{template_id}"
    
    # Check if page loads actual product content (look for price or product name in HTML)
    r1 = requests.get(url1, timeout=10)
    
    # In an SPA, the initial HTML has very little. Let's look for key indicators:
    has_product = product_name.split()[0].lower() in r1.text.lower() if r1.status_code == 200 else False
    has_404_text = 'page not found' in r1.text.lower() or 'product not found' in r1.text.lower() or '404' in r1.text[:500]
    has_redirect_script = 'window.location' in r1.text.lower() or 'redirect' in r1.text.lower()
    
    print(f"\n[{search}] {product_name[:40]}")
    print(f"  URL: {url1}")
    print(f"  HTTP: {r1.status_code} | Has product content: {has_product} | Has 404 text: {has_404_text}")
    print(f"  HTML length: {len(r1.text)} chars")
    
    # Check if it's using Next.js or similar
    if '__NEXT_DATA__' in r1.text:
        import json as j
        try:
            next_data = r1.text.split('__NEXT_DATA__')[1]
            next_data = next_data.split('>')[1].split('</script>')[0]
            nd = j.loads(next_data)
            page_props = nd.get('props', {}).get('pageProps', {})
            if 'product' in str(page_props).lower()[:200]:
                print(f"  >>> Next.js SSR - has product data in pageProps!")
            elif 'notFound' in str(nd):
                print(f"  >>> Next.js SSR - page marked as NOT FOUND!")
            else:
                print(f"  >>> Next.js SSR - pageProps keys: {list(page_props.keys())[:5]}")
        except:
            print(f"  >>> Has __NEXT_DATA__ but couldn't parse")
    
    # Also check if there's a meta og:url that reveals the canonical URL format
    og_url = re.findall(r'property="og:url"\s+content="([^"]+)"', r1.text)
    if og_url:
        print(f"  >>> og:url: {og_url[0]}")
    
    canonical = re.findall(r'rel="canonical"\s+href="([^"]+)"', r1.text)
    if canonical:
        print(f"  >>> canonical: {canonical[0]}")
