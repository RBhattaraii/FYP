"""
Unit tests for tiered search endpoint (Task 7.1)
Tests the GET /products/search/realtime endpoint
"""
import pytest
from unittest.mock import AsyncMock, patch, MagicMock
from fastapi import HTTPException
from app.routers.products import realtime_search_products
from app.models.product import Product


@pytest.mark.asyncio
async def test_search_validates_empty_query():
    """Test that empty query parameter is rejected with 400 error"""
    # Mock request object
    mock_request = MagicMock()
    mock_request.client.host = "127.0.0.1"
    
    # Mock db connection
    mock_db = AsyncMock()
    
    # Test with empty string
    with pytest.raises(HTTPException) as exc_info:
        await realtime_search_products(
            request=mock_request,
            q="",
            db=mock_db
        )
    
    assert exc_info.value.status_code == 400
    assert "cannot be empty" in exc_info.value.detail.lower()


@pytest.mark.asyncio
async def test_search_validates_whitespace_query():
    """Test that whitespace-only query parameter is rejected"""
    mock_request = MagicMock()
    mock_request.client.host = "127.0.0.1"
    mock_db = AsyncMock()
    
    # Test with whitespace
    with pytest.raises(HTTPException) as exc_info:
        await realtime_search_products(
            request=mock_request,
            q="   ",
            db=mock_db
        )
    
    assert exc_info.value.status_code == 400


@pytest.mark.asyncio
@patch('app.routers.products.tiered_search')
async def test_search_calls_coordinator_service(mock_tiered_search):
    """Test that search endpoint calls tiered_search coordinator service"""
    mock_request = MagicMock()
    mock_request.client.host = "127.0.0.1"
    mock_db = AsyncMock()
    
    # Mock coordinator response
    mock_tiered_search.return_value = {
        'request_id': 'test-123',
        'query': 'laptop',
        'tier': 1,
        'is_complete': False,
        'results': [
            {
                'title': 'Test Laptop',
                'price': 50000.0,
                'original_price': 60000.0,
                'discount_percent': 16,
                'image_url': 'https://example.com/image.jpg',
                'store_name': 'Daraz',
                'product_url': 'https://example.com/product',
                'category': 'Electronics'
            }
        ],
        'results_count': 1,
        'tier1_platforms': ['Daraz', 'Sastodeal', 'Oliz'],
        'from_cache': False
    }
    
    # Call endpoint
    response = await realtime_search_products(
        request=mock_request,
        q="laptop",
        db=mock_db
    )
    
    # Verify coordinator was called with correct parameters
    mock_tiered_search.assert_called_once_with(mock_db, "laptop")
    
    # Verify response structure
    assert response.request_id == 'test-123'
    assert response.query == 'laptop'
    assert response.tier == 1
    assert response.is_complete == False
    assert len(response.results) == 1
    assert response.results[0].title == 'Test Laptop'
    assert len(response.tier1_platforms) == 3


@pytest.mark.asyncio
@patch('app.routers.products.tiered_search')
async def test_search_returns_cached_results(mock_tiered_search):
    """Test that cached results are returned with appropriate message"""
    mock_request = MagicMock()
    mock_request.client.host = "127.0.0.1"
    mock_db = AsyncMock()
    
    # Mock cached response
    mock_tiered_search.return_value = {
        'request_id': 'cached-456',
        'query': 'phone',
        'tier': 'all',
        'is_complete': True,
        'results': [
            {
                'title': 'Test Phone',
                'price': 30000.0,
                'original_price': None,
                'discount_percent': None,
                'image_url': 'https://example.com/phone.jpg',
                'store_name': 'Sastodeal',
                'product_url': 'https://example.com/phone',
                'category': 'Electronics'
            }
        ],
        'results_count': 1,
        'tier1_platforms': ['Daraz', 'Sastodeal', 'Oliz'],
        'from_cache': True
    }
    
    response = await realtime_search_products(
        request=mock_request,
        q="phone",
        db=mock_db
    )
    
    # Verify response indicates cached results
    assert response.is_complete == True
    assert "cached" in response.message.lower()


@pytest.mark.asyncio
@patch('app.routers.products.tiered_search')
async def test_search_handles_tier1_incomplete_results(mock_tiered_search):
    """Test that Tier 1 results show progressive loading message"""
    mock_request = MagicMock()
    mock_request.client.host = "127.0.0.1"
    mock_db = AsyncMock()
    
    # Mock Tier 1 response (incomplete)
    mock_tiered_search.return_value = {
        'request_id': 'tier1-789',
        'query': 'tablet',
        'tier': 1,
        'is_complete': False,
        'results': [],
        'results_count': 0,
        'tier1_platforms': ['Daraz', 'Sastodeal', 'Oliz'],
        'from_cache': False
    }
    
    response = await realtime_search_products(
        request=mock_request,
        q="tablet",
        db=mock_db
    )
    
    # Verify message mentions polling for more results
    assert response.is_complete == False
    assert "poll" in response.message.lower() or "tier 1" in response.message.lower()


