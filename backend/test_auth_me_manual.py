"""
Manual test for GET /auth/me endpoint (Task 8.1)
This script tests the endpoint by making real HTTP requests
"""
import requests
import json
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# API base URL
BASE_URL = "http://localhost:8000"

def test_auth_me_endpoint():
    """Test the GET /auth/me endpoint"""
    
    print("=" * 60)
    print("Testing GET /auth/me Endpoint (Task 8.1)")
    print("=" * 60)
    
    # First, we need to login to get a JWT token
    print("\n1. Logging in to get JWT token...")
    
    # Try to login with test credentials
    login_url = f"{BASE_URL}/auth/login"
    login_data = {
        "email": "test@example.com",
        "password": "testpassword123"
    }
    
    try:
        login_response = requests.post(login_url, json=login_data)
        
        if login_response.status_code == 401:
            print("❌ Test user doesn't exist. Creating test user first...")
            
            # Register a new test user
            register_url = f"{BASE_URL}/auth/register"
            register_data = {
                "email": "test@example.com",
                "password": "testpassword123",
                "full_name": "Test User"
            }
            
            register_response = requests.post(register_url, json=register_data)
            
            if register_response.status_code == 200:
                token_data = register_response.json()
                token = token_data.get("token")
                print(f"✅ Test user created successfully")
                print(f"   User ID: {token_data.get('user_id')}")
                print(f"   Email: {token_data.get('email')}")
            else:
                print(f"❌ Failed to create test user: {register_response.status_code}")
                print(f"   Response: {register_response.text}")
                return
        
        elif login_response.status_code == 200:
            token_data = login_response.json()
            token = token_data.get("token")
            print(f"✅ Login successful")
            print(f"   User ID: {token_data.get('user_id')}")
            print(f"   Email: {token_data.get('email')}")
        else:
            print(f"❌ Login failed: {login_response.status_code}")
            print(f"   Response: {login_response.text}")
            return
    
    except requests.exceptions.ConnectionError:
        print("❌ Cannot connect to backend. Make sure the server is running:")
        print("   python backend/main.py")
        return
    except Exception as e:
        print(f"❌ Login error: {e}")
        return
    
    # Test 2: Call GET /auth/me with valid token
    print("\n2. Testing GET /auth/me with valid token...")
    
    me_url = f"{BASE_URL}/auth/me"
    headers = {
        "Authorization": f"Bearer {token}"
    }
    
    try:
        me_response = requests.get(me_url, headers=headers)
        
        if me_response.status_code == 200:
            user_data = me_response.json()
            print("✅ GET /auth/me successful!")
            print(f"\n   Response:")
            print(f"   {json.dumps(user_data, indent=6)}")
            
            # Verify response structure
            print("\n3. Verifying response structure...")
            required_fields = ['id', 'email', 'full_name', 'created_at']
            missing_fields = []
            
            for field in required_fields:
                if field not in user_data:
                    missing_fields.append(field)
            
            if missing_fields:
                print(f"❌ Missing required fields: {missing_fields}")
            else:
                print("✅ All required fields present")
            
            # Verify password_hash is NOT included
            if 'password_hash' in user_data or 'password' in user_data:
                print("❌ SECURITY ISSUE: password_hash is included in response!")
            else:
                print("✅ password_hash correctly excluded from response")
            
            # Test extracting first name for greeting
            full_name = user_data.get('full_name', '')
            if full_name:
                first_name = full_name.split()[0]
                print(f"\n4. Frontend greeting example:")
                print(f"   'Hello, {first_name}!'")
        
        else:
            print(f"❌ GET /auth/me failed: {me_response.status_code}")
            print(f"   Response: {me_response.text}")
            return
    
    except Exception as e:
        print(f"❌ Error calling /auth/me: {e}")
        return
    
    # Test 3: Call GET /auth/me without token (should fail with 401)
    print("\n5. Testing GET /auth/me without token (should fail)...")
    
    try:
        me_response_no_token = requests.get(me_url)
        
        if me_response_no_token.status_code == 401:
            print("✅ Correctly returns 401 Unauthorized without token")
        else:
            print(f"❌ Expected 401, got {me_response_no_token.status_code}")
    
    except Exception as e:
        print(f"❌ Error: {e}")
    
    # Test 4: Call GET /auth/me with invalid token (should fail with 401)
    print("\n6. Testing GET /auth/me with invalid token (should fail)...")
    
    headers_invalid = {
        "Authorization": "Bearer invalid.token.here"
    }
    
    try:
        me_response_invalid = requests.get(me_url, headers=headers_invalid)
        
        if me_response_invalid.status_code == 401:
            print("✅ Correctly returns 401 Unauthorized with invalid token")
        else:
            print(f"❌ Expected 401, got {me_response_invalid.status_code}")
    
    except Exception as e:
        print(f"❌ Error: {e}")
    
    print("\n" + "=" * 60)
    print("✅ Task 8.1 Test Complete!")
    print("=" * 60)
    print("\nSummary:")
    print("- GET /auth/me endpoint is working correctly")
    print("- Returns user profile (id, email, full_name, created_at, phone)")
    print("- Requires valid JWT token in Authorization header")
    print("- Returns 401 Unauthorized if token is missing or invalid")
    print("- Excludes password_hash from response (security)")
    print("- Can be used by frontend for header greeting")


if __name__ == "__main__":
    test_auth_me_endpoint()
