from pydantic_settings import BaseSettings, SettingsConfigDict

from app.url_cascade import (
    LOCAL_FRONTEND_URL,
    PROD_FRONTEND_URL,
    cascade_origins,
    resolve_cascade_url,
)


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

    app_env: str = ""
    frontend_url: str = ""
    frontend_url_prod: str = ""
    frontend_url_local: str = LOCAL_FRONTEND_URL
    frontend_url_tunnel: str = ""

    vapid_public_key: str = ""
    vapid_private_key: str = ""
    vapid_subject: str = "mailto:admin@lekha-likhi.local"
    cron_secret: str = ""
    
    model_config = SettingsConfigDict(
        env_file=(".env", ".env.local"),
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore",
    )

    @property
    def resolved_frontend_url(self) -> str:
        return resolve_cascade_url(
            tunnel=self.frontend_url_tunnel,
            local=self.frontend_url_local,
            prod=self.frontend_url_prod,
            legacy=self.frontend_url,
            app_env=self.app_env,
            hardcoded=PROD_FRONTEND_URL,
        )

    def frontend_origins(self) -> list[str]:
        return cascade_origins(
            self.frontend_url_tunnel,
            self.frontend_url_local,
            self.frontend_url_prod,
            self.frontend_url,
            self.resolved_frontend_url,
            LOCAL_FRONTEND_URL,
            "http://127.0.0.1:5173",
        )


settings = Settings()
