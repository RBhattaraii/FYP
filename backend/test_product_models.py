"""
Test product Pydantic models
Validates that models correctly parse and validate data
"""

from app.models.product import (
    Product,
    HomeScreenResponse,
    SearchResponse,
    SearchStatusResponse
)


def test_product_model():
    """Test Product model with all fields"""
    product_data = {
        "id": 1,
        "title": "iPhone 15 Pro Max",
        "price": 149999.0,
        "original_price": 199999.0,
        "discount_percent": 25,
        "image_url": "https://example.com/image.jpg",
        "store_name": "Daraz",
        "product_url": "https://example.com/product",
        "category": "Electronics"
    }
    
    product = Product(**product_data)
    
    assert product.id == 1
    assert product.title == "iPhone 15 Pro Max"
    assert product.price == 149999.0
    assert product.original_price == 199999.0
    assert product.discount_percent == 25
    assert product.store_name == "Daraz"
    assert product.category == "Electronics"
    
    print("✅ Product model test passed")


def test_product_model_minimal():
    """Test Product model with only required fields"""
    product_data = {
        "title": "Test Product",
        "price": 1000.0,
        "image_url": "https://example.com/image.jpg",
        "store_name": "Test Store",
        "product_url": "https://example.com/product"
    }
    
    product = Product(**product_data)
    
    assert product.id is None
    assert product.original_price is None
    assert product.discount_percent is None
    assert product.category is None
    assert product.title == "Test Product"
    
    print("✅ Product model minimal test passed")


def test_home_screen_response():
    """Test HomeScreenResponse model"""
    response_data = {
        "best_deals": [
            {
                "id": 1,
                "title": "Product 1",
                "price": 1000.0,
                "image_url": "https://example.com/1.jpg",
                "store_name": "Store 1",
                "product_url": "https://example.com/p1"
            }
        ],
        "top_price_drops": [
            {
                "id": 2,
                "title": "Product 2",
                "price": 2000.0,
                "original_price": 3000.0,
                "discount_percent": 33,
                "image_url": "https://example.com/2.jpg",
                "store_name": "Store 2",
                "product_url": "https://example.com/p2"
            }
        ]
    }
    
    response = HomeScreenResponse(**response_data)
    
    assert len(response.best_deals) == 1
    assert len(response.top_price_drops) == 1
    assert response.best_deals[0].title == "Product 1"
    assert response.top_price_drops[0].discount_percent == 33
    
    print("✅ HomeScreenResponse model test passed")


def test_search_response():
    """Test SearchResponse model"""
    response_data = {
        "request_id": "test-uuid-123",
        "query": "laptop",
        "tier": 1,
        "is_complete": False,
        "results": [
            {
                "title": "Dell Laptop",
                "price": 75000.0,
                "image_url": "https://example.com/dell.jpg",
                "store_name": "Daraz",
                "product_url": "https://example.com/dell"
            }
        ],
        "results_count": 1,
        "tier1_platforms": ["Daraz", "Sastodeal", "Oliz"],
        "message": "Tier 1 results ready"
    }
    
    response = SearchResponse(**response_data)
    
    assert response.request_id == "test-uuid-123"
    assert response.query == "laptop"
    assert response.tier == 1
    assert response.is_complete is False
    assert len(response.results) == 1
    assert response.results_count == 1
    assert len(response.tier1_platforms) == 3
    
    print("✅ SearchResponse model test passed")


def test_search_status_response():
    """Test SearchStatusResponse model"""
    response_data = {
        "request_id": "test-uuid-123",
        "is_complete": True,
        "new_results_count": 45,
        "new_results": [
            {
                "title": "HP Laptop",
                "price": 65000.0,
                "image_url": "https://example.com/hp.jpg",
                "store_name": "Better",
                "product_url": "https://example.com/hp"
            }
        ],
        "message": "All platforms scraped successfully"
    }
    
    response = SearchStatusResponse(**response_data)
    
    assert response.request_id == "test-uuid-123"
    assert response.is_complete is True
    assert response.new_results_count == 45
    assert len(response.new_results) == 1
    assert response.new_results[0].store_name == "Better"
    
    print("✅ SearchStatusResponse model test passed")


def test_empty_response_lists():
    """Test response models with empty lists"""
    home_response = HomeScreenResponse(
        best_deals=[],
        top_price_drops=[]
    )
    
    assert len(home_response.best_deals) == 0
    assert len(home_response.top_price_drops) == 0
    
    status_response = SearchStatusResponse(
        request_id="test-123",
        is_complete=False,
        new_results_count=0,
        new_results=[],
        message="Scraping in progress"
    )
    
    assert len(status_response.new_results) == 0
    
    print("✅ Empty response lists test passed")


if __name__ == "__main__":
    print("Running product model tests...\n")
    
    try:
        test_product_model()
        test_product_model_minimal()
        test_home_screen_response()
        test_search_response()
        test_search_status_response()
        test_empty_response_lists()
        
        print("\n" + "=" * 50)
        print("✅ ALL PRODUCT MODEL TESTS PASSED!")
        print("=" * 50)
        
    except AssertionError as e:
        print(f"\n❌ Test failed: {e}")
        raise
    except Exception as e:
        print(f"\n❌ Unexpected error: {e}")
        raise
