"""現在時刻取得からフォーマット・パースまでのラウンドトリップを検証する統合テスト。"""

from __future__ import annotations

import pytest

from python_util.time_utility import (
    DateTimeFormat,
    InvalidTimezoneError,
    format_datetime,
    now,
    parse_datetime,
    to_jst,
    to_timezone,
    to_utc,
)


def test_now_format_iso_parse_round_trip_preserves_original_value():
    original = now()

    formatted = format_datetime(original, DateTimeFormat.ISO)
    parsed = parse_datetime(formatted)

    assert parsed == original
    assert parsed.tzinfo is not None


def test_now_format_parse_round_trip_without_explicit_fmt_uses_iso_priority():
    original = now()

    formatted = format_datetime(original, DateTimeFormat.ISO)
    parsed = parse_datetime(formatted, fmt=None)

    assert parsed == original


def test_now_format_datetime_parse_round_trip_matches_second_precision():
    original = now().replace(microsecond=0)

    formatted = format_datetime(original, DateTimeFormat.DATETIME)
    parsed = parse_datetime(formatted)

    assert parsed == original


def test_now_format_japanese_datetime_parse_round_trip_matches_second_precision():
    original = now().replace(microsecond=0)

    formatted = format_datetime(original, DateTimeFormat.JAPANESE_DATETIME)
    parsed = parse_datetime(formatted)

    assert parsed == original


def test_now_with_explicit_timezone_format_parse_round_trip_preserves_offset():
    original = now(tz="America/New_York")

    formatted = format_datetime(original, DateTimeFormat.ISO)
    parsed = parse_datetime(formatted)

    assert parsed == original
    assert parsed.utcoffset() == original.utcoffset()


def test_to_utc_to_jst_round_trip_preserves_original_value():
    original = now()

    converted = to_jst(to_utc(original))

    assert converted == original
    assert converted.tzinfo is not None


@pytest.mark.parametrize(
    "invoke",
    [
        lambda: now(tz="Asia/Tokio"),
        lambda: to_timezone(now(), tz="Asia/Tokio"),
        lambda: parse_datetime("2026-07-11 10:00:00", tz="Asia/Tokio"),
    ],
)
def test_invalid_timezone_name_raises_invalid_timezone_error_consistently(invoke):
    with pytest.raises(InvalidTimezoneError):
        invoke()
