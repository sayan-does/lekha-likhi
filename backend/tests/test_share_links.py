import pytest
from fastapi.testclient import TestClient
from unittest.mock import Mock, patch, MagicMock
from uuid import uuid4
import os

# Set environment variables before importing app modules
os.environ["SUPABASE_URL"] = "https://test.supabase.co"
os.environ["SUPABASE_JWT_SECRET"] = "test-secret"
os.environ["UPSTASH_REDIS_URL"] = "https://test.upstash.io"
os.environ["UPSTASH_REDIS_TOKEN"] = "test-token"


@pytest.fixture
def mock_supabase():
    """Mock Supabase client for testing."""
    with patch("app.routers.share_links.get_supabase_client") as mock:
        yield mock.return_value


@pytest.fixture
def mock_rate_limit_service():
    """Mock rate limit service for testing."""
    with patch("app.routers.share_links.get_rate_limit_service") as mock:
        from unittest.mock import AsyncMock
        service = Mock()
        service.invalidate_share_link_cache = AsyncMock()
        mock.return_value = service
        yield service


@pytest.fixture
def mock_user():
    """Create a mock user for testing."""
    user_id = uuid4()
    mock_user_obj = Mock()
    mock_user_obj.id = user_id
    mock_user_obj.email = "test@example.com"
    mock_user_obj.display_name = "Test User"
    mock_user_obj.avatar_url = None
    return mock_user_obj


@pytest.fixture
def client(mock_user):
    """Create test client with mocked auth."""
    from app.main import app
    from app.routers import share_links
    from app.auth import get_current_user
    
    # Mount the router if not already mounted
    if not any(route.path.startswith("/entries") or route.path.startswith("/share-links") for route in app.routes):
        app.include_router(share_links.router)
    
    # Override the dependency
    app.dependency_overrides[get_current_user] = lambda: mock_user
    
    yield TestClient(app)
    
    # Cleanup
    app.dependency_overrides.clear()


def test_create_share_link_for_own_entry(client, mock_supabase, mock_user):
    """Test creating a share link for user's own entry (success)."""
    entry_id = str(uuid4())
    
    # Mock the database responses
    mock_table = MagicMock()
    mock_supabase.table.return_value = mock_table
    
    # Mock entry existence check (entry belongs to user)
    mock_table.select.return_value.eq.return_value.execute.return_value.data = [{
        "id": entry_id,
        "owner_id": str(mock_user.id)
    }]
    
    # Mock share link creation
    with patch("app.routers.share_links.generate_share_token", return_value="test-token-123"):
        mock_table.insert.return_value.execute.return_value.data = [{
            "id": str(uuid4()),
            "entry_id": entry_id,
            "token": "test-token-123",
            "is_active": True,
            "created_at": "2024-01-15T10:00:00"
        }]
        
        response = client.post(f"/entries/{entry_id}/share")
    
    assert response.status_code == 200
    data = response.json()
    assert data["token"] == "test-token-123"
    assert "/shared/" in data["url"]


def test_create_share_link_for_nonexistent_entry(client, mock_supabase, mock_user):
    """Test creating a share link for a nonexistent entry (404)."""
    entry_id = str(uuid4())
    
    # Mock the database responses
    mock_table = MagicMock()
    mock_supabase.table.return_value = mock_table
    
    # Mock entry not found
    mock_table.select.return_value.eq.return_value.execute.return_value.data = []
    
    response = client.post(f"/entries/{entry_id}/share")
    
    assert response.status_code == 404
    assert "not found" in response.json()["detail"].lower()


def test_create_share_link_for_other_users_entry(client, mock_supabase, mock_user):
    """Test creating a share link for someone else's entry (403/404)."""
    entry_id = str(uuid4())
    other_user_id = str(uuid4())
    
    # Mock the database responses
    mock_table = MagicMock()
    mock_supabase.table.return_value = mock_table
    
    # Mock entry exists but belongs to different user
    mock_table.select.return_value.eq.return_value.execute.return_value.data = [{
        "id": entry_id,
        "owner_id": other_user_id
    }]
    
    response = client.post(f"/entries/{entry_id}/share")
    
    # Should return 404 to avoid leaking information
    assert response.status_code == 404


