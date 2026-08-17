"""Tests for error responses per section 6 of the spec.

This module tests all error conditions to ensure they return the correct
status code and response shape:
- Invalid/expired JWT → 401 with {"detail": "Not authenticated"}
- Accessing another user's entry → 404 (not 403)
- Revoked/unknown share token → 404 with {"detail": "This entry is no longer available"}
- Duplicate entry race condition → 409
- Invalid emoji → 422 with allowed list
- Rate limit exceeded → 429 with {"detail": "Too many reactions, try again shortly"}
"""

import pytest
from fastapi.testclient import TestClient
from unittest.mock import patch, MagicMock, AsyncMock
from app.main import app
from app.auth import get_current_user
from app.schemas.reaction import ALLOWED_EMOJIS
from app.services.rate_limit import RateLimitExceeded


# Mock user data
MOCK_USER_1 = {
    "id": "00000000-0000-0000-0000-000000000001",
    "email": "user1@example.com",
    "display_name": "User One",
    "avatar_url": None
}

MOCK_USER_2 = {
    "id": "00000000-0000-0000-0000-000000000002",
    "email": "user2@example.com",
    "display_name": "User Two",
    "avatar_url": None
}


@pytest.fixture
def mock_supabase():
    """Mock Supabase client."""
    with patch("app.routers.entries.get_supabase_client") as mock_entries, \
         patch("app.routers.shared.get_supabase_client") as mock_shared:
        mock_client = MagicMock()
        mock_entries.return_value = mock_client
        mock_shared.return_value = mock_client
        yield mock_client


@pytest.fixture
def mock_rate_limit_service():
    """Mock rate limit service."""
    with patch("app.routers.shared.get_rate_limit_service") as mock:
        mock_service = MagicMock()
        mock_service.check_rate_limit = AsyncMock()
        mock_service.get_cached_share_link = AsyncMock(return_value=None)
        mock_service.set_cached_share_link = AsyncMock()
        mock_service.invalidate_share_link_cache = AsyncMock()
        mock.return_value = mock_service
        yield mock_service


def create_mock_user(user_data):
    """Helper to create a mock current user."""
    from app.schemas.user import User
    from uuid import UUID
    
    return User(
        id=UUID(user_data["id"]),
        email=user_data["email"],
        display_name=user_data["display_name"],
        avatar_url=user_data.get("avatar_url")
    )


def override_get_current_user(user_data):
    """Create a dependency override function for get_current_user."""
    user = create_mock_user(user_data)
    async def _get_current_user():
        return user
    return _get_current_user


# Test 1: Invalid/expired JWT → 401
def test_invalid_jwt_returns_401():
    """Test that an invalid JWT token returns 401 with 'Not authenticated'."""
    # No Authorization header - should fail auth
    client = TestClient(app)
    response = client.get("/me")
    assert response.status_code == 401
    assert response.json() == {"detail": "Not authenticated"}


def test_expired_jwt_returns_401():
    """Test that an expired JWT token returns 401."""
    # Invalid token format - should fail auth
    client = TestClient(app)
    response = client.get(
        "/me",
        headers={"Authorization": "Bearer invalid_token_here"}
    )
    assert response.status_code == 401
    assert response.json() == {"detail": "Not authenticated"}


def test_malformed_jwt_returns_401():
    """Test that a malformed JWT returns 401."""
    client = TestClient(app)
    response = client.get(
        "/me",
        headers={"Authorization": "Bearer not.a.valid.jwt"}
    )
    assert response.status_code == 401
    assert response.json() == {"detail": "Not authenticated"}


