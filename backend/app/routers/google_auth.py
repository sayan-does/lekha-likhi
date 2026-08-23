from urllib.parse import quote, urlparse

from fastapi import APIRouter, Depends, HTTPException, Request, Response
from fastapi.responses import RedirectResponse
from app.config import settings
from app.db import get_supabase_client
from datetime import datetime, timedelta, timezone
from jose import jwt
import httpx
import uuid

router = APIRouter(prefix="/auth/google", tags=["auth"])

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

    allowed_hosts = {urlparse(item).netloc for item in settings.frontend_origins()}
    if parsed.netloc in allowed_hosts:
        return candidate

    return default


@router.get("/login")
async def google_login(request: Request, origin: str | None = None):
    """Redirects the user to Google's OAuth 2.0 consent screen."""
    redirect_uri = str(request.url_for("google_callback"))
    frontend_target = resolve_frontend_url(origin)
    
    auth_url = (
        f"{GOOGLE_OAUTH_URL}?"
        f"client_id={settings.google_client_id}&"
        f"response_type=code&"
        f"redirect_uri={redirect_uri}&"
        f"scope=openid email profile&"
        f"access_type=offline&"
        f"state={quote(frontend_target, safe='')}"
    )
    return RedirectResponse(auth_url)


@router.get("/callback")
async def google_callback(request: Request, code: str, state: str | None = None):
    """Handles the callback from Google, exchanges code for token, and creates a session."""
    redirect_uri = str(request.url_for("google_callback"))
    frontend_target = resolve_frontend_url(state)
    
    # 1. Exchange the authorization code for an access token
    async with httpx.AsyncClient() as client:
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
            raise HTTPException(status_code=400, detail="Failed to retrieve token from Google")
        
        token_data = token_response.json()
        access_token = token_data.get("access_token")
        
        # 2. Use the access token to get user info from Google
        userinfo_response = await client.get(
            GOOGLE_USERINFO_URL,
            headers={"Authorization": f"Bearer {access_token}"}
        )
        if userinfo_response.status_code != 200:
            raise HTTPException(status_code=400, detail="Failed to retrieve user info from Google")
            
        user_info = userinfo_response.json()
        
    email = user_info.get("email")
    display_name = user_info.get("name")
    avatar_url = user_info.get("picture")
    
    if not email:
        raise HTTPException(status_code=400, detail="Email not provided by Google")
        
    # 3. Upsert user in Supabase manually
    supabase = get_supabase_client()
    
    # Check if user exists by email (if they do, we'll use their existing ID)
    # Since we don't have auth.users exposed directly easily, we manage our own users table.
    user_res = supabase.table("users").select("*").eq("email", email).execute()
    
    if user_res.data:
        user_id = user_res.data[0]["id"]
        # Update their profile just in case
        supabase.table("users").update({
            "display_name": display_name,
            "avatar_url": avatar_url
        }).eq("id", user_id).execute()
    else:
        # Create new user
        user_id = str(uuid.uuid4())
        supabase.table("users").insert({
            "id": user_id,
            "email": email,
            "display_name": display_name,
            "avatar_url": avatar_url
        }).execute()
        
    # 4. Mint our own JWT so the rest of the backend (app/auth.py) can authenticate the user
    # Our app/auth.py expects "sub" to be the user_id, and optionally "email", "name", "picture"
    payload = {
        "sub": user_id,
        "email": email,
        "name": display_name,
        "picture": avatar_url,
        "iat": datetime.now(timezone.utc),
        "exp": datetime.now(timezone.utc) + timedelta(days=7), # 7 day expiration
        "role": "authenticated"
    }
    
    # We sign it with our SUPABASE_JWT_SECRET so that app/auth.py can verify it seamlessly!
    jwt_token = jwt.encode(payload, settings.supabase_jwt_secret, algorithm="HS256")
    
    # 5. Return the token to the frontend
    # We redirect the user back to the frontend application, passing the token in the URL hash
    # (or you can use HttpOnly cookies for even better security!)
    redirect_url = f"{frontend_target}/#access_token={jwt_token}"
    return RedirectResponse(redirect_url)
