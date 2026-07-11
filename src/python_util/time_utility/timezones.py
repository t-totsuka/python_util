"""JST定数の提供とタイムゾーン名/オブジェクトの解決。"""

from __future__ import annotations

from datetime import tzinfo
from zoneinfo import ZoneInfo, ZoneInfoNotFoundError

from python_util.time_utility.exceptions import InvalidTimezoneError

JST: tzinfo = ZoneInfo("Asia/Tokyo")


def resolve_timezone(tz: str | tzinfo | None) -> tzinfo:
    """文字列/tzinfo/Noneを受け取りtzinfoへ解決する。Noneの場合はJSTを返す。"""
    if tz is None:
        return JST
    if isinstance(tz, tzinfo):
        return tz
    if isinstance(tz, str):
        try:
            return ZoneInfo(tz)
        except ZoneInfoNotFoundError as exc:
            raise InvalidTimezoneError(tz) from exc
    raise InvalidTimezoneError(tz)
