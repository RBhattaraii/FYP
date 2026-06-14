import re

with open('hukut_debug.html', 'r', encoding='utf-8') as f:
    html = f.read()

urls = re.findall(r'https?://[^\s\"\'<>]+', html)
api_urls = set([u for u in urls if 'api' in u or 'search' in u])
print('\n'.join(api_urls))

# Also let's check script IDs again
from bs4 import BeautifulSoup
soup = BeautifulSoup(html, 'html.parser')
print("\nScript IDs:")
print([s.get('id') for s in soup.find_all('script') if s.get('id')])

# What about Next.js or Nuxt? 
print("\nAny __NEXT_DATA__?", soup.find('script', id='__NEXT_DATA__') is not None)
print("Any __NUXT__?", soup.find('script', id='__NUXT__') is not None)

# Print out some script src
print("\nScript Sources:")
print([s.get('src') for s in soup.find_all('script') if s.get('src')][:5])
