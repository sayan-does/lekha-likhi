from supabase import create_client, Client
from app.config import settings


def get_supabase_client() -> Client:
    """Initialize and return a Supabase client instance."""
    return create_client(settings.supabase_url, settings.supabase_jwt_secret)


# Global client instance for the application
supabase_client = get_supabase_client()
