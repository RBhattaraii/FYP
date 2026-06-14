from bs4 import BeautifulSoup

def test_hardwarepasal_parser():
    with open('hardwarepasal_debug.html', 'r', encoding='utf-8') as f:
        soup = BeautifulSoup(f.read(), 'html.parser')
        
    items = soup.find_all('div', class_='product__item')
    print(f"Found {len(items)} items")
    
    for item in items[:10]:
        name_el = item.find('div', class_='product__name')
        name = name_el.find('h4').text.strip() if name_el and name_el.find('h4') else None
        
        price_el = item.find('div', class_='product__price')
        price = price_el.text.strip() if price_el else None
        
        # Sometimes there's a span or del for original price
        if price_el:
            print(f"Name: {name}")
            print(f"Price HTML: {price_el.prettify().strip()}")
            print("-" * 30)

if __name__ == "__main__":
    test_hardwarepasal_parser()
