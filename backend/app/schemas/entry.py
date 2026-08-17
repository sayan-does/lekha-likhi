from pydantic import BaseModel
from datetime import date, datetime
from uuid import UUID


class EntryBase(BaseModel):
    """Base schema for entry data."""
    body: str


class EntryCreate(EntryBase):
    """Schema for creating or updating an entry."""
    pass


class EntryUpdate(EntryBase):
    """Schema for updating an entry."""
    pass


class Entry(EntryBase):
    """Full entry schema returned from the API."""
    id: UUID
    owner_id: UUID
    entry_date: date
    created_at: datetime
    updated_at: datetime
    
    class Config:
        from_attributes = True


class EntryListItem(BaseModel):
    """Simplified entry schema for list views."""
    id: UUID
    entry_date: date
    body: str
    created_at: datetime
    updated_at: datetime
    
    class Config:
        from_attributes = True


class EntryListResponse(BaseModel):
    """Paginated response for entry lists."""
    entries: list[EntryListItem]
    total: int
    limit: int
    offset: int
