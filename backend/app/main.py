from fastapi import FastAPI, Depends
from fastapi.middleware.cors import CORSMiddleware
from fastapi.exceptions import RequestValidationError
from app.auth import get_current_user, upsert_user
from app.schemas.user import User
from app.routers import entries, share_links, shared, google_auth
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

# CORS middleware configuration for frontend integration
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Configure appropriately for production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/health")
async def health_check():
    """Health check endpoint to verify the service is running."""
    return {"status": "healthy", "service": "journal-app-backend"}


@app.get("/me", response_model=User)
async def get_me(current_user: User = Depends(get_current_user)):
    """
    Get current authenticated user's profile.
    Upserts user into database on first call.
    """
    await upsert_user(current_user)
    return current_user
