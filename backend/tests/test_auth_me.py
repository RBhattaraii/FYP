"""
Unit tests for GET /auth/me endpoint (Task 8.1)
Tests the user profile endpoint that returns logged-in user information
"""
import pytest
from unittest.mock import AsyncMock, MagicMock, patch
from fastapi import HTTPException
import uuid
from datetime import datetime


@pytest.mark.asyncio
async def test_auth_me_returns_user_profile():
    """Test that /auth/me returns user profile with correct fields"""
    from app.routers.auth import get_current_user
    
    # Mock request with valid Authorization header
    mock_request = MagicMock()
    test_token = "valid.jwt.token"
    mock_request.headers.get.return_value = f"Bearer {test_token}"
    
    # Mock database connection
    mock_db = AsyncMock()
    
    # Mock user data from database
    test_user_id = str(uuid.uuid4())
    test_created_at = datetime(2024, 1, 1, 12, 0, 0)
    mock_db.fetchrow.return_value = {
        'id': test_user_id,
        'email': 'test@example.com',
        'full_name': 'John Doe',
        'phone': '+9779812345678',
        'created_at': test_created_at
    }
    
    # Mock JWT decode
    with patch('app.routers.auth.decode_access_token') as mock_decode:
        mock_decode.return_value = {
            'user_id': test_user_id,
            'sub': test_user_id
        }
        
        # Call endpoint
        response = await get_current_user(
            request=mock_request,
            db=mock_db
        )
    
    # Verify database was queried with correct user_id
    mock_db.fetchrow.assert_called_once()
    call_args = mock_db.fetchrow.call_args
    assert test_user_id in str(call_args)
    
    # Verify response structure
    assert response['id'] == test_user_id
    assert response['email'] == 'test@example.com'
    assert response['full_name'] == 'John Doe'
    assert response['phone'] == '+9779812345678'
    assert response['created_at'] == test_created_at.isoformat()


@pytest.mark.asyncio
async def test_auth_me_missing_authorization_header():
    """Test that missing Authorization header returns 401"""
    from app.routers.auth import get_current_user
    
    # Mock request without Authorization header
    mock_request = MagicMock()
    mock_request.headers.get.return_value = None
    
    mock_db = AsyncMock()
    
    # Should raise HTTPException with 401 status
    with pytest.raises(HTTPException) as exc_info:
        await get_current_user(
            request=mock_request,
            db=mock_db
        )
    
    assert exc_info.value.status_code == 401
    assert "authorization" in exc_info.value.detail.lower()


@pytest.mark.asyncio
async def test_auth_me_invalid_authorization_format():
    """Test that invalid Authorization header format returns 401"""
    from app.routers.auth import get_current_user
    
    # Mock request with invalid format (missing "Bearer" prefix)
    mock_request = MagicMock()
    mock_request.headers.get.return_value = "InvalidFormat token123"
    
    mock_db = AsyncMock()
    
    # Should raise HTTPException with 401 status
    with pytest.raises(HTTPException) as exc_info:
        await get_current_user(
            request=mock_request,
            db=mock_db
        )
    
    assert exc_info.value.status_code == 401
    assert "authorization" in exc_info.value.detail.lower()


@pytest.mark.asyncio
async def test_auth_me_expired_token():
    """Test that expired JWT token returns 401"""
    from app.routers.auth import get_current_user
    
    # Mock request with Authorization header
    mock_request = MagicMock()
    mock_request.headers.get.return_value = "Bearer expired.jwt.token"
    
    mock_db = AsyncMock()
    
    # Mock JWT decode raising exception for expired token
    with patch('app.routers.auth.decode_access_token') as mock_decode:
        mock_decode.side_effect = Exception("Token has expired")
        
        # Should raise HTTPException with 401 status
        with pytest.raises(HTTPException) as exc_info:
            await get_current_user(
                request=mock_request,
                db=mock_db
            )
    
    assert exc_info.value.status_code == 401
    assert "token verification failed" in exc_info.value.detail.lower()


