from fastapi import FastAPI, Depends
from fastapi.middleware.cors import CORSMiddleware
from fastapi.exceptions import RequestValidationError
from uvicorn.middleware.proxy_headers import ProxyHeadersMiddleware
from app.auth import get_current_user, upsert_user
from app.config import settings
from app.db import get_supabase_client
from app.url_cascade import LOCAL_DEV_ORIGIN_REGEX, is_local_app_env
from app.schemas.user import User
from app.routers import entries, share_links, shared, google_auth, push
from app.exceptions import (
    EntryNotFoundException,
    ShareLinkNotFoundException,
    DuplicateEntryException,
    InvalidEmojiException,
    entry_not_found_handler,
    share_link_not_found_handler,
    duplicate_entry_handler,
    invalid_emoji_handler,
    rate_limit_exceeded_handler,
    validation_error_handler
)
from app.services.rate_limit import RateLimitExceeded

app = FastAPI(
    title="Journal App Backend",
    description="A FastAPI backend for a digital journal app with shared entries and emoji reactions",
    version="1.0.0"
)

# Register custom exception handlers
app.add_exception_handler(EntryNotFoundException, entry_not_found_handler)
app.add_exception_handler(ShareLinkNotFoundException, share_link_not_found_handler)
app.add_exception_handler(DuplicateEntryException, duplicate_entry_handler)
app.add_exception_handler(InvalidEmojiException, invalid_emoji_handler)
app.add_exception_handler(RateLimitExceeded, rate_limit_exceeded_handler)
app.add_exception_handler(RequestValidationError, validation_error_handler)

# Include routers
app.include_router(entries.router)
app.include_router(share_links.router)
app.include_router(shared.router)
app.include_router(google_auth.router)
app.include_router(push.router)

def _cors_origins() -> list[str]:
    return settings.frontend_origins()


def _cors_origin_regex() -> str | None:
    if is_local_app_env(settings.app_env):
        return LOCAL_DEV_ORIGIN_REGEX
    return None


_cors_kwargs = {
    "allow_origins": _cors_origins(),
    "allow_credentials": False,
    "allow_methods": ["*"],
    "allow_headers": ["*"],
}
_cors_regex = _cors_origin_regex()
if _cors_regex:
    _cors_kwargs["allow_origin_regex"] = _cors_regex

app.add_middleware(CORSMiddleware, **_cors_kwargs)
app.add_middleware(ProxyHeadersMiddleware, trusted_hosts="*")


@app.get("/health")
async def health_check():
    """Health check endpoint to verify the service is running."""
    payload = {"status": "healthy", "service": "journal-app-backend", "database": "unknown"}
    try:
        get_supabase_client().table("users").select("id").limit(1).execute()
        payload["database"] = "ok"
    except Exception:
        payload["status"] = "degraded"
        payload["database"] = "error"
    return payload


@app.get("/me", response_model=User)
async def get_me(current_user: User = Depends(get_current_user)):
    """
    Get current authenticated user's profile.
    Upserts user into database on first call.
    """
    await upsert_user(current_user)
    return current_user