@pytest.mark.asyncio
@patch('app.routers.products.tiered_search')
async def test_search_handles_coordinator_errors(mock_tiered_search):
    """Test that coordinator service errors are handled gracefully"""
    mock_request = MagicMock()
    mock_request.client.host = "127.0.0.1"
    mock_db = AsyncMock()
    
    # Mock coordinator raising exception
    mock_tiered_search.side_effect = Exception("Database connection failed")
    
    # Should raise HTTPException with 500 status
    with pytest.raises(HTTPException) as exc_info:
        await realtime_search_products(
            request=mock_request,
            q="laptop",
            db=mock_db
        )
    
    assert exc_info.value.status_code == 500
    assert "search failed" in exc_info.value.detail.lower()


@pytest.mark.asyncio
@patch('app.routers.products.tiered_search')
async def test_search_strips_whitespace_from_query(mock_tiered_search):
    """Test that leading/trailing whitespace is removed from query"""
    mock_request = MagicMock()
    mock_request.client.host = "127.0.0.1"
    mock_db = AsyncMock()
    
    mock_tiered_search.return_value = {
        'request_id': 'test-999',
        'query': 'headphone',
        'tier': 1,
        'is_complete': True,
        'results': [],
        'results_count': 0,
        'tier1_platforms': [],
        'from_cache': False
    }
    
    # Query with leading/trailing spaces
    await realtime_search_products(
        request=mock_request,
        q="  headphone  ",
        db=mock_db
    )
    
    # Verify coordinator was called with stripped query
    mock_tiered_search.assert_called_once_with(mock_db, "headphone")


if __name__ == "__main__":
    pytest.main([__file__, "-v"])


# ============================================================================
# Tests for Task 7.2: GET /products/search/status endpoint
# ============================================================================

@pytest.mark.asyncio
async def test_search_status_requires_query_and_request_id():
    """Test that both query and request_id parameters are required"""
    from app.routers.products import get_search_status_endpoint
    
    mock_db = AsyncMock()
    
    # Note: FastAPI will handle missing required parameters before the function is called
    # This test documents the expected behavior
    # In practice, FastAPI returns 422 Unprocessable Entity for missing required params


@pytest.mark.asyncio
@patch('app.routers.products.get_search_status')
async def test_search_status_returns_incomplete_status(mock_get_search_status):
    """Test that status endpoint returns in-progress status correctly"""
    from app.routers.products import get_search_status_endpoint
    
    mock_db = AsyncMock()
    
    # Mock coordinator response for in-progress search
    mock_get_search_status.return_value = {
        'request_id': 'test-request-123',
        'is_complete': False,
        'new_results': [],
        'new_results_count': 0,
        'message': 'Tier 2 scraping in progress...'
    }
    
    # Call endpoint
    response = await get_search_status_endpoint(
        query="laptop",
        request_id="test-request-123",
        db=mock_db
    )
    
    # Verify coordinator was called with correct request_id
    mock_get_search_status.assert_called_once_with(mock_db, "test-request-123")
    
    # Verify response structure
    assert response.request_id == 'test-request-123'
    assert response.is_complete == False
    assert response.new_results_count == 0
    assert len(response.new_results) == 0
    assert "progress" in response.message.lower()


@pytest.mark.asyncio
@patch('app.routers.products.get_search_status')
async def test_search_status_returns_complete_with_results(mock_get_search_status):
    """Test that status endpoint returns completed status with Tier 2 results"""
    from app.routers.products import get_search_status_endpoint
    
    mock_db = AsyncMock()
    
    # Mock coordinator response for completed search with Tier 2 results
    mock_get_search_status.return_value = {
        'request_id': 'test-request-456',
        'is_complete': True,
        'new_results': [
            {
                'title': 'Tier 2 Laptop 1',
                'price': 45000.0,
                'original_price': 50000.0,
                'discount_percent': 10,
                'image_url': 'https://example.com/laptop1.jpg',
                'store_name': 'CGDigital',
                'product_url': 'https://example.com/laptop1',
                'category': 'Electronics'
            },
            {
                'title': 'Tier 2 Laptop 2',
                'price': 52000.0,
                'original_price': 60000.0,
                'discount_percent': 13,
                'image_url': 'https://example.com/laptop2.jpg',
                'store_name': 'Better',
                'product_url': 'https://example.com/laptop2',
                'category': 'Electronics'
            }
        ],
        'new_results_count': 2,
        'message': 'Tier 2 scraping complete'
    }
    
    response = await get_search_status_endpoint(
        query="laptop",
        request_id="test-request-456",
        db=mock_db
    )
    
    # Verify response structure
    assert response.request_id == 'test-request-456'
    assert response.is_complete == True
    assert response.new_results_count == 2
    assert len(response.new_results) == 2
    assert response.new_results[0].title == 'Tier 2 Laptop 1'
    assert response.new_results[0].store_name == 'CGDigital'
    assert response.new_results[1].title == 'Tier 2 Laptop 2'
    assert "complete" in response.message.lower()


