"""Tests for reactions endpoints (Task 6)."""

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
        service.check_rate_limit = AsyncMock(return_value=(True, 1))
        mock.return_value = service
        yield service


@pytest.fixture
def mock_user():
    """Create a mock user for testing."""
    user_id = uuid4()
    mock_user_obj = Mock()
    mock_user_obj.id = user_id
    mock_user_obj.email = "reactor@example.com"
    mock_user_obj.display_name = "Reactor User"
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


def test_react_with_valid_emoji_creates_reaction(
    client, mock_supabase, mock_rate_limit_service, mock_user
):
    """Test reacting with a valid emoji creates a new reaction row."""
    token = "valid-token"
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
    
    # Mock existing reaction check (no existing reaction)
    existing_reaction_query = MagicMock()
    existing_reaction_query.eq.return_value.eq.return_value.execute.return_value.data = []
    
    # Mock insert response
    insert_query = MagicMock()
    insert_query.execute.return_value.data = [{
        "id": str(uuid4()),
        "entry_id": entry_id,
        "user_id": str(mock_user.id),
        "emoji": "❤️",
        "created_at": "2024-01-15T10:00:00"
    }]
    
    call_count = [0]
    def mock_table_select(*args, **kwargs):
        call_count[0] += 1
        if call_count[0] == 1:
            return share_link_query
        else:
            return existing_reaction_query
    
    mock_table.select.side_effect = mock_table_select
    mock_table.insert.return_value = insert_query
    
    response = client.post(
        f"/shared/{token}/react",
        json={"emoji": "❤️"}
    )
    
    assert response.status_code == 201
    assert "success" in response.json()["message"].lower()
    
    # Verify rate limit was checked
    mock_rate_limit_service.check_rate_limit.assert_called_once()


def test_react_again_with_different_emoji_updates_reaction(
    client, mock_supabase, mock_rate_limit_service, mock_user
):
    """Test reacting again with a different emoji updates the existing reaction."""
    token = "valid-token"
    entry_id = str(uuid4())
    reaction_id = str(uuid4())
    
    # Mock the database responses
    mock_table = MagicMock()
    mock_supabase.table.return_value = mock_table
    
    # Mock share link lookup
    share_link_query = MagicMock()
    share_link_query.eq.return_value.execute.return_value.data = [{
        "entry_id": entry_id,
        "is_active": True
    }]
    
    # Mock existing reaction check (reaction exists)
    existing_reaction_query = MagicMock()
    existing_reaction_query.eq.return_value.eq.return_value.execute.return_value.data = [{
        "id": reaction_id
    }]
    
    # Mock update response
    update_query = MagicMock()
    update_query.eq.return_value.execute.return_value = Mock()
    
    call_count = [0]
    def mock_table_select(*args, **kwargs):
        call_count[0] += 1
        if call_count[0] == 1:
            return share_link_query
        else:
            return existing_reaction_query
    
    mock_table.select.side_effect = mock_table_select
    mock_table.update.return_value = update_query
    
    response = client.post(
        f"/shared/{token}/react",
        json={"emoji": "😂"}
    )
    
    assert response.status_code == 201
    
    # Verify update was called, not insert
    mock_table.update.assert_called_once_with({"emoji": "😂"})


def test_react_with_invalid_emoji_returns_422(
    client, mock_supabase, mock_rate_limit_service, mock_user
):
    """Test reacting with an invalid emoji returns 422."""
    token = "valid-token"
    
    # The schema validation will catch this before hitting the database
    response = client.post(
        f"/shared/{token}/react",
        json={"emoji": "🚀"}  # Not in allowed set
    )
    
    assert response.status_code == 422
    # Pydantic validation error


