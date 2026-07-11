"""JSTを既定とした現在時刻(aware datetime)の取得。"""

from __future__ import annotations

from datetime import datetime, tzinfo

from python_util.time_utility.timezones import resolve_timezone


def now(tz: str | tzinfo | None = None) -> datetime:
    """指定タイムゾーン(既定JST)における現在時刻をawareなdatetimeで返す。"""
    if tz is not None and not isinstance(tz, (str, tzinfo)):
        raise TypeError(f"tzはstr/tzinfo/Noneのいずれかである必要があります: {tz!r}")
    return datetime.now(tz=resolve_timezone(tz))
