import os
from datetime import datetime, timedelta, timezone
from unittest.mock import MagicMock, Mock, patch
from uuid import uuid4

import pytest
from fastapi.testclient import TestClient

os.environ.setdefault("SUPABASE_URL", "https://test.supabase.co")
os.environ.setdefault("SUPABASE_JWT_SECRET", "test-secret")
os.environ.setdefault("SUPABASE_SERVICE_ROLE_KEY", "test-service-role-key")
os.environ.setdefault("UPSTASH_REDIS_URL", "https://test.upstash.io")
os.environ.setdefault("UPSTASH_REDIS_TOKEN", "test-token")
os.environ.setdefault("GOOGLE_CLIENT_ID", "test-google-client-id")
os.environ.setdefault("GOOGLE_CLIENT_SECRET", "test-google-client-secret")
os.environ.setdefault("VAPID_PUBLIC_KEY", "BEl62iUYgUivxIkv69yViEuiBIa-Ib9-SkvMeAtA3LFgDzkrxZJjSgSnfckjBJuBkr3qBUYIHBQFLXYp5Nksh8U")
os.environ.setdefault("VAPID_PRIVATE_KEY", "UUxI4O8-FbRPOA20nT-Yj9d7s8h4Y8Y8Y8Y8Y8Y8Y8Y8")
os.environ.setdefault("VAPID_SUBJECT", "mailto:test@example.com")
os.environ.setdefault("CRON_SECRET", "test-cron-secret")


@pytest.fixture
def mock_supabase():
    with patch("app.routers.push.get_supabase_client") as mock:
        yield mock.return_value


@pytest.fixture
def mock_user():
    user_id = uuid4()
    mock_user_obj = Mock()
    mock_user_obj.id = user_id
    mock_user_obj.email = "test@example.com"
    mock_user_obj.display_name = "Test User"
    mock_user_obj.avatar_url = None
    return mock_user_obj


@pytest.fixture
def client(mock_user):
    from app.auth import get_current_user
    from app.main import app

    app.dependency_overrides[get_current_user] = lambda: mock_user
    yield TestClient(app)
    app.dependency_overrides.clear()


def test_get_vapid_public_key(client):
    response = client.get("/push/vapid-public-key")
    assert response.status_code == 200
    assert response.json()["public_key"]


def test_get_push_status(client, mock_supabase, mock_user):
    users_table = MagicMock()
    subs_table = MagicMock()
    mock_supabase.table.side_effect = lambda name: users_table if name == "users" else subs_table

    users_table.select.return_value.eq.return_value.single.return_value.execute.return_value.data = {
        "reminders_enabled": True
    }
    subs_table.select.return_value.eq.return_value.limit.return_value.execute.return_value.data = [
        {"id": str(uuid4())}
    ]

    response = client.get("/push/status")
    assert response.status_code == 200
    assert response.json() == {"enabled": True, "subscribed": True}


def test_subscribe_push(client, mock_supabase, mock_user):
    table = MagicMock()
    mock_supabase.table.return_value = table

    response = client.post(
        "/push/subscribe",
        json={
            "endpoint": "https://push.example/abc",
            "keys": {"p256dh": "key", "auth": "auth"},
            "timezone": "Asia/Kolkata",
        },
    )

    assert response.status_code == 204
    table.upsert.assert_called_once()
    table.update.assert_called_once()


def test_dispatch_requires_cron_secret(client):
    response = client.post("/push/dispatch-reminders")
    assert response.status_code == 401


