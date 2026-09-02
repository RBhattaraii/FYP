import requests

# Test with the user who already has alerts
BASE_URL = "http://localhost:8000"

print("🧪 Quick Alert Test\n")

# Try to get alerts without auth to see the error
print("1️⃣ Testing GET /notifications/alerts without auth...")
response = requests.get(f"{BASE_URL}/notifications/alerts")
print(f"   Status: {response.status_code}")
print(f"   Response: {response.json()}\n")

# Now let's just verify the endpoint exists and responds
print("2️⃣ Testing root endpoint...")
response = requests.get(f"{BASE_URL}/")
print(f"   Status: {response.status_code}")
print(f"   Response: {response.json()}\n")

print("✅ Backend API is responding!")
print("\n📱 Now test from your mobile app:")
print("   1. Open a product page")
print("   2. Click 'Set Alert'")
print("   3. Check the console for errors")
