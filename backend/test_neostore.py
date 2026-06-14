from bs4 import BeautifulSoup

with open("neostore_debug.html", "r", encoding="utf-8") as f:
    html = f.read()

soup = BeautifulSoup(html, 'html.parser')

# Find elements with 'product-item' substring in class
items = soup.find_all(class_=lambda c: c and 'product-item' in c)
print(f"Elements with 'product-item' in class: {len(items)}")
if items:
    print(f"First element: <{items[0].name}> classes={items[0].get('class')}")
    card = items[0]
    print("\n=== CARD HTML (first 1500 chars) ===")
    print(str(card)[:1500])

# Also check for product links
print("\n\n=== PRODUCT LINKS ===")
links = soup.find_all('a', href=lambda h: h and '/product/' in h)
for link in links[:5]:
    print(f"  href={link.get('href','')[:80]}")
    print(f"  text={link.text.strip()[:80]}")
    # Check for price near this link
    parent = link.parent
    for _ in range(5):
        price = parent.find(class_=lambda c: c and 'price' in str(c).lower())
        if price:
            print(f"  price={price.text.strip()[:50]}")
            break
        parent = parent.parent
        if not parent:
            break
    print()
