import requests
from bs4 import BeautifulSoup

def investigate_ufonepal_woo():
    url = "https://www.ufonepal.com/?s=shirt&post_type=product"
    
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
    }

    print(f"\nTesting: {url}")
    try:
        response = requests.get(url, headers=headers, timeout=15)
        print(f"Status: {response.status_code}")
        
        if response.status_code == 200:
            soup = BeautifulSoup(response.text, 'html.parser')
            print(f"Title: {soup.title.string if soup.title else 'None'}")
            
            with open("ufonepal_debug2.html", "w", encoding="utf-8") as f:
                f.write(response.text)
                
            products = soup.find_all(class_=lambda c: c and ('product' in c.lower() or 'item' in c.lower()))
            print(f"Found {len(products)} product related elements")
            
            # look for ul class products
            ul = soup.find('ul', class_='products')
            if ul:
                items = ul.find_all('li', class_=lambda c: c and 'product' in c.lower())
                print(f"Found {len(items)} items in ul.products")
                if items:
                    print(items[0].prettify()[:1000])
            else:
                # div class products
                divs = soup.find_all('div', class_=lambda c: c and 'product' in c.lower())
                print(f"Found {len(divs)} items in div.product")
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    investigate_ufonepal_woo()
