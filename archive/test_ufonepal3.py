import requests
from bs4 import BeautifulSoup

headers = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"}
url = "https://www.ufonepal.com/?s=phone&post_type=product"
res = requests.get(url, headers=headers, timeout=10)
soup = BeautifulSoup(res.text, 'html.parser')

ul = soup.find('ul', class_='products')
print("ul.products found:", ul is not None)
items = ul.find_all('li') if ul else []
print("Items:", len(items))

for item in items:
    print("\n--- Item ---")
    print("Classes:", item.get('class'))
    
    # Check title
    title_el = item.find(class_='woocommerce-loop-product__title')
    print("Title:", title_el.text.strip() if title_el else "NOT FOUND")
    
    # Check link
    link_el = item.find('a', class_='woocommerce-LoopProduct-link')
    print("Link:", link_el.get('href') if link_el else "NOT FOUND")
    
    # Check price
    price_el = item.find(class_='price')
    print("Price:", price_el.get_text(separator=' ').strip() if price_el else "NOT FOUND")
    
    # Check image
    img = item.find('img')
    if img:
        print("Img src:", (img.get('data-src') or img.get('src') or '')[:80])
