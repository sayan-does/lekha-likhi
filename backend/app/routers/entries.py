from fastapi import APIRouter, Depends, HTTPException, status, Query
from typing import Optional
from datetime import date
from app.auth import get_current_user
from app.schemas.user import User
from app.schemas.entry import Entry, EntryCreate, EntryListResponse
from app.db import get_supabase_client


router = APIRouter(prefix="/entries", tags=["entries"])


@router.get("", response_model=EntryListResponse)
async def list_entries(
    from_date: Optional[date] = Query(None, alias="from"),
    to_date: Optional[date] = Query(None, alias="to"),
    limit: int = Query(50, ge=1, le=100),
    offset: int = Query(0, ge=0),
    current_user: User = Depends(get_current_user)
):
    """
    List current user's entries in date range, paginated.
    Defaults to all entries if no date range specified.
    """
    supabase = get_supabase_client()
    
    # Build query for current user's entries with count
    query = supabase.table("entries").select("*", count="exact").eq("owner_id", str(current_user.id))
    
    # Apply date filters if provided
    if from_date:
        query = query.gte("entry_date", str(from_date))
    if to_date:
        query = query.lte("entry_date", str(to_date))
    
    # Order by date descending
    query = query.order("entry_date", desc=True)
    
    # Apply pagination
    query = query.range(offset, offset + limit - 1)
    
    response = query.execute()
    
    total = response.count if response.count is not None else len(response.data)
    
    return EntryListResponse(
        entries=response.data,
        total=total,
        limit=limit,
        offset=offset
    )


@router.get("/{entry_date}", response_model=Entry)
async def get_entry(
    entry_date: date,
    current_user: User = Depends(get_current_user)
):
    """
    Get current user's entry for a specific date.
    Returns 404 if no entry exists for that date.
    """
    supabase = get_supabase_client()
    
    response = supabase.table("entries").select("*").eq(
        "owner_id", str(current_user.id)
    ).eq(
        "entry_date", str(entry_date)
    ).execute()
    
    if not response.data:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Entry not found"
        )
    
    return response.data[0]


@router.put("/{entry_date}", response_model=Entry)
async def upsert_entry(
    entry_date: date,
    entry_data: EntryCreate,
    current_user: User = Depends(get_current_user)
):
    """
    Create or update current user's entry for a specific date (upsert).
    """
    supabase = get_supabase_client()
    
    # Check if entry already exists
    existing = supabase.table("entries").select("*").eq(
        "owner_id", str(current_user.id)
    ).eq(
        "entry_date", str(entry_date)
    ).execute()
    
    if existing.data:
        # Update existing entry
        response = supabase.table("entries").update({
            "body": entry_data.body,
            "updated_at": "now()"
        }).eq(
            "id", existing.data[0]["id"]
        ).execute()
        
        return response.data[0]
    else:
        # Create new entry
        try:
            response = supabase.table("entries").insert({
                "owner_id": str(current_user.id),
                "entry_date": str(entry_date),
                "body": entry_data.body
            }).execute()
            
            return response.data[0]
        except Exception as e:
            # Handle potential race condition with unique constraint
            if "duplicate" in str(e).lower() or "unique" in str(e).lower():
                raise HTTPException(
                    status_code=status.HTTP_409_CONFLICT,
                    detail="Entry already exists for this date"
                )
            raise


@router.delete("/{entry_date}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_entry(
    entry_date: date,
    current_user: User = Depends(get_current_user)
):
    """
    Delete current user's entry for a specific date.
    Returns 404 if no entry exists for that date.
    """
    supabase = get_supabase_client()
    
    # First check if entry exists
    existing = supabase.table("entries").select("id").eq(
        "owner_id", str(current_user.id)
    ).eq(
        "entry_date", str(entry_date)
    ).execute()
    
    if not existing.data:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Entry not found"
        )
    
    # Delete the entry
    supabase.table("entries").delete().eq(
        "id", existing.data[0]["id"]
    ).execute()
    
    return None
