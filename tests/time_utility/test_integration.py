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


def test_結合_nowとformat_datetimeとparse_datetimeが_ISO形式で往復変換した場合_元の値を保つ():
    original = now()

    formatted = format_datetime(original, DateTimeFormat.ISO)
    parsed = parse_datetime(formatted)

    assert parsed == original
    assert parsed.tzinfo is not None


def test_結合_nowとformat_datetimeとparse_datetimeが_fmtを指定せず往復変換した場合_ISO形式を優先して元の値を保つ():
    original = now()

    formatted = format_datetime(original, DateTimeFormat.ISO)
    parsed = parse_datetime(formatted, fmt=None)

    assert parsed == original


def test_結合_nowとformat_datetimeとparse_datetimeが_DATETIME形式で往復変換した場合_秒精度で一致する():
    original = now().replace(microsecond=0)

    formatted = format_datetime(original, DateTimeFormat.DATETIME)
    parsed = parse_datetime(formatted)

    assert parsed == original


def test_結合_nowとformat_datetimeとparse_datetimeが_JAPANESE_DATETIME形式で往復変換した場合_秒精度で一致する():
    original = now().replace(microsecond=0)

    formatted = format_datetime(original, DateTimeFormat.JAPANESE_DATETIME)
    parsed = parse_datetime(formatted)

    assert parsed == original


def test_結合_nowとformat_datetimeとparse_datetimeが_明示的なタイムゾーンで往復変換した場合_UTCオフセットを保つ():
    original = now(tz="America/New_York")

    formatted = format_datetime(original, DateTimeFormat.ISO)
    parsed = parse_datetime(formatted)

    assert parsed == original
    assert parsed.utcoffset() == original.utcoffset()


def test_結合_to_utcとto_jstが_nowの結果を往復変換した場合_元の値を保つ():
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
def test_異常系_now_to_timezone_parse_datetimeが_未知のタイムゾーン名を指定された場合_一貫してInvalidTimezoneErrorを送出する(invoke):
    with pytest.raises(InvalidTimezoneError):
        invoke()
