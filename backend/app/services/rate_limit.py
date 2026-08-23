"""Rate limiting service using Upstash Redis."""

import json
import httpx
from app.config import settings
from typing import Any, Tuple
from uuid import UUID


def parse_cached_share_link(result: Any) -> dict | None:
    """Normalize a Redis GET result into share-link cache data.

    Older writers stored a JSON string via httpx ``json=``, so Redis may
    contain one extra encoding layer. Unwrap at most twice, then require
    a dict with ``entry_id``.
    """
    if result is None:
        return None

    data = result
    for _ in range(2):
        if not isinstance(data, str):
            break
        try:
            data = json.loads(data)
        except json.JSONDecodeError:
            return None

    if not isinstance(data, dict) or not data.get("entry_id"):
        return None
    return data


class RateLimitExceeded(Exception):
    """Exception raised when rate limit is exceeded."""
    def __init__(self, message: str, retry_after: int = 60):
        self.retry_after = retry_after
        super().__init__(message)


class RateLimitService:
    """Service for rate limiting using Upstash Redis REST API."""
    
    def __init__(self):
        self.base_url = settings.upstash_redis_url.rstrip('/')
        self.token = settings.upstash_redis_token
        self.headers = {
            "Authorization": f"Bearer {self.token}",
            "Content-Type": "application/json"
        }
    
    async def check_rate_limit(
        self,
        user_id: UUID,
        entry_id: UUID,
        limit: int = 10,
        window_seconds: int = 60
    ) -> Tuple[bool, int]:
        """
        Check if user has exceeded rate limit for reactions on this entry.
        
        Args:
            user_id: The user's UUID
            entry_id: The entry's UUID
            limit: Maximum number of requests allowed in window (default 10)
            window_seconds: Time window in seconds (default 60)
        
        Returns:
            Tuple of (allowed: bool, current_count: int)
        
        Raises:
            RateLimitExceeded: If rate limit is exceeded
        """
        key = f"ratelimit:react:{user_id}:{entry_id}"
        
        async with httpx.AsyncClient() as client:
            # Increment counter
            incr_response = await client.post(
                f"{self.base_url}/incr/{key}",
                headers=self.headers
            )
            incr_response.raise_for_status()
            count = incr_response.json().get("result", 1)
            
            # Set expiry on first request (when count == 1)
            if count == 1:
                expire_response = await client.post(
                    f"{self.base_url}/expire/{key}/{window_seconds}",
                    headers=self.headers
                )
                expire_response.raise_for_status()
            
            # Check if limit exceeded
            if count > limit:
                # Try to get TTL for accurate Retry-After
                ttl = window_seconds
                try:
                    ttl_response = await client.post(
                        f"{self.base_url}/ttl/{key}",
                        headers=self.headers
                    )
                    if ttl_response.status_code == 200:
                        ttl_val = ttl_response.json().get("result", window_seconds)
                        if ttl_val > 0:
                            ttl = ttl_val
                except Exception:
                    pass
                    
                raise RateLimitExceeded(
                    f"Rate limit exceeded: {count}/{limit} requests in {window_seconds}s window",
                    retry_after=ttl
                )
            
            return True, count
    
    async def get_cached_share_link(self, token: str) -> dict | None:
        """
        Get cached share link data from Redis.
        
        Args:
            token: The share link token
        
        Returns:
            Dict with entry_id and is_active, or None if not cached
        """
        key = f"share_link:{token}"

        try:
            async with httpx.AsyncClient() as client:
                response = await client.post(
                    self.base_url,
                    headers=self.headers,
                    json=["GET", key],
                )
                response.raise_for_status()
                return parse_cached_share_link(response.json().get("result"))
        except Exception:
            return None
    
    async def set_cached_share_link(
        self,
        token: str,
        entry_id: str,
        is_active: bool,
        ttl_seconds: int = 300
    ) -> None:
        """
        Cache share link data in Redis.
        
        Args:
            token: The share link token
            entry_id: The entry UUID
            is_active: Whether the link is active
            ttl_seconds: Time to live in seconds (default 5 minutes)
        """
        key = f"share_link:{token}"
        value = json.dumps({
            "entry_id": entry_id,
            "is_active": is_active
        })

        try:
            async with httpx.AsyncClient() as client:
                # Command-array body avoids double-encoding the JSON value.
                response = await client.post(
                    self.base_url,
                    headers=self.headers,
                    json=["SETEX", key, ttl_seconds, value],
                )
                response.raise_for_status()
        except Exception:
            return
    
    async def invalidate_share_link_cache(self, token: str) -> None:
        """
        Invalidate (delete) cached share link data.
        
        Args:
            token: The share link token to invalidate
        """
        key = f"share_link:{token}"
        
        async with httpx.AsyncClient() as client:
            response = await client.post(
                f"{self.base_url}/del/{key}",
                headers=self.headers
            )
            response.raise_for_status()


# Singleton instance
_rate_limit_service: RateLimitService | None = None


def get_rate_limit_service() -> RateLimitService:
    """Get or create the rate limit service singleton."""
    global _rate_limit_service
    if _rate_limit_service is None:
        _rate_limit_service = RateLimitService()
    return _rate_limit_service
