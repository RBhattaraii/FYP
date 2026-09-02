import requests
from bs4 import BeautifulSoup

url = "https://www.ufonepal.com/?s=iphone&post_type=product"
headers = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36",
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
}
res = requests.get(url, headers=headers, timeout=15)
print("Status:", res.status_code)
print("Content length:", len(res.text))

soup = BeautifulSoup(res.text, 'html.parser')

# Find main content area
main = soup.find('main') or soup.find('div', id='main') or soup.find('div', class_='main')
print("Main element:", main.name if main else "NOT FOUND")

# Look for any li or article elements that might be products
articles = soup.find_all('article')
print("Articles found:", len(articles))

lis = soup.find_all('li')
print("All li elements:", len(lis))

# Search for any WooCommerce-related elements
wc_elements = soup.find_all(class_=lambda c: c and ('woocommerce' in str(c) or 'product' in str(c)))
print("WooCommerce/product elements:", len(wc_elements))
for el in wc_elements[:5]:
    print(f"  <{el.name} class='{' '.join(el.get('class', []))}'>")

# Check if it's a redirect or different page
print("\nPage title:", soup.title.text if soup.title else "N/A")

# Check for WooCommerce REST API
print("\nTrying WC REST API...")
api_url = "https://www.ufonepal.com/ufo/wp-json/wc/v3/products?search=iphone&per_page=20"
res2 = requests.get(api_url, headers=headers, timeout=10)
print("API status:", res2.status_code)
if res2.status_code == 200:
    data = res2.json()
    print("API returned:", len(data), "products")
    if data:
        print("Sample:", data[0].get('name'))
else:
    print("API body (100 chars):", res2.text[:100])

# Try unauthenticated products endpoint
api_url2 = "https://www.ufonepal.com/ufo/wp-json/wc/v2/products?search=iphone&per_page=20&status=publish"
res3 = requests.get(api_url2, headers=headers, timeout=10)
print("\nWC v2 API status:", res3.status_code)
if res3.status_code == 200:
    data2 = res3.json()
    print("V2 API returned:", len(data2), "products")