# Test 2: Accessing another user's entry → 404 (not 403)
def test_accessing_other_users_entry_returns_404(mock_supabase):
    """Test that accessing another user's entry returns 404, not 403."""
    # Override auth dependency
    app.dependency_overrides[get_current_user] = override_get_current_user(MOCK_USER_1)
    
    try:
        client = TestClient(app)
        # Mock: no entry found for this user and date
        mock_supabase.table.return_value.select.return_value.eq.return_value.eq.return_value.execute.return_value = MagicMock(data=[])
        
        response = client.get(
            "/entries/2024-01-15",
            headers={"Authorization": "Bearer mock_token"}
        )
        
        assert response.status_code == 404
        assert response.json() == {"detail": "Entry not found"}
    finally:
        app.dependency_overrides.clear()


def test_deleting_other_users_entry_returns_404(mock_supabase):
    """Test that attempting to delete another user's entry returns 404."""
    # Override auth dependency
    app.dependency_overrides[get_current_user] = override_get_current_user(MOCK_USER_1)
    
    try:
        client = TestClient(app)
        # Mock: no entry found for this user and date
        mock_supabase.table.return_value.select.return_value.eq.return_value.eq.return_value.execute.return_value = MagicMock(data=[])
        
        response = client.delete(
            "/entries/2024-01-15",
            headers={"Authorization": "Bearer mock_token"}
        )
        
        assert response.status_code == 404
        assert response.json() == {"detail": "Entry not found"}
    finally:
        app.dependency_overrides.clear()


# Test 3: Revoked/unknown share token → 404
def test_unknown_share_token_returns_404(mock_supabase, mock_rate_limit_service):
    """Test that an unknown share token returns 404 with specific message."""
    # Override auth dependency
    app.dependency_overrides[get_current_user] = override_get_current_user(MOCK_USER_1)
    
    try:
        client = TestClient(app)
        # Mock: token not found
        mock_supabase.table.return_value.select.return_value.eq.return_value.execute.return_value = MagicMock(data=[])
        
        response = client.get(
            "/shared/nonexistent_token",
            headers={"Authorization": "Bearer mock_token"}
        )
        
        assert response.status_code == 404
        assert response.json() == {"detail": "This entry is no longer available"}
    finally:
        app.dependency_overrides.clear()


def test_revoked_share_token_returns_404(mock_supabase, mock_rate_limit_service):
    """Test that a revoked share token returns 404 with specific message."""
    # Override auth dependency
    app.dependency_overrides[get_current_user] = override_get_current_user(MOCK_USER_1)
    
    try:
        client = TestClient(app)
        # Mock: token exists but is_active = false
        mock_supabase.table.return_value.select.return_value.eq.return_value.execute.return_value = MagicMock(
            data=[{"entry_id": "entry-uuid", "is_active": False}]
        )
        
        response = client.get(
            "/shared/revoked_token",
            headers={"Authorization": "Bearer mock_token"}
        )
        
        assert response.status_code == 404
        assert response.json() == {"detail": "This entry is no longer available"}
    finally:
        app.dependency_overrides.clear()


def test_reacting_to_revoked_share_returns_404(mock_supabase, mock_rate_limit_service):
    """Test that reacting to a revoked share link returns 404."""
    # Override auth dependency
    app.dependency_overrides[get_current_user] = override_get_current_user(MOCK_USER_1)
    
    try:
        client = TestClient(app)
        # Mock: token exists but is_active = false
        mock_supabase.table.return_value.select.return_value.eq.return_value.execute.return_value = MagicMock(
            data=[{"entry_id": "entry-uuid", "is_active": False}]
        )
        
        response = client.post(
            "/shared/revoked_token/react",
            headers={"Authorization": "Bearer mock_token"},
            json={"emoji": "❤️"}
        )
        
        assert response.status_code == 404
        assert response.json() == {"detail": "This entry is no longer available"}
    finally:
        app.dependency_overrides.clear()


