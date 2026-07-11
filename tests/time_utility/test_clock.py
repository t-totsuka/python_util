"""clock.now の仕様を検証するテスト。"""

from __future__ import annotations

from zoneinfo import ZoneInfo

import pytest

from python_util.time_utility.clock import now
from python_util.time_utility.exceptions import InvalidTimezoneError
from python_util.time_utility.timezones import JST


def test_now_without_tz_returns_jst_aware_datetime():
    result = now()

    assert result.tzinfo is JST


def test_now_with_explicit_timezone_string_returns_that_timezone():
    result = now(tz="UTC")

    assert result.tzinfo == ZoneInfo("UTC")


def test_now_with_explicit_tzinfo_returns_same_tzinfo():
    tz = ZoneInfo("America/New_York")

    result = now(tz=tz)

    assert result.tzinfo is tz


def test_now_with_unsupported_type_raises_type_error():
    with pytest.raises(TypeError):
        now(tz=123)


def test_now_with_unknown_timezone_name_raises_invalid_timezone_error():
    with pytest.raises(InvalidTimezoneError):
        now(tz="Asia/Tokio")
