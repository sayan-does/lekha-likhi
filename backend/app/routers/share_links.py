from fastapi import APIRouter, Depends, HTTPException, status
from typing import List
from uuid import UUID
from app.auth import get_current_user
from app.schemas.user import User
from app.schemas.share_link import ShareLinkResponse, ShareLinkListItem
from app.db import get_supabase_client, generate_share_token
from app.services.rate_limit import get_rate_limit_service


router = APIRouter(tags=["share_links"])


@router.post("/entries/{entry_id}/share", response_model=ShareLinkResponse)
async def create_share_link(
    entry_id: UUID,
    current_user: User = Depends(get_current_user)
):
    """
    Create a new active share link for an entry.
    Only the entry owner can create share links.
    """
    supabase = get_supabase_client()
    
    # Verify the entry exists and belongs to current user
    entry_response = supabase.table("entries").select("id, owner_id").eq(
        "id", str(entry_id)
    ).execute()
    
    if not entry_response.data:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Entry not found"
        )
    
    entry = entry_response.data[0]
    if entry["owner_id"] != str(current_user.id):
        # Return 404 instead of 403 to avoid leaking information
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Entry not found"
        )
    
    # Generate unique token
    token = generate_share_token()
    
    # Create share link
    share_link_response = supabase.table("share_links").insert({
        "entry_id": str(entry_id),
        "token": token,
        "is_active": True
    }).execute()
    
    # Construct the share URL (frontend will handle the actual URL construction)
    share_url = f"/shared/{token}"
    
    return ShareLinkResponse(token=token, url=share_url)


@router.get("/share-links", response_model=List[ShareLinkListItem])
async def list_share_links(
    current_user: User = Depends(get_current_user)
):
    """
    List all share links owned by the current user (across all their entries).
    Includes entry_date for management UI.
    """
    supabase = get_supabase_client()
    
    # Query share links with joined entry data
    # Note: Supabase PostgREST syntax for joins
    response = supabase.table("share_links").select(
        "id, entry_id, token, is_active, created_at, revoked_at, entries!inner(entry_date, owner_id)"
    ).eq(
        "entries.owner_id", str(current_user.id)
    ).order("created_at", desc=True).execute()
    
    # Transform the response to flatten the structure
    result = []
    for item in response.data:
        result.append({
            "id": item["id"],
            "entry_id": item["entry_id"],
            "token": item["token"],
            "is_active": item["is_active"],
            "created_at": item["created_at"],
            "revoked_at": item.get("revoked_at"),
            "entry_date": str(item["entries"]["entry_date"])
        })
    
    return result


@router.delete("/share-links/{token}", status_code=status.HTTP_204_NO_CONTENT)
async def revoke_share_link(
    token: str,
    current_user: User = Depends(get_current_user)
):
    """
    Revoke a share link (set is_active = false).
    Only the entry owner can revoke their share links.
    """
    supabase = get_supabase_client()
    
    # Find the share link with entry ownership verification
    share_link_response = supabase.table("share_links").select(
        "id, entry_id, entries!inner(owner_id)"
    ).eq("token", token).execute()
    
    if not share_link_response.data:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Share link not found"
        )
    
    share_link = share_link_response.data[0]
    
    # Verify ownership
    if share_link["entries"]["owner_id"] != str(current_user.id):
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Share link not found"
        )
    
    # Revoke the link
    supabase.table("share_links").update({
        "is_active": False,
        "revoked_at": "now()"
    }).eq("id", share_link["id"]).execute()
    
    # Invalidate Upstash cache key share_link:{token}
    rate_limit_service = get_rate_limit_service()
    await rate_limit_service.invalidate_share_link_cache(token)
    
    return None
