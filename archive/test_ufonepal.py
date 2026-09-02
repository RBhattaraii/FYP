import requests
from bs4 import BeautifulSoup

url = "https://www.ufonepal.com/?s=iphone&post_type=product"
headers = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64)"}
res = requests.get(url, headers=headers, timeout=15)
print("Status:", res.status_code)

soup = BeautifulSoup(res.text, 'html.parser')

# Check for products ul
ul = soup.find('ul', class_='products')
print("ul.products:", ul is not None)

# Try other selectors
products_div = soup.find_all(class_=lambda c: c and 'product' in str(c).lower())
print("Elements with 'product' class:", len(products_div))

# Look at structure
for tag in products_div[:5]:
    print(f"  Tag: {tag.name}, classes: {tag.get('class')}")

# Save HTML for inspection
with open("ufonepal_dump.html", "w", encoding="utf-8") as f:
    f.write(res.text[:50000])
print("Saved first 50KB to ufonepal_dump.html")
