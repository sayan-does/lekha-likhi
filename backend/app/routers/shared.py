"""Router for shared entry viewing and reactions (viewer-facing endpoints)."""

from fastapi import APIRouter, Depends, HTTPException, status
from app.auth import get_current_user
from app.schemas.user import User
from app.schemas.shared import SharedEntryResponse
from app.schemas.reaction import ReactionCreate, Reaction
from app.db import get_supabase_client
from app.services.rate_limit import get_rate_limit_service
from typing import List


router = APIRouter(prefix="/shared", tags=["shared"])


@router.get("/{token}", response_model=SharedEntryResponse)
async def get_shared_entry(token: str):
    """
    View a shared entry via its share token.
    
    Requirements:
    - Token must be valid and active
    - No authentication required to read
    - Returns entry body, date, owner display name, and all reactions
    
    Returns 404 if token is invalid, revoked, or doesn't exist.
    """
    supabase = get_supabase_client()
    rate_limit_service = get_rate_limit_service()
    
    # Try to get from cache first
    cached_data = await rate_limit_service.get_cached_share_link(token)
    
    if cached_data:
        # Check if active
        if not cached_data.get("is_active"):
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="This entry is no longer available"
            )
        entry_id = cached_data["entry_id"]
    else:
        # Fall back to database
        share_link_response = supabase.table("share_links").select(
            "entry_id, is_active"
        ).eq("token", token).execute()
        
        if not share_link_response.data:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="This entry is no longer available"
            )
        
        share_link = share_link_response.data[0]
        
        # Check if active
        if not share_link["is_active"]:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="This entry is no longer available"
            )
        
        entry_id = share_link["entry_id"]
        
        # Populate cache for next time
        await rate_limit_service.set_cached_share_link(
            token=token,
            entry_id=entry_id,
            is_active=share_link["is_active"]
        )
    
    # Fetch the entry with owner information
    entry_response = supabase.table("entries").select(
        "entry_date, body, owner_id, users!inner(display_name)"
    ).eq("id", entry_id).execute()
    
    if not entry_response.data:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="This entry is no longer available"
        )
    
    entry = entry_response.data[0]
    
    # Fetch reactions for this entry
    reactions_response = supabase.table("reactions").select(
        "emoji, user_id, users!inner(display_name)"
    ).eq("entry_id", entry_id).execute()
    
    # Transform reactions to include display names
    reactions = [
        Reaction(
            display_name=r["users"]["display_name"],
            emoji=r["emoji"]
        )
        for r in reactions_response.data
    ]
    
    return SharedEntryResponse(
        entry_date=entry["entry_date"],
        body=entry["body"],
        owner_display_name=entry["users"]["display_name"],
        reactions=reactions
    )


@router.get("/{token}/reactions", response_model=List[Reaction])
async def get_shared_entry_reactions(token: str):
    """
    Get reactions for a shared entry.
    Useful for real-time updates without re-fetching the entire entry.
    """
    supabase = get_supabase_client()
    rate_limit_service = get_rate_limit_service()
    
    # Try to get from cache first
    cached_data = await rate_limit_service.get_cached_share_link(token)
    
    if cached_data:
        if not cached_data.get("is_active"):
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="This entry is no longer available"
            )
        entry_id = cached_data["entry_id"]
    else:
        share_link_response = supabase.table("share_links").select(
            "entry_id, is_active"
        ).eq("token", token).execute()
        
        if not share_link_response.data or not share_link_response.data[0]["is_active"]:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="This entry is no longer available"
            )
            
        entry_id = share_link_response.data[0]["entry_id"]
    
    # Fetch reactions for this entry, ordered by created_at
    reactions_response = supabase.table("reactions").select(
        "emoji, user_id, users!inner(display_name)"
    ).eq("entry_id", entry_id).order("created_at").execute()
    
    reactions = [
        Reaction(
            display_name=r["users"]["display_name"],
            emoji=r["emoji"]
        )
        for r in reactions_response.data
    ]
    
    return reactions


@router.post("/{token}/react", status_code=status.HTTP_201_CREATED)
async def react_to_entry(
    token: str,
    reaction_data: ReactionCreate,
    current_user: User = Depends(get_current_user)
):
    """
    React to a shared entry with an emoji.
    
    Requirements:
    - Token must be valid and active
    - User must be authenticated
    - Emoji must be in the allowed set
    - One reaction per user per entry (upsert behavior)
    - Rate limited to 10 requests per minute per user per entry
    
    Returns 404 if token is invalid/revoked.
    Returns 422 if emoji is not in allowed set.
    Returns 429 if rate limit exceeded.
    """
    supabase = get_supabase_client()
    rate_limit_service = get_rate_limit_service()
    
    # Verify token and get entry_id (re-validate, don't trust client state)
    share_link_response = supabase.table("share_links").select(
        "entry_id, is_active"
    ).eq("token", token).execute()
    
    if not share_link_response.data or not share_link_response.data[0]["is_active"]:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="This entry is no longer available"
        )
    
    entry_id = share_link_response.data[0]["entry_id"]
    
    # Check rate limit
    await rate_limit_service.check_rate_limit(
        user_id=current_user.id,
        entry_id=entry_id,
        limit=10,
        window_seconds=60
    )
    
    # Upsert reaction (one per user per entry)
    # Check if reaction exists
    existing_reaction = supabase.table("reactions").select("id").eq(
        "entry_id", entry_id
    ).eq(
        "user_id", str(current_user.id)
    ).execute()
    
    if existing_reaction.data:
        # Update existing reaction
        supabase.table("reactions").update({
            "emoji": reaction_data.emoji
        }).eq("id", existing_reaction.data[0]["id"]).execute()
    else:
        # Insert new reaction
        supabase.table("reactions").insert({
            "entry_id": entry_id,
            "user_id": str(current_user.id),
            "emoji": reaction_data.emoji
        }).execute()
    
    return {"message": "Reaction added successfully"}


@router.delete("/{token}/react", status_code=status.HTTP_204_NO_CONTENT)
async def remove_reaction(
    token: str,
    current_user: User = Depends(get_current_user)
):
    """
    Remove current user's reaction from a shared entry.
    
    Requirements:
    - Token must be valid and active
    - User must be authenticated
    - Only removes the current user's reaction
    
    Returns 404 if token is invalid/revoked or if no reaction exists.
    """
    supabase = get_supabase_client()
    
    # Verify token and get entry_id
    share_link_response = supabase.table("share_links").select(
        "entry_id, is_active"
    ).eq("token", token).execute()
    
    if not share_link_response.data or not share_link_response.data[0]["is_active"]:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="This entry is no longer available"
        )
    
    entry_id = share_link_response.data[0]["entry_id"]
    
    # Check if reaction exists
    existing_reaction = supabase.table("reactions").select("id").eq(
        "entry_id", entry_id
    ).eq(
        "user_id", str(current_user.id)
    ).execute()
    
    if not existing_reaction.data:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="No reaction found to remove"
        )
    
    # Delete the reaction
    supabase.table("reactions").delete().eq(
        "id", existing_reaction.data[0]["id"]
    ).execute()
    
    return None
