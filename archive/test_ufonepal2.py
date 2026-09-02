import requests
from bs4 import BeautifulSoup

# Test multiple queries on UFO Nepal to see what they stock
headers = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"}

for query in ["phone", "laptop", "samsung", "electronics"]:
    url = f"https://www.ufonepal.com/?s={query}&post_type=product"
    res = requests.get(url, headers=headers, timeout=10)
    soup = BeautifulSoup(res.text, 'html.parser')
    
    # Check for no-results notice
    info = soup.find('p', class_='woocommerce-info')
    ul = soup.find('ul', class_='products')
    
    if info:
        print(f"'{query}': No results ({info.text.strip()[:50]})")
    elif ul:
        items = ul.find_all('li')
        print(f"'{query}': {len(items)} products found in ul.products")
    else:
        # Look for other structures
        divs = soup.find_all('div', class_=lambda c: c and 'product' in str(c).lower())
        print(f"'{query}': ul.products not found, {len(divs)} product divs")
        
        # Try WooCommerce REST API for this query
        api = f"https://www.ufonepal.com/ufo/wp-json/wp/v2/product?search={query}&per_page=5"
        r2 = requests.get(api, headers=headers, timeout=5)
        print(f"         WP API: {r2.status_code}")
