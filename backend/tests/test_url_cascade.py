from app.routers.google_auth import resolve_frontend_url
from app.url_cascade import PROD_FRONTEND_URL, resolve_cascade_url


def test_empty_env_uses_prod():
    assert (
        resolve_cascade_url(
            tunnel="",
            local="http://localhost:5173",
            prod="https://lekha-likhi.vercel.app",
            legacy="http://localhost:5173",
            app_env="",
            hardcoded=PROD_FRONTEND_URL,
        )
        == "https://lekha-likhi.vercel.app"
    )


def test_app_env_local_uses_local():
    assert (
        resolve_cascade_url(
            tunnel="",
            local="http://localhost:5173",
            prod="https://lekha-likhi.vercel.app",
            legacy="http://legacy.example",
            app_env="local",
            hardcoded=PROD_FRONTEND_URL,
        )
        == "http://localhost:5173"
    )


def test_tunnel_wins_over_local_and_prod():
    assert (
        resolve_cascade_url(
            tunnel="https://frontend.trycloudflare.com",
            local="http://localhost:5173",
            prod="https://lekha-likhi.vercel.app",
            legacy="http://localhost:5173",
            app_env="local",
            hardcoded=PROD_FRONTEND_URL,
        )
        == "https://frontend.trycloudflare.com"
    )


def test_legacy_used_when_cascade_keys_empty():
    assert (
        resolve_cascade_url(
            tunnel="",
            local="",
            prod="",
            legacy="http://localhost:5173",
            app_env="",
            hardcoded=PROD_FRONTEND_URL,
        )
        == "http://localhost:5173"
    )


def test_oauth_allows_prod_and_local_origins():
    assert resolve_frontend_url("http://localhost:5173/write") == "http://localhost:5173/write"
    assert (
        resolve_frontend_url("https://lekha-likhi.vercel.app/")
        == "https://lekha-likhi.vercel.app"
    )


def test_oauth_unknown_origin_falls_back():
    resolved = resolve_frontend_url("https://evil.example")
    assert "evil.example" not in resolved
