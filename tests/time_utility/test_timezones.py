"""timezones.JST / resolve_timezone の仕様を検証するテスト。"""

from __future__ import annotations

from zoneinfo import ZoneInfo

import pytest

from python_util.time_utility.exceptions import InvalidTimezoneError
from python_util.time_utility.timezones import JST, resolve_timezone


def test_単体正常系_JSTが_定義された場合_Asia_TokyoのZoneInfoと一致する():
    assert JST == ZoneInfo("Asia/Tokyo")


def test_単体正常系_resolve_timezoneが_Noneを受け取った場合_JSTを返す():
    assert resolve_timezone(None) is JST


def test_単体正常系_resolve_timezoneが_有効なタイムゾーン名を受け取った場合_対応するZoneInfoを返す():
    assert resolve_timezone("UTC") == ZoneInfo("UTC")


def test_単体正常系_resolve_timezoneが_tzinfoオブジェクトを受け取った場合_同じtzinfoを返す():
    tz = ZoneInfo("America/New_York")
    assert resolve_timezone(tz) is tz


def test_異常系_resolve_timezoneが_未知のタイムゾーン名を受け取った場合_InvalidTimezoneErrorを送出する():
    with pytest.raises(InvalidTimezoneError) as exc_info:
        resolve_timezone("Asia/Tokio")

    assert "Asia/Tokio" in str(exc_info.value)


def test_異常系_resolve_timezoneが_サポート対象外の型を受け取った場合_InvalidTimezoneErrorを送出する():
    with pytest.raises(InvalidTimezoneError):
        resolve_timezone(123)
