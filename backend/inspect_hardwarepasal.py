from bs4 import BeautifulSoup

def inspect_hardwarepasal():
    with open('hardwarepasal_debug.html', 'r', encoding='utf-8') as f:
        soup = BeautifulSoup(f.read(), 'html.parser')
        
    items = soup.find_all('div', class_='product__item')
    print(f"Found {len(items)} items")
    
    if items:
        print(items[0].prettify()[:1000])

if __name__ == "__main__":
    inspect_hardwarepasal()
