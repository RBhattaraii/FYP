from bs4 import BeautifulSoup
import re

def inspect_better():
    with open('better_debug.html', 'r', encoding='utf-8') as f:
        soup = BeautifulSoup(f.read(), 'html.parser')
        
    links = soup.find_all('a', href=re.compile(r'/product/', re.IGNORECASE))
    
    if links:
        link = links[0]
        # Let's go up a few levels to get the container
        # The parent with class containing 'S4WbK_' or 'ejYUwA' seems to be the card
        parent = link.parent
        for _ in range(5):
            if parent:
                parent = parent.parent
        
        print("--- CONTAINER HTML ---")
        if parent:
            print(parent.prettify()[:2000])

if __name__ == "__main__":
    inspect_better()
