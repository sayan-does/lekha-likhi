"""Shared pytest fixtures and configuration for all tests."""

import pytest
import os


@pytest.fixture(scope="session", autouse=True)
def setup_test_environment():
    """Set up test environment variables before any tests run."""
    # Set minimal required environment variables for testing
    # Use a valid JWT-like format for the secret to avoid Supabase client initialization errors
    os.environ.setdefault("SUPABASE_URL", "https://test.supabase.co")
    os.environ.setdefault("SUPABASE_JWT_SECRET", "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiIxMjM0NTY3ODkwIiwibmFtZSI6IkpvaG4gRG9lIiwiaWF0IjoxNTE2MjM5MDIyfQ.SflKxwRJSMeKKF2QT4fwpMeJf36POk6yJV_adQssw5c")
    os.environ.setdefault("UPSTASH_REDIS_URL", "https://test-redis.upstash.io")
    os.environ.setdefault("UPSTASH_REDIS_TOKEN", "test-redis-token")
    
    yield
    
    # Cleanup is not needed as tests run in isolated processes
