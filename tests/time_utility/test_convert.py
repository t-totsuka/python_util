"""convert.ensure_aware / to_jst / to_utc / to_timezone の仕様を検証するテスト。"""

from __future__ import annotations

from datetime import datetime, timedelta
from zoneinfo import ZoneInfo

import pytest

from python_util.time_utility.convert import ensure_aware, to_jst, to_timezone, to_utc
from python_util.time_utility.exceptions import InvalidTimezoneError
from python_util.time_utility.timezones import JST

UTC = ZoneInfo("UTC")


def test_ensure_aware_attaches_jst_by_default_to_naive_datetime():
    naive = datetime(2026, 7, 11, 9, 0, 0)

    result = ensure_aware(naive)

    assert result.tzinfo is JST
    assert (result.year, result.month, result.day, result.hour) == (2026, 7, 11, 9)


def test_ensure_aware_returns_aware_datetime_unchanged():
    aware = datetime(2026, 7, 11, 9, 0, 0, tzinfo=UTC)

    result = ensure_aware(aware)

    assert result == aware
    assert result.tzinfo is UTC


def test_ensure_aware_uses_explicit_default_tz_for_naive_datetime():
    naive = datetime(2026, 7, 11, 9, 0, 0)

    result = ensure_aware(naive, default_tz=UTC)

    assert result.tzinfo is UTC


def test_ensure_aware_ignores_default_tz_for_already_aware_datetime():
    aware = datetime(2026, 7, 11, 9, 0, 0, tzinfo=UTC)

    result = ensure_aware(aware, default_tz=JST)

    assert result.tzinfo is UTC


def test_ensure_aware_raises_type_error_for_non_datetime():
    with pytest.raises(TypeError):
        ensure_aware(None)


def test_to_jst_converts_aware_datetime_preserving_instant():
    aware_utc = datetime(2026, 7, 11, 0, 0, 0, tzinfo=UTC)

    result = to_jst(aware_utc)

    assert result.tzinfo is JST
    assert result == aware_utc
    assert result.hour == 9


def test_to_jst_treats_naive_datetime_as_already_jst():
    naive = datetime(2026, 7, 11, 9, 0, 0)

    result = to_jst(naive)

    assert result.tzinfo is JST
    assert (result.year, result.month, result.day, result.hour) == (2026, 7, 11, 9)


def test_to_jst_raises_type_error_for_non_datetime():
    with pytest.raises(TypeError):
        to_jst(None)


def test_to_utc_converts_naive_datetime_as_jst_interpreted_value():
    naive = datetime(2026, 7, 11, 9, 0, 0)

    result = to_utc(naive)

    assert result.tzinfo is not None
    assert result.utcoffset() == timedelta(0)
    assert result.hour == 0
    assert result.day == 11


def test_to_utc_converts_aware_datetime_preserving_instant():
    aware_jst = datetime(2026, 7, 11, 9, 0, 0, tzinfo=JST)

    result = to_utc(aware_jst)

    assert result.utcoffset() == timedelta(0)
    assert result == aware_jst
    assert result.hour == 0


def test_to_utc_raises_type_error_for_non_datetime():
    with pytest.raises(TypeError):
        to_utc(None)


def test_to_timezone_converts_to_specified_timezone_by_string_name():
    aware_jst = datetime(2026, 7, 11, 9, 0, 0, tzinfo=JST)

    result = to_timezone(aware_jst, "America/New_York")

    assert result.tzinfo == ZoneInfo("America/New_York")
    assert result == aware_jst


def test_to_timezone_treats_naive_datetime_as_jst_before_converting():
    naive = datetime(2026, 7, 11, 9, 0, 0)

    result = to_timezone(naive, UTC)

    assert result.tzinfo is UTC
    assert result.hour == 0


def test_to_timezone_raises_invalid_timezone_error_for_unknown_name():
    aware_jst = datetime(2026, 7, 11, 9, 0, 0, tzinfo=JST)

    with pytest.raises(InvalidTimezoneError):
        to_timezone(aware_jst, "Asia/Tokio")


def test_to_timezone_raises_type_error_for_non_datetime():
    with pytest.raises(TypeError):
        to_timezone(None, UTC)


def test_utc_to_jst_round_trip_preserves_original_aware_value():
    original = datetime(2026, 7, 11, 9, 0, 0, tzinfo=JST)

    round_tripped = to_jst(to_utc(original))

    assert round_tripped == original
    assert round_tripped.tzinfo is JST


def test_naive_datetime_round_trip_through_utc_and_back_to_jst_preserves_wall_clock():
    naive = datetime(2026, 7, 11, 9, 0, 0)

    round_tripped = to_jst(to_utc(naive))

    assert (round_tripped.year, round_tripped.month, round_tripped.day, round_tripped.hour) == (
        2026,
        7,
        11,
        9,
    )
