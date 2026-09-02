from bs4 import BeautifulSoup

with open("cg_laptop.html", "r", encoding="utf-8") as f:
    soup = BeautifulSoup(f.read(), "html.parser")

links = soup.find_all('a')
print("Found links:", len(links))

# Find any links that contain "product"
product_links = [a for a in links if a.get('href') and '/product/' in a.get('href')]
print("Product links:", len(product_links))

if product_links:
    for a in product_links[:5]:
        print(a.get('href'), a.text.strip())
        
# Find typical price elements
prices = soup.find_all(text=lambda t: t and 'Rs.' in t)
print("Prices found:", len(prices))
if prices:
    print([p.strip() for p in prices[:5]])
