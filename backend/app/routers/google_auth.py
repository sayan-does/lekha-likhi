from urllib.parse import quote, urlencode, urlparse
from fastapi import APIRouter, Request
from fastapi.responses import RedirectResponse
from app.config import settings
from app.url_cascade import is_local_app_env, is_loopback_or_private_host
from app.db import get_supabase_client
from datetime import datetime, timedelta, timezone
from jose import jwt
import httpx
import logging
import uuid

router = APIRouter(prefix="/auth/google", tags=["auth"])
logger = logging.getLogger(__name__)

GOOGLE_OAUTH_URL = "https://accounts.google.com/o/oauth2/v2/auth"
GOOGLE_TOKEN_URL = "https://oauth2.googleapis.com/token"
GOOGLE_USERINFO_URL = "https://www.googleapis.com/oauth2/v2/userinfo"

# Note: The redirect URI must match the one configured in the Google Developer Console EXACTLY.
# For local development, this usually looks like http://localhost:8000/auth/google/callback
# Or whatever frontend domain if the frontend handles the redirect. In this setup, we handle it.


def resolve_frontend_url(origin: str | None) -> str:
    """Pick a safe redirect target for the OAuth callback."""
    default = settings.resolved_frontend_url
    if not origin:
        return default

    candidate = origin.rstrip("/")
    parsed = urlparse(candidate)
    if parsed.scheme not in {"http", "https"} or not parsed.netloc:
        return default

    if parsed.hostname in {"localhost", "127.0.0.1"}:
        return candidate

    if is_local_app_env(settings.app_env) and is_loopback_or_private_host(parsed.hostname):
        return candidate

    allowed_hosts = {urlparse(item).netloc for item in settings.frontend_origins()}
    if parsed.netloc in allowed_hosts:
        return candidate

    return default


def callback_redirect_uri(request: Request) -> str:
    return str(request.url_for("google_callback"))


def display_name_from_google(user_info: dict, email: str) -> str:
    name = (user_info.get("name") or user_info.get("given_name") or "").strip()
    if name:
        return name
    prefix = (email.split("@")[0] if email else "").strip()
    return prefix or "Writer"


def upsert_google_user(email: str, display_name: str, avatar_url: str | None) -> str:
    """Find or create the app user. Profile updates must not block sign-in."""
    supabase = get_supabase_client()
    user_res = supabase.table("users").select("id").eq("email", email).execute()

    if user_res.data:
        user_id = user_res.data[0]["id"]
        try:
            supabase.table("users").update({
                "display_name": display_name,
                "avatar_url": avatar_url,
            }).eq("id", user_id).execute()
        except Exception:
            logger.exception("Failed to update Google user profile for %s", email)
        return user_id

    user_id = str(uuid.uuid4())
    supabase.table("users").insert({
        "id": user_id,
        "email": email,
        "display_name": display_name,
        "avatar_url": avatar_url,
    }).execute()
    return user_id


def mint_session_token(user_id: str, email: str, display_name: str, avatar_url: str | None) -> str:
    now = datetime.now(timezone.utc)
    payload = {
        "sub": user_id,
        "email": email,
        "name": display_name,
        "picture": avatar_url,
        "iat": int(now.timestamp()),
        "exp": int((now + timedelta(days=7)).timestamp()),
        "role": "authenticated",
    }
    return jwt.encode(payload, settings.supabase_jwt_secret, algorithm="HS256")


def _frontend_error_redirect(frontend_target: str, code: str) -> RedirectResponse:
    return RedirectResponse(f"{frontend_target}/#auth_error={quote(code, safe='')}")


@router.get("/login")
async def google_login(request: Request, origin: str | None = None):
    """Redirects the user to Google's OAuth 2.0 consent screen."""
    redirect_uri = callback_redirect_uri(request)
    frontend_target = resolve_frontend_url(origin)

    auth_url = (
        f"{GOOGLE_OAUTH_URL}?"
        + urlencode(
            {
                "client_id": settings.google_client_id,
                "response_type": "code",
                "redirect_uri": redirect_uri,
                "scope": "openid email profile",
                "access_type": "offline",
                "state": frontend_target,
            }
        )
    )
    return RedirectResponse(auth_url)


@router.get("/callback")
async def google_callback(
    request: Request,
    code: str | None = None,
    state: str | None = None,
    error: str | None = None,
):
    """Handles the callback from Google, exchanges code for token, and creates a session."""
    redirect_uri = callback_redirect_uri(request)
    frontend_target = resolve_frontend_url(state)

    if error or not code:
        logger.warning("Google OAuth callback missing code or returned error=%s", error)
        return _frontend_error_redirect(frontend_target, "google_denied")

    try:
        async with httpx.AsyncClient(timeout=20.0) as client:
            token_response = await client.post(
                GOOGLE_TOKEN_URL,
                data={
                    "client_id": settings.google_client_id,
                    "client_secret": settings.google_client_secret,
                    "code": code,
                    "grant_type": "authorization_code",
                    "redirect_uri": redirect_uri,
                },
            )
            if token_response.status_code != 200:
                logger.warning(
                    "Google token exchange failed status=%s body=%s",
                    token_response.status_code,
                    token_response.text[:300],
                )
                return _frontend_error_redirect(frontend_target, "google_token")

            access_token = token_response.json().get("access_token")
            if not access_token:
                return _frontend_error_redirect(frontend_target, "google_token")

            userinfo_response = await client.get(
                GOOGLE_USERINFO_URL,
                headers={"Authorization": f"Bearer {access_token}"},
            )
            if userinfo_response.status_code != 200:
                logger.warning(
                    "Google userinfo failed status=%s body=%s",
                    userinfo_response.status_code,
                    userinfo_response.text[:300],
                )
                return _frontend_error_redirect(frontend_target, "google_profile")

            user_info = userinfo_response.json()

        email = (user_info.get("email") or "").strip()
        if not email:
            return _frontend_error_redirect(frontend_target, "google_profile")

        display_name = display_name_from_google(user_info, email)
        avatar_url = user_info.get("picture")
        user_id = upsert_google_user(email, display_name, avatar_url)
        jwt_token = mint_session_token(user_id, email, display_name, avatar_url)
        return RedirectResponse(f"{frontend_target}/#access_token={jwt_token}")
    except Exception as exc:
        logger.exception("Google OAuth callback failed")
        if exc.__class__.__name__ == "APIError":
            return _frontend_error_redirect(frontend_target, "db_error")
        return _frontend_error_redirect(frontend_target, "unknown")
