"""Shared pytest fixtures and configuration for all tests."""

import os

import pytest

# Settings() loads at import time. Set defaults here so CI (no .env) can collect tests.
os.environ.setdefault("SUPABASE_URL", "https://test.supabase.co")
os.environ.setdefault(
    "SUPABASE_JWT_SECRET",
    "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiIxMjM0NTY3ODkwIiwibmFtZSI6IkpvaG4gRG9lIiwiaWF0IjoxNTE2MjM5MDIyfQ.SflKxwRJSMeKKF2QT4fwpMeJf36POk6yJV_adQssw5c",
)
os.environ.setdefault("SUPABASE_SERVICE_ROLE_KEY", "test-service-role-key")
os.environ.setdefault("UPSTASH_REDIS_URL", "https://test-redis.upstash.io")
os.environ.setdefault("UPSTASH_REDIS_TOKEN", "test-redis-token")
os.environ.setdefault("GOOGLE_CLIENT_ID", "test-google-client-id")
os.environ.setdefault("GOOGLE_CLIENT_SECRET", "test-google-client-secret")
os.environ.setdefault("FRONTEND_URL", "http://localhost:5173")
os.environ.setdefault(
    "VAPID_PUBLIC_KEY",
    "BEl62iUYgUivxIkv69yViEuiBIa-Ib9-SkvMeAtA3LFgDzkrxZJjSgSnfckjBJuBkr3qBUYIHBQFLXYp5Nksh8U",
)
os.environ.setdefault("VAPID_PRIVATE_KEY", "UUxI4O8-FbRPOA20nT-Yj9d7s8h4Y8Y8Y8Y8Y8Y8Y8Y8")
os.environ.setdefault("VAPID_SUBJECT", "mailto:test@example.com")
os.environ.setdefault("CRON_SECRET", "test-cron-secret")


@pytest.fixture(scope="session", autouse=True)
def setup_test_environment():
    """Keep required test env vars present for the whole session."""
    yield
