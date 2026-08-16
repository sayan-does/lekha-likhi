import pytest
from fastapi.testclient import TestClient
from unittest.mock import patch, MagicMock, AsyncMock
from jose import jwt
from datetime import datetime, timedelta
from uuid import uuid4
from app.main import app
from app.config import settings


client = TestClient(app)


def create_test_token(user_id: str, email: str, metadata: dict = None) -> str:
    """Helper to create a valid JWT token for testing."""
    payload = {
        "sub": user_id,
        "email": email,
        "user_metadata": metadata or {},
        "exp": datetime.utcnow() + timedelta(hours=1),
        "iat": datetime.utcnow()
    }
    return jwt.encode(payload, settings.supabase_jwt_secret, algorithm="HS256")


class TestAuthMiddleware:
    """Test suite for authentication middleware."""
    
    def test_request_without_token_returns_401(self):
        """Test that a request without Bearer token gets 401/403 Unauthorized."""
        response = client.get("/me")
        assert response.status_code in [401, 403]  # FastAPI's HTTPBearer returns 403 when no credentials
        assert "detail" in response.json()
    
    def test_request_with_invalid_token_returns_401(self):
        """Test that a request with an invalid token gets 401."""
        headers = {"Authorization": "Bearer invalid_token_here"}
        response = client.get("/me", headers=headers)
        assert response.status_code == 401
        assert response.json()["detail"] == "Not authenticated"
    
    def test_request_with_expired_token_returns_401(self):
        """Test that an expired token is rejected."""
        user_id = str(uuid4())
        payload = {
            "sub": user_id,
            "email": "test@example.com",
            "user_metadata": {},
            "exp": datetime.utcnow() - timedelta(hours=1),  # Expired
            "iat": datetime.utcnow() - timedelta(hours=2)
        }
        expired_token = jwt.encode(payload, settings.supabase_jwt_secret, algorithm="HS256")
        headers = {"Authorization": f"Bearer {expired_token}"}
        response = client.get("/me", headers=headers)
        assert response.status_code == 401
    
    @patch("app.auth.get_supabase_client")
    def test_valid_token_returns_user_profile(self, mock_get_supabase):
        """Test that a valid token successfully authenticates and returns user data."""
        user_id = str(uuid4())
        email = "testuser@example.com"
        metadata = {
            "full_name": "Test User",
            "avatar_url": "https://example.com/avatar.jpg"
        }
        
        # Mock the database response (user doesn't exist yet)
        mock_supabase = MagicMock()
        mock_get_supabase.return_value = mock_supabase
        mock_table = MagicMock()
        mock_supabase.table.return_value = mock_table
        mock_table.select.return_value.eq.return_value.execute.return_value = MagicMock(data=[])
        mock_table.insert.return_value.execute.return_value = MagicMock()
        
        token = create_test_token(user_id, email, metadata)
        headers = {"Authorization": f"Bearer {token}"}
        
        response = client.get("/me", headers=headers)
        
        assert response.status_code == 200
        data = response.json()
        assert data["email"] == email
        assert data["display_name"] == "Test User"
        assert data["avatar_url"] == "https://example.com/avatar.jpg"
        assert data["id"] == user_id
    
    @patch("app.auth.get_supabase_client")
    def test_me_endpoint_upserts_new_user(self, mock_get_supabase):
        """Test that /me endpoint inserts a new user on first call."""
        user_id = str(uuid4())
        email = "newuser@example.com"
        metadata = {"full_name": "New User"}
        
        # Mock database: user doesn't exist
        mock_supabase = MagicMock()
        mock_get_supabase.return_value = mock_supabase
        mock_table = MagicMock()
        mock_supabase.table.return_value = mock_table
        mock_table.select.return_value.eq.return_value.execute.return_value = MagicMock(data=[])
        mock_insert = MagicMock()
        mock_table.insert.return_value.execute.return_value = mock_insert
        
        token = create_test_token(user_id, email, metadata)
        headers = {"Authorization": f"Bearer {token}"}
        
        response = client.get("/me", headers=headers)
        
        assert response.status_code == 200
        # Verify insert was called
        mock_table.insert.assert_called_once()
        insert_call_args = mock_table.insert.call_args[0][0]
        assert insert_call_args["id"] == user_id
        assert insert_call_args["email"] == email
        assert insert_call_args["display_name"] == "New User"
    
    @patch("app.auth.get_supabase_client")
    def test_me_endpoint_updates_existing_user(self, mock_get_supabase):
        """Test that /me endpoint updates an existing user's data."""
        user_id = str(uuid4())
        email = "existing@example.com"
        metadata = {"full_name": "Updated Name"}
        
        # Mock database: user exists
        mock_supabase = MagicMock()
        mock_get_supabase.return_value = mock_supabase
        mock_table = MagicMock()
        mock_supabase.table.return_value = mock_table
        mock_table.select.return_value.eq.return_value.execute.return_value = MagicMock(
            data=[{"id": user_id, "email": email}]
        )
        mock_update = MagicMock()
        mock_table.update.return_value.eq.return_value.execute.return_value = mock_update
        
        token = create_test_token(user_id, email, metadata)
        headers = {"Authorization": f"Bearer {token}"}
        
        response = client.get("/me", headers=headers)
        
        assert response.status_code == 200
        # Verify update was called
        mock_table.update.assert_called_once()
        update_call_args = mock_table.update.call_args[0][0]
        assert update_call_args["display_name"] == "Updated Name"
    
    @patch("app.auth.get_supabase_client")
    def test_token_without_email_returns_401(self, mock_get_supabase):
        """Test that a token without email field is rejected."""
        user_id = str(uuid4())
        payload = {
            "sub": user_id,
            # Missing email
            "user_metadata": {},
            "exp": datetime.utcnow() + timedelta(hours=1),
            "iat": datetime.utcnow()
        }
        token = jwt.encode(payload, settings.supabase_jwt_secret, algorithm="HS256")
        headers = {"Authorization": f"Bearer {token}"}
        
        response = client.get("/me", headers=headers)
        assert response.status_code == 401
    
    @patch("app.auth.get_supabase_client")
    def test_display_name_defaults_to_email_prefix(self, mock_get_supabase):
        """Test that display_name defaults to email prefix when metadata is empty."""
        user_id = str(uuid4())
        email = "testuser@example.com"
        
        # Mock database
        mock_supabase = MagicMock()
        mock_get_supabase.return_value = mock_supabase
        mock_table = MagicMock()
        mock_supabase.table.return_value = mock_table
        mock_table.select.return_value.eq.return_value.execute.return_value = MagicMock(data=[])
        mock_table.insert.return_value.execute.return_value = MagicMock()
        
        token = create_test_token(user_id, email, {})  # Empty metadata
        headers = {"Authorization": f"Bearer {token}"}
        
        response = client.get("/me", headers=headers)
        
        assert response.status_code == 200
        data = response.json()
        assert data["display_name"] == "testuser"  # Email prefix
