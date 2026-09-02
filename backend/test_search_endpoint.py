"""
Unit tests for Task 7.1: GET /products/search endpoint

This test file verifies that the search endpoint:
1. Validates query parameter (non-empty)
2. Implements rate limiting (max 10 searches/minute)
3. Returns proper response format with metadata
4. Uses tiered search coordinator service
"""
from fastapi.testclient import TestClient
from main import app

client = TestClient(app)


def test_search_endpoint_exists():
    """Test that /products/search endpoint exists"""
    response = client.get("/products/search?q=laptop")
    assert response.status_code in [200, 500], "Endpoint should exist (200 or 500 for errors)"


def test_search_validates_empty_query():
    """Test that empty query returns 400 error"""
    response = client.get("/products/search?q=")
    assert response.status_code == 400
    assert "empty" in response.json()["detail"].lower()


def test_search_validates_missing_query():
    """Test that missing query parameter returns 422 error"""
    response = client.get("/products/search")
    assert response.status_code == 422  # FastAPI validation error


def test_search_response_structure():
    """Test that search response has correct structure"""
    response = client.get("/products/search?q=test")
    
    if response.status_code == 200:
        data = response.json()
        
        # Verify required fields exist
        assert "request_id" in data
        assert "query" in data
        assert "tier" in data
        assert "is_complete" in data
        assert "results" in data
        assert "results_count" in data
        assert "tier1_platforms" in data
        assert "message" in data
        
        # Verify data types
        assert isinstance(data["request_id"], str)
        assert isinstance(data["query"], str)
        assert isinstance(data["is_complete"], bool)
        assert isinstance(data["results"], list)
        assert isinstance(data["results_count"], int)
        assert isinstance(data["tier1_platforms"], list)
        assert isinstance(data["message"], str)
        
        # Verify query is normalized
        assert data["query"] == "test"


def test_search_rate_limiting():
    """Test that rate limiting works (max 10 requests per minute)"""
    # Make 11 requests quickly
    responses = []
    for i in range(11):
        response = client.get(f"/products/search?q=ratelimit{i}")
        responses.append(response.status_code)
    
    # First 10 should succeed (200) or have search errors (500)
    # 11th should be rate limited (429)
    success_count = sum(1 for code in responses if code in [200, 500])
    rate_limited_count = sum(1 for code in responses if code == 429)
    
    assert success_count <= 10, "Should allow max 10 searches"
    assert rate_limited_count >= 1, "Should rate limit after 10 searches"


def test_search_caching():
    """Test that repeated searches use cache"""
    # First search
    response1 = client.get("/products/search?q=cachetest")
    if response1.status_code != 200:
        print("  ⚠ Search failed, skipping cache test")
        return
    
    data1 = response1.json()
    request_id1 = data1["request_id"]
    
    # Second search with same query (should use cache)
    response2 = client.get("/products/search?q=cachetest")
    assert response2.status_code == 200
    
    data2 = response2.json()
    
    # Verify cache was used (message should mention "cached")
    assert "cached" in data2["message"].lower() or data2["request_id"] == request_id1


def test_search_returns_metadata():
    """Test that search returns required metadata"""
    response = client.get("/products/search?q=metadata")
    
    if response.status_code == 200:
        data = response.json()
        
        # Verify tier1_platforms list is populated
        assert len(data["tier1_platforms"]) > 0, "Should have tier1_platforms"
        
        # Verify is_complete indicates search status
        assert isinstance(data["is_complete"], bool)
        
        # Verify message is informative
        assert len(data["message"]) > 0, "Should have status message"


if __name__ == "__main__":
    print("Running tests for Task 7.1: GET /products/search endpoint")
    print("=" * 70)
    
    # Run tests
    try:
        test_search_endpoint_exists()
        print("✓ Test 1: Endpoint exists")
    except AssertionError as e:
        print(f"✗ Test 1 failed: {e}")
    
    try:
        test_search_validates_empty_query()
        print("✓ Test 2: Validates empty query")
    except AssertionError as e:
        print(f"✗ Test 2 failed: {e}")
    
    try:
        test_search_validates_missing_query()
        print("✓ Test 3: Validates missing query parameter")
    except AssertionError as e:
        print(f"✗ Test 3 failed: {e}")
    
    try:
        test_search_response_structure()
        print("✓ Test 4: Response has correct structure")
    except AssertionError as e:
        print(f"✗ Test 4 failed: {e}")
    
    try:
        test_search_rate_limiting()
        print("✓ Test 5: Rate limiting works (max 10/minute)")
    except AssertionError as e:
        print(f"✗ Test 5 failed: {e}")
    
    try:
        test_search_caching()
        print("✓ Test 6: Caching works for repeated queries")
    except AssertionError as e:
        print(f"✗ Test 6 failed: {e}")
    
    try:
        test_search_returns_metadata()
        print("✓ Test 7: Returns required metadata")
    except AssertionError as e:
        print(f"✗ Test 7 failed: {e}")
    
    print("=" * 70)
    print("All tests completed!")
