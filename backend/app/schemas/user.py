from pydantic import BaseModel
from uuid import UUID
from typing import Optional


class User(BaseModel):
    """User model representing authenticated user."""
    id: UUID
    email: str
    display_name: str
    avatar_url: Optional[str] = None


class UserInDB(User):
    """User model as stored in database with timestamps."""
    created_at: str
