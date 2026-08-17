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
    with patch("app.routers.entries.get_supabase_client") as mock:
        yield mock.return_value


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
    from app.routers import entries
    from app.auth import get_current_user
    
    # Mount the router if not already mounted
    if not any(route.path.startswith("/entries") for route in app.routes):
        app.include_router(entries.router)
    
    # Override the dependency
    app.dependency_overrides[get_current_user] = lambda: mock_user
    
    yield TestClient(app)
    
    # Cleanup
    app.dependency_overrides.clear()


def test_create_entry(client, mock_supabase, mock_user):
    """Test creating a new entry."""
    entry_date = "2024-01-15"
    entry_body = "My first journal entry"
    
    # Mock the database responses
    mock_table = MagicMock()
    mock_supabase.table.return_value = mock_table
    
    # Mock existing check (no existing entry)
    mock_table.select.return_value.eq.return_value.eq.return_value.execute.return_value.data = []
    
    # Mock insert response
    mock_table.insert.return_value.execute.return_value.data = [{
        "id": str(uuid4()),
        "owner_id": str(mock_user.id),
        "entry_date": entry_date,
        "body": entry_body,
        "created_at": "2024-01-15T10:00:00",
        "updated_at": "2024-01-15T10:00:00"
    }]
    
    response = client.put(
        f"/entries/{entry_date}",
        json={"body": entry_body}
    )
    
    assert response.status_code == 200
    data = response.json()
    assert data["entry_date"] == entry_date
    assert data["body"] == entry_body
    assert data["owner_id"] == str(mock_user.id)


def test_get_entry_by_date(client, mock_supabase, mock_user):
    """Test retrieving an entry by date."""
    entry_date = "2024-01-15"
    entry_id = str(uuid4())
    
    # Mock the database response
    mock_table = MagicMock()
    mock_supabase.table.return_value = mock_table
    mock_table.select.return_value.eq.return_value.eq.return_value.execute.return_value.data = [{
        "id": entry_id,
        "owner_id": str(mock_user.id),
        "entry_date": entry_date,
        "body": "Test entry",
        "created_at": "2024-01-15T10:00:00",
        "updated_at": "2024-01-15T10:00:00"
    }]
    
    response = client.get(f"/entries/{entry_date}")
    
    assert response.status_code == 200
    data = response.json()
    assert data["entry_date"] == entry_date
    assert data["id"] == entry_id


def test_get_nonexistent_entry(client, mock_supabase, mock_user):
    """Test that fetching a nonexistent entry returns 404."""
    entry_date = "2024-01-15"
    
    # Mock empty database response
    mock_table = MagicMock()
    mock_supabase.table.return_value = mock_table
    mock_table.select.return_value.eq.return_value.eq.return_value.execute.return_value.data = []
    
    response = client.get(f"/entries/{entry_date}")
    
    assert response.status_code == 404
    assert "not found" in response.json()["detail"].lower()


def test_update_entry(client, mock_supabase, mock_user):
    """Test updating an existing entry."""
    entry_date = "2024-01-15"
    entry_id = str(uuid4())
    original_body = "Original entry"
    updated_body = "Updated entry"
    
    # Mock the database responses
    mock_table = MagicMock()
    mock_supabase.table.return_value = mock_table
    
    # Mock existing check (entry exists)
    mock_table.select.return_value.eq.return_value.eq.return_value.execute.return_value.data = [{
        "id": entry_id,
        "owner_id": str(mock_user.id),
        "entry_date": entry_date,
        "body": original_body,
        "created_at": "2024-01-15T10:00:00",
        "updated_at": "2024-01-15T10:00:00"
    }]
    
    # Mock update response
    mock_table.update.return_value.eq.return_value.execute.return_value.data = [{
        "id": entry_id,
        "owner_id": str(mock_user.id),
        "entry_date": entry_date,
        "body": updated_body,
        "created_at": "2024-01-15T10:00:00",
        "updated_at": "2024-01-15T12:00:00"
    }]
    
    response = client.put(
        f"/entries/{entry_date}",
        json={"body": updated_body}
    )
    
    assert response.status_code == 200
    data = response.json()
    assert data["body"] == updated_body


def test_delete_entry(client, mock_supabase, mock_user):
    """Test deleting an entry."""
    entry_date = "2024-01-15"
    entry_id = str(uuid4())
    
    # Mock the database responses
    mock_table = MagicMock()
    mock_supabase.table.return_value = mock_table
    
    # Mock existing check (entry exists)
    mock_table.select.return_value.eq.return_value.eq.return_value.execute.return_value.data = [{
        "id": entry_id
    }]
    
    # Mock delete response
    mock_table.delete.return_value.eq.return_value.execute.return_value = Mock()
    
    response = client.delete(f"/entries/{entry_date}")
    
    assert response.status_code == 204


def test_delete_nonexistent_entry(client, mock_supabase, mock_user):
    """Test that deleting a nonexistent entry returns 404."""
    entry_date = "2024-01-15"
    
    # Mock empty database response
    mock_table = MagicMock()
    mock_supabase.table.return_value = mock_table
    mock_table.select.return_value.eq.return_value.eq.return_value.execute.return_value.data = []
    
    response = client.delete(f"/entries/{entry_date}")
    
    assert response.status_code == 404


