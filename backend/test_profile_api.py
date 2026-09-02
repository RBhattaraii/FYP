"""
Test script to verify profile API endpoints work correctly
"""
import requests
import json

BASE_URL = "http://localhost:8000"

def test_profile_endpoints():
    print("=" * 70)
    print("PROFILE API ENDPOINT TESTS")
    print("=" * 70)
    
    # Step 1: Login to get token
    print("\n1. Testing Login...")
    login_response = requests.post(
        f"{BASE_URL}/auth/login",
        json={
            "email": "test@example.com",
            "password": "testpass123"
        }
    )
    
    if login_response.status_code == 200:
        login_data = login_response.json()
        token = login_data['token']
        print(f"   ✓ Login successful")
        print(f"   Token: {token[:30]}...")
    else:
        print(f"   ✗ Login failed: {login_response.status_code}")
        print(f"   Creating test user first...")
        
        # Register test user
        register_response = requests.post(
            f"{BASE_URL}/auth/register",
            json={
                "email": "test@example.com",
                "password": "testpass123",
                "full_name": "Test User"
            }
        )
        
        if register_response.status_code == 200:
            register_data = register_response.json()
            token = register_data['token']
            print(f"   ✓ Registration successful")
        else:
            print(f"   ✗ Registration failed: {register_response.status_code}")
            return
    
    # Step 2: Get current profile
    print("\n2. Testing GET /auth/me...")
    headers = {"Authorization": f"Bearer {token}"}
    
    profile_response = requests.get(f"{BASE_URL}/auth/me", headers=headers)
    
    if profile_response.status_code == 200:
        profile = profile_response.json()
        print(f"   ✓ Profile fetched successfully")
        print(f"   Email: {profile['email']}")
        print(f"   Name: {profile['full_name']}")
        print(f"   Phone: {profile.get('phone', 'Not set')}")
    else:
        print(f"   ✗ Failed to fetch profile: {profile_response.status_code}")
        return
    
    # Step 3: Update profile
    print("\n3. Testing PUT /auth/me...")
    update_data = {
        "full_name": "Updated Test User",
        "phone": "+977 9876543210"
    }
    
    update_response = requests.put(
        f"{BASE_URL}/auth/me",
        headers=headers,
        json=update_data
    )
    
    if update_response.status_code == 200:
        updated_profile = update_response.json()
        print(f"   ✓ Profile updated successfully")
        print(f"   New Name: {updated_profile['full_name']}")
        print(f"   New Phone: {updated_profile.get('phone', 'Not set')}")
        print(f"   Message: {updated_profile.get('message', '')}")
    else:
        print(f"   ✗ Failed to update profile: {update_response.status_code}")
        print(f"   Error: {update_response.text}")
        return
    
    # Step 4: Verify changes persisted
    print("\n4. Verifying changes persisted...")
    verify_response = requests.get(f"{BASE_URL}/auth/me", headers=headers)
    
    if verify_response.status_code == 200:
        verified_profile = verify_response.json()
        
        if verified_profile['full_name'] == update_data['full_name']:
            print(f"   ✓ Name change persisted")
        else:
            print(f"   ✗ Name change did not persist")
        
        if verified_profile.get('phone') == update_data['phone']:
            print(f"   ✓ Phone change persisted")
        else:
            print(f"   ✗ Phone change did not persist")
    else:
        print(f"   ✗ Failed to verify: {verify_response.status_code}")
    
    print("\n" + "=" * 70)
    print("ALL TESTS COMPLETED")
    print("=" * 70)

if __name__ == "__main__":
    try:
        test_profile_endpoints()
    except requests.exceptions.ConnectionError:
        print("\n✗ Error: Cannot connect to backend at http://localhost:8000")
        print("  Make sure the FastAPI backend is running:")
        print("  cd backend")
        print("  uvicorn main:app --reload")
    except Exception as e:
        print(f"\n✗ Unexpected error: {e}")
