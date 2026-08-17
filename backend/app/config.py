from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Application configuration loaded from environment variables."""
    
    supabase_url: str
    supabase_jwt_secret: str
    supabase_service_role_key: str
    upstash_redis_url: str
    upstash_redis_token: str
    
    # Google OAuth
    google_client_id: str
    google_client_secret: str

    frontend_url: str = "http://localhost:5173"
    
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False
    )


settings = Settings()
