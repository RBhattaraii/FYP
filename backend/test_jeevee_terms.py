import requests
import time

terms = ['a', 'b', 'c', 'electronics', 'home', 'gaming', 'office', 'baby', 'beauty', 'sports']
headers = {'User-Agent': 'Mozilla/5.0', 'Origin': 'https://www.jeevee.com'}
for term in terms:
    r = requests.get('https://search.jeevee.com/search-test-updated',
        params={'search': term, 'item_per_page': 100, 'page': 1, 'pagination': 'true', 'query': term},
        headers=headers, timeout=10)
    if r.status_code == 200:
        data = r.json()
        items = data.get('data', [])
        total = data.get('total_count', data.get('total', len(items)))
        print(f'Term "{term}": {len(items)} items (total: {total})')
    time.sleep(0.3)
