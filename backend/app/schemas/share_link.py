from pydantic import BaseModel
from datetime import datetime
from uuid import UUID
from typing import Optional


class ShareLinkCreate(BaseModel):
    """Schema for creating a share link (no input required)."""
    pass


class ShareLink(BaseModel):
    """Full share link schema returned from the API."""
    id: UUID
    entry_id: UUID
    token: str
    is_active: bool
    created_at: datetime
    revoked_at: Optional[datetime] = None
    
    class Config:
        from_attributes = True


class ShareLinkResponse(BaseModel):
    """Response when creating a share link."""
    token: str
    url: str


class ShareLinkListItem(BaseModel):
    """Share link item in management list."""
    id: UUID
    entry_id: UUID
    token: str
    is_active: bool
    created_at: datetime
    revoked_at: Optional[datetime] = None
    entry_date: str  # From joined entry data
    
    class Config:
        from_attributes = True
