from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from jose import jwt, JWTError
from app.schemas.user import User
from app.config import settings
from app.db import get_supabase_client
from uuid import UUID
import httpx
from typing import Optional


security = HTTPBearer()

# Cache for JWKS to avoid repeated requests
_jwks_cache: Optional[dict] = None


async def get_jwks() -> dict:
    """Fetch JWKS from Supabase for JWT verification."""
    global _jwks_cache
    if _jwks_cache is not None:
        return _jwks_cache
    
    # Extract project reference from Supabase URL
    # Format: https://PROJECT_REF.supabase.co
    project_ref = settings.supabase_url.split("//")[1].split(".")[0]
    jwks_url = f"https://{project_ref}.supabase.co/auth/v1/jwks"
    
    async with httpx.AsyncClient() as client:
        response = await client.get(jwks_url)
        response.raise_for_status()
        _jwks_cache = response.json()
        return _jwks_cache


async def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(security)
) -> User:
    """
    FastAPI dependency that extracts and verifies the JWT token,
    returning the authenticated user.
    
    Raises:
        HTTPException: 401 if token is invalid or missing
    """
    token = credentials.credentials
    
    try:
        # Verify JWT token using the Supabase JWT secret
        payload = jwt.decode(
            token,
            settings.supabase_jwt_secret,
            algorithms=["HS256"],
            options={"verify_aud": False}  # Supabase tokens don't always have aud
        )
        
        # Extract user information from token
        user_id = payload.get("sub")
        email = payload.get("email")
        user_metadata = payload.get("user_metadata", {})
        
        if not user_id or not email:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Not authenticated"
            )
        
        # Create User model from token data
        user = User(
            id=UUID(user_id),
            email=email,
            display_name=user_metadata.get("full_name") or user_metadata.get("name") or email.split("@")[0],
            avatar_url=user_metadata.get("avatar_url") or user_metadata.get("picture")
        )
        
        return user
        
    except JWTError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Not authenticated"
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Not authenticated"
        )


async def upsert_user(user: User) -> None:
    """
    Upsert user into the database on first login.
    """
    try:
        supabase_client = get_supabase_client()
        # Check if user exists
        response = supabase_client.table("users").select("*").eq("id", str(user.id)).execute()
        
        if not response.data:
            # Insert new user
            supabase_client.table("users").insert({
                "id": str(user.id),
                "email": user.email,
                "display_name": user.display_name,
                "avatar_url": user.avatar_url
            }).execute()
        else:
            # Update existing user (in case profile data changed)
            supabase_client.table("users").update({
                "email": user.email,
                "display_name": user.display_name,
                "avatar_url": user.avatar_url
            }).eq("id", str(user.id)).execute()
            
    except Exception as e:
        # Log error but don't block authentication
        print(f"Error upserting user: {e}")
