from bs4 import BeautifulSoup

def test_better_parser():
    with open('better_debug.html', 'r', encoding='utf-8') as f:
        soup = BeautifulSoup(f.read(), 'html.parser')
        
    cards = soup.find_all(attrs={"data-hook": "product-list-grid-item"})
    print(f"Found {len(cards)} products.")
    
    for card in cards[:5]:
        root = card.find(attrs={"data-hook": "product-item-root"})
        if not root:
            continue
            
        link = root.find('a', attrs={"data-hook": "product-item-container"})
        product_url = link.get('href') if link else None
        
        # Product name is often in a specific data-hook
        name_el = root.find(attrs={"data-hook": "product-item-name"})
        product_name = name_el.text.strip() if name_el else None
        
        price_el = root.find(attrs={"data-hook": "product-item-price-to-pay"})
        price = price_el.text.strip() if price_el else None
        
        orig_price_el = root.find(attrs={"data-hook": "product-item-formatted-price"})
        orig_price = orig_price_el.text.strip() if orig_price_el else None
        
        img = root.find('img')
        img_url = img.get('src') if img else None
        if img_url and 'static.wixstatic.com' in img_url:
            # Clean up wix image url
            img_url = img_url.split('/v1/')[0]
            
        print(f"Name: {product_name}")
        print(f"Price: {price}")
        print(f"Orig: {orig_price}")
        print(f"URL: {product_url}")
        print(f"Image: {img_url}")
        print("-" * 30)

if __name__ == "__main__":
    test_better_parser()
