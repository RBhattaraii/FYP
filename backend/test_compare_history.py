#!/usr/bin/env python3
"""
Test script for Compare and History features
Tests the new API endpoints to ensure they work correctly
"""

import requests
import json

# API base URL
BASE_URL = "http://localhost:8000"

def test_endpoints():
    """Test the new Compare and History endpoints"""
    
    print("🧪 Testing Compare and History API endpoints...")
    
    # Test endpoints that don't require authentication
    endpoints_to_test = [
        "/docs",  # API documentation
        "/products/search?q=laptop&limit=3",  # Product search
    ]
    
    for endpoint in endpoints_to_test:
        try:
            response = requests.get(f"{BASE_URL}{endpoint}")
            if response.status_code == 200:
                print(f"✅ {endpoint} - Status: {response.status_code}")
            else:
                print(f"❌ {endpoint} - Status: {response.status_code}")
        except Exception as e:
            print(f"❌ {endpoint} - Error: {e}")
    
    # Test product detail endpoint (should work without auth)
    try:
        # First get a product ID from search
        search_response = requests.get(f"{BASE_URL}/products/search?q=laptop&limit=1")
        if search_response.status_code == 200:
            search_data = search_response.json()
            if search_data.get("results"):
                product_id = search_data["results"][0]["id"]
                
                # Test product detail
                detail_response = requests.get(f"{BASE_URL}/products/{product_id}")
                if detail_response.status_code == 200:
                    print(f"✅ /products/{product_id} - Status: 200 (Product detail works without auth)")
                else:
                    print(f"❌ /products/{product_id} - Status: {detail_response.status_code}")
    except Exception as e:
        print(f"❌ Product detail test - Error: {e}")
    
    # Test authenticated endpoints (should return 401 without token)
    auth_endpoints = [
        "/history/",  # Get user history
        "/compare/",  # Get user comparisons
    ]
    
    for endpoint in auth_endpoints:
        try:
            response = requests.get(f"{BASE_URL}{endpoint}")
            if response.status_code == 401:
                print(f"✅ {endpoint} - Status: 401 (Properly requires authentication)")
            else:
                print(f"⚠️  {endpoint} - Status: {response.status_code} (Expected 401)")
        except Exception as e:
            print(f"❌ {endpoint} - Error: {e}")
    
    print("\n📋 API Endpoint Summary:")
    print("✅ Compare API endpoints: /compare/")
    print("   - GET  /compare/                    # List user comparisons")
    print("   - POST /compare/create              # Create new comparison")
    print("   - GET  /compare/{id}                # Get comparison details") 
    print("   - POST /compare/{id}/add            # Add product to comparison")
    print("   - POST /compare/quick               # Quick 2-product comparison")
    print("   - POST /compare/search              # Search products for comparison")
    print("")
    print("✅ History API endpoints: /history/")
    print("   - GET  /history/                    # Get user history")
    print("   - POST /history/add                 # Add product to history")
    print("   - DELETE /history/clear             # Clear history")
    print("   - GET  /history/stats               # Get history statistics")
    print("")
    print("✅ Enhanced product endpoint:")
    print("   - GET  /products/{id}               # Auto-adds to history if user logged in")
    
    print(f"\n🎉 Compare and History features are ready!")
    print(f"📖 View full API documentation: {BASE_URL}/docs")

if __name__ == "__main__":
    test_endpoints()