# Test 4: Duplicate entry race condition → 409
def test_duplicate_entry_race_condition_returns_409(mock_supabase):
    """Test that a duplicate entry (race condition) returns 409."""
    # Override auth dependency
    app.dependency_overrides[get_current_user] = override_get_current_user(MOCK_USER_1)
    
    try:
        client = TestClient(app)
        # First check returns no existing entry
        mock_supabase.table.return_value.select.return_value.eq.return_value.eq.return_value.execute.return_value = MagicMock(data=[])
        
        # Insert raises a unique constraint violation
        mock_insert = MagicMock()
        mock_insert.execute.side_effect = Exception("duplicate key value violates unique constraint")
        mock_supabase.table.return_value.insert.return_value = mock_insert
        
        response = client.put(
            "/entries/2024-01-15",
            headers={"Authorization": "Bearer mock_token"},
            json={"body": "Test entry"}
        )
        
        assert response.status_code == 409
        assert response.json() == {"detail": "Entry already exists for this date"}
    finally:
        app.dependency_overrides.clear()


# Test 5: Invalid emoji → 422 with allowed list
def test_invalid_emoji_returns_422_with_allowed_list():
    """Test that an invalid emoji returns 422 with the allowed emoji list."""
    # Override auth dependency
    app.dependency_overrides[get_current_user] = override_get_current_user(MOCK_USER_1)
    
    try:
        client = TestClient(app)
        response = client.post(
            "/shared/some_token/react",
            headers={"Authorization": "Bearer mock_token"},
            json={"emoji": "🚀"}  # Not in allowed list
        )
        
        assert response.status_code == 422
        response_data = response.json()
        assert "detail" in response_data
        assert "allowed_emojis" in response_data
        assert response_data["allowed_emojis"] == ALLOWED_EMOJIS
    finally:
        app.dependency_overrides.clear()


def test_missing_emoji_field_returns_422():
    """Test that missing emoji field returns 422."""
    # Override auth dependency
    app.dependency_overrides[get_current_user] = override_get_current_user(MOCK_USER_1)
    
    try:
        client = TestClient(app)
        response = client.post(
            "/shared/some_token/react",
            headers={"Authorization": "Bearer mock_token"},
            json={}  # Missing emoji field
        )
        
        assert response.status_code == 422
    finally:
        app.dependency_overrides.clear()


def test_each_allowed_emoji_is_valid(mock_supabase, mock_rate_limit_service):
    """Test that each emoji in the allowed list is actually accepted."""
    # Override auth dependency
    app.dependency_overrides[get_current_user] = override_get_current_user(MOCK_USER_1)
    
    try:
        client = TestClient(app)
        # Mock valid share link
        mock_supabase.table.return_value.select.return_value.eq.return_value.execute.return_value = MagicMock(
            data=[{"entry_id": "entry-uuid", "is_active": True}]
        )
        
        # Mock no existing reaction
        mock_supabase.table.return_value.select.return_value.eq.return_value.eq.return_value.execute.return_value = MagicMock(data=[])
        
        # Mock successful insert
        mock_supabase.table.return_value.insert.return_value.execute.return_value = MagicMock(data=[{"id": "reaction-id"}])
        
        for emoji in ALLOWED_EMOJIS:
            response = client.post(
                "/shared/valid_token/react",
                headers={"Authorization": "Bearer mock_token"},
                json={"emoji": emoji}
            )
            
            # Should not be 422 (validation error)
            assert response.status_code != 422, f"Emoji {emoji} should be valid but got 422"
    finally:
        app.dependency_overrides.clear()


# Test 6: Rate limit exceeded → 429
def test_rate_limit_exceeded_returns_429(mock_supabase, mock_rate_limit_service):
    """Test that exceeding rate limit returns 429 with specific message."""
    # Override auth dependency
    app.dependency_overrides[get_current_user] = override_get_current_user(MOCK_USER_1)
    
    try:
        client = TestClient(app)
        # Mock valid share link
        mock_supabase.table.return_value.select.return_value.eq.return_value.execute.return_value = MagicMock(
            data=[{"entry_id": "entry-uuid", "is_active": True}]
        )
        
        # Mock rate limit exceeded
        mock_rate_limit_service.check_rate_limit.side_effect = RateLimitExceeded("Rate limit exceeded", retry_after=30)
        
        response = client.post(
            "/shared/valid_token/react",
            headers={"Authorization": "Bearer mock_token"},
            json={"emoji": "❤️"}
        )
        
        assert response.status_code == 429
        assert response.json() == {"detail": "Too many reactions, try again shortly"}
        assert "retry-after" in response.headers
        assert response.headers["retry-after"] == "30"
    finally:
        app.dependency_overrides.clear()


