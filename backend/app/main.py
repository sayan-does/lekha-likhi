from fastapi import FastAPI, Depends
from fastapi.middleware.cors import CORSMiddleware
from app.auth import get_current_user, upsert_user
from app.schemas.user import User

app = FastAPI(
    title="Journal App Backend",
    description="A FastAPI backend for a digital journal app with shared entries and emoji reactions",
    version="1.0.0"
)

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
