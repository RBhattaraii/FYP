import requests
from bs4 import BeautifulSoup

def investigate_better_appliances():
    urls = [
        "https://www.thebetterappliances.com/?s=tv&post_type=product",
        "https://www.thebetterappliances.com/search?q=tv",
        "https://www.thebetterappliances.com/?s=tv"
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
                
                # We often see WooCommerce using ?s=query&post_type=product
                
                # Look for common product strings or Next/Nuxt data
                if 'tv' in response.text.lower() or 'television' in response.text.lower():
                    print("Found relevant text in HTML!")
                    with open("better_debug.html", "w", encoding="utf-8") as f:
                        f.write(response.text)
                    print("Saved better_debug.html")
                    found = True
                    break
        except Exception as e:
            print(f"Error: {e}")
            
    if not found:
        print("\nCould not find a valid search page with 'tv' text.")
        return

    # Check for WooCommerce/WordPress structures
    print("\nChecking for common product classes:")
    for cls in ['product', 'type-product', 'product-item', 'product-card', 'item']:
        els = soup.find_all(class_=lambda c: c and cls in c)
        if els:
            print(f"Found {len(els)} elements with class containing '{cls}'")

if __name__ == "__main__":
    investigate_better_appliances()
