"""
Test admin login endpoint
Run this script: python test_admin_login.py

Make sure the server is running: uvicorn main:app --reload
"""

import requests
import sys
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# API URL
BASE_URL = "http://localhost:8000"

def test_admin_login():
    """Test admin login endpoint"""
    print("🧪 Testing Admin Login Endpoint...\n")
    
    # Get admin credentials from environment
    admin_username = os.getenv("ADMIN_USERNAME")
    admin_password = os.getenv("ADMIN_PASSWORD")
    
    if not admin_username or not admin_password:
        print("❌ Admin credentials not found in .env file")
        return False
    
    print(f"📧 Admin Username: {admin_username}")
    print(f"🔐 Admin Password: {'*' * len(admin_password)}\n")
    
    # Test 1: Valid admin credentials
    print("Test 1: Valid admin credentials")
    print("-" * 50)
    try:
        response = requests.post(
            f"{BASE_URL}/auth/admin-login",
            json={
                "email": admin_username,
                "password": admin_password
            }
        )
        
        if response.status_code == 200:
            data = response.json()
            print("✅ Admin login successful!")
            print(f"   Token Type: {data.get('token_type')}")
            print(f"   User ID: {data.get('user_id')}")
            print(f"   Role: {data.get('role')}")
            print(f"   Email: {data.get('email')}")
            print(f"   Full Name: {data.get('full_name')}")
            print(f"   Token: {data.get('token')[:50]}...")
            
            # Verify role is admin
            if data.get('role') == 'admin':
                print("✅ Role claim verified: admin")
            else:
                print(f"❌ Role claim incorrect: {data.get('role')}")
                return False
                
            return data.get('token')
        else:
            print(f"❌ Failed with status code: {response.status_code}")
            print(f"   Response: {response.json()}")
            return False
    except Exception as e:
        print(f"❌ Error: {e}")
        return False
    
    print()
    
    # Test 2: Invalid credentials
    print("\nTest 2: Invalid credentials (wrong password)")
    print("-" * 50)
    try:
        response = requests.post(
            f"{BASE_URL}/auth/admin-login",
            json={
                "email": admin_username,
                "password": "WrongPassword123!"
            }
        )
        
        if response.status_code == 401:
            print("✅ Correctly rejected invalid credentials")
            print(f"   Response: {response.json()}")
        else:
            print(f"❌ Unexpected status code: {response.status_code}")
            print(f"   Response: {response.json()}")
            return False
    except Exception as e:
        print(f"❌ Error: {e}")
        return False
    
    print()
    
    # Test 3: Invalid username
    print("\nTest 3: Invalid credentials (wrong username)")
    print("-" * 50)
    try:
        response = requests.post(
            f"{BASE_URL}/auth/admin-login",
            json={
                "email": "wrong@example.com",
                "password": admin_password
            }
        )
        
        if response.status_code == 401:
            print("✅ Correctly rejected invalid credentials")
            print(f"   Response: {response.json()}")
        else:
            print(f"❌ Unexpected status code: {response.status_code}")
            print(f"   Response: {response.json()}")
            return False
    except Exception as e:
        print(f"❌ Error: {e}")
        return False
    
    print()
    
    return True


def test_token_claims(token):
    """Test that the token contains admin role claim"""
    print("\nTest 4: Verify token claims")
    print("-" * 50)
    
    try:
        import jwt
        
        # Decode without verification to inspect claims
        decoded = jwt.decode(token, options={"verify_signature": False})
        
        print("Token payload:")
        for key, value in decoded.items():
            if key != 'exp':
                print(f"   {key}: {value}")
            else:
                from datetime import datetime
                exp_time = datetime.fromtimestamp(value)
                print(f"   {key}: {exp_time} (expires at)")
        
        # Check required claims
        required_claims = ['user_id', 'role', 'email']
        for claim in required_claims:
            if claim in decoded:
                print(f"✅ Claim '{claim}' present: {decoded[claim]}")
            else:
                print(f"❌ Claim '{claim}' missing")
                return False
        
        # Verify role is admin
        if decoded.get('role') == 'admin':
            print("✅ Admin role claim verified")
        else:
            print(f"❌ Expected role='admin', got role='{decoded.get('role')}'")
            return False
            
        return True
        
    except Exception as e:
        print(f"❌ Error decoding token: {e}")
        return False


def main():
    """Run all tests"""
    print("=" * 50)
    print("ADMIN LOGIN ENDPOINT TESTS")
    print("=" * 50)
    print()
    
    # Check if server is running
    try:
        response = requests.get(f"{BASE_URL}/docs")
        if response.status_code != 200:
            print("❌ Server is not running or not responding")
            print("   Start the server with: uvicorn main:app --reload")
            sys.exit(1)
    except requests.exceptions.ConnectionError:
        print("❌ Cannot connect to server at", BASE_URL)
        print("   Start the server with: uvicorn main:app --reload")
        sys.exit(1)
    
    print("✅ Server is running\n")
    
    # Run tests
    token = test_admin_login()
    
    if token and isinstance(token, str):
        test_token_claims(token)
    
    print("\n" + "=" * 50)
    print("ALL TESTS COMPLETED")
    print("=" * 50)


if __name__ == "__main__":
    main()
