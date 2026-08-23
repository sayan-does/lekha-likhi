from datetime import datetime, timedelta, timezone
from typing import Any
from zoneinfo import ZoneInfo

from pywebpush import WebPushException, webpush

from app.config import settings
from app.db import get_supabase_client

REMINDER_INTERVAL = timedelta(hours=4)
NOTIFICATION_TITLE = "Lekha Likhi"
NOTIFICATION_BODY = "What's on your mind today?"
NOTIFICATION_URL = "/write?today=1"


def local_today_iso(tz_name: str) -> str:
    try:
        tz = ZoneInfo(tz_name)
    except Exception:
        tz = timezone.utc
    return datetime.now(tz).date().isoformat()


def user_has_entry_for_date(user_id: str, entry_date: str) -> bool:
    supabase = get_supabase_client()
    response = (
        supabase.table("entries")
        .select("id")
        .eq("owner_id", user_id)
        .eq("entry_date", entry_date)
        .limit(1)
        .execute()
    )
    return bool(response.data)


def reminder_is_due(last_sent_at: str | None, now: datetime | None = None) -> bool:
    if not last_sent_at:
        return True
    now = now or datetime.now(timezone.utc)
    try:
        last_sent = datetime.fromisoformat(last_sent_at.replace("Z", "+00:00"))
    except ValueError:
        return True
    if last_sent.tzinfo is None:
        last_sent = last_sent.replace(tzinfo=timezone.utc)
    return now - last_sent >= REMINDER_INTERVAL


def build_subscription_info(subscription: dict[str, Any]) -> dict[str, Any]:
    return {
        "endpoint": subscription["endpoint"],
        "keys": {
            "p256dh": subscription["p256dh"],
            "auth": subscription["auth_key"],
        },
    }


def send_push_notification(subscription: dict[str, Any]) -> None:
    payload = (
        '{"title":"'
        + NOTIFICATION_TITLE.replace('"', '\\"')
        + '","body":"'
        + NOTIFICATION_BODY.replace('"', '\\"')
        + '","url":"'
        + NOTIFICATION_URL
        + '"}'
    )
    webpush(
        subscription_info=build_subscription_info(subscription),
        data=payload,
        vapid_private_key=settings.vapid_private_key,
        vapid_claims={"sub": settings.vapid_subject},
    )


def delete_subscription(subscription_id: str) -> None:
    supabase = get_supabase_client()
    supabase.table("push_subscriptions").delete().eq("id", subscription_id).execute()


def dispatch_reminders() -> dict[str, int]:
    supabase = get_supabase_client()
    users_response = (
        supabase.table("users")
        .select("id, reminder_last_sent_at, reminders_enabled")
        .eq("reminders_enabled", True)
        .execute()
    )
    users = users_response.data or []

    checked = 0
    sent = 0
    skipped = 0
    failed = 0

    for user in users:
        checked += 1
        user_id = str(user["id"])

        subs_response = (
            supabase.table("push_subscriptions")
            .select("*")
            .eq("user_id", user_id)
            .execute()
        )
        subscriptions = subs_response.data or []
        if not subscriptions:
            skipped += 1
            continue

        timezone_name = subscriptions[0].get("timezone") or "UTC"
        today = local_today_iso(timezone_name)

        if user_has_entry_for_date(user_id, today):
            skipped += 1
            continue

        if not reminder_is_due(user.get("reminder_last_sent_at")):
            skipped += 1
            continue

        delivered = False
        for subscription in subscriptions:
            try:
                send_push_notification(subscription)
                delivered = True
            except WebPushException as exc:
                status_code = getattr(getattr(exc, "response", None), "status_code", None)
                if status_code in (404, 410):
                    delete_subscription(str(subscription["id"]))
                else:
                    failed += 1

        if delivered:
            sent += 1
            supabase.table("users").update(
                {"reminder_last_sent_at": datetime.now(timezone.utc).isoformat()}
            ).eq("id", user_id).execute()
        else:
            skipped += 1

    return {
        "checked": checked,
        "sent": sent,
        "skipped": skipped,
        "failed": failed,
    }