def test_list_share_links(client, mock_supabase, mock_user):
    """Test listing all share links for current user."""
    # Mock the database response
    mock_table = MagicMock()
    mock_supabase.table.return_value = mock_table
    
    mock_share_links = [
        {
            "id": str(uuid4()),
            "entry_id": str(uuid4()),
            "token": "token-1",
            "is_active": True,
            "created_at": "2024-01-15T10:00:00",
            "revoked_at": None,
            "entries": {
                "entry_date": "2024-01-15",
                "owner_id": str(mock_user.id)
            }
        },
        {
            "id": str(uuid4()),
            "entry_id": str(uuid4()),
            "token": "token-2",
            "is_active": False,
            "created_at": "2024-01-14T10:00:00",
            "revoked_at": "2024-01-14T11:00:00",
            "entries": {
                "entry_date": "2024-01-14",
                "owner_id": str(mock_user.id)
            }
        }
    ]
    
    # Create a chain of mocks for the query builder pattern
    mock_query = MagicMock()
    mock_table.select.return_value = mock_query
    mock_query.eq.return_value = mock_query
    mock_query.order.return_value = mock_query
    mock_query.execute.return_value.data = mock_share_links
    
    response = client.get("/share-links")
    
    assert response.status_code == 200
    data = response.json()
    assert len(data) == 2
    assert data[0]["token"] == "token-1"
    assert data[0]["is_active"] is True
    assert data[1]["is_active"] is False


def test_revoke_own_share_link(client, mock_supabase, mock_rate_limit_service, mock_user):
    """Test revoking user's own share link (success)."""
    token = "test-token-to-revoke"
    share_link_id = str(uuid4())
    
    # Mock the database responses
    mock_table = MagicMock()
    mock_supabase.table.return_value = mock_table
    
    # Mock share link lookup with ownership verification
    mock_table.select.return_value.eq.return_value.execute.return_value.data = [{
        "id": share_link_id,
        "entry_id": str(uuid4()),
        "entries": {
            "owner_id": str(mock_user.id)
        }
    }]
    
    # Mock update response
    mock_table.update.return_value.eq.return_value.execute.return_value = Mock()
    
    response = client.delete(f"/share-links/{token}")
    
    assert response.status_code == 204
    
    # Verify cache was invalidated
    mock_rate_limit_service.invalidate_share_link_cache.assert_called_once_with(token)


def test_revoke_nonexistent_share_link(client, mock_supabase, mock_rate_limit_service, mock_user):
    """Test revoking a nonexistent share link (404)."""
    token = "nonexistent-token"
    
    # Mock the database responses
    mock_table = MagicMock()
    mock_supabase.table.return_value = mock_table
    
    # Mock share link not found
    mock_table.select.return_value.eq.return_value.execute.return_value.data = []
    
    response = client.delete(f"/share-links/{token}")
    
    assert response.status_code == 404


def test_revoke_other_users_share_link(client, mock_supabase, mock_rate_limit_service, mock_user):
    """Test revoking someone else's share link (404)."""
    token = "other-user-token"
    other_user_id = str(uuid4())
    
    # Mock the database responses
    mock_table = MagicMock()
    mock_supabase.table.return_value = mock_table
    
    # Mock share link exists but belongs to different user
    mock_table.select.return_value.eq.return_value.execute.return_value.data = [{
        "id": str(uuid4()),
        "entry_id": str(uuid4()),
        "entries": {
            "owner_id": other_user_id
        }
    }]
    
    response = client.delete(f"/share-links/{token}")
    
    # Should return 404 to avoid leaking information
    assert response.status_code == 404