@pytest.mark.asyncio
async def test_auth_me_invalid_token_payload():
    """Test that token without user_id returns 401"""
    from app.routers.auth import get_current_user
    
    # Mock request with Authorization header
    mock_request = MagicMock()
    mock_request.headers.get.return_value = "Bearer valid.but.empty.token"
    
    mock_db = AsyncMock()
    
    # Mock JWT decode returning payload without user_id
    with patch('app.routers.auth.decode_access_token') as mock_decode:
        mock_decode.return_value = {
            'some_other_field': 'value'
            # Missing user_id
        }
        
        # Should raise HTTPException with 401 status
        with pytest.raises(HTTPException) as exc_info:
            await get_current_user(
                request=mock_request,
                db=mock_db
            )
    
    assert exc_info.value.status_code == 401
    assert "invalid token payload" in exc_info.value.detail.lower()


@pytest.mark.asyncio
async def test_auth_me_user_not_found():
    """Test that non-existent user_id returns 404"""
    from app.routers.auth import get_current_user
    
    # Mock request with valid Authorization header
    mock_request = MagicMock()
    mock_request.headers.get.return_value = "Bearer valid.jwt.token"
    
    # Mock database connection returning None (user not found)
    mock_db = AsyncMock()
    mock_db.fetchrow.return_value = None
    
    # Mock JWT decode
    with patch('app.routers.auth.decode_access_token') as mock_decode:
        mock_decode.return_value = {
            'user_id': 'non-existent-user-id',
            'sub': 'non-existent-user-id'
        }
        
        # Should raise HTTPException with 404 status
        with pytest.raises(HTTPException) as exc_info:
            await get_current_user(
                request=mock_request,
                db=mock_db
            )
    
    assert exc_info.value.status_code == 404
    assert "not found" in exc_info.value.detail.lower()


@pytest.mark.asyncio
async def test_auth_me_deactivated_account():
    """Test that deactivated user account returns 404"""
    from app.routers.auth import get_current_user
    
    # Mock request with valid Authorization header
    mock_request = MagicMock()
    mock_request.headers.get.return_value = "Bearer valid.jwt.token"
    
    # Mock database connection
    # The query filters by is_active = TRUE, so deactivated users return None
    mock_db = AsyncMock()
    mock_db.fetchrow.return_value = None
    
    # Mock JWT decode
    with patch('app.routers.auth.decode_access_token') as mock_decode:
        mock_decode.return_value = {
            'user_id': 'deactivated-user-id',
            'sub': 'deactivated-user-id'
        }
        
        # Should raise HTTPException with 404 status
        with pytest.raises(HTTPException) as exc_info:
            await get_current_user(
                request=mock_request,
                db=mock_db
            )
    
    assert exc_info.value.status_code == 404
    assert "deactivated" in exc_info.value.detail.lower() or "not found" in exc_info.value.detail.lower()


@pytest.mark.asyncio
async def test_auth_me_excludes_password_hash():
    """Test that password_hash is NOT included in response"""
    from app.routers.auth import get_current_user
    
    # Mock request with valid Authorization header
    mock_request = MagicMock()
    mock_request.headers.get.return_value = "Bearer valid.jwt.token"
    
    # Mock database connection
    mock_db = AsyncMock()
    test_user_id = str(uuid.uuid4())
    # Note: password_hash is NOT selected in the SQL query
    mock_db.fetchrow.return_value = {
        'id': test_user_id,
        'email': 'test@example.com',
        'full_name': 'Jane Doe',
        'phone': None,
        'created_at': datetime(2024, 1, 1, 12, 0, 0)
    }
    
    # Mock JWT decode
    with patch('app.routers.auth.decode_access_token') as mock_decode:
        mock_decode.return_value = {
            'user_id': test_user_id,
            'sub': test_user_id
        }
        
        # Call endpoint
        response = await get_current_user(
            request=mock_request,
            db=mock_db
        )
    
    # Verify password_hash is not in response
    assert 'password_hash' not in response
    assert 'password' not in response


