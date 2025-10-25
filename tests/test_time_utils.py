from datetime import datetime, timezone

import pytest

from binance_copy_trading_api import coerce_to_milliseconds, default_time_range


def test_coerce_from_iso_date():
    result = coerce_to_milliseconds("2024-01-15")
    expected_dt = datetime(2024, 1, 15, tzinfo=timezone.utc)
    expected = int(expected_dt.timestamp() * 1000)
    assert result == expected


def test_coerce_from_datetime():
    dt = datetime(2024, 4, 2, 12, 30, tzinfo=timezone.utc)
    assert coerce_to_milliseconds(dt) == int(dt.timestamp() * 1000)


def test_coerce_from_epoch_string():
    assert coerce_to_milliseconds("1700000000000") == 1700000000000


def test_default_time_range_ordering():
    start, end = default_time_range(days=1)
    assert end > start
    assert end - start <= 24 * 60 * 60 * 1000


def test_invalid_format_raises():
    with pytest.raises(ValueError):
        coerce_to_milliseconds("not-a-date")


def test_invalid_type_raises():
    with pytest.raises(TypeError):
        coerce_to_milliseconds({})
