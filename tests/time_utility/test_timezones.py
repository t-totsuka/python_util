"""timezones.JST / resolve_timezone の仕様を検証するテスト。"""

from __future__ import annotations

from zoneinfo import ZoneInfo

import pytest

from python_util.time_utility.exceptions import InvalidTimezoneError
from python_util.time_utility.timezones import JST, resolve_timezone


def test_jst_is_asia_tokyo_zoneinfo():
    assert JST == ZoneInfo("Asia/Tokyo")


def test_resolve_timezone_returns_jst_when_none():
    assert resolve_timezone(None) is JST


def test_resolve_timezone_returns_zoneinfo_for_valid_name():
    assert resolve_timezone("UTC") == ZoneInfo("UTC")


def test_resolve_timezone_returns_same_tzinfo_when_tzinfo_passed():
    tz = ZoneInfo("America/New_York")
    assert resolve_timezone(tz) is tz


def test_resolve_timezone_raises_invalid_timezone_error_for_unknown_name():
    with pytest.raises(InvalidTimezoneError) as exc_info:
        resolve_timezone("Asia/Tokio")

    assert "Asia/Tokio" in str(exc_info.value)


def test_resolve_timezone_raises_invalid_timezone_error_for_unsupported_type():
    with pytest.raises(InvalidTimezoneError):
        resolve_timezone(123)
