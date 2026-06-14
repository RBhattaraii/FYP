import requests
from bs4 import BeautifulSoup
import json
import re

def investigate_oliz():
    url = "https://www.olizstore.com/search?q=apple"
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64)"
    }
    
    response = requests.get(url, headers=headers)
    soup = BeautifulSoup(response.text, 'html.parser')
    
    # Check for Next.js data
    next_data = soup.find('script', id='__NEXT_DATA__')
    if next_data:
        print("Found Next.js data!")
        try:
            data = json.loads(next_data.string)
            print("Successfully parsed Next.js JSON.")
            # Usually products are in props.pageProps...
            with open("oliz_next_data.json", "w", encoding="utf-8") as f:
                json.dump(data, f, indent=2)
            print("Saved to oliz_next_data.json")
            return
        except Exception as e:
            print(f"Error parsing Next.js JSON: {e}")
            
    # Check for Nuxt.js or other state
    scripts = soup.find_all('script')
    for i, script in enumerate(scripts):
        if script.string and 'window.__INITIAL_STATE__' in script.string:
            print("Found Vue/Nuxt initial state!")
            return
            
    print("Could not find embedded JSON state. Let's dump the HTML to see what classes it actually uses.")
    with open("oliz_html.html", "w", encoding="utf-8") as f:
        f.write(response.text)

if __name__ == "__main__":
    investigate_oliz()