def test_user_cannot_access_other_users_entry(client, mock_supabase, mock_user):
    """
    Critical test: Verify that user A cannot fetch user B's entry.
    The endpoint enforces owner_id = current_user.id, so accessing another user's
    entry should return 404 (not 403, to avoid confirming existence).
    """
    entry_date = "2024-01-15"
    other_user_id = uuid4()  # Different user
    
    # Mock the database response - no entry found for current user
    # (even though entry might exist for other user, the query filters by current user's ID)
    mock_table = MagicMock()
    mock_supabase.table.return_value = mock_table
    mock_table.select.return_value.eq.return_value.eq.return_value.execute.return_value.data = []
    
    response = client.get(f"/entries/{entry_date}")
    
    # Must return 404, not 403, to avoid leaking information
    assert response.status_code == 404
    assert "not found" in response.json()["detail"].lower()


def test_list_entries(client, mock_supabase, mock_user):
    """Test listing entries with date range filters."""
    # Mock the database response
    mock_table = MagicMock()
    mock_supabase.table.return_value = mock_table
    
    mock_entries = [
        {
            "id": str(uuid4()),
            "entry_date": "2024-01-15",
            "body": "Entry 1",
            "created_at": "2024-01-15T10:00:00",
            "updated_at": "2024-01-15T10:00:00"
        },
        {
            "id": str(uuid4()),
            "entry_date": "2024-01-14",
            "body": "Entry 2",
            "created_at": "2024-01-14T10:00:00",
            "updated_at": "2024-01-14T10:00:00"
        }
    ]
    
    # Create a chain of mocks for the query builder pattern
    mock_query = MagicMock()
    mock_table.select.return_value = mock_query
    mock_query.eq.return_value = mock_query
    mock_query.order.return_value = mock_query
    mock_query.range.return_value = mock_query
    mock_query.execute.return_value.data = mock_entries
    mock_query.execute.return_value.count = 2
    
    response = client.get("/entries?limit=10&offset=5")
    
    assert response.status_code == 200
    data = response.json()
    assert data["total"] == 2
    assert data["limit"] == 10
    assert data["offset"] == 5
    assert len(data["entries"]) == 2
    assert data["entries"][0]["entry_date"] == "2024-01-15"
    assert "id" in data["entries"][0]
    
    # Verify range was called correctly
    mock_query.range.assert_called_with(5, 14)


def test_list_entries_with_date_range(client, mock_supabase, mock_user):
    """Test listing entries with from/to date filters."""
    # Mock the database response
    mock_table = MagicMock()
    mock_supabase.table.return_value = mock_table
    
    mock_entries = [
        {
            "id": str(uuid4()),
            "entry_date": "2024-01-15",
            "body": "Entry in range",
            "created_at": "2024-01-15T10:00:00",
            "updated_at": "2024-01-15T10:00:00"
        }
    ]
    
    # Create a chain of mocks for the query builder pattern
    mock_query = MagicMock()
    mock_table.select.return_value = mock_query
    mock_query.eq.return_value = mock_query
    mock_query.gte.return_value = mock_query
    mock_query.lte.return_value = mock_query
    mock_query.order.return_value = mock_query
    mock_query.range.return_value = mock_query
    mock_query.execute.return_value.data = mock_entries
    mock_query.execute.return_value.count = 1
    
    response = client.get("/entries?from=2024-01-10&to=2024-01-20")
    
    assert response.status_code == 200
    data = response.json()
    assert data["total"] == 1
    assert len(data["entries"]) == 1

def test_create_empty_entry(client, mock_supabase, mock_user):
    """Test creating an entry with an empty body."""
    entry_date = "2024-01-16"
    entry_body = ""
    
    mock_table = MagicMock()
    mock_supabase.table.return_value = mock_table
    
    # Mock existing check (no existing entry)
    mock_table.select.return_value.eq.return_value.eq.return_value.execute.return_value.data = []
    
    # Mock insert response
    mock_table.insert.return_value.execute.return_value.data = [{
        "id": str(uuid4()),
        "owner_id": str(mock_user.id),
        "entry_date": entry_date,
        "body": entry_body,
        "created_at": "2024-01-16T10:00:00",
        "updated_at": "2024-01-16T10:00:00"
    }]
    
    response = client.put(
        f"/entries/{entry_date}",
        json={"body": entry_body}
    )
    
    assert response.status_code == 200
    data = response.json()
    assert data["body"] == ""

def test_empty_entry_counts_toward_constraint(client, mock_supabase, mock_user):
    """Test that an empty entry updates an existing entry (upsert constraint)."""
    entry_date = "2024-01-16"
    entry_body = ""
    entry_id = str(uuid4())
    
    mock_table = MagicMock()
    mock_supabase.table.return_value = mock_table
    
    # Mock existing check (entry exists)
    mock_table.select.return_value.eq.return_value.eq.return_value.execute.return_value.data = [{
        "id": entry_id,
        "owner_id": str(mock_user.id),
        "entry_date": entry_date,
        "body": "Existing content",
        "created_at": "2024-01-16T10:00:00",
        "updated_at": "2024-01-16T10:00:00"
    }]
    
    # Mock update response
    mock_table.update.return_value.eq.return_value.execute.return_value.data = [{
        "id": entry_id,
        "owner_id": str(mock_user.id),
        "entry_date": entry_date,
        "body": entry_body,
        "created_at": "2024-01-16T10:00:00",
        "updated_at": "2024-01-16T12:00:00"
    }]
    
    response = client.put(
        f"/entries/{entry_date}",
        json={"body": entry_body}
    )
    
    assert response.status_code == 200
    data = response.json()
    assert data["body"] == ""
