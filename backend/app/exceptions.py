"""Custom exception handlers for the Journal App API.

This module defines custom exceptions and their handlers to ensure consistent
error responses across the application per section 6 of the spec.
"""

from fastapi import Request, status
from fastapi.responses import JSONResponse
from fastapi.exceptions import RequestValidationError
from app.services.rate_limit import RateLimitExceeded


class EntryNotFoundException(Exception):
    """Exception raised when an entry is not found (used for 404 instead of 403)."""
    def __init__(self, detail: str = "Entry not found"):
        self.detail = detail
        super().__init__(self.detail)


class ShareLinkNotFoundException(Exception):
    """Exception raised when a share link is not found or revoked."""
    def __init__(self, detail: str = "This entry is no longer available"):
        self.detail = detail
        super().__init__(self.detail)


class DuplicateEntryException(Exception):
    """Exception raised when a duplicate entry is created (race condition)."""
    def __init__(self, detail: str = "Entry already exists for this date"):
        self.detail = detail
        super().__init__(self.detail)


class InvalidEmojiException(Exception):
    """Exception raised when an invalid emoji is provided."""
    def __init__(self, emoji: str, allowed_emojis: list[str]):
        self.emoji = emoji
        self.allowed_emojis = allowed_emojis
        self.detail = f"Invalid emoji '{emoji}'. Allowed emojis: {', '.join(allowed_emojis)}"
        super().__init__(self.detail)


async def entry_not_found_handler(request: Request, exc: EntryNotFoundException) -> JSONResponse:
    """Handler for EntryNotFoundException - returns 404."""
    return JSONResponse(
        status_code=status.HTTP_404_NOT_FOUND,
        content={"detail": exc.detail}
    )


async def share_link_not_found_handler(request: Request, exc: ShareLinkNotFoundException) -> JSONResponse:
    """Handler for ShareLinkNotFoundException - returns 404 with specific message."""
    return JSONResponse(
        status_code=status.HTTP_404_NOT_FOUND,
        content={"detail": exc.detail}
    )


async def duplicate_entry_handler(request: Request, exc: DuplicateEntryException) -> JSONResponse:
    """Handler for DuplicateEntryException - returns 409 Conflict."""
    return JSONResponse(
        status_code=status.HTTP_409_CONFLICT,
        content={"detail": exc.detail}
    )


async def invalid_emoji_handler(request: Request, exc: InvalidEmojiException) -> JSONResponse:
    """Handler for InvalidEmojiException - returns 422 with allowed list."""
    return JSONResponse(
        status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
        content={
            "detail": exc.detail,
            "allowed_emojis": exc.allowed_emojis
        }
    )


async def rate_limit_exceeded_handler(request: Request, exc: RateLimitExceeded) -> JSONResponse:
    """Handler for RateLimitExceeded - returns 429 with Retry-After header."""
    return JSONResponse(
        status_code=status.HTTP_429_TOO_MANY_REQUESTS,
        content={"detail": "Too many reactions, try again shortly"},
        headers={"Retry-After": str(exc.retry_after)}
    )


async def validation_error_handler(request: Request, exc: RequestValidationError) -> JSONResponse:
    """
    Handler for Pydantic validation errors.
    
    Special handling for emoji validation to return proper 422 with allowed list.
    """
    # Check if this is an emoji validation error
    for error in exc.errors():
        if error.get("loc") and "emoji" in error.get("loc", []):
            # Import here to avoid circular dependency
            from app.schemas.reaction import ALLOWED_EMOJIS
            return JSONResponse(
                status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                content={
                    "detail": f"Invalid emoji. Allowed emojis: {', '.join(ALLOWED_EMOJIS)}",
                    "allowed_emojis": ALLOWED_EMOJIS
                }
            )
    
    # Default validation error response
    return JSONResponse(
        status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
        content={"detail": exc.errors()}
    )
