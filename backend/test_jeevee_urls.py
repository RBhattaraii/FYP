import requests
import json
import re

def get_jeevee_url(product_name, product_template_id, slug=""):
    if slug:
        return f"https://www.jeevee.com/products/{slug}-{product_template_id}"
    slug_from_name = re.sub(r'[^a-z0-9]+', '-', product_name.lower()).strip('-')
    return f"https://www.jeevee.com/products/{slug_from_name}-{product_template_id}"

url = 'https://search.jeevee.com/search-test-updated?search=samsung&item_per_page=5&page=1'
r = requests.get(url)
data = r.json().get('data', [])

for item in data:
    slug = item.get('seo_details', {}).get('slug', '')
    product_name = item.get('label')
    tid = item.get('product_template_id')
    
    print('Label:', product_name)
    print('Template:', tid)
    print('SEO slug:', slug)
    
    url = get_jeevee_url(product_name, tid, slug)
    print('URL from scraper:', url)
    
    # Let's see if this URL works
    res = requests.get(url, allow_redirects=False)
    print('HTTP Status:', res.status_code)
    if 'not found' in res.text.lower() or '404' in res.text:
        print('PAGE IS A SOFT 404!')
    else:
        print('PAGE IS VALID!')
    print('-'*40)
