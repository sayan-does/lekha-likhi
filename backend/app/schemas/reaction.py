from pydantic import BaseModel, Field
from uuid import UUID
from typing import Literal


# Allowed emoji set as per spec
ALLOWED_EMOJIS = ["❤️", "😢", "👏", "😂", "😮"]

AllowedEmoji = Literal["❤️", "😢", "👏", "😂", "😮"]


class ReactionCreate(BaseModel):
    """Schema for creating or updating a reaction."""
    emoji: AllowedEmoji = Field(..., description="Emoji must be one of the allowed set")


class Reaction(BaseModel):
    """Reaction response with user display name."""
    display_name: str
    emoji: str
    
    class Config:
        from_attributes = True


class ReactionInDB(BaseModel):
    """Full reaction schema as stored in database."""
    id: UUID
    entry_id: UUID
    user_id: UUID
    emoji: str
    created_at: str
    
    class Config:
        from_attributes = True
