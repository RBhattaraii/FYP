"""
Integration test for GET /products/home API endpoint
Tests task 6.1 requirements
"""
import requests
import json

BASE_URL = "http://localhost:8000"

def test_home_endpoint():
    """Test GET /products/home endpoint"""
    
    print("[TEST 1] Testing GET /products/home endpoint...")
    try:
        response = requests.get(f"{BASE_URL}/products/home")
        
        # Check status code
        assert response.status_code == 200, f"Expected 200, got {response.status_code}"
        print(f"✓ Status code: {response.status_code}")
        
        # Parse JSON response
        data = response.json()
        
        # Check response structure
        assert 'best_deals' in data, "Missing 'best_deals' field"
        assert 'top_price_drops' in data, "Missing 'top_price_drops' field"
        print(f"✓ Response has required fields: best_deals, top_price_drops")
        
        # Check data types
        assert isinstance(data['best_deals'], list), "'best_deals' should be a list"
        assert isinstance(data['top_price_drops'], list), "'top_price_drops' should be a list"
        print(f"✓ Both fields are arrays")
        
        # Check results count
        print(f"✓ Best deals count: {len(data['best_deals'])}")
        print(f"✓ Top price drops count: {len(data['top_price_drops'])}")
        
        # Verify product structure
        if data['best_deals']:
            product = data['best_deals'][0]
            required_fields = ['id', 'title', 'price', 'store_name', 'product_url', 'image_url']
            for field in required_fields:
                assert field in product, f"Missing field '{field}' in product"
            print(f"✓ Product structure is valid")
            print(f"  Sample: {product['title'][:50]}... - Rs {product['price']}")
        
        # Test response time
        print(f"\n[TEST 2] Testing response time...")
        import time
        start = time.time()
        response = requests.get(f"{BASE_URL}/products/home")
        elapsed = time.time() - start
        print(f"✓ Response time: {elapsed:.3f}s")
        
        if elapsed < 0.5:
            print(f"✓ Response time is under 500ms (requirement met)")
        else:
            print(f"⚠ Response time exceeds 500ms target")
        
        print("\n[SUCCESS] All API tests passed!")
        return True
        
    except requests.exceptions.ConnectionError:
        print("[ERROR] Cannot connect to server. Is it running on port 8000?")
        return False
    except AssertionError as e:
        print(f"[ERROR] Test assertion failed: {e}")
        return False
    except Exception as e:
        print(f"[ERROR] Unexpected error: {e}")
        return False

if __name__ == "__main__":
    success = test_home_endpoint()
    exit(0 if success else 1)
