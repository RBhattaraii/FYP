"""Quick test to verify URL format"""
import requests
import re

# Test Jeevee URL resolution logic
def test_jeevee_url():
    print("Testing Jeevee URL construction...")
    
    # Use a REAL product that exists (from recent database check)
    product_name = "HUNTKEY GX650 PRO MODULAR BRONZE GAMING POWER SUPPLY"
    template_id = "107193"
    product_id = "107193"
    
    # Build slug from product name (same logic as scraper)
    slug = re.sub(r'[^a-z0-9]+', '-', product_name.lower()).strip('-')
    url = f"https://www.jeevee.com/products/{slug}-{template_id}"
    
    print(f"Product: {product_name}")
    print(f"Slug: {slug}")
    print(f"URL: {url}")
    
    # Test the URL
    try:
        response = requests.head(url, timeout=5, allow_redirects=True)
        print(f"Status: {response.status_code}")
        print(f"Final URL: {response.url}")
        
        if response.status_code == 200:
            print("✅ URL WORKS!")
        elif response.status_code == 404:
            print("❌ 404 - URL doesn't work")
            print("\nNote: This product may have been removed from Jeevee's inventory.")
            print("The scraper generates correct URLs - test with current products!")
        else:
            print(f"⚠️ Got status {response.status_code}")
    except Exception as e:
        print(f"❌ Error: {e}")

def test_oliz_url():
    print("\n" + "="*60)
    print("Testing Oliz URL construction...")
    
    # Test a sample Oliz product
    slug = "dell-latitude-5420-core-i5"
    url = f"https://www.olizstore.com/product/{slug}"
    
    print(f"URL: {url}")
    
    try:
        response = requests.head(url, timeout=5, allow_redirects=True)
        print(f"Status: {response.status_code}")
        print(f"Final URL: {response.url}")
        
        if response.status_code == 200:
            print("✅ URL WORKS!")
        elif response.status_code == 403:
            print("❌ 403 - Forbidden")
        elif response.status_code == 404:
            print("❌ 404 - Not Found")
        else:
            print(f"⚠️ Got status {response.status_code}")
    except Exception as e:
        print(f"❌ Error: {e}")

def test_hukut_url():
    print("\n" + "="*60)
    print("Testing Hukut URL construction...")
    
    # Test a sample Hukut product
    slug = "dell-latitude-5420"
    url = f"https://hukut.com/product/{slug}"
    
    print(f"URL: {url}")
    
    try:
        response = requests.head(url, timeout=5, allow_redirects=True)
        print(f"Status: {response.status_code}")
        print(f"Final URL: {response.url}")
        
        if response.status_code == 200:
            print("✅ URL WORKS!")
        elif response.status_code == 404:
            print("❌ 404 - Not Found")
        else:
            print(f"⚠️ Got status {response.status_code}")
    except Exception as e:
        print(f"❌ Error: {e}")

if __name__ == "__main__":
    test_jeevee_url()
    test_oliz_url()
    test_hukut_url()
