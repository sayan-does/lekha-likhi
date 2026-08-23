"""Resolve frontend/API origins without overwriting sibling env values."""

import ipaddress

PROD_FRONTEND_URL = "https://lekha-likhi.vercel.app"
PROD_API_URL = "https://lekha-likhi-api.onrender.com"
LOCAL_FRONTEND_URL = "http://localhost:5173"

# Vite --host uses the LAN IP and may pick 5174+ when 5173 is busy.
LOCAL_DEV_ORIGIN_REGEX = (
    r"https?://("
    r"localhost|127\.0\.0\.1|\[::1\]|"
    r"10\.\d{1,3}\.\d{1,3}\.\d{1,3}|"
    r"192\.168\.\d{1,3}\.\d{1,3}|"
    r"172\.(1[6-9]|2\d|3[0-1])\.\d{1,3}\.\d{1,3}"
    r")(:\d+)?"
)


def first_nonempty_url(*candidates: str) -> str:
    for raw in candidates:
        value = (raw or "").strip().rstrip("/")
        if value:
            return value
    return ""


def resolve_cascade_url(
    *,
    tunnel: str = "",
    local: str = "",
    prod: str = "",
    legacy: str = "",
    app_env: str = "",
    hardcoded: str = "",
) -> str:
    """TUNNEL → LOCAL (if APP_ENV=local) → PROD → legacy → hardcoded."""
    use_local = (app_env or "").strip().lower() == "local"
    return first_nonempty_url(
        tunnel,
        local if use_local else "",
        prod,
        legacy,
        hardcoded,
    )


def cascade_origins(*candidates: str) -> list[str]:
    origins: set[str] = set()
    for raw in candidates:
        value = (raw or "").strip().rstrip("/")
        if value:
            origins.add(value)
    return sorted(origins)


def is_local_app_env(app_env: str) -> bool:
    return (app_env or "").strip().lower() == "local"


def is_loopback_or_private_host(hostname: str | None) -> bool:
    """True for localhost and RFC1918 / loopback addresses (Vite --host)."""
    if not hostname:
        return False
    if hostname.lower() in {"localhost", "127.0.0.1", "::1"}:
        return True
    try:
        ip = ipaddress.ip_address(hostname)
    except ValueError:
        return False
    return ip.is_private or ip.is_loopback
