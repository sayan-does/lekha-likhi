"""Tests for share-link Redis cache parsing."""

from app.services.rate_limit import parse_cached_share_link


def test_parse_cached_share_link_none():
    assert parse_cached_share_link(None) is None


def test_parse_cached_share_link_valid_json_string():
    raw = '{"entry_id": "abc", "is_active": true}'
    assert parse_cached_share_link(raw) == {"entry_id": "abc", "is_active": True}


def test_parse_cached_share_link_double_encoded_string():
    """Legacy setter stored a JSON string inside another JSON string."""
    raw = '"{\\"entry_id\\": \\"abc\\", \\"is_active\\": true}"'
    assert parse_cached_share_link(raw) == {"entry_id": "abc", "is_active": True}


def test_parse_cached_share_link_already_a_dict():
    data = {"entry_id": "abc", "is_active": True}
    assert parse_cached_share_link(data) is data


def test_parse_cached_share_link_rejects_invalid_string():
    assert parse_cached_share_link("not-json") is None


def test_parse_cached_share_link_rejects_non_object():
    assert parse_cached_share_link(300) is None
    assert parse_cached_share_link(["abc"]) is None


def test_parse_cached_share_link_rejects_missing_entry_id():
    assert parse_cached_share_link('{"is_active": true}') is None
