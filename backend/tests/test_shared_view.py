"""Tests for shared entry viewing endpoint (Task 5)."""

import pytest
from fastapi.testclient import TestClient
from unittest.mock import Mock, patch, MagicMock, AsyncMock
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
    with patch("app.routers.shared.get_supabase_client") as mock:
        yield mock.return_value


@pytest.fixture
def mock_rate_limit_service():
    """Mock rate limit service for testing."""
    with patch("app.routers.shared.get_rate_limit_service") as mock:
        service = Mock()
        service.get_cached_share_link = AsyncMock(return_value=None)
        service.set_cached_share_link = AsyncMock()
        mock.return_value = service
        yield service


@pytest.fixture
def mock_user():
    """Create a mock user for testing."""
    user_id = uuid4()
    mock_user_obj = Mock()
    mock_user_obj.id = user_id
    mock_user_obj.email = "viewer@example.com"
    mock_user_obj.display_name = "Viewer User"
    mock_user_obj.avatar_url = None
    return mock_user_obj


@pytest.fixture
def client(mock_user):
    """Create test client with mocked auth."""
    from app.main import app
    from app.auth import get_current_user
    
    # Override the dependency
    app.dependency_overrides[get_current_user] = lambda: mock_user
    
    yield TestClient(app)
    
    # Cleanup
    app.dependency_overrides.clear()


def test_get_shared_entry_with_valid_active_token(
    client, mock_supabase, mock_rate_limit_service, mock_user
):
    """Test viewing a shared entry with a valid, active token returns entry + reactions."""
    token = "valid-test-token"
    entry_id = str(uuid4())
    owner_id = str(uuid4())
    
    # Mock the database responses
    mock_table = MagicMock()
    mock_supabase.table.return_value = mock_table
    
    # Mock share link lookup
    def mock_select(*args, **kwargs):
        query = MagicMock()
        query.eq.return_value.execute.return_value.data = [{
            "entry_id": entry_id,
            "is_active": True
        }]
        return query
    mock_table.select.side_effect = mock_select
    
    # Mock entry lookup with owner
    entry_query = MagicMock()
    entry_query.eq.return_value.execute.return_value.data = [{
        "entry_date": "2024-01-15",
        "body": "This is a shared journal entry",
        "owner_id": owner_id,
        "users": {
            "display_name": "Entry Owner"
        }
    }]
    
    # Mock reactions lookup
    reactions_query = MagicMock()
    reactions_query.eq.return_value.execute.return_value.data = [
        {
            "emoji": "❤️",
            "user_id": str(uuid4()),
            "users": {"display_name": "Reactor 1"}
        },
        {
            "emoji": "😂",
            "user_id": str(uuid4()),
            "users": {"display_name": "Reactor 2"}
        }
    ]
    
    # Set up table mock to return different queries
    call_count = [0]
    def mock_table_select(*args, **kwargs):
        call_count[0] += 1
        if call_count[0] == 1:
            return mock_select(*args, **kwargs)
        elif call_count[0] == 2:
            return entry_query
        else:
            return reactions_query
    
    mock_table.select.side_effect = mock_table_select
    
    response = client.get(f"/shared/{token}")
    
    assert response.status_code == 200
    data = response.json()
    assert data["entry_date"] == "2024-01-15"
    assert data["body"] == "This is a shared journal entry"
    assert data["owner_display_name"] == "Entry Owner"
    assert len(data["reactions"]) == 2
    assert data["reactions"][0]["emoji"] == "❤️"
    assert data["reactions"][0]["display_name"] == "Reactor 1"
    assert data["reactions"][1]["emoji"] == "😂"
    assert data["reactions"][1]["display_name"] == "Reactor 2"


def test_get_shared_entry_with_revoked_token(
    client, mock_supabase, mock_rate_limit_service, mock_user
):
    """Test that a revoked token returns 404."""
    token = "revoked-test-token"
    
    # Mock the database responses
    mock_table = MagicMock()
    mock_supabase.table.return_value = mock_table
    
    # Mock share link lookup - revoked
    mock_query = MagicMock()
    mock_query.eq.return_value.execute.return_value.data = [{
        "entry_id": str(uuid4()),
        "is_active": False  # Revoked
    }]
    mock_table.select.return_value = mock_query
    
    response = client.get(f"/shared/{token}")
    
    assert response.status_code == 404
    assert "no longer available" in response.json()["detail"].lower()


