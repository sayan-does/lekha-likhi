from fastapi import APIRouter, Depends, Header, HTTPException, status

from app.auth import get_current_user
from app.config import settings
from app.db import get_supabase_client
from app.schemas.push import (
    DispatchRemindersResponse,
    PushStatusResponse,
    PushSubscriptionPayload,
    VapidPublicKeyResponse,
)
from app.schemas.user import User
from app.services.push import dispatch_reminders

router = APIRouter(prefix="/push", tags=["push"])


@router.get("/vapid-public-key", response_model=VapidPublicKeyResponse)
async def get_vapid_public_key():
    return VapidPublicKeyResponse(public_key=settings.vapid_public_key)


@router.get("/status", response_model=PushStatusResponse)
async def get_push_status(current_user: User = Depends(get_current_user)):
    supabase = get_supabase_client()
    user_response = (
        supabase.table("users")
        .select("reminders_enabled")
        .eq("id", str(current_user.id))
        .single()
        .execute()
    )
    enabled = bool(user_response.data and user_response.data.get("reminders_enabled"))

    subs_response = (
        supabase.table("push_subscriptions")
        .select("id")
        .eq("user_id", str(current_user.id))
        .limit(1)
        .execute()
    )
    subscribed = bool(subs_response.data)

    return PushStatusResponse(enabled=enabled, subscribed=subscribed)


@router.post("/subscribe", status_code=status.HTTP_204_NO_CONTENT)
async def subscribe_to_push(
    payload: PushSubscriptionPayload,
    current_user: User = Depends(get_current_user),
):
    supabase = get_supabase_client()
    supabase.table("push_subscriptions").upsert(
        {
            "user_id": str(current_user.id),
            "endpoint": payload.endpoint,
            "p256dh": payload.keys.p256dh,
            "auth_key": payload.keys.auth,
            "timezone": payload.timezone,
        },
        on_conflict="user_id,endpoint",
    ).execute()

    supabase.table("users").update({"reminders_enabled": True}).eq(
        "id", str(current_user.id)
    ).execute()


@router.delete("/subscribe", status_code=status.HTTP_204_NO_CONTENT)
async def unsubscribe_from_push(
    payload: PushSubscriptionPayload,
    current_user: User = Depends(get_current_user),
):
    supabase = get_supabase_client()
    supabase.table("push_subscriptions").delete().eq(
        "user_id", str(current_user.id)
    ).eq("endpoint", payload.endpoint).execute()

    remaining = (
        supabase.table("push_subscriptions")
        .select("id")
        .eq("user_id", str(current_user.id))
        .limit(1)
        .execute()
    )
    if not remaining.data:
        supabase.table("users").update({"reminders_enabled": False}).eq(
            "id", str(current_user.id)
        ).execute()


@router.post("/dispatch-reminders", response_model=DispatchRemindersResponse)
async def dispatch_reminder_notifications(
    x_cron_secret: str | None = Header(default=None, alias="X-Cron-Secret"),
):
    if not settings.cron_secret or x_cron_secret != settings.cron_secret:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid cron secret",
        )

    result = dispatch_reminders()
    return DispatchRemindersResponse(**result)