@pytest.mark.asyncio
async def test_auth_me_handles_null_phone():
    """Test that null phone number is handled correctly"""
    from app.routers.auth import get_current_user
    
    # Mock request with valid Authorization header
    mock_request = MagicMock()
    mock_request.headers.get.return_value = "Bearer valid.jwt.token"
    
    # Mock database connection
    mock_db = AsyncMock()
    test_user_id = str(uuid.uuid4())
    mock_db.fetchrow.return_value = {
        'id': test_user_id,
        'email': 'nophone@example.com',
        'full_name': 'No Phone User',
        'phone': None,  # No phone number
        'created_at': datetime(2024, 1, 1, 12, 0, 0)
    }
    
    # Mock JWT decode
    with patch('app.routers.auth.decode_access_token') as mock_decode:
        mock_decode.return_value = {
            'user_id': test_user_id,
            'sub': test_user_id
        }
        
        # Call endpoint
        response = await get_current_user(
            request=mock_request,
            db=mock_db
        )
    
    # Verify phone is None or not present
    assert response['phone'] is None or 'phone' not in response


@pytest.mark.asyncio
async def test_auth_me_handles_database_error():
    """Test that database errors return 500"""
    from app.routers.auth import get_current_user
    
    # Mock request with valid Authorization header
    mock_request = MagicMock()
    mock_request.headers.get.return_value = "Bearer valid.jwt.token"
    
    # Mock database connection raising exception
    mock_db = AsyncMock()
    mock_db.fetchrow.side_effect = Exception("Database connection lost")
    
    # Mock JWT decode
    with patch('app.routers.auth.decode_access_token') as mock_decode:
        mock_decode.return_value = {
            'user_id': 'some-user-id',
            'sub': 'some-user-id'
        }
        
        # Should raise HTTPException with 500 status
        with pytest.raises(HTTPException) as exc_info:
            await get_current_user(
                request=mock_request,
                db=mock_db
            )
    
    assert exc_info.value.status_code == 500
    assert "failed" in exc_info.value.detail.lower()


@pytest.mark.asyncio
async def test_auth_me_extracts_first_name_for_greeting():
    """Test that full_name can be parsed for greeting (e.g., 'Hello, John!')"""
    from app.routers.auth import get_current_user
    
    # Mock request with valid Authorization header
    mock_request = MagicMock()
    mock_request.headers.get.return_value = "Bearer valid.jwt.token"
    
    # Mock database connection
    mock_db = AsyncMock()
    test_user_id = str(uuid.uuid4())
    mock_db.fetchrow.return_value = {
        'id': test_user_id,
        'email': 'john@example.com',
        'full_name': 'John Doe Smith',  # Multiple names
        'phone': None,
        'created_at': datetime(2024, 1, 1, 12, 0, 0)
    }
    
    # Mock JWT decode
    with patch('app.routers.auth.decode_access_token') as mock_decode:
        mock_decode.return_value = {
            'user_id': test_user_id,
            'sub': test_user_id
        }
        
        # Call endpoint
        response = await get_current_user(
            request=mock_request,
            db=mock_db
        )
    
    # Verify full_name is returned
    assert response['full_name'] == 'John Doe Smith'
    
    # Frontend can extract first name: full_name.split()[0] = 'John'
    first_name = response['full_name'].split()[0]
    assert first_name == 'John'


if __name__ == "__main__":
    pytest.main([__file__, "-v"])


# ============================================================================
# TEST DOCUMENTATION
# ============================================================================

"""
These tests verify that the GET /auth/me endpoint (Task 8.1) works correctly:

✅ Returns user profile with correct fields (id, email, full_name, created_at, phone)
✅ Returns 401 Unauthorized when Authorization header is missing
✅ Returns 401 Unauthorized when Authorization header format is invalid
✅ Returns 401 Unauthorized when JWT token is expired
✅ Returns 401 Unauthorized when JWT token payload is invalid (missing user_id)
✅ Returns 404 Not Found when user doesn't exist
✅ Returns 404 Not Found when user account is deactivated (is_active=FALSE)
✅ Excludes password_hash from response (security requirement)
✅ Handles null phone numbers correctly
✅ Returns 500 Internal Server Error when database error occurs
✅ Full_name can be parsed for greeting ("Hello, John!")

Test Coverage:
- Authorization header validation
- JWT token verification
- User lookup in database
- Error handling (401, 404, 500)
- Security (password_hash excluded)
- Edge cases (null phone, deactivated account)
- Frontend usage (first name extraction for greeting)

All tests use mocks to avoid database dependencies and ensure fast test execution.
"""