def test_get_shared_entry_with_nonexistent_token(
    client, mock_supabase, mock_rate_limit_service, mock_user
):
    """Test that a nonexistent token returns 404."""
    token = "nonexistent-token"
    
    # Mock the database responses
    mock_table = MagicMock()
    mock_supabase.table.return_value = mock_table
    
    # Mock share link lookup - not found
    mock_query = MagicMock()
    mock_query.eq.return_value.execute.return_value.data = []
    mock_table.select.return_value = mock_query
    
    response = client.get(f"/shared/{token}")
    
    assert response.status_code == 404
    assert "no longer available" in response.json()["detail"].lower()


def test_get_shared_entry_uses_cache(
    client, mock_supabase, mock_rate_limit_service, mock_user
):
    """Test that the endpoint uses Redis cache for share link resolution."""
    token = "cached-token"
    entry_id = str(uuid4())
    
    # Mock cache hit
    mock_rate_limit_service.get_cached_share_link.return_value = {
        "entry_id": entry_id,
        "is_active": True
    }
    
    # Mock the database responses for entry and reactions
    mock_table = MagicMock()
    mock_supabase.table.return_value = mock_table
    
    # Mock entry lookup
    entry_query = MagicMock()
    entry_query.eq.return_value.execute.return_value.data = [{
        "entry_date": "2024-01-15",
        "body": "Cached entry",
        "owner_id": str(uuid4()),
        "users": {"display_name": "Owner"}
    }]
    
    # Mock reactions lookup
    reactions_query = MagicMock()
    reactions_query.eq.return_value.execute.return_value.data = []
    
    call_count = [0]
    def mock_table_select(*args, **kwargs):
        call_count[0] += 1
        if call_count[0] == 1:
            return entry_query
        else:
            return reactions_query
    
    mock_table.select.side_effect = mock_table_select
    
    response = client.get(f"/shared/{token}")
    
    assert response.status_code == 200
    # Verify cache was checked
    mock_rate_limit_service.get_cached_share_link.assert_called_once_with(token)


def test_get_shared_entry_falls_back_when_cache_is_poisoned_string(
    client, mock_supabase, mock_rate_limit_service, mock_user
):
    """A double-encoded cache value must not 500; fall back to the database."""
    token = "poisoned-cache-token"
    entry_id = str(uuid4())

    mock_rate_limit_service.get_cached_share_link.return_value = (
        '{"entry_id": "%s", "is_active": true}' % entry_id
    )

    mock_table = MagicMock()
    mock_supabase.table.return_value = mock_table

    share_link_query = MagicMock()
    share_link_query.eq.return_value.execute.return_value.data = [{
        "entry_id": entry_id,
        "is_active": True
    }]

    entry_query = MagicMock()
    entry_query.eq.return_value.execute.return_value.data = [{
        "entry_date": "2024-01-15",
        "body": "Recovered from cache poison",
        "owner_id": str(uuid4()),
        "users": {"display_name": "Owner"}
    }]

    reactions_query = MagicMock()
    reactions_query.eq.return_value.execute.return_value.data = []

    call_count = [0]

    def mock_table_select(*args, **kwargs):
        call_count[0] += 1
        if call_count[0] == 1:
            return share_link_query
        if call_count[0] == 2:
            return entry_query
        return reactions_query

    mock_table.select.side_effect = mock_table_select

    response = client.get(f"/shared/{token}")

    assert response.status_code == 200
    assert response.json()["body"] == "Recovered from cache poison"


