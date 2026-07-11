"""naive/awareの相互変換、およびJST/UTC/任意タイムゾーン間の変換。"""

from __future__ import annotations

from datetime import datetime, tzinfo
from zoneinfo import ZoneInfo

from python_util.time_utility.timezones import JST, resolve_timezone

UTC: tzinfo = ZoneInfo("UTC")


def ensure_aware(dt: datetime, default_tz: tzinfo = JST) -> datetime:
    """naiveなdatetimeにdefault_tzを付与してawareにする。既にawareな場合はそのまま返す。"""
    if not isinstance(dt, datetime):
        raise TypeError(f"dtはdatetime型である必要があります: {dt!r}")
    if dt.tzinfo is not None and dt.tzinfo.utcoffset(dt) is not None:
        return dt
    return dt.replace(tzinfo=default_tz)


def to_timezone(dt: datetime, tz: str | tzinfo) -> datetime:
    """datetimeを指定タイムゾーンに変換する。naiveな場合はJSTとして解釈してから変換する。"""
    if not isinstance(dt, datetime):
        raise TypeError(f"dtはdatetime型である必要があります: {dt!r}")
    resolved = resolve_timezone(tz)
    return ensure_aware(dt).astimezone(resolved)


def to_jst(dt: datetime) -> datetime:
    """datetimeをJSTに変換する。naiveな場合はJSTとして解釈済みとみなす。"""
    return to_timezone(dt, JST)


def to_utc(dt: datetime) -> datetime:
    """datetimeをUTCに変換する。naiveな場合はJSTとして解釈してから変換する。"""
    return to_timezone(dt, UTC)
