"""
Test authentication endpoints
Run this script: python test_auth.py
Make sure the server is running: uvicorn main:app --reload
"""

import requests
import json

BASE_URL = "http://localhost:8000"

def test_register():
    """Test user registration"""
    print("\n" + "="*60)
    print("🧪 Testing User Registration")
    print("="*60)
    
    # Test data
    user_data = {
        "email": "testuser@pricepilot.com",
        "password": "testpass123",
        "full_name": "Test User"
    }
    
    print(f"\n📤 Sending POST request to {BASE_URL}/auth/register")
    print(f"Data: {json.dumps(user_data, indent=2)}")
    
    try:
        response = requests.post(
            f"{BASE_URL}/auth/register",
            json=user_data
        )
        
        print(f"\n📥 Response Status: {response.status_code}")
        print(f"Response Body:")
        print(json.dumps(response.json(), indent=2))
        
        if response.status_code == 200:
            print("\n✅ Registration successful!")
            return response.json()["token"]
        elif response.status_code == 400:
            print("\n⚠️  Email already registered (this is expected if you ran this before)")
            return None
        else:
            print(f"\n❌ Registration failed with status {response.status_code}")
            return None
            
    except requests.exceptions.ConnectionError:
        print("\n❌ Connection failed! Make sure the server is running:")
        print("   uvicorn main:app --reload")
        return None
    except Exception as e:
        print(f"\n❌ Error: {e}")
        return None


def test_login():
    """Test user login"""
    print("\n" + "="*60)
    print("🧪 Testing User Login")
    print("="*60)
    
    # Test credentials
    credentials = {
        "email": "testuser@pricepilot.com",
        "password": "testpass123"
    }
    
    print(f"\n📤 Sending POST request to {BASE_URL}/auth/login")
    print(f"Data: {json.dumps(credentials, indent=2)}")
    
    try:
        response = requests.post(
            f"{BASE_URL}/auth/login",
            json=credentials
        )
        
        print(f"\n📥 Response Status: {response.status_code}")
        print(f"Response Body:")
        print(json.dumps(response.json(), indent=2))
        
        if response.status_code == 200:
            print("\n✅ Login successful!")
            return response.json()["token"]
        else:
            print(f"\n❌ Login failed with status {response.status_code}")
            return None
            
    except requests.exceptions.ConnectionError:
        print("\n❌ Connection failed! Make sure the server is running:")
        print("   uvicorn main:app --reload")
        return None
    except Exception as e:
        print(f"\n❌ Error: {e}")
        return None


def test_invalid_password():
    """Test registration with invalid password"""
    print("\n" + "="*60)
    print("🧪 Testing Invalid Password (too short)")
    print("="*60)
    
    user_data = {
        "email": "test2@pricepilot.com",
        "password": "short",  # Too short, no number
        "full_name": "Test User 2"
    }
    
    print(f"\n📤 Sending POST request to {BASE_URL}/auth/register")
    print(f"Data: {json.dumps(user_data, indent=2)}")
    
    try:
        response = requests.post(
            f"{BASE_URL}/auth/register",
            json=user_data
        )
        
        print(f"\n📥 Response Status: {response.status_code}")
        print(f"Response Body:")
        print(json.dumps(response.json(), indent=2))
        
        if response.status_code == 422:
            print("\n✅ Validation error caught correctly!")
        else:
            print(f"\n⚠️  Expected 422, got {response.status_code}")
            
    except Exception as e:
        print(f"\n❌ Error: {e}")


def test_wrong_password():
    """Test login with wrong password"""
    print("\n" + "="*60)
    print("🧪 Testing Wrong Password")
    print("="*60)
    
    credentials = {
        "email": "testuser@pricepilot.com",
        "password": "wrongpassword123"
    }
    
    print(f"\n📤 Sending POST request to {BASE_URL}/auth/login")
    print(f"Data: {json.dumps(credentials, indent=2)}")
    
    try:
        response = requests.post(
            f"{BASE_URL}/auth/login",
            json=credentials
        )
        
        print(f"\n📥 Response Status: {response.status_code}")
        print(f"Response Body:")
        print(json.dumps(response.json(), indent=2))
        
        if response.status_code == 401:
            print("\n✅ Unauthorized error returned correctly!")
        else:
            print(f"\n⚠️  Expected 401, got {response.status_code}")
            
    except Exception as e:
        print(f"\n❌ Error: {e}")


def main():
    """Run all tests"""
    print("\n" + "="*60)
    print("🚀 PricePilot Authentication Tests")
    print("="*60)
    print("\n⚠️  Make sure the server is running:")
    print("   cd backend")
    print("   uvicorn main:app --reload")
    print("\nPress Enter to continue...")
    input()
    
    # Test 1: Register
    token = test_register()
    
    # Test 2: Login
    if token is None:  # If registration failed (email exists), try login
        token = test_login()
    
    # Test 3: Invalid password
    test_invalid_password()
    
    # Test 4: Wrong password
    test_wrong_password()
    
    # Summary
    print("\n" + "="*60)
    print("✅ All tests completed!")
    print("="*60)
    
    if token:
        print(f"\n🎫 Your JWT Token:")
        print(f"{token[:50]}...")
        print("\n💡 Use this token in Authorization header:")
        print(f"   Authorization: Bearer {token}")
    
    print("\n📚 Next steps:")
    print("1. Test in Swagger UI: http://localhost:8000/docs")
    print("2. Create protected routes that require authentication")
    print("3. Set up mobile app to use these endpoints")
    print()


if __name__ == "__main__":
    main()
