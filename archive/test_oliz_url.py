import requests
from bs4 import BeautifulSoup
import json
import urllib.parse

search_query = "iphone"
encoded_query = urllib.parse.quote(search_query)
url = f"https://www.olizstore.com/search?q={encoded_query}"

headers = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36",
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8",
}

response = requests.get(url, headers=headers, timeout=15)
print(f"Status: {response.status_code}")

if response.status_code == 200:
    soup = BeautifulSoup(response.text, 'html.parser')
    
    # Try to find product links on the search page directly
    links = []
    for a in soup.find_all('a', href=True):
        href = a['href']
        if '/product/' in href or '/products/' in href:
            links.append(href)
            
    print(f"Found {len(links)} product links in HTML")
    for link in links[:5]:
        print(f"  {link}")
        
    # Also check Next.js data
    next_data_script = soup.find('script', id='__NEXT_DATA__')
    if next_data_script:
        data = json.loads(next_data_script.string)
        results = data.get('props', {}).get('pageProps', {}).get('response', [])
        print(f"\nNext.js data has {len(results)} products. First 3 slugs:")
        for item in results[:3]:
            print(f"  {item.get('name')}: {item.get('slug')}")
