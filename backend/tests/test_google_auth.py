from unittest.mock import AsyncMock, MagicMock, patch
from uuid import uuid4

from fastapi.testclient import TestClient
from jose import jwt

from app.config import settings
from app.main import app
from app.routers.google_auth import display_name_from_google, mint_session_token, upsert_google_user


client = TestClient(app)


def test_display_name_prefers_google_name():
    assert display_name_from_google({"name": "Ada Lovelace"}, "ada@example.com") == "Ada Lovelace"


def test_display_name_falls_back_to_email_prefix():
    assert display_name_from_google({}, "ada@example.com") == "ada"
    assert display_name_from_google({"name": "  "}, "ada@example.com") == "ada"


def test_display_name_falls_back_to_writer():
    assert display_name_from_google({}, "") == "Writer"


def test_mint_session_token_roundtrip():
    user_id = str(uuid4())
    token = mint_session_token(user_id, "ada@example.com", "Ada", None)
    payload = jwt.decode(
        token,
        settings.supabase_jwt_secret,
        algorithms=["HS256"],
        options={"verify_aud": False},
    )
    assert payload["sub"] == user_id
    assert payload["email"] == "ada@example.com"
    assert isinstance(payload["exp"], int)


@patch("app.routers.google_auth.get_supabase_client")
def test_upsert_existing_user_survives_profile_update_error(mock_get_supabase):
    user_id = str(uuid4())
    mock_supabase = MagicMock()
    mock_get_supabase.return_value = mock_supabase
    table = mock_supabase.table.return_value
    table.select.return_value.eq.return_value.execute.return_value = MagicMock(
        data=[{"id": user_id}]
    )
    table.update.return_value.eq.return_value.execute.side_effect = RuntimeError("not null")

    assert upsert_google_user("ada@example.com", "Ada", None) == user_id
    table.insert.assert_not_called()


@patch("app.routers.google_auth.get_supabase_client")
def test_upsert_new_user_never_inserts_empty_name(mock_get_supabase):
    mock_supabase = MagicMock()
    mock_get_supabase.return_value = mock_supabase
    table = mock_supabase.table.return_value
    table.select.return_value.eq.return_value.execute.return_value = MagicMock(data=[])
    table.insert.return_value.execute.return_value = MagicMock()

    user_id = upsert_google_user("ada@example.com", "ada", None)
    insert_row = table.insert.call_args[0][0]
    assert insert_row["id"] == user_id
    assert insert_row["display_name"] == "ada"


def _mock_google(token_ok=True, userinfo=None, token_status=200, userinfo_status=200):
    instance = AsyncMock()
    token_response = MagicMock()
    token_response.status_code = token_status
    token_response.text = "token-error"
    token_response.json.return_value = {"access_token": "g-token"} if token_ok else {}

    info_response = MagicMock()
    info_response.status_code = userinfo_status
    info_response.text = "userinfo-error"
    info_response.json.return_value = userinfo or {}

    instance.post = AsyncMock(return_value=token_response)
    instance.get = AsyncMock(return_value=info_response)
    return instance


@patch("app.routers.google_auth.get_supabase_client")
@patch("app.routers.google_auth.httpx.AsyncClient")
def test_callback_creates_user_when_google_omits_name(mock_async_client, mock_get_supabase):
    google = _mock_google(userinfo={"email": "ada@example.com", "picture": None})
    mock_async_client.return_value.__aenter__.return_value = google

    mock_supabase = MagicMock()
    mock_get_supabase.return_value = mock_supabase
    table = mock_supabase.table.return_value
    table.select.return_value.eq.return_value.execute.return_value = MagicMock(data=[])
    table.insert.return_value.execute.return_value = MagicMock()

    response = client.get(
        "/auth/google/callback",
        params={"code": "real-code", "state": "http://localhost:5173"},
        follow_redirects=False,
    )

    assert response.status_code in {302, 307}
    assert response.headers["location"].startswith("http://localhost:5173/#access_token=")
    insert_row = table.insert.call_args[0][0]
    assert insert_row["display_name"] == "ada"
    assert insert_row["email"] == "ada@example.com"


@patch("app.routers.google_auth.httpx.AsyncClient")
def test_callback_token_failure_returns_to_frontend(mock_async_client):
    mock_async_client.return_value.__aenter__.return_value = _mock_google(
        token_ok=False, token_status=400
    )
    response = client.get(
        "/auth/google/callback",
        params={"code": "bad-code", "state": "http://localhost:5173"},
        follow_redirects=False,
    )
    assert response.status_code in {302, 307}
    assert response.headers["location"] == "http://localhost:5173/#auth_error=google_token"


def test_callback_google_error_returns_to_frontend():
    response = client.get(
        "/auth/google/callback",
        params={"error": "access_denied", "state": "http://localhost:5173"},
        follow_redirects=False,
    )
    assert response.status_code in {302, 307}
    assert response.headers["location"] == "http://localhost:5173/#auth_error=google_denied"


@patch("app.routers.google_auth.upsert_google_user", side_effect=RuntimeError("db down"))
@patch("app.routers.google_auth.httpx.AsyncClient")
def test_callback_unexpected_error_returns_to_frontend(mock_async_client, _mock_upsert):
    mock_async_client.return_value.__aenter__.return_value = _mock_google(
        userinfo={"email": "ada@example.com", "name": "Ada"}
    )
    response = client.get(
        "/auth/google/callback",
        params={"code": "real-code", "state": "http://localhost:5173"},
        follow_redirects=False,
    )
    assert response.status_code in {302, 307}
    assert response.headers["location"] == "http://localhost:5173/#auth_error=unknown"
