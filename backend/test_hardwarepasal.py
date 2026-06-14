import requests
from bs4 import BeautifulSoup

def investigate_hardwarepasal():
    urls = [
        "https://hardwarepasal.com/search?q=drill",
        "https://hardwarepasal.com/search/drill",
        "https://hardwarepasal.com/?s=drill"
    ]
    
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
    }

    found = False
    for url in urls:
        print(f"\nTesting: {url}")
        try:
            response = requests.get(url, headers=headers, timeout=15)
            print(f"Status: {response.status_code}")
            
            if response.status_code == 200:
                soup = BeautifulSoup(response.text, 'html.parser')
                print(f"Title: {soup.title.string if soup.title else 'None'}")
                
                # Look for common product strings or Next/Nuxt data
                if 'drill' in response.text.lower() or 'search' in response.text.lower():
                    print("Found relevant text in HTML!")
                    with open("hardwarepasal_debug.html", "w", encoding="utf-8") as f:
                        f.write(response.text)
                    print("Saved hardwarepasal_debug.html")
                    found = True
                    break
        except Exception as e:
            print(f"Error: {e}")
            
    if not found:
        print("\nCould not find a valid search page with 'drill' text.")
        return

    # Check for Next.js / Nuxt.js
    next_data = soup.find('script', id='__NEXT_DATA__')
    if next_data:
        print("\nFound Next.js __NEXT_DATA__!")
        return

    # Check for embedded JSON state
    for script in soup.find_all('script'):
        if script.string and ('window.__INITIAL_STATE__' in script.string or 'window.__data__' in script.string):
            print("\nFound Nuxt/Vue state!")
            return

    # Check for standard product containers
    print("\nChecking for common product classes:")
    for cls in ['product', 'product-item', 'product-card', 'product-wrapper', 'product-grid', 'item']:
        els = soup.find_all(class_=lambda c: c and cls in c)
        if els:
            print(f"Found {len(els)} elements with class containing '{cls}'")

if __name__ == "__main__":
    investigate_hardwarepasal()
