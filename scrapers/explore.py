import sys
from playwright.sync_api import sync_playwright

def main():
    try:
        with sync_playwright() as p:
            browser = p.chromium.launch(headless=True)
            page = browser.new_page(user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/125.0.0.0 Safari/537.36")
            page.goto("https://www.olizstore.com/", wait_until="domcontentloaded", timeout=60000)
            page.wait_for_timeout(5000)
            print("Successfully loaded Oliz Store")
            
            # Find product cards
            html = page.content()
            with open("oliz_dump.html", "w", encoding="utf-8") as f:
                f.write(html)
            browser.close()
            print("Dumped HTML to oliz_dump.html")
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    main()
