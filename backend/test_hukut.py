import requests
from bs4 import BeautifulSoup

def investigate_hukut():
    url = "https://hukut.com/search?q=apple"
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko)"
    }

    try:
        response = requests.get(url, headers=headers, timeout=10)
        with open("hukut_debug.html", "w", encoding="utf-8") as f:
            f.write(response.text)
        print("Saved hukut_debug.html")
        
        soup = BeautifulSoup(response.text, 'html.parser')
        products = soup.find_all('div', class_=lambda c: c and 'product' in c.lower())
        print(f"Found {len(products)} div tags containing 'product' in class")
        
        if len(products) > 0:
            for p in products[:5]:
                print(p.get('class'))
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    investigate_hukut()
