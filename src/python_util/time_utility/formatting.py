"""ロケール設定なしで日本語表記の日時文字列を生成・解析する。"""

from __future__ import annotations

import re
from collections.abc import Callable
from datetime import datetime, tzinfo
from enum import Enum

from python_util.time_utility.convert import ensure_aware
from python_util.time_utility.exceptions import DateTimeParseError
from python_util.time_utility.timezones import JST, resolve_timezone

_WEEKDAY_JA = ("月", "火", "水", "木", "金", "土", "日")


class DateTimeFormat(Enum):
    ISO = "iso"
    DATE = "date"
    DATETIME = "datetime"
    JAPANESE_DATE = "japanese_date"
    JAPANESE_DATETIME = "japanese_datetime"


def _format_japanese_date(dt: datetime) -> str:
    weekday = _WEEKDAY_JA[dt.weekday()]
    return f"{dt.year}年{dt.month:02d}月{dt.day:02d}日({weekday})"


def format_datetime(dt: datetime, fmt: DateTimeFormat | str = DateTimeFormat.DATETIME) -> str:
    """datetimeを指定フォーマットの文字列に変換する。localeモジュールは使用しない。"""
    if not isinstance(dt, datetime):
        raise TypeError(f"dtはdatetime型である必要があります: {dt!r}")

    if isinstance(fmt, str):
        try:
            fmt = DateTimeFormat(fmt)
        except ValueError:
            return dt.strftime(fmt)

    if fmt is DateTimeFormat.ISO:
        return dt.isoformat()
    if fmt is DateTimeFormat.DATE:
        return dt.strftime("%Y-%m-%d")
    if fmt is DateTimeFormat.DATETIME:
        return dt.strftime("%Y-%m-%d %H:%M:%S")
    if fmt is DateTimeFormat.JAPANESE_DATE:
        return _format_japanese_date(dt)
    return f"{_format_japanese_date(dt)} {dt.strftime('%H:%M:%S')}"


_JAPANESE_DATE_RE = re.compile(
    r"^(?P<year>\d{4})年(?P<month>\d{2})月(?P<day>\d{2})日\((?P<weekday>[月火水木金土日])\)$"
)
_JAPANESE_DATETIME_RE = re.compile(
    r"^(?P<year>\d{4})年(?P<month>\d{2})月(?P<day>\d{2})日\((?P<weekday>[月火水木金土日])\)"
    r" (?P<hour>\d{2}):(?P<minute>\d{2}):(?P<second>\d{2})$"
)


def _parse_iso(text: str) -> datetime | None:
    try:
        return datetime.fromisoformat(text)
    except ValueError:
        return None


def _parse_strptime(text: str, pattern: str) -> datetime | None:
    try:
        return datetime.strptime(text, pattern)
    except ValueError:
        return None


def _parse_japanese_date(text: str) -> datetime | None:
    match = _JAPANESE_DATE_RE.match(text)
    if match is None:
        return None
    return datetime(int(match["year"]), int(match["month"]), int(match["day"]))


def _parse_japanese_datetime(text: str) -> datetime | None:
    match = _JAPANESE_DATETIME_RE.match(text)
    if match is None:
        return None
    return datetime(
        int(match["year"]),
        int(match["month"]),
        int(match["day"]),
        int(match["hour"]),
        int(match["minute"]),
        int(match["second"]),
    )


_PARSERS: dict[DateTimeFormat, Callable[[str], datetime | None]] = {
    DateTimeFormat.ISO: _parse_iso,
    DateTimeFormat.DATETIME: lambda text: _parse_strptime(text, "%Y-%m-%d %H:%M:%S"),
    DateTimeFormat.DATE: lambda text: _parse_strptime(text, "%Y-%m-%d"),
    DateTimeFormat.JAPANESE_DATETIME: _parse_japanese_datetime,
    DateTimeFormat.JAPANESE_DATE: _parse_japanese_date,
}

_FALLBACK_ORDER = (
    DateTimeFormat.ISO,
    DateTimeFormat.DATETIME,
    DateTimeFormat.DATE,
    DateTimeFormat.JAPANESE_DATETIME,
    DateTimeFormat.JAPANESE_DATE,
)


def parse_datetime(
    text: str,
    fmt: DateTimeFormat | str | None = None,
    tz: str | tzinfo = JST,
) -> datetime:
    """日時文字列をdatetimeに変換する。タイムゾーン情報を含まない場合はtz(既定JST)として解釈する。"""
    resolved_tz = resolve_timezone(tz)

    if fmt is None:
        for candidate in _FALLBACK_ORDER:
            parsed = _PARSERS[candidate](text)
            if parsed is not None:
                return ensure_aware(parsed, default_tz=resolved_tz)
        raise DateTimeParseError(text)

    if isinstance(fmt, str):
        try:
            fmt = DateTimeFormat(fmt)
        except ValueError:
            parsed = _parse_strptime(text, fmt)
            if parsed is None:
                raise DateTimeParseError(text)
            return ensure_aware(parsed, default_tz=resolved_tz)

    parsed = _PARSERS[fmt](text)
    if parsed is None:
        raise DateTimeParseError(text)
    return ensure_aware(parsed, default_tz=resolved_tz)