def test_remove_reaction_deletes_existing_reaction(
    client, mock_supabase, mock_rate_limit_service, mock_user
):
    """Test removing a reaction deletes the existing reaction row."""
    token = "valid-token"
    entry_id = str(uuid4())
    reaction_id = str(uuid4())
    
    # Mock the database responses
    mock_table = MagicMock()
    mock_supabase.table.return_value = mock_table
    
    # Mock share link lookup
    share_link_query = MagicMock()
    share_link_query.eq.return_value.execute.return_value.data = [{
        "entry_id": entry_id,
        "is_active": True
    }]
    
    # Mock existing reaction check (reaction exists)
    existing_reaction_query = MagicMock()
    existing_reaction_query.eq.return_value.eq.return_value.execute.return_value.data = [{
        "id": reaction_id
    }]
    
    # Mock delete response
    delete_query = MagicMock()
    delete_query.eq.return_value.execute.return_value = Mock()
    
    call_count = [0]
    def mock_table_select(*args, **kwargs):
        call_count[0] += 1
        if call_count[0] == 1:
            return share_link_query
        else:
            return existing_reaction_query
    
    mock_table.select.side_effect = mock_table_select
    mock_table.delete.return_value = delete_query
    
    response = client.delete(f"/shared/{token}/react")
    
    assert response.status_code == 204
    
    # Verify delete was called
    mock_table.delete.assert_called_once()


def test_remove_nonexistent_reaction_returns_404(
    client, mock_supabase, mock_rate_limit_service, mock_user
):
    """Test removing a reaction that doesn't exist returns 404."""
    token = "valid-token"
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
    
    # Mock existing reaction check (no reaction)
    existing_reaction_query = MagicMock()
    existing_reaction_query.eq.return_value.eq.return_value.execute.return_value.data = []
    
    call_count = [0]
    def mock_table_select(*args, **kwargs):
        call_count[0] += 1
        if call_count[0] == 1:
            return share_link_query
        else:
            return existing_reaction_query
    
    mock_table.select.side_effect = mock_table_select
    
    response = client.delete(f"/shared/{token}/react")
    
    assert response.status_code == 404


def test_react_with_invalid_token_returns_404(
    client, mock_supabase, mock_rate_limit_service, mock_user
):
    """Test reacting with invalid/revoked token returns 404."""
    token = "invalid-token"
    
    # Mock the database responses
    mock_table = MagicMock()
    mock_supabase.table.return_value = mock_table
    
    # Mock share link lookup - not found
    share_link_query = MagicMock()
    share_link_query.eq.return_value.execute.return_value.data = []
    mock_table.select.return_value = share_link_query
    
    response = client.post(
        f"/shared/{token}/react",
        json={"emoji": "❤️"}
    )
    
    assert response.status_code == 404
    assert "no longer available" in response.json()["detail"].lower()


def test_exceed_rate_limit_returns_429(
    client, mock_supabase, mock_rate_limit_service, mock_user
):
    """Test exceeding rate limit returns 429."""
    from app.services.rate_limit import RateLimitExceeded
    
    token = "valid-token"
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
    mock_table.select.return_value = share_link_query
    
    # Mock rate limit exceeded
    mock_rate_limit_service.check_rate_limit.side_effect = RateLimitExceeded(
        "Rate limit exceeded", retry_after=45
    )
    
    response = client.post(
        f"/shared/{token}/react",
        json={"emoji": "❤️"}
    )
    
    assert response.status_code == 429
    assert "too many reactions" in response.json()["detail"].lower()
    assert "retry-after" in response.headers
    assert response.headers["retry-after"] == "45"


def test_allowed_emoji_set_validation(
    client, mock_supabase, mock_rate_limit_service, mock_user
):
    """Test that only emojis from the allowed set are accepted."""
    token = "valid-token"
    
    allowed_emojis = ["❤️", "😢", "👏", "😂", "😮"]
    invalid_emojis = ["🚀", "🎉", "✨", "💯", "🔥"]
    
    # Test all allowed emojis would be accepted by schema
    for emoji in allowed_emojis:
        # Just validate the schema accepts it
        from app.schemas.reaction import ReactionCreate
        reaction = ReactionCreate(emoji=emoji)
        assert reaction.emoji == emoji
    
    # Test invalid emojis are rejected by schema
    for emoji in invalid_emojis:
        from app.schemas.reaction import ReactionCreate
        from pydantic import ValidationError
        with pytest.raises(ValidationError):
            ReactionCreate(emoji=emoji)