def test_get_shared_entry_populates_cache_on_miss(
    client, mock_supabase, mock_rate_limit_service, mock_user
):
    """Test that cache is populated on cache miss."""
    token = "uncached-token"
    entry_id = str(uuid4())
    
    # Mock cache miss
    mock_rate_limit_service.get_cached_share_link.return_value = None
    
    # Mock the database responses
    mock_table = MagicMock()
    mock_supabase.table.return_value = mock_table
    
    # Mock share link lookup
    share_link_query = MagicMock()
    share_link_query.eq.return_value.execute.return_value.data = [{
        "entry_id": entry_id,
        "is_active": True
    }]
    
    # Mock entry lookup
    entry_query = MagicMock()
    entry_query.eq.return_value.execute.return_value.data = [{
        "entry_date": "2024-01-15",
        "body": "Entry to cache",
        "owner_id": str(uuid4()),
        "users": {"display_name": "Owner"}
    }]
    
    # Mock reactions lookup
    reactions_query = MagicMock()
    reactions_query.eq.return_value.execute.return_value.data = []
    
    call_count = [0]
    def mock_table_select(*args, **kwargs):
        call_count[0] += 1
        if call_count[0] == 1:
            return share_link_query
        elif call_count[0] == 2:
            return entry_query
        else:
            return reactions_query
    
    mock_table.select.side_effect = mock_table_select
    
    response = client.get(f"/shared/{token}")
    
    assert response.status_code == 200
    # Verify cache was populated
    mock_rate_limit_service.set_cached_share_link.assert_called_once_with(
        token=token,
        entry_id=entry_id,
        is_active=True
    )


def test_get_shared_entry_reactions_valid_token(
    client, mock_supabase, mock_rate_limit_service, mock_user
):
    """Test getting reactions for a shared entry with a valid token."""
    token = "valid-test-token"
    entry_id = str(uuid4())
    
    # Mock the database responses
    mock_table = MagicMock()
    mock_supabase.table.return_value = mock_table
    
    # Mock share link lookup
    share_link_query = MagicMock()
    share_link_query.eq.return_value.execute.return_value.data = [{
        "entry_id": entry_id,
        "is_active": True
    }]
    
    # Mock reactions lookup
    reactions_query = MagicMock()
    reactions_query.eq.return_value.order.return_value.execute.return_value.data = [
        {
            "emoji": "❤️",
            "user_id": str(uuid4()),
            "users": {"display_name": "Reactor 1"}
        }
    ]
    
    call_count = [0]
    def mock_table_select(*args, **kwargs):
        call_count[0] += 1
        if call_count[0] == 1:
            return share_link_query
        else:
            return reactions_query
            
    mock_table.select.side_effect = mock_table_select
    
    response = client.get(f"/shared/{token}/reactions")
    
    assert response.status_code == 200
    data = response.json()
    assert len(data) == 1
    assert data[0]["emoji"] == "❤️"
    assert data[0]["display_name"] == "Reactor 1"


def test_get_shared_entry_without_auth(
    mock_supabase, mock_rate_limit_service, mock_user
):
    """Test viewing a shared entry without authentication."""
    from app.main import app

    token = "public-test-token"
    entry_id = str(uuid4())
    owner_id = str(uuid4())

    mock_table = MagicMock()
    mock_supabase.table.return_value = mock_table

    def mock_select(*args, **kwargs):
        query = MagicMock()
        query.eq.return_value.execute.return_value.data = [{
            "entry_id": entry_id,
            "is_active": True
        }]
        return query
    mock_table.select.side_effect = mock_select

    entry_query = MagicMock()
    entry_query.eq.return_value.execute.return_value.data = [{
        "entry_date": "2024-01-15",
        "body": "Public shared entry",
        "owner_id": owner_id,
        "users": {
            "display_name": "Entry Owner"
        }
    }]

    reactions_query = MagicMock()
    reactions_query.eq.return_value.execute.return_value.data = []

    call_count = [0]
    def mock_table_select(*args, **kwargs):
        call_count[0] += 1
        if call_count[0] == 1:
            return mock_select(*args, **kwargs)
        elif call_count[0] == 2:
            return entry_query
        return reactions_query

    mock_table.select.side_effect = mock_table_select

    client = TestClient(app)
    response = client.get(f"/shared/{token}")

    assert response.status_code == 200
    data = response.json()
    assert data["body"] == "Public shared entry"


def test_get_shared_entry_reactions_revoked_token(
    client, mock_supabase, mock_rate_limit_service, mock_user
):
    """Test getting reactions with a revoked token returns 404."""
    token = "revoked-test-token"
    
    mock_table = MagicMock()
    mock_supabase.table.return_value = mock_table
    
    mock_query = MagicMock()
    mock_query.eq.return_value.execute.return_value.data = [{
        "entry_id": str(uuid4()),
        "is_active": False
    }]
    mock_table.select.return_value = mock_query
    
    response = client.get(f"/shared/{token}/reactions")
    
    assert response.status_code == 404