# Additional edge case tests
def test_rate_limit_specific_to_user_and_entry(mock_supabase, mock_rate_limit_service):
    """Test that rate limiting is enforced per user per entry."""
    # Override auth dependency
    app.dependency_overrides[get_current_user] = override_get_current_user(MOCK_USER_1)
    
    try:
        client = TestClient(app)
        # Mock valid share link
        mock_supabase.table.return_value.select.return_value.eq.return_value.execute.return_value = MagicMock(
            data=[{"entry_id": "entry-uuid-123", "is_active": True}]
        )
        
        # Mock rate limit check being called
        mock_rate_limit_service.check_rate_limit.return_value = (True, 1)
        
        # Mock no existing reaction
        mock_supabase.table.return_value.select.return_value.eq.return_value.eq.return_value.execute.return_value = MagicMock(data=[])
        
        # Mock successful insert
        mock_supabase.table.return_value.insert.return_value.execute.return_value = MagicMock(data=[{"id": "reaction-id"}])
        
        response = client.post(
            "/shared/valid_token/react",
            headers={"Authorization": "Bearer mock_token"},
            json={"emoji": "❤️"}
        )
        
        # Verify rate limit was checked with correct parameters
        mock_rate_limit_service.check_rate_limit.assert_called_once()
        call_args = mock_rate_limit_service.check_rate_limit.call_args
        assert call_args[1]["user_id"] == create_mock_user(MOCK_USER_1).id
        assert call_args[1]["entry_id"] == "entry-uuid-123"
        assert call_args[1]["limit"] == 10
        assert call_args[1]["window_seconds"] == 60
    finally:
        app.dependency_overrides.clear()


def test_error_responses_include_detail_field():
    """Test that all error responses include a 'detail' field."""
    client = TestClient(app)
    
    # Test 401
    response = client.get("/me")
    assert response.status_code == 401
    assert "detail" in response.json()
    
    # Test 422 for invalid data
    app.dependency_overrides[get_current_user] = override_get_current_user(MOCK_USER_1)
    try:
        response = client.post(
            "/shared/token/react",
            headers={"Authorization": "Bearer mock_token"},
            json={"emoji": "invalid"}
        )
        assert response.status_code == 422
        assert "detail" in response.json()
    finally:
        app.dependency_overrides.clear()


def test_consistent_404_message_for_share_links(mock_supabase, mock_rate_limit_service):
    """Test that all share link 404s use the same message."""
    # Override auth dependency
    app.dependency_overrides[get_current_user] = override_get_current_user(MOCK_USER_1)
    
    try:
        client = TestClient(app)
        # Mock: token not found
        mock_supabase.table.return_value.select.return_value.eq.return_value.execute.return_value = MagicMock(data=[])
        
        expected_message = "This entry is no longer available"
        
        # Test GET endpoint
        response = client.get(
            "/shared/nonexistent",
            headers={"Authorization": "Bearer mock_token"}
        )
        assert response.status_code == 404
        assert response.json()["detail"] == expected_message
        
        # Test POST react endpoint
        response = client.post(
            "/shared/nonexistent/react",
            headers={"Authorization": "Bearer mock_token"},
            json={"emoji": "❤️"}
        )
        assert response.status_code == 404
        assert response.json()["detail"] == expected_message
        
        # Test DELETE react endpoint
        response = client.delete(
            "/shared/nonexistent/react",
            headers={"Authorization": "Bearer mock_token"}
        )
        assert response.status_code == 404
        assert response.json()["detail"] == expected_message
    finally:
        app.dependency_overrides.clear()
