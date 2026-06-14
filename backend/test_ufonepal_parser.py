from bs4 import BeautifulSoup

def test_ufonepal_parser():
    with open('ufonepal_debug2.html', 'r', encoding='utf-8') as f:
        soup = BeautifulSoup(f.read(), 'html.parser')
        
    ul = soup.find('ul', class_='products')
    if not ul:
        print("No ul.products found")
        return
        
    items = ul.find_all('li', class_=lambda c: c and 'product' in c.lower())
    print(f"Found {len(items)} items")
    
    for item in items:
        # Title
        title_el = item.find(class_='woocommerce-loop-product__title')
        title = title_el.text.strip() if title_el else None
        
        # Link
        link_el = item.find('a', class_='woocommerce-LoopProduct-link')
        link = link_el.get('href') if link_el else None
        
        # Price
        price_el = item.find(class_='price')
        price = price_el.text.strip() if price_el else None
        
        # Image
        img_el = item.find('img')
        img = img_el.get('src') if img_el else None
        
        print(f"Name: {title}")
        print(f"URL: {link}")
        print(f"Price: {price}")
        if price_el:
            print(f"Price HTML: {price_el.prettify().strip()}")
        print(f"Image: {img}")
        print("-" * 30)

if __name__ == "__main__":
    test_ufonepal_parser()
