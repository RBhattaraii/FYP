"""
Debug script: Saves Daraz page HTML so we can find correct CSS selectors.
"""
from playwright.sync_api import sync_playwright
import time

USER_AGENT = (
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
    "AppleWebKit/537.36 (KHTML, like Gecko) "
    "Chrome/125.0.0.0 Safari/537.36"
)

with sync_playwright() as pw:
    browser = pw.chromium.launch(headless=True)
    context = browser.new_context(user_agent=USER_AGENT, viewport={"width": 1366, "height": 768})
    page = context.new_page()
    
    print("Loading daraz.com.np...")
    page.goto("https://www.daraz.com.np/catalog/?page=1", wait_until="domcontentloaded", timeout=30000)
    time.sleep(5)
    
    # Scroll to trigger lazy loading
    for i in range(0, 5000, 500):
        page.evaluate(f"window.scrollTo(0, {i})")
        time.sleep(0.3)
    time.sleep(2)
    
    # Save full HTML
    html = page.content()
    with open("debug_page.html", "w", encoding="utf-8") as f:
        f.write(html)
    print(f"Saved HTML ({len(html)} chars) to debug_page.html")
    
    # Try to find product-like elements
    test_selectors = [
        "div[data-qa-locator='product-item']",
        ".gridItem--Yd0sa",
        "[data-item-id]",
        ".product-card",
        "div.box--ujueT",
        "[data-tracking='product-card']",
        "a[data-tracking='product-card']",
        ".card-jfy-li",
        "[class*='product']",
        "[class*='Product']",
        "[class*='card']",
        "[class*='Card']",
        "[class*='grid']",
        "[class*='Grid']",
        "[class*='item']",
        "[class*='Item']",
    ]
    
    print("\n--- SELECTOR TEST RESULTS ---")
    for sel in test_selectors:
        try:
            els = page.query_selector_all(sel)
            if els:
                print(f"  ✅ {sel} → {len(els)} elements")
                # Show first element's outer HTML (truncated)
                if els[0]:
                    outer = els[0].evaluate("el => el.outerHTML")
                    print(f"     Preview: {outer[:200]}...")
        except Exception as e:
            pass
    
    # Also try to find any <a> tags with product-like hrefs
    product_links = page.query_selector_all("a[href*='/products/']")
    print(f"\n  Links with /products/: {len(product_links)}")
    if product_links:
        for link in product_links[:3]:
            href = link.get_attribute("href")
            text = link.inner_text().strip()[:80]
            print(f"    → {href[:80]} | {text}")
    
    browser.close()
    print("\nDone!")
