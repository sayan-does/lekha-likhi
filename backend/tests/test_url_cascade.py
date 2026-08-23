from app.routers.google_auth import resolve_frontend_url
from app.url_cascade import (
    PROD_FRONTEND_URL,
    is_loopback_or_private_host,
    resolve_cascade_url,
)


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


def test_oauth_allows_lan_origin_in_local_env():
    assert resolve_frontend_url("http://192.168.0.102:5173/") == "http://192.168.0.102:5173"
    assert resolve_frontend_url("http://localhost:5174/write") == "http://localhost:5174/write"


def test_loopback_or_private_host():
    assert is_loopback_or_private_host("localhost")
    assert is_loopback_or_private_host("192.168.0.102")
    assert is_loopback_or_private_host("10.0.0.4")
    assert not is_loopback_or_private_host("evil.example")
    assert not is_loopback_or_private_host("lekha-likhi.vercel.app")


def test_oauth_unknown_origin_falls_back():
    resolved = resolve_frontend_url("https://evil.example")
    assert "evil.example" not in resolved
