"""Debug: get full HTML of one search result card"""
import time
from playwright.sync_api import sync_playwright

with sync_playwright() as pw:
    browser = pw.chromium.launch(headless=True)
    page = browser.new_page()
    page.goto("https://www.daraz.com.np/catalog/?q=samsung+s24", wait_until="domcontentloaded")
    time.sleep(3)
    for i in range(0, 3000, 500):
        page.evaluate(f"window.scrollTo(0, {i})")
        time.sleep(0.2)
    time.sleep(1)
    
    # Use the CORRECT selector: div.Bm3ON with data-qa-locator="product-item"
    card = page.query_selector("div.Bm3ON[data-qa-locator='product-item']")
    if card:
        full_html = card.evaluate("el => el.outerHTML")
        with open("one_card.txt", "w", encoding="utf-8") as f:
            f.write(full_html)
        print(f"Saved one card ({len(full_html)} chars)")
    else:
        print("No card found with div.Bm3ON")
    
    browser.close()
