"""
Direct test of price alerts API endpoints
"""
import requests
import json

BASE_URL = "http://localhost:8000"

# First, let's login to get a token
def login():
    response = requests.post(
        f"{BASE_URL}/auth/login",
        json={"email": "test@pricepilot.com", "password": "password123"}
    )
    if response.status_code == 200:
        data = response.json()
        print(f"✅ Login successful: {data.get('user', {}).get('email')}")
        return data.get('token')
    else:
        print(f"❌ Login failed: {response.status_code} - {response.text}")
        return None

# Test getting price alerts
def test_get_alerts(token):
    headers = {"Authorization": f"Bearer {token}"}
    response = requests.get(f"{BASE_URL}/notifications/alerts", headers=headers)
    
    print(f"\n📋 GET /notifications/alerts")
    print(f"Status: {response.status_code}")
    
    if response.status_code == 200:
        data = response.json()
        print(f"✅ Success: Found {data.get('total_count', 0)} alerts")
        print(f"   Active: {data.get('active_count', 0)}")
        if data.get('alerts'):
            print(f"   First alert: {data['alerts'][0].get('product_title')}")
        return True
    else:
        print(f"❌ Failed: {response.text}")
        return False

# Test creating a price alert
def test_create_alert(token):
    headers = {
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json"
    }
    payload = {
        "product_id": 999,
        "product_title": "Test Product",
        "product_url": "https://test.com/product",
        "store_name": "TestStore",
        "target_price": 900,
        "current_price": 1000
    }
    
    response = requests.post(
        f"{BASE_URL}/notifications/alerts",
        headers=headers,
        json=payload
    )
    
    print(f"\n🆕 POST /notifications/alerts")
    print(f"Status: {response.status_code}")
    
    if response.status_code == 200:
        data = response.json()
        print(f"✅ Success: Created alert {data.get('id')}")
        return data.get('id')
    elif response.status_code == 400:
        print(f"⚠️  Duplicate: {response.json().get('detail')}")
        return None
    else:
        print(f"❌ Failed: {response.text}")
        return None

if __name__ == "__main__":
    print("🧪 Testing Price Alerts API\n")
    
    # Step 1: Login
    token = login()
    if not token:
        print("\n❌ Cannot proceed without authentication")
        exit(1)
    
    # Step 2: Get existing alerts
    get_success = test_get_alerts(token)
    
    # Step 3: Try to create an alert
    alert_id = test_create_alert(token)
    
    # Step 4: Get alerts again to see if it was added
    if alert_id:
        print("\n📋 Fetching alerts again after creation...")
        test_get_alerts(token)
    
    print("\n✅ All tests complete!")
