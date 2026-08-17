from supabase import create_client, Client
from app.config import settings
from typing import Optional
import secrets


_supabase_client: Optional[Client] = None


def init_supabase_client() -> Client:
    """Initialize the Supabase client with service role credentials."""
    return create_client(settings.supabase_url, settings.supabase_service_role_key)


def get_supabase_client() -> Client:
    """Get or initialize the Supabase client instance."""
    global _supabase_client
    if _supabase_client is None:
        _supabase_client = init_supabase_client()
    return _supabase_client


def generate_share_token() -> str:
    """
    Generate a cryptographically random share token.
    Uses 32 bytes (256 bits) to ensure unguessability.
    """
    return secrets.token_urlsafe(32)
