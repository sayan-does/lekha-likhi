from pydantic import BaseModel
from datetime import date
from typing import List
from app.schemas.reaction import Reaction


class SharedEntryResponse(BaseModel):
    """Response for viewing a shared entry."""
    entry_date: date
    body: str
    owner_display_name: str
    reactions: List[Reaction] = []
    
    class Config:
        from_attributes = True