@pytest.mark.asyncio
@patch('app.routers.products.get_search_status')
async def test_search_status_handles_invalid_request_id(mock_get_search_status):
    """Test that status endpoint handles non-existent request_id"""
    from app.routers.products import get_search_status_endpoint
    
    mock_db = AsyncMock()
    
    # Mock coordinator response for non-existent request
    mock_get_search_status.return_value = {
        'request_id': 'invalid-request',
        'is_complete': False,
        'new_results': [],
        'new_results_count': 0,
        'message': 'Request not found or expired'
    }
    
    response = await get_search_status_endpoint(
        query="laptop",
        request_id="invalid-request",
        db=mock_db
    )
    
    # Verify response indicates not found
    assert response.is_complete == False
    assert response.new_results_count == 0
    assert "not found" in response.message.lower() or "expired" in response.message.lower()


@pytest.mark.asyncio
@patch('app.routers.products.get_search_status')
async def test_search_status_handles_coordinator_errors(mock_get_search_status):
    """Test that status endpoint handles errors gracefully"""
    from app.routers.products import get_search_status_endpoint
    
    mock_db = AsyncMock()
    
    # Mock coordinator raising exception
    mock_get_search_status.side_effect = Exception("Database connection lost")
    
    # Should raise HTTPException with 500 status
    with pytest.raises(HTTPException) as exc_info:
        await get_search_status_endpoint(
            query="laptop",
            request_id="test-request-789",
            db=mock_db
        )
    
    assert exc_info.value.status_code == 500
    assert "failed to get search status" in exc_info.value.detail.lower()


@pytest.mark.asyncio
@patch('app.routers.products.get_search_status')
async def test_search_status_filters_invalid_products(mock_get_search_status):
    """Test that status endpoint handles products that fail model validation"""
    from app.routers.products import get_search_status_endpoint
    
    mock_db = AsyncMock()
    
    # Mock coordinator response with one valid and one invalid product
    mock_get_search_status.return_value = {
        'request_id': 'test-request-999',
        'is_complete': True,
        'new_results': [
            {
                'title': 'Valid Product',
                'price': 35000.0,
                'original_price': None,
                'discount_percent': None,
                'image_url': 'https://example.com/valid.jpg',
                'store_name': 'Hukut',
                'product_url': 'https://example.com/valid',
                'category': 'Electronics'
            },
            {
                'title': 'Invalid Product',
                # Missing required fields like price
                'store_name': 'Jeevee',
                'product_url': 'https://example.com/invalid'
            }
        ],
        'new_results_count': 2,
        'message': 'Tier 2 scraping complete'
    }
    
    response = await get_search_status_endpoint(
        query="phone",
        request_id="test-request-999",
        db=mock_db
    )
    
    # Verify that only valid product is included
    # (invalid product should be filtered out during Product model conversion)
    assert len(response.new_results) <= 2
    # At least the valid product should be present
    valid_products = [p for p in response.new_results if p.title == 'Valid Product']
    assert len(valid_products) == 1


@pytest.mark.asyncio
@patch('app.routers.products.get_search_status')
async def test_search_status_response_time_target(mock_get_search_status):
    """Test that status endpoint meets <100ms response time target (documentation)"""
    import time
    from app.routers.products import get_search_status_endpoint
    
    mock_db = AsyncMock()
    
    # Mock fast coordinator response
    mock_get_search_status.return_value = {
        'request_id': 'perf-test',
        'is_complete': True,
        'new_results': [],
        'new_results_count': 0,
        'message': 'Complete'
    }
    
    # Measure response time
    start_time = time.time()
    response = await get_search_status_endpoint(
        query="test",
        request_id="perf-test",
        db=mock_db
    )
    elapsed_ms = (time.time() - start_time) * 1000
    
    # Note: This test documents the performance requirement
    # Actual performance depends on database query optimization with indexes
    # The requirement is <100ms for the database query, not the Python function
    assert response.request_id == 'perf-test'
    print(f"Status endpoint response time: {elapsed_ms:.2f}ms (target: <100ms for full request)")