@patch("app.services.push.send_push_notification")
@patch("app.services.push.user_has_entry_for_date", return_value=False)
@patch("app.services.push.get_supabase_client")
def test_dispatch_sends_when_due(mock_get_client, mock_has_entry, mock_send):
    from app.services.push import dispatch_reminders

    user_id = str(uuid4())
    sub_id = str(uuid4())

    users_table = MagicMock()
    subs_table = MagicMock()
    entries_table = MagicMock()
    update_table = MagicMock()

    client = MagicMock()

    def table_router(name):
        if name == "users":
            return users_table
        if name == "push_subscriptions":
            return subs_table
        if name == "entries":
            return entries_table
        return update_table

    client.table.side_effect = table_router
    mock_get_client.return_value = client

    users_table.select.return_value.eq.return_value.execute.return_value.data = [
        {
            "id": user_id,
            "reminder_last_sent_at": None,
            "reminders_enabled": True,
        }
    ]
    subs_table.select.return_value.eq.return_value.execute.return_value.data = [
        {
            "id": sub_id,
            "endpoint": "https://push.example/abc",
            "p256dh": "key",
            "auth_key": "auth",
            "timezone": "UTC",
        }
    ]
    update_table.update.return_value.eq.return_value.execute.return_value.data = []

    result = dispatch_reminders()

    assert result["sent"] == 1
    mock_send.assert_called_once()


@patch("app.services.push.send_push_notification")
@patch("app.services.push.user_has_entry_for_date", return_value=True)
@patch("app.services.push.get_supabase_client")
def test_dispatch_skips_when_entry_exists(mock_get_client, mock_has_entry, mock_send):
    from app.services.push import dispatch_reminders

    user_id = str(uuid4())
    users_table = MagicMock()
    subs_table = MagicMock()
    client = MagicMock()

    def table_router(name):
        if name == "users":
            return users_table
        return subs_table

    client.table.side_effect = table_router
    mock_get_client.return_value = client

    users_table.select.return_value.eq.return_value.execute.return_value.data = [
        {
            "id": user_id,
            "reminder_last_sent_at": None,
            "reminders_enabled": True,
        }
    ]
    subs_table.select.return_value.eq.return_value.execute.return_value.data = [
        {
            "id": str(uuid4()),
            "endpoint": "https://push.example/abc",
            "p256dh": "key",
            "auth_key": "auth",
            "timezone": "UTC",
        }
    ]

    result = dispatch_reminders()

    assert result["skipped"] == 1
    assert result["sent"] == 0
    mock_send.assert_not_called()


@patch("app.services.push.send_push_notification")
@patch("app.services.push.user_has_entry_for_date", return_value=False)
@patch("app.services.push.get_supabase_client")
def test_dispatch_skips_when_recently_sent(mock_get_client, mock_has_entry, mock_send):
    from app.services.push import dispatch_reminders

    user_id = str(uuid4())
    users_table = MagicMock()
    subs_table = MagicMock()
    client = MagicMock()

    def table_router(name):
        if name == "users":
            return users_table
        return subs_table

    client.table.side_effect = table_router
    mock_get_client.return_value = client

    recent = (datetime.now(timezone.utc) - timedelta(hours=1)).isoformat()
    users_table.select.return_value.eq.return_value.execute.return_value.data = [
        {
            "id": user_id,
            "reminder_last_sent_at": recent,
            "reminders_enabled": True,
        }
    ]
    subs_table.select.return_value.eq.return_value.execute.return_value.data = [
        {
            "id": str(uuid4()),
            "endpoint": "https://push.example/abc",
            "p256dh": "key",
            "auth_key": "auth",
            "timezone": "UTC",
        }
    ]

    result = dispatch_reminders()

    assert result["skipped"] == 1
    assert result["sent"] == 0
    mock_send.assert_not_called()


def test_dispatch_with_valid_secret(client):
    with patch("app.routers.push.dispatch_reminders") as mock_dispatch:
        mock_dispatch.return_value = {
            "checked": 0,
            "sent": 0,
            "skipped": 0,
            "failed": 0,
        }
        response = client.post(
            "/push/dispatch-reminders",
            headers={"X-Cron-Secret": "test-cron-secret"},
        )
        assert response.status_code == 200
        assert response.json()["sent"] == 0
