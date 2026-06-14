from bs4 import BeautifulSoup
import re

def inspect_ufonepal():
    with open('ufonepal_debug.html', 'r', encoding='utf-8') as f:
        soup = BeautifulSoup(f.read(), 'html.parser')
        
    print(f"Total size of HTML: {len(str(soup))}")
    
    # Check for Next.js __NEXT_DATA__
    next_data = soup.find('script', id='__NEXT_DATA__')
    if next_data:
        print("\nFound Next.js __NEXT_DATA__!")
        return

    # Look for links that might be products.
    links = soup.find_all('a')
    print(f"Found {len(links)} total links")
    
    shirt_links = []
    for link in links:
        href = link.get('href', '')
        if 'shirt' in href.lower() or 'shirt' in link.text.lower():
            shirt_links.append(link)
            
    print(f"Found {len(shirt_links)} links containing 'shirt'")
    
    if shirt_links:
        print("First few shirt links:")
        for l in shirt_links[:5]:
            print(f"  {l.get('href')} -> {l.text.strip()}")
            
    # Check if there's any dynamic loading script
    for script in soup.find_all('script'):
        if script.get('src'):
            print(f"Script: {script.get('src')}")

if __name__ == "__main__":
    inspect_ufonepal()
