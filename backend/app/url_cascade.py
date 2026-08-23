"""Resolve frontend/API origins without overwriting sibling env values."""

PROD_FRONTEND_URL = "https://lekha-likhi.vercel.app"
PROD_API_URL = "https://lekha-likhi-api.onrender.com"
LOCAL_FRONTEND_URL = "http://localhost:5173"


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
