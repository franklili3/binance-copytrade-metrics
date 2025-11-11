from unittest.mock import MagicMock

import pytest

from binance_copy_trading_api import (
    _normalise_records,
    load_supabase_credentials,
    SupabaseUploader,
)


class DummyResponse:
    def __init__(self, error=None):
        self.error = error
        self.data = []


def test_normalise_records_from_list_of_dicts():
    rows = [{"a": 1}, {"b": 2}]
    assert _normalise_records(rows) == rows


def test_normalise_records_from_mapping_with_data_key():
    payload = {"data": [{"x": 1}, {"x": 2}]}
    assert _normalise_records(payload) == payload["data"]


def test_normalise_records_none_returns_empty_list():
    assert _normalise_records(None) == []


def test_normalise_records_ignores_non_mappings_in_list():
    rows = [{"a": 1}, 42, {"b": 2}]
    assert _normalise_records(rows) == [{"a": 1}, {"b": 2}]


def test_normalise_records_unsupported_type_raises_type_error():
    with pytest.raises(TypeError):
        _normalise_records("invalid")


def test_load_supabase_credentials_supports_supabase_key(monkeypatch):
    monkeypatch.delenv("SUPABASE_API_KEY", raising=False)
    monkeypatch.delenv("SUPABASE_SERVICE_KEY", raising=False)
    monkeypatch.delenv("supabase_api_key", raising=False)
    monkeypatch.setenv("SUPABASE_KEY", "test-key")
    monkeypatch.setenv("SUPABASE_URL", "https://example.supabase.co")

    url, key = load_supabase_credentials()

    assert url == "https://example.supabase.co"
    assert key == "test-key"


def test_supabase_uploader_insert_uses_client_upsert():
    client = MagicMock()
    upsert_call = client.table.return_value.upsert.return_value
    upsert_call.execute.return_value = DummyResponse()

    uploader = SupabaseUploader(
        project_url="https://example.supabase.co",
        api_key="test-key",
        client=client,
    )

    uploader.insert("my_table", [{"a": 1}])

    client.table.assert_called_once_with("my_table")
    client.table.return_value.upsert.assert_called_once_with([{"a": 1}])
    upsert_call.execute.assert_called_once()


def test_supabase_uploader_insert_raises_on_error():
    client = MagicMock()
    upsert_call = client.table.return_value.upsert.return_value
    upsert_call.execute.return_value = DummyResponse(error="boom")

    uploader = SupabaseUploader(
        project_url="https://example.supabase.co",
        api_key="test-key",
        client=client,
    )

    with pytest.raises(RuntimeError):
        uploader.insert("my_table", [{"a": 1}])
